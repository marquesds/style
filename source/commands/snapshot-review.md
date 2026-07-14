---
id: snapshot-review
kind: command
title: Snapshot Review
description: "Read pending snapshot diffs, classify each as intended or unintended, accept intentional only. Never bulk-accept. Hard stop on any unintended diff."
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

Use skill:snapshot-testing.

Steps:

1. List all pending snapshot diffs. Tooling by stack:
   - Rust: `cargo insta review --unreview`
   - JS / TS: `vitest --reporter=verbose` or `jest --verbose`
   - Python: `pytest --snapshot-update --dry-run` (or equivalent for installed library)
2. For each snapshot diff, show:
   - Test name and snapshot file.
   - The diff (before → after).
3. Classify each diff as one of:
   - **Intended** — behavior changed deliberately; update is correct.
   - **Unintended** — output changed unexpectedly; investigate before accepting.
4. Accept only diffs classified as **Intended**, one at a time.
5. For each **Unintended** diff, **stop and report** the test name and the unexpected
   change. Do not accept any further diffs until root cause is understood.
6. After accepting all intended diffs, run the full test suite to confirm no
   remaining failures.

Hard stops:
- If any diff is unintended, stop and report. Do not proceed to remaining diffs.
- If `--update-snapshots` (or equivalent) ran without this review, reject
  the bulk update and undo it.
