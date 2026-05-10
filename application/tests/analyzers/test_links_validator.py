"""Unit tests for core.analyzer.links_validator — LinkValidator class."""

import sys
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import MagicMock

APP_DIR = Path(__file__).resolve().parents[2]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from core.analyzer.links_validator import LinkValidator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _entry(content: str, line: int) -> Dict[str, Any]:
    return {"content": content, "line": line}


def _lines(*contents: str) -> List[Dict[str, Any]]:
    return [_entry(c, i + 1) for i, c in enumerate(contents)]


def _heading(raw_lines: List[Dict[str, Any]], is_group: bool = False) -> MagicMock:
    h = MagicMock()
    h.is_group = is_group
    h.content.raw_lines = raw_lines
    return h


def _doc(filepath: str, headings: List[MagicMock] = None) -> MagicMock:
    doc = MagicMock()
    doc.meta.filepath = filepath
    doc.headings = headings or []
    return doc


def _validator(
    filepath: str,
    headings: List[MagicMock] = None,
    project_index: Dict[str, Any] = None,
    references_content: str = None,
) -> LinkValidator:
    return LinkValidator(
        doc=_doc(filepath, headings or []),
        project_index=project_index or {},
        references_content=references_content,
    )


# ---------------------------------------------------------------------------
# check_reciprocal_links
# ---------------------------------------------------------------------------

class TestCheckReciprocalLinks:

    def test_no_related_links_no_warnings(self):
        index = {"Pattern_A.md": {"related": [], "aliases": []}}
        v = _validator("path/to/Pattern_A.md", project_index=index)
        v.check_reciprocal_links()
        assert v.warnings == []

    def test_current_file_not_in_index_returns_early(self):
        v = _validator("path/to/Unknown.md", project_index={})
        v.check_reciprocal_links()
        assert v.warnings == []

    def test_reciprocal_link_present_no_warning(self):
        index = {
            "Pattern_A.md": {"related": ["Pattern_B.md"], "aliases": []},
            "Pattern_B.md": {"related": ["Pattern_A.md"], "aliases": []},
        }
        v = _validator("path/to/Pattern_A.md", project_index=index)
        v.check_reciprocal_links()
        assert v.warnings == []

    def test_missing_reciprocal_link_warns(self):
        index = {
            "Pattern_A.md": {"related": ["Pattern_B.md"], "aliases": []},
            "Pattern_B.md": {"related": [], "aliases": []},
        }
        v = _validator("path/to/Pattern_A.md", project_index=index)
        v.check_reciprocal_links()
        assert len(v.warnings) == 1
        assert "Pattern_B.md" in v.warnings[0]["msg"]
        assert "Reciprocal" in v.warnings[0]["msg"]

    def test_linked_file_not_in_index_warns(self):
        index = {
            "Pattern_A.md": {"related": ["Nonexistent.md"], "aliases": []},
        }
        v = _validator("path/to/Pattern_A.md", project_index=index)
        v.check_reciprocal_links()
        assert len(v.warnings) == 1
        assert "not found" in v.warnings[0]["msg"].lower()
        assert "Nonexistent.md" in v.warnings[0]["msg"]

    def test_reciprocal_link_with_path_prefix_stripped(self):
        index = {
            "Pattern_A.md": {"related": ["../catalogue/Pattern_B.md"], "aliases": []},
            "Pattern_B.md": {"related": ["Pattern_A.md"], "aliases": []},
        }
        v = _validator("path/to/Pattern_A.md", project_index=index)
        v.check_reciprocal_links()
        assert v.warnings == []

    def test_multiple_related_some_missing_warns_each(self):
        index = {
            "Pattern_A.md": {"related": ["Pattern_B.md", "Pattern_C.md"], "aliases": []},
            "Pattern_B.md": {"related": ["Pattern_A.md"], "aliases": []},
            "Pattern_C.md": {"related": [], "aliases": []},
        }
        v = _validator("path/to/Pattern_A.md", project_index=index)
        v.check_reciprocal_links()
        assert len(v.warnings) == 1
        assert "Pattern_C.md" in v.warnings[0]["msg"]

    def test_warning_uses_line_1(self):
        index = {
            "Pattern_A.md": {"related": ["Pattern_B.md"], "aliases": []},
            "Pattern_B.md": {"related": [], "aliases": []},
        }
        v = _validator("path/to/Pattern_A.md", project_index=index)
        v.check_reciprocal_links()
        assert v.warnings[0]["line"] == 1


# ---------------------------------------------------------------------------
# check_link_targets
# ---------------------------------------------------------------------------

class TestCheckLinkTargets:

    def test_no_headings_no_warnings(self):
        v = _validator("path/to/Pattern_A.md")
        v.check_link_targets()
        assert v.warnings == []

    def test_valid_link_target_no_warning(self):
        index = {"Pattern_B.md": {"aliases": [], "related": []}}
        headings = [_heading(_lines("[Pattern B](Pattern_B.md)"))]
        v = _validator("path/to/Pattern_A.md", headings=headings, project_index=index)
        v.check_link_targets()
        assert v.warnings == []

    def test_missing_link_target_warns(self):
        headings = [_heading(_lines("[Missing](Missing_File.md)"))]
        v = _validator("path/to/Pattern_A.md", headings=headings, project_index={})
        v.check_link_targets()
        assert len(v.warnings) == 1
        assert "Missing_File.md" in v.warnings[0]["msg"]
        assert "not found" in v.warnings[0]["msg"].lower()

    def test_external_http_link_skipped(self):
        headings = [_heading(_lines("[External](https://example.com)"))]
        v = _validator("path/to/Pattern_A.md", headings=headings, project_index={})
        v.check_link_targets()
        assert v.warnings == []

    def test_anchor_only_link_skipped(self):
        headings = [_heading(_lines("[Section](#section-name)"))]
        v = _validator("path/to/Pattern_A.md", headings=headings, project_index={})
        v.check_link_targets()
        assert v.warnings == []

    def test_references_md_link_skipped(self):
        headings = [_heading(_lines("[MUN'17](References.md#MUN17)"))]
        v = _validator("path/to/Pattern_A.md", headings=headings, project_index={})
        v.check_link_targets()
        assert v.warnings == []

    def test_non_md_link_skipped(self):
        headings = [_heading(_lines("[Image](image.png)"))]
        v = _validator("path/to/Pattern_A.md", headings=headings, project_index={})
        v.check_link_targets()
        assert v.warnings == []

    def test_link_with_anchor_fragment_resolved_correctly(self):
        index = {"Pattern_B.md": {"aliases": [], "related": []}}
        headings = [_heading(_lines("[Pattern B](Pattern_B.md#section)"))]
        v = _validator("path/to/Pattern_A.md", headings=headings, project_index=index)
        v.check_link_targets()
        assert v.warnings == []

    def test_link_with_path_prefix_resolved_correctly(self):
        index = {"Pattern_B.md": {"aliases": [], "related": []}}
        headings = [_heading(_lines("[Pattern B](../catalogue/Pattern_B.md)"))]
        v = _validator("path/to/Pattern_A.md", headings=headings, project_index=index)
        v.check_link_targets()
        assert v.warnings == []

    def test_warning_contains_correct_line_number(self):
        raw = [_entry("some text", 1), _entry("[Bad](Bad.md)", 5)]
        headings = [_heading(raw)]
        v = _validator("path/to/Pattern_A.md", headings=headings, project_index={})
        v.check_link_targets()
        assert v.warnings[0]["line"] == 5

    def test_multiple_missing_links_warns_each(self):
        headings = [_heading(_lines("[A](A.md) and [B](B.md)"))]
        v = _validator("path/to/Pattern_A.md", headings=headings, project_index={})
        v.check_link_targets()
        assert len(v.warnings) == 2


# ---------------------------------------------------------------------------
# check_alias_consistency
# ---------------------------------------------------------------------------

class TestCheckAliasConsistency:

    def test_non_group_document_skipped(self):
        headings = [_heading(_lines("[Bad Label](Pattern_B.md)"), is_group=False)]
        index = {"Pattern_B.md": {"aliases": ["Correct Alias"], "related": []}}
        v = _validator("path/to/Catalogue.md", headings=headings, project_index=index)
        v.check_alias_consistency()
        assert v.warnings == []

    def test_label_matches_filename_stem_no_warning(self):
        headings = [_heading(_lines("[Pattern_B](Pattern_B.md)"), is_group=True)]
        index = {"Pattern_B.md": {"aliases": [], "related": []}}
        v = _validator("path/to/Catalogue.md", headings=headings, project_index=index)
        v.check_alias_consistency()
        assert v.warnings == []

    def test_label_matches_alias_no_warning(self):
        headings = [_heading(_lines("[My Alias](Pattern_B.md)"), is_group=True)]
        index = {"Pattern_B.md": {"aliases": ["My Alias"], "related": []}}
        v = _validator("path/to/Catalogue.md", headings=headings, project_index=index)
        v.check_alias_consistency()
        assert v.warnings == []

    def test_unrecognized_label_warns(self):
        headings = [_heading(_lines("[Wrong Label](Pattern_B.md)"), is_group=True)]
        index = {"Pattern_B.md": {"aliases": ["Correct Alias"], "related": []}}
        v = _validator("path/to/Catalogue.md", headings=headings, project_index=index)
        v.check_alias_consistency()
        assert len(v.warnings) == 1
        assert "Wrong Label" in v.warnings[0]["msg"]
        assert "not a recognized alias" in v.warnings[0]["msg"].lower()

    def test_empty_label_warns(self):
        headings = [_heading(_lines("[](Pattern_B.md)"), is_group=True)]
        index = {"Pattern_B.md": {"aliases": [], "related": []}}
        v = _validator("path/to/Catalogue.md", headings=headings, project_index=index)
        v.check_alias_consistency()
        assert len(v.warnings) == 1
        assert "empty" in v.warnings[0]["msg"].lower()

    def test_target_not_in_index_no_warning(self):
        headings = [_heading(_lines("[Any Label](Unknown.md)"), is_group=True)]
        v = _validator("path/to/Catalogue.md", headings=headings, project_index={})
        v.check_alias_consistency()
        assert v.warnings == []

    def test_link_with_path_prefix_resolved_correctly(self):
        headings = [_heading(_lines("[My Alias](../catalogue/Pattern_B.md)"), is_group=True)]
        index = {"Pattern_B.md": {"aliases": ["My Alias"], "related": []}}
        v = _validator("path/to/Catalogue.md", headings=headings, project_index=index)
        v.check_alias_consistency()
        assert v.warnings == []

    def test_target_without_md_extension_added_automatically(self):
        headings = [_heading(_lines("[My Alias](Pattern_B)"), is_group=True)]
        index = {"Pattern_B.md": {"aliases": ["My Alias"], "related": []}}
        v = _validator("path/to/Catalogue.md", headings=headings, project_index=index)
        v.check_alias_consistency()
        assert v.warnings == []

    def test_warning_contains_correct_line_number(self):
        raw = [_entry("no links here", 3), _entry("[Bad](Pattern_B.md)", 7)]
        headings = [_heading(raw, is_group=True)]
        index = {"Pattern_B.md": {"aliases": ["Good Alias"], "related": []}}
        v = _validator("path/to/Catalogue.md", headings=headings, project_index=index)
        v.check_alias_consistency()
        assert v.warnings[0]["line"] == 7

    def test_at_least_one_group_heading_enables_check(self):
        normal = _heading(_lines("[Bad](Pattern_B.md)"), is_group=False)
        group = _heading(_lines("[Good Alias](Pattern_C.md)"), is_group=True)
        index = {
            "Pattern_B.md": {"aliases": ["Correct"], "related": []},
            "Pattern_C.md": {"aliases": ["Good Alias"], "related": []},
        }
        v = _validator("path/to/Catalogue.md", headings=[normal, group], project_index=index)
        v.check_alias_consistency()
        # The non-group heading's link is also checked once a group heading exists
        assert len(v.warnings) == 1
        assert "Bad" in v.warnings[0]["msg"]


# ---------------------------------------------------------------------------
# check_citation_keys
# ---------------------------------------------------------------------------

class TestCheckCitationKeys:

    def test_no_references_content_skips_check(self):
        headings = [_heading(_lines("[MUN'17](References.md#MUN17)"))]
        v = _validator("path/to/Pattern_A.md", headings=headings, references_content=None)
        v.check_citation_keys()
        assert v.warnings == []

    def test_citation_key_found_no_warning(self):
        refs = "## References\n[MUN'17] Munroe, R. ..."
        headings = [_heading(_lines("[MUN'17](References.md#MUN17)"))]
        v = _validator("path/to/Pattern_A.md", headings=headings, references_content=refs)
        v.check_citation_keys()
        assert v.warnings == []

    def test_citation_key_missing_warns(self):
        refs = "## References\n[FOO'99] Foo, B. ..."
        headings = [_heading(_lines("[MUN'17](References.md#MUN17)"))]
        v = _validator("path/to/Pattern_A.md", headings=headings, references_content=refs)
        v.check_citation_keys()
        assert len(v.warnings) == 1
        assert "MUN'17" in v.warnings[0]["msg"]
        assert "not found" in v.warnings[0]["msg"].lower()

    def test_non_references_link_not_checked(self):
        refs = "## References"
        headings = [_heading(_lines("[SomeLabel](Other.md)"))]
        index = {"Other.md": {"aliases": [], "related": []}}
        v = _validator("path/to/Pattern_A.md", headings=headings, project_index=index, references_content=refs)
        v.check_citation_keys()
        assert v.warnings == []

    def test_warning_contains_correct_line_number(self):
        refs = "## References\n[FOO'99] Foo."
        raw = [_entry("text", 1), _entry("[BAR'00](References.md)", 4)]
        headings = [_heading(raw)]
        v = _validator("path/to/Pattern_A.md", headings=headings, references_content=refs)
        v.check_citation_keys()
        assert v.warnings[0]["line"] == 4

    def test_empty_references_content_skips_check(self):
        # Empty string is falsy, treated the same as None — no check performed.
        refs = ""
        headings = [_heading(_lines("[MUN'17](References.md)"))]
        v = _validator("path/to/Pattern_A.md", headings=headings, references_content=refs)
        v.check_citation_keys()
        assert v.warnings == []


# ---------------------------------------------------------------------------
# run_all_checks
# ---------------------------------------------------------------------------

class TestRunAllChecks:

    def test_returns_list(self):
        v = _validator("path/to/Pattern_A.md", project_index={"Pattern_A.md": {"related": [], "aliases": []}})
        result = v.run_all_checks()
        assert isinstance(result, list)

    def test_aggregates_warnings_from_all_checks(self):
        # Trigger: missing reciprocal + missing link target + missing citation
        refs = "## References\n[FOO'99] Foo."
        index = {
            "Pattern_A.md": {"related": ["Pattern_B.md"], "aliases": []},
            "Pattern_B.md": {"related": [], "aliases": []},
        }
        raw = _lines("[MUN'17](References.md)", "[Dead](Dead.md)")
        headings = [_heading(raw)]
        v = _validator("path/to/Pattern_A.md", headings=headings, project_index=index, references_content=refs)
        result = v.run_all_checks()
        assert len(result) >= 3

    def test_warnings_reset_on_each_call(self):
        index = {
            "Pattern_A.md": {"related": ["Pattern_B.md"], "aliases": []},
            "Pattern_B.md": {"related": [], "aliases": []},
        }
        v = _validator("path/to/Pattern_A.md", project_index=index)
        first = v.run_all_checks()
        second = v.run_all_checks()
        assert first == second

    def test_clean_document_returns_empty_list(self):
        index = {"Pattern_A.md": {"related": [], "aliases": []}}
        v = _validator("path/to/Pattern_A.md", project_index=index)
        assert v.run_all_checks() == []