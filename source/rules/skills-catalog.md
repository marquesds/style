---
id: skills-catalog
kind: rule
title: Skills Catalog
description: >
  Always-on index of every skill. Read catalog to match trigger; load exactly the
  matching skill body on demand. Never preload all skills at once.
always_apply: true
globs: "**/*"
agents:
  claude: { kind: rule }
  cursor: { kind: rule, glob: "**/*" }
  codex:  { section: rules }
  goose:  { section: rules }
  openclaw: { section: rules }
  opencode: { kind: rule }
  pi:       { section: rules }
  vibe:   { kind: rule }
---

# Skills Catalog

Catalog always loaded. Skill bodies loaded only on trigger match — never all at once.
Match the task to a row; load that one skill; follow it.

## Translate Examples to Your Stack

All skill examples are Python. Principles are language-agnostic. When working in
TypeScript, Rust, Elixir, Kotlin, etc., translate Python idioms to the target stack
(pattern matching, traits, sum types, OTP, coroutines) while keeping the semantic
guidance intact. Exception: skills whose topic is the language or format itself
(`bindings-as-thin-wrappers` for Rust FFI, `xss-and-csp` for HTML,
`task-runner-conventions` for Make, `design-aesthetic-commitment` for CSS).

## Catalog

| Skill ID | Load when |
|----------|-----------|
| agents-md-checklists | authoring an AGENTS.md file for a project |
| ai-collaboration-hygiene | guidelines for working alongside AI tools; attribution |
| ai-contribution-disclosure | disclosing AI-generated content in docs or PRs |
| api-and-interface-design | designing or changing a public interface, port, or API |
| architecture-haiku | very short architectural description needed |
| bindings-as-thin-wrappers | writing FFI or language bindings to a native library |
| bounded-context-mapping | slicing by bounded context; aggregate repos; ACL translators |
| bug-first-debugging | bug report — reproduce as failing test before any fix |
| caching-strategy | cache-aside vs write-through; key shape; TTL jitter; singleflight; event-driven invalidation |
| canonical-reference-in-docstrings | documenting an algorithm, protocol, or formula |
| ci-pipeline-design | fail-fast ordering; matrix discipline; cache hygiene; secrets in vault |
| caveman | ultra-compressed communication mode for token efficiency |
| centralized-ui-components | building UI components; enforcing one catalog source before page use |
| code-review-and-quality | reviewing a diff or PR across five axes |
| code-simplification | reducing complexity in tested code, one change at a time |
| compile-time-feature-flags | optional integrations or heavy deps behind build extras |
| concurrency-correctness | writing or reviewing concurrent code; shared state; locks |
| data-privacy-and-retention | handling PII, retention limits, or right-to-erasure |
| defensive-programming | hardening boundaries; validating untrusted input |
| definition-of-done | checking a change is truly done before push or merge |
| deprecation-and-migration | removing code or schema in a safe, two-step sequence |
| design-aesthetic-commitment | committing to a consistent visual design language |
| functional-core-imperative-shell | separating pure logic from I/O; effects at boundary |
| hexagonal-architecture | ports and adapters; dependency direction; feature slices |
| honest-limits-disclosure | documenting known constraints where readers look first |
| i18n-discipline | internationalizing strings, dates, numbers across locales |
| injection-defense | preventing SQLi, command, SSTI, or path traversal |
| integration-design | designing contracts between services or modules |
| jsonb-first-search | postgres jsonb + GIN for schema-fluid or search-heavy features |
| liskov-and-design-by-contract | subtype correctness; pre/post/invariants in types |
| llm-prompt-injection | untrusted text vs system instructions; tool and RAG boundaries |
| llm-system-design | designing systems that incorporate LLM calls |
| minimal-dependency-budget | justifying and auditing dependencies before adding |
| modular-file-as-feature-toggle | file-level module boundaries as a feature toggle seam |
| n-plus-one-prevention | detecting and eliminating N+1 query patterns |
| operational-repair-tasks | runbooks; break-glass procedures; on-call repair |
| owasp-top-ten | web security risk review against OWASP Top 10 2021 |
| password-hashing-storage | argon2id / bcrypt; salting; constant-time verify |
| pipeline-saga-orchestration | long-running workflows; sagas; compensating actions |
| pull-request-and-commit-style | conventional commits; small PRs; one logical change |
| queue-topology-design | message queue shape; fan-out; dead-letter; ordering |
| rate-limiting-and-throttling | token bucket vs sliding window; per-tenant dims; 429 + Retry-After; cost-based limits |
| refactoring | structural change without behavior change; legacy code without tests |
| requirements-crushing | crushing vague specs into a Ready-to-Code brief |
| resilience-retries | retries with backoff/jitter; idempotency; circuit breakers |
| restful-http-design | nouns, methods, versioning, RFC 7807 errors, cursor pagination |
| rollout-and-feature-flags | runtime toggles; gradual rollout; flag lifecycle |
| runnable-doc-examples | public API examples that execute as tests |
| secrets-never-in-repo | no credentials, tokens, or PEMs in VCS |
| snapshot-testing | snapshot / golden-file tests; when to use and update |
| source-driven-development | verify framework code against installed-version docs |
| spec-driven-development | spec before code; SPECIFY → PLAN → TASKS → IMPLEMENT |
| sql-antipatterns | relational traps: jaywalking, EAV, naive trees, keyless entry |
| sql-app-discipline | application-side SQL hygiene: pseudokeys, error handling, review, stored procs |
| sql-foreign-keys | foreign key implementation mistakes: direction, types, lifecycle, operational |
| sql-physical-design | physical design traps: money types, ENUM lookups, file storage |
| sql-query-antipatterns | query smells: NULL handling, GROUP BY, RAND(), LIKE, spaghetti, SELECT * |
| sql-query-performance | index shape, sargable predicates, keyset pagination |
| task-runner-conventions | Makefile / justfile conventions; standard task names |
| tdd | RED → GREEN → REFACTOR; Testing Trophy; Chicago school |
| threat-modeling | STRIDE per trust boundary; abuse cases; mitigations before the diff |
| test-design | what to test, how much, which doubles; afferent coupling |
| twelve-factor-app | cloud-native shape: codebase, deps, config, backing services, build/release/run, statelessness, disposability, parity, logs, admin tasks |
| unit-of-work-and-transactions | one UoW per use case; atomic boundary; outbox pattern |
| wide-events-and-cardinality | high-cardinality observability; wide events |
| xss-and-csp | reflected/stored/DOM XSS; context-aware encoding; CSP |

## How to Load

Skill name in catalog matches `~/.claude/skills/<id>/SKILL.md` (Claude),
`.cursor/rules/<id>.mdc` (Cursor), and the `## Skills` heading in `AGENTS.md`
(Codex, Goose, OpenClaw, Pi). `skill:<id>` references inside other rules resolve
via the lint cross-ref check. Load one skill at a time; never batch-load.

## GOOD

Bug report arrives in a Rust crate → catalog matches `bug-first-debugging` → load
that one skill → translate Python `pytest` examples to `cargo test` + `#[test]`
mentally → reproduce first, fix second.

## BAD

Preload every skill body before reading the request — context bloat, slower recall,
higher cost. Or refuse to apply a skill because the example is Python and the project
is Go.

## Red Flags

- Catalog row missing for a skill under `source/skills/` — lint will catch this.
- Five or more skills loaded speculatively before the task is understood.
- Agent ignored catalog and reinvented a skill's content from memory.
- Agent declined to apply a skill solely because the project language differs.
