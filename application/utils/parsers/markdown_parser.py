import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from utils.parsers.base_parser import (
    classify_content_line,
    parse_breadcrumbs,
    parse_heading_line,
    split_h1,
)
from utils.constants import LoaderConstants

logger = logging.getLogger(__name__)


@dataclass
class DocumentMeta:
    """Document-level metadata extracted from the file.

    Attributes:
        breadcrumbs:            Breadcrumb parts as they appear in the file.
        breadcrumbs_normalized: Same parts with link markup stripped and
                                variable last-part replaced by "*" so
                                comparison with the template is straightforward.
        h1_prefix:              Fixed prefix before the colon in H1, e.g. "Category".
                                None when H1 has no prefix (plain pattern title).
        h1_value:               Concrete value after the prefix, e.g. "Agile".
        filepath:               Absolute path to the source file.
    """
    breadcrumbs: List[str] = field(default_factory=list)
    breadcrumbs_normalized: List[str] = field(default_factory=list)
    h1_prefix: Optional[str] = None
    h1_value: Optional[str] = None
    filepath: str = ""


@dataclass
class ContentInfo:
    """Content kinds actually found under a heading.

    Attributes:
        found_types:         Set of content-type strings (same vocabulary as
                             ContentRules.expected_types).
        bullet_prefixes:     Parenthesised prefixes in bullet items, e.g. '(+)'.
        exact_list_prefixes: [Label](url): prefixes in bullet items.
        table_headers:       Column headers of the first table under this heading.
        is_empty:            True when no non-whitespace content follows the heading.
        first_content_line:  1-based line of the first content line (0 = empty).
    """
    found_types: Set[str] = field(default_factory=set)
    bullet_prefixes: Set[str] = field(default_factory=set)
    exact_list_prefixes: Set[str] = field(default_factory=set)
    table_headers: List[str] = field(default_factory=list)
    is_empty: bool = True
    first_content_line: int = 0
    raw_lines: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable representation of the content info.

        Returns:
            Dict[str, Any]: Dictionary with keys 'found_types', 'bullet_prefixes', 'exact_list_prefixes', 'table_headers', 'is_empty' and 'first_content_line'. Values are basic Python types suitable for JSON encoding.
        """
        return {
            "found_types": sorted(self.found_types),
            "bullet_prefixes": sorted(self.bullet_prefixes),
            "exact_list_prefixes": sorted(self.exact_list_prefixes),
            "table_headers": self.table_headers,
            "is_empty": self.is_empty,
            "first_content_line": self.first_content_line,
            "raw_lines": self.raw_lines,
        }


@dataclass
class HeadingInfo:
    """A single heading (or collapsed alphabet group) from an actual document.

    Attributes:
        level:              Heading depth (1–6).
        text:               Cleaned heading text.
        raw_text:           Original text after the hashes.
        line_number:        1-based line of the heading (first member if group).
        is_link:            True if the heading is a hyperlink.
        link_target:        URL when is_link is True.
        is_group:           True when this represents a collapsed A–Z block.
        group_members:      Alphabet labels present in the document for this group.
        group_line_numbers: Line numbers matching group_members order.
        content:            Merged content info for the whole group (or single heading).
    """
    level: int
    text: str
    raw_text: str
    line_number: int = 0
    is_link: bool = False
    link_target: Optional[str] = None
    is_group: bool = False
    group_members: List[str] = field(default_factory=list)
    group_line_numbers: List[int] = field(default_factory=list)
    content: ContentInfo = field(default_factory=ContentInfo)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable representation of the heading.

        Returns:
            Dict[str, Any]: Mapping representing this heading suitable for serialization and comparison with template data.
        """
        dictionary = {
            "level": self.level,
            "text": self.text,
            "raw_text": self.raw_text,
            "line_number": self.line_number,
            "is_link": self.is_link,
            "link_target": self.link_target,
            "is_group": self.is_group,
            "content": self.content.to_dict(),
        }
        if self.is_group:
            dictionary["group_members"] = self.group_members
            dictionary["group_line_numbers"] = self.group_line_numbers
        return dictionary


@dataclass
class ParsedDocument:
    """Complete parsed representation of one Markdown file.

    Attributes:
        meta:     Document-level metadata.
        headings: Ordered list of headings (alphabet runs already collapsed).
    """
    meta: DocumentMeta = field(default_factory=DocumentMeta)
    headings: List[HeadingInfo] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable mapping of the parsed document.

        Returns:
            Dict[str, Any]: Dictionary with 'meta' and 'headings' keys. 'meta' contains filepath, breadcrumbs and H1 info; 'headings' is a list of heading dictionaries as produced by :meth:HeadingInfo.to_dict.
        """
        return {
            "meta": {
                "filepath": self.meta.filepath,
                "breadcrumbs": self.meta.breadcrumbs,
                "breadcrumbs_normalized": self.meta.breadcrumbs_normalized,
                "h1_prefix": self.meta.h1_prefix,
                "h1_value": self.meta.h1_value,
            },
            "headings": [heading.to_dict() for heading in self.headings],
        }


def _collapse_alphabet_groups(headings: List[HeadingInfo]) -> List[HeadingInfo]:
    """Collapse runs of A–Z / 0-9 headings into a single is_group=True entry.

    Args:
        headings: The headings value.

    Returns:
        List[HeadingInfo]: New list of headings where qualifying alphabet runs are replaced by a single grouped heading.
    """
    result: List[HeadingInfo] = []
    i = 0
    while i < len(headings):
        heading = headings[i]
        if heading.text not in LoaderConstants.ALPHABET_SET:
            result.append(heading)
            i += 1
            continue

        run: List[HeadingInfo] = [heading]
        j = i + 1
        while j < len(headings) and headings[j].text in LoaderConstants.ALPHABET_SET and headings[j].level == heading.level:
            run.append(headings[j])
            j += 1

        if len(run) >= LoaderConstants.MIN_ALPHABET_RUN:
            merged_content = _merge_content([r.content for r in run])
            result.append(HeadingInfo(
                level=heading.level,
                text="[A-Z]",
                raw_text="[A-Z]",
                line_number=heading.line_number,   # line of first member
                is_group=True,
                group_members=[r.text for r in run],
                group_line_numbers=[r.line_number for r in run],
                content=merged_content,
            ))
            i = j
        else:
            result.append(heading)
            i += 1

    return result


def _merge_content(infos: List[ContentInfo]) -> ContentInfo:
    """Merge multiple ContentInfo objects into one.

    Args:
        infos: The infos value.

    Returns:
        ContentInfo: A new instance representing the merged content.
    """
    merged = ContentInfo()
    for info in infos:
        merged.found_types.update(info.found_types)
        merged.bullet_prefixes.update(info.bullet_prefixes)
        merged.exact_list_prefixes.update(info.exact_list_prefixes)
        if not merged.table_headers and info.table_headers:
            merged.table_headers = info.table_headers
        if info.first_content_line and not merged.first_content_line:
            merged.first_content_line = info.first_content_line
        merged.raw_lines.extend(info.raw_lines)
    merged.is_empty = not bool(merged.found_types)
    return merged


class MarkdownParser:
    """Parse Markdown files into ParsedDocument objects for validation.

    The parsed structure mirrors the shape produced by TemplateLoader:

    * Alphabet heading runs are collapsed to is_group=True entries.
    * All regex / classification logic is shared via md_parser.

    Args:
        file_helper: FileHelper instance used for reading files and
                     discovering .md files in directories.
    """

    def __init__(self) -> None:
        """Initialize the object with required collaborators.
        """
        pass

    def parse_content(self, filepath: str, content: str) -> ParsedDocument:
        """Parse a single Markdown document from in-memory content.

        Args:
            filepath: The filepath value.
            content: The markdown or template content to process.

        Returns:
            ParsedDocument: Parsed representation of the content.
        """
        if not isinstance(content, str):
            raise TypeError("content must be a string")

        normalized_path = os.path.abspath(filepath)
        return self._parse(normalized_path, content)


    def dump_json(self, doc: ParsedDocument, output_dir: str, indent: int = 2) -> None:
        """Write a JSON representation of doc to output_dir. Just for debugging purposes.

        Args:
            doc: The parsed document to process.
            output_dir: The directory where output files should be written.
            indent: The indent value.
        """
        os.makedirs(output_dir, exist_ok=True)
        stem = os.path.splitext(os.path.basename(doc.meta.filepath))[0]
        dest = os.path.join(output_dir, f"{stem}.json")
        with open(dest, "w", encoding="utf-8") as fh:
            json.dump(doc.to_dict(), fh, indent=indent, ensure_ascii=False)
        logger.debug("Debug JSON written: %s", dest)

    def _parse(self, filepath: str, content: str) -> ParsedDocument:
        """Internal parser that constructs a ParsedDocument from already-read content.

        Args:
            filepath: The filepath value.
            content: The markdown or template content to process.

        Returns:
            ParsedDocument: Parsed representation including meta and headings.
        """
        meta = DocumentMeta(filepath=filepath)
        raw_headings: List[HeadingInfo] = []
        current: Optional[HeadingInfo] = None
        pre_heading = True

        for line_num, raw_line in enumerate(content.splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue

            # Heading
            match = LoaderConstants.RE_HEADING.match(line)
            if match:
                ph = parse_heading_line(match.group(1), match.group(2), is_template=False)
                current = HeadingInfo(
                    level=ph.level,
                    text=ph.text,
                    raw_text=ph.raw_text,
                    line_number=line_num,
                    is_link=ph.is_link,
                    link_target=ph.link_target,
                )
                raw_headings.append(current)
                pre_heading = False

                if current.level == 1 and meta.h1_value is None:
                    meta.h1_prefix, meta.h1_value = split_h1(current.text)
                continue

            # Preamble
            if pre_heading:
                parts = parse_breadcrumbs(line)
                if parts:
                    meta.breadcrumbs = parts
                continue

            # Content
            if current is not None:
                info = current.content
                if info.is_empty:
                    info.first_content_line = line_num
                info.is_empty = False
                info.raw_lines.append({"line": line_num, "content": line})

                types, bp, elp, headers = classify_content_line(line, is_template=False)
                info.found_types.update(types)
                if bp:
                    info.bullet_prefixes.add(bp)
                if elp:
                    info.exact_list_prefixes.add(elp)
                if headers and not info.table_headers:
                    info.table_headers = headers

        # Collapse alphabet runs
        headings = _collapse_alphabet_groups(raw_headings)

        return ParsedDocument(meta=meta, headings=headings)

    def get_link_metadata(self, doc: ParsedDocument) -> Dict[str, Any]:
        """
        This method scans the headings and content of a parsed markdown file to 
        identify aliases (from the 'Also Known As' section) and outbound links 
        (from the 'Related Patterns' section).

        Args:
            doc (ParsedDocument): The parsed representation of the markdown file.

        Returns:
            Dict[str, Any]: A dictionary containing two keys:
                - 'aliases': A list of strings representing alternative names 
                  for the pattern.
                - 'related_links': A list of filenames (e.g., 'Observer.md') 
                  referenced in the 'Related Patterns' section.
        """
        import re
        metadata = {
            "aliases": [],
            "related_links": []
        }
        
        for heading in doc.headings:
            # Aliases in "Also Known As"
            if heading.text.lower() == "also known as":
                for line_entry in heading.content.raw_lines:
                    line = line_entry["content"].strip()
                    if not line:
                        continue
                    
                    clean_line = re.sub(r'^[-*+]\s+', '', line)
                    parts = [p.strip() for p in clean_line.split(',') if p.strip()]
                    metadata["aliases"].extend(parts)

            # Links in "Related Patterns"
            elif heading.text.lower() == "related patterns":
                for line_entry in heading.content.raw_lines:
                    line = line_entry["content"]
                    links = LoaderConstants.RE_MARKDOWN_LINK_URL.findall(line)
                    for url in links:
                        if os.path.basename(url.split('#')[0]).lower() == 'references.md':
                            continue
                        filename = os.path.basename(url.split('#')[0])
                        metadata["related_links"].append(filename)
        
        return metadata