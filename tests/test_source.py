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
