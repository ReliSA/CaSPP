"""Unit tests for core.analyzer.content_validator — ContentValidator class."""

import sys
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import MagicMock

APP_DIR = Path(__file__).resolve().parents[2]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from core.analyzer.content_validator import ContentValidator
from utils.parsers.template_parser import ContentRules, HeadingRules


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _entry(content: str, line: int) -> Dict[str, Any]:
    return {"content": content, "line": line}


def _lines(*contents: str) -> List[Dict[str, Any]]:
    return [_entry(c, i + 1) for i, c in enumerate(contents)]


def _rule_heading(text: str, is_group: bool = False, group_members: List[str] = None,
                  expected_types: set = None) -> HeadingRules:
    content_rules = ContentRules(expected_types=expected_types or {"text"})
    return HeadingRules(
        level=2,
        text=text,
        is_group=is_group,
        group_members=group_members or [],
        content_rules=content_rules,
    )


def _doc_heading(text: str, line_number: int = 1, group_members: List[str] = None,
                 has_table: bool = False, raw_lines: List[Dict] = None) -> MagicMock:
    h = MagicMock()
    h.text = text
    h.line_number = line_number
    h.group_members = group_members or []
    h.has_table = has_table
    h.content.raw_lines = raw_lines or []
    return h


def _rules(headings: List[HeadingRules]) -> MagicMock:
    r = MagicMock()
    r.headings = headings
    return r


def _doc(headings: List[MagicMock]) -> MagicMock:
    d = MagicMock()
    d.headings = headings
    return d


def _validator(raw_lines: List[Dict] = None, headings: List[MagicMock] = None,
               rule_headings: List[HeadingRules] = None) -> ContentValidator:
    return ContentValidator(
        raw_lines=raw_lines or [],
        doc_data=_doc(headings or []),
        rules=_rules(rule_headings or []),
    )


# ---------------------------------------------------------------------------
# check_placeholder_text
# ---------------------------------------------------------------------------

class TestCheckPlaceholderText:

    def test_clean_line_no_warning(self):
        v = _validator(raw_lines=_lines("Normal text without placeholders."))
        v.check_placeholder_text()
        assert v.warnings == []

    def test_placeholder_remove_warns(self):
        v = _validator(raw_lines=_lines("_remove this text_"))
        v.check_placeholder_text()
        assert len(v.warnings) == 1

    def test_placeholder_insert_warns(self):
        v = _validator(raw_lines=_lines("*insert something here*"))
        v.check_placeholder_text()
        assert len(v.warnings) == 1

    def test_placeholder_optional_warns(self):
        v = _validator(raw_lines=_lines("***optional***"))
        v.check_placeholder_text()
        assert len(v.warnings) == 1

    def test_placeholder_replace_warns(self):
        v = _validator(raw_lines=_lines("_replace this_"))
        v.check_placeholder_text()
        assert len(v.warnings) == 1

    def test_placeholder_choose_warns(self):
        v = _validator(raw_lines=_lines("*choose one*"))
        v.check_placeholder_text()
        assert len(v.warnings) == 1

    def test_placeholder_example_warns(self):
        v = _validator(raw_lines=_lines("_example text_"))
        v.check_placeholder_text()
        assert len(v.warnings) == 1

    def test_placeholder_case_insensitive(self):
        v = _validator(raw_lines=_lines("_REMOVE this text_"))
        v.check_placeholder_text()
        assert len(v.warnings) == 1

    def test_warning_contains_correct_line_number(self):
        raw = [_entry("Normal line", 1), _entry("_remove this_", 5)]
        v = _validator(raw_lines=raw)
        v.check_placeholder_text()
        assert v.warnings[0]["line"] == 5

    def test_warning_message_contains_line_content(self):
        v = _validator(raw_lines=_lines("  _insert value_  "))
        v.check_placeholder_text()
        assert "_insert value_" in v.warnings[0]["msg"]

    def test_multiple_placeholder_lines_warn_each(self):
        v = _validator(raw_lines=_lines("_remove this_", "clean", "*replace this*"))
        v.check_placeholder_text()
        assert len(v.warnings) == 2

    def test_empty_raw_lines_no_warnings(self):
        v = _validator(raw_lines=[])
        v.check_placeholder_text()
        assert v.warnings == []

    def test_word_remove_without_markers_no_warning(self):
        v = _validator(raw_lines=_lines("You can remove this section manually."))
        v.check_placeholder_text()
        assert v.warnings == []


# ---------------------------------------------------------------------------
# check_AZ_groups
# ---------------------------------------------------------------------------

class TestCheckAZGroups:

    def test_no_headings_no_warnings(self):
        v = _validator()
        v.check_AZ_groups()
        assert v.warnings == []

    def test_heading_with_no_matching_rule_no_warning(self):
        doc_h = _doc_heading("Unknown Section", group_members=["A", "B"])
        rule_h = _rule_heading("Other Section", is_group=True, group_members=["A", "B", "C"])
        v = _validator(headings=[doc_h], rule_headings=[rule_h])
        v.check_AZ_groups()
        assert v.warnings == []

    def test_matching_rule_not_group_no_warning(self):
        doc_h = _doc_heading("Patterns", group_members=[])
        rule_h = _rule_heading("Patterns", is_group=False, group_members=["A", "B"])
        v = _validator(headings=[doc_h], rule_headings=[rule_h])
        v.check_AZ_groups()
        assert v.warnings == []

    def test_all_required_members_present_no_warning(self):
        doc_h = _doc_heading("Patterns", group_members=["A", "B", "C"])
        rule_h = _rule_heading("Patterns", is_group=True, group_members=["A", "B", "C"])
        v = _validator(headings=[doc_h], rule_headings=[rule_h])
        v.check_AZ_groups()
        assert v.warnings == []

    def test_missing_one_member_warns(self):
        doc_h = _doc_heading("Patterns", group_members=["A", "B"])
        rule_h = _rule_heading("Patterns", is_group=True, group_members=["A", "B", "C"])
        v = _validator(headings=[doc_h], rule_headings=[rule_h])
        v.check_AZ_groups()
        assert len(v.warnings) == 1
        assert "C" in v.warnings[0]["msg"]

    def test_missing_multiple_members_warns(self):
        doc_h = _doc_heading("Patterns", group_members=["A"])
        rule_h = _rule_heading("Patterns", is_group=True, group_members=["A", "B", "C"])
        v = _validator(headings=[doc_h], rule_headings=[rule_h])
        v.check_AZ_groups()
        assert len(v.warnings) == 1
        assert "B" in v.warnings[0]["msg"]
        assert "C" in v.warnings[0]["msg"]

    def test_warning_mentions_section_name(self):
        doc_h = _doc_heading("Patterns", group_members=[])
        rule_h = _rule_heading("Patterns", is_group=True, group_members=["A"])
        v = _validator(headings=[doc_h], rule_headings=[rule_h])
        v.check_AZ_groups()
        assert "Patterns" in v.warnings[0]["msg"]

    def test_warning_uses_heading_line_number(self):
        doc_h = _doc_heading("Patterns", line_number=42, group_members=[])
        rule_h = _rule_heading("Patterns", is_group=True, group_members=["A"])
        v = _validator(headings=[doc_h], rule_headings=[rule_h])
        v.check_AZ_groups()
        assert v.warnings[0]["line"] == 42

    def test_extra_members_in_doc_not_flagged(self):
        doc_h = _doc_heading("Patterns", group_members=["A", "B", "C", "D"])
        rule_h = _rule_heading("Patterns", is_group=True, group_members=["A", "B"])
        v = _validator(headings=[doc_h], rule_headings=[rule_h])
        v.check_AZ_groups()
        assert v.warnings == []


# ---------------------------------------------------------------------------
# check_table_existence
# ---------------------------------------------------------------------------

class TestCheckTableExistence:

    def test_no_headings_no_warnings(self):
        v = _validator()
        v.check_table_existence()
        assert v.warnings == []

    def test_heading_without_matching_rule_no_warning(self):
        doc_h = _doc_heading("Results", has_table=False)
        rule_h = _rule_heading("Other Section", expected_types={"table"})
        v = _validator(headings=[doc_h], rule_headings=[rule_h])
        v.check_table_existence()
        assert v.warnings == []

    def test_rule_without_table_requirement_no_warning(self):
        doc_h = _doc_heading("Context", has_table=False)
        rule_h = _rule_heading("Context", expected_types={"text"})
        v = _validator(headings=[doc_h], rule_headings=[rule_h])
        v.check_table_existence()
        assert v.warnings == []

    def test_has_table_attribute_true_no_warning(self):
        doc_h = _doc_heading("Results", has_table=True)
        rule_h = _rule_heading("Results", expected_types={"table"})
        v = _validator(headings=[doc_h], rule_headings=[rule_h])
        v.check_table_existence()
        assert v.warnings == []

    def test_no_table_found_warns(self):
        doc_h = _doc_heading("Results", has_table=False, raw_lines=_lines("Some text"))
        rule_h = _rule_heading("Results", expected_types={"table"})
        v = _validator(headings=[doc_h], rule_headings=[rule_h])
        v.check_table_existence()
        assert len(v.warnings) == 1
        assert "Results" in v.warnings[0]["msg"]

    def test_separator_in_raw_lines_counts_as_table(self):
        raw = _lines("| Col1 | Col2 |", "|---|---|", "| A | B |")
        doc_h = _doc_heading("Results", has_table=False, raw_lines=raw)
        rule_h = _rule_heading("Results", expected_types={"table"})
        v = _validator(headings=[doc_h], rule_headings=[rule_h])
        v.check_table_existence()
        assert v.warnings == []

    def test_spaced_separator_in_raw_lines_counts_as_table(self):
        raw = _lines("| Col |", "| -- |", "| val |")
        doc_h = _doc_heading("Results", has_table=False, raw_lines=raw)
        rule_h = _rule_heading("Results", expected_types={"table"})
        v = _validator(headings=[doc_h], rule_headings=[rule_h])
        v.check_table_existence()
        assert v.warnings == []

    def test_warning_uses_heading_line_number(self):
        doc_h = _doc_heading("Results", line_number=15, has_table=False, raw_lines=[])
        rule_h = _rule_heading("Results", expected_types={"table"})
        v = _validator(headings=[doc_h], rule_headings=[rule_h])
        v.check_table_existence()
        assert v.warnings[0]["line"] == 15

    def test_warning_message_mentions_table(self):
        doc_h = _doc_heading("Results", has_table=False, raw_lines=[])
        rule_h = _rule_heading("Results", expected_types={"table"})
        v = _validator(headings=[doc_h], rule_headings=[rule_h])
        v.check_table_existence()
        assert "table" in v.warnings[0]["msg"].lower()

    def test_empty_raw_lines_warns_when_table_required(self):
        doc_h = _doc_heading("Results", has_table=False, raw_lines=[])
        rule_h = _rule_heading("Results", expected_types={"table"})
        v = _validator(headings=[doc_h], rule_headings=[rule_h])
        v.check_table_existence()
        assert len(v.warnings) == 1


# ---------------------------------------------------------------------------
# run_all_checks
# ---------------------------------------------------------------------------

class TestRunAllChecks:

    def test_returns_list(self):
        v = _validator()
        assert isinstance(v.run_all_checks(), list)

    def test_clean_doc_returns_empty_list(self):
        v = _validator(raw_lines=_lines("Clean content."))
        assert v.run_all_checks() == []

    def test_warnings_sorted_by_line(self):
        # Placeholder on line 5, missing table section on line 2
        raw = [_entry("clean", 1), _entry("clean", 2), _entry("clean", 3),
               _entry("clean", 4), _entry("_remove_", 5)]
        doc_h = _doc_heading("Results", line_number=2, has_table=False, raw_lines=[])
        rule_h = _rule_heading("Results", expected_types={"table"})
        v = _validator(raw_lines=raw, headings=[doc_h], rule_headings=[rule_h])
        result = v.run_all_checks()
        lines = [w["line"] for w in result]
        assert lines == sorted(lines)

    def test_warnings_reset_on_each_call(self):
        v = _validator(raw_lines=_lines("_remove_"))
        first = v.run_all_checks()
        second = v.run_all_checks()
        assert first == second

    def test_aggregates_warnings_from_all_checks(self):
        # placeholder text + missing AZ member + missing table
        raw = _lines("_insert value_")
        doc_h_group = _doc_heading("Patterns", line_number=3, group_members=["A"])
        doc_h_table = _doc_heading("Results", line_number=2, has_table=False, raw_lines=[])
        rule_group = _rule_heading("Patterns", is_group=True, group_members=["A", "B"])
        rule_table = _rule_heading("Results", expected_types={"table"})
        v = _validator(
            raw_lines=raw,
            headings=[doc_h_group, doc_h_table],
            rule_headings=[rule_group, rule_table],
        )
        result = v.run_all_checks()
        assert len(result) >= 3