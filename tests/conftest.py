from __future__ import annotations

import sys
from pathlib import Path
from textwrap import dedent

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


AUX_SENTINEL = "py-bundle-aux-sentinel"


def _write_bundle(root: Path) -> None:
    """Multi-file skill bundle: SKILL.md plus one auxiliary reference file."""
    bundle = root / "skills" / "py-bundle"
    bundle.mkdir(parents=True)
    (bundle / "SKILL.md").write_text(
        dedent(
            """\
            ---
            id: py-bundle
            kind: skill
            title: Py Bundle
            description: "Python idioms router with reference files."
            applies_when:
              - python idiom lookup
            agents:
              claude: { kind: skill }
              cursor: { kind: skill, glob: "**/*.py" }
              codex:  { section: skills }
              goose:  { section: skills }
              openclaw: { section: skills }
              opencode: { kind: skill }
              pi:       { section: skills }
              vibe:   { kind: skill }
            ---

            # Py Bundle

            Index: see data-model.md for data structures.

            ## GOOD

            ```python
            x = [i for i in range(3)]
            ```

            ## BAD

            ```python
            y = list(map(lambda i: i, range(3)))
            ```
            """
        ),
        encoding="utf-8",
    )
    (bundle / "data-model.md").write_text(
        f"# Data Model\n\n{AUX_SENTINEL}\n\nPlain markdown reference file.\n",
        encoding="utf-8",
    )


@pytest.fixture
def fake_source_dir(tmp_path: Path) -> Path:
    """Tiny source/ tree covering all three kinds and every agent."""
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
            description: "Production code: max 200 lines. Docs and tests are exempt."
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
            description: "Test fail first. Code second."
            applies_when:
              - new logic
            agents:
              claude: { kind: skill }
              cursor: { kind: skill, glob: "**/*.py" }
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
    _write_bundle(root)
    (root / "commands" / "tdd.md").write_text(
        dedent(
            """\
            ---
            id: tdd
            kind: command
            title: Start TDD cycle
            description: "Kick off RED-GREEN-REFACTOR for the current target."
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
