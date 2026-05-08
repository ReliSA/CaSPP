
"""Unit tests for utils.markdown_parser — MarkdownParser class."""

import sys
from pathlib import Path

import pytest

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from utils.constants import LoaderConstants
from utils.parsers.markdown_parser import MarkdownParser, ParsedDocument

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

SAMPLE_MD = (FIXTURES_DIR / "sample_pattern.md").read_text(encoding="utf-8")


def _make_parser() -> MarkdownParser:
    return MarkdownParser()


class TestParseContent:

    def setup_method(self):
        self.parser = _make_parser()

    def test_returns_parsed_document(self):
        doc = self.parser.parse_content("fake/sample.md", SAMPLE_MD)
        assert isinstance(doc, ParsedDocument)

    def test_meta_filepath_ends_with_filename(self):
        doc = self.parser.parse_content("fake/sample.md", SAMPLE_MD)
        assert doc.meta.filepath.endswith("sample.md")

    def test_meta_breadcrumbs_three_parts(self):
        doc = self.parser.parse_content("fake/sample.md", SAMPLE_MD)
        assert len(doc.meta.breadcrumbs) == 3

    def test_meta_h1_value(self):
        doc = self.parser.parse_content("fake/sample.md", SAMPLE_MD)
        assert doc.meta.h1_value == "Sample Pattern"

    def test_meta_h1_no_prefix_for_plain_title(self):
        doc = self.parser.parse_content("fake/sample.md", SAMPLE_MD)
        assert doc.meta.h1_prefix is None

    def test_headings_extracted(self):
        doc = self.parser.parse_content("fake/sample.md", SAMPLE_MD)
        assert len(doc.headings) > 0

    def test_h1_heading_text(self):
        doc = self.parser.parse_content("fake/sample.md", SAMPLE_MD)
        h1 = next(h for h in doc.headings if h.level == 1)
        assert h1.text == "Sample Pattern"

    def test_classification_heading_is_link(self):
        doc = self.parser.parse_content("fake/sample.md", SAMPLE_MD)
        h = next((h for h in doc.headings if h.text == "Classification"), None)
        assert h is not None
        assert h.is_link is True
        assert h.link_target == "facets/facets.md"

    def test_classification_content_has_bullet_list(self):
        doc = self.parser.parse_content("fake/sample.md", SAMPLE_MD)
        h = next(h for h in doc.headings if h.text == "Classification")
        assert LoaderConstants.CT_BULLET_LIST in h.content.found_types

    def test_classification_content_has_exact_list_prefixes(self):
        doc = self.parser.parse_content("fake/sample.md", SAMPLE_MD)
        h = next(h for h in doc.headings if h.text == "Classification")
        assert len(h.content.exact_list_prefixes) > 0

    def test_forces_plus_and_minus_bullet_prefixes(self):
        doc = self.parser.parse_content("fake/sample.md", SAMPLE_MD)
        h = next(h for h in doc.headings if h.text == "Forces")
        assert "(+)" in h.content.bullet_prefixes
        assert "(-)" in h.content.bullet_prefixes

    def test_related_patterns_has_table(self):
        doc = self.parser.parse_content("fake/sample.md", SAMPLE_MD)
        h = next(h for h in doc.headings if h.text == "Related Patterns")
        assert LoaderConstants.CT_TABLE in h.content.found_types

    def test_related_patterns_table_headers_extracted(self):
        doc = self.parser.parse_content("fake/sample.md", SAMPLE_MD)
        h = next(h for h in doc.headings if h.text == "Related Patterns")
        assert h.content.table_headers == ["Pattern", "Relation type", "Relation description"]

    def test_notes_has_image(self):
        doc = self.parser.parse_content("fake/sample.md", SAMPLE_MD)
        h = next(h for h in doc.headings if h.text == "Notes")
        assert LoaderConstants.CT_IMAGE in h.content.found_types

    def test_notes_has_horizontal_rule(self):
        doc = self.parser.parse_content("fake/sample.md", SAMPLE_MD)
        h = next(h for h in doc.headings if h.text == "Notes")
        assert LoaderConstants.CT_HORIZONTAL_RULE in h.content.found_types

    def test_sources_has_footnote(self):
        doc = self.parser.parse_content("fake/sample.md", SAMPLE_MD)
        h = next(h for h in doc.headings if h.text == "Sources")
        assert LoaderConstants.CT_FOOTNOTE in h.content.found_types

    def test_solution_has_links(self):
        doc = self.parser.parse_content("fake/sample.md", SAMPLE_MD)
        h = next(h for h in doc.headings if h.text == "Solution")
        assert LoaderConstants.CT_LINKS in h.content.found_types

    def test_context_content_not_empty(self):
        doc = self.parser.parse_content("fake/sample.md", SAMPLE_MD)
        h = next(h for h in doc.headings if h.text == "Context")
        assert h.content.is_empty is False
        assert h.content.first_content_line > 0

    def test_empty_section_is_empty(self):
        content = "# Title\n\n## Empty Section\n\n## Next Section\n\nSome text.\n"
        doc = self.parser.parse_content("fake.md", content)
        empty_h = next(h for h in doc.headings if h.text == "Empty Section")
        assert empty_h.content.is_empty is True

    def test_heading_line_numbers_are_positive(self):
        doc = self.parser.parse_content("fake/sample.md", SAMPLE_MD)
        for h in doc.headings:
            assert h.line_number > 0

    def test_type_error_on_non_string_content(self):
        with pytest.raises(TypeError):
            self.parser.parse_content("fake/sample.md", 42)

    def test_sources_heading_is_link(self):
        doc = self.parser.parse_content("fake/sample.md", SAMPLE_MD)
        h = next((h for h in doc.headings if h.text == "Sources"), None)
        assert h is not None
        assert h.is_link is True


class TestH1Prefix:

    def test_category_prefix_extracted(self):
        parser = _make_parser()
        content = "# Category: Guidance\n\nSome text.\n"
        doc = parser.parse_content("fake.md", content)
        assert doc.meta.h1_prefix == "Category"
        assert doc.meta.h1_value == "Guidance"

    def test_no_prefix_for_plain_h1(self):
        parser = _make_parser()
        content = "# Plain Title\n\nSome text.\n"
        doc = parser.parse_content("fake.md", content)
        assert doc.meta.h1_prefix is None
        assert doc.meta.h1_value == "Plain Title"

    def test_multi_word_prefix(self):
        parser = _make_parser()
        content = "# Primary perspective: Teacher\n\nText.\n"
        doc = parser.parse_content("fake.md", content)
        assert doc.meta.h1_prefix == "Primary perspective"
        assert doc.meta.h1_value == "Teacher"

    def test_only_first_h1_sets_meta(self):
        parser = _make_parser()
        content = "# First Title\n\nText.\n\n# Second Title\n\nMore text.\n"
        doc = parser.parse_content("fake.md", content)
        assert doc.meta.h1_value == "First Title"


class TestAlphabetGroupCollapse:

    @staticmethod
    def _alphabet_md(labels) -> str:
        return "\n".join(f"## {label}\n\nContent under {label}.\n" for label in labels)

    def test_five_labels_collapsed_to_one_group(self):
        parser = _make_parser()
        content = self._alphabet_md(["A", "B", "C", "D", "E"])
        doc = parser.parse_content("fake.md", content)
        groups = [h for h in doc.headings if h.is_group]
        assert len(groups) == 1
        assert groups[0].text == "[A-Z]"

    def test_group_members_all_present(self):
        parser = _make_parser()
        content = self._alphabet_md(["A", "B", "C", "D", "E"])
        doc = parser.parse_content("fake.md", content)
        group = doc.headings[0]
        assert set(group.group_members) == {"A", "B", "C", "D", "E"}

    def test_group_line_numbers_match_member_count(self):
        parser = _make_parser()
        content = self._alphabet_md(["A", "B", "C", "D", "E"])
        doc = parser.parse_content("fake.md", content)
        group = doc.headings[0]
        assert len(group.group_line_numbers) == len(group.group_members)

    def test_fewer_than_min_run_not_collapsed(self):
        parser = _make_parser()
        # MIN_ALPHABET_RUN = 5, so 3 should not collapse
        content = self._alphabet_md(["A", "B", "C"])
        doc = parser.parse_content("fake.md", content)
        assert all(not h.is_group for h in doc.headings)

    def test_non_alphabet_headings_not_grouped(self):
        parser = _make_parser()
        content = "## Context\n\nText.\n\n## Problem\n\nText.\n"
        doc = parser.parse_content("fake.md", content)
        assert all(not h.is_group for h in doc.headings)

    def test_group_content_merges_all_members(self):
        parser = _make_parser()
        content = self._alphabet_md(["A", "B", "C", "D", "E"])
        doc = parser.parse_content("fake.md", content)
        group = doc.headings[0]
        assert LoaderConstants.CT_TEXT in group.content.found_types

    def test_numeric_label_0_9_collapses(self):
        parser = _make_parser()
        labels = ["0-9", "A", "B", "C", "D"]
        content = self._alphabet_md(labels)
        doc = parser.parse_content("fake.md", content)
        groups = [h for h in doc.headings if h.is_group]
        assert len(groups) == 1

    def test_full_alphabet_collapses(self):
        parser = _make_parser()
        labels = [chr(c) for c in range(ord("A"), ord("F") + 1)]  # A–F (6 items)
        content = self._alphabet_md(labels)
        doc = parser.parse_content("fake.md", content)
        groups = [h for h in doc.headings if h.is_group]
        assert len(groups) == 1


class TestToDict:

    def test_to_dict_has_meta_and_headings(self):
        parser = _make_parser()
        doc = parser.parse_content("fake.md", SAMPLE_MD)
        d = doc.to_dict()
        assert "meta" in d
        assert "headings" in d

    def test_meta_dict_contains_expected_keys(self):
        parser = _make_parser()
        doc = parser.parse_content("fake.md", SAMPLE_MD)
        meta = doc.to_dict()["meta"]
        for key in ("filepath", "breadcrumbs", "breadcrumbs_normalized", "h1_prefix", "h1_value"):
            assert key in meta

    def test_heading_dict_contains_expected_keys(self):
        parser = _make_parser()
        doc = parser.parse_content("fake.md", SAMPLE_MD)
        h = next(h for h in doc.headings if h.text == "Forces")
        d = h.to_dict()
        for key in ("level", "text", "raw_text", "line_number", "is_link", "content"):
            assert key in d

    def test_content_dict_found_types_is_sorted_list(self):
        parser = _make_parser()
        doc = parser.parse_content("fake.md", SAMPLE_MD)
        h = next(h for h in doc.headings if h.text == "Forces")
        found_types = h.to_dict()["content"]["found_types"]
        assert isinstance(found_types, list)
        assert found_types == sorted(found_types)

    def test_group_heading_dict_includes_members(self):
        parser = _make_parser()
        content = "\n".join(f"## {c}\n\nText.\n" for c in "ABCDE")
        doc = parser.parse_content("fake.md", content)
        group = next(h for h in doc.headings if h.is_group)
        d = group.to_dict()
        assert "group_members" in d
        assert "group_line_numbers" in d