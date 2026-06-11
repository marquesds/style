"""Codex adapter.

Layout:
- Rules/commands are collapsed into one managed section in <root>/.codex/AGENTS.md.
- Skills are written as native Codex skills in <root>/.agents/skills/<id>/SKILL.md.

Legacy cleanup: if <root>/AGENTS.md contains the managed block (from a prior install),
the block is stripped on the next write_all or prune_all run.
"""

from __future__ import annotations

from pathlib import Path

from scripts.adapters.base import (
    AdapterReport,
    WriteOp,
    apply_op,
    replace_managed_section,
    skill_bundle_ops,
    strip_managed_section,
    walk_managed_files,
)
from scripts.source import Source

SECTIONS = (("rule", "Rules"), ("skill", "Skills"), ("command", "Commands"))
CODEX_AGENTS_SECTIONS = (("rule", "Rules"), ("command", "Commands"))
AUX_NOT_INSTALLED_NOTE = "_Reference files are not installed for this agent; use the index above._"


def _merged_entry(s: Source) -> list[str]:
    parts = [f"### {s.title}", "", s.description, "", s.body.strip(), ""]
    if s.auxiliary:
        parts.extend([AUX_NOT_INSTALLED_NOTE, ""])
    return parts


def render_merged_agents_block(
    sources: list[Source],
    sections: tuple[tuple[str, str], ...] = SECTIONS,
) -> str:
    """Single markdown block for AGENTS.md managed section (Codex, OpenClaw, Pi)."""
    parts = ["# Style Harness", "", "Installed by `style-harness`.", ""]
    for kind, label in sections:
        items = [s for s in sources if s.kind == kind]
        if not items:
            continue
        parts.extend([f"## {label}", ""])
        for s in items:
            parts.extend(_merged_entry(s))
    return "\n".join(parts).rstrip() + "\n"


def prune_merged_agents_md(path: Path, report: AdapterReport) -> None:
    """Strip the harness managed section from a merged AGENTS.md."""
    if not path.exists():
        return
    existing = path.read_text(encoding="utf-8")
    stripped = strip_managed_section(existing)
    if stripped == existing:
        return
    action = "delete" if not stripped.strip() else "write"
    report.add(WriteOp(path=path, content=stripped, action=action))


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

        for skill in [s for s in eligible if s.kind == "skill"]:
            for op in self._skill_ops(skill, target_root):
                report.add(op)

        path = target_root / ".codex" / "AGENTS.md"
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        agents_sources = [s for s in eligible if s.kind != "skill"]
        new_block = render_merged_agents_block(agents_sources, CODEX_AGENTS_SECTIONS)
        merged = replace_managed_section(existing, new_block)
        report.add(WriteOp(path=path, content=merged))

        prune_merged_agents_md(target_root / "AGENTS.md", report)

        if not dry_run:
            for op in report.ops:
                apply_op(op)
        return report

    def _skill_ops(self, src: Source, target_root: Path) -> list[WriteOp]:
        return skill_bundle_ops(src, target_root / ".agents" / "skills" / src.id)

    def prune_all(self, target_root: Path, dry_run: bool) -> AdapterReport:
        report = AdapterReport(agent=self.name)
        prune_merged_agents_md(target_root / ".codex" / "AGENTS.md", report)
        prune_merged_agents_md(target_root / "AGENTS.md", report)
        for path in walk_managed_files(target_root / ".agents" / "skills"):
            report.add(WriteOp(path=path, content="", action="delete"))
        if not dry_run:
            for op in report.ops:
                apply_op(op)
        return report
