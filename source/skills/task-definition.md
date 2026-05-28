---
id: task-definition
kind: skill
title: Task Definition
description: >
  Four disciplines for a pickup-ready task: a one-sentence Why naming a
  victim and a metric, a clear title, a single agreed estimate scale (no
  T-shirt/Fibonacci mixing), and acceptance criteria in Gherkin.
applies_when:
  - writing a backlog ticket, story, or task
  - defining a unit of work for someone else to pick up
  - standardizing titles, estimates, or acceptance criteria
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

# Task Definition

Four disciplines before a task enters the backlog: a stated **Why**, a clear
title, one estimate scale, Gherkin acceptance. Pickup is mechanical when
these hold.

Distinct from skill:requirements-crushing (implementer crushes a vague ask
at pickup) and skill:spec-driven-development (feature-level spec workflow).
This skill is the **upstream artifact**: the ticket itself. A ticket with a
sharp Why feeds a thin requirements-crushing pass; a ticket without one
forces the picker to reconstruct purpose from Slack archaeology.

## 1. Why — Purpose On The Card

Every ticket states **why it exists** before saying *what* to build or *how
big* it is. Two forms, both required:

- **`Why:` field** — peer of `Title` and `Estimate`. One sentence. Names
  **a victim** (who hurts without this) **and a metric** (what number moves,
  or what gain is lost). Visible in any backlog view without expanding the
  card.
- **Why paragraph in description** — expands the one-liner with context:
  source of the pain, link to the incident or research, why now rather than
  later. Sits above the Gherkin block. Free prose, kept short.

Same gate language as skill:requirements-crushing — the Why Gate flips a
brief to `Ready-to-Code: NO` for the same reasons that flip a ticket from
groomed to ungroomed. Single source of truth lives in that skill; this one
applies the rule at the upstream artifact.

Quick check:

| Why field | Verdict |
|---|---|
| `Free-tier users see a broken export button, generating 30 support tickets/week; goal: <5/week.` | groomed |
| `Improve the export experience.` | bounce — no victim, no metric |
| `Add CSV export field.` | bounce — paraphrases title |
| Blank | bounce — not ready for pickup |

Gherkin scenarios test **behavior**. The Why field tests **purpose**. Keep
them adjacent on the card; do not nest the Why inside `Feature:` or
`Scenario:` lines.

## 2. Clear Titles

- **Verb + object + context.** Imperative mood.
- ~60 char ceiling. Long → split.
- No vague nouns: "improvements", "stuff", "fixes".
- No "and" — two verbs = two tickets.
- Mention the surface if not obvious from project scope.

| Bad | Good |
|---|---|
| `Billing improvements` | `Add CSV export to billing dashboard` |
| `Fix and refactor cart` | `Fix cart total ignoring promo cap` (+ separate refactor ticket) |
| `Auth stuff` | `Block sign-in for soft-deleted users` |

## 3. Estimate — One Scale Per Team

Pick one scale. Stay there. **Mixing destroys velocity math** and turns
estimates into noise.

| Scale | Use when |
|---|---|
| T-shirt (XS, S, M, L, XL) | Early product, fuzzy domain, relative sizing only |
| Fibonacci (1, 2, 3, 5, 8, 13) | Mature backlog, points feed velocity, finer grain |

Rules either way:

- Estimate captures **effort + uncertainty**, not raw hours.
- `> XL` or `> 13` → split. Too big to plan.
- Re-estimate when scope changes; never keep a stale number.
- Don't translate hours into points to satisfy a process — re-estimate.

## 4. Description in Gherkin

Every acceptance criterion as `Given / When / Then`. One scenario per
criterion. `Background` for shared setup. Concrete values, not placeholders.

```gherkin
Feature: CSV export from billing dashboard

  Background:
    Given I am signed in as a paid user
    And the billing dashboard shows transactions for May 2026

  Scenario: Export current month
    When I click "Export CSV"
    Then a file billing-2026-05.csv downloads
    And it contains one row per transaction with columns date, amount, status

  Scenario: Anonymous user is blocked
    Given I am not signed in
    When I GET /billing/export.csv
    Then the response status is 401
```

- One outcome per scenario; multiple `Then` lines fine if they assert the
  same outcome.
- Edge cases get their own scenario, not a bullet inside prose.
- No "valid email", "appropriate response" — write the actual value.

## GOOD

```text
Why:      Paid users on the billing dashboard cannot export transactions to
          CSV; finance ops files ~30 tickets/week tagged "billing export".
          Goal: drop billing-export tickets to <5/week within one cycle.
Title:    Add CSV export to billing dashboard
Estimate: M           (team scale: T-shirt)
Description:
  Context: finance ops currently screenshots the dashboard table and retypes
  values into a spreadsheet. Export was deprioritized in Q1 but ticket
  volume has doubled since the May pricing change.

  Feature: CSV export from billing dashboard

    Scenario: Export current month
      Given I am signed in as a paid user
      When I click "Export CSV"
      Then billing-2026-05.csv downloads with date,amount,status columns

    Scenario: Anonymous request is blocked
      Given I am not signed in
      When I GET /billing/export.csv
      Then the response status is 401
```

Why names the victim (paid users, finance ops) **and** the metric (tickets/week,
target). Verb-led title. Single-scale estimate. Description expands the Why
above Gherkin. Acceptance is executable in a reviewer's head.

## BAD

```text
Why:      Improve the billing experience.
Title:    Billing stuff
Estimate: ~3 days, maybe 5 if hard
Description:
  Add export. Should work for paid users. Handle errors appropriately.
  Also clean up the dashboard a bit while we're in there.
```

Why paraphrases the title with a verb — no victim, no metric. Noun-phrase
title. Time estimate the team doesn't track in time. Prose acceptance with
"appropriately". Two scopes glued together.

## Red Flags

- `Why:` field blank or missing — ticket is not groomed; do not estimate yet.
- Why names a victim but no metric, or a metric but no victim.
- Why uses "improve", "better", "cleaner", "support" with no named person or
  measurable gain.
- Why paraphrases the title or restates the requested change.
- Why field longer than one sentence — expand in the description, not the field.
- Why nested inside `Feature:` / `Scenario:` instead of as its own field.
- Title is a noun phrase or ends in "improvements" / "updates" / "stuff".
- Title contains "and" — split it.
- Hours/days on a points team (or points on a T-shirt team).
- T-shirt and Fibonacci mixed in the same backlog.
- Description is prose paragraphs instead of `Given / When / Then`.
- Gherkin scenario with "valid X", "appropriate Y", or no concrete value.
- One ticket with three unrelated `Scenario:` blocks — separate tickets.
- `TBD` or "to be defined" in acceptance — task isn't ready for pickup.
- Estimate above the top bucket (`XL`, `13`) — must split before estimating.
