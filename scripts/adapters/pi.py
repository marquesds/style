"""Pi (pi.dev) adapter.

Same merged AGENTS.md layout as Codex; installs to <root>/AGENTS.md for global user rules.
"""

from __future__ import annotations

from pathlib import Path

from scripts.adapters.base import AdapterReport, WriteOp, apply_op, replace_managed_section
from scripts.adapters.codex import render_merged_agents_block
from scripts.source import Source


class PiAdapter:
    name = "pi"

    def write_all(
        self,
        sources: list[Source],
        target_root: Path,
        dry_run: bool,
    ) -> AdapterReport:
        report = AdapterReport(agent=self.name)
        eligible = [s for s in sources if "pi" in s.agents]
        if not eligible:
            return report

        path = target_root / "AGENTS.md"
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        new_block = render_merged_agents_block(eligible)
        merged = replace_managed_section(existing, new_block)
        report.add(WriteOp(path=path, content=merged))

        if not dry_run:
            for op in report.ops:
                apply_op(op)
        return report
