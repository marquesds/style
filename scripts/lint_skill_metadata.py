"""Lint for optional static skill-routing metadata.

Skills may declare `related_skills`, `conflicts_with`, and
`verification_prompts` in frontmatter. Refs must resolve to known skills;
self-conflicts and empty/malformed verification prompts are rejected.
"""

from __future__ import annotations

from scripts.source import Source


def lint_static_skill_metadata(src: Source, known_skill_ids: set[str]) -> list[str]:
    if src.kind != "skill":
        return []
    errors: list[str] = []
    errors.extend(_lint_related(src, known_skill_ids))
    errors.extend(_lint_conflicts(src, known_skill_ids))
    errors.extend(_lint_verification_prompts(src))
    return errors


def _lint_related(src: Source, known: set[str]) -> list[str]:
    return [
        f"{src.path}: related_skills references unknown skill '{ref}'"
        for ref in src.related_skills
        if ref not in known
    ]


def _lint_conflicts(src: Source, known: set[str]) -> list[str]:
    errors: list[str] = []
    for ref in src.conflicts_with:
        if ref == src.id:
            errors.append(f"{src.path}: conflicts_with cannot reference itself ('{ref}')")
        elif ref not in known:
            errors.append(f"{src.path}: conflicts_with references unknown skill '{ref}'")
    return errors


def _lint_verification_prompts(src: Source) -> list[str]:
    errors: list[str] = []
    for i, item in enumerate(src.verification_prompts):
        if not isinstance(item, dict):
            errors.append(f"{src.path}: verification_prompts[{i}] must be a mapping")
            continue
        if not str(item.get("prompt", "")).strip():
            errors.append(f"{src.path}: verification_prompts[{i}] has empty 'prompt'")
        if "should_load" not in item:
            errors.append(f"{src.path}: verification_prompts[{i}] missing 'should_load'")
    return errors
