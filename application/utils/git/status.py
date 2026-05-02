"""Git status operations."""

from .types import GitResult
from . import runner


def get_status(repo_path: str, markdown_only: bool = False) -> GitResult:
    """Return structured status payload.

    Args:
        repo_path: The git repository path.
        markdown_only: The markdown only boolean value.

    Returns:
        The git operation result.
    """
    try:
        repo = runner.load_repo(repo_path)
        status_payload = runner.get_status(repo, markdown_only=markdown_only)
        return GitResult(True, "Status collected", payload=status_payload)
    except Exception as exc:
        return GitResult(False, f"Error getting status: {str(exc)}")


def get_status_detailed(repo_path: str, markdown_only: bool = False) -> GitResult:
    """Return formatted status string and structured payload.

    Args:
        repo_path: The git repository path.
        markdown_only: The markdown only boolean value.

    Returns:
        The git operation result.
    """
    try:
        repo = runner.load_repo(repo_path)
        branch = runner.get_current_branch(repo)
        status_payload = runner.get_status(repo, markdown_only=markdown_only)
        message = runner.format_status_message(branch, status_payload, markdown_only=markdown_only)
        payload = {"branch": branch, "status": status_payload}
        return GitResult(True, message, payload=payload)
    except Exception as exc:
        return GitResult(False, f"Error getting status: {str(exc)}")
