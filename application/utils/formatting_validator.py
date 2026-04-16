import re
from typing import List, Dict, Any, Set
from core.constants import LoaderConstants

class FormattingValidator:

    @staticmethod
    def validate_formatting_consistency(raw_lines: List[Dict[str, Any]]) -> List[str]:
        """
        doplnit google docs strings
        """

        warnings = []

        for entry in raw_lines:
            line_content = entry["content"]
            line_number = entry["line"]

            # Excel table - 20 Unclosed bold lettering
            bold_count = len(re.findall(r'(?<!\\)\*\*', line_content))
            if bold_count % 2 != 0:
                warnings.append({ "line": line_number, "msg": f"Unclosed bold formatting (odd number of **)."})

            # Excel table - 21 Unclosed italics
            clean_italic_line = re.sub(r'^\s*\*\s+', '', line_content)
            italic_count = len(re.findall(r'(?<!\*)\*(?!\*)', clean_italic_line))
            if italic_count % 2 != 0:
                warnings.append({ "line": line_number, "msg": "Unclosed italic formatting (odd number of *)." })

            # Excel table - 22 Images missing alt text
            if re.search(r'!\[\s*\]\(', line_content):
                warnings.append({
                    "line": line_number,
                    "msg": "Image is missing alt text (format ![]() is incorrect)."
                })

        

        return warnings