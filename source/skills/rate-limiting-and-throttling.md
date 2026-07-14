---
id: rate-limiting-and-throttling
kind: skill
title: Rate Limiting and Throttling
description: "Token bucket (burst) vs sliding window (smooth) vs fixed window (lossy). Per-tenant + per-endpoint dimensions. 429 + Retry-After headers. Redis counters. Cost-based limiting. Backpressure: queue vs shed. Outbound counterpart in resilience-retries; 429 semantics in restful-http-design."
applies_when:
  - public API endpoint design
  - protecting a downstream dependency from overload
  - abuse mitigation (scraping, brute-force, DDoS)
  - cost or quota enforcement per tenant or plan tier
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

# Rate Limiting and Throttling

Right algorithm per surface. Right dimensions per tenant. Honest headers always.

## Algorithm Selection

| Algorithm | Shape | Best for |
|-----------|-------|----------|
| **Token bucket** | Tokens refill at rate R; burst up to capacity B | Burst-friendly APIs; clients that batch |
| **Sliding window** | Count requests in rolling window | Smooth enforcement; prevents boundary bursts |
| **Fixed window** | Count resets on clock tick | Lowest cost; allows 2× burst at window boundary |

Fixed window is acceptable for low-risk internal quotas. Token bucket or sliding
window for user-facing or sensitive endpoints.

## Dimensions

Always limit on at least two axes:

1. **Per-tenant / per-account**: prevent one tenant from monopolizing shared infra.
2. **Per-endpoint**: expensive endpoints (report generation, bulk export) need
   tighter limits than cheap read endpoints.

Global-only limits fail silently: one noisy tenant starves everyone else before
the global threshold fires.

Optional third axis: **per-IP** as abuse backstop (DDoS, brute-force). IP limits
complement, not replace, authenticated tenant limits.

## Response Contract

Always return `429 Too Many Requests` with:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 42
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1715000042
Content-Type: application/problem+json

{
  "type": "https://api.example.com/problems/rate-limited",
  "title": "Rate limit exceeded",
  "status": 429,
  "detail": "100 requests per minute per account. Retry after 42 s.",
  "retry_after": 42
}
```

`Retry-After` in seconds. `X-RateLimit-*` on every response (not only 429) so
clients can back off before exhaustion.

See skill:restful-http-design for full status-code and error-body conventions.

## Distributed Counters

Redis `INCR` + `EXPIRE` pattern for token bucket or fixed window:

```python
def check_fixed_window(key: str, limit: int, window_s: int) -> bool:
    pipe = redis.pipeline()
    pipe.incr(key)
    pipe.expire(key, window_s)
    count, _ = pipe.execute()
    return count <= limit
```

For sliding window, use a sorted set with timestamps as scores; prune entries
older than `now - window_s` before counting.

Trade-off vs local counters: Redis adds a network hop (~0.5 ms) but gives correct
counts across multiple instances. Local-only counters allow N× overshoot where N
= instance count.

## Cost-Based Limiting

Some operations are more expensive than a single request count suggests:

```python
OPERATION_COST = {
    "read_item": 1,
    "search": 5,
    "bulk_export": 50,
    "report_generate": 100,
}
```

Consume cost units from a shared bucket rather than incrementing a flat counter.
Callers hit budget limits before hitting request-count limits on expensive paths.

## Backpressure: Queue vs Shed

When a downstream dependency is saturated, choose one strategy:

| Strategy | When | Trade-off |
|----------|------|-----------|
| **Queue** | Caller can tolerate latency; work must complete | Adds memory/latency; queue can fill |
| **Shed (reject)** | Latency budget tight; caller retries | Simpler; requires client retry logic |

Shedding is usually correct for synchronous HTTP APIs. Queueing suits async jobs
and batch workloads. Never silently drop requests — always signal back.

Combine with skill:resilience-retries on the outbound side: the client sees a 429,
backs off with jitter, retries.

## GOOD

```python
def check_rate_limit(tenant_id: TenantId, endpoint: str, cost: int = 1) -> None:
    key = f"rl:{tenant_id}:{endpoint}:{current_window()}"
    new_count = redis.incrby(key, cost)
    if new_count == cost:
        redis.expire(key, WINDOW_SECONDS)
    limit = LIMITS[endpoint]
    if new_count > limit:
        retry_after = seconds_until_next_window()
        raise RateLimitExceeded(limit=limit, retry_after=retry_after)
```

Per-tenant + per-endpoint key. Cost-based. Returns `Retry-After`. No global limit only.

## BAD

```python
if request_count > 1000:   # global counter, no tenant dimension
    return 503             # wrong status code, no Retry-After, no headers
```

Global-only limit. Wrong status (503 ≠ 429). No headers. No retry guidance for client.

## Red Flags

- Only a global rate limit — one tenant can exhaust it for everyone.
- 429 returned without `Retry-After` or `X-RateLimit-*` headers.
- Expensive endpoints (bulk export, report) counted at weight 1 same as a ping.
- Rate limit state stored in-process only — resets on every deploy or pod restart.
- Silently dropping requests instead of returning 429.
- Client receives 503 (server error) instead of 429 (client should back off).
