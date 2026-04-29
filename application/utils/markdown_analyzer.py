import re
import os
from pathlib import Path
from typing import Dict, List, Tuple
import logging

from core.constants import FileConstants, LoaderConstants, ReportConstants
from utils.exceptions import FileNotFoundError, InvalidInputError
from utils.formatting_validator import FormattingValidator
from utils.markdown_parser import DocumentMeta, HeadingInfo, ParsedDocument
from utils.template_parser import ContentRules, DocumentRules, HeadingRules, TemplateRules

logger = logging.getLogger(__name__)


class MarkdownAnalyzer:
    def __init__(self, base_path: str = None):
        """Initialise the analyzer.

        Args:
            base_path: Root path of the project. Defaults to the repository root inferred from the location of this file.
        """
        if base_path is None:
            app_dir = Path(__file__).parent.parent
            self.base_path = app_dir.parent
        else:
            if not isinstance(base_path, (str, Path)):
                raise InvalidInputError("base_path", base_path, "must be a string or Path object")
            base_path_obj = Path(base_path)
            if not base_path_obj.exists():
                raise FileNotFoundError(str(base_path_obj))
            self.base_path = base_path_obj

        self.current_warnings: List[Dict] = []
        self.current_passed: List[str] = []

    def validate_structure(self, doc: ParsedDocument, template: TemplateRules) -> Dict:
        """Compare a parsed document against template rules.

        Args:
            doc: Parsed representation of the markdown file.
            template: Rules extracted from the matching template.

        Returns:
            Dict with keys 'file', 'warnings', and 'passed'.
        """
        self.current_warnings = []
        self.current_passed = []
        
        # Breadcrumbs
        self._validate_breadcrumbs(doc.meta, template.document_rules)
        self._check_breadcrumb_links(doc.meta)

        # H1 heading
        h1_headings = [h for h in doc.headings if h.level == 1]
        self._check_h1_count(h1_headings)
        doc_h1 = h1_headings[0] if len(h1_headings) == 1 else None
        self._check_h1_filename(doc.meta)
        self._check_h1_prefix(doc.meta, template.document_rules)

        # Separate the variable H1 rule from the rest for section checks
        template_h1 = next((h for h in template.headings if h.level == 1 and h.is_variable), None)
        non_h1_headings = [h for h in template.headings if not (h.level == 1 and h.is_variable)]
        doc_map = {h.text: h for h in doc.headings}

        # Section structure
        self._check_mandatory_sections(doc_map, non_h1_headings)
        self._check_section_order(doc.headings, non_h1_headings)
        self._check_no_unknown_sections(doc.headings, template)
        self._check_heading_levels(doc_map, non_h1_headings)

        # Content checks per matched section
        self._check_mandatory_sections_not_empty(doc_map, non_h1_headings)
        if doc_h1 and template_h1:
            self._check_section_content(doc_h1.content, template_h1.content_rules, doc_h1.line_number, doc_h1.text)
        for t_heading in non_h1_headings:
            actual = doc_map.get(t_heading.text)
            if actual:
                self._check_section_content(actual.content, t_heading.content_rules, actual.line_number, actual.text)

        # Formatting
        all_raw_lines = []
        for heading in doc.headings:
            all_raw_lines.extend(heading.content.raw_lines)

        formatting_warnings = FormattingValidator.run_all_checks(
            full_content=getattr(doc, 'raw_content', ""),
            raw_lines=all_raw_lines
        )
        self.current_warnings.extend(formatting_warnings)

        if not formatting_warnings:
            self._add_passed("Formatting (bold, italics, tables, images) is consistent.")

        return {
            "file": doc.meta.filepath,
            "warnings": self.current_warnings,
            "passed": self.current_passed,
        }

    def _check_h1_count(self, h1_headings: List[HeadingInfo]) -> None:
        """Document must contain exactly one H1 heading.

        Args:
            h1_headings: All HeadingInfo objects whose level equals 1.
        """
        count = len(h1_headings)
        if count == 0:
            self._add_warning(1, "Document is missing an H1 heading.")
        elif count > 1:
            lines = ", ".join(str(h.line_number) for h in h1_headings)
            self._add_warning(
                h1_headings[1].line_number,
                f"Document contains {count} H1 headings (lines {lines}); exactly one is required.",
            )
        else:
            self._add_passed("Document contains exactly one H1 heading.")

    def _check_h1_filename(self, meta: DocumentMeta) -> None:
        """H1 value must match the filename stem (case-insensitive).

        Args:
            meta: Metadata extracted from the parsed document.
        """
        if meta.h1_value is None or not meta.filepath:
            return
        stem = os.path.splitext(os.path.basename(meta.filepath))[0]
        if meta.h1_value.lower().replace(" ", "_") != stem.lower():
            self._add_warning(
                1,
                f"H1 value '{meta.h1_value}' does not match filename stem '{stem}'.",
            )
        else:
            self._add_passed("H1 value matches the filename stem.")

    def _check_h1_prefix(self, meta: DocumentMeta, doc_rules: DocumentRules) -> None:
        """H1 prefix must match the template's expected prefix.

        Args:
            meta: Metadata extracted from the parsed document.
            doc_rules: Document-level rules from the matched template.
        """
        expected = doc_rules.h1_prefix
        actual = meta.h1_prefix
        if expected == actual:
            self._add_passed("H1 prefix matches the template.")
            return
        if expected is None:
            self._add_warning(1, f"H1 has an unexpected prefix '{actual}'; template expects a plain title.")
        elif actual is None:
            self._add_warning(1, f"H1 is missing required prefix '{expected}'.")
        else:
            self._add_warning(1, f"H1 prefix '{actual}' does not match expected prefix '{expected}'.")

    def _check_mandatory_sections(
        self,
        doc_map: Dict[str, HeadingInfo],
        template_headings: List[HeadingRules],
    ) -> None:
        """Every non-optional template heading must exist in the document.

        Args:
            doc_map: Mapping of heading text to HeadingInfo for the document.
            template_headings: Non-H1 heading rules from the template.
        """
        before = len(self.current_warnings)
        for t_heading in template_headings:
            if not t_heading.optional and t_heading.text not in doc_map:
                self._add_warning(0, f"Mandatory section '{t_heading.text}' is missing.")
        if len(self.current_warnings) == before:
            self._add_passed("All mandatory sections are present.")

    def _check_section_order(
        self,
        doc_headings: List[HeadingInfo],
        template_headings: List[HeadingRules],
    ) -> None:
        """Sections must appear in the same relative order as in the template.

        Args:
            doc_headings: All headings extracted from the document, in document order.
            template_headings: Non-H1 heading rules from the template, in template order.
        """
        template_index = {h.text: i for i, h in enumerate(template_headings)}
        matched = [h for h in doc_headings if h.text in template_index]
        order = [template_index[h.text] for h in matched]

        before = len(self.current_warnings)
        for i in range(1, len(order)):
            if order[i] < order[i - 1]:
                offender = matched[i]
                self._add_warning(
                    offender.line_number,
                    f"Section '{offender.text}' is out of order relative to the template.",
                )
        if len(self.current_warnings) == before:
            self._add_passed("Section order matches the template.")

    def _check_no_unknown_sections(
        self,
        doc_headings: List[HeadingInfo],
        template: TemplateRules,
    ) -> None:
        """Document must not contain headings that are absent from the template.

        Args:
            doc_headings: All headings extracted from the document.
            template: Full template rules including all heading definitions.
        """
        known_texts = {h.text for h in template.headings}
        template_h1 = next((h for h in template.headings if h.level == 1), None)
        h1_is_variable = template_h1 is not None and template_h1.is_variable

        before = len(self.current_warnings)
        for heading in doc_headings:
            if heading.level == 1 and h1_is_variable:
                continue  # Variable H1 is matched by level, not by text
            if heading.text not in known_texts:
                self._add_warning(
                    heading.line_number,
                    f"Unknown section '{heading.text}' is not defined in the template.",
                )
        if len(self.current_warnings) == before:
            self._add_passed("No unknown sections found.")

    def _check_heading_levels(
        self,
        doc_map: Dict[str, HeadingInfo],
        template_headings: List[HeadingRules],
    ) -> None:
        """Each section must have the heading level specified in the template.

        Args:
            doc_map: Mapping of heading text to HeadingInfo for the document.
            template_headings: Non-H1 heading rules from the template.
        """
        before = len(self.current_warnings)
        for t_heading in template_headings:
            actual = doc_map.get(t_heading.text)
            if actual and actual.level != t_heading.level:
                self._add_warning(
                    actual.line_number,
                    f"Section '{actual.text}' is H{actual.level} "
                    f"but template requires H{t_heading.level}.",
                )
        if len(self.current_warnings) == before:
            self._add_passed("All heading levels match the template.")

    def _validate_breadcrumbs(self, doc_meta: DocumentMeta, doc_rules: DocumentRules) -> None:
        """Validate the breadcrumb navigation line.

        Args:
            doc_meta: Metadata extracted from the parsed document.
            doc_rules: Document-level rules from the matched template.
        """
        if not doc_meta.breadcrumbs:
            self._add_warning(1, "Document is missing breadcrumbs.")
            return

        template_crumbs = doc_rules.breadcrumbs
        actual_crumbs = doc_meta.breadcrumbs

        if len(actual_crumbs) != len(template_crumbs):
            self._add_warning(
                1,
                f"Breadcrumbs have {len(actual_crumbs)} part(s), "
                f"but template expects {len(template_crumbs)}.",
            )
            return

        before = len(self.current_warnings)
        for i, (expected, actual) in enumerate(zip(template_crumbs, actual_crumbs)):
            if expected.startswith("*") and expected.endswith("*"):
                if not actual.strip():
                    self._add_warning(
                        1,
                        f"Breadcrumb part {i + 1} (wildcard '{expected}') must not be empty.",
                    )
                continue
            if expected != actual:
                self._add_warning(
                    1,
                    f"Breadcrumb part {i + 1} is '{actual}', but template expects '{expected}'.",
                )
        if len(self.current_warnings) == before:
            self._add_passed("Breadcrumbs are present and valid.")

    def _check_breadcrumb_links(self, doc_meta: DocumentMeta) -> None:
        """Validate that every linked part in breadcrumbs points to an existing file.

        Args:
            doc_meta: Metadata extracted from the parsed document.
        """
        if not doc_meta.breadcrumbs or not doc_meta.filepath:
            return

        before = len(self.current_warnings)

        for crumb in doc_meta.breadcrumbs:
            for match in LoaderConstants.RE_LINK.finditer(crumb):
                url = match.group(2)
                exists, _ = self.check_file_exists(url, doc_meta.filepath)
                if not exists:
                    self._add_warning(1, f"Breadcrumb link '{url}' does not point to an existing file.")

        if len(self.current_warnings) == before:
            self._add_passed("All breadcrumb links point to existing files.")

    def _check_mandatory_sections_not_empty(self, doc_map: Dict[str, HeadingInfo], template_headings:
                                                List[HeadingRules]) -> None:
        """Non-optional sections must contain at least some content.

        Args:
            doc_map: Mapping of heading text to HeadingInfo for the document.
            template_headings: Non-H1 heading rules from the template.
        """
        before = len(self.current_warnings)
        for t_heading in template_headings:
            if not t_heading.optional:
                actual = doc_map.get(t_heading.text)
                if actual and actual.content.is_empty:
                    self._add_warning(
                        actual.line_number,
                        f"Mandatory section '{t_heading.text}' is empty.",
                    )
        if len(self.current_warnings) == before:
            self._add_passed("All mandatory sections have content.")

    def _check_section_content(self, actual_content, rules: ContentRules, line_num: int, section_name: str = "") -> None:
        """Validate content within a single section.

        Args:
            actual_content: Parsed content info for the section being validated.
            rules: Expected content rules extracted from the matching template heading.
            line_num: Line number of the section heading, used for error reporting.
            section_name: Display name of the section, used for the passed message.
        """
        if actual_content.is_empty:
            return
        self._check_content_types(actual_content, rules, line_num, section_name)
        self._check_table_headers(actual_content, rules, line_num, section_name)
        self._check_bullet_prefixes(actual_content, rules, line_num, section_name)

        if actual_content.exact_list_prefixes is not []:
            self._check_exact_list_prefix_values(actual_content, section_name)

    def _check_content_types(self,  actual_content, rules: ContentRules, line_num: int, section_name: str) -> None:
        """found_types must be a superset of expected_types (excluding 'text').

        Args:
            actual_content: Parsed content info for the section.
            rules: Expected content rules from the template.
            line_num: Line number of the section heading.
            section_name: Display name of the section.
        """
        expected_non_text = rules.expected_types - {"text"}
        if not expected_non_text:
            self._add_passed(f"Section '{section_name}': no specific content types required.")
            return
        missing_types = expected_non_text - actual_content.found_types
        if missing_types:
            self._add_warning(
                line_num,
                f"Section '{section_name}' is missing expected content types: {sorted(missing_types)}.",
            )
        else:
            self._add_passed(f"Section '{section_name}' has all required content types.")

    def _check_table_headers(self, actual_content, rules: ContentRules, line_num: int, section_name: str) -> None:
        """Table column headers must match the template exactly.

        Args:
            actual_content: Parsed content info for the section.
            rules: Expected content rules from the template.
            line_num: Line number of the section heading.
            section_name: Display name of the section.
        """
        if not rules.table_headers:
            return
        if not actual_content.table_headers:
            self._add_warning(line_num, f"Section '{section_name}' is missing a required table.")
        elif actual_content.table_headers != rules.table_headers:
            self._add_warning(
                line_num,
                f"Section '{section_name}' table headers {actual_content.table_headers} "
                f"do not match expected {rules.table_headers}.",
            )
        else:
            self._add_passed(f"Section '{section_name}' table headers match the template.")

    def _check_bullet_prefixes(self, actual_content, rules: ContentRules, line_num: int, section_name: str) -> None:
        """Bullet prefixes used in the section must belong to the template's allowed set.

        Args:
            actual_content: Parsed content info for the section.
            rules: Expected content rules from the template.
            line_num: Line number of the section heading.
            section_name: Display name of the section.
        """
        if not rules.bullet_prefixes and not rules.exact_list_prefixes:
            return
        before = len(self.current_warnings)
        missing_bullet = rules.bullet_prefixes - actual_content.bullet_prefixes
        if missing_bullet:
            allowed = ", ".join(sorted(rules.bullet_prefixes))
            self._add_warning(
                line_num,
                f"Section '{section_name}' is missing required bullet prefixes. "
                f"Allowed: {allowed}.",
            )
        missing_exact = rules.exact_list_prefixes - actual_content.exact_list_prefixes
        if missing_exact:
            allowed = ", ".join(sorted(rules.exact_list_prefixes))
            self._add_warning(
                line_num,
                f"Section '{section_name}' is missing required list item prefixes. "
                f"Allowed: {allowed}.",
            )
        if len(self.current_warnings) == before:
            self._add_passed(f"Section '{section_name}' has all required bullet prefixes.")

    def _check_exact_list_prefix_values(self, actual_content, section_name: str) -> None:
        """Each [Label](url): list item must have a link value after the colon.

        Args:
            actual_content: Parsed content info for the section.
            section_name: Display name of the section.
        """
        before = len(self.current_warnings)
        for entry in actual_content.raw_lines:
            line = entry["content"]
            line_number = entry["line"]
            m = LoaderConstants.RE_EXACT_LIST_PREFIX.match(line)
            if not m:
                continue
            remainder = line[m.end():].strip()
            if not remainder or not LoaderConstants.RE_LINK.search(remainder):
                label_match = LoaderConstants.RE_LINK.search(m.group(1))
                label = label_match.group(1) if label_match else m.group(1)
                self._add_warning(
                    line_number,
                    f"'{label}' in section '{section_name}' has no value assigned.",
                )
        if len(self.current_warnings) == before:
            self._add_passed(f"Section '{section_name}' all list items have values.")

    def find_markdown_links(self, content: str) -> List[Dict]:
        """Find all markdown links in the content.

        Args:
            content: Raw markdown text to scan.

        Returns:
            List of dicts with keys 'text', 'url', 'type', and 'line_position'.
        """
        if not isinstance(content, str):
            raise InvalidInputError("content", content, "must be a string")
        if not content.strip():
            return []

        links = []
        for match in re.finditer(LoaderConstants.RE_LINK, content):
            text = match.group(1)
            url = match.group(2)
            link_type = (
                "markdown"
                if any(url.endswith(ext) for ext in FileConstants.MARKDOWN_EXTENSIONS)
                else "other"
            )
            links.append({
                "text": text,
                "url": url,
                "type": link_type,
                "line_position": content[: match.start()].count("\n") + 1,
            })
        return links

    def check_file_exists(self, file_path: str, relative_to_file: str) -> Tuple[bool, str]:
        """Check whether a file exists relative to the analysed file's location.

        Args:
            file_path: The file path extracted from a markdown link.
            relative_to_file: Absolute path of the markdown file being analysed.

        Returns:
            (exists, absolute_path) tuple.
        """
        if not isinstance(file_path, str) or not file_path.strip():
            raise InvalidInputError("file_path", file_path, "must be a non-empty string")
        if not isinstance(relative_to_file, str) or not relative_to_file.strip():
            raise InvalidInputError("relative_to_file", relative_to_file, "must be a non-empty string")

        try:
            base_dir = Path(relative_to_file).parent
            full_path = (
                base_dir / file_path
                if not os.path.isabs(file_path)
                else Path(file_path)
            )
            return full_path.exists(), str(full_path.resolve())
        except (OSError, ValueError) as exc:
            logger.warning("Error checking file existence for '%s': %s", file_path, exc)
            return False, ""

    def generate_report(self, analysis: Dict) -> str:
        """Generate a human-readable report of the analysis.

        Args:
            analysis: Dict returned by validate_structure.

        Returns:
            Formatted markdown report string.
        """
        if not isinstance(analysis, dict):
            raise InvalidInputError("analysis", analysis, "must be a dictionary")

        if "error" in analysis:
            return f"Error: {analysis['error']}"

        report = "# Markdown Analysis Report\n\n"

        if analysis:
            warnings = analysis.get("warnings", [])
            passed = analysis.get("passed", [])
            report += "## Structural Validation\n"
            for warn in warnings:
                report += f"{ReportConstants.ICON_WARNING} (line {warn['line']}): {warn['msg']}\n"
            for msg in passed:
                report += f"{ReportConstants.ICON_OK} {msg}\n"
            if not warnings and not passed:
                report += "No checks were performed.\n"
            report += "\n"

        return report

    def get_base_path(self) -> Path:
        """Return the base path used for file operations.

        Returns:
            Root path of the project as a Path object.
        """
        return self.base_path

    def _add_warning(self, line: int, msg: str) -> None:
        """Append a validation warning to the current session.

        Args:
            line: The 1-based line number where the warning occurred.
            msg: A description of the warning.
        """
        self.current_warnings.append({"line": line, "msg": msg})

    def _add_passed(self, msg: str) -> None:
        """Append a passed check message to the current session.

        Args:
            msg: A description of what passed.
        """
        self.current_passed.append(msg)
