"""Vibe adapter.

Vibe's native format is unsettled across versions; this writes a generic
per-file layout that Vibe can read or that the user can adapt:
- <root>/.vibe/rules/<id>.md
- <root>/.vibe/skills/<id>.md
- <root>/.vibe/commands/<id>.md

Each file carries a `style-harness:managed` marker so re-runs are idempotent.
"""

from __future__ import annotations

from pathlib import Path

from scripts.adapters.base import FILE_MARKER_HTML, AdapterReport, WriteOp, apply_op
from scripts.source import Source

KIND_DIR = {"rule": "rules", "skill": "skills", "command": "commands"}


class VibeAdapter:
    name = "vibe"

    def write_all(
        self,
        sources: list[Source],
        target_root: Path,
        dry_run: bool,
    ) -> AdapterReport:
        report = AdapterReport(agent=self.name)
        root = target_root / ".vibe"

        for s in sources:
            if "vibe" not in s.agents:
                continue
            subdir = KIND_DIR.get(s.kind)
            if subdir is None:
                continue
            path = root / subdir / f"{s.id}.md"
            content = (
                "---\n"
                f"id: {s.id}\n"
                f"kind: {s.kind}\n"
                f"title: {s.title}\n"
                "---\n\n"
                f"{FILE_MARKER_HTML}\n\n"
                f"# {s.title}\n\n"
                f"{s.description}\n\n"
                f"{s.body.strip()}\n"
            )
            report.add(WriteOp(path=path, content=content))

        if not dry_run:
            for op in report.ops:
                apply_op(op)
        return report
