from __future__ import annotations

from pathlib import Path

from scripts.lint_source import lint_all
from scripts.source import load_all

SKILL_TEMPLATE = (
    "---\nid: {skill_id}\nkind: {kind}\ntitle: Bundle\ndescription: \"A bundle.\"\n"
    "applies_when:\n  - testing bundles\n"
    "agents: {{ claude: {{ kind: skill }} }}\n---\n\n"
    "# Bundle\n\n## GOOD\n\n```python\nx = 1\n```\n\n## BAD\n\n```python\ny = 2\n```\n"
)


def _write_bundle(
    tmp_path: Path,
    *,
    skill_id: str = "py-bundle",
    dir_name: str = "py-bundle",
    kind: str = "skill",
    parent: str = "skills",
    aux: dict[str, str] | None = None,
) -> Path:
    bundle = tmp_path / parent / dir_name
    bundle.mkdir(parents=True)
    (bundle / "SKILL.md").write_text(
        SKILL_TEMPLATE.format(skill_id=skill_id, kind=kind), encoding="utf-8"
    )
    for name, content in (aux or {"data-model.md": "# Data Model\n\nClean aux.\n"}).items():
        (bundle / name).write_text(content, encoding="utf-8")
    return bundle


def test_lint_flags_bundle_id_dir_mismatch(tmp_path: Path) -> None:
    _write_bundle(tmp_path, skill_id="py-bundle", dir_name="other-dir")
    errors = lint_all(load_all(tmp_path))
    assert any("must match directory name 'other-dir'" in e for e in errors)


def test_lint_flags_bundle_with_rule_kind(tmp_path: Path) -> None:
    _write_bundle(tmp_path, kind="rule", parent="rules")
    errors = lint_all(load_all(tmp_path))
    assert any("bundle must be kind 'skill'" in e for e in errors)


def test_lint_allows_large_auxiliary_documentation(tmp_path: Path) -> None:
    long_aux = "# Long\n" + "line\n" * 200
    _write_bundle(tmp_path, aux={"long.md": long_aux})
    assert lint_all(load_all(tmp_path)) == []


def test_lint_flags_aux_long_python_def(tmp_path: Path) -> None:
    body = "\n".join(f"    line_{i} = {i}" for i in range(15))
    aux = f"# Aux\n\n```python\ndef big():\n{body}\n```\n"
    _write_bundle(tmp_path, aux={"funcs.md": aux})
    errors = lint_all(load_all(tmp_path))
    assert any("funcs.md" in e and "exceeds 10 lines" in e for e in errors)


def test_lint_flags_aux_with_frontmatter(tmp_path: Path) -> None:
    _write_bundle(tmp_path, aux={"meta.md": "---\nid: nope\n---\n\nBody.\n"})
    errors = lint_all(load_all(tmp_path))
    assert any("meta.md" in e and "must not start with frontmatter" in e for e in errors)


def test_lint_flags_aux_bad_stem(tmp_path: Path) -> None:
    _write_bundle(tmp_path, aux={"Bad_Name.md": "# Aux\n\nBody.\n"})
    errors = lint_all(load_all(tmp_path))
    assert any("Bad_Name.md" in e and "stem must be lowercase" in e for e in errors)


def test_lint_flags_aux_unknown_skill_ref(tmp_path: Path) -> None:
    _write_bundle(tmp_path, aux={"refs.md": "# Aux\n\nSee skill:does-not-exist.\n"})
    errors = lint_all(load_all(tmp_path))
    assert any("refs.md" in e and "skill:does-not-exist" in e for e in errors)


def test_lint_clean_bundle_passes(tmp_path: Path) -> None:
    _write_bundle(tmp_path)
    assert lint_all(load_all(tmp_path)) == []
