"""Pi (pi.dev) adapter.

Same merged AGENTS.md layout as Codex; installs to <root>/.pi/agent/AGENTS.md
(PI_CODING_AGENT_DIR) for global user rules.

Legacy cleanup: if <root>/AGENTS.md contains the managed block (from a prior install),
the block is stripped on the next write_all or prune_all run.
"""

from __future__ import annotations

from pathlib import Path

from scripts.adapters.base import AdapterReport, WriteOp, apply_op, replace_managed_section
from scripts.adapters.codex import prune_merged_agents_md, render_merged_agents_block
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

        path = target_root / ".pi" / "agent" / "AGENTS.md"
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        new_block = render_merged_agents_block(eligible)
        merged = replace_managed_section(existing, new_block)
        report.add(WriteOp(path=path, content=merged))

        prune_merged_agents_md(target_root / "AGENTS.md", report)

        if not dry_run:
            for op in report.ops:
                apply_op(op)
        return report

    def prune_all(self, target_root: Path, dry_run: bool) -> AdapterReport:
        report = AdapterReport(agent=self.name)
        prune_merged_agents_md(target_root / ".pi" / "agent" / "AGENTS.md", report)
        prune_merged_agents_md(target_root / "AGENTS.md", report)
        if not dry_run:
            for op in report.ops:
                apply_op(op)
        return report
