---
id: injection-defense
kind: skill
title: Injection Defense
description: "SQLi via parameters. Command / LDAP / SSTI / path traversal callouts. No string concat for structure."
applies_when:
  - raw SQL or shell
  - dynamic query building
  - template engine with user input
  - ORM raw fragments
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

# Injection Defense

Boundary: treat all external strings as **data**, never as **syntax**, unless escaped for exact target language. skill:sql-antipatterns = schema traps; this = **app** concat + shell + template.

## SQLi

**Trap**: `f"SELECT * FROM u WHERE id = '{user}'"` or `+ req.query.id`. **Fix**: prepared / parameterized; bound params only. ORM: no raw `%` concat; if dynamic columns, **allowlist** names, never user string as identifier.

## Command injection

**Trap**: `os.system("convert " + path)`. **Fix**: `subprocess` argv list, no shell; validate path normalize + root jail; no user in shell string.

## LDAP / XPath / NoSQL

**Trap**: concat filter with user input. **Fix**: parameterized APIs or strict escape per spec; deny `*` wildcards where inappropriate.

## SSTI

**Trap**: user string as template body (Jinja, ERB, etc.). **Fix**: templates fixed in code; user data only as **variables** passed in.

## Path traversal

**Trap**: `open(base + user_path)`. **Fix**: resolve realpath under root; reject `..` after normalize.

## LLM / prompt

User text driving tool args → skill:llm-prompt-injection.

## GOOD

```python
cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
subprocess.run(["convert", in_path, out_path], check=True)
```

## BAD

```python
cur.execute(f"SELECT * FROM users WHERE id = '{user_id}'")
os.system(f"convert {path} out.png")
```

Dynamic SQL string; shell string. Game over on malicious input.
