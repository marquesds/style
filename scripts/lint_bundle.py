"""Lint for multi-file skill bundles plus shared example-code length helpers.

A bundle is a `source/skills/<id>/` directory holding `SKILL.md` and sibling
auxiliary `*.md` reference files. Auxiliary files are plain markdown: no
frontmatter, <= MAX_FILE_LINES lines, python example defs <= MAX_FUNCTION_LINES.
"""

from __future__ import annotations

import re
from pathlib import Path

from scripts.source import AuxFile, Source

MAX_FILE_LINES = 200
MAX_FUNCTION_LINES = 10
SOURCE_ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
PY_FENCE_RE = re.compile(r"```python\n(.*?)```", re.DOTALL)
PY_DEF_RE = re.compile(r"^(\s*)def\s+\w+\(", re.MULTILINE)


def def_length_errors(path: Path, text: str) -> list[str]:
    """Flag python fenced example defs whose body exceeds MAX_FUNCTION_LINES."""
    return [
        f"{path}: example function exceeds {MAX_FUNCTION_LINES} lines ({n} body lines)"
        for fence in PY_FENCE_RE.findall(text)
        for match in PY_DEF_RE.finditer(fence)
        if (n := _python_def_length(fence, match)) > MAX_FUNCTION_LINES
    ]


def _python_def_length(fence: str, def_match: re.Match[str]) -> int:
    """Count body lines until dedent or end of fence."""
    indent = def_match.group(1)
    after = fence[def_match.end() :]
    body_indent = indent + "    "
    body_count = 0
    seen_body = False
    for line in after.splitlines()[1:]:
        if not line.strip():
            continue
        if line.startswith(body_indent):
            body_count += 1
            seen_body = True
        elif seen_body and not line.startswith(indent + " "):
            break
    return body_count


def lint_bundle_kind(src: Source) -> list[str]:
    kind = src.frontmatter.get("kind")
    if src.is_bundle and kind != "skill":
        return [f"{src.path}: bundle must be kind 'skill', got '{kind}'"]
    return []


def lint_auxiliary(src: Source) -> list[str]:
    return [e for aux in src.auxiliary for e in _lint_aux_file(aux)]


def _lint_aux_file(aux: AuxFile) -> list[str]:
    errors = _aux_shape_errors(aux)
    errors.extend(def_length_errors(aux.path, aux.content))
    return errors


def _aux_shape_errors(aux: AuxFile) -> list[str]:
    errors: list[str] = []
    n = len(aux.content.splitlines())
    if n > MAX_FILE_LINES:
        errors.append(f"{aux.path}: {n} lines exceeds {MAX_FILE_LINES} max")
    if aux.content.startswith("---"):
        errors.append(f"{aux.path}: auxiliary file must not start with frontmatter '---'")
    if not SOURCE_ID_RE.fullmatch(Path(aux.name).stem):
        errors.append(f"{aux.path}: stem must be lowercase words separated by hyphens")
    return errors
