"""
Loader for markdown templates defining expected document structure and content.
"""

# standard library imports
import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

# local imports
from utils.md_parser import (
    classify_content_line,
    parse_breadcrumbs,
    parse_heading_line,
    split_h1,
)
from core.constants import LoaderConstants
from utils.file_helper import FileHelper

logger = logging.getLogger(__name__)


@dataclass
class DocumentRules:
    """Rules applied to the entire document (breadcrumbs, expected H1 prefix, …).

    Attributes:
        breadcrumbs: List of expected breadcrumb components.
        h1_prefix:   Fixed prefix before the colon in H1, e.g. "Category".
                     None when H1 has no prefix (plain pattern title).
    """
    breadcrumbs: List[str] = field(default_factory=list)
    h1_prefix: Optional[str] = None


@dataclass
class ContentRules:
    """Rules specifying the expected content under a particular heading.

    Attributes:
        expected_types:      Set of allowed content-type strings.
        bullet_prefixes:     Expected parenthesised prefixes in bullet items, e.g. '(+)'.
        exact_list_prefixes: Hard-coded [Label](url): prefix strings in list items.
        table_headers:       Expected column headers for a table under this heading.
    """
    expected_types: Set[str] = field(default_factory=lambda: {"text"})
    bullet_prefixes: Set[str] = field(default_factory=set)
    exact_list_prefixes: Set[str] = field(default_factory=set)
    table_headers: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable representation of the content rules.

        Returns:
            Dict[str, Any]: Dictionary with primitive types suitable for JSON.
        """
        return {
            "expected_types": sorted(self.expected_types),
            "bullet_prefixes": sorted(self.bullet_prefixes),
            "exact_list_prefixes": sorted(self.exact_list_prefixes),
            "table_headers": self.table_headers,
        }


@dataclass
class HeadingRules:
    """Rules specifying the characteristics of a heading and its content.

    Attributes:
        level:         Heading depth (1 = H1).
        text:          Cleaned heading text (links resolved, asterisks stripped).
        optional:      Whether the heading is marked *(optional)*.
        is_variable:   Whether the heading (or part of it) is an italic placeholder.
        variable_part: The placeholder text, e.g. "Name" for "Category: *Name*".
        is_link:       Whether the heading itself is a hyperlink.
        link_target:   Target URL when is_link is True.
        formatting:    Reserved for future use.
        is_group:      True when this heading represents a collapsed A–Z block.
        group_members: Member labels when is_group is True.
        content_rules: Validation rules for the content block below this heading.
    """
    level: int
    text: str
    optional: bool = False
    is_variable: bool = False
    is_link: bool = False
    link_target: Optional[str] = None
    formatting: str = "normal"
    is_group: bool = False
    group_members: List[str] = field(default_factory=list)
    variable_part: Optional[str] = None
    content_rules: ContentRules = field(default_factory=ContentRules)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable representation of the heading rules.

        Returns:
            Dict[str, Any]: Dictionary suitable for JSON and debugging dumps.
        """
        dictionary: Dict[str, Any] = {
            "level": self.level,
            "text": self.text,
            "optional": self.optional,
            "is_variable": self.is_variable,
            "variable_part": self.variable_part,
            "is_link": self.is_link,
            "link_target": self.link_target,
            "formatting": self.formatting,
            "is_group": self.is_group,
            "content_rules": self.content_rules.to_dict(),
        }
        if self.is_group:
            dictionary["group_members"] = self.group_members
        return dictionary


@dataclass
class TemplateRules:
    """Root structure holding all rules for a parsed template.

    Attributes:
        document_rules: Document-wide settings and requirements.
        headings:       Ordered list of expected headings and their content rules.
    """
    document_rules: DocumentRules = field(default_factory=DocumentRules)
    headings: List[HeadingRules] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable representation of the template rules.

        Returns:
            Dict[str, Any]: Dictionary that includes document rules and heading rules.
        """
        return {
            "document_rules": {
                "breadcrumbs": self.document_rules.breadcrumbs,
                "h1_prefix": self.document_rules.h1_prefix,
            },
            "headings": [heading.to_dict() for heading in self.headings],
        }


def _detect_and_collapse_alphabet_groups(headings: List[HeadingRules]) -> List[HeadingRules]:
    """Detect and collapse A–Z / 0-9 heading runs into a single grouped rule.

    Many templates contain an alphabet index where sibling headings are single
    letters (or '0-9') and repeat for a long sequence. To simplify downstream
    validation, this function replaces qualifying runs with a single synthetic
    heading rule:

    * text is set to "[A-Z]"
    * is_group is set to True
    * group_members contains the original run members

    Content rules for the whole group are taken from the first member.

    Args:
        headings (List[HeadingRules]): Heading rules extracted from the template
            in the original order.

    Returns:
        List[HeadingRules]: New list of heading rules where qualifying alphabet
        runs are replaced by a single grouped heading.
    """
    result: List[HeadingRules] = []
    i = 0
    while i < len(headings):
        heading = headings[i]
        if heading.text not in LoaderConstants.ALPHABET_SET:
            result.append(heading)
            i += 1
            continue

        run: List[HeadingRules] = [heading]
        j = i + 1
        while j < len(headings) and headings[j].text in LoaderConstants.ALPHABET_SET and headings[j].level == heading.level:
            run.append(headings[j])
            j += 1

        if len(run) >= LoaderConstants.MIN_ALPHABET_RUN:
            result.append(HeadingRules(
                level=heading.level,
                text="[A-Z]",
                optional=sum(r.optional for r in run) >= len(run) // 2,
                is_group=True,
                group_members=[r.text for r in run],
                content_rules=run[0].content_rules,
            ))
            i = j
        else:
            result.append(heading)
            i += 1

    return result


class TemplateLoader:
    """Parse every .md template file in a directory into TemplateRules.

    All regex and classification logic lives in LoaderConstant; this class
    only handles file I/O and maps parsed primitives onto template-specific
    data classes.
    """

    def __init__(self, templates_dir: str, file_helper: FileHelper) -> None:
        """Create a new loader bound to *templates_dir*.

        Args:
            templates_dir (str): Directory containing Markdown template files.
            file_helper (FileHelper): FileHelper instance used for reading files
                                      and discovering templates in the directory.
        """
        self.templates_dir = templates_dir
        self._file_helper = file_helper
        self.templates: Dict[str, TemplateRules] = {}
        self._loaded: bool = False

    def parse(self, force: bool = False) -> None:
        """Load (or reload) all templates from *templates_dir*.

        Args:
            force (bool, optional): Re-parse even if templates were already loaded.
                Defaults to False.
        """
        if self._loaded and not force:
            return

        self.templates = {}

        filepaths = sorted(self._file_helper.find_markdown_files(self.templates_dir, recursive=False))
        if not filepaths:
            logger.warning("No templates found in: %s", self.templates_dir)
            return

        for filepath in filepaths:
            name = os.path.splitext(os.path.basename(filepath))[0]
            try:
                self.templates[name] = self._parse_template(filepath)
                logger.debug("Loaded template: %s", name)
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to load template %s: %s", name, exc)

        self._loaded = True
        self.dump_json("output/templates_debug")
        logger.info("Loaded %d template(s) from %s", len(self.templates), self.templates_dir)

    def get_template(self, name: str) -> TemplateRules:
        """Return rules for a single named template.

        If templates were not loaded yet, they are loaded lazily.

        Args:
            name (str): Template name (filename without the .md extension).

        Returns:
            TemplateRules: Parsed rules of the template. Returns an empty
            TemplateRules instance if *name* is unknown.
        """
        if not self._loaded:
            self.parse()
        return self.templates.get(name, TemplateRules())

    def get_all_templates(self) -> Dict[str, TemplateRules]:
        """Return mapping of all loaded templates.

        If templates were not loaded yet, they are loaded lazily.

        Returns:
            Dict[str, TemplateRules]: Mapping of template name → parsed rules.
        """
        if not self._loaded:
            self.parse()
        return self.templates

    def dump_json(self, output_dir: str, indent: int = 2) -> None:
        """Write one <name>.json per template into *output_dir*.

        Args:
            output_dir: Target folder (created if absent).
            indent:     JSON indentation spaces.
        """
        if not self._loaded:
            self.parse()
        os.makedirs(output_dir, exist_ok=True)
        for name, rules in self.templates.items():
            dest = os.path.join(output_dir, f"{name}.json")
            with open(dest, "w", encoding="utf-8") as fh:
                json.dump(rules.to_dict(), fh, indent=indent, ensure_ascii=False)
            logger.debug("Debug JSON written: %s", dest)
        logger.info("Debug JSON dumped to %s (%d file(s))", output_dir, len(self.templates))

    def dump_json_single(self, name: str, output_dir: str, indent: int = 2) -> None:
        """Write a JSON file for a single template into *output_dir*.

        Args:
            name:       Template name (filename without .md).
            output_dir: Target folder.
            indent:     JSON indentation spaces.
        """
        rules = self.get_template(name)
        os.makedirs(output_dir, exist_ok=True)
        dest = os.path.join(output_dir, f"{name}.json")
        with open(dest, "w", encoding="utf-8") as fh:
            json.dump(rules.to_dict(), fh, indent=indent, ensure_ascii=False)
        logger.debug("Debug JSON written: %s", dest)

    def _parse_template(self, filepath: str) -> TemplateRules:
        """Parse a single template Markdown file.

        Args:
            filepath (str): Absolute path to a .md template file.

        Returns:
            TemplateRules: Parsed template rules extracted from the file.
        """
        document_rules = DocumentRules()
        raw_headings: List[HeadingRules] = []
        current: Optional[HeadingRules] = None

        content = self._file_helper.read_file(filepath)
        if content is None:
            logger.error("Failed to read template: %s", filepath)
            return TemplateRules()

        for raw_line in content.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            # Heading
            match = LoaderConstants.RE_HEADING.match(line)
            if match:
                ph = parse_heading_line(match.group(1), match.group(2), is_template=True)
                current = HeadingRules(
                    level=ph.level,
                    text=ph.text,
                    optional=ph.is_optional,
                    is_variable=ph.is_variable,
                    variable_part=ph.variable_part,
                    is_link=ph.is_link,
                    link_target=ph.link_target,
                )
                raw_headings.append(current)

                if current.level == 1 and document_rules.h1_prefix is None:
                    prefix, _ = split_h1(current.text)
                    document_rules.h1_prefix = prefix
                continue

            # Preamble
            if current is None:
                parts = parse_breadcrumbs(line)
                if parts:
                    document_rules.breadcrumbs = parts
                continue

            # Content
            types, bp, elp, headers = classify_content_line(line, is_template=True)
            cr = current.content_rules
            cr.expected_types.update(types)
            if bp:
                cr.bullet_prefixes.add(bp)
            if elp:
                cr.exact_list_prefixes.add(elp)
            if headers and not cr.table_headers:
                cr.table_headers = headers

        return TemplateRules(
            document_rules=document_rules,
            headings=_detect_and_collapse_alphabet_groups(raw_headings),
        )