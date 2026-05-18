"""Unit tests for utils.template_parser."""

import sys
from pathlib import Path
from typing import List

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from utils.constants import LoaderConstants
from utils.parsers.template_parser import (
    ContentRules,
    DocumentRules,
    HeadingRules,
    TemplateParser,
    TemplateRules,
    _detect_and_collapse_alphabet_groups,
)

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"

_PATTERN_CONTENT = (FIXTURES_DIR / "template_pattern.md").read_text(encoding="utf-8")
_CATEGORY_CONTENT = (FIXTURES_DIR / "template_category.md").read_text(encoding="utf-8")


def _parse_content(content: str) -> TemplateRules:
    """Parse in-memory content and return the resulting TemplateRules."""
    return TemplateParser().parse_content("fake/t.md", content)


# ---------------------------------------------------------------------------
# Data-class unit tests
# ---------------------------------------------------------------------------

class TestContentRules:

    def test_default_expected_types_contains_text(self):
        assert "text" in ContentRules().expected_types

    def test_defaults_are_empty_collections(self):
        cr = ContentRules()
        assert cr.bullet_prefixes == set()
        assert cr.exact_list_prefixes == set()
        assert cr.table_headers == []

    def test_to_dict_has_required_keys(self):
        d = ContentRules(expected_types={"text", "table"}, bullet_prefixes={"(+)"}).to_dict()
        assert set(d) == {"expected_types", "bullet_prefixes", "exact_list_prefixes", "table_headers"}

    def test_to_dict_expected_types_is_sorted(self):
        d = ContentRules(expected_types={"text", "bullet_list", "table"}).to_dict()
        assert d["expected_types"] == sorted(["text", "bullet_list", "table"])

    def test_to_dict_bullet_prefixes_is_sorted(self):
        d = ContentRules(bullet_prefixes={"(-)", "(+)"}).to_dict()
        assert d["bullet_prefixes"] == sorted(["(-)", "(+)"])


class TestHeadingRules:

    def test_defaults(self):
        h = HeadingRules(level=2, text="Section")
        assert h.optional is False
        assert h.is_variable is False
        assert h.is_link is False
        assert h.link_target is None
        assert h.is_group is False
        assert h.group_members == []
        assert h.variable_part is None

    def test_to_dict_omits_group_members_when_not_group(self):
        d = HeadingRules(level=2, text="Section").to_dict()
        assert "group_members" not in d

    def test_to_dict_includes_group_members_when_group(self):
        d = HeadingRules(level=2, text="[A-Z]", is_group=True, group_members=["A", "B"]).to_dict()
        assert d["group_members"] == ["A", "B"]

    def test_to_dict_has_all_scalar_fields(self):
        d = HeadingRules(level=3, text="X", optional=True, is_variable=True, variable_part="V",
                         is_link=True, link_target="t.md").to_dict()
        assert d["level"] == 3
        assert d["text"] == "X"
        assert d["optional"] is True
        assert d["is_variable"] is True
        assert d["variable_part"] == "V"
        assert d["is_link"] is True
        assert d["link_target"] == "t.md"


class TestDocumentRules:

    def test_defaults(self):
        dr = DocumentRules()
        assert dr.breadcrumbs == []
        assert dr.h1_prefix is None


class TestTemplateRules:

    def test_to_dict_top_level_keys(self):
        d = TemplateRules().to_dict()
        assert "document_rules" in d
        assert "headings" in d

    def test_to_dict_document_rules_keys(self):
        d = TemplateRules().to_dict()
        assert "breadcrumbs" in d["document_rules"]
        assert "h1_prefix" in d["document_rules"]

    def test_to_dict_headings_serialized(self):
        tr = TemplateRules(headings=[HeadingRules(level=2, text="Test")])
        d = tr.to_dict()
        assert len(d["headings"]) == 1
        assert d["headings"][0]["text"] == "Test"


# ---------------------------------------------------------------------------
# _detect_and_collapse_alphabet_groups
# ---------------------------------------------------------------------------

class TestDetectAndCollapseAlphabetGroups:

    @staticmethod
    def _headings(texts: List[str], level: int = 2) -> List[HeadingRules]:
        return [HeadingRules(level=level, text=t) for t in texts]

    def test_empty_list_returns_empty(self):
        assert _detect_and_collapse_alphabet_groups([]) == []

    def test_non_alphabet_headings_pass_through(self):
        result = _detect_and_collapse_alphabet_groups(self._headings(["Context", "Problem"]))
        assert len(result) == 2
        assert all(not h.is_group for h in result)

    def test_run_below_threshold_not_collapsed(self):
        result = _detect_and_collapse_alphabet_groups(self._headings(["A", "B", "C", "D"]))
        assert len(result) == 4
        assert all(not h.is_group for h in result)

    def test_exactly_min_run_collapsed(self):
        # MIN_ALPHABET_RUN = 5
        result = _detect_and_collapse_alphabet_groups(self._headings(["A", "B", "C", "D", "E"]))
        assert len(result) == 1
        assert result[0].is_group is True

    def test_full_az_plus_digits_collapsed_to_single_group(self):
        labels = ["0-9"] + [chr(c) for c in range(ord("A"), ord("Z") + 1)]
        result = _detect_and_collapse_alphabet_groups(self._headings(labels))
        assert len(result) == 1
        assert result[0].text == "[A-Z]"

    def test_group_members_match_original_labels(self):
        result = _detect_and_collapse_alphabet_groups(self._headings(["A", "B", "C", "D", "E"]))
        assert result[0].group_members == ["A", "B", "C", "D", "E"]

    def test_run_flanked_by_non_alphabet_headings(self):
        headings = (
            [HeadingRules(level=2, text="Intro")]
            + self._headings(["A", "B", "C", "D", "E"])
            + [HeadingRules(level=2, text="Footer")]
        )
        result = _detect_and_collapse_alphabet_groups(headings)
        assert len(result) == 3
        assert result[0].text == "Intro"
        assert result[1].is_group is True
        assert result[2].text == "Footer"

    def test_content_rules_taken_from_first_member(self):
        first = HeadingRules(level=2, text="A")
        first.content_rules.expected_types.add("table")
        headings = [first] + [HeadingRules(level=2, text=c) for c in "BCDE"]
        result = _detect_and_collapse_alphabet_groups(headings)
        assert "table" in result[0].content_rules.expected_types

    def test_different_levels_not_merged(self):
        headings = [
            HeadingRules(level=2, text="A"),
            HeadingRules(level=3, text="B"),
            HeadingRules(level=3, text="C"),
            HeadingRules(level=3, text="D"),
            HeadingRules(level=3, text="E"),
        ]
        result = _detect_and_collapse_alphabet_groups(headings)
        assert len(result) == 5

    def test_majority_optional_propagates_to_group(self):
        headings = [HeadingRules(level=2, text=c, optional=True) for c in "ABCDE"]
        result = _detect_and_collapse_alphabet_groups(headings)
        assert result[0].optional is True

    def test_minority_optional_yields_non_optional_group(self):
        headings = [HeadingRules(level=2, text=c, optional=False) for c in "ABCDE"]
        headings[0].optional = True  # only 1 of 5
        result = _detect_and_collapse_alphabet_groups(headings)
        assert result[0].optional is False


# ---------------------------------------------------------------------------
# TemplateParser.parse_content — pattern template
# ---------------------------------------------------------------------------

class TestTemplateParserPattern:
    """Parse template_pattern.md and verify the extracted rules."""

    def setup_method(self):
        parser = TemplateParser()
        parser.parse_content("fake/template_pattern.md", _PATTERN_CONTENT)
        self.rules = parser.get_template("template_pattern")

    def test_breadcrumbs_have_three_parts(self):
        assert len(self.rules.document_rules.breadcrumbs) == 3

    def test_h1_prefix_is_none_for_plain_pattern_title(self):
        assert self.rules.document_rules.h1_prefix is None

    def test_h1_is_variable(self):
        h1 = next(h for h in self.rules.headings if h.level == 1)
        assert h1.is_variable is True
        assert h1.variable_part is not None

    def test_also_known_as_is_optional(self):
        h = next(h for h in self.rules.headings if "Also Known As" in h.text)
        assert h.optional is True

    def test_optional_marker_stripped_from_heading_text(self):
        for h in self.rules.headings:
            assert "optional" not in h.text.lower()

    def test_classification_is_link_heading(self):
        h = next(h for h in self.rules.headings if h.text == "Classification")
        assert h.is_link is True
        assert h.link_target is not None

    def test_classification_has_bullet_list_type(self):
        h = next(h for h in self.rules.headings if h.text == "Classification")
        assert LoaderConstants.CT_BULLET_LIST in h.content_rules.expected_types

    def test_classification_has_exact_list_prefixes(self):
        h = next(h for h in self.rules.headings if h.text == "Classification")
        assert len(h.content_rules.exact_list_prefixes) > 0

    def test_forces_has_plus_and_minus_prefixes(self):
        h = next(h for h in self.rules.headings if h.text == "Forces")
        assert "(+)" in h.content_rules.bullet_prefixes
        assert "(-)" in h.content_rules.bullet_prefixes

    def test_consequences_has_plus_and_minus_prefixes(self):
        h = next(h for h in self.rules.headings if h.text == "Consequences")
        assert "(+)" in h.content_rules.bullet_prefixes
        assert "(-)" in h.content_rules.bullet_prefixes

    def test_related_patterns_has_table_type(self):
        h = next(h for h in self.rules.headings if "Related Patterns" in h.text)
        assert LoaderConstants.CT_TABLE in h.content_rules.expected_types

    def test_related_patterns_has_table_headers(self):
        h = next(h for h in self.rules.headings if "Related Patterns" in h.text)
        assert len(h.content_rules.table_headers) > 0

    def test_notes_is_optional(self):
        h = next(h for h in self.rules.headings if h.text == "Notes")
        assert h.optional is True

    def test_sources_is_link_heading(self):
        h = next(h for h in self.rules.headings if h.text == "Sources")
        assert h.is_link is True

    def test_sources_has_horizontal_rule(self):
        h = next(h for h in self.rules.headings if h.text == "Sources")
        assert LoaderConstants.CT_HORIZONTAL_RULE in h.content_rules.expected_types

    def test_sources_has_footnote(self):
        h = next(h for h in self.rules.headings if h.text == "Sources")
        assert LoaderConstants.CT_FOOTNOTE in h.content_rules.expected_types


# ---------------------------------------------------------------------------
# TemplateParser.parse_content — pattern template with modified content
# ---------------------------------------------------------------------------

class TestTemplateParserPatternModified:
    """Load the pattern fixture content and modify it per test to probe edge cases."""

    def test_removing_optional_marker_makes_heading_required(self):
        content = _PATTERN_CONTENT.replace("## Also Known As *(optional)*", "## Also Known As")
        rules = _parse_content(content)
        h = next(h for h in rules.headings if "Also Known As" in h.text)
        assert h.optional is False

    def test_adding_prefix_to_h1_sets_h1_prefix(self):
        content = _PATTERN_CONTENT.replace("# *Pattern Name*", "# Category: *Pattern Name*")
        rules = _parse_content(content)
        assert rules.document_rules.h1_prefix == "Category"

    def test_replacing_table_with_text_removes_table_type(self):
        content = _PATTERN_CONTENT.replace(
            "## Related Patterns\n\n|Pattern|Relation type|Relation description|\n|--|--|--|\n|*related pattern*|*relation*|*description*|",
            "## Related Patterns\n\nSee other patterns for details.",
        )
        rules = _parse_content(content)
        h = next(h for h in rules.headings if "Related Patterns" in h.text)
        assert LoaderConstants.CT_TABLE not in h.content_rules.expected_types

    def test_two_part_breadcrumb_parsed(self):
        rules = _parse_content("[Home](README.md) > [Cat](cat.md)\n\n# Title\n")
        assert len(rules.document_rules.breadcrumbs) == 2

    def test_section_with_image_detects_image_type(self):
        content = _PATTERN_CONTENT.replace(
            "## Notes *(optional)*\n\n*Remarks and information.*",
            "## Notes *(optional)*\n\n![Chart](chart.png)",
        )
        rules = _parse_content(content)
        h = next(h for h in rules.headings if h.text == "Notes")
        assert LoaderConstants.CT_IMAGE in h.content_rules.expected_types


# ---------------------------------------------------------------------------
# TemplateParser.parse_content — category template
# ---------------------------------------------------------------------------

class TestTemplateParserCategory:
    """Parse template_category.md and verify the extracted rules."""

    def setup_method(self):
        parser = TemplateParser()
        parser.parse_content("fake/template_category.md", _CATEGORY_CONTENT)
        self.rules = parser.get_template("template_category")

    def test_breadcrumbs_have_five_parts(self):
        assert len(self.rules.document_rules.breadcrumbs) == 5

    def test_h1_prefix_is_category(self):
        assert self.rules.document_rules.h1_prefix == "Category"

    def test_h1_is_variable(self):
        h1 = next(h for h in self.rules.headings if h.level == 1)
        assert h1.is_variable is True

    def test_alphabet_letters_collapsed_to_single_group(self):
        groups = [h for h in self.rules.headings if h.is_group]
        assert len(groups) == 1

    def test_group_text_is_az_placeholder(self):
        group = next(h for h in self.rules.headings if h.is_group)
        assert group.text == "[A-Z]"

    def test_group_members_include_digits_and_full_alphabet(self):
        group = next(h for h in self.rules.headings if h.is_group)
        assert "0-9" in group.group_members
        assert "A" in group.group_members
        assert "Z" in group.group_members

    def test_total_heading_count_is_two(self):
        # H1 + one collapsed [A-Z] group
        assert len(self.rules.headings) == 2


# ---------------------------------------------------------------------------
# TemplateParser — parse_content API and templates dict
# ---------------------------------------------------------------------------

class TestTemplateParserAPI:

    def test_parse_content_returns_template_rules(self):
        rules = TemplateParser().parse_content("fake/t.md", "# T\n\n## S\n\nText.")
        assert isinstance(rules, TemplateRules)

    def test_parse_content_stores_under_stem_name(self):
        parser = TemplateParser()
        parser.parse_content("fake/my_template.md", "# T\n\n## S\n\nText.")
        assert "my_template" in parser.templates

    def test_parse_content_raises_on_non_string(self):
        import pytest
        with pytest.raises(TypeError):
            TemplateParser().parse_content("fake/t.md", None)  # type: ignore[arg-type]

    def test_get_template_returns_stored_rules(self):
        parser = TemplateParser()
        parser.parse_content("fake/t.md", "# T\n\n## S\n\nText.")
        result = parser.get_template("t")
        assert isinstance(result, TemplateRules)
        assert result.headings != []

    def test_get_unknown_template_returns_empty_rules(self):
        parser = TemplateParser()
        result = parser.get_template("nonexistent")
        assert isinstance(result, TemplateRules)
        assert result.headings == []

    def test_get_all_templates_returns_all_loaded(self):
        parser = TemplateParser()
        parser.parse_content("fake/a.md", "# A\n\n## S\n\nText.")
        parser.parse_content("fake/b.md", "# B\n\n## S\n\nText.")
        assert set(parser.get_all_templates().keys()) == {"a", "b"}

    def test_parse_content_overwrites_previous_result(self):
        parser = TemplateParser()
        parser.parse_content("fake/t.md", "# First\n\n## A\n\nText.")
        parser.parse_content("fake/t.md", "# Second\n\n## B\n\nText.")
        assert parser.get_template("t").headings[0].text == "Second"


# ---------------------------------------------------------------------------
# TemplateParser — edge cases
# ---------------------------------------------------------------------------

class TestTemplateParserEdgeCases:

    def test_heading_with_no_content_defaults_to_text_type(self):
        rules = _parse_content("# Title\n\n## EmptySection\n")
        h = next(h for h in rules.headings if h.text == "EmptySection")
        assert LoaderConstants.CT_TEXT in h.content_rules.expected_types

    def test_image_content_detected(self):
        rules = _parse_content("# T\n\n## Gallery\n\n![Alt](img.png)\n")
        h = next(h for h in rules.headings if h.text == "Gallery")
        assert LoaderConstants.CT_IMAGE in h.content_rules.expected_types

    def test_preamble_breadcrumbs_parsed_correctly(self):
        rules = _parse_content("[Home](README.md) > [Cat](cat.md) > Leaf\n\n# Title\n")
        assert len(rules.document_rules.breadcrumbs) == 3

    def test_blank_lines_between_headings_ignored(self):
        rules = _parse_content("# T\n\n\n## A\n\n\n## B\n")
        texts = [h.text for h in rules.headings]
        assert "A" in texts
        assert "B" in texts

    def test_table_first_row_used_as_headers(self):
        rules = _parse_content("# T\n\n## Table\n\n| Col1 | Col2 |\n|--|--|\n| a | b |\n")
        h = next(h for h in rules.headings if h.text == "Table")
        assert h.content_rules.table_headers == ["Col1", "Col2"]

    def test_second_table_headers_not_overwritten(self):
        content = "# T\n\n## T1\n\n| A | B |\n|--|--|\n| 1 | 2 |\n\n## T2\n\n| X | Y |\n|--|--|\n"
        rules = _parse_content(content)
        h = next(h for h in rules.headings if h.text == "T1")
        assert h.content_rules.table_headers == ["A", "B"]