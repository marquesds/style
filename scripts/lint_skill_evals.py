"""Lint for static skill-routing eval fixtures.

`source/evals/skill-routing.yml` holds offline routing assertions: each case
declares a prompt and which skills should/should not load. We validate the
file references known skill ids only; we do not run the LLM.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import yaml

from scripts.source import Source


def lint_skill_routing_evals(source_dir: Path, sources: Iterable[Source]) -> list[str]:
    path = source_dir / "evals" / "skill-routing.yml"
    if not path.exists():
        return []
    known = {s.id for s in sources if s.kind == "skill"}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        return [f"{path}: invalid YAML: {e}"]
    return [
        err
        for case in (data.get("cases") or [])
        for err in _lint_routing_case(path, case, known)
    ]


def _lint_routing_case(path: Path, case: dict, known: set[str]) -> list[str]:
    cid = case.get("id", "?")
    return [
        f"{path}: case '{cid}' {field} unknown skill '{ref}'"
        for field in ("load", "do_not_load")
        for ref in (case.get(field) or [])
        if ref not in known
    ]
