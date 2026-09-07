---
id: owasp-appsec
version: "top10-2021+asvs-lite.harness.1"
source: "OWASP Top 10 (2021) and OWASP ASVS themes"
priority: 5-domain
applies_when: [risk_at_least:R1]
agents: [secure-coding, code-review, security-review, security-testing, threat-modeling, requirements, remediation]
---
# OWASP application security pack

| ID | Strength | Requirement | Check (review) | Check (test) |
|---|---|---|---|---|
| OWASP-A01 | MUST | Enforce authorization server-side at every access path; deny by default; object-level checks (no IDOR). | Authz check present at boundary for every new handler/route/tool. | Access another user's object/ID → denied; missing role → denied. |
| OWASP-A02 | MUST | Protect sensitive data in transit and at rest with approved crypto (see `cryptography` pack); no sensitive data in logs/URLs. | grep for logging of tokens/PII; TLS config. | Response/logs contain no secrets. |
| OWASP-A03 | MUST | Prevent injection: parameterized queries, safe command execution (no shell string building), context-aware output encoding, safe template engines, validated paths (no traversal), safe LDAP/XPath/log formatting, prompt/context delimiting for LLM inputs. | Every sink traced from untrusted source. | Payloads per sink type: `' OR 1=1--`, `; id`, `../../etc/passwd`, `{{7*7}}`, CRLF. |
| OWASP-A04 | MUST | Insecure design: threat model exists (R2+), abuse cases covered, rate/resource limits on abusable endpoints. | threat-model coverage. | Abuse-case tests. |
| OWASP-A05 | MUST | Security misconfiguration: no debug in prod, strict CORS, secure cookie flags, minimal features/permissions, safe error pages. | secure-defaults review. | Error response leaks no stack trace/config. |
| OWASP-A06 | MUST | Vulnerable/outdated components: vetted, pinned, audited (see `openssf-dependencies`). | vetting result present. | audit tool run. |
| OWASP-A07 | MUST | Identification/authentication failures: approved libraries, MFA-compatible, brute-force protection, secure session handling (see `auth-identity`). | — | Negative auth tests. |
| OWASP-A08 | MUST | Software/data integrity: no unsafe deserialization of untrusted data; signed/verified updates & CI artifacts. | grep pickle/yaml.load/ObjectInputStream/unserialize. | Malformed serialized payload rejected. |
| OWASP-A09 | SHOULD | Logging/monitoring: security events logged without sensitive data; tamper-evident where required. | logging changes reviewed for redaction. | Log output inspection. |
| OWASP-A10 | MUST | SSRF: validate/allowlist outbound URLs; block internal ranges/metadata endpoints; no redirects to internal. | outbound request code reviewed. | `http://169.254.169.254`, `localhost`, DNS rebinding cases rejected. |
| OWASP-INPUT | MUST | Validate all untrusted input for type, length, range, format, allowlist; reject, do not sanitize-and-hope, for structured data. | validation at boundary. | Oversized/malformed/unicode edge cases. |
| OWASP-ERR | MUST | Fail securely: exceptions default to deny; no sensitive info in errors. | error paths traced. | Forced error tests. |
| OWASP-UPLOAD | MUST (uploads) | Validate content type by content, size limits, store outside web root, randomize names, scan if policy requires. | — | Polyglot/oversize upload tests. |

Prohibited patterns: string-concatenated SQL/commands; `eval`/`exec` on untrusted data; disabling TLS verification; wildcard CORS with credentials; catching-and-ignoring auth errors; secrets in code.
