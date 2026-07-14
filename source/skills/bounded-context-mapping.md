---
id: bounded-context-mapping
kind: skill
title: Bounded Context + Domain Mapping (DDD)
description: "Slice by bounded context. Repositories are aggregate/context ports, not table DAOs. Map explicitly at seams (ACL / translators); keep row↔aggregate mapping inside the context adapter."
applies_when:
  - bounded context boundaries
  - defining repositories or persistence ports
  - translating models across contexts
  - refactoring centralized data-access layer
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

# Bounded Context + Domain Mapping (DDD)

See skill:hexagonal-architecture for dependency direction; this skill spells **DDD placement**: context boundary, repos, mapping.

## Bounded context

Ubiquitous language + aggregates owned **inside** one context. Align vertical slice ↔ context: name tree for capability, not random layer dump.

**Forbidden:** omnibus `domain/` mixing unrelated aggregates; shared “repos” folder whose types belong to mixed languages/contexts.

## Repository (DDD) vs DAO layering

Repository = persistence **port for aggregate roots** in **this context** — collection-like semantics for aggregates you load/save.

**DAO smell:** packages keyed by tables/CRUD reused as grab-bag across features; repo type per row shape with zero aggregate contract; callers stitch many table repos mid–use-case.

Persistence **adapter** implements context’s repo port(s). UoW still one per use case; see skill:unit-of-work-and-transactions.

Pure rules stay isolated from I/O — skill:functional-core-imperative-shell.

## Domain mapping (two seams)

**Across contexts:** Partner / legacy / other slice model ↔ yours only via translator, published event payload, or explicit DTO — **anticorruption** at boundary. Never treat another context’s persistent model as yours.

**Inside adapter:** row or document ↔ aggregate mapping lives in **that** context’s infra module — no global mapper dumping every table into every aggregate.

## Red flags

- Context B imports aggregate or repo adapter from Context A “for convenience.”
- Repo names mirror SQL tables without aggregate vocabulary.
- One “dao” tier shared by unrelated modules — connascence of storage shape.
- Use case pulls ORM entities from foreign bounded context unchanged.

## GOOD

Bounded slice layout + aggregate-scoped repo port (sketch):

```text
billing/
  domain/           # BillingAccount aggregate, invariant language
  ports/
    BillingAccountRepository.py   # Protocol: load/save root
  adapters/
    sql_billing_repository.py      # maps rows ↔ BillingAccount here only
```

```python
class BillingAccountRepository(Protocol):
    def get(self, id: AccountId) -> BillingAccount | None: ...

    def save(self, aggregate: BillingAccount) -> None: ...
```

## BAD

God data layer + table repos glued in use cases:

```text
infra/dao/
  orders_table.py
  line_items_table.py
  invoices_table.py
# every feature reaches in and composes persistence ad hoc
```

```python
def load_order_for_report(order_id: str) -> tuple[dict, list[dict]]:
    row = OrdersDao.select_by_pk(order_id)
    lines = LineItemsDao.select_by_order(order_id)
    return row, lines
```
