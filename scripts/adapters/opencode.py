"""OpenCode adapter.

Layout:
- Skills  -> <root>/.config/opencode/skills/<id>/SKILL.md
- Rules   -> managed section in <root>/.config/opencode/AGENTS.md
- Commands -> <root>/.config/opencode/commands/<id>.md (YAML description + template body)
"""

from __future__ import annotations

from pathlib import Path

from scripts.adapters.base import (
    FILE_MARKER_HTML,
    AdapterReport,
    WriteOp,
    apply_op,
    replace_managed_section,
    strip_managed_section,
    walk_managed_files,
)
from scripts.source import Source


class OpenCodeAdapter:
    name = "opencode"

    def write_all(
        self,
        sources: list[Source],
        target_root: Path,
        dry_run: bool,
    ) -> AdapterReport:
        report = AdapterReport(agent=self.name)
        root = target_root / ".config" / "opencode"

        for s in sources:
            if "opencode" not in s.agents:
                continue
            if s.kind == "skill":
                op = self._skill_op(s, root)
            elif s.kind == "command":
                op = self._command_op(s, root)
            elif s.kind == "rule":
                continue
            else:
                continue
            report.add(op)

        rules = [s for s in sources if s.kind == "rule" and "opencode" in s.agents]
        if rules:
            report.add(self._agents_md_op(rules, root))

        if not dry_run:
            for op in report.ops:
                apply_op(op)
        return report

    def prune_all(self, target_root: Path, dry_run: bool) -> AdapterReport:
        report = AdapterReport(agent=self.name)
        root = target_root / ".config" / "opencode"
        agents_md = root / "AGENTS.md"
        if agents_md.exists():
            existing = agents_md.read_text(encoding="utf-8")
            stripped = strip_managed_section(existing)
            if stripped != existing:
                action = "delete" if not stripped.strip() else "write"
                report.add(WriteOp(path=agents_md, content=stripped, action=action))
        for d in (root / "skills", root / "commands"):
            for p in walk_managed_files(d):
                report.add(WriteOp(path=p, content="", action="delete"))
        if not dry_run:
            for op in report.ops:
                apply_op(op)
        return report

    def _skill_op(self, src: Source, root: Path) -> WriteOp:
        path = root / "skills" / src.id / "SKILL.md"
        content = (
            "---\n"
            f"name: {src.id}\n"
            f"description: >\n  {src.description.replace(chr(10), chr(10) + '  ')}\n"
            "---\n\n"
            f"{FILE_MARKER_HTML}\n"
            f"{src.body.lstrip()}"
        )
        return WriteOp(path=path, content=content)

    def _command_op(self, src: Source, root: Path) -> WriteOp:
        path = root / "commands" / f"{src.id}.md"
        desc_folded = src.description.replace(chr(10), chr(10) + "  ")
        content = (
            "---\n"
            f"description: >\n  {desc_folded}\n"
            "---\n\n"
            f"{FILE_MARKER_HTML}\n\n"
            f"# /{src.id}\n\n"
            f"{src.body.lstrip()}"
        )
        return WriteOp(path=path, content=content)

    def _agents_md_op(self, rules: list[Source], root: Path) -> WriteOp:
        path = root / "AGENTS.md"
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
