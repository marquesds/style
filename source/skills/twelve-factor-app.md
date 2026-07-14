---
id: twelve-factor-app
kind: skill
title: Twelve-Factor App
description: "Cloud-native shape for SaaS services. Ten of the twelve factors that still earn their keep, with cross-refs to deeper skills. Navigation layer only."
applies_when:
  - new service shape
  - production readiness review
  - containerizing a service
  - cloud deploy planning
  - scaling or ops review
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

# Twelve-Factor App

Navigation layer. Cloud-native shape for SaaS apps. Source: https://12factor.net (Heroku, 2017).
Deeper skills: skill:secrets-never-in-repo, skill:minimal-dependency-budget,
skill:operational-repair-tasks, skill:wide-events-and-cardinality, rule:observability.

## I. Codebase

**One repo per app. Many deploys from the same code; differ only by config.**
Shared code extracted to a library, not copied across repos. Version control tracks
every deploy candidate.

## II. Dependencies

**Declare + lock; isolate.** Lockfile committed; no implicit system-wide deps assumed.
Container or venv enforces isolation so `works on my machine` never ships.
Drill: skill:minimal-dependency-budget.

## III. Config

**Env vars or secret manager — never source.** Structured config files OK when loaded
at runtime from a config/secret store, not baked into the image. Test: can you open-source
the codebase without exposing credentials? Drill: skill:secrets-never-in-repo.

## IV. Backing services

**Postgres, Redis, S3, SMTP — attached resources addressed by URL or config.**
Swap dev↔prod via config; no code change. Failover = config change. Local and
third-party services treated identically by the app.

## V. Build, release, run

**Three immutable stages.** Build = artifact (image/binary). Release = artifact +
config + release id. Run = process(es). Rollback = redeploy a prior release id;
never edit a live release. Config changes require a new release.

## VI. Processes

**Stateless, share-nothing.** Memory and local disk = ephemeral cache only.
Sticky sessions banned; session state lives in a backing store (Redis, DB).
Horizontal scale = add workers, no coordination required.

Subsumes the surviving spirit of factor VIII: pick a concurrency primitive
(threads, async, processes, lambdas) that fits the runtime. The prescription
for Unix process forking is dated; the stateless-scale principle is not.

## IX. Disposability

**Fast boot, graceful SIGTERM, crash-only safe.** Worker stops accepting work,
finishes in-flight requests within the shutdown grace window, exits. Crash
mid-write recovers via idempotent re-run. Drill: skill:resilience-retries,
skill:unit-of-work-and-transactions.

## X. Dev/prod parity

**Same backing service types across envs.** Postgres in prod → Postgres in dev,
not SQLite. Container parity closes the "it worked locally" gap. Deploy daily;
keep time, tool, and personnel gaps small.

## XI. Logs

**Stdout as event stream.** App writes structured events to stdout; infra aggregates,
routes, and stores them. App never manages log files, log rotation, or log shipping.
Drill: skill:wide-events-and-cardinality, rule:observability.

## XII. Admin processes

**Migrations, backfills, REPL — one-off processes run under the same release artifact
and config as the app.** Never apply migrations via an ad hoc shell session against
prod. Drill: skill:operational-repair-tasks, skill:deprecation-and-migration.

## What's outdated

- **VII Port binding** — platform-managed today (k8s, Fargate, Lambda). The principle
  (app self-contained, not injected into a container) is implied by V/VI; the literal
  port-binding prescription adds nothing for most teams.
- **VIII Concurrency (Unix process model)** — prescriptive process forking is dated.
  The stateless horizontal-scale spirit is folded into VI above.

## GOOD

```text
Image built once in CI; promoted to staging then prod without rebuild.
DATABASE_URL injected at deploy; same Postgres version in dev and prod.
SIGTERM handler drains in-flight requests within 30s then exits cleanly.
Migration runs as a one-off job under the same release artifact before traffic shifts.
Structured JSON events written to stdout; collector aggregates them.
```

## BAD

```text
Config baked into the image — different image per env.
SQLite in dev, Postgres in prod — surprise schema divergence at launch.
`session_data` stored in worker process memory — sticky sessions required.
Migration applied via ad hoc psql session in production shell.
App writes and rotates log files; logs lost on container restart.
```

## Red Flags

- Different image built per environment.
- `.env.production` committed to the repo.
- App reads or rotates log files instead of writing to stdout.
- Worker holds session state in process memory (sticky sessions needed).
- Migration applied via ad hoc shell session, not a release artifact.
- Dev runs SQLite; prod runs Postgres.
- No graceful SIGTERM handler; data corruption on rolling deploy.
- Credentials hard-coded in source, not injected at runtime.
