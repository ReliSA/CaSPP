"""Unit tests for utils.markdown_analyzer — MarkdownAnalyzer class."""

import sys
from pathlib import Path

import pytest

APP_DIR = Path(__file__).resolve().parents[2]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from utils.constants import ReportConstants
from utils.exceptions import FileNotFoundError as AppFileNotFoundError
from utils.exceptions import InvalidInputError
from core.analyzer.markdown_analyzer import MarkdownAnalyzer
from utils.parsers.markdown_parser import ContentInfo, DocumentMeta, HeadingInfo, MarkdownParser, ParsedDocument
from utils.parsers.template_parser import DocumentRules, HeadingRules, TemplateParser, TemplateRules

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"
SAMPLE_MD = (FIXTURES_DIR / "sample_pattern.md").read_text(encoding="utf-8")
TEMPLATE_PATTERN_MD = (FIXTURES_DIR / "template_pattern.md").read_text(encoding="utf-8")


def _analyzer(base_path=None) -> MarkdownAnalyzer:
    return MarkdownAnalyzer(base_path=base_path)


def _parse_doc(filepath: str, content: str) -> ParsedDocument:
    return MarkdownParser().parse_content(filepath, content)


def _parse_template(content: str) -> TemplateRules:
    return TemplateParser().parse_content("fake/t.md", content)


def _heading(level: int, text: str, line: int = 1, is_empty: bool = False) -> HeadingInfo:
    content = ContentInfo(is_empty=is_empty)
    if not is_empty:
        content.found_types = {"text"}
        content.first_content_line = line + 1
    return HeadingInfo(level=level, text=text, raw_text=text, line_number=line, content=content)


def _heading_rule(level: int, text: str, optional: bool = False, is_variable: bool = False) -> HeadingRules:
    return HeadingRules(level=level, text=text, optional=optional, is_variable=is_variable)


# ---------------------------------------------------------------------------
# MarkdownAnalyzer.__init__
# ---------------------------------------------------------------------------

class TestMarkdownAnalyzerInit:

    def test_default_base_path_is_set(self):
        analyzer = _analyzer()
        assert analyzer.base_path is not None
        assert isinstance(analyzer.base_path, Path)

    def test_custom_base_path_accepted(self, tmp_path):
        analyzer = _analyzer(base_path=str(tmp_path))
        assert analyzer.base_path == tmp_path

    def test_path_object_accepted(self, tmp_path):
        analyzer = _analyzer(base_path=tmp_path)
        assert analyzer.base_path == tmp_path

    def test_nonexistent_path_raises(self):
        with pytest.raises(AppFileNotFoundError):
            _analyzer(base_path="/nonexistent/path/xyz")

    def test_non_string_base_path_raises(self):
        with pytest.raises(InvalidInputError):
            _analyzer(base_path=42)

    def test_warnings_initially_empty(self):
        assert _analyzer().current_warnings == []

    def test_passed_initially_empty(self):
        assert _analyzer().current_passed == []

    def test_get_base_path_returns_path(self, tmp_path):
        analyzer = _analyzer(base_path=tmp_path)
        assert analyzer.get_base_path() == tmp_path


# ---------------------------------------------------------------------------
# _check_h1_count
# ---------------------------------------------------------------------------

class TestCheckH1Count:

    def setup_method(self):
        self.analyzer = _analyzer()
        self.analyzer.current_warnings = []
        self.analyzer.current_passed = []

    def test_zero_h1_adds_warning(self):
        self.analyzer._check_h1_count([])
        assert len(self.analyzer.current_warnings) == 1
        assert "missing" in self.analyzer.current_warnings[0]["msg"].lower()

    def test_one_h1_adds_passed(self):
        h1 = _heading(1, "Title")
        self.analyzer._check_h1_count([h1])
        assert len(self.analyzer.current_warnings) == 0
        assert len(self.analyzer.current_passed) == 1

    def test_multiple_h1_adds_warning(self):
        h1a = _heading(1, "First", line=1)
        h1b = _heading(1, "Second", line=5)
        self.analyzer._check_h1_count([h1a, h1b])
        assert len(self.analyzer.current_warnings) == 1
        assert "2" in self.analyzer.current_warnings[0]["msg"]

    def test_multiple_h1_warning_mentions_line_numbers(self):
        h1a = _heading(1, "First", line=1)
        h1b = _heading(1, "Second", line=10)
        self.analyzer._check_h1_count([h1a, h1b])
        msg = self.analyzer.current_warnings[0]["msg"]
        assert "1" in msg and "10" in msg


# ---------------------------------------------------------------------------
# _check_h1_filename
# ---------------------------------------------------------------------------

class TestCheckH1Filename:

    def setup_method(self):
        self.analyzer = _analyzer()
        self.analyzer.current_warnings = []
        self.analyzer.current_passed = []

    def _meta(self, h1_value, filepath) -> DocumentMeta:
        return DocumentMeta(h1_value=h1_value, filepath=filepath)

    def test_matching_filename_passes(self):
        meta = self._meta("Sample Pattern", "path/sample_pattern.md")
        self.analyzer._check_h1_filename(meta)
        assert len(self.analyzer.current_warnings) == 0
        assert len(self.analyzer.current_passed) == 1

    def test_mismatched_h1_adds_warning(self):
        meta = self._meta("Wrong Title", "path/sample_pattern.md")
        self.analyzer._check_h1_filename(meta)
        assert len(self.analyzer.current_warnings) == 1
        assert "sample_pattern" in self.analyzer.current_warnings[0]["msg"]

    def test_h1_value_none_skips_silently(self):
        meta = self._meta(None, "path/sample_pattern.md")
        self.analyzer._check_h1_filename(meta)
        assert len(self.analyzer.current_warnings) == 0
        assert len(self.analyzer.current_passed) == 0

    def test_empty_filepath_skips_silently(self):
        meta = self._meta("Sample Pattern", "")
        self.analyzer._check_h1_filename(meta)
        assert len(self.analyzer.current_warnings) == 0

    def test_case_insensitive_comparison(self):
        meta = self._meta("SAMPLE PATTERN", "path/sample_pattern.md")
        self.analyzer._check_h1_filename(meta)
        assert len(self.analyzer.current_warnings) == 0

    def test_spaces_normalized_to_underscores(self):
        meta = self._meta("My Document", "docs/My_Document.md")
        self.analyzer._check_h1_filename(meta)
        assert len(self.analyzer.current_warnings) == 0


# ---------------------------------------------------------------------------
# _check_h1_prefix
# ---------------------------------------------------------------------------

class TestCheckH1Prefix:

    def setup_method(self):
        self.analyzer = _analyzer()
        self.analyzer.current_warnings = []
        self.analyzer.current_passed = []

    def _doc_rules(self, h1_prefix) -> DocumentRules:
        return DocumentRules(h1_prefix=h1_prefix)

    def _meta(self, h1_prefix) -> DocumentMeta:
        return DocumentMeta(h1_prefix=h1_prefix)

    def test_both_none_passes(self):
        self.analyzer._check_h1_prefix(self._meta(None), self._doc_rules(None))
        assert len(self.analyzer.current_warnings) == 0
        assert len(self.analyzer.current_passed) == 1

    def test_matching_prefix_passes(self):
        self.analyzer._check_h1_prefix(self._meta("Category"), self._doc_rules("Category"))
        assert len(self.analyzer.current_warnings) == 0

    def test_unexpected_prefix_warns(self):
        self.analyzer._check_h1_prefix(self._meta("Category"), self._doc_rules(None))
        assert len(self.analyzer.current_warnings) == 1
        assert "unexpected" in self.analyzer.current_warnings[0]["msg"].lower()

    def test_missing_required_prefix_warns(self):
        self.analyzer._check_h1_prefix(self._meta(None), self._doc_rules("Category"))
        assert len(self.analyzer.current_warnings) == 1
        assert "missing" in self.analyzer.current_warnings[0]["msg"].lower()

    def test_wrong_prefix_warns(self):
        self.analyzer._check_h1_prefix(self._meta("Form"), self._doc_rules("Category"))
        assert len(self.analyzer.current_warnings) == 1
        assert "Form" in self.analyzer.current_warnings[0]["msg"]


# ---------------------------------------------------------------------------
# _check_mandatory_sections
# ---------------------------------------------------------------------------

class TestCheckMandatorySections:

    def setup_method(self):
        self.analyzer = _analyzer()
        self.analyzer.current_warnings = []
        self.analyzer.current_passed = []

    def test_all_mandatory_present_passes(self):
        doc_map = {"Context": _heading(2, "Context"), "Problem": _heading(2, "Problem")}
        template = [_heading_rule(2, "Context"), _heading_rule(2, "Problem")]
        self.analyzer._check_mandatory_sections(doc_map, template)
        assert len(self.analyzer.current_warnings) == 0
        assert len(self.analyzer.current_passed) == 1

    def test_missing_mandatory_warns(self):
        doc_map = {"Context": _heading(2, "Context")}
        template = [_heading_rule(2, "Context"), _heading_rule(2, "Problem")]
        self.analyzer._check_mandatory_sections(doc_map, template)
        assert len(self.analyzer.current_warnings) == 1
        assert "Problem" in self.analyzer.current_warnings[0]["msg"]

    def test_optional_section_missing_does_not_warn(self):
        doc_map = {"Context": _heading(2, "Context")}
        template = [_heading_rule(2, "Context"), _heading_rule(2, "Notes", optional=True)]
        self.analyzer._check_mandatory_sections(doc_map, template)
        assert len(self.analyzer.current_warnings) == 0

    def test_multiple_missing_mandatory_generates_multiple_warnings(self):
        doc_map = {}
        template = [_heading_rule(2, "Context"), _heading_rule(2, "Problem"), _heading_rule(2, "Solution")]
        self.analyzer._check_mandatory_sections(doc_map, template)
        assert len(self.analyzer.current_warnings) == 3


# ---------------------------------------------------------------------------
# _check_section_order
# ---------------------------------------------------------------------------

class TestCheckSectionOrder:

    def setup_method(self):
        self.analyzer = _analyzer()
        self.analyzer.current_warnings = []
        self.analyzer.current_passed = []

    def test_correct_order_passes(self):
        doc_headings = [_heading(2, "Context", 2), _heading(2, "Problem", 5)]
        template = [_heading_rule(2, "Context"), _heading_rule(2, "Problem")]
        self.analyzer._check_section_order(doc_headings, template)
        assert len(self.analyzer.current_warnings) == 0
        assert len(self.analyzer.current_passed) == 1

    def test_reversed_order_warns(self):
        doc_headings = [_heading(2, "Problem", 2), _heading(2, "Context", 5)]
        template = [_heading_rule(2, "Context"), _heading_rule(2, "Problem")]
        self.analyzer._check_section_order(doc_headings, template)
        assert len(self.analyzer.current_warnings) == 1
        assert "Context" in self.analyzer.current_warnings[0]["msg"]

    def test_extra_doc_sections_not_in_template_ignored(self):
        doc_headings = [_heading(2, "Context", 2), _heading(2, "Unknown", 4), _heading(2, "Problem", 6)]
        template = [_heading_rule(2, "Context"), _heading_rule(2, "Problem")]
        self.analyzer._check_section_order(doc_headings, template)
        assert len(self.analyzer.current_warnings) == 0

    def test_empty_doc_headings_passes(self):
        self.analyzer._check_section_order([], [_heading_rule(2, "Context")])
        assert len(self.analyzer.current_warnings) == 0


# ---------------------------------------------------------------------------
# _check_no_unknown_sections
# ---------------------------------------------------------------------------

class TestCheckNoUnknownSections:

    def setup_method(self):
        self.analyzer = _analyzer()
        self.analyzer.current_warnings = []
        self.analyzer.current_passed = []

    def _template(self, headings) -> TemplateRules:
        return TemplateRules(headings=headings)

    def test_all_known_sections_passes(self):
        doc_headings = [_heading(2, "Context")]
        template = self._template([_heading_rule(2, "Context")])
        self.analyzer._check_no_unknown_sections(doc_headings, template)
        assert len(self.analyzer.current_warnings) == 0
        assert len(self.analyzer.current_passed) == 1

    def test_unknown_section_warns(self):
        doc_headings = [_heading(2, "RandomSection")]
        template = self._template([_heading_rule(2, "Context")])
        self.analyzer._check_no_unknown_sections(doc_headings, template)
        assert len(self.analyzer.current_warnings) == 1
        assert "RandomSection" in self.analyzer.current_warnings[0]["msg"]

    def test_variable_h1_not_flagged_as_unknown(self):
        doc_headings = [_heading(1, "My Pattern Title")]
        h1_rule = HeadingRules(level=1, text="*Pattern Name*", is_variable=True)
        template = self._template([h1_rule])
        self.analyzer._check_no_unknown_sections(doc_headings, template)
        assert len(self.analyzer.current_warnings) == 0

    def test_non_variable_h1_in_template_not_skipped(self):
        doc_headings = [_heading(1, "Unexpected")]
        template = self._template([_heading_rule(1, "Expected Title")])
        self.analyzer._check_no_unknown_sections(doc_headings, template)
        assert len(self.analyzer.current_warnings) == 1


# ---------------------------------------------------------------------------
# _check_heading_levels
# ---------------------------------------------------------------------------

class TestCheckHeadingLevels:

    def setup_method(self):
        self.analyzer = _analyzer()
        self.analyzer.current_warnings = []
        self.analyzer.current_passed = []

    def test_correct_levels_pass(self):
        doc_map = {"Context": _heading(2, "Context")}
        template = [_heading_rule(2, "Context")]
        self.analyzer._check_heading_levels(doc_map, template)
        assert len(self.analyzer.current_warnings) == 0
        assert len(self.analyzer.current_passed) == 1

    def test_wrong_level_warns(self):
        doc_map = {"Context": _heading(3, "Context")}
        template = [_heading_rule(2, "Context")]
        self.analyzer._check_heading_levels(doc_map, template)
        assert len(self.analyzer.current_warnings) == 1
        msg = self.analyzer.current_warnings[0]["msg"]
        assert "H3" in msg and "H2" in msg

    def test_section_not_in_doc_is_skipped(self):
        doc_map = {}
        template = [_heading_rule(2, "Missing")]
        self.analyzer._check_heading_levels(doc_map, template)
        assert len(self.analyzer.current_warnings) == 0


# ---------------------------------------------------------------------------
# _validate_breadcrumbs
# ---------------------------------------------------------------------------

class TestValidateBreadcrumbs:

    def setup_method(self):
        self.analyzer = _analyzer()
        self.analyzer.current_warnings = []
        self.analyzer.current_passed = []

    def _meta(self, breadcrumbs) -> DocumentMeta:
        return DocumentMeta(breadcrumbs=breadcrumbs)

    def _doc_rules(self, breadcrumbs) -> DocumentRules:
        return DocumentRules(breadcrumbs=breadcrumbs)

    def test_missing_breadcrumbs_warns(self):
        meta = self._meta([])
        self.analyzer._validate_breadcrumbs(meta, self._doc_rules(["Home", "Catalogue", "Pattern"]))
        assert len(self.analyzer.current_warnings) == 1
        assert "missing" in self.analyzer.current_warnings[0]["msg"].lower()

    def test_valid_breadcrumbs_pass(self):
        meta = self._meta(["Home", "Catalogue", "Pattern"])
        rules = self._doc_rules(["Home", "Catalogue", "Pattern"])
        self.analyzer._validate_breadcrumbs(meta, rules)
        assert len(self.analyzer.current_warnings) == 0
        assert len(self.analyzer.current_passed) == 1

    def test_wrong_count_warns(self):
        meta = self._meta(["Home", "Pattern"])
        rules = self._doc_rules(["Home", "Catalogue", "Pattern"])
        self.analyzer._validate_breadcrumbs(meta, rules)
        assert len(self.analyzer.current_warnings) == 1
        assert "2" in self.analyzer.current_warnings[0]["msg"]
        assert "3" in self.analyzer.current_warnings[0]["msg"]

    def test_fixed_part_mismatch_warns(self):
        meta = self._meta(["Home", "Wrong", "Pattern"])
        rules = self._doc_rules(["Home", "Catalogue", "Pattern"])
        self.analyzer._validate_breadcrumbs(meta, rules)
        assert len(self.analyzer.current_warnings) == 1
        assert "Wrong" in self.analyzer.current_warnings[0]["msg"]

    def test_wildcard_part_accepts_any_nonempty(self):
        meta = self._meta(["Home", "Catalogue", "My Pattern"])
        rules = self._doc_rules(["Home", "Catalogue", "*Pattern name*"])
        self.analyzer._validate_breadcrumbs(meta, rules)
        assert len(self.analyzer.current_warnings) == 0

    def test_empty_wildcard_warns(self):
        meta = self._meta(["Home", "Catalogue", ""])
        rules = self._doc_rules(["Home", "Catalogue", "*Pattern name*"])
        self.analyzer._validate_breadcrumbs(meta, rules)
        assert len(self.analyzer.current_warnings) == 1
        assert "wildcard" in self.analyzer.current_warnings[0]["msg"].lower()


# ---------------------------------------------------------------------------
# _check_breadcrumb_links
# ---------------------------------------------------------------------------

class TestCheckBreadcrumbLinks:

    def setup_method(self):
        self.analyzer = _analyzer()
        self.analyzer.current_warnings = []
        self.analyzer.current_passed = []

    def test_no_breadcrumbs_skips(self):
        meta = DocumentMeta(breadcrumbs=[], filepath="/some/file.md")
        self.analyzer._check_breadcrumb_links(meta)
        assert len(self.analyzer.current_warnings) == 0
        assert len(self.analyzer.current_passed) == 0

    def test_no_filepath_skips(self):
        meta = DocumentMeta(breadcrumbs=["[Home](README.md)"], filepath="")
        self.analyzer._check_breadcrumb_links(meta)
        assert len(self.analyzer.current_warnings) == 0

    def test_existing_linked_file_passes(self, tmp_path):
        target = tmp_path / "README.md"
        target.write_text("# Home", encoding="utf-8")
        source = tmp_path / "sub" / "file.md"
        source.parent.mkdir()
        source.write_text("content", encoding="utf-8")
        meta = DocumentMeta(
            breadcrumbs=[f"[Home](../README.md)"],
            filepath=str(source),
        )
        self.analyzer._check_breadcrumb_links(meta)
        assert len(self.analyzer.current_warnings) == 0
        assert len(self.analyzer.current_passed) == 1

    def test_missing_linked_file_warns(self, tmp_path):
        source = tmp_path / "file.md"
        source.write_text("content", encoding="utf-8")
        meta = DocumentMeta(
            breadcrumbs=["[Home](nonexistent.md)"],
            filepath=str(source),
        )
        self.analyzer._check_breadcrumb_links(meta)
        assert len(self.analyzer.current_warnings) == 1
        assert "nonexistent.md" in self.analyzer.current_warnings[0]["msg"]

    def test_crumb_without_link_is_ignored(self, tmp_path):
        source = tmp_path / "file.md"
        source.write_text("content", encoding="utf-8")
        meta = DocumentMeta(breadcrumbs=["PlainText"], filepath=str(source))
        self.analyzer._check_breadcrumb_links(meta)
        assert len(self.analyzer.current_warnings) == 0


# ---------------------------------------------------------------------------
# find_markdown_links
# ---------------------------------------------------------------------------

class TestFindMarkdownLinks:

    def setup_method(self):
        self.analyzer = _analyzer()

    def test_finds_single_link(self):
        links = self.analyzer.find_markdown_links("[Title](page.md)")
        assert len(links) == 1
        assert links[0]["text"] == "Title"
        assert links[0]["url"] == "page.md"

    def test_finds_multiple_links(self):
        content = "[A](a.md) and [B](b.md)"
        links = self.analyzer.find_markdown_links(content)
        assert len(links) == 2

    def test_empty_content_returns_empty_list(self):
        assert self.analyzer.find_markdown_links("") == []

    def test_whitespace_only_returns_empty_list(self):
        assert self.analyzer.find_markdown_links("   \n  ") == []

    def test_non_string_raises(self):
        with pytest.raises(InvalidInputError):
            self.analyzer.find_markdown_links(123)

    def test_md_extension_type_is_markdown(self):
        links = self.analyzer.find_markdown_links("[Doc](guide.md)")
        assert links[0]["type"] == "markdown"

    def test_markdown_extension_type_is_markdown(self):
        links = self.analyzer.find_markdown_links("[Doc](guide.markdown)")
        assert links[0]["type"] == "markdown"

    def test_other_extension_type_is_other(self):
        links = self.analyzer.find_markdown_links("[Site](https://example.com)")
        assert links[0]["type"] == "other"

    def test_line_position_first_line(self):
        links = self.analyzer.find_markdown_links("[A](a.md)")
        assert links[0]["line_position"] == 1

    def test_line_position_second_line(self):
        links = self.analyzer.find_markdown_links("text\n[A](a.md)")
        assert links[0]["line_position"] == 2

    def test_no_links_in_plain_text(self):
        assert self.analyzer.find_markdown_links("No links here at all.") == []


# ---------------------------------------------------------------------------
# check_file_exists
# ---------------------------------------------------------------------------

class TestCheckFileExists:

    def setup_method(self):
        self.analyzer = _analyzer()

    def test_existing_file_returns_true(self, tmp_path):
        f = tmp_path / "doc.md"
        f.write_text("content", encoding="utf-8")
        exists, path = self.analyzer.check_file_exists("doc.md", str(tmp_path / "source.md"))
        assert exists is True
        assert "doc.md" in path

    def test_nonexistent_file_returns_false(self, tmp_path):
        exists, path = self.analyzer.check_file_exists("missing.md", str(tmp_path / "source.md"))
        assert exists is False

    def test_empty_file_path_raises(self, tmp_path):
        with pytest.raises(InvalidInputError):
            self.analyzer.check_file_exists("", str(tmp_path / "source.md"))

    def test_empty_relative_to_raises(self):
        with pytest.raises(InvalidInputError):
            self.analyzer.check_file_exists("doc.md", "")

    def test_non_string_file_path_raises(self, tmp_path):
        with pytest.raises(InvalidInputError):
            self.analyzer.check_file_exists(None, str(tmp_path / "source.md"))

    def test_non_string_relative_to_raises(self):
        with pytest.raises(InvalidInputError):
            self.analyzer.check_file_exists("doc.md", None)

    def test_absolute_path_resolved_directly(self, tmp_path):
        f = tmp_path / "absolute.md"
        f.write_text("content", encoding="utf-8")
        exists, _ = self.analyzer.check_file_exists(str(f), str(tmp_path / "source.md"))
        assert exists is True

    def test_relative_path_resolved_from_source_dir(self, tmp_path):
        sub = tmp_path / "sub"
        sub.mkdir()
        target = tmp_path / "README.md"
        target.write_text("content", encoding="utf-8")
        source = sub / "page.md"
        exists, _ = self.analyzer.check_file_exists("../README.md", str(source))
        assert exists is True


# ---------------------------------------------------------------------------
# generate_report
# ---------------------------------------------------------------------------

class TestGenerateReport:

    def setup_method(self):
        self.analyzer = _analyzer()

    def test_warning_icon_present(self):
        analysis = {
            "file": "test.md",
            "warnings": [{"line": 5, "msg": "Something is wrong"}],
            "passed": [],
        }
        report = self.analyzer.generate_report(analysis)
        assert ReportConstants.ICON_WARNING in report
        assert "Something is wrong" in report

    def test_ok_icon_present(self):
        analysis = {
            "file": "test.md",
            "warnings": [],
            "passed": ["All sections present."],
        }
        report = self.analyzer.generate_report(analysis)
        assert ReportConstants.ICON_OK in report
        assert "All sections present." in report

    def test_error_key_shows_error_message(self):
        report = self.analyzer.generate_report({"error": "Something broke"})
        assert "Something broke" in report

    def test_no_checks_message_when_empty(self):
        analysis = {"file": "test.md", "warnings": [], "passed": []}
        report = self.analyzer.generate_report(analysis)
        assert "No checks" in report

    def test_non_dict_raises(self):
        with pytest.raises(InvalidInputError):
            self.analyzer.generate_report("not a dict")

    def test_report_starts_with_heading(self):
        analysis = {"file": "test.md", "warnings": [], "passed": []}
        assert self.analyzer.generate_report(analysis).startswith("#")

    def test_line_number_in_warning_output(self):
        analysis = {
            "file": "test.md",
            "warnings": [{"line": 42, "msg": "Problem here"}],
            "passed": [],
        }
        report = self.analyzer.generate_report(analysis)
        assert "42" in report


# ---------------------------------------------------------------------------
# validate_structure — integration tests using real fixture files
# ---------------------------------------------------------------------------

class TestValidateStructure:
    """Integration tests: parse sample_pattern.md against template_pattern.md."""

    def setup_method(self):
        self.analyzer = _analyzer()
        self.doc = MarkdownParser().parse_content(
            str(FIXTURES_DIR / "sample_pattern.md"), SAMPLE_MD
        )
        template_parser = TemplateParser()
        self.template = template_parser.parse_content(
            str(FIXTURES_DIR / "template_pattern.md"), TEMPLATE_PATTERN_MD
        )

    def test_returns_dict_with_required_keys(self):
        result = self.analyzer.validate_structure(self.doc, self.template)
        assert "file" in result
        assert "warnings" in result
        assert "passed" in result

    def test_passed_list_is_nonempty(self):
        result = self.analyzer.validate_structure(self.doc, self.template)
        assert len(result["passed"]) > 0

    def test_warnings_list_is_list(self):
        result = self.analyzer.validate_structure(self.doc, self.template)
        assert isinstance(result["warnings"], list)

    def test_state_reset_between_calls(self):
        self.analyzer.validate_structure(self.doc, self.template)
        result2 = self.analyzer.validate_structure(self.doc, self.template)
        # State must not accumulate across calls
        assert result2["warnings"] == self.analyzer.current_warnings
        assert result2["passed"] == self.analyzer.current_passed

    def test_missing_section_generates_warning(self):
        truncated = SAMPLE_MD.split("## Context")[0]
        doc = MarkdownParser().parse_content(str(FIXTURES_DIR / "sample_pattern.md"), truncated)
        result = self.analyzer.validate_structure(doc, self.template)
        warning_msgs = [w["msg"] for w in result["warnings"]]
        assert any("Context" in m for m in warning_msgs)

    def test_h1_match_passes(self):
        result = self.analyzer.validate_structure(self.doc, self.template)
        passed = result["passed"]
        assert any("H1" in p or "filename" in p.lower() for p in passed)

    def test_generate_report_from_validate_structure(self):
        result = self.analyzer.validate_structure(self.doc, self.template)
        report = self.analyzer.generate_report(result)
        assert len(report) > 0
        assert "#" in report


# ---------------------------------------------------------------------------
# validate_structure — targeted edge cases
# ---------------------------------------------------------------------------

class TestValidateStructureEdgeCases:

    def setup_method(self):
        self.analyzer = _analyzer()

    def _validate(self, doc_content: str, template_content: str, filepath: str = "fake/doc.md"):
        doc = _parse_doc(filepath, doc_content)
        template = _parse_template(template_content)
        return self.analyzer.validate_structure(doc, template)

    def test_extra_unknown_section_warns(self):
        result = self._validate(
            "[Home](README.md) > Docs\n\n# Doc\n\n## Context\n\nText.\n\n## Unknown\n\nText.\n",
            "[Home](README.md) > Docs\n\n# *Title*\n\n## Context\n\nText.\n",
        )
        warning_msgs = [w["msg"] for w in result["warnings"]]
        assert any("Unknown" in m for m in warning_msgs)

    def test_out_of_order_section_warns(self):
        result = self._validate(
            "[Home](README.md) > Docs\n\n# Doc\n\n## Problem\n\nText.\n\n## Context\n\nText.\n",
            "[Home](README.md) > Docs\n\n# *Title*\n\n## Context\n\nText.\n\n## Problem\n\nText.\n",
        )
        warning_msgs = [w["msg"] for w in result["warnings"]]
        assert any("order" in m.lower() for m in warning_msgs)

    def test_wrong_heading_level_warns(self):
        result = self._validate(
            "[Home](README.md) > Docs\n\n# Doc\n\n### Context\n\nText.\n",
            "[Home](README.md) > Docs\n\n# *Title*\n\n## Context\n\nText.\n",
        )
        warning_msgs = [w["msg"] for w in result["warnings"]]
        assert any("H3" in m and "H2" in m for m in warning_msgs)

    def test_empty_mandatory_section_warns(self):
        result = self._validate(
            "[Home](README.md) > Docs\n\n# Doc\n\n## Context\n\n",
            "[Home](README.md) > Docs\n\n# *Title*\n\n## Context\n\nText.\n",
        )
        warning_msgs = [w["msg"] for w in result["warnings"]]
        assert any("empty" in m.lower() for m in warning_msgs)
