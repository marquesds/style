from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from scripts.lint_source import lint_all, lint_skill_routing_evals
from scripts.source import load_all


def _write_skill(tmp_path: Path, skill_id: str) -> None:
    f = tmp_path / "skills" / f"{skill_id}.md"
    f.parent.mkdir(parents=True, exist_ok=True)
    title = skill_id.replace("-", " ").title()
    f.write_text(
        f"---\nid: {skill_id}\nkind: skill\ntitle: {title}\n"
        "description: >\n  A test skill.\n"
        "applies_when:\n  - testing lint behavior\n"
        "agents:\n  claude: { kind: skill }\n---\n\n"
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
            applies_when:
              - testing missing examples
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
        "applies_when:\n  - testing long functions\n"
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
        "applies_when:\n  - testing unknown references\n"
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


def test_lint_flags_unknown_static_skill_metadata_refs(tmp_path: Path) -> None:
    _write_skill(tmp_path, "known")
    f = tmp_path / "skills" / "known.md"
    text = f.read_text(encoding="utf-8")
    f.write_text(
        text.replace(
            "agents:\n  claude",
            "related_skills:\n  - missing-related\n"
            "conflicts_with:\n  - known\n"
            "verification_prompts:\n  - prompt: ''\n    should_load: true\n"
            "agents:\n  claude",
        ),
        encoding="utf-8",
    )

    errors = lint_all(load_all(tmp_path))
    assert any("related_skills" in e and "missing-related" in e for e in errors)
    assert any("conflicts_with" in e and "cannot reference itself" in e for e in errors)
    assert any("verification_prompts" in e and "prompt" in e for e in errors)


def test_lint_flags_native_skill_spec_violations(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "bad-name.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "---\n"
        "id: Bad_Name\nkind: skill\ntitle: Bad\ndescription: >\n  Uses <xml/> tags.\n"
        "agents: { claude: { kind: skill } }\n---\n\n"
        "## GOOD\n\n```python\nx = 1\n```\n\n## BAD\n\n```python\ny = 2\n```\n",
        encoding="utf-8",
    )

    errors = lint_all(load_all(tmp_path))
    assert any("must be lowercase words separated by hyphens" in e for e in errors)
    assert any("must match file name" in e for e in errors)
    assert any("must declare applies_when" in e for e in errors)
    assert any("must not contain XML tags" in e for e in errors)


def test_lint_flags_long_skill_discovery_description(tmp_path: Path) -> None:
    _write_skill(tmp_path, "long-description")
    skill = tmp_path / "skills" / "long-description.md"
    text = skill.read_text(encoding="utf-8")
    skill.write_text(text.replace("A test skill.", "x" * 1100), encoding="utf-8")

    errors = lint_all(load_all(tmp_path))
    assert any("skill discovery description exceeds 1024 chars" in e for e in errors)


def test_lint_skill_routing_evals_passes_with_known_skills(tmp_path: Path) -> None:
    _write_skill(tmp_path, "tdd")
    evals = tmp_path / "evals"
    evals.mkdir()
    (evals / "skill-routing.yml").write_text(
        "version: 1\n"
        "cases:\n"
        "  - id: feature-tdd\n"
        "    prompt: Add a checkout feature\n"
        "    load:\n      - tdd\n"
        "    do_not_load: []\n",
        encoding="utf-8",
    )

    assert lint_skill_routing_evals(tmp_path, load_all(tmp_path)) == []


def test_lint_skill_routing_evals_flags_bad_refs(tmp_path: Path) -> None:
    _write_skill(tmp_path, "tdd")
    evals = tmp_path / "evals"
    evals.mkdir()
    (evals / "skill-routing.yml").write_text(
        "version: 1\n"
        "cases:\n"
        "  - id: bad-ref\n"
        "    prompt: Review this diff\n"
        "    load:\n      - missing\n"
        "    do_not_load:\n      - tdd\n",
        encoding="utf-8",
    )

    errors = lint_skill_routing_evals(tmp_path, load_all(tmp_path))
    assert any("unknown skill 'missing'" in e for e in errors)
