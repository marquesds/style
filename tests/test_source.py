from __future__ import annotations

from pathlib import Path

import pytest

from scripts.source import SourceError, load_all, parse_text


def test_load_all_orders_by_kind_then_id(fake_source_dir: Path) -> None:
    sources = load_all(fake_source_dir)
    assert [s.id for s in sources] == ["tdd", "code-quality", "tdd"]
    assert [s.kind for s in sources] == ["command", "rule", "skill"]


def test_parse_text_rejects_missing_frontmatter() -> None:
    with pytest.raises(SourceError):
        parse_text(Path("x.md"), "no frontmatter here\n")


def test_parse_text_exposes_static_skill_metadata() -> None:
    src = parse_text(
        Path("skill.md"),
        "---\n"
        "id: sample\nkind: skill\ntitle: Sample\ndescription: d\n"
        "do_not_use_when:\n  - reviewing a diff\n"
        "related_skills:\n  - tdd\n"
        "conflicts_with:\n  - refactoring\n"
        "verification_prompts:\n  - prompt: Add a feature\n    should_load: true\n"
        "agents: { claude: { kind: skill } }\n---\nBody\n",
    )

    assert src.do_not_use_when == ["reviewing a diff"]
    assert src.related_skills == ["tdd"]
    assert src.conflicts_with == ["refactoring"]
    assert src.verification_prompts == [
        {"prompt": "Add a feature", "should_load": True}
    ]
