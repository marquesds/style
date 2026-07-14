---
id: requirements-crushing
kind: skill
title: Requirements Crushing
description: "Coding last. Crush ticket into crisp brief; brief leads with Why; gate on Ready-to-Code. Use before every implementation task; hard-stop on unanswered questions by asking the next blocking question unless the human writes blind mode."
applies_when:
  - starting any implementation task before writing code
  - open questions block Ready-to-Code
  - user asks to grill, refine, or clarify requirements before coding
  - user invokes blind mode after unanswered questions
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

Implement / fix / integrate / refactor / UX / business rule / tests from ticket
→ crush first. Trivial, unambiguous work may use **Micro-Brief**. Big change +
fuzzy goal → full brief. Large blast radius → include the **Staff+/owner lens**
in **rule:agent-workflow** (trade-offs, downside, opportunity cost).

## Required Output

Emit **Requirements Crushing Brief**. Paste template once; fill compact. When
`Ready-to-Code` is **NO**, end with `NEXT QUESTION` and stop.

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
NEXT QUESTION: <one blocking question + recommended answer>
```

The **Why** field is the gate, not decoration. Sections 4–9 explain *how* and
*what*; without a sharp *why* they design the wrong thing precisely.

### Micro-Brief

Use only for trivial, unambiguous work. Emit 2–3 lines:

```text
MICRO REQUIREMENTS BRIEF
Why: <one sentence with victim or measurable gain>
Ready-to-Code: YES
```

Any open question, product branch, unclear source, or non-trivial behavior
upgrades the task to the full brief.

## Source Hierarchy

Use top item that exists; downgrade if missing.

- Written ticket / issue / spec (highest)
- Design doc / RFC / ADR
- PM / stakeholder message (capture quote + date)
- Slack / email thread (link + summary)
- Code / prior PR as **only** clue → mark **low confidence**, spike separate from ship

Unknown source → state gap + **risk if wrong**.

## Rule

**No code** until `Ready-to-Code: YES`. If Section 5 has unanswered questions,
ask the next blocking question in `NEXT QUESTION`, then stop and do nothing else
until the human answers.

Do not scaffold, edit the "safe parts", or proceed on silent assumptions. The
only override is the human writing **`blind mode`** after the gaps are listed.

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

## Grill the Open Questions

Section 5 is not a parking lot — it is the interview queue. Empty it before the
gate flips. Interview the human about every unresolved branch until
understanding is shared.

- Ask one blocking question per turn in `NEXT QUESTION`. It must be the final
  line of the response.
- Do not dump a questionnaire and proceed. Batched questions get skimmed;
  serial answers expose dependencies between decisions.
- Walk the decision tree. Resolve the branch a later question depends on first.
- Recommend one answer in the question. A bare question offloads thinking; a
  recommendation moves the decision forward and surfaces disagreement fast.
- Explore the codebase instead of asking when the answer lives there. Asking
  a human what the code already states is a red flag (rule:agent-workflow).

`Ready-to-Code` stays **NO** while any grilled branch is open. The next agent
turn updates the brief from the human answer, asks the next blocking question if
one remains, or flips to **YES**.

## Blind Mode

Blind mode is the per-task override for unanswered questions. It starts only
when the human writes **`blind mode`** after the open questions are visible.

Before editing, record each skipped question and the AI-recommended answer:

```text
BLIND MODE DECISION
- Q: <question> -> Assumed: <recommendation>
```

Any PR created from blind-mode work must include:

```text
## Blind Mode Disclosure
Open questions were not answered; implementation follows AI-suggested answers.
- Q: <question> -> Assumed: <AI recommendation>
```

Blind mode ends when the current task ends. The next task gates again.


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
- Editing after unanswered questions without `blind mode`.
- PR from blind-mode work missing the disclosure block.
