"""Tests for Config repository resolution and MarkdownAnalyzer base path."""

from pathlib import Path

import pytest

from core.analyzer import markdown_analyzer as markdown_analyzer_module
from core.analyzer.markdown_analyzer import MarkdownAnalyzer
from core.config import Config
from utils.constants import AppConstants
from utils.exceptions import FileNotFoundError as AppFileNotFoundError, InvalidInputError


def test_config_get_base_path_uses_git_directory_in_cwd_or_parents(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    repo = tmp_path / "myrepo"
    repo.mkdir()
    (repo / ".git").mkdir()
    nested = repo / "docs" / "nested"
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)

    base = Config.get_base_path()

    assert base.resolve() == repo.resolve()


def test_config_get_base_path_raises_when_no_git_repository(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    empty = tmp_path / "nogit"
    empty.mkdir()
    monkeypatch.chdir(empty)

    with pytest.raises(RuntimeError, match="No Git repository"):
        Config.get_base_path()


def test_config_get_default_markdown_path_relative_to_repo_root(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo = tmp_path / "root"
    repo.mkdir()
    (repo / ".git").mkdir()
    monkeypatch.chdir(repo)

    path = Config.get_default_markdown_path()

    assert path == str(repo / AppConstants.DEFAULT_MARKDOWN_FILE)


def test_markdown_analyzer_default_base_path_is_application_directory() -> None:
    analyzer = MarkdownAnalyzer()
    expected = Path(markdown_analyzer_module.__file__).resolve().parent.parent.parent
    assert analyzer.base_path.resolve() == expected.resolve()


def test_markdown_analyzer_accepts_explicit_existing_base_path(tmp_path: Path) -> None:
    analyzer = MarkdownAnalyzer(base_path=str(tmp_path))
    assert analyzer.base_path.resolve() == tmp_path.resolve()


def test_markdown_analyzer_raises_when_explicit_base_missing(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist"
    with pytest.raises(AppFileNotFoundError):
        MarkdownAnalyzer(base_path=str(missing))


def test_markdown_analyzer_rejects_invalid_base_path_type() -> None:
    with pytest.raises(InvalidInputError):
        MarkdownAnalyzer(base_path=123)  # type: ignore[arg-type]
