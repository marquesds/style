"""Source-file loader for the style harness.

Parses a Markdown file with YAML frontmatter into a typed `Source` record.
Pure functions only — no I/O side effects beyond `Path.read_text`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

FRONTMATTER_DELIM = "---"
ALLOWED_KINDS = frozenset({"rule", "skill", "command"})
ALLOWED_AGENTS = frozenset(
    {"claude", "cursor", "codex", "openclaw", "opencode", "pi", "vibe"}
)
REQUIRED_FIELDS = frozenset({"id", "kind", "title", "description", "agents"})


class SourceError(ValueError):
    """Raised when a source file is malformed."""


@dataclass(frozen=True)
class Source:
    """A loaded source file."""

    path: Path
    frontmatter: dict[str, Any]
    body: str
    body_line_offset: int = 0
    raw_lines: tuple[str, ...] = field(default_factory=tuple)

    @property
    def id(self) -> str:
        return str(self.frontmatter["id"])

    @property
    def kind(self) -> str:
        return str(self.frontmatter["kind"])

    @property
    def title(self) -> str:
        return str(self.frontmatter["title"])

    @property
    def description(self) -> str:
        return str(self.frontmatter["description"]).strip()

    @property
    def applies_when(self) -> list[str]:
        v = self.frontmatter.get("applies_when") or []
        return [str(x) for x in v]

    @property
    def always_apply(self) -> bool:
        return bool(self.frontmatter.get("always_apply", False))

    @property
    def globs(self) -> str | None:
        v = self.frontmatter.get("globs")
        return None if v is None else str(v)

    @property
    def agents(self) -> dict[str, dict[str, Any]]:
        v = self.frontmatter.get("agents") or {}
        return {str(k): dict(val or {}) for k, val in v.items()}


def parse_text(path: Path, text: str) -> Source:
    """Parse a frontmatter+body Markdown string into a Source."""
    if not text.startswith(FRONTMATTER_DELIM + "\n"):
        raise SourceError(f"{path}: missing opening frontmatter delimiter")
    rest = text[len(FRONTMATTER_DELIM) + 1 :]
    closing = "\n" + FRONTMATTER_DELIM + "\n"
    end = rest.find(closing)
    if end < 0:
        raise SourceError(f"{path}: unterminated frontmatter (no closing '---')")
    fm_raw = rest[:end]
    body = rest[end + len(closing) :]
    try:
        fm = yaml.safe_load(fm_raw) or {}
    except yaml.YAMLError as e:
        raise SourceError(f"{path}: invalid YAML frontmatter: {e}") from e
    if not isinstance(fm, dict):
        raise SourceError(f"{path}: frontmatter must be a mapping, got {type(fm).__name__}")

    body_line_offset = 1 + fm_raw.count("\n") + 2
    return Source(
        path=path,
        frontmatter=fm,
        body=body,
        body_line_offset=body_line_offset,
        raw_lines=tuple(text.splitlines()),
    )


def parse(path: Path) -> Source:
    return parse_text(path, path.read_text(encoding="utf-8"))


def load_all(source_dir: Path) -> list[Source]:
    """Load every `*.md` file under `source_dir`, sorted by (kind, id)."""
    files = sorted(source_dir.rglob("*.md"))
    sources = [parse(p) for p in files]
    return sorted(sources, key=lambda s: (s.kind, s.id))


def by_kind(sources: list[Source], kind: str) -> list[Source]:
    return [s for s in sources if s.kind == kind]
