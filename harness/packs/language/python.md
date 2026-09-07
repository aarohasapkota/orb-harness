---
id: language.python
version: "harness.1"
source: "harness-defined; OWASP Python security cheat sheets; Bandit rule themes"
priority: 6-language
applies_when: [lang:python]
agents: [secure-coding, code-review, security-review, security-testing, remediation, regression-prevention]
---
# Python secure coding pack

| ID | Strength | Rule | Detect |
|---|---|---|---|
| PY-01 | MUST | No `eval`/`exec`/`compile` on untrusted input; no `pickle`/`marshal`/`shelve`/`yaml.load` (use `yaml.safe_load`) on untrusted data. | grep |
| PY-02 | MUST | `subprocess` with list args and `shell=False`; never build shell strings from input; no `os.system`. | grep `shell=True`, `os.system` |
| PY-03 | MUST | Parameterized queries / ORM; no f-string/format SQL. | grep `execute(f"`, `% (` |
| PY-04 | MUST | Path handling: resolve and check `is_relative_to` an allowed root; no `..` traversal; `tempfile` secure APIs. | review |
| PY-05 | MUST | `secrets` for tokens; `hashlib` with SHA-256+; `hmac.compare_digest`; no `random` for security. | grep |
| PY-06 | MUST | `requests`/`httpx` with `verify=True`, explicit timeouts; validate outbound URLs (SSRF). | grep `verify=False`, missing `timeout` |
| PY-07 | MUST | Templates auto-escaped (Jinja2 `autoescape=True`); `Markup`/`|safe` only with reviewed data. | grep |
| PY-08 | MUST | Deserialization of untrusted JSON with schema validation (pydantic/jsonschema); `defusedxml` for XML. | review |
| PY-09 | MUST | No `assert` for security checks (stripped with -O); explicit exceptions. | grep |
| PY-10 | SHOULD | Run `bandit -q -r <paths>` / `ruff` / `mypy` when available; record command evidence. | command |
| PY-11 | MUST | Dependencies pinned in lock (poetry/uv/pip-tools); `pip-audit` when available. | command |
