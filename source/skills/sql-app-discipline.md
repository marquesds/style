---
id: sql-app-discipline
kind: skill
title: SQL App Discipline
description: >
  Application-side SQL hygiene: surrogate key gaps are normal, handle DB
  errors explicitly, SQL in version control, stored procs only where earned.
applies_when:
  - surrogate key renumbering
  - error handling with DB calls
  - SQL outside version control
  - stored procedure decisions
agents:
  claude: { kind: skill }
  cursor: { kind: skill, glob: "**/*.{sql,ddl,psql,pgsql},**/migrations/**/*,**/schema.prisma" }
  codex:  { section: skills }
  goose:  { section: skills }
  openclaw: { section: skills }
  opencode: { kind: skill }
  pi:       { section: skills }
  vibe:   { kind: skill }
---

# SQL App Discipline

App-layer habits around DB interaction. Security patterns delegated:
passwords → [skill:password-hashing-storage](source/skills/password-hashing-storage.md);
injection → [skill:injection-defense](source/skills/injection-defense.md).

## Pseudokey Neat-Freak

**Trap**: renumbering or resequencing surrogate keys to fill gaps left by deletes.
**Why**: surrogate keys are opaque implementation detail — gaps are meaningless.
Renumbering requires cascading UPDATE across FK references; concurrent transactions
see temporarily duplicate or missing IDs; external systems (logs, caches, bookmarks)
hold stale references that now point elsewhere. **Fix**: gaps are normal and harmless;
never renumber. If "no gaps" is a genuine business requirement (invoice sequences,
regulatory IDs), use a dedicated sequence table separate from the PK — not
auto-increment. **Smell**: `UPDATE orders SET id = row_number() OVER (ORDER BY id)`.

```sql
-- BAD: renumbering after deletes
UPDATE products
SET id = sub.new_id
FROM (SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS new_id FROM products) sub
WHERE products.id = sub.id;

-- GOOD: leave gaps; PK is opaque
-- Gaps in id (1, 2, 5, 9) are fine. Sequences are not document numbers.
```

## See No Evil

**Trap**: ignoring DB return values, swallowing exceptions, or treating every DB call
as infallible. **Why**: silent data loss; partial writes that look like success; bugs
that surface only as stale reads days later. **Fix**: check affected-row count on
UPDATE/DELETE (0 rows = precondition unmet → raise not-found or conflict); propagate
DB exceptions as structured domain errors; never `try/except: pass` around a write;
log the error + correlation ID (cross-ref
[skill:defensive-programming](source/skills/defensive-programming.md)).

```python
# BAD: silently discards "no rows updated"
def deactivate(conn, user_id):
    conn.execute("UPDATE users SET active = FALSE WHERE id = %s", (user_id,))

# GOOD: raise if precondition unmet
def deactivate(conn, user_id):
    result = conn.execute(
        "UPDATE users SET active = FALSE WHERE id = %s", (user_id,)
    )
    if result.rowcount == 0:
        raise NotFoundError(f"user {user_id} not found")
```

## Diplomatic Immunity

**Trap**: SQL living outside version control, skipped in code review, untested by
automated tests. **Why**: schema drift is invisible until prod breaks; migration order
mismatches cause deployment failures; SQL complexity bypasses the same quality gates
that catch app bugs. **Fix**: all schema changes as versioned migration files
(Alembic, Flyway, Liquibase, `golang-migrate`); migrations reviewed like code (cross-ref
[skill:code-review-and-quality](source/skills/code-review-and-quality.md)); migration
correctness tested in CI against a real DB (cross-ref [skill:tdd](source/skills/tdd.md));
deprecated columns removed via two-step process (cross-ref
[skill:deprecation-and-migration](source/skills/deprecation-and-migration.md)).
**Smell**: schema changes delivered as "run this on prod" Slack messages.

## Standard Operating Procedures

**Trap**: stored procedures as universal business-logic hammer; cargo-culting legacy
SP patterns because "that's how it was always done." **Why**: SP logic is hard to
unit-test, harder to debug, invisible to app-layer tracing; version control workflows
are awkward; language features (ORM, type system, observability) unavailable inside
the DB. **Fix**: business logic in app code where it is testable, traceable, and
deployable independently. SP justified only when: atomic DB-side operation with
measurable performance benefit (e.g. bulk upsert, complex aggregation that generates
less data movement than equivalent app code); operation requires data locality that
network round trips would destroy. Document the justification. **Smell**: SP that
sends emails, calls external APIs, or embeds domain rules that change per sprint.

## GOOD

Surrogate key gaps left intact; DB errors raise structured domain exceptions with
correlation ID; all migrations in VCS, reviewed, CI-tested; stored procs only for
proven DB-side performance wins with documented rationale.

## BAD

`UPDATE … SET id = row_number()` to fill PK gaps; `except: pass` around INSERT;
schema changes deployed from memory without migration file; stored proc that contains
the pricing engine and sends Slack notifications.
