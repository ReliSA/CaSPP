"""Tests for refactored git operation modules and manager behavior."""

import sys
from pathlib import Path

from git import Repo

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from core.git_manager import GitManager, GitOperationWorker
from utils.git.commit import commit
from utils.git.stage import stage_markdown_files
from utils.git.status import get_status_detailed


def _init_repo(tmp_path: Path) -> Repo:
    repo = Repo.init(tmp_path)
    file_path = tmp_path / "README.md"
    file_path.write_text("initial\n", encoding="utf-8")
    repo.git.add("README.md")
    repo.index.commit("Initial commit")
    return repo


def test_stage_markdown_files_only_stages_markdown(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    (tmp_path / "README.md").write_text("changed\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("text\n", encoding="utf-8")

    result = stage_markdown_files(str(tmp_path))

    assert result.success is True
    staged_files = repo.git.diff("--cached", "--name-only").splitlines()
    assert "README.md" in staged_files
    assert "notes.txt" not in staged_files


def test_commit_stage_all_commits_markdown_changes(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    (tmp_path / "README.md").write_text("new content\n", encoding="utf-8")

    result = commit(str(tmp_path), "Update markdown", stage_all=True)

    assert result.success is True
    assert "hash" in result.payload
    assert repo.head.commit.message.strip() == "Update markdown"


def test_status_detailed_includes_structured_payload(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    (tmp_path / "new_doc.md").write_text("hello\n", encoding="utf-8")

    result = get_status_detailed(str(tmp_path), markdown_only=True)

    assert result.success is True
    assert "status" in result.payload
    assert "untracked" in result.payload["status"]
    assert "new_doc.md" in result.payload["status"]["untracked"]


def test_git_operation_worker_unknown_operation() -> None:
    worker = GitOperationWorker(operation="unknown", repo_path=".")

    result = worker._dispatch()

    assert result.success is False
    assert "Unknown operation" in result.message


def test_git_manager_rejects_when_busy() -> None:
    manager = GitManager(repo_path=".")

    class _BusyWorker:
        def isRunning(self) -> bool:
            return True

    manager._worker = _BusyWorker()
    started = manager.start_operation("status")

    assert started is False
