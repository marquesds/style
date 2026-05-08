"""Adapter primitives: write operations + managed-section helper.

Pure functions for content transformation; only `apply_op` performs I/O.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from scripts.source import Source

MARKER_ID = "style-harness"
BEGIN_MARKER = f"<!-- BEGIN {MARKER_ID} -->"
END_MARKER = f"<!-- END {MARKER_ID} -->"
FILE_MARKER_HTML = f"<!-- {MARKER_ID}:managed -->"


@dataclass(frozen=True)
class WriteOp:
    """A single filesystem operation."""

    path: Path
    content: str
    action: str = "write"

    def describe(self) -> str:
        return f"{self.action} {self.path}"


@dataclass
class AdapterReport:
    """What an adapter did (or would do, in dry-run)."""

    agent: str
    ops: list[WriteOp] = field(default_factory=list)

    def add(self, op: WriteOp) -> None:
        self.ops.append(op)

    def print(self, prefix: str = "") -> None:
        if not self.ops:
            print(f"{prefix}{self.agent}: no changes.")
            return
        print(f"{prefix}{self.agent}: {len(self.ops)} op(s).")
        for op in self.ops:
            print(f"{prefix}  {op.describe()}")


class Adapter(Protocol):
    name: str

    def write_all(
        self,
        sources: list[Source],
        target_root: Path,
        dry_run: bool,
    ) -> AdapterReport: ...


def apply_op(op: WriteOp) -> None:
    """Perform a write operation."""
    op.path.parent.mkdir(parents=True, exist_ok=True)
    op.path.write_text(op.content, encoding="utf-8")


def replace_managed_section(existing: str, new_block: str) -> str:
    """Replace content between BEGIN/END markers, or append a new managed block."""
    block = f"{BEGIN_MARKER}\n{new_block.rstrip()}\n{END_MARKER}\n"
    if BEGIN_MARKER in existing and END_MARKER in existing:
        before = existing.split(BEGIN_MARKER, 1)[0]
        after = existing.split(END_MARKER, 1)[1]
        return before.rstrip("\n") + "\n\n" + block + after.lstrip("\n")
    sep = "\n\n" if existing.strip() else ""
    return existing + sep + block
