"""Unit tests for utils.md_parser — pure parsing primitives."""

import sys
from pathlib import Path

import pytest

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from core.constants import LoaderConstants
from utils.md_parser import classify_content_line, parse_breadcrumbs, parse_heading_line, split_h1


class TestParseHeadingLine:

    def test_simple_h2_level_and_text(self):
        ph = parse_heading_line("##", "Context")
        assert ph.level == 2
        assert ph.text == "Context"
        assert ph.raw_text == "Context"
        assert ph.is_link is False
        assert ph.link_target is None

    def test_h1_level(self):
        ph = parse_heading_line("#", "Sample Pattern")
        assert ph.level == 1
        assert ph.text == "Sample Pattern"

    def test_h6_level(self):
        ph = parse_heading_line("######", "Deepest Section")
        assert ph.level == 6

    def test_link_heading_extracts_label_and_url(self):
        ph = parse_heading_line("##", "[Classification](facets/facets.md)")
        assert ph.text == "Classification"
        assert ph.is_link is True
        assert ph.link_target == "facets/facets.md"

    def test_link_heading_preserves_raw_text(self):
        ph = parse_heading_line("##", "[Sources](../References.md)")
        assert ph.raw_text == "[Sources](../References.md)"
        assert ph.text == "Sources"

    def test_relative_link_target_preserved_as_is(self):
        ph = parse_heading_line("##", "[Sources](../References.md)")
        assert ph.link_target == "../References.md"

    def test_trailing_whitespace_stripped(self):
        ph = parse_heading_line("##", "  Title  ")
        assert ph.text == "Title"
        assert ph.raw_text == "Title"

    def test_template_optional_marker_removed_from_text(self):
        ph = parse_heading_line("##", "Also Known As *(optional)*", is_template=True)
        assert ph.is_optional is True
        assert "optional" not in ph.text.lower()
        assert ph.text == "Also Known As"

    def test_template_optional_without_asterisks(self):
        ph = parse_heading_line("##", "Synopsis (optional)", is_template=True)
        assert ph.is_optional is True

    def test_template_optional_case_insensitive(self):
        ph = parse_heading_line("##", "Notes *(OPTIONAL)*", is_template=True)
        assert ph.is_optional is True

    def test_document_mode_optional_flag_is_false(self):
        ph = parse_heading_line("##", "Also Known As *(optional)*", is_template=False)
        assert ph.is_optional is False
        assert "(optional)" in ph.text

    def test_template_italic_variable(self):
        ph = parse_heading_line("#", "*Pattern Name*", is_template=True)
        assert ph.is_variable is True
        assert ph.variable_part == "Pattern Name"
        assert ph.text == "Pattern Name"

    def test_document_mode_italic_not_treated_as_variable(self):
        ph = parse_heading_line("#", "*Pattern Name*", is_template=False)
        assert ph.is_variable is False
        assert ph.text == "Pattern Name"

    def test_asterisks_stripped_from_clean_text(self):
        ph = parse_heading_line("##", "*Italic heading*")
        assert ph.text == "Italic heading"

    def test_link_with_optional_in_template(self):
        ph = parse_heading_line("##", "[Sources](../References.md) *(optional)*", is_template=True)
        assert ph.is_link is True
        assert ph.link_target == "../References.md"
        assert ph.text == "Sources"
        assert ph.is_optional is True

    def test_no_link_returns_none_link_target(self):
        ph = parse_heading_line("##", "Plain Heading")
        assert ph.link_target is None
        assert ph.is_link is False


class TestSplitH1:

    def test_simple_prefix(self):
        prefix, value = split_h1("Category: Name")
        assert prefix == "Category"
        assert value == "Name"

    def test_no_prefix_plain_title(self):
        prefix, value = split_h1("Tracking progress")
        assert prefix is None
        assert value == "Tracking progress"

    def test_multi_word_prefix(self):
        prefix, value = split_h1("Project Methodology: Agile")
        assert prefix == "Project Methodology"
        assert value == "Agile"

    def test_colon_in_value_preserved(self):
        prefix, value = split_h1("Category: Name: Extra")
        assert prefix == "Category"
        assert "Name" in value

    def test_single_word_title(self):
        prefix, value = split_h1("Introduction")
        assert prefix is None
        assert value == "Introduction"

    def test_whitespace_stripped_from_match_groups(self):
        prefix, value = split_h1("Category: Guidance")
        assert prefix == "Category"
        assert value == "Guidance"


class TestParseBreadcrumbs:

    def test_three_part_breadcrumb(self):
        line = "[Home](../README.md) > [Catalogue](../Patterns_catalogue.md) > Pattern Name"
        parts = parse_breadcrumbs(line)
        assert parts is not None
        assert len(parts) == 3

    def test_two_part_breadcrumb(self):
        line = "[Home](../README.md) > [Sub](sub.md)"
        parts = parse_breadcrumbs(line)
        assert parts is not None
        assert len(parts) == 2

    def test_parts_are_stripped(self):
        line = "[Home](../README.md) > [Sub](sub.md) > Leaf"
        parts = parse_breadcrumbs(line)
        for part in parts:
            assert part == part.strip()

    def test_no_angle_bracket_returns_none(self):
        line = "[Home](../README.md) and [Something](link.md)"
        assert parse_breadcrumbs(line) is None

    def test_no_square_bracket_returns_none(self):
        line = "Home > Catalogue > Pattern"
        assert parse_breadcrumbs(line) is None

    def test_italic_only_returns_none(self):
        # Italic-only lines are template instructions, not breadcrumbs
        line = "*remove or replace everything in italics, including above*"
        assert parse_breadcrumbs(line) is None

    def test_italic_with_brackets_and_gt_returns_none(self):
        # Has '>' and '[' but is wrapped in asterisks → not a breadcrumb
        line = "*[Home](../README.md) > [Catalogue](../Patterns_catalogue.md)*"
        assert parse_breadcrumbs(line) is None

    def test_plain_text_returns_none(self):
        line = "Just a regular paragraph with no breadcrumb markers."
        assert parse_breadcrumbs(line) is None


class TestClassifyContentLine:

    def test_image_line(self):
        types, bp, elp, headers = classify_content_line("![Alt text](image.png)")
        assert LoaderConstants.CT_IMAGE in types
        assert len(types) == 1

    def test_image_with_title(self):
        types, bp, elp, headers = classify_content_line('![Caption](img.png "Title")')
        assert LoaderConstants.CT_IMAGE in types

    def test_table_row_extracts_headers(self):
        types, bp, elp, headers = classify_content_line("| Pattern | Relation | Description |")
        assert LoaderConstants.CT_TABLE in types
        assert headers == ["Pattern", "Relation", "Description"]

    def test_table_separator_no_headers(self):
        types, bp, elp, headers = classify_content_line("|--|--|--|")
        assert LoaderConstants.CT_TABLE in types
        assert headers is None

    def test_table_separator_with_colons(self):
        types, bp, elp, headers = classify_content_line("|:--|:--:|--:|")
        assert LoaderConstants.CT_TABLE in types
        assert headers is None

    def test_bullet_dash(self):
        types, bp, elp, headers = classify_content_line("- Simple item")
        assert LoaderConstants.CT_BULLET_LIST in types
        assert bp is None

    def test_bullet_asterisk(self):
        types, bp, elp, headers = classify_content_line("* Item with asterisk")
        assert LoaderConstants.CT_BULLET_LIST in types

    def test_bullet_plus_prefix(self):
        types, bp, elp, headers = classify_content_line("- (+) First benefit")
        assert LoaderConstants.CT_BULLET_LIST in types
        assert bp == "(+)"

    def test_bullet_minus_prefix(self):
        types, bp, elp, headers = classify_content_line("- (-) First liability")
        assert LoaderConstants.CT_BULLET_LIST in types
        assert bp == "(-)"

    def test_bullet_exact_link_prefix(self):
        types, bp, elp, headers = classify_content_line(
            "- [Category](facets/categories/categories.md): Something"
        )
        assert LoaderConstants.CT_BULLET_LIST in types
        assert elp is not None
        assert elp.startswith("[Category]")

    def test_horizontal_rule_dashes(self):
        types, bp, elp, headers = classify_content_line("---")
        assert LoaderConstants.CT_HORIZONTAL_RULE in types

    def test_horizontal_rule_underscores(self):
        types, bp, elp, headers = classify_content_line("___")
        assert LoaderConstants.CT_HORIZONTAL_RULE in types

    def test_horizontal_rule_triple_asterisks(self):
        types, bp, elp, headers = classify_content_line("***")
        assert LoaderConstants.CT_HORIZONTAL_RULE in types

    def test_template_wrapped_hr(self):
        types, bp, elp, headers = classify_content_line("*---*", is_template=True)
        assert LoaderConstants.CT_HORIZONTAL_RULE in types

    def test_document_mode_wrapped_hr_not_matched(self):
        types, bp, elp, headers = classify_content_line("*---*", is_template=False)
        assert LoaderConstants.CT_HORIZONTAL_RULE not in types

    def test_footnote_definition(self):
        types, bp, elp, headers = classify_content_line("[^1]: A footnote.")
        assert LoaderConstants.CT_FOOTNOTE in types

    def test_footnote_named_key(self):
        types, bp, elp, headers = classify_content_line("[^sprint]: Definition of a sprint.")
        assert LoaderConstants.CT_FOOTNOTE in types

    def test_template_wrapped_footnote(self):
        types, bp, elp, headers = classify_content_line("*[^1]: A footnote.*", is_template=True)
        assert LoaderConstants.CT_FOOTNOTE in types

    def test_document_mode_wrapped_footnote_not_matched(self):
        types, bp, elp, headers = classify_content_line("*[^1]: A footnote.*", is_template=False)
        assert LoaderConstants.CT_FOOTNOTE not in types

    def test_text_with_inline_link(self):
        types, bp, elp, headers = classify_content_line("See [more info](http://example.com) here.")
        assert LoaderConstants.CT_TEXT in types
        assert LoaderConstants.CT_LINKS in types

    def test_plain_text_no_special_types(self):
        types, bp, elp, headers = classify_content_line("Just plain text without any special markup.")
        assert LoaderConstants.CT_TEXT in types
        assert LoaderConstants.CT_LINKS not in types
        assert LoaderConstants.CT_BULLET_LIST not in types
        assert LoaderConstants.CT_TABLE not in types
        assert LoaderConstants.CT_IMAGE not in types