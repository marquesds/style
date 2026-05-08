# Style Overview

This document is the one-page version of the philosophy behind my rules, skills, and commands in this repository. It is written in normal English so newcomers can read it quickly. The rule and skill files themselves are written in caveman style for token efficiency once an agent has loaded them.

## What this is

A single source of truth for my coding style, distributed as native files for any AI coding agent: Claude Code, Cursor, Codex, Goose, OpenClaw, OpenCode, Pi, and Vibe. You clone the repo, run `./install.sh`, and the same practices appear in every agent you use.

## What this is not

It is not a framework. It does not lock you into a stack, a directory layout, or a language. It describes responsibilities and tradeoffs so that the choice of `Protocol` vs `interface` vs `trait` falls naturally out of whichever language is in front of you.

## The practices, in plain English

**Test-driven development.** Write a failing test for the next behavior, then write the smallest implementation that makes it pass, then refactor while the test keeps you honest. Tests are how I prove the code does what it claims; they come first, not last.

**Bug-first debugging.** A bug report is not a fix request, it is a "reproduce this" request. The first artifact when a bug is reported is a failing test that pins the bug. The fix follows. The test stays as a regression guard, tagged so future readers can find it.

**Minimal hexagonal architecture.** The domain knows nothing about its surroundings; adapters know about the domain. I name the layers however the language and project want, but the dependency direction always points inward toward pure business rules.

**Functional core, imperative shell.** Pure functions over plain data hold the logic. The shell at the boundary calls into the core, then performs I/O. Tests on the core require no mocks. Effects are postponed until the last possible step.

**Liskov first.** Substitutability is the SOLID principle that earns its keep. I encode contracts (preconditions, invariants, postconditions) in the type system whenever the language allows; I use runtime asserts and property tests when types fall short. Subclasses that throw `NotImplementedError` are not subtypes.

**RESTful HTTP.** Nouns plural, methods over verbs, URL versioning, RFC 7807 problem+json bodies for errors, cursor pagination, ETags for conditional requests, idempotency keys for non-idempotent POSTs. Predictable shape across services.

**Unit of Work for transactions.** Each use case opens one unit of work, registers repository writes inside it, persists the outbox event in the same transaction, and only then commits. External effects (emails, webhooks) fire after commit, never inside, and dispatch via the outbox to keep delivery at-least-once.

**Observability is non-negotiable.** Three pillars (logs, traces, metrics), correlation IDs propagated through every boundary, structured logs at every state change, no PII. A new endpoint without a span and a counter is not done.

**Code is a liability.** Less code beats more code. Two-step removal (stop using, then delete). Migrations are reversible; data backfills live in their own files. Deprecation markers carry a removal version.

**Source-driven development.** I verify framework code against the official docs of the version installed, not against memory. Every nontrivial framework decision cites a URL.

**Conventional Commits, small PRs, feature flags when applicable.** One logical change per PR, target around 100 lines, body of the commit message explains why. Risky or partial changes ship behind a flag with a removal date.

## How to read the rest of the repo

- `source/rules/` — always-on guidance. Seven files: agent workflow, subagent-first, code quality, design principles, documentation, observability, reuse and idioms.
- `source/skills/` — on-demand expertise. Twenty-eight files covering everything described above.
- `source/commands/` — slash-command prompts that engage one or more skills (`/spec`, `/plan`, `/tdd`, `/bug`, `/review`, `/done`, `/commit`).
- `scripts/` — the loader, lint, build orchestrator, and per-agent adapters.
- `tests/` — snapshot tests for the build pipeline.
- `docs/adr/` — short architecture decision records explaining why specific choices in this repo are the way they are.

## Why caveman voice

Once an agent has the practices in context, every additional token of preamble costs real money and degrades the agent's recall. Caveman voice removes filler while leaving every technical term, identifier, code block, and error string verbatim. Newcomers read these documents (in normal English); agents read the caveman versions.

Read the ADR (`docs/adr/0003-caveman-voice-for-rules.md`) for the full reasoning.
