"""Per-agent adapters."""

from __future__ import annotations

from scripts.adapters.base import (
    Adapter,
    AdapterReport,
    WriteOp,
    apply_op,
    replace_managed_section,
)
from scripts.adapters.claude import ClaudeAdapter
from scripts.adapters.codex import CodexAdapter
from scripts.adapters.cursor import CursorAdapter
from scripts.adapters.vibe import VibeAdapter

ADAPTERS: dict[str, Adapter] = {
    "claude": ClaudeAdapter(),
    "cursor": CursorAdapter(),
    "codex": CodexAdapter(),
    "vibe": VibeAdapter(),
}

__all__ = [
    "ADAPTERS",
    "Adapter",
    "AdapterReport",
    "WriteOp",
    "apply_op",
    "replace_managed_section",
]
