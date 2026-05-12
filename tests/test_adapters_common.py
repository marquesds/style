from __future__ import annotations

from pathlib import Path

import pytest

from scripts.adapters import ADAPTERS
from scripts.adapters.base import (
    BEGIN_MARKER,
    END_MARKER,
    FILE_MARKER_HTML,
    replace_managed_section,
    strip_managed_section,
    walk_managed_files,
)
from scripts.source import load_all


def test_replace_managed_section_first_write_appends() -> None:
    out = replace_managed_section("# Pre-existing\n\ncontent\n", "managed body")
    assert "# Pre-existing" in out
    assert BEGIN_MARKER in out and END_MARKER in out
    assert "managed body" in out


def test_replace_managed_section_replaces_existing() -> None:
    seed = (
        "# header\n\n"
        f"{BEGIN_MARKER}\nold body\n{END_MARKER}\n\n"
        "# trailing\n"
    )
    out = replace_managed_section(seed, "new body")
    assert "old body" not in out
    assert "new body" in out
    assert out.count(BEGIN_MARKER) == 1
    assert "# trailing" in out


def test_strip_managed_section_removes_block() -> None:
    existing = "# header\n\n" + BEGIN_MARKER + "\nblock\n" + END_MARKER + "\n\n# footer\n"
    result = strip_managed_section(existing)
    assert BEGIN_MARKER not in result
    assert "# header" in result
    assert "# footer" in result


def test_strip_managed_section_noop_when_absent() -> None:
    existing = "# no markers here\n"
    assert strip_managed_section(existing) == existing


def test_walk_managed_files_yields_marked(tmp_path: Path) -> None:
    marked = tmp_path / "a.md"
    marked.write_text(f"{FILE_MARKER_HTML}\ncontent\n", encoding="utf-8")
    clean = tmp_path / "b.md"
    clean.write_text("no marker\n", encoding="utf-8")
    found = list(walk_managed_files(tmp_path))
    assert found == [marked]


@pytest.mark.parametrize("agent_name", sorted(ADAPTERS.keys()))
def test_adapter_dry_run_emits_ops(
    fake_source_dir: Path, tmp_path: Path, agent_name: str
) -> None:
    adapter = ADAPTERS[agent_name]
    sources = load_all(fake_source_dir)
    report = adapter.write_all(sources, target_root=tmp_path / "out", dry_run=True)
    assert report.ops, f"{agent_name} produced no ops"
    for op in report.ops:
        assert FILE_MARKER_HTML in op.content or BEGIN_MARKER in op.content


def test_prune_preserves_user_content_in_merged(
    fake_source_dir: Path, tmp_path: Path
) -> None:
    out = tmp_path / "out"
    agents_md = out / ".codex" / "AGENTS.md"
    agents_md.parent.mkdir(parents=True)
    agents_md.write_text("# My own notes\n\nKeep this.\n", encoding="utf-8")
    sources = load_all(fake_source_dir)
    ADAPTERS["codex"].write_all(sources, target_root=out, dry_run=False)
    ADAPTERS["codex"].prune_all(target_root=out, dry_run=False)
    result = agents_md.read_text(encoding="utf-8")
    assert "Keep this" in result
    assert BEGIN_MARKER not in result


def test_prune_idempotent(fake_source_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    sources = load_all(fake_source_dir)
    ADAPTERS["cursor"].write_all(sources, target_root=out, dry_run=False)
    for _ in range(3):
        ADAPTERS["cursor"].prune_all(target_root=out, dry_run=False)
    assert not (out / ".cursor" / "skills" / "tdd" / "SKILL.md").exists()


def test_prune_dry_run_does_not_delete(fake_source_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    sources = load_all(fake_source_dir)
    ADAPTERS["cursor"].write_all(sources, target_root=out, dry_run=False)
    skill = out / ".cursor" / "skills" / "tdd" / "SKILL.md"
    assert skill.exists()
    report = ADAPTERS["cursor"].prune_all(target_root=out, dry_run=True)
    assert skill.exists()
    assert any(op.action == "delete" for op in report.ops)


def test_idempotent_rewrite(fake_source_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    sources = load_all(fake_source_dir)
    for _ in range(3):
        ADAPTERS["codex"].write_all(sources, target_root=out, dry_run=False)
    text = (out / ".codex" / "AGENTS.md").read_text(encoding="utf-8")
    assert text.count(BEGIN_MARKER) == 1
    assert text.count(END_MARKER) == 1
