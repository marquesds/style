from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from scripts.lint_source import lint_all
from scripts.source import load_all


def _write_skill(tmp_path: Path, skill_id: str) -> None:
    f = tmp_path / "skills" / f"{skill_id}.md"
    f.parent.mkdir(parents=True, exist_ok=True)
    title = skill_id.replace("-", " ").title()
    f.write_text(
        f"---\nid: {skill_id}\nkind: skill\ntitle: {title}\n"
        "description: >\n  A test skill.\nagents:\n  claude: { kind: skill }\n---\n\n"
        f"# {title}\n\n## GOOD\n\n```python\nx = 1\n```\n\n## BAD\n\n```python\ny = 2\n```\n",
        encoding="utf-8",
    )


def _write_catalog(tmp_path: Path, rows: str) -> None:
    catalog = tmp_path / "rules" / "skills-catalog.md"
    catalog.parent.mkdir(parents=True, exist_ok=True)
    catalog.write_text(
        "---\nid: skills-catalog\nkind: rule\ntitle: Skills Catalog\n"
        "description: >\n  Index of every skill.\n"
        "always_apply: true\nglobs: \"**/*\"\nagents:\n  claude: { kind: rule }\n---\n\n"
        "# Skills Catalog\n\n## Catalog\n\n| Skill ID | Load when |\n|----------|----------|\n"
        f"{rows}\n## GOOD\n\nOne skill → load it.\n\n## BAD\n\nPreload all skills.\n",
        encoding="utf-8",
    )


def test_lint_clean_on_fixture(fake_source_dir: Path) -> None:
    assert lint_all(load_all(fake_source_dir)) == []


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


def test_lint_skills_catalog_passes_when_in_sync(tmp_path: Path) -> None:
    _write_skill(tmp_path, "myskill")
    _write_catalog(tmp_path, "| myskill | any test |\n")
    assert not any("skills-catalog" in e for e in lint_all(load_all(tmp_path)))


def test_lint_skills_catalog_fails_when_skill_missing(tmp_path: Path) -> None:
    _write_skill(tmp_path, "missing-skill")
    _write_catalog(tmp_path, "")
    errors = lint_all(load_all(tmp_path))
    assert any("missing-skill" in e and "skills-catalog: missing rows" in e for e in errors)
