---
id: skills-catalog
kind: rule
title: Skills Catalog
description: "Always-on index of every skill. Read catalog to match trigger; load exactly the matching skill body on demand. Never preload all skills at once."
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
| accessibility-and-inclusive-ui | building or reviewing a frontend UI; adding a form, modal, or interactive widget; auditing keyboard or screen-reader support |
| agents-md-checklists | authoring an AGENTS.md file for a project |
| ai-collaboration-hygiene | reviewing AI-generated code before merging; deciding what to delegate to AI; setting AI contribution policy |
| api-and-interface-design | designing or changing a public interface, port, or API |
| architecture-haiku | very short architectural description needed |
| bindings-as-thin-wrappers | writing FFI or language bindings to a native library |
| bounded-context-mapping | dividing a large domain into bounded subdomains or services; designing how separate modules or contexts communicate |
| bug-first-debugging | bug report — reproduce as failing test before any fix |
| caching-strategy | adding a cache layer to a feature; choosing a cache strategy; cache invalidation or TTL design; Redis or in-process LRU |
| capacity-and-cost-engineering | sizing infrastructure for launch; planning capacity for peak load; setting up cost budgets or guardrails; running a load test |
| canonical-reference-in-docstrings | documenting an algorithm, protocol, or formula |
| ci-pipeline-design | designing or improving a CI/CD pipeline; setting up or modifying GitHub Actions or CI configuration |
| centralized-ui-components | building UI components; enforcing one catalog source before page use |
| code-review-and-quality | reviewing a diff or PR across six axes |
| code-simplification | reducing complexity in tested code, one change at a time |
| compile-time-feature-flags | making a dependency or integration optional at build time; shipping a minimal variant without heavy optional deps |
| concurrency-correctness | writing or reviewing concurrent code; shared state; locks |
| data-privacy-and-retention | handling PII, retention limits, or right-to-erasure |
| data-quality-and-analytics | adding a tracking event or product metric; building or reviewing an analytics dashboard; changing a metric definition; auditing data lineage |
| defensive-programming | hardening boundaries; validating untrusted input |
| definition-of-done | checking a change is truly done before push or merge |
| deprecation-and-migration | removing, replacing, or retiring a feature, API endpoint, database column, or module |
| design-aesthetic-commitment | committing to a consistent visual design language |
| functional-core-imperative-shell | separating pure logic from I/O; effects at boundary |
| hexagonal-architecture | slicing top-level packages by feature; defining a feature's public facade; placing a small hexagon (domain, ports, adapters) inside each feature |
| honest-limits-disclosure | documenting known constraints where readers look first |
| i18n-discipline | internationalizing strings, dates, numbers across locales |
| incident-response-and-postmortem | production incident in flight; writing a postmortem after an outage; defining severity tiers or on-call escalation |
| injection-defense | preventing SQLi, command, SSTI, or path traversal |
| integration-design | designing contracts between services or modules |
| jsonb-first-search | postgres jsonb + GIN for schema-fluid or search-heavy features |
| liskov-and-design-by-contract | designing an inheritance hierarchy or protocol; checking that a subclass or implementation is safe to substitute for its base type |
| llm-prompt-injection | untrusted text vs system instructions; tool and RAG boundaries |
| llm-system-design | designing systems that incorporate LLM calls |
| minimal-dependency-budget | justifying and auditing dependencies before adding |
| modular-file-as-feature-toggle | splitting a codebase into optional capability modules; building variant products (paid vs free, mutable vs immutable) from a single source |
| n-plus-one-prevention | detecting and eliminating N+1 query patterns |
| operational-repair-tasks | writing a CLI repair command or runbook for on-call; designing a post-deploy data fix; creating idempotent repair tooling |
| owasp-top-ten | web security risk review against OWASP Top 10 2021 |
| password-hashing-storage | implementing user authentication; storing or verifying passwords; choosing a password hashing algorithm |
| pipeline-saga-orchestration | designing a multi-step workflow that must survive deploys or partial failures; implementing a durable background job, saga, or compensating transaction |
| pull-request-and-commit-style | writing a commit message or PR description; preparing a change for code review |
| python-best-practices | writing or reviewing Python code; choosing Python idioms, data structures, type hints, or a concurrency model |
| queue-topology-design | adding background jobs or workers; designing a message queue setup; choosing queue concurrency, dead-letter, or worker isolation |
| rate-limiting-and-throttling | adding rate limiting to an endpoint or API; protecting a service from abuse, overuse, or noisy tenants |
| refactoring | structural change without behavior change; legacy code without tests |
| requirements-crushing | starting any implementation task before code; asking to grill, refine, or clarify requirements; open questions block Ready-to-Code; user invoked blind mode |
| resilience-retries | handling failures in outbound HTTP or queue calls; adding retry logic; making a service resilient to downstream failures |
| restful-http-design | designing or reviewing an HTTP API; adding or changing endpoints, versioning, status codes, or pagination |
| rollout-and-feature-flags | safely shipping a risky or partial feature; adding a kill switch or feature flag; managing gradual rollout to users |
| runnable-doc-examples | public API examples that execute as tests |
| secrets-never-in-repo | no credentials, tokens, or PEMs in VCS |
| snapshot-testing | snapshot / golden-file tests; when to use and update |
| source-driven-development | verify framework code against installed-version docs |
| spec-driven-development | creating or updating a design, technical specification, implementation plan, feature, module, or architectural decision |
| sql-antipatterns | relational traps: jaywalking, EAV, naive trees, keyless entry |
| sql-app-discipline | application-side SQL hygiene: pseudokeys, error handling, review, stored procs |
| sql-foreign-keys | foreign key implementation mistakes: direction, types, lifecycle, operational |
| sql-physical-design | physical design traps: money types, ENUM lookups, file storage |
| sql-query-antipatterns | query smells: NULL handling, GROUP BY, RAND(), LIKE, spaghetti, SELECT * |
| sql-query-performance | optimizing a slow query; adding or evaluating indexes; reviewing query execution plan shape |
| task-definition | writing a backlog ticket, story, or task for someone else to pick up; standardizing task titles, estimates, or acceptance criteria |
| task-runner-conventions | Makefile / justfile conventions; standard task names |
| tdd | implementing new features, functions, or modules; writing any new code; adding behavior to the codebase |
| threat-modeling | designing a feature that crosses trust boundaries; security review before implementing auth, data handling, or external integrations |
| test-design | designing a test strategy; writing regression, contract, or behavior tests; choosing test levels or doubles |
| twelve-factor-app | designing or auditing a cloud-native service for production readiness; configuring environment-based config, logging, or deployment |
| unit-of-work-and-transactions | writing a use case that touches multiple repositories or needs an atomic DB transaction; designing event publishing alongside a DB write |
| wide-events-and-cardinality | adding observability to a service; designing structured logging or metrics; setting up SLOs or alerting |
| xss-and-csp | reflected/stored/DOM XSS; context-aware encoding; CSP |

## How to Load

Skill name in catalog matches `~/.claude/skills/<id>/SKILL.md` (Claude),
`.cursor/skills/<id>/SKILL.md` (Cursor), `.agents/skills/<id>/SKILL.md`
(Codex), and the `## Skills` heading in `AGENTS.md` (Goose, OpenClaw, Pi).
`skill:<id>` references inside other rules resolve via the lint cross-ref check.
Load one skill at a time; never batch-load.

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
