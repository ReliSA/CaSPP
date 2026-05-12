import re
from typing import List, Dict, Any
from utils.constants import ValidationConstants


class FormattingValidator:
    """Validator for Markdown formatting and structural integrity.

    Attributes:
        full_content (str): The entire raw string content of the file.
        raw_lines (List[Dict[str, Any]]): A list of dictionaries, where each dict
            contains 'content' (str) and 'line' (int) for every line in the file.
        warnings (List[Dict[str, Any]]): Collection of identified formatting issues.
        passed (List[str]): Collection of passed check messages.
    """

    def __init__(self, full_content: str, raw_lines: List[Dict[str, Any]]):
        """Initializes the FormattingValidator.

        Args:
            full_content: The entire raw string content of the file.
            raw_lines: List of dictionaries with 'content' (str) and 'line' (int).
        """
        self.full_content = full_content
        self.raw_lines = raw_lines
        self.warnings: List[Dict[str, Any]] = []
        self.passed: List[str] = []

    def check_encoding_errors(self) -> None:
        """Checks for the presence of Unicode replacement characters."""
        if ValidationConstants.UNICODE_REPLACEMENT_CHARACTER in self.full_content:
            self.warnings.append({"line": 1, "msg": "File contains encoding errors (replacement characters found)."})
        else:
            self.passed.append("No encoding errors found.")

    def check_bold(self) -> None:
        """Checks for unclosed bold formatting across all lines."""
        before = len(self.warnings)
        for entry in self.raw_lines:
            bold_count = len(re.findall(ValidationConstants.BOLD_FORMAT, entry["content"]))
            if bold_count % 2 != 0:
                self.warnings.append({"line": entry["line"], "msg": "Unclosed bold formatting (odd number of **)."})
        if len(self.warnings) == before:
            self.passed.append("Bold formatting is consistent.")

    def check_italics(self) -> None:
        """Checks for unclosed italic formatting across all lines."""
        before = len(self.warnings)
        for entry in self.raw_lines:
            clean = re.sub(ValidationConstants.BULLET_POINT, '', entry["content"])
            if len(re.findall(ValidationConstants.ITALICS_FORMAT, clean)) % 2 != 0:
                self.warnings.append({"line": entry["line"], "msg": "Unclosed italic formatting (odd number of *)."})
        if len(self.warnings) == before:
            self.passed.append("Italic formatting is consistent.")

    def check_image_alt_text(self) -> None:
        """Checks for missing alt text in images across all lines."""
        before = len(self.warnings)
        for entry in self.raw_lines:
            if re.search(ValidationConstants.ALT_TEXT, entry["content"]):
                self.warnings.append({"line": entry["line"], "msg": "Image is missing alt text (format ![]() is incorrect)."})
        if len(self.warnings) == before:
            self.passed.append("All images have alt text.")

    def validate_formatting_consistency(self) -> None:
        """Runs all text formatting checks: bold, italics, and image alt text."""
        self.check_bold()
        self.check_italics()
        self.check_image_alt_text()

    def check_separator(self, entry: Dict[str, Any], header_columns: int) -> None:
        """Validates a single table separator row.

        Args:
            entry: The dictionary for the separator line (contains 'content' and 'line').
            header_columns: Count of pipes in the header row.
        """
        sep_line = entry["content"].strip()
        sep_line_number = entry["line"]
        if not re.fullmatch(ValidationConstants.TABLE_SEPARATOR, sep_line):
            self.warnings.append({
                "line": sep_line_number,
                "msg": "Missing or invalid table separator row (| --- |)."
            })
        elif sep_line.count('|') != header_columns:
            self.warnings.append({
                "line": sep_line_number,
                "msg": f"Separator row has {sep_line.count('|') - 1} columns, but header has {header_columns - 1}."
            })

    def check_table_row(self, entry: Dict[str, Any], header_columns: int) -> None:
        """Validates a single data row of a Markdown table.

        Args:
            entry: Dictionary with 'content' and 'line' of the current row.
            header_columns: Number of pipes found in the header row.
        """
        current_line = entry["content"].strip()
        current_line_number = entry["line"]
        if not current_line.endswith('|'):
            self.warnings.append({
                "line": current_line_number,
                "msg": "Table row is not closed with '|'."
            })
        elif current_line.count('|') != header_columns:
            self.warnings.append({
                "line": current_line_number,
                "msg": f"Table row has inconsistent column count ({current_line.count('|') - 1} vs {header_columns - 1})."
            })

    def validate_table_consistency(self) -> None:
        """Validates the structural integrity of all Markdown tables."""
        before = len(self.warnings)
        i = 0
        total_lines = len(self.raw_lines)

        while i < total_lines:
            line_content = self.raw_lines[i]["content"].strip()
            if line_content.startswith('|') and line_content.endswith('|'):
                header_columns = line_content.count('|')
                i += 1
                if i < total_lines:
                    self.check_separator(self.raw_lines[i], header_columns)
                while i + 1 < total_lines and self.raw_lines[i + 1]["content"].strip().startswith('|'):
                    i += 1
                    self.check_table_row(self.raw_lines[i], header_columns)
            i += 1

        if len(self.warnings) == before:
            self.passed.append("Table structure is consistent.")

    def run_all_checks(self) -> List[Dict[str, Any]]:
        """Executes all formatting checks.

        Returns:
            A list of warning dictionaries sorted by line number.
            Passed messages are available via self.passed after this call.
        """
        self.warnings = []
        self.passed = []

        self.check_encoding_errors()
        self.validate_formatting_consistency()
        self.validate_table_consistency()

        self.warnings.sort(key=lambda x: x['line'])
        return self.warnings