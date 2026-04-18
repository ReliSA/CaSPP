"""Git push operations."""

from core.constants import GitConstants

from .types import GitResult
from . import runner


def push(repo_path: str, remote_name: str = GitConstants.DEFAULT_REMOTE_NAME, branch: str = None) -> GitResult:
    """Push local branch to remote."""
    try:
        repo = runner.load_repo(repo_path)
        remote_names = [remote.name for remote in repo.remotes]
        if not remote_names:
            return GitResult(False, "No remotes configured")
        if remote_name not in remote_names:
            return GitResult(False, f"Remote '{remote_name}' not found")

        remote = getattr(repo.remotes, remote_name)
        push_branch = branch
        if push_branch is None:
            try:
                push_branch = repo.active_branch.name
            except Exception:
                return GitResult(False, "Cannot determine current branch (detached HEAD). Specify branch explicitly.")

        remote.push(push_branch)
        return GitResult(True, f"Successfully pushed {push_branch} to {remote_name}")
    except Exception as exc:
        return GitResult(False, f"Push failed: {str(exc)}")


def push_markdown_changes(
    repo_path: str,
    commit_message: str = None,
    remote_name: str = None,
    branch: str = None,
) -> GitResult:
    """Stage markdown files, commit them, then push."""
    try:
        repo = runner.load_repo(repo_path)
        message = (commit_message or GitConstants.DEFAULT_COMMIT_MESSAGE).strip() or GitConstants.DEFAULT_COMMIT_MESSAGE
        resolved_remote = remote_name or GitConstants.DEFAULT_REMOTE_NAME

        markdown_status = runner.get_status(repo, markdown_only=True)
        markdown_paths = sorted(
            set(
                markdown_status["modified"]
                + markdown_status["added"]
                + markdown_status["deleted"]
                + markdown_status["untracked"]
            )
        )

        result_lines = []
        if markdown_paths:
            repo.git.add(*markdown_paths)
            result_lines.append(f"Staged {len(markdown_paths)} markdown file(s): {', '.join(markdown_paths)}")
            try:
                repo.git.commit("-m", message, "--", *markdown_paths)
                result_lines.append(f"Committed markdown changes with message: {message}")
            except Exception as exc:
                if "nothing to commit" in str(exc).lower():
                    result_lines.append("No markdown commit created (nothing to commit).")
                else:
                    return GitResult(False, f"Commit failed: {str(exc)}")

        push_result = push(repo_path, remote_name=resolved_remote, branch=branch)
        if not push_result.success:
            message_lines = result_lines + [push_result.message]
            return GitResult(False, "\n".join(message_lines))

        final_message = "\n".join(result_lines + [push_result.message]) if result_lines else push_result.message
        return GitResult(True, final_message)
    except Exception as exc:
        return GitResult(False, f"Push failed: {str(exc)}")
