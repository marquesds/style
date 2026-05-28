---
id: requirements-crushing
kind: skill
title: Requirements Crushing
description: >
  Coding last. Crush ticket into crisp brief; brief leads with Why; gate on
  Ready-to-Code. Use when ask vague ("should", "support", "improve"),
  UX/business rule, or big blast radius.
applies_when:
  - incomplete or ambiguous request before implementation
  - user-facing, cross-team, compliance, or high-impact change
  - planning reveals unanswered product questions
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

# Requirements Crushing

Core idea: rework hurts. Nail requirement **before** diff explosion. Lead with
**Why** — purpose, cause, the pain we erase or the gain we unlock. A brief that
cannot name a victim or a measurable gain is not ready, regardless of how
detailed sections 6–9 look.

## When

Implement / fix / integrate / refactor / UX / business rule / tests from ticket — especially vague verbs. Big change + fuzzy goal → crush first. Large blast radius → crushing/planning should still cover the **Staff+/owner lens** in **rule:agent-workflow** (trade-offs, downside, opportunity cost—not product questions alone).

## Required Output

Emit **Requirements Crushing Brief**. Paste template once; fill compact.

```text
REQUIREMENTS CRUSHING BRIEF

1. Why (cause): one sentence — who hurts if we don't ship, or what gain is lost.
2. Original request:
3. Source: (see hierarchy below; note confidence + risk if unknown)
4. Confirmed understanding:
5. Open questions:
6. Flow sketch:
7. Test scenarios:
8. Edge cases:
9. Implementation walkthrough (outline only, no code):
10. Ready-to-Code: YES | NO
```

The **Why** field is the gate, not decoration. Sections 4–9 explain *how* and
*what*; without a sharp *why* they design the wrong thing precisely.

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

## Why Gate

`Ready-to-Code` is automatically **NO** when any of these hold:

- Section 1 is blank.
- Why takes more than one sentence — if you can't say it short, you don't know
  it yet.
- Why names no concrete victim and no measurable gain ("improve UX", "make it
  better", "fix the bug", "refactor for cleanliness"). State *who* is harmed
  or *what* metric moves.
- Why paraphrases the ticket title or restates the requested change ("Why: add
  export field" when the ticket is "Add export field").

Crush the Why first. Sections 4–9 are wasted effort on top of a blurry purpose.

## GOOD

```text
1. Why: paid users on the export page see a broken button — support gets
   ~30 tickets/week tagged "can't export". Goal: drop export-related tickets
   to <5/week.
4. Confirmed understanding: paid users see export button; free users hidden.
7. Test scenarios: paid toggles visible; free GET /export → 403.
8. Edge cases: grace period user = paid.
10. Ready-to-Code: YES
```

Why names the victim (paid users, support) and the gain (ticket drop).
Sections 4–9 build on a sharp purpose.

## BAD

```text
1. Why: improve the export experience.
10. Ready-to-Code: YES
```

No victim. No gain. Reads like the ticket title with a verb. Gate must flip
to **NO** until cause is concrete.

Ticket: "add export field" → immediate migration + column + UI. No source besides
ticket. No who's affected. `Ready-to-Code` skipped. Code before crush = redo loop.

## Red Flags

- Section 1 blank, vague, or paraphrasing the ticket title.
- Why uses "improve", "better", "cleaner", "support" with no named victim or metric.
- Why spans a paragraph instead of one sentence.
- Vague verb and zero clarifying questions.
- Single-source rumor treated as spec with no confidence note.
- Large diff while section 5 still long.
