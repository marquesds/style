# ADR-0011 — Privacy opt-out for the style harness itself

**Status:** Accepted
**Date:** 2026-05-15
**Scope:** `repo: style-harness` (this repository only — does **not** apply to
projects that install the harness)
**Owner:** Lucas Marques (maintainer)
**Reversal trigger:** harness collects, stores, or processes any data about
end-users or contributors beyond Git commit metadata
**`review_by:`** 2027-05-15

## Context

`rule:privacy-by-design` is always-on across every project that installs the
style harness. The harness itself is contributor tooling: it ingests no end-user
data, persists nothing, and ships zero runtime services. Applying the rule's
mechanical clauses (retention windows, DSR pipelines, residency tags, DPIA
checks) to its own source tree would be theater.

The rule mandates that any opt-out must be a dated ADR with named scope, owner,
and reversal trigger. This ADR is that record for the harness.

## Decision

The style harness repository (`marquesds/style`) operates under a documented
opt-out from `rule:privacy-by-design`'s implementation clauses on the grounds
that the repository:

- Stores no personal data of any kind.
- Has no end-users in the data-subject sense — only contributors interacting
  via Git and GitHub, whose data is governed by GitHub's own DPA.
- Ships no runtime that could collect, log, or transmit personal data.
- Builds files; it does not process data subjects.

The **principles** of the rule (minimization, purpose limitation, accountability)
still inform contributor practice. The **mechanics** (retention enum, DSR state
machine, audit log, residency tags) do not apply.

## Consequences

- Lint and review do not require privacy-related fields in new harness code.
- Any future change that introduces telemetry, analytics, contributor account
  state, hosted runtime, or third-party data processor automatically voids this
  opt-out per the reversal trigger above. A new ADR superseding this one is
  required before that change merges.
- Projects that **install** the harness do **not** inherit this opt-out. Each
  consuming project author its own ADR if they want one, scoped to their repo.
- This ADR is reviewed annually (`review_by:` above). Expired ADR = invalid
  opt-out per `rule:privacy-by-design`.
