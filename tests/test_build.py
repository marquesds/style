from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from scripts.adapters import ADAPTERS
from scripts.adapters.base import (
    BEGIN_MARKER,
    END_MARKER,
    FILE_MARKER_HTML,
    replace_managed_section,
)
from scripts.lint_source import lint_all
from scripts.source import load_all, parse_text


@pytest.fixture
def fake_source_dir(tmp_path: Path) -> Path:
    """Build a tiny source/ tree covering all three kinds and every agent."""
    root = tmp_path / "source"
    (root / "rules").mkdir(parents=True)
    (root / "skills").mkdir(parents=True)
    (root / "commands").mkdir(parents=True)

    (root / "rules" / "code-quality.md").write_text(
        dedent(
            """\
            ---
            id: code-quality
            kind: rule
            title: Code Quality
            description: >
              Max 200 lines per file. Max 10 lines per function.
            applies_when:
              - any source change
            always_apply: true
            globs: "**/*"
            agents:
              claude: { kind: rule }
              cursor: { kind: rule, glob: "**/*" }
              codex:  { section: rules }
              goose:  { section: rules }
              openclaw: { section: rules }
              opencode: { kind: rule }
              pi:       { section: rules }
              vibe:   { kind: rule }
            ---

            # Code Quality

            Small files. Small functions. Iterator chains over loops.

            ## GOOD

            ```python
            def total(items):
                return sum(i.price for i in items)
            ```

            ## BAD

            ```python
            def total(items):
                t = 0
                for i in items:
                    t = t + i.price
                return t
            ```
            """
        ),
        encoding="utf-8",
    )
    (root / "skills" / "tdd.md").write_text(
        dedent(
            """\
            ---
            id: tdd
            kind: skill
            title: TDD
            description: >
              Test fail first. Code second.
            applies_when:
              - new logic
            agents:
              claude: { kind: skill }
              cursor: { kind: rule }
              codex:  { section: skills }
              goose:  { section: skills }
              openclaw: { section: skills }
              opencode: { kind: skill }
              pi:       { section: skills }
              vibe:   { kind: skill }
            ---

            # TDD

            RED then GREEN then REFACTOR.

            ## GOOD

            ```python
            def test_adds_two_numbers():
                assert add(1, 2) == 3
            ```

            ## BAD

            ```python
            def test_works():
                assert True
            ```
            """
        ),
        encoding="utf-8",
    )
    (root / "commands" / "tdd.md").write_text(
        dedent(
            """\
            ---
            id: tdd
            kind: command
            title: Start TDD cycle
            description: >
              Kick off RED-GREEN-REFACTOR for the current target.
            agents:
              claude: { kind: command }
              cursor: { kind: command }
              codex:  { section: commands }
              goose:  { section: commands }
              openclaw: { section: commands }
              opencode: { kind: command }
              pi:       { section: commands }
              vibe:   { kind: command }
            ---

            Walk RED-GREEN-REFACTOR for the current target. Refer to skill:tdd.
            """
        ),
        encoding="utf-8",
    )
    return root


def test_load_all_orders_by_kind_then_id(fake_source_dir: Path) -> None:
    sources = load_all(fake_source_dir)
    assert [s.id for s in sources] == ["tdd", "code-quality", "tdd"]
    assert [s.kind for s in sources] == ["command", "rule", "skill"]


def test_lint_clean_on_fixture(fake_source_dir: Path) -> None:
    sources = load_all(fake_source_dir)
    assert lint_all(sources) == []


def test_lint_flags_missing_examples(tmp_path: Path) -> None:
    bad = tmp_path / "skills" / "no-examples.md"
    bad.parent.mkdir(parents=True)
    bad.write_text(
        dedent(
            """\
            ---
            id: no-examples
            kind: skill
            title: No Examples
            description: >
              Missing required example blocks.
            agents:
              claude: { kind: skill }
            ---

            # No Examples

            Body without GOOD or BAD blocks.
            """
        ),
        encoding="utf-8",
    )
    errors = lint_all(load_all(tmp_path))
    assert any("missing '## GOOD'" in e for e in errors)
    assert any("missing '## BAD'" in e for e in errors)


def test_lint_flags_long_function(tmp_path: Path) -> None:
    f = tmp_path / "skills" / "long-fn.md"
    f.parent.mkdir(parents=True)
    body = "\n".join([f"    line_{i} = {i}" for i in range(15)])
    f.write_text(
        "---\n"
        "id: long-fn\nkind: skill\ntitle: Long\ndescription: >\n  d\n"
        "agents: { claude: { kind: skill } }\n---\n\n"
        "## GOOD\n\n```python\n"
        f"def big():\n{body}\n```\n\n"
        "## BAD\n\n```python\nx = 1\n```\n",
        encoding="utf-8",
    )
    errors = lint_all(load_all(tmp_path))
    assert any("exceeds 10 lines" in e for e in errors)


def test_lint_flags_unknown_skill_ref(tmp_path: Path) -> None:
    f = tmp_path / "skills" / "ref.md"
    f.parent.mkdir(parents=True)
    f.write_text(
        "---\nid: ref\nkind: skill\ntitle: Ref\ndescription: >\n  d\n"
        "agents: { claude: { kind: skill } }\n---\n\n"
        "Refer to skill:does-not-exist.\n\n## GOOD\n\n```python\nx=1\n```\n\n"
        "## BAD\n\n```python\ny=2\n```\n",
        encoding="utf-8",
    )
    errors = lint_all(load_all(tmp_path))
    assert any("skill:does-not-exist" in e for e in errors)


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


@pytest.mark.parametrize("agent_name", sorted(ADAPTERS.keys()))
def test_adapter_dry_run_emits_ops(fake_source_dir: Path, tmp_path: Path, agent_name: str) -> None:
    adapter = ADAPTERS[agent_name]
    sources = load_all(fake_source_dir)
    report = adapter.write_all(sources, target_root=tmp_path / "out", dry_run=True)
    assert report.ops, f"{agent_name} produced no ops"
    for op in report.ops:
        assert FILE_MARKER_HTML in op.content or BEGIN_MARKER in op.content


def test_claude_writes_skill_dir(fake_source_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    sources = load_all(fake_source_dir)
    ADAPTERS["claude"].write_all(sources, target_root=out, dry_run=False)
    skill = out / ".claude" / "skills" / "tdd" / "SKILL.md"
    assert skill.exists()
    text = skill.read_text(encoding="utf-8")
    assert text.startswith("---\nname: tdd\n")
    assert "RED then GREEN" in text


def test_cursor_writes_mdc(fake_source_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    sources = load_all(fake_source_dir)
    ADAPTERS["cursor"].write_all(sources, target_root=out, dry_run=False)
    mdc = out / ".cursor" / "rules" / "code-quality.mdc"
    assert mdc.exists()
    head = mdc.read_text(encoding="utf-8").splitlines()[:6]
    assert head[0] == "---"
    assert any(line.startswith("description: ") for line in head)
    assert any("alwaysApply: true" in line for line in head)


def test_codex_merges_into_agents_md(fake_source_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    pre = out / "AGENTS.md"
    pre.parent.mkdir(parents=True)
    pre.write_text("# Pre-existing user content\n", encoding="utf-8")
    sources = load_all(fake_source_dir)
    ADAPTERS["codex"].write_all(sources, target_root=out, dry_run=False)
    text = pre.read_text(encoding="utf-8")
    assert "Pre-existing user content" in text
    assert BEGIN_MARKER in text and END_MARKER in text
    assert "Code Quality" in text and "TDD" in text


def test_opencode_writes_layout(fake_source_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    sources = load_all(fake_source_dir)
    ADAPTERS["opencode"].write_all(sources, target_root=out, dry_run=False)
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
    sources = load_all(fake_source_dir)
    ADAPTERS["openclaw"].write_all(sources, target_root=out, dry_run=False)
    path = out / ".openclaw" / "workspace" / "AGENTS.md"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert BEGIN_MARKER in text and END_MARKER in text
    assert "Code Quality" in text


def test_goose_merges_config_agents(fake_source_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    sources = load_all(fake_source_dir)
    ADAPTERS["goose"].write_all(sources, target_root=out, dry_run=False)
    path = out / ".config" / "goose" / "AGENTS.md"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert BEGIN_MARKER in text and END_MARKER in text
    assert "Code Quality" in text


def test_pi_merges_into_agents_md(fake_source_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    sources = load_all(fake_source_dir)
    ADAPTERS["pi"].write_all(sources, target_root=out, dry_run=False)
    text = (out / "AGENTS.md").read_text(encoding="utf-8")
    assert BEGIN_MARKER in text and END_MARKER in text
    assert "TDD" in text


def test_idempotent_rewrite(fake_source_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    sources = load_all(fake_source_dir)
    for _ in range(3):
        ADAPTERS["codex"].write_all(sources, target_root=out, dry_run=False)
    text = (out / "AGENTS.md").read_text(encoding="utf-8")
    assert text.count(BEGIN_MARKER) == 1
    assert text.count(END_MARKER) == 1


def test_parse_text_rejects_missing_frontmatter() -> None:
    from scripts.source import SourceError

    with pytest.raises(SourceError):
        parse_text(Path("x.md"), "no frontmatter here\n")
