"""Claude Code adapter.

Layout:
- Skills  -> <root>/.claude/skills/<id>/SKILL.md   (Claude's native skill format).
- Rules   -> managed section in <root>/.claude/CLAUDE.md (rules merged inline).
- Commands -> <root>/.claude/commands/<id>.md      (slash command prompts).
"""

from __future__ import annotations

from pathlib import Path

from scripts.adapters.base import (
    AdapterReport,
    WriteOp,
    apply_op,
    render_command_markdown,
    replace_managed_section,
    skill_bundle_ops,
    strip_managed_section,
    walk_managed_files,
)
from scripts.source import Source


class ClaudeAdapter:
    name = "claude"

    def write_all(
        self,
        sources: list[Source],
        target_root: Path,
        dry_run: bool,
    ) -> AdapterReport:
        report = AdapterReport(agent=self.name)
        root = target_root / ".claude"

        for s in sources:
            if "claude" not in s.agents:
                continue
            if s.kind == "skill":
                for op in self._skill_ops(s, root):
                    report.add(op)
            elif s.kind == "command":
                report.add(self._command_op(s, root))

        rules = [s for s in sources if s.kind == "rule" and "claude" in s.agents]
        if rules:
            report.add(self._claude_md_op(rules, root))

        if not dry_run:
            for op in report.ops:
                apply_op(op)
        return report

    def prune_all(self, target_root: Path, dry_run: bool) -> AdapterReport:
        report = AdapterReport(agent=self.name)
        root = target_root / ".claude"
        claude_md = root / "CLAUDE.md"
        if claude_md.exists():
            existing = claude_md.read_text(encoding="utf-8")
            stripped = strip_managed_section(existing)
            if stripped != existing:
                action = "delete" if not stripped.strip() else "write"
                report.add(WriteOp(path=claude_md, content=stripped, action=action))
        for d in (root / "skills", root / "commands"):
            for p in walk_managed_files(d):
                report.add(WriteOp(path=p, content="", action="delete"))
        if not dry_run:
            for op in report.ops:
                apply_op(op)
        return report

    def _skill_ops(self, src: Source, root: Path) -> list[WriteOp]:
        return skill_bundle_ops(src, root / "skills" / src.id)

    def _command_op(self, src: Source, root: Path) -> WriteOp:
        return WriteOp(
            path=root / "commands" / f"{src.id}.md",
            content=render_command_markdown(src),
        )

    def _claude_md_op(self, rules: list[Source], root: Path) -> WriteOp:
        path = root / "CLAUDE.md"
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        body_parts = [
            "# Style Harness Rules",
            "",
            "Always-on guidance installed by `style-harness`.",
            "",
        ]
        for r in rules:
            body_parts.append(f"## {r.title}")
            body_parts.append("")
            body_parts.append(r.description)
            body_parts.append("")
            body_parts.append(r.body.strip())
            body_parts.append("")
        new_block = "\n".join(body_parts).rstrip() + "\n"
        merged = replace_managed_section(existing, new_block)
        return WriteOp(path=path, content=merged)
