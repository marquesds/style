"""Mechanical lint for `source/` files.

Checks (fail closed):
- Frontmatter has all required fields and valid `kind`.
- `agents` mapping has at least one allowed agent.
- Rules and skills contain a `## GOOD` and `## BAD` example block.
- Python `def` blocks in code examples <= 10 lines (heuristic).
- Cross-skill references like `skill:<id>` resolve to a known id.
- Native skills emit spec-compliant discovery metadata.
- Skill bundles: kind skill, id matches directory, aux files plain markdown
  (see scripts/lint_bundle.py).

Prose quality is NOT linted — that is a review concern.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Iterable
from pathlib import Path

from scripts.lint_bundle import (
    SOURCE_ID_RE,
    def_length_errors,
    lint_auxiliary,
    lint_bundle_kind,
)
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

MAX_SKILL_DESCRIPTION_CHARS = 1024
SKILL_REF_RE = re.compile(r"\bskill:([a-z0-9][a-z0-9-]*)")
HEADING_GOOD = re.compile(r"^##\s+GOOD\b", re.MULTILINE)
HEADING_BAD = re.compile(r"^##\s+BAD\b", re.MULTILINE)
CATALOG_ROW_RE = re.compile(r"^\|\s*([a-z][a-z0-9-]+)\s*\|", re.MULTILINE)
XML_TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")
QUOTED_DESCRIPTION_RE = re.compile(r'^description: "(?:[^"\\]|\\.)*"$')




def lint_frontmatter(src: Source) -> list[str]:
    errors: list[str] = []
    description_line = next(
        (line for line in src.raw_lines if line.startswith("description:")), None
    )
    if description_line is not None and not QUOTED_DESCRIPTION_RE.fullmatch(description_line):
        errors.append(f"{src.path}: description must be a double-quoted YAML string")
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


def lint_native_skill_spec(src: Source) -> list[str]:
    errors: list[str] = []
    src_id = str(src.frontmatter.get("id") or "")
    if src_id and not SOURCE_ID_RE.fullmatch(src_id):
        errors.append(f"{src.path}: id '{src_id}' must be lowercase words separated by hyphens")
    if src_id and src.is_bundle and src.path.parent.name != src_id:
        errors.append(
            f"{src.path}: id '{src_id}' must match directory name '{src.path.parent.name}'"
        )
    if src_id and not src.is_bundle and src.path.stem != src_id:
        errors.append(f"{src.path}: id '{src_id}' must match file name '{src.path.stem}'")
    if src.frontmatter.get("kind") != "skill":
        return errors
    if not src.applies_when:
        errors.append(f"{src.path}: skill must declare applies_when for discovery")
    if "description" not in src.frontmatter:
        return errors
    description = src.discovery_description.strip()
    if not description:
        errors.append(f"{src.path}: skill discovery description must be non-empty")
    if len(description) > MAX_SKILL_DESCRIPTION_CHARS:
        errors.append(
            f"{src.path}: skill discovery description exceeds "
            f"{MAX_SKILL_DESCRIPTION_CHARS} chars ({len(description)})"
        )
    if XML_TAG_RE.search(description):
        errors.append(f"{src.path}: skill discovery description must not contain XML tags")
    return errors


def lint_function_length(src: Source) -> list[str]:
    return def_length_errors(src.path, src.body)


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
    texts = [(src.path, src.body)] + [(a.path, a.content) for a in src.auxiliary]
    return [
        f"{path}: unknown reference 'skill:{m.group(1)}'"
        for path, text in texts
        for m in SKILL_REF_RE.finditer(text)
        if m.group(1) not in known_ids
    ]


def lint_all(sources: Iterable[Source]) -> list[str]:
    sources = list(sources)
    known_ids = {s.id for s in sources}
    known_skill_ids = {s.id for s in sources if s.kind == "skill"}
    errors: list[str] = []
    for s in sources:
        errors.extend(lint_frontmatter(s))
        errors.extend(lint_native_skill_spec(s))
        errors.extend(lint_examples(s))
        errors.extend(lint_function_length(s))
        errors.extend(lint_bundle_kind(s))
        errors.extend(lint_auxiliary(s))
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
