"""Mechanical lint for `source/` files.

Checks (fail closed):
- File <= 200 lines (including frontmatter).
- Frontmatter has all required fields and valid `kind`.
- `agents` mapping has at least one allowed agent.
- Rules and skills contain a `## GOOD` and `## BAD` example block.
- Python `def` blocks in code examples <= 10 lines (heuristic).
- Cross-skill references like `skill:<id>` resolve to a known id.

Caveman quality is NOT linted — that is a review concern.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Iterable
from pathlib import Path

from scripts.lint_skill_evals import lint_skill_routing_evals
from scripts.lint_skill_metadata import lint_static_skill_metadata
from scripts.source import (
    ALLOWED_AGENTS,
    ALLOWED_KINDS,
    REQUIRED_FIELDS,
    Source,
    SourceError,
    load_all,
)

__all__ = [
    "lint_all",
    "lint_skill_routing_evals",
    "lint_static_skill_metadata",
]

MAX_FILE_LINES = 200
MAX_FUNCTION_LINES = 10
SKILL_REF_RE = re.compile(r"\bskill:([a-z0-9][a-z0-9-]*)")
PY_FENCE_RE = re.compile(r"```python\n(.*?)```", re.DOTALL)
PY_DEF_RE = re.compile(r"^(\s*)def\s+\w+\(", re.MULTILINE)
HEADING_GOOD = re.compile(r"^##\s+GOOD\b", re.MULTILINE)
HEADING_BAD = re.compile(r"^##\s+BAD\b", re.MULTILINE)
CATALOG_ROW_RE = re.compile(r"^\|\s*([a-z][a-z0-9-]+)\s*\|", re.MULTILINE)


def lint_file_size(src: Source) -> list[str]:
    n = len(src.raw_lines)
    if n > MAX_FILE_LINES:
        return [f"{src.path}: {n} lines exceeds {MAX_FILE_LINES} max"]
    return []


def lint_frontmatter(src: Source) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_FIELDS - set(src.frontmatter.keys())
    if missing:
        errors.append(f"{src.path}: missing frontmatter fields: {sorted(missing)}")
    if "kind" in src.frontmatter and src.kind not in ALLOWED_KINDS:
        errors.append(f"{src.path}: kind '{src.kind}' not in {sorted(ALLOWED_KINDS)}")
    if "agents" in src.frontmatter:
        agent_keys = set(src.agents.keys())
        unknown = agent_keys - ALLOWED_AGENTS
        if unknown:
            errors.append(f"{src.path}: unknown agents: {sorted(unknown)}")
        if not agent_keys & ALLOWED_AGENTS:
            errors.append(f"{src.path}: agents map empty or all unknown")
    return errors


def lint_examples(src: Source) -> list[str]:
    if src.kind not in {"rule", "skill"}:
        return []
    errors: list[str] = []
    if not HEADING_GOOD.search(src.body):
        errors.append(f"{src.path}: missing '## GOOD' example block")
    if not HEADING_BAD.search(src.body):
        errors.append(f"{src.path}: missing '## BAD' example block")
    return errors


def lint_function_length(src: Source) -> list[str]:
    errors: list[str] = []
    for fence in PY_FENCE_RE.findall(src.body):
        for match in PY_DEF_RE.finditer(fence):
            body_len = _python_def_length(fence, match)
            if body_len > MAX_FUNCTION_LINES:
                errors.append(
                    f"{src.path}: example function exceeds {MAX_FUNCTION_LINES} lines "
                    f"({body_len} body lines)"
                )
    return errors


def _python_def_length(fence: str, def_match: re.Match[str]) -> int:
    """Count body lines until dedent or end of fence."""
    indent = def_match.group(1)
    after = fence[def_match.end() :]
    lines = after.splitlines()
    body_indent = indent + "    "
    body_count = 0
    seen_body = False
    for line in lines[1:]:
        if not line.strip():
            if seen_body:
                continue
            else:
                continue
        if line.startswith(body_indent):
            body_count += 1
            seen_body = True
        elif seen_body and not line.startswith(indent + " "):
            break
    return body_count


def lint_skills_catalog(sources: list[Source]) -> list[str]:
    """Verify skills-catalog rule lists exactly the known skill IDs."""
    catalog = next((s for s in sources if s.id == "skills-catalog" and s.kind == "rule"), None)
    if catalog is None:
        return []
    known = {s.id for s in sources if s.kind == "skill"}
    raw_ids = {m.group(1) for m in CATALOG_ROW_RE.finditer(catalog.body)}
    header_words = {"skill", "id", "load", "when"}
    referenced = raw_ids - header_words
    missing = known - referenced
    unknown = referenced - known
    errors: list[str] = []
    if missing:
        errors.append(f"skills-catalog: missing rows for: {sorted(missing)}")
    if unknown:
        errors.append(f"skills-catalog: unknown rows: {sorted(unknown)}")
    return errors


def lint_cross_refs(src: Source, known_ids: set[str]) -> list[str]:
    errors: list[str] = []
    for match in SKILL_REF_RE.finditer(src.body):
        ref = match.group(1)
        if ref not in known_ids:
            errors.append(f"{src.path}: unknown reference 'skill:{ref}'")
    return errors


def lint_all(sources: Iterable[Source]) -> list[str]:
    sources = list(sources)
    known_ids = {s.id for s in sources}
    known_skill_ids = {s.id for s in sources if s.kind == "skill"}
    errors: list[str] = []
    for s in sources:
        errors.extend(lint_file_size(s))
        errors.extend(lint_frontmatter(s))
        errors.extend(lint_examples(s))
        errors.extend(lint_function_length(s))
        errors.extend(lint_cross_refs(s, known_ids))
        errors.extend(lint_static_skill_metadata(s, known_skill_ids))
    errors.extend(lint_skills_catalog(sources))
    return errors


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    source_dir = Path(argv[0]) if argv else Path(__file__).resolve().parents[1] / "source"
    try:
        sources = load_all(source_dir)
    except SourceError as e:
        print(f"lint: {e}", file=sys.stderr)
        return 2
    errors = lint_all(sources) + lint_skill_routing_evals(source_dir, sources)
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        print(f"\n{len(errors)} lint error(s).", file=sys.stderr)
        return 1
    print(f"ok: {len(sources)} source file(s) clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
