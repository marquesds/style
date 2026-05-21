# Style Overview

One-page philosophy behind the rules, skills, and commands in this repository.
The source files use concise technical prose: brief, direct, and readable.

## What this is

A single source of truth for my coding style, distributed as native files for any
AI coding agent. Clone the repo, run `./install.sh`, and the same practices appear
in every agent you use.

## What this is not

It is not a framework. It does not lock you into a stack, a directory layout, or a
language. It describes responsibilities and trade-offs so that the choice of
`Protocol` vs `interface` vs `trait` falls naturally out of whichever language is
in front of you.

## The practices

- **Test-driven development.** Write a failing test for the next behavior, then write
  the smallest implementation that makes it pass, then refactor. Default shape is the
  Testing Trophy: thick integration tests on real seams, focused unit tests for pure
  logic, few end-to-end tests for critical journeys.
- **Bug-first debugging.** Reproduce the bug as a failing test before touching
  production code. The fix follows. The test stays as a regression guard.
- **Changed-surface manual proof.** Before calling work done, manually exercise every
  changed user/operator-visible surface. Record exact steps and observed results in
  the final response and PR test plan.
- **Minimal hexagonal architecture.** Domain depends on nothing. Adapters depend on
  domain ports. Dependency direction always points inward.
- **Functional core, imperative shell.** Pure functions hold logic. Effects live at
  the boundary and are postponed until the last possible step.
- **Liskov first.** Encode contracts in the type system; use runtime asserts and
  property tests where types fall short.
- **RESTful HTTP.** Nouns plural, URL versioning, RFC 7807 errors, cursor pagination,
  idempotency keys for non-idempotent POSTs.
- **Unit of Work for transactions.** One UoW per use case. Outbox event in the same
  transaction. External effects after commit, not inside.
- **Observability is non-negotiable.** Three pillars (logs, traces, metrics),
  correlation IDs, structured logs at every state change, no PII.
- **Privacy by design.** Minimize collection, declare purpose and lawful basis,
  enforce retention, honor subject rights. Covers GDPR, LGPD, CCPA, PIPEDA,
  POPIA, APPI, PDPA. Opt out only with a dated ADR.
- **Code is a liability.** Two-step removal. Reversible migrations. Deprecation markers
  carry a removal version.
- **Source-driven development.** Verify framework code against the docs of the version
  installed, not memory. Cite the URL.
- **Conventional Commits, small PRs, feature flags.** One logical change per PR,
  ~100 lines, body explains why. Risky changes ship behind a flag.

## How to read the rest of the repo

- `source/rules/` — nine always-on rules, including `privacy-by-design` and the
  `skills-catalog` index.
- `source/skills/` — on-demand expertise; see `source/rules/skills-catalog.md` for
  the navigable index with one-line triggers. Skills are grouped loosely by family:

  | Family | Skills |
  |--------|--------|
  | Core design | functional-core-imperative-shell, hexagonal-architecture, bounded-context-mapping, liskov-and-design-by-contract, unit-of-work-and-transactions |
  | Testing | tdd, test-design, bug-first-debugging, snapshot-testing |
  | HTTP / API | restful-http-design, api-and-interface-design, rate-limiting-and-throttling |
  | Frontend / UX | centralized-ui-components, design-aesthetic-commitment, accessibility-and-inclusive-ui, i18n-discipline |
  | Data / SQL | sql-antipatterns, sql-query-performance, sql-foreign-keys, sql-physical-design, sql-query-antipatterns, sql-app-discipline, jsonb-first-search, data-quality-and-analytics |
  | Security | owasp-top-ten, injection-defense, xss-and-csp, secrets-never-in-repo, password-hashing-storage, llm-prompt-injection, threat-modeling |
  | Performance / reliability | n-plus-one-prevention, resilience-retries, caching-strategy, queue-topology-design, pipeline-saga-orchestration, capacity-and-cost-engineering |
  | Operations / delivery | ci-pipeline-design, rollout-and-feature-flags, deprecation-and-migration, observability, wide-events-and-cardinality, incident-response-and-postmortem |
  | Process / workflow | requirements-crushing, spec-driven-development, task-definition, code-review-and-quality, pull-request-and-commit-style, definition-of-done, refactoring |

- `source/commands/` — slash-command prompts: `/spec`, `/plan`, `/tdd`, `/bug`,
  `/review`, `/done`, `/commit`, `/threat-model`, `/refactor`, and more.
- `docs/adr/` — architecture decision records explaining why specific choices were made.

## Why concise prose

Once an agent has the practices in context, every extra token of preamble costs
money and adds noise. The harness still removes filler, hedging, and throat-clearing,
but it no longer requires full caveman grammar. Concise normal prose keeps the token
budget low while preserving sequence, danger, and ownership where those details
matter.

See `docs/adr/0012-concise-technical-prose-for-agent-sources.md` for the current
decision. ADR-0003 records the earlier caveman default.
