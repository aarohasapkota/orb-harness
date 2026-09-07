---
id: secrets
version: "harness.1"
source: "harness-defined; SSDF PS.1, PO.5"
priority: 5-domain
applies_when: [always]
agents: ["*"]
---
# Secrets handling pack (applies to every run)

| ID | Strength | Requirement | Check |
|---|---|---|---|
| SEC-01 | MUST | No secret values in source, tests, fixtures, docs, CI files, prompts, logs, evidence, or result.json. Reference names/paths only. | `harness scan secrets` on changed files (record as `secrets-scan` evidence) |
| SEC-02 | MUST | Secrets loaded from environment/secret manager at runtime; `.env` files git-ignored; example files contain placeholders only. | .gitignore, config loaders |
| SEC-03 | MUST | Secrets never logged; redaction in error handlers and structured logging. | log statements review |
| SEC-04 | MUST | Least-privilege, scoped, short-lived credentials for automation; rotation documented. | CI/permission review |
| SEC-05 | MUST | Discovery of a real secret in the repo/history → critical finding, immediate stop, human escalation (rotation is the human's decision). | finding severity critical |
| SEC-06 | MUST | Secrets never passed on command lines visible in process lists where avoidable; never in URLs. | code review |
