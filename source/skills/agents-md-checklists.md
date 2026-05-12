---
id: agents-md-checklists
kind: skill
title: AGENTS.md Checklists
description: >
  Explicit ordered checklists per change type in AGENTS.md. Agents run them without
  prompting. Four kinds: after any code change, after a new feature, before a PR,
  after a bug fix.
applies_when:
  - writing or reviewing AGENTS.md / CLAUDE.md
  - onboarding a new agent to a repo
  - agent output is inconsistent or incomplete
agents:
  claude: { kind: skill }
  cursor: { kind: skill }
  codex:  { section: skills }
  goose:  { section: skills }
  openclaw: { section: skills }
  opencode: { kind: skill }
  pi:       { section: skills }
  vibe:   { kind: skill }
---

# AGENTS.md Checklists

Explicit ordered checklists per change type. Agents run them without prompting.

## The Four Checklists

Embed in `AGENTS.md` (or `CLAUDE.md`, `CURSOR.md`, etc.). Each checklist is ordered;
earlier steps must pass before later ones.

### After Any Code Change

1. `<fmt-verb>` — format all code.
2. `<check-verb>` — lint + type check.
3. `<test-verb>` — full test suite, no shortcuts.

### After a New Feature

1. All steps from "After any code change."
2. New behavior covered by tests.
3. Docs updated if a user-facing surface changed.
4. Examples updated if public API changed (skill:runnable-doc-examples).
5. Relevant skills or references noted in PR description.

### Before Opening a PR

1. All steps from "After any code change."
2. `<fmt-verb> --check` (pedantic mode, not just run).
3. Verify examples still run and produce expected output.
4. PR description filled: context, why, test plan (skill:pull-request-and-commit-style).

### After a Bug Fix

1. Reproduction test added; confirmed to fail before the fix.
2. Fix applied; reproduction test now passes.
3. Full test suite green.
4. PR description references the regression test.

## Reference Task Verbs

Checklists reference task verbs, not raw commands (skill:task-runner-conventions).
When the test runner changes, update the task file; checklists stay stable.

## GOOD

```markdown
# AGENTS.md

## After any code change
1. `mask fmt`
2. `mask check`
3. `mask test`

## Before opening a PR
1. `mask fmt --check`
2. `mask check`
3. `mask test`
4. Fill PR template (context, why, test plan)
```

Short. Unambiguous. Agent can execute without interpretation.

## BAD

```markdown
Make sure the code is well-tested and formatted before submitting.
```

No steps. No order. Agent decides what "well-tested" means. Results are inconsistent.

## Red Flags

- `AGENTS.md` has prose guidance but no ordered checklist.
- Checklist references raw commands instead of task verbs.
- "After bug fix" checklist missing the regression test step.
- No "Before PR" entry; agent pushes without a pedantic check.
- Checklist is aspirational ("should test") rather than imperative ("run `mask test`").
