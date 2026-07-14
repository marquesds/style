---
id: sql-foreign-keys
kind: skill
title: SQL Foreign Keys
description: "Foreign key implementation mistakes: wrong direction, bad target shape, type/collation mismatches, lifecycle gaps, operational conflicts."
applies_when:
  - schema review with FK constraints
  - FK error on migration
  - ON DELETE / ON UPDATE decisions
  - multi-column FK design
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

# SQL Foreign Keys

FK constraints that *exist but are wrong*. Omitting FKs altogether →
[skill:sql-antipatterns](source/skills/sql-antipatterns.md) "Keyless entry".

## Direction + Creation Order

**Reversed direction**: FK must point from child to parent, never parent to child.
The child table holds the `REFERENCES parent(pk)` clause. Reversing it creates a
circular dependency that blocks both inserts and schema creation.

**Reference before creation**: the referenced table must exist before the FK is
declared. Migration order matters — create parent tables first; child tables after.
In circular schemas, use `ALTER TABLE … ADD CONSTRAINT` after both tables exist, or
use deferrable constraints.

```sql
-- BAD: child created before parent
CREATE TABLE orders (user_id INT REFERENCES users(id)); -- users doesn't exist yet

-- GOOD: parent first
CREATE TABLE users (id SERIAL PRIMARY KEY);
CREATE TABLE orders (user_id INT NOT NULL REFERENCES users(id));
```

## Target Shape

**No UNIQUE/PK on referenced column**: FK must target a column (or column set) with a
`PRIMARY KEY` or `UNIQUE` constraint. Referencing a plain column silently fails on
some engines or raises an error on strict ones. Always verify the parent column is
uniquely constrained.

**Compound FK column mismatch**: multi-column FKs must match the parent's composite
key exactly — same column count and same semantic order. Declaring columns in the
wrong order references the wrong composite index.

```sql
-- BAD: referencing non-unique column
REFERENCES orders(status)  -- status has no UNIQUE constraint

-- GOOD: reference the PK or a UNIQUE-constrained column
REFERENCES orders(id)

-- Compound: order must match
FOREIGN KEY (tenant_id, order_id) REFERENCES orders(tenant_id, id)  -- correct
FOREIGN KEY (order_id, tenant_id) REFERENCES orders(tenant_id, id)  -- wrong order
```

**Type mismatch**: child FK column must be the same data type as the parent PK. Mixing
`INT` with `BIGINT`, `TEXT` with `VARCHAR`, or comparing collations produces FK
creation errors or silent cast failures. **Collation mismatch**: character FK columns
must share collation — `utf8mb4_unicode_ci` on parent, `utf8mb4_bin` on child = FK
creation failure or unexpected inequality on lookup.

```sql
-- BAD: type mismatch
CREATE TABLE users   (id   BIGINT PRIMARY KEY);
CREATE TABLE orders  (user_id INT REFERENCES users(id));  -- INT ≠ BIGINT

-- GOOD: matching types
CREATE TABLE orders  (user_id BIGINT NOT NULL REFERENCES users(id));
```

## Lifecycle

**Orphans on delete — no `ON DELETE` clause**: default `ON DELETE RESTRICT` blocks
parent deletion when children exist. Omitting an explicit clause leaves the behavior
implicit and unclear to reviewers. Always declare intent:

| Intent | Clause |
|--------|--------|
| Block parent delete | `ON DELETE RESTRICT` (explicit) |
| Remove children too | `ON DELETE CASCADE` |
| Null the FK | `ON DELETE SET NULL` (child col must be nullable) |
| Set default | `ON DELETE SET DEFAULT` |

**`SET NULL` on `NOT NULL` column**: declaring `ON DELETE SET NULL` on a FK column
with a `NOT NULL` constraint is a contradiction — the DB will reject the DDL or raise
a runtime error on delete.

```sql
-- BAD: SET NULL on NOT NULL
CREATE TABLE orders (
  user_id INT NOT NULL REFERENCES users(id) ON DELETE SET NULL
);

-- GOOD: nullable column if SET NULL is the intent
CREATE TABLE orders (
  user_id INT REFERENCES users(id) ON DELETE SET NULL
);
-- or: NOT NULL + RESTRICT if deletion should be blocked
```

## Operational

**Duplicate constraint identifiers**: two constraints in the same schema with the same
name cause migration failures. Use a consistent naming convention:
`fk_<child>_<parent>` or `<child>_<col>_fkey`. Migration tools that auto-generate
names can collide on repeated column names across tables.

**Incompatible table/engine types**: MySQL MyISAM does not support FK constraints —
FKs parse silently but are never enforced. Mixing MyISAM and InnoDB tables in the same
FK relationship means the constraint is phantom. Partitioned tables (MySQL < 8.4) also
have FK restrictions — the partition scheme may prevent FK creation entirely.

```sql
-- BAD (MySQL): FK on MyISAM table is a no-op
CREATE TABLE orders (user_id INT, FOREIGN KEY (user_id) REFERENCES users(id))
ENGINE = MyISAM;

-- GOOD: use InnoDB for FK enforcement
CREATE TABLE orders (user_id INT, FOREIGN KEY (user_id) REFERENCES users(id))
ENGINE = InnoDB;
```

## GOOD

Child references parent PK with matching type and collation; parent table created
first; `ON DELETE` clause explicit; `SET NULL` only on nullable columns; unique
constraint names; InnoDB (MySQL) or any engine with real FK support.

## BAD

FK direction reversed; referencing non-unique column; `INT` child → `BIGINT` parent;
implicit `ON DELETE` behavior; `SET NULL` on `NOT NULL` column; duplicate constraint
name across two migrations; FK on MyISAM table that silently does nothing.
