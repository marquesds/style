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

from scripts.adapters.base import (
    FILE_MARKER_HTML,
    AdapterReport,
    WriteOp,
    apply_op,
    render_aux_markdown,
    stale_managed_delete_ops,
    walk_managed_files,
)
from scripts.source import Source

KIND_DIR = {"rule": "rules", "skill": "skills", "command": "commands"}


def _vibe_markdown(s: Source) -> str:
    return (
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


def _vibe_ops(s: Source, kind_dir: Path) -> list[WriteOp]:
    if not s.is_bundle:
        return [WriteOp(path=kind_dir / f"{s.id}.md", content=_vibe_markdown(s))]
    bundle_dir = kind_dir / s.id
    skill_op = WriteOp(path=bundle_dir / "SKILL.md", content=_vibe_markdown(s))
    aux_ops = [
        WriteOp(path=bundle_dir / a.name, content=render_aux_markdown(a)) for a in s.auxiliary
    ]
    return [skill_op, *aux_ops]


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
            for op in _vibe_ops(s, root / subdir):
                report.add(op)

        keep = [op.path for op in report.ops]
        for subdir in ("rules", "skills", "commands"):
            for op in stale_managed_delete_ops(root / subdir, keep):
                report.add(op)

        if not dry_run:
            for op in report.ops:
                apply_op(op)
        return report

    def prune_all(self, target_root: Path, dry_run: bool) -> AdapterReport:
        report = AdapterReport(agent=self.name)
        root = target_root / ".vibe"
        for subdir in ("rules", "skills", "commands"):
            for p in walk_managed_files(root / subdir):
                report.add(WriteOp(path=p, content="", action="delete"))
        if not dry_run:
            for op in report.ops:
                apply_op(op)
        return report
