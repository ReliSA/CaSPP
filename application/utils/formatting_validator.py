import re
from typing import List, Dict, Any, Set
from core.constants import LoaderConstants

class FormattingValidator:

    @staticmethod
    def check_encoding_errors(full_content: str) -> List[Dict[str, Any]]:
        """Checks for the presence of Unicode replacement characters. (Excel table 23).

        Args:
            full_content: The entire raw string content of the markdown file.

        Returns:
            A list of dictionaries, each containing 'line' (int) and 'msg' (str). Returns an empty list if no encoding errors are found.
        """
        warnings = []
        if "\ufffd" in full_content:
            warnings.append({"line": 1, "msg": "File contains encoding errors (replacement characters found)."})
        return warnings

    @staticmethod
    def check_bold(line_content: str, line_number: int, warnings: List[Dict]):
        """Checks for unclosed bold formatting in a single line. Excel table - 20.

        Args:
            line_content: The raw text content of the line.
            line_number: The 1-based line number for error reporting.
            warnings: The list to which any identified warnings are appended.
        """

        bold_count = len(re.findall(r'(?<!\\)\*\*', line_content))
        if bold_count % 2 != 0:
            warnings.append({ "line": line_number, "msg": f"Unclosed bold formatting (odd number of **)."})

    @staticmethod
    def check_italics(line_content: str, line_number: int, warnings: List[Dict]):
        """Checks for unclosed italics formatting in a single line. Excel table - 21.

        Args:
            line_content: The raw text content of the line.
            line_number: The 1-based line number for error reporting.
            warnings: The list to which any identified warnings are appended.
        """

        clean_italic_line = re.sub(r'^\s*\*\s+', '', line_content)
        italic_count = len(re.findall(r'(?<!\*)\*(?!\*)', clean_italic_line))
        if italic_count % 2 != 0:
            warnings.append({ "line": line_number, "msg": "Unclosed italic formatting (odd number of *)." })

    @staticmethod
    def check_image_alt_text(line_content: str, line_number: int, warnings: List[Dict]):
        """Checks for missing alt text in images - Excel table 22.

        Args:
            line_content: The raw text content of the line.
            line_number: The 1-based line number for error reporting.
            warnings: The list to which any identified warnings are appended.
        """
        if re.search(r'!\[\s*\]\(', line_content):
            warnings.append({ "line": line_number, "msg": "Image is missing alt text (format ![]() is incorrect)."})

    @staticmethod
    def validate_formatting_consistency(raw_lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Runs control of text formatting (Bold, italics and alt text of images) - coresponds to Excel table 20, 21, 22.

        Args:
            raw_lines: A list of dictionaries representing document lines. Each dictionary must contain: - 'content' (str): The raw text of the line. - 'line' (int): The 1-based line number for error reporting.

        Returns:
            A list of dictionaries, each containing: - 'line' (int): The line number where the issue was found. - 'msg' (str): A descriptive warning message.
        """

        warnings = []

        for entry in raw_lines:
            line_content = entry["content"]
            line_number = entry["line"]

            FormattingValidator.check_bold(line_content, line_number, warnings)
            FormattingValidator.check_italics(line_content, line_number, warnings)
            FormattingValidator.check_image_alt_text(line_content, line_number, warnings)

        return warnings
    
    @staticmethod
    def check_separator(entry: Dict[str, Any], header_columns: int, warnings: List[Dict]):
        """Validates the table separator row.

        Args:
            entry: The dictionary for the separator line (contains 'content' and 'line').
            header_columns: Count of pipes in the header row.
            warnings: List to append findings.
        """
        sep_line = entry["content"].strip()
        sep_line_number = entry["line"]
        
        # Valid separators | --- | :--- | ---: | :---: |
        if not re.fullmatch(r'\|(?:\s*:?-+:?\s*\|)+', sep_line):
            warnings.append({
                "line": sep_line_number,
                "msg": "Missing or invalid table separator row (| --- |)."
            })
        elif sep_line.count('|') != header_columns:
            warnings.append({
                "line": sep_line_number,
                "msg": f"Separator row has {sep_line.count('|')-1} columns, but header has {header_columns-1}."
            })
    
    @staticmethod
    def check_table_row(entry: Dict[str, Any], header_columns: int, warnings: List[Dict]):
        """Validates a single data row of a Markdown table. (Excel table 24).

        Args:
            entry: Dictionary with 'content' and 'line' of the current row.
            header_columns: Number of pipes found in the header row.
            warnings: List to append formatting issues.
        """
        current_line = entry["content"].strip()
        current_line_number = entry["line"]

        if not current_line.endswith('|'):
            warnings.append({
                "line": current_line_number,
                "msg": "Table row is not closed with '|'."
            })
        elif current_line.count('|') != header_columns:
            warnings.append({
                "line": current_line_number,
                "msg": f"Table row has inconsistent column count ({current_line.count('|')-1} vs {header_columns-1})."
            })

    @staticmethod
    def validate_table_consistency(raw_lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

        """Validates the structural integrity of Markdown tables.

        Args:
            raw_lines: A list of dictionaries representing document lines. Each dictionary must contain: - 'content' (str): The raw text of the line. - 'line' (int): The 1-based line number for error reporting.

        Returns:
            A list of dictionaries, each containing: - 'line' (int): The line number where the structural issue was found. - 'msg' (str): A descriptive warning message about the error.
        """
        warnings = []
        i = 0
        total_lines = len(raw_lines)

        while i < total_lines:
            line_content = raw_lines[i]["content"].strip()

            # Detection that line starts and ends with "|"
            if line_content.startswith('|') and line_content.endswith('|'):
                header_columns = line_content.count('|')

                i += 1               
                if i < total_lines:
                    FormattingValidator.check_separator(raw_lines[i], header_columns, warnings)

                while i + 1 < total_lines and raw_lines[i+1]["content"].strip().startswith('|'):
                    i += 1
                    FormattingValidator.check_table_row(raw_lines[i], header_columns, warnings)

            i += 1

        return warnings
    
    
    @staticmethod
    def run_all_checks(full_content: str, raw_lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Executes all the formatting checks.

        Args:
            full_content: The entire raw string content of the markdown file (used for encoding check).
            raw_lines: A list of dictionaries representing document lines, where each dict contains 'content' (str) and 'line' (int).

        Returns:
            A list of dictionaries representing all identified formatting issues, sorted by line number. Each dictionary contains: - 'line' (int): The line number where the issue was found. - 'msg' (str): A descriptive warning message.
        """
        all_warnings = []
        
        # Control of special symbols (23)
        all_warnings.extend(FormattingValidator.check_encoding_errors(full_content))
        
        # Control of Text formatting (Bold, Italics, Alt-text - 20, 21, 22)
        all_warnings.extend(FormattingValidator.validate_formatting_consistency(raw_lines))
        
        # Control of table formatting
        all_warnings.extend(FormattingValidator.validate_table_consistency(raw_lines))
        
        all_warnings.sort(key=lambda x: x['line'])
        
        return all_warnings
