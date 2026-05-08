"""Codex adapter.

Layout:
- All rules/skills/commands collapsed into one managed section in <root>/AGENTS.md.
- Sections: ## Rules, ## Skills, ## Commands, each with ### <Title> subheadings.
"""

from __future__ import annotations

from pathlib import Path

from scripts.adapters.base import AdapterReport, WriteOp, apply_op, replace_managed_section
from scripts.source import Source

SECTIONS = (("rule", "Rules"), ("skill", "Skills"), ("command", "Commands"))


class CodexAdapter:
    name = "codex"

    def write_all(
        self,
        sources: list[Source],
        target_root: Path,
        dry_run: bool,
    ) -> AdapterReport:
        report = AdapterReport(agent=self.name)
        eligible = [s for s in sources if "codex" in s.agents]
        if not eligible:
            return report

        path = target_root / "AGENTS.md"
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        new_block = self._render(eligible)
        merged = replace_managed_section(existing, new_block)
        report.add(WriteOp(path=path, content=merged))

        if not dry_run:
            for op in report.ops:
                apply_op(op)
        return report

    def _render(self, sources: list[Source]) -> str:
        parts = ["# Style Harness", "", "Installed by `style-harness`.", ""]
        for kind, label in SECTIONS:
            items = [s for s in sources if s.kind == kind]
            if not items:
                continue
            parts.append(f"## {label}")
            parts.append("")
            for s in items:
                parts.append(f"### {s.title}")
                parts.append("")
                parts.append(s.description)
                parts.append("")
                parts.append(s.body.strip())
                parts.append("")
        return "\n".join(parts).rstrip() + "\n"
