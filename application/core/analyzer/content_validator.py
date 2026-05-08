import re
from typing import List, Dict, Any

from utils.constants import ValidationConstants

class ContentValidator:
    """Validator for document content against template-specific rules.

    This class includes methods to check table existency, leftover placeholder text, and missing letters in A-Z groups.

    Attributes:
        raw_lines (List[Dict[str, Any]]): All lines of the document with their 
            original line numbers.
        doc_data (Any): The parsed document object (ParsedDocument) containing 
            structured heading information.
        rules (Any): The template rules object (TemplateRules) to validate against.
        warnings (List[Dict[str, Any]]): Collection of identified content issues.
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

    def check_placeholder_text(self) -> None:
        """
        Scans the document for leftover placeholder or instruction text. Covers excel table 17
        """
        for entry in self.raw_lines:
            line_content = entry["content"]
            line_number = entry["line"]

            if re.search(ValidationConstants.PLACEHOLDER_PATTERN, line_content, re.IGNORECASE):
                self.warnings.append({
                    "line": line_number,
                    "msg": f"Leftover placeholder text '{line_content.strip()}'"
                })


    def check_AZ_groups(self) -> None:
        """
        Verifies that mandatory members of alphabetical groups are present.
        Corresponds excel table 18.
        """
        for heading in self.doc_data.headings:
            rule = next((h for h in self.rules.headings if h.text == heading.text), None)
            if rule and rule.is_group:
                required = set(rule.group_members)
                actual = set(getattr(heading, 'group_members', []))
                
                missing = required - actual
                if missing:
                    sorted_missing = sorted(list(missing))
                    self.warnings.append({
                        "line": heading.line_number,
                        "msg": f"Section '{heading.text}' is missing members: {', '.join(sorted_missing)}."
                    })

    def check_table_existence(self) -> None:
        """
        Ensures mandatory tables are present in specific sections.
        Corresponds to excel table 19.
        """
        for heading in self.doc_data.headings:
            rule = next((h for h in self.rules.headings if h.text == heading.text), None)
            
            if rule and "table" in rule.content_rules.expected_types:
                found_table = getattr(heading, 'has_table', False)
                
                if not found_table:
                    lines = getattr(heading.content, 'raw_lines', [])
                    found_table = any(re.search(r'\|--|\| --', str(line.get("content", ""))) for line in lines)
                
                if not found_table:
                    self.warnings.append({
                        "line": heading.line_number,
                        "msg": f"Section '{heading.text}' must include a table."
                    })

    def run_all_checks(self) -> List[Dict[str, Any]]:
        """
        Executes content-related validation checks.
        Returns:
            A list of dictionaries containing detected issues. Each dictionary 
            has a 'line' (int) and a 'msg' (str).
        """

        self.warnings = []

        self.check_placeholder_text()
        self.check_AZ_groups()
        self.check_table_existence()

        self.warnings.sort(key=lambda x: x['line'])
        return self.warnings