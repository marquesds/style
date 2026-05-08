"""Cursor adapter.

Layout:
- Rules + skills -> <root>/.cursor/rules/<id>.mdc with frontmatter.
  - Rules: alwaysApply: true.
  - Skills: alwaysApply: false, description-driven loading.
- Commands -> <root>/.cursor/commands/<id>.md.
"""

from __future__ import annotations

from pathlib import Path

from scripts.adapters.base import FILE_MARKER_HTML, AdapterReport, WriteOp, apply_op
from scripts.source import Source


class CursorAdapter:
    name = "cursor"

    def write_all(
        self,
        sources: list[Source],
        target_root: Path,
        dry_run: bool,
    ) -> AdapterReport:
        report = AdapterReport(agent=self.name)
        root = target_root / ".cursor"

        for s in sources:
            if "cursor" not in s.agents:
                continue
            if s.kind in {"rule", "skill"}:
                report.add(self._mdc_op(s, root))
            elif s.kind == "command":
                report.add(self._command_op(s, root))

        if not dry_run:
            for op in report.ops:
                apply_op(op)
        return report

    def _mdc_op(self, src: Source, root: Path) -> WriteOp:
        path = root / "rules" / f"{src.id}.mdc"
        agent_cfg = src.agents.get("cursor") or {}
        always_apply = agent_cfg.get("always_apply", src.always_apply)
        globs = agent_cfg.get("glob") or src.globs
        fm_lines = ["---", f"description: {src.description.splitlines()[0]}"]
        if globs:
            fm_lines.append(f"globs: {globs}")
        fm_lines.append(f"alwaysApply: {str(bool(always_apply)).lower()}")
        fm_lines.append("---")
        content = "\n".join(fm_lines) + f"\n\n{FILE_MARKER_HTML}\n\n{src.body.lstrip()}"
        return WriteOp(path=path, content=content)

    def _command_op(self, src: Source, root: Path) -> WriteOp:
        path = root / "commands" / f"{src.id}.md"
        content = f"{FILE_MARKER_HTML}\n\n# /{src.id}\n\n{src.body.lstrip()}"
        return WriteOp(path=path, content=content)
