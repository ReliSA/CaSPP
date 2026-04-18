"""Shared result types for git operations."""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class GitResult:
    """Normalized result for git operations."""

    success: bool
    message: str
    payload: Dict[str, Any] = field(default_factory=dict)
