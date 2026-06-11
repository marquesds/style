from __future__ import annotations

from pathlib import Path

import pytest

from scripts.source import SourceError, load_all, parse_text
from tests.conftest import AUX_SENTINEL


def test_load_all_orders_by_kind_then_id(fake_source_dir: Path) -> None:
    sources = load_all(fake_source_dir)
    assert [s.id for s in sources] == ["tdd", "code-quality", "py-bundle", "tdd"]
    assert [s.kind for s in sources] == ["command", "rule", "skill", "skill"]


def test_load_all_parses_bundle_once_with_auxiliary(fake_source_dir: Path) -> None:
    sources = load_all(fake_source_dir)
    bundles = [s for s in sources if s.id == "py-bundle"]
    assert len(bundles) == 1
    assert bundles[0].is_bundle
    assert [a.name for a in bundles[0].auxiliary] == ["data-model.md"]


def test_load_all_excludes_auxiliary_from_flat_scan(fake_source_dir: Path) -> None:
    sources = load_all(fake_source_dir)
    assert not any(s.path.name == "data-model.md" for s in sources)


def test_bundle_auxiliary_content_loaded(fake_source_dir: Path) -> None:
    bundle = next(s for s in load_all(fake_source_dir) if s.id == "py-bundle")
    assert AUX_SENTINEL in bundle.auxiliary[0].content


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
