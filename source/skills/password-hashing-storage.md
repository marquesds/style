---
id: password-hashing-storage
kind: skill
title: Password Hashing + Storage
description: "Argon2id / bcrypt / scrypt. Random salt per password stored with verify record. No plaintext. Constant-time verify. Pepper in vault only."
applies_when:
  - signup / login / password reset
  - credential storage design
  - replacing legacy hash scheme
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

# Password Hashing + Storage

Password **verification** storage, not encryption. Attacker gets DB → offline guess; slow KDF + unique salt limits rainbow tables.

## Algorithm

Prefer **Argon2id** (memory-hard). **bcrypt** / **scrypt** OK with team agreement + tuned cost. **No** MD5, SHA-1, SHA-256 alone for passwords.

## Salt

**Per-password** random salt (≥128 bits), **stored** next to hash (encoding as single string OK: algo + params + salt + hash). **Not** one global salt; not “secret salt” only — global salt still allows table attack across users without per-user entropy.

## Pepper

Optional **server secret** pepper (skill:secrets-never-in-repo — vault/KMS, **never** git). Concat or HMAC pepper into verify; rotation story documented.

## Verify API

Use library `verify(stored_record, plaintext)` — timing-safe internally. Upgrade path: on successful login rehash if params aged.

## Transport

HTTPS only on wire. OWASP map: skill:owasp-top-ten A02/A07.

## GOOD

Library stores `$argon2id$v=19$...` with embedded salt; cost tuned; plaintext zeroed after verify; migrate from bcrypt when policy says.

## BAD

Plaintext column `password`. SHA256(password). Single app-wide salt constant in source. bcrypt with cost 4. Pepper string in `.env committed`.
