---
id: requirements-crushing
kind: skill
title: Requirements Crushing
description: >
  Coding last. Crush ticket into crisp brief; gate on Ready-to-Code.
  Use when ask vague ("should", "support", "improve"), UX/business rule, or big blast radius.
applies_when:
  - incomplete or ambiguous request before implementation
  - user-facing, cross-team, compliance, or high-impact change
  - planning reveals unanswered product questions
agents:
  claude: { kind: skill }
  cursor: { kind: rule }
  codex:  { section: skills }
  openclaw: { section: skills }
  opencode: { kind: skill }
  pi:       { section: skills }
  vibe:   { kind: skill }
---

# Requirements Crushing

Core idea: rework hurts. Nail requirement **before** diff explosion.

## When

Implement / fix / integrate / refactor / UX / business rule / tests from ticket — especially vague verbs. Big change + fuzzy goal → crush first. Large blast radius → crushing/planning should still cover the **Staff+/owner lens** in **rule:agent-workflow** (trade-offs, downside, opportunity cost—not product questions alone).

## Required Output

Emit **Requirements Crushing Brief**. Paste template once; fill compact.

```text
REQUIREMENTS CRUSHING BRIEF

1. Original request:
2. Source: (see hierarchy below; note confidence + risk if unknown)
3. Problem / why:
4. Confirmed understanding:
5. Open questions:
6. Flow sketch:
7. Test scenarios:
8. Edge cases:
9. Implementation walkthrough (outline only, no code):
10. Ready-to-Code: YES | NO
```

## Source Hierarchy

Use top item that exists; downgrade if missing.

- Written ticket / issue / spec (highest)
- Design doc / RFC / ADR
- PM / stakeholder message (capture quote + date)
- Slack / email thread (link + summary)
- Code / prior PR as **only** clue → mark **low confidence**, spike separate from ship

Unknown source → state gap + **risk if wrong**.

## Rule

**No code** until `Ready-to-Code: YES`, unless human **explicitly** overrides **after** gaps listed in brief.

Override still needs recorded decision (even one-liner).

## GOOD

```text
10. Ready-to-Code: YES
4. Confirmed understanding: paid users see export button; free users hidden.
7. Test scenarios: paid toggles visible; free GET /export → 403.
8. Edge cases: grace period user = paid.
```

Brief short. Sources named. Tests + edges explicit. Gate green.

## BAD

Ticket: "add export field" → immediate migration + column + UI. No source besides ticket. No who's affected. No errors for anon. `Ready-to-Code` skipped.

Code before crush = redo loop.

## Red Flags

- Vague verb and zero clarifying questions.
- Single-source rumor treated as spec with no confidence note.
- Large diff while section 5 still long.
