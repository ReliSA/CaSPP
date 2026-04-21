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
            base_path: Root path of the project. Defaults to the repository root
                       inferred from the location of this file.
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
  
        # Formatting
        all_raw_lines = []
        for heading in doc.headings:
            all_raw_lines.extend(heading.content.raw_lines)

        formatting_validator = FormattingValidator(
            full_content=getattr(doc, 'raw_content', ""),
            raw_lines=all_raw_lines
        )
        formatting_warnings = formatting_validator.run_all_checks()
        self.current_warnings.extend(formatting_warnings)
        
        if not formatting_warnings:
            self._add_passed("Formatting (bold, italics, tables, images) is consistent.")    
        
        # Breadcrumbs
        self._validate_breadcrumbs(doc.meta, template.document_rules)

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

        # Content checks per matched section TODO - Need more robust checks
        # if doc_h1 and template_h1:
        #     self._check_section_content(doc_h1.content, template_h1.content_rules, doc_h1.line_number, doc_h1.text)
        # for t_heading in non_h1_headings:
        #     actual = doc_map.get(t_heading.text)
        #     if actual:
        #         self._check_section_content(actual.content, t_heading.content_rules, actual.line_number, actual.text)

        return {
            "file": doc.meta.filepath,
            "warnings": self.current_warnings,
            "passed": self.current_passed,
        }

    def _check_h1_count(self, h1_headings: List[HeadingInfo]) -> None:
        """Document must contain exactly one H1 heading.

        Args:
            h1_headings: All HeadingInfo objects whose level equals 1.

        Returns:
            None: Warnings are appended to self.current_warnings.
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

        When the H1 has a prefix (e.g. "Category: Agile"), only the value part
        ("Agile") is compared to the stem. For plain titles the full text is used.

        Args:
            meta: Metadata extracted from the parsed document.

        Returns:
            None: Warnings are appended to self.current_warnings.
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

        Returns:
            None: Warnings are appended to self.current_warnings.
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

        Returns:
            None: Warnings are appended to self.current_warnings.
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

        Only headings that are present in both the document and the template are
        considered. The check verifies that their template-index sequence is
        monotonically non-decreasing.

        Note: Optional section names are validated implicitly because sections
        are matched by exact text.

        Args:
            doc_headings: All headings extracted from the document, in document order.
            template_headings: Non-H1 heading rules from the template, in template order.

        Returns:
            None: Warnings are appended to self.current_warnings.
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

        Returns:
            None: Warnings are appended to self.current_warnings.
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

        Returns:
            None: Warnings are appended to self.current_warnings.
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

    # ------------------------------------------------------------------ #
    # Breadcrumbs                                                         #
    # ------------------------------------------------------------------ #

    def _validate_breadcrumbs(self, doc_meta: DocumentMeta, doc_rules: DocumentRules) -> None:
        """Validate the breadcrumb navigation line.

        Breadcrumbs must be present, have the same number of parts as the
        template (separated by '>'), and each fixed part must textually match
        the template. Parts wrapped in '*...*' are treated as wildcards and
        must only be non-empty.

        Args:
            doc_meta: Metadata extracted from the parsed document.
            doc_rules: Document-level rules from the matched template.

        Returns:
            None: Warnings are appended to self.current_warnings.
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

    def _check_section_content(
        self,
        actual_content,
        rules: ContentRules,
        line_num: int,
        section_name: str = "",
    ) -> None:
        """Validate content within a single section.

        Table column headers must match the template exactly and all required
        list prefixes defined in the template must be present.

        Args:
            actual_content: Parsed content info for the section being validated.
            rules: Expected content rules extracted from the matching template heading.
            line_num: Line number of the section heading, used for error reporting.
            section_name: Display name of the section, used for the passed message.

        Returns:
            None: Warnings are appended to self.current_warnings.
        """
        before = len(self.current_warnings)

        # Table headers
        if rules.table_headers:
            if not actual_content.table_headers:
                self._add_warning(line_num, "Section is missing a required table.")
            elif actual_content.table_headers != rules.table_headers:
                self._add_warning(
                    line_num,
                    f"Table headers {actual_content.table_headers} "
                    f"do not match expected {rules.table_headers}.",
                )

        # Required list prefixes
        for prefix in rules.bullet_prefixes:
            if prefix not in actual_content.bullet_prefixes:
                self._add_warning(
                    line_num,
                    f"Required bullet prefix '{prefix}' is missing from section.",
                )
        for prefix in rules.exact_list_prefixes:
            if prefix not in actual_content.exact_list_prefixes:
                self._add_warning(
                    line_num,
                    f"Required list item prefix '{prefix}' is missing from section.",
                )

        if len(self.current_warnings) == before:
            label = f"'{section_name}'" if section_name else f"at line {line_num}"
            self._add_passed(f"Section {label} content is valid.")

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

    def extract_headings(self, content: str) -> List[Dict]:
        """Extract all headings from markdown content.

        Args:
            content: Raw markdown text.

        Returns:
            List of dicts with keys 'level', 'text', and 'line'.
        """
        if not isinstance(content, str):
            raise InvalidInputError("content", content, "must be a string")
        if not content.strip():
            return []

        headings = []
        for line_num, line in enumerate(content.split("\n"), 1):
            match = re.match(LoaderConstants.RE_HEADING, line.strip())
            if match:
                headings.append({
                    "level": len(match.group(1)),
                    "text": match.group(2),
                    "line": line_num,
                })
        return headings

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

        Returns:
            None: Warnings are appended to self.current_warnings.
        """
        self.current_warnings.append({"line": line, "msg": msg})

    def _add_passed(self, msg: str) -> None:
        """Append a passed check message to the current session.

        Args:
            msg: A description of what passed.

        Returns:
            None: Messages are appended to self.current_passed.
        """
        self.current_passed.append(msg)
