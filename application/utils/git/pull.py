"""Git pull operation."""

from .types import GitResult
from . import runner


def pull(repo_path: str) -> GitResult:
    """Pull from origin for the current branch.

    Args:
        repo_path: The git repository path.

    Returns:
        The git operation result.
    """
    try:
        repo = runner.load_repo(repo_path)

        sync_state = runner.get_branch_sync_state(repo, fetch_remote=True)
        if not sync_state.get("ok"):
            return GitResult(False, f"Pull blocked: {sync_state.get('message', 'Unable to verify branch sync state.')}")

        if sync_state.get("behind", 0) == 0:
            return GitResult(True, "Already up to date.")

        has_unstaged, has_staged = runner.has_changes(repo)
        if has_staged:
            return GitResult(
                False,
                "Cannot pull: your branch is behind and you have staged changes. "
                "Use 'Export Staged' first, then pull, then manually restore your changes.",
            )

        if has_unstaged:
            return GitResult(False, "Cannot pull. Please commit or stash your changes first.")

        tracking_branch = repo.active_branch.tracking_branch()
        remote_name = tracking_branch.remote_name if tracking_branch else "origin"
        if remote_name not in [remote.name for remote in repo.remotes]:
            return GitResult(False, f"No '{remote_name}' remote found")

        origin = getattr(repo.remotes, remote_name)
        current_branch = repo.active_branch
        result = origin.pull(current_branch.name)

        if result:
            return GitResult(True, f"Successfully pulled changes. Updated {len(result)} reference(s).")
        return GitResult(True, "Already up to date.")
    except Exception as exc:
        return GitResult(False, f"Pull failed: {str(exc)}")
