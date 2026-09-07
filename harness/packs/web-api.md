---
id: web-api
version: "harness.1"
source: "harness-defined; OWASP API Security Top 10 (2023) themes"
priority: 5-domain
applies_when: [change_type:public_api, change_type:internal_api, flag:externally_exposed, change_type:external_integration]
agents: [requirements, threat-modeling, secure-coding, code-review, security-review, security-testing, secure-defaults, remediation]
---
# Web / API pack

| ID | Strength | Requirement | Review check | Test |
|---|---|---|---|---|
| API-01 | MUST | Authentication expectation stated per endpoint; anonymous access explicit. | route table vs requirements | unauthenticated call → 401 |
| API-02 | MUST | Object- and function-level authorization enforced server-side; no client-supplied ownership. | handler authz | other user's id → 403/404 |
| API-03 | MUST | Input schema validation (types, bounds, allowlists) before use; reject unknown fields where the API is strict. | validator present | malformed/oversize/extra fields |
| API-04 | MUST | Output exposure: only intended fields; no internal ids/PII/secrets leaked; consistent error shape without stack traces. | serializer review | response inspection |
| API-05 | SHOULD | Rate/resource limits for abusable or expensive endpoints; pagination bounds. | middleware | burst test |
| API-06 | MUST | Backward compatibility of public contracts or explicit versioning; document breaking changes. | contract diff | existing contract tests |
| API-07 | SHOULD | Security-relevant audit logging (who, what, outcome) with redaction. | logging | log check |
| API-08 | MUST (webhooks/callbacks) | Verify signatures/HMAC and timestamps; idempotency; replay protection. | verification code | replayed/forged payload rejected |
| API-09 | MUST | SSRF and redirect safety for any server-side fetch. | URL handling | internal address rejected |
| API-10 | MUST | CORS, cookies (`HttpOnly`, `Secure`, `SameSite`), CSRF protection for state-changing browser-facing endpoints. | config | cross-origin test |
