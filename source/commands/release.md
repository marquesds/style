---
id: release
kind: command
title: Release
description: >
  Bump version, update CHANGELOG, commit, tag, push. Hard stop if CHANGELOG
  is missing the next version entry or if tests fail.
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

Use skill:pull-request-and-commit-style, skill:task-runner-conventions.

Steps:

1. Read `CHANGELOG.md`. Confirm an entry exists for the version being released.
   If the entry is missing, **stop and report**. Do not proceed.
2. Determine the next version from the canonical version file: `pyproject.toml`,
   `package.json`, `Cargo.toml`, or `mix.exs`.
3. Run the bump script if one exists (`scripts/bump-version.sh` or equivalent task
   verb). Otherwise update the version field manually in the version file.
4. Update `CHANGELOG.md`: move the `[Unreleased]` section to a new version heading
   with today's date.
5. Run `<check-verb>` and `<test-verb>` (skill:task-runner-conventions). Both must pass.
6. Stage the version file(s) and `CHANGELOG.md`. Commit: `chore(release): vX.Y.Z`.
7. Tag: `git tag vX.Y.Z -m "vX.Y.Z"`.
8. Push commits and tags: `git push && git push --tags`.

Hard stops:
- If `CHANGELOG.md` is missing the next version entry, stop at step 1.
- If `<check-verb>` or `<test-verb>` fails, do not tag or push.
- If unrelated uncommitted working-tree changes are present, stash them or stop.
