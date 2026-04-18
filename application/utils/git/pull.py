"""Git pull operation."""

from .types import GitResult
from . import runner


def pull(repo_path: str) -> GitResult:
    """Pull from origin for the current branch."""
    try:
        repo = runner.load_repo(repo_path)

        if repo.is_dirty():
            return GitResult(False, "Cannot pull. Please commit or stash your changes first.")

        if "origin" not in [remote.name for remote in repo.remotes]:
            return GitResult(False, "No 'origin' remote found")

        origin = repo.remotes.origin
        current_branch = repo.active_branch
        result = origin.pull(current_branch.name)

        if result:
            return GitResult(True, f"Successfully pulled changes. Updated {len(result)} reference(s).")
        return GitResult(True, "Already up to date.")
    except Exception as exc:
        return GitResult(False, f"Pull failed: {str(exc)}")
