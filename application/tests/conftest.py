"""Pytest plugins and fixtures for application tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parent
APP_DIR = TESTS_DIR.parent

for directory in (str(APP_DIR), str(TESTS_DIR)):
    if directory not in sys.path:
        sys.path.insert(0, directory)

from git import Repo  # noqa: E402

from git_fixtures import init_repo_with_readme  # noqa: E402


@pytest.fixture
def git_repo(tmp_path: Path) -> Repo:
    """Fresh git repository with README and initial commit on main."""
    return init_repo_with_readme(tmp_path)
