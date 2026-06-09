from __future__ import annotations

from pathlib import Path

from scripts.adapters import ADAPTERS
from scripts.adapters.base import BEGIN_MARKER, END_MARKER
from scripts.source import load_all


def test_claude_writes_skill_dir(fake_source_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    ADAPTERS["claude"].write_all(load_all(fake_source_dir), target_root=out, dry_run=False)
    skill = out / ".claude" / "skills" / "tdd" / "SKILL.md"
    assert skill.exists()
    text = skill.read_text(encoding="utf-8")
    assert text.startswith("---\nname: tdd\n")
    assert "Use when: new logic." in text
    assert "paths:" not in text
    assert "RED then GREEN" in text


def test_cursor_writes_mdc(fake_source_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    ADAPTERS["cursor"].write_all(load_all(fake_source_dir), target_root=out, dry_run=False)
    mdc = out / ".cursor" / "rules" / "code-quality.mdc"
    assert mdc.exists()
    head = mdc.read_text(encoding="utf-8").splitlines()[:6]
    assert head[0] == "---"
    assert any(line.startswith("description: ") for line in head)
    assert any("alwaysApply: true" in line for line in head)


def test_cursor_writes_skill_dir(fake_source_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    ADAPTERS["cursor"].write_all(load_all(fake_source_dir), target_root=out, dry_run=False)
    skill = out / ".cursor" / "skills" / "tdd" / "SKILL.md"
    assert skill.exists()
    text = skill.read_text(encoding="utf-8")
    assert text.startswith("---\nname: tdd\n")
    assert 'paths: "**/*.py"' in text
    assert "Use when: new logic." in text
    assert "RED then GREEN" in text
    assert (out / ".cursor" / "rules" / "tdd.mdc").exists() is False


def test_cursor_prune_removes_skill_dir(fake_source_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    ADAPTERS["cursor"].write_all(load_all(fake_source_dir), target_root=out, dry_run=False)
    skill = out / ".cursor" / "skills" / "tdd" / "SKILL.md"
    assert skill.exists()
    ADAPTERS["cursor"].prune_all(target_root=out, dry_run=False)
    assert not skill.exists()


def test_codex_writes_agents_md_and_native_skills(
    fake_source_dir: Path, tmp_path: Path
) -> None:
    out = tmp_path / "out"
    pre = out / ".codex" / "AGENTS.md"
    pre.parent.mkdir(parents=True)
    pre.write_text("# Pre-existing user content\n", encoding="utf-8")
    ADAPTERS["codex"].write_all(load_all(fake_source_dir), target_root=out, dry_run=False)
    text = pre.read_text(encoding="utf-8")
    assert "Pre-existing user content" in text
    assert BEGIN_MARKER in text and END_MARKER in text
    assert "Code Quality" in text and "Start TDD cycle" in text
    assert "## Skills" not in text
    assert "RED then GREEN" not in text
    skill = out / ".agents" / "skills" / "tdd" / "SKILL.md"
    assert skill.exists()
    skill_text = skill.read_text(encoding="utf-8")
    assert skill_text.startswith("---\nname: tdd\n")
    assert "Use when: new logic." in skill_text
    assert "paths:" not in skill_text


def test_codex_install_strips_legacy_root_agents_md(
    fake_source_dir: Path, tmp_path: Path
) -> None:
    out = tmp_path / "out"
    legacy = out / "AGENTS.md"
    legacy.parent.mkdir(parents=True)
    legacy.write_text(
        f"# My notes\n\n{BEGIN_MARKER}\nold block\n{END_MARKER}\n\nKeep this.\n",
        encoding="utf-8",
    )
    ADAPTERS["codex"].write_all(load_all(fake_source_dir), target_root=out, dry_run=False)
    result = legacy.read_text(encoding="utf-8")
    assert BEGIN_MARKER not in result
    assert "Keep this" in result


def test_codex_prune_removes_native_skills(fake_source_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    ADAPTERS["codex"].write_all(load_all(fake_source_dir), target_root=out, dry_run=False)
    skill = out / ".agents" / "skills" / "tdd" / "SKILL.md"
    assert skill.exists()
    ADAPTERS["codex"].prune_all(target_root=out, dry_run=False)
    assert not skill.exists()


def test_opencode_writes_layout(fake_source_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    ADAPTERS["opencode"].write_all(load_all(fake_source_dir), target_root=out, dry_run=False)
    agents = out / ".config" / "opencode" / "AGENTS.md"
    assert agents.exists()
    ag_text = agents.read_text(encoding="utf-8")
    assert BEGIN_MARKER in ag_text and "Code Quality" in ag_text
    skill = out / ".config" / "opencode" / "skills" / "tdd" / "SKILL.md"
    assert skill.exists()
    assert skill.read_text(encoding="utf-8").startswith("---\nname: tdd\n")
    cmd = out / ".config" / "opencode" / "commands" / "tdd.md"
    assert "---\ndescription: >\n" in cmd.read_text(encoding="utf-8")


def test_openclaw_merges_workspace_agents(fake_source_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    ADAPTERS["openclaw"].write_all(load_all(fake_source_dir), target_root=out, dry_run=False)
    path = out / ".openclaw" / "workspace" / "AGENTS.md"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert BEGIN_MARKER in text and END_MARKER in text
    assert "Code Quality" in text


def test_goose_merges_config_agents(fake_source_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    ADAPTERS["goose"].write_all(load_all(fake_source_dir), target_root=out, dry_run=False)
    path = out / ".config" / "goose" / "AGENTS.md"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert BEGIN_MARKER in text and END_MARKER in text
    assert "Code Quality" in text


def test_pi_merges_into_agents_md(fake_source_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    ADAPTERS["pi"].write_all(load_all(fake_source_dir), target_root=out, dry_run=False)
    text = (out / ".pi" / "agent" / "AGENTS.md").read_text(encoding="utf-8")
    assert BEGIN_MARKER in text and END_MARKER in text
    assert "TDD" in text


def test_pi_install_strips_legacy_root_agents_md(
    fake_source_dir: Path, tmp_path: Path
) -> None:
    out = tmp_path / "out"
    legacy = out / "AGENTS.md"
    legacy.parent.mkdir(parents=True)
    legacy.write_text(
        f"# My notes\n\n{BEGIN_MARKER}\nold block\n{END_MARKER}\n\nKeep this.\n",
        encoding="utf-8",
    )
    ADAPTERS["pi"].write_all(load_all(fake_source_dir), target_root=out, dry_run=False)
    result = legacy.read_text(encoding="utf-8")
    assert BEGIN_MARKER not in result
    assert "Keep this" in result
