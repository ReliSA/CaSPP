import re
from typing import List, Dict, Any

from utils.constants import LoaderConstants, ValidationConstants


class ContentValidator:
    """Validator for document content against template-specific rules.

    Attributes:
        raw_lines (List[Dict[str, Any]]): All lines of the document with their
            original line numbers.
        doc_data (Any): The parsed document object (ParsedDocument) containing
            structured heading information.
        rules (Any): The template rules object (TemplateRules) to validate against.
        warnings (List[Dict[str, Any]]): Collection of identified content issues.
        passed (List[str]): Collection of passed check messages.
    """

    def __init__(self, raw_lines: List[Dict[str, Any]], doc_data: Any, rules: Any):
        """Initializes the ContentValidator.

        Args:
            raw_lines: List of dictionaries with 'content' (str) and 'line' (int).
            doc_data: Structured data from the MarkdownParser.
            rules: Configuration and rules from the TemplateParser.
        """
        self.raw_lines = raw_lines
        self.doc_data = doc_data
        self.rules = rules
        self.warnings: List[Dict[str, Any]] = []
        self.passed: List[str] = []

    def check_section_contents(self) -> None:
        """Validates content within each section against template rules."""
        doc_map = {h.text: h for h in self.doc_data.headings}
        non_h1_headings = [
            h for h in self.rules.headings
            if not (h.level == 1 and h.is_variable)
        ]
        template_h1 = next(
            (h for h in self.rules.headings if h.level == 1 and h.is_variable), None
        )

        self._check_mandatory_sections_not_empty(doc_map, non_h1_headings)

        h1_headings = [h for h in self.doc_data.headings if h.level == 1]
        doc_h1 = h1_headings[0] if len(h1_headings) == 1 else None
        if doc_h1 and template_h1:
            self._check_section_content(
                doc_h1.content, template_h1.content_rules, doc_h1.line_number, doc_h1.text
            )
        for t_heading in non_h1_headings:
            actual = doc_map.get(t_heading.text)
            if actual:
                self._check_section_content(
                    actual.content, t_heading.content_rules, actual.line_number, actual.text
                )

    def _check_mandatory_sections_not_empty(self, doc_map: Dict, template_headings: List) -> None:
        """Non-optional sections must contain at least some content.

        Args:
            doc_map: Mapping of heading text to HeadingInfo for the document.
            template_headings: Non-H1 heading rules from the template.
        """
        before = len(self.warnings)
        for t_heading in template_headings:
            if not t_heading.optional:
                actual = doc_map.get(t_heading.text)
                if actual and actual.content.is_empty:
                    self.warnings.append({
                        "line": actual.line_number,
                        "msg": f"Mandatory section '{t_heading.text}' is empty.",
                    })
        if len(self.warnings) == before:
            self.passed.append("All mandatory sections have content.")

    def _check_section_content(self, actual_content: Any, rules: Any, line_num: int, section_name: str = "") -> None:
        """Validates content within a single section.

        Args:
            actual_content: Parsed content info for the section being validated.
            rules: Expected content rules from the matching template heading.
            line_num: Line number of the section heading.
            section_name: Display name of the section.
        """
        if actual_content.is_empty:
            return
        self._check_content_types(actual_content, rules, line_num, section_name)
        self._check_table_headers(actual_content, rules, line_num, section_name)
        self._check_bullet_prefixes(actual_content, rules, line_num, section_name)
        if actual_content.exact_list_prefixes:
            self._check_exact_list_prefix_values(actual_content, section_name)

    def _check_content_types(self, actual_content: Any, rules: Any, line_num: int, section_name: str) -> None:
        """found_types must be a superset of expected_types, excluding 'text'.

        Args:
            actual_content: Parsed content info for the section.
            rules: Expected content rules from the template.
            line_num: Line number of the section heading.
            section_name: Display name of the section.
        """
        expected_non_text = rules.expected_types - {"text", "footnote", "horizontal_rule"}
        if not expected_non_text:
            self.passed.append(f"Section '{section_name}': no specific content types required.")
            return
        missing_types = expected_non_text - actual_content.found_types
        if missing_types:
            self.warnings.append({
                "line": line_num,
                "msg": f"Section '{section_name}' is missing expected content types: {sorted(missing_types)}.",
            })
        else:
            self.passed.append(f"Section '{section_name}' has all required content types.")

    def _check_table_headers(self, actual_content: Any, rules: Any, line_num: int, section_name: str) -> None:
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
            self.warnings.append({
                "line": line_num,
                "msg": f"Section '{section_name}' is missing a required table.",
            })
        elif actual_content.table_headers != rules.table_headers:
            self.warnings.append({
                "line": line_num,
                "msg": (
                    f"Section '{section_name}' table headers {actual_content.table_headers} "
                    f"do not match expected {rules.table_headers}."
                ),
            })
        else:
            self.passed.append(f"Section '{section_name}' table headers match the template.")

    def _check_bullet_prefixes(self, actual_content: Any, rules: Any, line_num: int, section_name: str) -> None:
        """Bullet prefixes used in the section must belong to the template's allowed set.

        Args:
            actual_content: Parsed content info for the section.
            rules: Expected content rules from the template.
            line_num: Line number of the section heading.
            section_name: Display name of the section.
        """
        if not rules.bullet_prefixes and not rules.exact_list_prefixes:
            return
        before = len(self.warnings)
        missing_bullet = rules.bullet_prefixes - actual_content.bullet_prefixes
        if missing_bullet:
            allowed = ", ".join(sorted(rules.bullet_prefixes))
            self.warnings.append({
                "line": line_num,
                "msg": (
                    f"Section '{section_name}' is missing required bullet prefixes. "
                    f"Allowed: {allowed}."
                ),
            })
        missing_exact = rules.exact_list_prefixes - actual_content.exact_list_prefixes
        if missing_exact:
            allowed = ", ".join(sorted(rules.exact_list_prefixes))
            self.warnings.append({
                "line": line_num,
                "msg": (
                    f"Section '{section_name}' is missing required list item prefixes. "
                    f"Allowed: {allowed}."
                ),
            })
        if len(self.warnings) == before:
            self.passed.append(f"Section '{section_name}' has all required bullet prefixes.")

    def _check_exact_list_prefix_values(self, actual_content: Any, section_name: str) -> None:
        """Each [Label](url): list item must have a link value after the colon.

        Args:
            actual_content: Parsed content info for the section.
            section_name: Display name of the section.
        """
        before = len(self.warnings)
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
                self.warnings.append({
                    "line": line_number,
                    "msg": f"'{label}' in section '{section_name}' has no value assigned.",
                })
        if len(self.warnings) == before:
            self.passed.append(f"Section '{section_name}' all list items have values.")


    def check_placeholder_text(self) -> None:
        """Scans the document for leftover placeholder or instruction text."""
        for entry in self.raw_lines:
            line_content = entry["content"]
            line_number = entry["line"]
            if re.search(ValidationConstants.PLACEHOLDER_PATTERN, line_content, re.IGNORECASE):
                self.warnings.append({
                    "line": line_number,
                    "msg": f"Leftover placeholder text '{line_content.strip()}'"
                })

    def check_AZ_groups(self) -> None:
        """Verifies that mandatory members of alphabetical groups are present."""
        for heading in self.doc_data.headings:
            rule = next((h for h in self.rules.headings if h.text == heading.text), None)
            if rule and rule.is_group:
                required = set(rule.group_members)
                actual = set(getattr(heading, 'group_members', []))
                missing = required - actual
                if missing:
                    self.warnings.append({
                        "line": heading.line_number,
                        "msg": f"Section '{heading.text}' is missing members: {', '.join(sorted(missing))}."
                    })

    def check_table_existence(self) -> None:
        """Ensures mandatory tables are present in specific sections."""
        for heading in self.doc_data.headings:
            rule = next((h for h in self.rules.headings if h.text == heading.text), None)
            if rule and "table" in rule.content_rules.expected_types:
                found_table = getattr(heading, 'has_table', False)
                if not found_table:
                    lines = getattr(heading.content, 'raw_lines', [])
                    found_table = any(
                        re.search(r'\|--|\| --', str(line.get("content", ""))) for line in lines
                    )
                if not found_table:
                    self.warnings.append({
                        "line": heading.line_number,
                        "msg": f"Section '{heading.text}' must include a table."
                    })


    def run_all_checks(self) -> List[Dict[str, Any]]:
        """Executes all content-related validation checks.

        Returns:
            A list of warning dictionaries, each with 'line' (int) and 'msg' (str).
            Passed messages are available via self.passed after this call.
        """
        self.warnings = []
        self.passed = []

        self.check_section_contents()
        self.check_placeholder_text()
        self.check_AZ_groups()
        self.check_table_existence()

        self.warnings.sort(key=lambda x: x['line'])
        return self.warnings