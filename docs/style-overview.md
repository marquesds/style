# Style Overview

One-page philosophy behind the rules, skills, and commands in this repository.
Written in normal English for newcomers. The rule and skill files use caveman style
for token efficiency once an agent has loaded them.

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
- **Code is a liability.** Two-step removal. Reversible migrations. Deprecation markers
  carry a removal version.
- **Source-driven development.** Verify framework code against the docs of the version
  installed, not memory. Cite the URL.
- **Conventional Commits, small PRs, feature flags.** One logical change per PR,
  ~100 lines, body explains why. Risky changes ship behind a flag.

## How to read the rest of the repo

- `source/rules/` — eight always-on rules, including the `skills-catalog` index.
- `source/skills/` — on-demand expertise; see `source/rules/skills-catalog.md` for
  the navigable index with one-line triggers for all 56 skills.
- `source/commands/` — slash-command prompts.
- `docs/adr/` — architecture decision records explaining why specific choices were made.

## Why caveman voice

Once an agent has the practices in context, every additional token of preamble costs
real money and degrades recall. Caveman voice removes filler while preserving every
technical term, identifier, code block, and error string verbatim. Newcomers read
these documents in normal English; agents read the caveman versions.

See `docs/adr/0003-caveman-voice-for-rules.md` for the full reasoning.
