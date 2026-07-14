---
id: caching-strategy
kind: skill
title: Caching Strategy
description: "Cache-aside vs write-through vs write-behind per surface. Key completeness. TTL discipline with jitter. Singleflight for hot keys. Negative caching. Event-driven invalidation via outbox. HTTP caching lives in restful-http-design."
applies_when:
  - adding a cache layer to a hot read path
  - investigating stale-data or cache-poisoning bugs
  - designing invalidation strategy for shared data
  - cache stampede or thundering-herd incident
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

# Caching Strategy

Pick one pattern per surface. Invalidate on events. Key all variability.

## Pattern Selection

Choose one pattern per cache surface. Mixing patterns on the same key space causes
inconsistency bugs.

### Cache-Aside (Lazy Population)

Application reads cache; on miss, loads from DB, populates cache, returns.

```python
def get_user(user_id: UserId) -> User:
    cached = cache.get(f"user:{user_id}")
    if cached is not None:
        return User.from_cache(cached)
    user = db.load_user(user_id)
    cache.set(f"user:{user_id}", user.to_cache(), ttl=300)
    return user
```

Use when: read-heavy, tolerate brief stale after write, DB is the authority.

### Write-Through

Application writes to cache and DB in the same operation (or via the cache layer
as write proxy).

Use when: reads must always hit cache (high read:write ratio); DB write and cache
write treated as a unit. Coupling cost: cache failure blocks writes.

### Write-Behind (Write-Back)

Application writes to cache only; async process flushes to DB later.

Use when: very high write throughput, eventual durability acceptable. Risk: cache
failure → data loss. Requires careful durability contract with the caller.

## Key Shape

A cache key must encode **every dimension that produces a different value**:

```text
{resource}:{id}:{tenant}:{locale}:{version}
```

Omit any dimension → cache poisoning across tenants, locales, or API versions.
Use a typed key builder — not ad-hoc string concatenation — so dimensions cannot
be accidentally dropped.

## TTL Discipline + Jitter

- Set a TTL on every key. No eternal keys.
- Jitter expiry: `ttl = base_ttl + random(0, base_ttl * 0.1)` — prevents
  synchronized stampede when many keys share the same base TTL.
- Short TTL (seconds) for high-churn or sensitive data.
- Longer TTL (minutes) for stable reference data; invalidate on write event.

## Singleflight / Request Coalescing

When the same key is requested concurrently during a cold cache, only one fetch
runs; others wait for the first result. Prevents thundering-herd on popular keys.

```python
result = singleflight.do(f"user:{user_id}", lambda: db.load_user(user_id))
```

Use when: hot-key reads are expensive (slow DB query, external API call).

## Negative Caching

Cache misses explicitly with a shorter TTL (e.g. 10 s vs 300 s for hits).
Prevents repeated DB hits for non-existent resources under load.

```python
NOT_FOUND_SENTINEL = object()
value = cache.get(key)
if value is NOT_FOUND_SENTINEL:
    raise NotFound(key)
if value is None:
    value = db.load(key)
    ttl = 10 if value is None else 300
    cache.set(key, value if value is not None else NOT_FOUND_SENTINEL, ttl=ttl)
```

## Invalidation

Prefer **event-driven invalidation** over time-based when consistency matters.
Write the invalidation event into the outbox in the same UoW as the DB write
(skill:unit-of-work-and-transactions). The outbox consumer deletes or refreshes
the cache key. No dual-write race.

Time-based TTL as a fallback safety net; not the primary invalidation mechanism
for mutable data.

## What This Skill Covers

Internal application-layer caches (Redis, Memcached, in-process LRU).  
HTTP-layer caching (`ETag`, `Cache-Control`, `If-None-Match`) lives in
skill:restful-http-design.  
Query-result caching (materialized views, read replicas) lives in
skill:n-plus-one-prevention and skill:sql-query-performance.

## GOOD

```python
@dataclass(frozen=True)
class UserCacheKey:
    user_id: UserId
    tenant_id: TenantId

    def __str__(self) -> str:
        return f"user:{self.tenant_id}:{self.user_id}"

def get_user(key: UserCacheKey, cache: Cache, db: Db) -> User:
    hit = cache.get(str(key))
    if hit is not None:
        return User.from_cache(hit)
    user = db.load(key.user_id, key.tenant_id)
    cache.set(str(key), user.to_cache(), ttl=jitter(300))
    return user
```

Typed key includes tenant. Jittered TTL. Pure function — cache and db injected.

## BAD

```python
def get_user(user_id):
    cached = redis.get(f"user:{user_id}")  # missing tenant → cross-tenant leak
    if cached:
        return pickle.loads(cached)        # unsafe deserialization
    user = db.query(f"SELECT * FROM users WHERE id = {user_id}")  # SQL injection
    redis.set(f"user:{user_id}", pickle.dumps(user))  # no TTL → eternal key
    return user
```

Missing tenant in key, no TTL, unsafe pickle, SQL injection.

## Red Flags

- Cache key omits a tenant, locale, or version dimension.
- TTL not set on any key — eternal entries accumulate.
- Cache write and DB write in separate transactions (dual-write race).
- No singleflight / coalescing on a known hot key.
- Invalidation relies only on TTL expiry for mutable, write-heavy data.
- `pickle` or unsafe deserialization used to store / retrieve cached objects.
