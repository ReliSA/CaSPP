"""Git fetch operation."""

from .types import GitResult
from . import runner


def fetch(repo_path: str) -> GitResult:
    """Fetch from all configured remotes."""
    try:
        repo = runner.load_repo(repo_path)
        if not repo.remotes:
            return GitResult(False, "No remotes configured")

        for remote in repo.remotes:
            remote.fetch()

        return GitResult(True, "Successfully fetched changes from remote(s)")
    except Exception as exc:
        return GitResult(False, f"Fetch failed: {str(exc)}")
