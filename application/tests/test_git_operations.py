"""Tests for refactored git operation modules and manager behavior."""

import sys
import importlib
from zipfile import ZipFile
from pathlib import Path

from git import Repo

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from core.git_manager import GitManager, GitOperationWorker
from core.constants import GitConstants
from utils.git.commit import commit
from utils.git.stage import stage_markdown_files
from utils.git.status import get_status_detailed
from utils.git.types import GitResult

push_module = importlib.import_module("utils.git.push")
pull_module = importlib.import_module("utils.git.pull")
export_module = importlib.import_module("utils.git.export")


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


def test_push_markdown_changes_uses_custom_commit_message(tmp_path: Path, monkeypatch) -> None:
    repo = _init_repo(tmp_path)
    (tmp_path / "README.md").write_text("changed\n", encoding="utf-8")

    monkeypatch.setattr(
        push_module.runner,
        "get_branch_sync_state",
        lambda _repo, fetch_remote=True, remote_name=GitConstants.DEFAULT_REMOTE_NAME: {
            "ok": True,
            "branch": "main",
            "upstream": "origin/main",
            "ahead": 0,
            "behind": 0,
            "is_up_to_date": True,
        },
    )

    monkeypatch.setattr(
        push_module,
        "push",
        lambda repo_path, remote_name=GitConstants.DEFAULT_REMOTE_NAME, branch=None: GitResult(True, "push ok"),
    )

    result = push_module.push_markdown_changes(str(tmp_path), commit_message="My custom push message")

    assert result.success is True
    assert repo.head.commit.message.strip() == "My custom push message"


def test_push_markdown_changes_uses_default_message_when_empty(tmp_path: Path, monkeypatch) -> None:
    repo = _init_repo(tmp_path)
    (tmp_path / "README.md").write_text("changed again\n", encoding="utf-8")

    monkeypatch.setattr(
        push_module.runner,
        "get_branch_sync_state",
        lambda _repo, fetch_remote=True, remote_name=GitConstants.DEFAULT_REMOTE_NAME: {
            "ok": True,
            "branch": "main",
            "upstream": "origin/main",
            "ahead": 0,
            "behind": 0,
            "is_up_to_date": True,
        },
    )

    monkeypatch.setattr(
        push_module,
        "push",
        lambda repo_path, remote_name=GitConstants.DEFAULT_REMOTE_NAME, branch=None: GitResult(True, "push ok"),
    )

    result = push_module.push_markdown_changes(str(tmp_path), commit_message="")

    assert result.success is True
    assert repo.head.commit.message.strip() == GitConstants.DEFAULT_COMMIT_MESSAGE


def test_push_markdown_changes_blocks_when_branch_is_behind(tmp_path: Path, monkeypatch) -> None:
    repo = _init_repo(tmp_path)
    (tmp_path / "README.md").write_text("local change\n", encoding="utf-8")

    initial_head = repo.head.commit.hexsha
    push_called = {"value": False}

    monkeypatch.setattr(
        push_module.runner,
        "get_branch_sync_state",
        lambda _repo, fetch_remote=True, remote_name=GitConstants.DEFAULT_REMOTE_NAME: {
            "ok": True,
            "branch": "main",
            "upstream": "origin/main",
            "ahead": 0,
            "behind": 1,
            "is_up_to_date": False,
        },
    )

    def _fake_push(repo_path, remote_name=GitConstants.DEFAULT_REMOTE_NAME, branch=None):
        push_called["value"] = True
        return GitResult(True, "push ok")

    monkeypatch.setattr(push_module, "push", _fake_push)

    result = push_module.push_markdown_changes(str(tmp_path), commit_message="Should not commit")

    assert result.success is False
    assert "behind" in result.message.lower()
    assert repo.head.commit.hexsha == initial_head
    assert push_called["value"] is False


def test_pull_blocks_when_behind_with_staged_changes(tmp_path: Path, monkeypatch) -> None:
    _init_repo(tmp_path)
    (tmp_path / "README.md").write_text("staged local change\n", encoding="utf-8")

    repo = Repo(tmp_path)
    repo.git.add("README.md")

    monkeypatch.setattr(
        pull_module.runner,
        "get_branch_sync_state",
        lambda _repo, fetch_remote=True, remote_name=GitConstants.DEFAULT_REMOTE_NAME: {
            "ok": True,
            "branch": "main",
            "upstream": "origin/main",
            "ahead": 0,
            "behind": 2,
            "is_up_to_date": False,
        },
    )

    result = pull_module.pull(str(tmp_path))

    assert result.success is False
    assert "export staged" in result.message.lower()


def test_export_staged_files_zip_creates_archive_with_staged_files(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    (tmp_path / "README.md").write_text("zip me\n", encoding="utf-8")

    repo = Repo(tmp_path)
    repo.git.add("README.md")

    result = export_module.export_staged_files_zip(str(tmp_path))

    assert result.success is True
    zip_path = Path(result.payload["zip_path"])
    assert zip_path.exists()

    with ZipFile(zip_path, "r") as archive:
        names = archive.namelist()
        assert "README.md" in names
