---
id: auth-identity
version: "harness.1"
source: "harness-defined; OWASP ASVS V2/V3; NIST SP 800-63B themes"
priority: 5-domain
applies_when: [change_type:authentication, change_type:authorization, flag:security_boundary_affected, flag:privilege_boundary_affected]
agents: [requirements, threat-modeling, architecture-review, secure-coding, code-review, security-review, security-testing, secure-defaults, remediation]
---
# Authentication / identity / authorization pack (R3 by default)

| ID | Strength | Requirement | Test expectation |
|---|---|---|---|
| AUTH-01 | MUST | Use the platform's or an approved library's authentication; no bespoke password hashing, token formats, or session stores. | — |
| AUTH-02 | MUST | Password storage: memory-hard hash (argon2id/bcrypt/scrypt) with per-user salt; never reversible. | hash format check |
| AUTH-03 | MUST | Brute-force resistance: rate limiting/lockout/backoff on credential endpoints; generic error messages (no user enumeration). | repeated failures throttled; same message for unknown user |
| AUTH-04 | MUST | Session/token lifecycle: secure random ids, rotation on privilege change/login, server-side revocation, bounded lifetime, `HttpOnly/Secure/SameSite` cookies, no tokens in URLs/logs. | token reuse after logout fails |
| AUTH-05 | MUST | JWT/OIDC: verify signature with pinned algorithms (reject `none`), issuer, audience, expiry, nonce/state for OAuth flows; keys fetched securely and cached with rotation. | tampered/`alg=none`/expired token rejected |
| AUTH-06 | MUST | Authorization decisions server-side, centralized, deny-by-default, evaluated at the boundary before any side effect; role/scope changes require re-authentication where sensitive. | privilege escalation attempts fail |
| AUTH-07 | MUST | MFA hooks not weakened; recovery flows as strong as primary auth. | — |
| AUTH-08 | MUST | Fail closed on identity provider errors. | IdP failure → denied |
| AUTH-09 | MUST | Audit log for auth events (success/failure/lockout/privilege change) without credentials. | log check |
| AUTH-10 | MUST | The implementer never approves authentication correctness; independent security review + negative tests are mandatory. | gate SoD |
