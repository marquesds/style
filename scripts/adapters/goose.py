"""Goose (Block / AAIF) adapter.

Global project context lives under ~/.config/goose/. Goose loads AGENTS.md from
that directory by default (with .goosehints). We merge rules/skills/commands into
a single managed AGENTS.md so format matches other markdown-based agents.
"""

from __future__ import annotations

from pathlib import Path

from scripts.adapters.base import AdapterReport, WriteOp, apply_op, replace_managed_section
from scripts.adapters.codex import render_merged_agents_block, prune_merged_agents_md
from scripts.source import Source


class GooseAdapter:
    name = "goose"

    def write_all(
        self,
        sources: list[Source],
        target_root: Path,
        dry_run: bool,
    ) -> AdapterReport:
        report = AdapterReport(agent=self.name)
        eligible = [s for s in sources if "goose" in s.agents]
        if not eligible:
            return report

        path = target_root / ".config" / "goose" / "AGENTS.md"
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        new_block = render_merged_agents_block(eligible)
        merged = replace_managed_section(existing, new_block)
        report.add(WriteOp(path=path, content=merged))

        if not dry_run:
            for op in report.ops:
                apply_op(op)
        return report

    def prune_all(self, target_root: Path, dry_run: bool) -> AdapterReport:
        report = AdapterReport(agent=self.name)
        prune_merged_agents_md(target_root / ".config" / "goose" / "AGENTS.md", report)
        if not dry_run:
            for op in report.ops:
                apply_op(op)
        return report
