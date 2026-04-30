import re
from typing import List, Dict, Any, Set
from core.constants import ValidationConstants

class FormattingValidator:
    """Validator for Markdown formatting and structural integrity.

    This class includes methods to check text formatting (bold, italics), image syntax, encoding errors,
    and the structural consistency of Markdown tables.

    Attributes:
        full_content (str): The entire raw string content of the file.
        raw_lines (List[Dict[str, Any]]): A list of dictionaries, where each dict
            contains 'content' (str) and 'line' (int) for every line in the file.
        warnings (List[Dict[str, Any]]): A collection of identified issues found
            during the validation process.
    """
    
    def __init__(self, full_content: str, raw_lines: List[Dict[str, Any]]):
        """
        Tady si objekt při vytvoření uloží vše, co potřebuje.
        Už to nemusíme posílat každé metodě zvlášť.
        """
        self.full_content = full_content
        self.raw_lines = raw_lines
        self.warnings = []  # Tady si budeme sbírat chyby


    def check_encoding_errors(self) -> None:
        """
        Checks for the presence of Unicode replacement characters. (Excel table 23)

        This method validates if the document contains the '' character 
        (\\ufffd), which usually indicates that an encoding error occurred 
        during file reading. 

        Args: None (Uses self.full_content)

        Returns: None
        """
        if "\ufffd" in self.full_content:
            self.warnings.append({"line": 1, "msg": "File contains encoding errors (replacement characters found)."})

    def check_bold(self, line_content: str, line_number: int):
        """
        Checks for unclosed bold formatting in a single line. Excel table - 20

        Args:
            line_content: The raw text content of the line.
            line_number: The 1-based line number for error reporting.
        """

        bold_count = len(re.findall(ValidationConstants.BOLD_FORMAT , line_content))
        if bold_count % 2 != 0:
            self.warnings.append({ "line": line_number, "msg": f"Unclosed bold formatting (odd number of **)."})

    def check_italics(self, line_content: str, line_number: int):
        """
        Checks for unclosed italics formatting in a single line. Excel table - 21

        Args:
            line_content: The raw text content of the line.
            line_number: The 1-based line number for error reporting.
        """
        clean_italic_line = re.sub(ValidationConstants.BULLET_POINT, '', line_content)
        italic_count = len(re.findall(ValidationConstants.ITALICS_FORMAT, clean_italic_line))
        if italic_count % 2 != 0:
            self.warnings.append({ "line": line_number, "msg": "Unclosed italic formatting (odd number of *)." })

    def check_image_alt_text(self, line_content: str, line_number: int):
        """
        Checks for missing alt text in images - Excel table 22

        Args:
            line_content: The raw text content of the line.
            line_number: The 1-based line number for error reporting.
        """
        if re.search(ValidationConstants.ALT_TEXT, line_content):
            self.warnings.append({ "line": line_number, "msg": "Image is missing alt text (format ![]() is incorrect)."})

    def validate_formatting_consistency(self) -> None:
        """
        Runs control of text formatting (Bold, italics and alt text of images) - coresponds to Excel table 20, 21, 22
        """

        for entry in self.raw_lines:
            line_content = entry["content"]
            line_number = entry["line"]

            self.check_bold(line_content, line_number)
            self.check_italics(line_content, line_number)
            self.check_image_alt_text(line_content, line_number)
    
    def check_separator(self, entry: Dict[str, Any], header_columns: int):
        """
        Validates the table separator row.
        
        Args:
            entry: The dictionary for the separator line (contains 'content' and 'line').
            header_columns: Count of pipes in the header row.
        """
        sep_line = entry["content"].strip()
        sep_line_number = entry["line"]
        
        # Valid separators | --- | :--- | ---: | :---: |
        if not re.fullmatch(ValidationConstants.TABLE_SEPARATOR, sep_line):
            self.warnings.append({
                "line": sep_line_number,
                "msg": "Missing or invalid table separator row (| --- |)."
            })
        elif sep_line.count('|') != header_columns:
            self.warnings.append({
                "line": sep_line_number,
                "msg": f"Separator row has {sep_line.count('|')-1} columns, but header has {header_columns-1}."
            })
    
    def check_table_row(self, entry: Dict[str, Any], header_columns: int):
        """
        Validates a single data row of a Markdown table. (Excel table 24)

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
                "msg": f"Table row has inconsistent column count ({current_line.count('|')-1} vs {header_columns-1})."
            })

    def validate_table_consistency(self,) -> None:

        """
        Validates the structural integrity of Markdown tables.
        """
        i = 0
        total_lines = len(self.raw_lines)

        while i < total_lines:
            line_content = self.raw_lines[i]["content"].strip()

            # Detection that line starts and ends with "|"
            if line_content.startswith('|') and line_content.endswith('|'):
                header_columns = line_content.count('|')

                i += 1               
                if i < total_lines:
                    self.check_separator(self.raw_lines[i], header_columns)

                while i + 1 < total_lines and self.raw_lines[i+1]["content"].strip().startswith('|'):
                    i += 1
                    self.check_table_row(self.raw_lines[i], header_columns)

            i += 1
    

    def run_all_checks(self) -> List[Dict[str, Any]]:
        """
        Executes all the formatting checks

        Returns:
            A list of dictionaries representing all identified formatting issues, 
            sorted by line number. Each dictionary contains:
                - 'line' (int): The line number where the issue was found.
                - 'msg' (str): A descriptive warning message.
        """
        self.warnings = []
        
        # Control of special symbols (23)
        self.check_encoding_errors()
        # Control of Text formatting (Bold, Italics, Alt-text - 20, 21, 22)
        self.validate_formatting_consistency()
        # Control of table formatting (24)
        self.validate_table_consistency()
        
        self.warnings.sort(key=lambda x: x['line'])
        
        return self.warnings