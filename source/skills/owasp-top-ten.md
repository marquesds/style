---
id: owasp-top-ten
kind: skill
title: OWASP Top 10 (2021) Map
description: >
  Ten-category web risk map. Failure mode + primary control + drill-down skills.
  OWASP Top 10 2021 alignment.
applies_when:
  - threat model sketch
  - security review
  - new surface with auth or data
  - compliance checklist
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

# OWASP Top 10 (2021) Map

Navigation layer. Deep dives: skill:injection-defense, skill:xss-and-csp, skill:password-hashing-storage, skill:secrets-never-in-repo, skill:llm-prompt-injection. API shape: skill:restful-http-design, skill:api-and-interface-design.

## A01 Broken access control

**Trap**: IDOR, missing authz on action, path `/admin` guessable, CORS `*`. **Fix**: default deny; check on every handler; object-level permission; tests for cross-tenant. **API**: skill:restful-http-design (errors, versioning).

## A02 Cryptographic failures

**Trap**: TLS off, weak ciphers, secrets in repo, plaintext PII at rest. **Fix**: TLS everywhere; strong suites; envelope encryption where needed; skill:password-hashing-storage; skill:secrets-never-in-repo.

## A03 Injection

**Trap**: concat SQL/shell/template; untrusted in query. **Fix**: params, safe APIs, context escape. **Drill**: skill:injection-defense, skill:sql-antipatterns (schema vs app concat).

## A04 Insecure design

**Trap**: threat model skipped; trust boundary wrong; “we’ll add auth later.” **Fix**: abuse cases with design; least privilege by default; failure states explicit.

## A05 Security misconfiguration

**Trap**: debug on prod, default creds, broad headers, repo `.env`. **Fix**: hardened config; feature flags; skill:secrets-never-in-repo.

## A06 Vulnerable and outdated components

**Trap**: stale deps, unpinned supply chain. **Fix**: lockfiles, renovate/dependabot, SBOM where org requires; patch SLA.

## A07 Identification and authentication failures

**Trap**: weak session, missing MFA where needed, credential stuffing friendly. **Fix**: skill:password-hashing-storage; secure cookies; rate limit; session fixation hygiene.

## A08 Software and data integrity failures

**Trap**: unsigned updates, CI without provenance, deser gadget. **Fix**: signed artifacts; verify packages; safe JSON/YAML parsing; no `pickle` from network.

## A09 Security logging and monitoring failures

**Trap**: no audit on authz change, silent 401 flood. **Fix**: structured logs, alerts on auth anomalies; no secrets in logs (skill:secrets-never-in-repo). **Rule**: observability rule in repo.

## A10 SSRF

**Trap**: server fetches user-supplied URL; metadata creds stolen. **Fix**: allowlist hosts; block link-local; no raw URL pass-through to HTTP client.

## GOOD

```text
Review: A01 IDOR tests for /items/{id}; A03 all SQL via bound params;
A02 pepper in vault not git (skill:secrets-never-in-repo); A10 fetcher allowlist only.
```

## BAD

```text
"We use HTTPS and ORM so Top 10 covered"
```

ORM != authz. TLS != injection proof. No map, no proof.
