"""Unit tests for utils.git.runner helpers."""

from pathlib import Path

import pytest
from git import Repo

from fixtures.git_fixtures import init_repo_with_readme
from utils.git import runner


def test_normalize_repo_path_relative_inside_repo(tmp_path: Path) -> None:
    repo = init_repo_with_readme(tmp_path)
    readme = tmp_path / "README.md"
    assert runner.normalize_repo_path(repo, "README.md") == "README.md"
    assert runner.normalize_repo_path(repo, str(readme)) == "README.md"


def test_normalize_repo_path_absolute_inside_repo(tmp_path: Path) -> None:
    repo = init_repo_with_readme(tmp_path)
    readme = tmp_path / "README.md"
    assert runner.normalize_repo_path(repo, str(readme.resolve())) == "README.md"


def test_normalize_repo_path_absolute_outside_repo_raises(tmp_path: Path) -> None:
    repo = init_repo_with_readme(tmp_path)
    outside = tmp_path.parent / "outside_repo_normalize_test.md"
    outside.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="not within repository"):
        runner.normalize_repo_path(repo, str(outside.resolve()))


def test_is_markdown_file_recognizes_extensions() -> None:
    assert runner.is_markdown_file("foo.md") is True
    assert runner.is_markdown_file("bar.markdown") is True
    assert runner.is_markdown_file("BAR.MD") is True
    assert runner.is_markdown_file("notes.txt") is False
    assert runner.is_markdown_file("readme") is False


def test_find_git_repo_from_subdirectory(tmp_path: Path) -> None:
    repo = init_repo_with_readme(tmp_path)
    sub = tmp_path / "deep" / "nested"
    sub.mkdir(parents=True)
    # Path must exist: GitPython may not resolve a repo from a non-existent file path.
    found = runner.find_git_repo(str(sub))
    assert found == str(repo.working_dir)


def test_find_git_repo_non_repo_returns_none(tmp_path: Path) -> None:
    no_git = tmp_path / "nogit"
    no_git.mkdir()
    assert runner.find_git_repo(str(no_git)) is None


def test_get_status_untracked_modified_and_markdown_filter(tmp_path: Path) -> None:
    init_repo_with_readme(tmp_path)
    repo = Repo(tmp_path)
    (tmp_path / "new.md").write_text("x\n", encoding="utf-8")
    (tmp_path / "other.txt").write_text("y\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("changed\n", encoding="utf-8")

    full = runner.get_status(repo, markdown_only=False)
    assert "new.md" in full["untracked"]
    assert "other.txt" in full["untracked"]
    assert "README.md" in full["modified"]

    md_only = runner.get_status(repo, markdown_only=True)
    assert "other.txt" not in md_only["untracked"]
    assert "new.md" in md_only["untracked"]
    assert "README.md" in md_only["modified"]


def test_format_status_message_includes_sections(tmp_path: Path) -> None:
    init_repo_with_readme(tmp_path)
    repo = Repo(tmp_path)
    (tmp_path / "u.md").write_text("u\n", encoding="utf-8")
    status = runner.get_status(repo, markdown_only=True)
    branch = runner.get_current_branch(repo)
    text = runner.format_status_message(branch, status, markdown_only=True)
    assert f"Branch: {branch}" in text
    assert "u.md" in text
    assert "Untracked files:" in text


def test_format_status_message_clean_working_tree(tmp_path: Path) -> None:
    init_repo_with_readme(tmp_path)
    repo = Repo(tmp_path)
    status = runner.get_status(repo, markdown_only=False)
    text = runner.format_status_message("main", status, markdown_only=False)
    assert "Working directory clean" in text


def test_get_status_staged_add_lists_added(tmp_path: Path) -> None:
    init_repo_with_readme(tmp_path)
    (tmp_path / "staged.md").write_text("s\n", encoding="utf-8")
    repo = Repo(tmp_path)
    repo.git.add("staged.md")
    status = runner.get_status(repo, markdown_only=False)
    assert "staged.md" in status["added"]
