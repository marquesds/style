---
id: operational-repair-tasks
kind: skill
title: Operational Repair Tasks
description: >
  Named idempotent CLI tasks for post-deploy repair without DB surgery.
  Three archetypes: reanalyze (replay analysis), refresh (rebuild from
  snapshots), crossref (recompute relationships). Each idempotent, safe to
  rerun, documented with when-to-use guidance.
applies_when:
  - post-deploy data repair needed
  - logic changed and historical records need reprocessing
  - relationships between entities are stale or missing
  - on-call runbook references a repair command
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

# Operational Repair Tasks

Named commands let operators repair state without touching the DB directly.
Each task is idempotent, scoped, and documented.

## Three Archetypes

| Archetype | Does | When to use |
|---|---|---|
| `reanalyze` | Replays analysis logic over raw inputs | Analysis code changed; results stale |
| `refresh` | Rebuilds derived data from stored snapshots through current logic | Derived columns or caches are stale |
| `crossref` | Recomputes relationships between entities | References missing, broken, or never computed |

Use the right archetype. Running `reanalyze` when `crossref` is needed wastes
work and may produce wrong results.

## Idempotency Contract

Every repair task must satisfy: run once or run ten times — same outcome.

```python
def reanalyze(entity_id: EntityId, repo: EntityRepo) -> RepairResult:
    entity = repo.get(entity_id)
    analysis = analyze(entity.raw_input)
    repo.save_analysis(entity_id, analysis)
    return RepairResult(entity_id=entity_id, status="done")
```

`save_analysis` is an upsert, not an insert. Re-running does not duplicate rows.

## Scoping

Support a `--target` flag (single entity, cohort, or `--all`). Default to a
dry-run mode that logs what would change without writing. Operators verify
before running against the full corpus.

```python
def crossref(
    target: EntityId | Literal["all"],
    repo: EntityRepo,
    dry_run: bool = True,
) -> list[RepairResult]:
    entities = repo.all() if target == "all" else [repo.get(target)]
    return [_crossref_one(e, repo, dry_run) for e in entities]
```

## Observability

Log structured events per entity processed: `entity_id`, `archetype`, `status`,
`dry_run`. Emit a counter metric for repair tasks executed. Runbooks reference
the task by name — correlate logs by task name + run ID.

## Distinct from Migrations

Repair tasks do not change schema. They reprocess existing data through current
application logic. Schema changes use migrations (see skill:deprecation-and-migration).

## GOOD

```
# Replay analysis for one record
$ cli reanalyze --target entity-123 --dry-run
# Dry run shows: would update analysis_result for entity-123

$ cli reanalyze --target entity-123
# Updated analysis_result for entity-123
```

Named, documented, dry-runnable, idempotent. On-call can run safely without
author present.

## BAD

```python
# one-off script
db.execute("UPDATE entities SET analysis = NULL WHERE created_at < '2024-01-01'")
```

No name. No dry-run. Not idempotent (second run nulls already-fixed rows).
Not in source control as a durable tool. Not logged or measured.

## Red Flags

- Repair logic lives in a one-off script or a notebook, not a named CLI task.
- Task has no dry-run mode; operators cannot preview changes.
- Running the task twice produces duplicated rows or doubled values.
- No structured log per entity; impossible to audit which records were repaired.
- `crossref` used when `reanalyze` was needed; confuses cause and symptom.
