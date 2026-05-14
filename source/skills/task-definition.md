---
id: task-definition
kind: skill
title: Task Definition
description: >
  Three disciplines for a pickup-ready task: clear title, single agreed
  estimate scale (no T-shirt/Fibonacci mixing), acceptance criteria in
  Gherkin.
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

Three disciplines before a task enters the backlog: clear title, one estimate
scale, Gherkin acceptance. Pickup is mechanical when these hold.

Distinct from skill:requirements-crushing (implementer crushes a vague ask
at pickup) and skill:spec-driven-development (feature-level spec workflow).
This skill is the **upstream artifact**: the ticket itself.

## 1. Clear Titles

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

## 2. Estimate — One Scale Per Team

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

## 3. Description in Gherkin

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
Title:    Add CSV export to billing dashboard
Estimate: M           (team scale: T-shirt)
Description:
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

Verb-led title. Single-scale estimate. Acceptance is executable in a
reviewer's head.

## BAD

```text
Title:    Billing stuff
Estimate: ~3 days, maybe 5 if hard
Description:
  Add export. Should work for paid users. Handle errors appropriately.
  Also clean up the dashboard a bit while we're in there.
```

Noun-phrase title. Time estimate the team doesn't track in time. Prose
acceptance with "appropriately". Two scopes glued together.

## Red Flags

- Title is a noun phrase or ends in "improvements" / "updates" / "stuff".
- Title contains "and" — split it.
- Hours/days on a points team (or points on a T-shirt team).
- T-shirt and Fibonacci mixed in the same backlog.
- Description is prose paragraphs instead of `Given / When / Then`.
- Gherkin scenario with "valid X", "appropriate Y", or no concrete value.
- One ticket with three unrelated `Scenario:` blocks — separate tickets.
- `TBD` or "to be defined" in acceptance — task isn't ready for pickup.
- Estimate above the top bucket (`XL`, `13`) — must split before estimating.
