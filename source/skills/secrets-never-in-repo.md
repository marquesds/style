---
id: secrets-never-in-repo
kind: skill
title: Secrets Never in Repo
description: "No API keys, tokens, PEMs, real .env, or credential literals in VCS or tests. Env, vault, CI secrets; scan; rotate if leaked."
applies_when:
  - new service config
  - CI pipeline
  - sample env files
  - code review spotting literals
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

# Secrets Never in Repo

VCS history is long-lived copies. Assume clone leak.

## Forbidden in git

Live API keys, OAuth client secrets, DB passwords, private keys (.pem), session signing keys, **real** `.env`, webhook signing secrets. Test doubles: fake values or generators — not prod copy.

## Where secrets live

Process **env**, cloud **secret manager**, CI **masked** variables. `.env.example` = names + dummy values only. Deploy injects runtime config.

## Hygiene

`.gitignore` for local env files; pre-commit / CI-secret scan (trufflehog, gitleaks, gh secret scanning). Keys in Slack/screenshot/email = same rotation as leak.

## After leak

**Rotate** credential at provider; revoke old keys. Revert commit not enough — history scrub only if policy allows + coordinated rotation.

## Logs and prompts

Structured logs omit tokens; truncate `Authorization`. LLM prompts: skill:llm-prompt-injection — never paste vault material into chat logs. Pepper: skill:password-hashing-storage.

## GOOD

`DATABASE_URL` from env; `.env.local` gitignored; CI uses OIDC to cloud; example file `API_KEY=replace-me`; scanner green on PR.

## BAD

```python
STRIPE_KEY = "sk_live_xxxx"
```

Hardcoded live key. Also: “temporary” key in test file committed; real `.env` pushed “by accident once”.
