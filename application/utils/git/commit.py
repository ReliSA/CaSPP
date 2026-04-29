"""Git commit operation."""

from core.constants import GitConstants

from .types import GitResult
from . import runner
from .stage import stage_markdown_files


def commit(repo_path: str, message: str, stage_all: bool = False) -> GitResult:
    """Create commit for staged changes.

    Args:
        repo_path: The git repository path.
        message: The message to display or use for the operation.
        stage_all: Whether to stage all changes before committing.

    Returns:
        The git operation result.
    """
    try:
        normalized_message = (message or "").strip()
        if not normalized_message:
            return GitResult(False, "Invalid commit message: cannot be empty")
        if len(normalized_message) > GitConstants.MAX_COMMIT_MESSAGE_LENGTH:
            return GitResult(
                False,
                f"Invalid commit message: too long (max {GitConstants.MAX_COMMIT_MESSAGE_LENGTH} characters)",
            )

        if stage_all:
            stage_result = stage_markdown_files(repo_path)
            if not stage_result.success:
                return stage_result

        repo = runner.load_repo(repo_path)
        has_unstaged, has_staged = runner.has_changes(repo)
        if not has_staged:
            if has_unstaged:
                return GitResult(False, "No staged changes to commit. Stage files first.")
            return GitResult(False, "No changes to commit - working directory is clean.")

        commit_obj = repo.index.commit(normalized_message)
        short_hash = commit_obj.hexsha[:GitConstants.COMMIT_HASH_DISPLAY_LENGTH]
        return GitResult(True, f"Successfully committed changes: {short_hash}", payload={"hash": short_hash})
    except Exception as exc:
        return GitResult(False, f"Git commit failed: {str(exc)}")
