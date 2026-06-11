from __future__ import annotations

from pathlib import Path

import pytest

from scripts.adapters import ADAPTERS
from scripts.adapters.base import FILE_MARKER_HTML
from scripts.adapters.codex import AUX_NOT_INSTALLED_NOTE
from scripts.source import load_all
from tests.conftest import AUX_SENTINEL

NATIVE_SKILL_DIRS = {
    "claude": Path(".claude") / "skills",
    "cursor": Path(".cursor") / "skills",
    "codex": Path(".agents") / "skills",
    "opencode": Path(".config") / "opencode" / "skills",
}
MERGED_AGENTS_MD = {
    "goose": Path(".config") / "goose" / "AGENTS.md",
    "openclaw": Path(".openclaw") / "workspace" / "AGENTS.md",
    "pi": Path(".pi") / "agent" / "AGENTS.md",
}


def _install(agent_name: str, fake_source_dir: Path, out: Path) -> None:
    ADAPTERS[agent_name].write_all(load_all(fake_source_dir), target_root=out, dry_run=False)


@pytest.mark.parametrize("agent_name", sorted(NATIVE_SKILL_DIRS))
def test_native_agent_writes_bundle_aux(
    fake_source_dir: Path, tmp_path: Path, agent_name: str
) -> None:
    out = tmp_path / "out"
    _install(agent_name, fake_source_dir, out)
    aux = out / NATIVE_SKILL_DIRS[agent_name] / "py-bundle" / "data-model.md"
    assert aux.exists()
    text = aux.read_text(encoding="utf-8")
    assert FILE_MARKER_HTML in text.splitlines()[0]
    assert AUX_SENTINEL in text


@pytest.mark.parametrize("agent_name", sorted(NATIVE_SKILL_DIRS))
def test_prune_removes_bundle_aux(
    fake_source_dir: Path, tmp_path: Path, agent_name: str
) -> None:
    out = tmp_path / "out"
    _install(agent_name, fake_source_dir, out)
    aux = out / NATIVE_SKILL_DIRS[agent_name] / "py-bundle" / "data-model.md"
    assert aux.exists()
    ADAPTERS[agent_name].prune_all(target_root=out, dry_run=False)
    assert not aux.exists()


def test_vibe_writes_bundle_dir_and_keeps_flat_skills(
    fake_source_dir: Path, tmp_path: Path
) -> None:
    out = tmp_path / "out"
    _install("vibe", fake_source_dir, out)
    bundle_dir = out / ".vibe" / "skills" / "py-bundle"
    assert (bundle_dir / "SKILL.md").exists()
    aux_text = (bundle_dir / "data-model.md").read_text(encoding="utf-8")
    assert FILE_MARKER_HTML in aux_text.splitlines()[0]
    assert AUX_SENTINEL in aux_text
    assert (out / ".vibe" / "skills" / "tdd.md").exists()


def test_vibe_prune_removes_bundle_files(fake_source_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    _install("vibe", fake_source_dir, out)
    bundle_dir = out / ".vibe" / "skills" / "py-bundle"
    ADAPTERS["vibe"].prune_all(target_root=out, dry_run=False)
    assert not (bundle_dir / "SKILL.md").exists()
    assert not (bundle_dir / "data-model.md").exists()


@pytest.mark.parametrize("agent_name", sorted(MERGED_AGENTS_MD))
def test_merged_agents_notes_missing_reference_files(
    fake_source_dir: Path, tmp_path: Path, agent_name: str
) -> None:
    out = tmp_path / "out"
    _install(agent_name, fake_source_dir, out)
    text = (out / MERGED_AGENTS_MD[agent_name]).read_text(encoding="utf-8")
    assert "Index: see data-model.md" in text
    assert AUX_NOT_INSTALLED_NOTE in text
    assert AUX_SENTINEL not in text
