"""Unit tests for utils.formatting_validator — FormattingValidator class."""

import sys
from pathlib import Path
from typing import Dict, Any, List

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from utils.formatting_validator import FormattingValidator


def _entry(content: str, line: int) -> Dict[str, Any]:
    return {"content": content, "line": line}


def _lines(*contents: str) -> List[Dict[str, Any]]:
    return [_entry(c, i + 1) for i, c in enumerate(contents)]


# ---------------------------------------------------------------------------
# check_encoding_errors
# ---------------------------------------------------------------------------

class TestCheckEncodingErrors:

    def test_clean_content_returns_empty(self):
        assert FormattingValidator.check_encoding_errors("Normal text.") == []

    def test_replacement_char_returns_warning(self):
        result = FormattingValidator.check_encoding_errors("Bad � char")
        assert len(result) == 1
        assert result[0]["line"] == 1

    def test_multiple_replacement_chars_one_warning(self):
        result = FormattingValidator.check_encoding_errors("� � �")
        assert len(result) == 1

    def test_empty_string_returns_empty(self):
        assert FormattingValidator.check_encoding_errors("") == []

    def test_warning_message_is_descriptive(self):
        result = FormattingValidator.check_encoding_errors("bad �")
        assert "encoding" in result[0]["msg"].lower()


# ---------------------------------------------------------------------------
# check_bold
# ---------------------------------------------------------------------------

class TestCheckBold:

    def _run(self, line: str, line_number: int = 1) -> List[Dict]:
        warnings: List[Dict] = []
        FormattingValidator.check_bold(line, line_number, warnings)
        return warnings

    def test_closed_bold_no_warning(self):
        assert self._run("**bold text**") == []

    def test_unclosed_bold_warns(self):
        result = self._run("**unclosed bold")
        assert len(result) == 1

    def test_no_bold_markers_no_warning(self):
        assert self._run("plain text") == []

    def test_multiple_closed_bold_no_warning(self):
        assert self._run("**a** and **b**") == []

    def test_three_markers_warns(self):
        result = self._run("**a** **b")
        assert len(result) == 1

    def test_warning_contains_correct_line_number(self):
        result = self._run("**bad", line_number=7)
        assert result[0]["line"] == 7

    def test_warning_appended_to_existing_list(self):
        warnings = [{"line": 1, "msg": "prior"}]
        FormattingValidator.check_bold("**bad", 2, warnings)
        assert len(warnings) == 2

    def test_empty_line_no_warning(self):
        assert self._run("") == []


# ---------------------------------------------------------------------------
# check_italics
# ---------------------------------------------------------------------------

class TestCheckItalics:

    def _run(self, line: str, line_number: int = 1) -> List[Dict]:
        warnings: List[Dict] = []
        FormattingValidator.check_italics(line, line_number, warnings)
        return warnings

    def test_closed_italic_no_warning(self):
        assert self._run("*italic text*") == []

    def test_unclosed_italic_warns(self):
        result = self._run("*unclosed italic")
        assert len(result) == 1

    def test_no_italic_no_warning(self):
        assert self._run("plain text") == []

    def test_bullet_with_star_not_flagged(self):
        assert self._run("* bullet item") == []

    def test_indented_bullet_with_star_not_flagged(self):
        assert self._run("  * indented bullet") == []

    def test_dash_bullet_not_flagged(self):
        assert self._run("- dash bullet") == []

    def test_bold_markers_not_counted_as_italics(self):
        assert self._run("**bold text**") == []

    def test_mixed_bold_and_italic_closed_no_warning(self):
        assert self._run("**bold** and *italic*") == []

    def test_warning_contains_correct_line_number(self):
        result = self._run("*bad", line_number=5)
        assert result[0]["line"] == 5

    def test_empty_line_no_warning(self):
        assert self._run("") == []

    def test_two_unclosed_italics_warns(self):
        result = self._run("*one* *two")
        assert len(result) == 1

    def test_warning_appended_to_existing_list(self):
        warnings = [{"line": 1, "msg": "prior"}]
        FormattingValidator.check_italics("*bad", 2, warnings)
        assert len(warnings) == 2


# ---------------------------------------------------------------------------
# check_image_alt_text
# ---------------------------------------------------------------------------

class TestCheckImageAltText:

    def _run(self, line: str, line_number: int = 1) -> List[Dict]:
        warnings: List[Dict] = []
        FormattingValidator.check_image_alt_text(line, line_number, warnings)
        return warnings

    def test_image_with_alt_no_warning(self):
        assert self._run("![Alt text](image.png)") == []

    def test_image_without_alt_warns(self):
        result = self._run("![](image.png)")
        assert len(result) == 1

    def test_image_with_whitespace_alt_warns(self):
        result = self._run("![ ](image.png)")
        assert len(result) == 1

    def test_no_image_no_warning(self):
        assert self._run("Just plain text") == []

    def test_regular_link_not_flagged(self):
        assert self._run("[link text](page.md)") == []

    def test_warning_contains_correct_line_number(self):
        result = self._run("![](img.png)", line_number=12)
        assert result[0]["line"] == 12

    def test_warning_message_mentions_alt_text(self):
        result = self._run("![](img.png)")
        assert "alt" in result[0]["msg"].lower()

    def test_empty_line_no_warning(self):
        assert self._run("") == []

    def test_warning_appended_to_existing_list(self):
        warnings = [{"line": 1, "msg": "prior"}]
        FormattingValidator.check_image_alt_text("![](img.png)", 2, warnings)
        assert len(warnings) == 2


# ---------------------------------------------------------------------------
# validate_formatting_consistency
# ---------------------------------------------------------------------------

class TestValidateFormattingConsistency:

    def test_clean_lines_return_empty(self):
        lines = _lines("Normal text.", "**bold** and *italic*.")
        assert FormattingValidator.validate_formatting_consistency(lines) == []

    def test_unclosed_bold_detected(self):
        lines = _lines("**unclosed bold")
        result = FormattingValidator.validate_formatting_consistency(lines)
        assert any("bold" in w["msg"].lower() for w in result)

    def test_unclosed_italic_detected(self):
        lines = _lines("*unclosed italic")
        result = FormattingValidator.validate_formatting_consistency(lines)
        assert any("italic" in w["msg"].lower() for w in result)

    def test_missing_alt_text_detected(self):
        lines = _lines("![](img.png)")
        result = FormattingValidator.validate_formatting_consistency(lines)
        assert any("alt" in w["msg"].lower() for w in result)

    def test_empty_lines_list_returns_empty(self):
        assert FormattingValidator.validate_formatting_consistency([]) == []

    def test_multiple_issues_across_lines_all_reported(self):
        lines = _lines("**unclosed", "*unclosed", "![](img.png)")
        result = FormattingValidator.validate_formatting_consistency(lines)
        assert len(result) == 3

    def test_line_numbers_preserved_correctly(self):
        lines = [_entry("normal", 10), _entry("**bad", 20)]
        result = FormattingValidator.validate_formatting_consistency(lines)
        assert result[0]["line"] == 20


# ---------------------------------------------------------------------------
# check_separator
# ---------------------------------------------------------------------------

class TestCheckSeparator:

    def _run(self, content: str, header_columns: int, line: int = 2) -> List[Dict]:
        warnings: List[Dict] = []
        FormattingValidator.check_separator(_entry(content, line), header_columns, warnings)
        return warnings

    def test_valid_separator_no_warning(self):
        assert self._run("|---|---|", header_columns=3) == []

    def test_valid_separator_with_spaces_no_warning(self):
        assert self._run("| --- | --- |", header_columns=3) == []

    def test_left_aligned_no_warning(self):
        assert self._run("|:---|:---|", header_columns=3) == []

    def test_right_aligned_no_warning(self):
        assert self._run("|---:|---:|", header_columns=3) == []

    def test_centered_no_warning(self):
        assert self._run("|:---:|:---:|", header_columns=3) == []

    def test_invalid_separator_warns(self):
        result = self._run("not a separator", header_columns=3)
        assert len(result) == 1
        assert "separator" in result[0]["msg"].lower()

    def test_column_count_mismatch_warns(self):
        result = self._run("|---|", header_columns=3)
        assert len(result) == 1
        assert "column" in result[0]["msg"].lower()

    def test_correct_line_number_in_warning(self):
        result = self._run("bad sep", header_columns=3, line=5)
        assert result[0]["line"] == 5

    def test_warning_appended_to_existing_list(self):
        warnings = [{"line": 1, "msg": "prior"}]
        FormattingValidator.check_separator(_entry("bad", 2), 3, warnings)
        assert len(warnings) == 2


# ---------------------------------------------------------------------------
# check_table_row
# ---------------------------------------------------------------------------

class TestCheckTableRow:

    def _run(self, content: str, header_columns: int, line: int = 3) -> List[Dict]:
        warnings: List[Dict] = []
        FormattingValidator.check_table_row(_entry(content, line), header_columns, warnings)
        return warnings

    def test_valid_row_no_warning(self):
        assert self._run("| a | b |", header_columns=3) == []

    def test_row_not_closed_warns(self):
        result = self._run("| a | b", header_columns=3)
        assert len(result) == 1
        assert "closed" in result[0]["msg"].lower()

    def test_column_count_mismatch_warns(self):
        result = self._run("| a |", header_columns=3)
        assert len(result) == 1
        assert "column" in result[0]["msg"].lower()

    def test_correct_line_number_in_warning(self):
        result = self._run("| a | b", header_columns=3, line=8)
        assert result[0]["line"] == 8

    def test_warning_appended_to_existing_list(self):
        warnings = [{"line": 1, "msg": "prior"}]
        FormattingValidator.check_table_row(_entry("| a | b", 3), 3, warnings)
        assert len(warnings) == 2

    def test_row_with_leading_whitespace_still_validated(self):
        assert self._run("  | a | b |  ", header_columns=3) == []


# ---------------------------------------------------------------------------
# validate_table_consistency
# ---------------------------------------------------------------------------

class TestValidateTableConsistency:

    def test_valid_table_no_warnings(self):
        lines = _lines("| H1 | H2 |", "|---|---|", "| d1 | d2 |")
        assert FormattingValidator.validate_table_consistency(lines) == []

    def test_three_column_table_no_warnings(self):
        lines = _lines("| A | B | C |", "|---|---|---|", "| 1 | 2 | 3 |")
        assert FormattingValidator.validate_table_consistency(lines) == []

    def test_invalid_separator_warns(self):
        lines = _lines("| H1 | H2 |", "not a separator", "| d1 | d2 |")
        result = FormattingValidator.validate_table_consistency(lines)
        assert any("separator" in w["msg"].lower() for w in result)

    def test_data_row_not_closed_warns(self):
        lines = _lines("| H1 | H2 |", "|---|---|", "| d1 | d2")
        result = FormattingValidator.validate_table_consistency(lines)
        assert any("closed" in w["msg"].lower() for w in result)

    def test_data_row_column_mismatch_warns(self):
        lines = _lines("| H1 | H2 |", "|---|---|", "| d1 |")
        result = FormattingValidator.validate_table_consistency(lines)
        assert any("column" in w["msg"].lower() for w in result)

    def test_non_table_content_ignored(self):
        lines = _lines("Just plain text.", "Another line.", "No table here.")
        assert FormattingValidator.validate_table_consistency(lines) == []

    def test_empty_lines_list_returns_empty(self):
        assert FormattingValidator.validate_table_consistency([]) == []

    def test_multiple_data_rows_all_checked(self):
        lines = _lines(
            "| H1 | H2 |",
            "|---|---|",
            "| r1c1 | r1c2 |",
            "| r2c1 | r2c2 |",
            "| r3c1 |",
        )
        result = FormattingValidator.validate_table_consistency(lines)
        assert len(result) == 1
        assert result[0]["line"] == 5

    def test_table_preceded_by_non_table_lines(self):
        lines = _lines(
            "Some intro text.",
            "| H1 | H2 |",
            "|---|---|",
            "| d1 | d2 |",
        )
        assert FormattingValidator.validate_table_consistency(lines) == []

    def test_separator_with_aligned_columns_valid(self):
        lines = _lines("| H1 | H2 |", "|:---|---:|", "| d1 | d2 |")
        assert FormattingValidator.validate_table_consistency(lines) == []


# ---------------------------------------------------------------------------
# run_all_checks
# ---------------------------------------------------------------------------

class TestRunAllChecks:

    def test_clean_document_returns_empty(self):
        lines = _lines("**bold** and *italic*.", "![Alt](img.png)")
        result = FormattingValidator.run_all_checks("**bold** and *italic*.\n![Alt](img.png)", lines)
        assert result == []

    def test_encoding_error_detected(self):
        result = FormattingValidator.run_all_checks("bad � char", [])
        assert any("encoding" in w["msg"].lower() for w in result)

    def test_bold_error_detected(self):
        lines = _lines("**unclosed bold")
        result = FormattingValidator.run_all_checks("**unclosed bold", lines)
        assert any("bold" in w["msg"].lower() for w in result)

    def test_italic_error_detected(self):
        lines = _lines("*unclosed italic")
        result = FormattingValidator.run_all_checks("*unclosed italic", lines)
        assert any("italic" in w["msg"].lower() for w in result)

    def test_missing_alt_text_detected(self):
        lines = _lines("![](img.png)")
        result = FormattingValidator.run_all_checks("![](img.png)", lines)
        assert any("alt" in w["msg"].lower() for w in result)

    def test_table_error_detected(self):
        lines = _lines("| H1 | H2 |", "bad separator", "| d1 | d2 |")
        result = FormattingValidator.run_all_checks("", lines)
        assert any("separator" in w["msg"].lower() for w in result)

    def test_results_sorted_by_line_number(self):
        lines = [
            _entry("**unclosed", 5),
            _entry("*unclosed", 3),
            _entry("![](img.png)", 1),
        ]
        result = FormattingValidator.run_all_checks("", lines)
        line_numbers = [w["line"] for w in result]
        assert line_numbers == sorted(line_numbers)

    def test_empty_inputs_return_empty(self):
        assert FormattingValidator.run_all_checks("", []) == []

    def test_multiple_issues_all_reported(self):
        lines = _lines("**unclosed", "*unclosed", "![](img.png)")
        full = "\n".join(e["content"] for e in lines)
        result = FormattingValidator.run_all_checks(full, lines)
        assert len(result) == 3

    def test_encoding_error_always_at_line_1(self):
        result = FormattingValidator.run_all_checks("� bad content", [])
        assert result[0]["line"] == 1
