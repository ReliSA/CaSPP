"""Unit tests for utils.file_matcher — FileMatcher class."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

APP_DIR = Path(__file__).resolve().parents[2]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from utils.file_matcher import FileMatcher
from utils.facets_index_template import FACETS_INDEX_TEMPLATE_NAME, PUBLICATIONS_INDEX_TEMPLATE_NAME


def _matcher(templates: dict = None) -> FileMatcher:
    loader = MagicMock()
    loader.get_template.side_effect = lambda name: templates.get(name) if templates else name
    return FileMatcher(loader)


# ---------------------------------------------------------------------------
# Direct parent-folder matching
# ---------------------------------------------------------------------------

class TestDirectFolderMatch:

    def test_catalogue_direct_child_uses_pattern_template(self):
        m = _matcher()
        m.match("catalogue/My_Pattern.md")
        m.loader.get_template.assert_called_with("template-pattern")

    def test_known_folder_returns_correct_template(self):
        # A non-index file inside a known folder still gets the folder template
        m = _matcher()
        m.match("facets/publications/some_other_file.md")
        m.loader.get_template.assert_called_with("template-publication")

    def test_categories_folder_returns_category_template(self):
        m = _matcher()
        m.match("facets/categories/some_file.md")
        m.loader.get_template.assert_called_with("template-category")

    def test_unknown_folder_returns_none(self):
        m = _matcher()
        result = m.match("unknown_folder/file.md")
        assert result is None

    def test_too_short_path_returns_none(self):
        m = _matcher()
        result = m.match("file.md")
        assert result is None


# ---------------------------------------------------------------------------
# Grandparent-folder fallback (nested publication subfolders)
# ---------------------------------------------------------------------------

class TestGrandparentFolderFallback:

    def test_publication_subfolder_gets_publication_template(self):
        m = _matcher()
        m.match("catalogue/facets/publications/ber24/ber24.md")
        m.loader.get_template.assert_called_with("template-publication")

    def test_category_subfolder_gets_category_template(self):
        m = _matcher()
        m.match("catalogue/facets/categories/subcat/subcat.md")
        m.loader.get_template.assert_called_with("template-category")

    def test_nested_unknown_grandparent_returns_none(self):
        m = _matcher()
        result = m.match("some/unknown/nested/file.md")
        assert result is None

    def test_backslash_path_handled(self):
        m = _matcher()
        m.match("catalogue\\facets\\publications\\ber24\\ber24.md")
        m.loader.get_template.assert_called_with("template-publication")


# ---------------------------------------------------------------------------
# Facets index file detection (stem == parent folder, grandparent == "facets")
# ---------------------------------------------------------------------------

class TestFacetsIndexDetection:

    def test_methodologies_index_gets_facets_index_template(self):
        m = _matcher()
        result = m.match("catalogue/facets/methodologies/methodologies.md")
        assert result is not None
        assert result.name == FACETS_INDEX_TEMPLATE_NAME

    def test_categories_index_gets_facets_index_template(self):
        m = _matcher()
        result = m.match("catalogue/facets/categories/categories.md")
        assert result is not None
        assert result.name == FACETS_INDEX_TEMPLATE_NAME

    def test_publications_index_gets_publications_index_template(self):
        m = _matcher()
        result = m.match("catalogue/facets/publications/publications.md")
        assert result is not None
        assert result.name == PUBLICATIONS_INDEX_TEMPLATE_NAME

    def test_regular_file_in_methodologies_not_affected(self):
        m = _matcher()
        m.match("catalogue/facets/methodologies/General.md")
        m.loader.get_template.assert_called_with("template-methodology")

    def test_publication_subfolder_file_not_affected(self):
        m = _matcher()
        m.match("catalogue/facets/publications/ber24/ber24.md")
        m.loader.get_template.assert_called_with("template-publication")

    def test_backslash_path_index_detected(self):
        m = _matcher()
        result = m.match("catalogue\\facets\\methodologies\\methodologies.md")
        assert result is not None
        assert result.name == FACETS_INDEX_TEMPLATE_NAME

    def test_facets_index_template_has_variable_h1(self):
        m = _matcher()
        result = m.match("catalogue/facets/categories/categories.md")
        h1 = next((h for h in result.headings if h.level == 1), None)
        assert h1 is not None
        assert h1.is_variable is True

    def test_facets_index_template_has_no_required_content_type(self):
        # expected_types={"text"} → excluded from check → no content type required
        m = _matcher()
        result = m.match("catalogue/facets/methodologies/methodologies.md")
        h1 = result.headings[0]
        assert h1.content_rules.expected_types == {"text"}

    def test_publications_index_template_has_az_group(self):
        m = _matcher()
        result = m.match("catalogue/facets/publications/publications.md")
        az = next((h for h in result.headings if h.is_group), None)
        assert az is not None
        assert az.text == "[A-Z]"
        assert az.optional is True

    def test_publications_index_template_az_requires_no_specific_letters(self):
        m = _matcher()
        result = m.match("catalogue/facets/publications/publications.md")
        az = next(h for h in result.headings if h.is_group)
        assert az.group_members == []