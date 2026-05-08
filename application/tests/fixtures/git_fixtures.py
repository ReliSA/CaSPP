"""Shared git test helpers (importable from tests and conftest)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from git import Repo  # noqa: E402


def init_repo_with_readme(path: Path) -> Repo:
    """Create a repository with an initial commit on branch main when possible."""
    try:
        repo = Repo.init(path, initial_branch="main")
    except TypeError:
        repo = Repo.init(path)
    readme = path / "README.md"
    readme.write_text("initial\n", encoding="utf-8")
    repo.git.add("README.md")
    repo.index.commit("Initial commit")
    try:
        if repo.active_branch.name != "main":
            repo.git.branch("-M", "main")
    except Exception:
        pass
    return repo


def sync_state_ok(**overrides: Any) -> Dict[str, Any]:
    """Default successful branch sync state for monkeypatching."""
    state: Dict[str, Any] = {
        "ok": True,
        "branch": "main",
        "upstream": "origin/main",
        "ahead": 0,
        "behind": 0,
        "is_up_to_date": True,
    }
    state.update(overrides)
    return state
