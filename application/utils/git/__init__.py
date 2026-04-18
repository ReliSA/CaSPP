"""Git operation package."""

from .types import GitResult
from .runner import is_git_available, is_repo_available, find_git_repo
from .status import get_status, get_status_detailed
from .fetch import fetch
from .pull import pull
from .stage import stage_file, stage_markdown_files, unstage_all
from .commit import commit
from .push import push, push_markdown_changes

__all__ = [
    "GitResult",
    "is_git_available",
    "is_repo_available",
    "find_git_repo",
    "get_status",
    "get_status_detailed",
    "fetch",
    "pull",
    "stage_file",
    "stage_markdown_files",
    "unstage_all",
    "commit",
    "push",
    "push_markdown_changes",
]
