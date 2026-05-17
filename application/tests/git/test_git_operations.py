"""Tests for refactored git operation modules and manager behavior."""

import importlib
from zipfile import ZipFile
from pathlib import Path

import pytest
from git import Repo

import core.managers.git_manager as gm
from core.managers.git_manager import GitManager, GitOperationWorker
from fixtures.git_fixtures import init_repo_with_readme, sync_state_ok
from utils.constants import GitConstants
from utils.git.commit import commit
from utils.git.fetch import fetch
from utils.git.stage import stage_file, stage_markdown_files, unstage_all
from utils.git.status import get_status_detailed
from utils.git.types import GitResult

push_module = importlib.import_module("utils.git.push")
pull_module = importlib.import_module("utils.git.pull")
export_module = importlib.import_module("utils.git.export")


def test_stage_markdown_files_only_stages_markdown(tmp_path: Path) -> None:
    repo = init_repo_with_readme(tmp_path)
    (tmp_path / "README.md").write_text("changed\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("text\n", encoding="utf-8")

    result = stage_markdown_files(str(tmp_path))

    assert result.success is True
    staged_files = repo.git.diff("--cached", "--name-only").splitlines()
    assert "README.md" in staged_files
    assert "notes.txt" not in staged_files


def test_stage_markdown_files_with_explicit_paths_filters_non_markdown(tmp_path: Path) -> None:
    init_repo_with_readme(tmp_path)
    (tmp_path / "a.md").write_text("a\n", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b\n", encoding="utf-8")
    result = stage_markdown_files(str(tmp_path), file_paths=["a.md", "b.txt", "nope.md"])
    assert result.success is True
    repo = Repo(tmp_path)
    staged = repo.git.diff("--cached", "--name-only").splitlines()
    assert "a.md" in staged
    assert "b.txt" not in staged


def test_stage_markdown_files_partial_failure_one_invalid(tmp_path: Path) -> None:
    init_repo_with_readme(tmp_path)
    (tmp_path / "good.md").write_text("g\n", encoding="utf-8")
    outside = tmp_path.parent / "outside_markdown_test.md"
    outside.write_text("o\n", encoding="utf-8")

    result = stage_markdown_files(
        str(tmp_path),
        file_paths=["good.md", str(outside.resolve())],
    )
    assert result.success is True
    assert "good.md" in result.message
    assert "Failed" in result.message or "outside" in result.message
    repo = Repo(tmp_path)
    staged = repo.git.diff("--cached", "--name-only").splitlines()
    assert "good.md" in staged


def test_stage_file_success_and_payload(tmp_path: Path) -> None:
    init_repo_with_readme(tmp_path)
    (tmp_path / "README.md").write_text("edited\n", encoding="utf-8")
    result = stage_file(str(tmp_path), "README.md")
    assert result.success is True
    assert result.payload["path"] == "README.md"


def test_stage_file_rejects_path_outside_repo(tmp_path: Path) -> None:
    init_repo_with_readme(tmp_path)
    outside = tmp_path.parent / "ext.md"
    outside.write_text("x\n", encoding="utf-8")
    result = stage_file(str(tmp_path), str(outside.resolve()))
    assert result.success is False
    assert "repository" in result.message.lower() or "within" in result.message.lower()


def test_unstage_all_leaves_working_tree_changes(tmp_path: Path) -> None:
    init_repo_with_readme(tmp_path)
    (tmp_path / "README.md").write_text("new\n", encoding="utf-8")
    repo = Repo(tmp_path)
    repo.git.add("README.md")
    assert len(repo.index.diff("HEAD")) > 0

    unstage_result = unstage_all(str(tmp_path))
    assert unstage_result.success is True

    assert len(repo.index.diff("HEAD")) == 0
    assert len(repo.index.diff(None)) > 0 or repo.is_dirty()


def test_commit_rejects_empty_message(tmp_path: Path) -> None:
    init_repo_with_readme(tmp_path)
    r = commit(str(tmp_path), "   ", stage_all=False)
    assert r.success is False
    assert "empty" in r.message.lower() or "invalid" in r.message.lower()


def test_commit_rejects_message_too_long(tmp_path: Path) -> None:
    init_repo_with_readme(tmp_path)
    long_msg = "x" * (GitConstants.MAX_COMMIT_MESSAGE_LENGTH + 1)
    r = commit(str(tmp_path), long_msg, stage_all=False)
    assert r.success is False
    assert "long" in r.message.lower() or "too long" in r.message.lower()


def test_push_markdown_changes_rejects_message_too_long(tmp_path: Path) -> None:
    init_repo_with_readme(tmp_path)
    (tmp_path / "README.md").write_text("changed\n", encoding="utf-8")
    long_msg = "x" * (GitConstants.MAX_COMMIT_MESSAGE_LENGTH + 1)
    result = push_module.push_markdown_changes(str(tmp_path), commit_message=long_msg)
    assert result.success is False
    assert "too long" in result.message.lower()


def test_commit_without_staged_changes_reports_stage_first(tmp_path: Path) -> None:
    init_repo_with_readme(tmp_path)
    (tmp_path / "README.md").write_text("dirty\n", encoding="utf-8")
    r = commit(str(tmp_path), "msg", stage_all=False)
    assert r.success is False
    assert "staged" in r.message.lower()


def test_commit_stage_all_commits_markdown_changes(tmp_path: Path) -> None:
    repo = init_repo_with_readme(tmp_path)
    (tmp_path / "README.md").write_text("new content\n", encoding="utf-8")

    result = commit(str(tmp_path), "Update markdown", stage_all=True)

    assert result.success is True
    assert "hash" in result.payload
    assert repo.head.commit.message.strip() == "Update markdown"


def test_status_detailed_includes_structured_payload(tmp_path: Path) -> None:
    init_repo_with_readme(tmp_path)
    (tmp_path / "new_doc.md").write_text("hello\n", encoding="utf-8")

    result = get_status_detailed(str(tmp_path), markdown_only=True)

    assert result.success is True
    assert "status" in result.payload
    assert "untracked" in result.payload["status"]
    assert "new_doc.md" in result.payload["status"]["untracked"]


def test_fetch_fails_without_remotes(tmp_path: Path) -> None:
    init_repo_with_readme(tmp_path)
    result = fetch(str(tmp_path))
    assert result.success is False
    assert "remote" in result.message.lower()


def test_pull_blocked_when_sync_state_not_ok(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    init_repo_with_readme(tmp_path)

    def _bad_sync(_repo, fetch_remote=True, remote_name=GitConstants.DEFAULT_REMOTE_NAME):
        return {"ok": False, "message": "no upstream"}

    monkeypatch.setattr(pull_module.runner, "get_branch_sync_state", _bad_sync)
    result = pull_module.pull(str(tmp_path))
    assert result.success is False
    assert "Pull blocked" in result.message


def test_pull_blocked_when_behind_with_unstaged_changes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    init_repo_with_readme(tmp_path)
    (tmp_path / "README.md").write_text("unstaged edit\n", encoding="utf-8")

    monkeypatch.setattr(
        pull_module.runner,
        "get_branch_sync_state",
        lambda _repo, fetch_remote=True, remote_name=GitConstants.DEFAULT_REMOTE_NAME: {
            **sync_state_ok(behind=2, is_up_to_date=False),
        },
    )

    result = pull_module.pull(str(tmp_path))
    assert result.success is False
    assert "stash" in result.message.lower() or "commit" in result.message.lower()


def test_push_fails_without_remotes(tmp_path: Path) -> None:
    init_repo_with_readme(tmp_path)
    result = push_module.push(str(tmp_path))
    assert result.success is False
    assert "remote" in result.message.lower()


def test_push_markdown_changes_fails_push_when_no_remote_even_if_no_markdown(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    init_repo_with_readme(tmp_path)

    monkeypatch.setattr(
        push_module.runner,
        "get_branch_sync_state",
        lambda _repo, fetch_remote=True, remote_name=GitConstants.DEFAULT_REMOTE_NAME: sync_state_ok(),
    )

    result = push_module.push_markdown_changes(str(tmp_path), commit_message="nothing to do")
    assert result.success is False
    assert "remote" in result.message.lower()


def test_export_staged_files_zip_fails_when_nothing_staged(tmp_path: Path) -> None:
    init_repo_with_readme(tmp_path)
    result = export_module.export_staged_files_zip(str(tmp_path))
    assert result.success is False
    assert "No staged" in result.message


def test_export_staged_files_zip_custom_output_path(tmp_path: Path) -> None:
    init_repo_with_readme(tmp_path)
    (tmp_path / "README.md").write_text("zip custom\n", encoding="utf-8")
    repo = Repo(tmp_path)
    repo.git.add("README.md")
    zip_target = tmp_path / "my_export.zip"

    result = export_module.export_staged_files_zip(str(tmp_path), output_zip_path=str(zip_target))

    assert result.success is True
    assert Path(result.payload["zip_path"]) == zip_target.resolve()
    assert zip_target.exists()
    with ZipFile(zip_target, "r") as archive:
        assert "README.md" in archive.namelist()


def test_git_operation_worker_unknown_operation() -> None:
    worker = GitOperationWorker(operation="unknown", repo_path=".")

    result = worker._dispatch()

    assert result.success is False
    assert "Unknown operation" in result.message


@pytest.mark.parametrize(
    ("operation", "kwargs", "patch_attr"),
    [
        (GitConstants.GIT_OPERATION_STATUS, {}, "get_status_detailed"),
        (GitConstants.GIT_OPERATION_FETCH, {}, "fetch_operation"),
        (GitConstants.GIT_OPERATION_PULL, {}, "pull_operation"),
        (GitConstants.GIT_OPERATION_PUSH, {"message": "msg"}, "push_markdown_changes"),
        (GitConstants.GIT_OPERATION_STAGE_FILE, {"file_path": "README.md"}, "stage_file_operation"),
        (GitConstants.GIT_OPERATION_STAGE_MARKDOWN, {"file_paths": None}, "stage_markdown_files_operation"),
        (GitConstants.GIT_OPERATION_UNSTAGE_ALL, {}, "unstage_all_operation"),
        (GitConstants.GIT_OPERATION_COMMIT, {"message": "x", "stage_all": False}, "commit_operation"),
        (GitConstants.GIT_OPERATION_EXPORT_STAGED, {"output_zip_path": None}, "export_staged_files_zip_operation"),
    ],
)
def test_git_operation_worker_dispatch_wires_known_operations(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    operation: str,
    kwargs: dict,
    patch_attr: str,
) -> None:
    sentinel = GitResult(True, f"wired:{operation}")

    def _capture(*_a, **_k):
        return sentinel

    monkeypatch.setattr(gm, patch_attr, _capture)
    worker = GitOperationWorker(operation=operation, repo_path=str(tmp_path), **kwargs)
    result = worker._dispatch()
    assert result.success is True
    assert result.message == f"wired:{operation}"


def test_git_manager_rejects_when_busy() -> None:
    manager = GitManager(repo_path=".")

    class _BusyWorker:
        def isRunning(self) -> bool:
            return True

    manager._worker = _BusyWorker()  # type: ignore[assignment]
    started = manager.start_operation(GitConstants.GIT_OPERATION_STATUS)

    assert started is False


def test_git_manager_export_staged_calls_start_when_user_confirms(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, dict]] = []

    def fake_ask(_cls, _title: str, _message: str) -> bool:
        return True

    monkeypatch.setattr(gm.ErrorManager, "ask_yes_no", classmethod(fake_ask))

    manager = GitManager(repo_path=str(tmp_path))

    def fake_start(operation: str, **kw: object) -> bool:
        calls.append((operation, kw))
        return True

    monkeypatch.setattr(manager, "start_operation", fake_start)
    assert manager.export_staged() is True
    assert calls[0][0] == GitConstants.GIT_OPERATION_EXPORT_STAGED
    assert calls[0][1] == {}


def test_git_manager_export_staged_skips_when_user_declines(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_ask(_cls, _title: str, _message: str) -> bool:
        return False

    monkeypatch.setattr(gm.ErrorManager, "ask_yes_no", classmethod(fake_ask))
    manager = GitManager(repo_path=str(tmp_path))
    started: list[bool] = []

    def capture_start(*_a, **_k):
        started.append(True)
        return True

    monkeypatch.setattr(manager, "start_operation", capture_start)
    assert manager.export_staged() is False
    assert started == []


def test_push_markdown_changes_uses_custom_commit_message(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = init_repo_with_readme(tmp_path)
    (tmp_path / "README.md").write_text("changed\n", encoding="utf-8")

    monkeypatch.setattr(
        push_module.runner,
        "get_branch_sync_state",
        lambda _repo, fetch_remote=True, remote_name=GitConstants.DEFAULT_REMOTE_NAME: sync_state_ok(),
    )

    monkeypatch.setattr(
        push_module,
        "push",
        lambda repo_path, remote_name=GitConstants.DEFAULT_REMOTE_NAME, branch=None: GitResult(True, "push ok"),
    )

    result = push_module.push_markdown_changes(str(tmp_path), commit_message="My custom push message")

    assert result.success is True
    assert repo.head.commit.message.strip() == "My custom push message"


def test_push_markdown_changes_uses_default_message_when_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = init_repo_with_readme(tmp_path)
    (tmp_path / "README.md").write_text("changed again\n", encoding="utf-8")

    monkeypatch.setattr(
        push_module.runner,
        "get_branch_sync_state",
        lambda _repo, fetch_remote=True, remote_name=GitConstants.DEFAULT_REMOTE_NAME: sync_state_ok(),
    )

    monkeypatch.setattr(
        push_module,
        "push",
        lambda repo_path, remote_name=GitConstants.DEFAULT_REMOTE_NAME, branch=None: GitResult(True, "push ok"),
    )

    result = push_module.push_markdown_changes(str(tmp_path), commit_message="")

    assert result.success is True
    assert repo.head.commit.message.strip() == GitConstants.DEFAULT_COMMIT_MESSAGE


def test_push_markdown_changes_blocks_when_branch_is_behind(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = init_repo_with_readme(tmp_path)
    (tmp_path / "README.md").write_text("local change\n", encoding="utf-8")

    initial_head = repo.head.commit.hexsha
    push_called = {"value": False}

    monkeypatch.setattr(
        push_module.runner,
        "get_branch_sync_state",
        lambda _repo, fetch_remote=True, remote_name=GitConstants.DEFAULT_REMOTE_NAME: {
            **sync_state_ok(behind=1, is_up_to_date=False),
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


def test_pull_blocks_when_behind_with_staged_changes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    init_repo_with_readme(tmp_path)
    (tmp_path / "README.md").write_text("staged local change\n", encoding="utf-8")

    repo = Repo(tmp_path)
    repo.git.add("README.md")

    monkeypatch.setattr(
        pull_module.runner,
        "get_branch_sync_state",
        lambda _repo, fetch_remote=True, remote_name=GitConstants.DEFAULT_REMOTE_NAME: {
            **sync_state_ok(behind=2, is_up_to_date=False),
        },
    )

    result = pull_module.pull(str(tmp_path))

    assert result.success is False
    assert "export staged" in result.message.lower()


def test_export_staged_files_zip_creates_archive_with_staged_files(tmp_path: Path) -> None:
    init_repo_with_readme(tmp_path)
    (tmp_path / "README.md").write_text("zip me\n", encoding="utf-8")
    (tmp_path / "notes.tmp").write_text("temporary\n", encoding="utf-8")

    repo = Repo(tmp_path)
    repo.git.add("README.md")

    result = export_module.export_staged_files_zip(str(tmp_path))

    assert result.success is True
    zip_path = Path(result.payload["zip_path"])
    assert zip_path.exists()
    assert tmp_path not in zip_path.parents

    with ZipFile(zip_path, "r") as archive:
        names = archive.namelist()
        assert "README.md" in names

    assert repo.is_dirty(untracked_files=True) is False
    assert repo.untracked_files == []
