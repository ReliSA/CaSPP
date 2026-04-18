"""Git stage and unstage operations."""

from typing import List, Optional

from .types import GitResult
from . import runner


def stage_file(repo_path: str, file_path: str) -> GitResult:
    """Stage a single file."""
    try:
        repo = runner.load_repo(repo_path)
        relative_path = runner.normalize_repo_path(repo, file_path)
        repo.git.add(relative_path)
        return GitResult(True, f"Successfully staged: {relative_path}", payload={"path": relative_path})
    except ValueError as exc:
        return GitResult(False, str(exc))
    except Exception as exc:
        return GitResult(False, f"Failed to stage file: {str(exc)}")


def stage_markdown_files(repo_path: str, file_paths: Optional[List[str]] = None) -> GitResult:
    """Stage markdown files from provided paths or from current status."""
    try:
        repo = runner.load_repo(repo_path)

        candidate_paths = file_paths
        if candidate_paths is None:
            status_payload = runner.get_status(repo)
            candidate_paths = status_payload["modified"] + status_payload["deleted"] + status_payload["untracked"]

        markdown_paths = sorted({path for path in candidate_paths if runner.is_markdown_file(path)})
        if not markdown_paths:
            return GitResult(True, "No markdown files to stage", payload={"staged": []})

        staged = []
        failed = []

        for path in markdown_paths:
            stage_result = stage_file(repo_path, path)
            if stage_result.success:
                staged.append(path)
            else:
                failed.append(f"{path}: {stage_result.message}")

        messages = []
        if staged:
            messages.append(f"Staged {len(staged)} markdown file(s): {', '.join(staged)}")
        if failed:
            messages.append(f"Failed to stage {len(failed)} file(s): {', '.join(failed)}")

        return GitResult(
            success=len(staged) > 0 or not failed,
            message="; ".join(messages) if messages else "No files staged",
            payload={"staged": staged, "failed": failed},
        )
    except Exception as exc:
        return GitResult(False, f"Error staging markdown files: {str(exc)}")


def unstage_all(repo_path: str) -> GitResult:
    """Unstage all staged changes."""
    try:
        repo = runner.load_repo(repo_path)
        repo.git.reset("HEAD")
        return GitResult(True, "All changes unstaged successfully")
    except Exception as exc:
        return GitResult(False, f"Failed to unstage changes: {str(exc)}")
