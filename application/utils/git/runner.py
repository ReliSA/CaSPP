"""Shared helpers for git operations."""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from git import Repo as GitRepo
else:
    GitRepo = Any

try:
    import git
    from git import Repo, InvalidGitRepositoryError, GitCommandError

    GIT_AVAILABLE = True
except ImportError:
    git = None
    Repo = None
    InvalidGitRepositoryError = Exception
    GitCommandError = Exception
    GIT_AVAILABLE = False

from core.constants import GitConstants, FileConstants
from utils.exceptions import GitLibraryNotAvailableError, GitRepositoryNotFoundError


def is_git_available() -> bool:
    """Return True if GitPython can be imported."""
    return GIT_AVAILABLE


def ensure_git_available() -> None:
    """Raise if GitPython is not available."""
    if not GIT_AVAILABLE:
        raise GitLibraryNotAvailableError()


def load_repo(repo_path: Optional[str] = None) -> GitRepo:
    """Load and validate a git repository."""
    ensure_git_available()

    try:
        if repo_path:
            path = Path(repo_path)
            if not path.exists():
                raise GitRepositoryNotFoundError(repo_path)
            return Repo(path)

        return Repo(Path.cwd(), search_parent_directories=True)
    except InvalidGitRepositoryError as exc:
        raise GitRepositoryNotFoundError(repo_path) from exc


def find_git_repo(start_path: Optional[str] = None) -> Optional[str]:
    """Find git repository root from a path."""
    if not GIT_AVAILABLE:
        return None

    try:
        search_path = Path(start_path) if start_path else Path.cwd()
        repo = Repo(search_path, search_parent_directories=True)
        return str(repo.working_dir)
    except Exception:
        return None


def is_repo_available(repo_path: Optional[str] = None) -> bool:
    """Return True if repository is present and not bare."""
    try:
        repo = load_repo(repo_path)
        return repo is not None and not repo.bare
    except Exception:
        return False


def is_markdown_file(file_path: str) -> bool:
    """Return True when the path is a markdown file."""
    return file_path.lower().endswith(tuple(FileConstants.MARKDOWN_EXTENSIONS))


def get_current_branch(repo: GitRepo) -> str:
    """Return current branch name or detached indicator."""
    try:
        return str(repo.active_branch)
    except Exception:
        return "detached HEAD"


def has_changes(repo: GitRepo) -> Tuple[bool, bool]:
    """Return tuple of (has_unstaged_changes, has_staged_changes)."""
    try:
        unstaged = len(repo.index.diff(None)) > 0 or len(repo.untracked_files) > 0
    except Exception:
        unstaged = False

    try:
        staged = len(repo.index.diff(GitConstants.DEFAULT_BRANCH_HEAD)) > 0
    except Exception:
        staged = False

    return unstaged, staged


def get_branch_sync_state(
    repo: GitRepo,
    fetch_remote: bool = False,
    remote_name: str = GitConstants.DEFAULT_REMOTE_NAME,
) -> Dict[str, Any]:
    """Return branch sync state against tracking upstream branch."""
    branch = get_current_branch(repo)
    if branch == "detached HEAD":
        return {
            "ok": False,
            "reason": "detached_head",
            "message": "Cannot determine sync status in detached HEAD state.",
            "branch": branch,
            "upstream": None,
            "ahead": 0,
            "behind": 0,
            "is_up_to_date": False,
        }

    try:
        tracking_branch = repo.active_branch.tracking_branch()
    except Exception:
        tracking_branch = None

    if tracking_branch is None:
        return {
            "ok": False,
            "reason": "no_upstream",
            "message": f"Branch '{branch}' has no upstream tracking branch.",
            "branch": branch,
            "upstream": None,
            "ahead": 0,
            "behind": 0,
            "is_up_to_date": False,
        }

    upstream_name = tracking_branch.name

    if fetch_remote:
        try:
            remote_to_fetch = getattr(repo.remotes, tracking_branch.remote_name)
            remote_to_fetch.fetch()
        except Exception as exc:
            return {
                "ok": False,
                "reason": "fetch_failed",
                "message": f"Failed to fetch remote updates: {str(exc)}",
                "branch": branch,
                "upstream": upstream_name,
                "ahead": 0,
                "behind": 0,
                "is_up_to_date": False,
            }

    try:
        behind_str, ahead_str = repo.git.rev_list("--left-right", "--count", f"{upstream_name}...HEAD").split()
        behind = int(behind_str)
        ahead = int(ahead_str)
    except Exception as exc:
        return {
            "ok": False,
            "reason": "sync_check_failed",
            "message": f"Failed to compute branch sync status: {str(exc)}",
            "branch": branch,
            "upstream": upstream_name,
            "ahead": 0,
            "behind": 0,
            "is_up_to_date": False,
        }

    return {
        "ok": True,
        "reason": "ok",
        "message": "Sync status collected",
        "branch": branch,
        "upstream": upstream_name,
        "ahead": ahead,
        "behind": behind,
        "is_up_to_date": behind == 0,
    }


def get_staged_name_status(repo: GitRepo) -> List[Tuple[str, str]]:
    """Return staged files as (status, path) tuples."""
    try:
        output = repo.git.diff("--cached", "--name-status")
    except Exception:
        return []

    result: List[Tuple[str, str]] = []
    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue

        status_code = parts[0].strip()
        status = status_code[0] if status_code else ""

        if status == "R" and len(parts) >= 3:
            result.append((status, parts[2].strip()))
            continue

        path = parts[1].strip()
        result.append((status, path))

    return result


def discard_working_tree_changes(repo: GitRepo, preserve_paths: Optional[List[str]] = None) -> Dict[str, Any]:
    """Discard staged/unstaged tracked changes and remove untracked files."""
    preserve_paths = preserve_paths or []
    repo_root = Path(repo.working_dir).resolve()

    try:
        repo.git.reset("--hard", "HEAD")
    except Exception as exc:
        return {
            "success": False,
            "message": f"Failed to reset tracked changes: {str(exc)}",
        }

    clean_args = ["-fd"]
    for preserve_path in preserve_paths:
        try:
            preserve_rel = Path(preserve_path).resolve().relative_to(repo_root)
            clean_args.extend(["-e", preserve_rel.as_posix()])
        except ValueError:
            continue
        except Exception:
            continue

    try:
        repo.git.clean(*clean_args)
    except Exception as exc:
        return {
            "success": False,
            "message": f"Failed to remove untracked files: {str(exc)}",
        }

    return {
        "success": True,
        "message": "Discarded local tracked and untracked changes.",
    }


def get_status(repo: GitRepo, markdown_only: bool = False) -> Dict[str, List[str]]:
    """Return normalized working tree status."""
    status = {
        "modified": [],
        "added": [],
        "deleted": [],
        "untracked": list(repo.untracked_files),
    }

    if markdown_only:
        status["untracked"] = [p for p in status["untracked"] if is_markdown_file(p)]

    for diff in repo.index.diff(None):
        path = diff.a_path or diff.b_path
        if not path:
            continue
        if markdown_only and not is_markdown_file(path):
            continue

        if diff.change_type == GitConstants.CHANGE_TYPE_MODIFIED:
            status["modified"].append(path)
        elif diff.change_type == GitConstants.CHANGE_TYPE_DELETED:
            status["deleted"].append(path)

    try:
        staged_diffs = repo.index.diff(GitConstants.DEFAULT_BRANCH_HEAD)
    except Exception:
        staged_diffs = []

    for diff in staged_diffs:
        path = diff.a_path or diff.b_path
        if not path:
            continue
        if markdown_only and not is_markdown_file(path):
            continue

        if diff.change_type == GitConstants.CHANGE_TYPE_ADDED:
            status["added"].append(path)
        elif diff.change_type == GitConstants.CHANGE_TYPE_MODIFIED and path not in status["modified"]:
            status["modified"].append(path)
        elif diff.change_type == GitConstants.CHANGE_TYPE_DELETED and path not in status["deleted"]:
            status["deleted"].append(path)

    return status


def normalize_repo_path(repo: GitRepo, file_path: str) -> str:
    """Convert path to repository-relative path."""
    repo_root = Path(repo.working_dir)
    path_obj = Path(file_path)

    if path_obj.is_absolute():
        try:
            return str(path_obj.relative_to(repo_root))
        except ValueError as exc:
            raise ValueError(f"File is not within repository: {file_path}") from exc

    full_path = repo_root / path_obj
    if not full_path.exists() and not full_path.parent.exists():
        raise ValueError(f"File not found: {file_path}")
    return str(path_obj)


def format_status_message(branch: str, status: Dict[str, List[str]], markdown_only: bool = False) -> str:
    """Build human-readable status output."""
    lines = [f"Branch: {branch}", ""]
    has_any_changes = False

    if status["untracked"]:
        lines.append("Untracked files:")
        lines.extend([f"  {path}" for path in status["untracked"]])
        lines.append("")
        has_any_changes = True

    if status["modified"]:
        lines.append("Modified files:")
        lines.extend([f"  {path}" for path in status["modified"]])
        lines.append("")
        has_any_changes = True

    if status["added"]:
        lines.append("Staged files:")
        lines.extend([f"  {path}" for path in status["added"]])
        lines.append("")
        has_any_changes = True

    if status["deleted"]:
        lines.append("Deleted files:")
        lines.extend([f"  {path}" for path in status["deleted"]])
        lines.append("")
        has_any_changes = True

    if not has_any_changes:
        if markdown_only:
            lines.append("No markdown changes (.md/.markdown) in working directory.")
        else:
            lines.append("Working directory clean - no changes to commit.")

    return "\n".join(lines)
