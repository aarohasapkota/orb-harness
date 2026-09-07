---
id: openssf-dependencies
version: "harness.1"
source: "OpenSSF Concise Guide for Evaluating Open Source Software; OpenSSF Scorecard checks; OpenSSF npm/PyPI best practices"
priority: 5-domain
applies_when: [change_type:dependency, flag:third_party_code_added]
agents: [dependency-vetting, secure-coding, code-review, security-review, build-security, remediation]
---
# OpenSSF-derived dependency pack

| ID | Strength | Requirement | Check | Evidence |
|---|---|---|---|---|
| DEP-01 | MUST | Necessity: prefer existing functionality/vetted components; each new dependency has a stated reason. | vetting verdict discusses alternatives. | vetting.md |
| DEP-02 | MUST | Exact pinning: manifest + lockfile agree; no floating majors for R2+; integrity hashes present where the ecosystem supports them. | `harness scan deps`; lock inspection. | command |
| DEP-03 | MUST | Known vulnerabilities: run the ecosystem audit tool or OSV lookup; critical/high with reachable exposure → reject or waiver by human. | `npm audit`/`pip-audit`/`cargo audit`/`govulncheck`/`osv-scanner`. | command |
| DEP-04 | MUST | Install-time code: inspect `preinstall/postinstall`, `setup.py`, build scripts, native builds, network fetches during install. | package tarball / repo inspection. | analysis |
| DEP-05 | SHOULD | Maintenance & trust: active maintenance, multiple maintainers or org, signed releases/provenance (npm provenance, Sigstore), 2FA hints, repo matches package. | registry metadata, repo. | analysis + URLs |
| DEP-06 | MUST | Name confusion: verify exact package name/scope (typosquats, dependency confusion with internal names); registry source is the intended one. | name/registry check. | analysis |
| DEP-07 | SHOULD | Licence compatible with repository policy; recorded (`unknown` allowed). | registry/LICENSE. | analysis |
| DEP-08 | MUST | Scope of privilege: dependency that executes at build with broad privileges, loads native code in a critical boundary, handles credentials, or implements auth/crypto → escalate to R3. | analysis. | finding RISK_ESCALATION |
| DEP-09 | MUST | Transitive changes reviewed when lockfile diff adds new transitive packages with install scripts or native code. | lock diff. | analysis |
| DEP-10 | SHOULD | Re-vet when usage context changes materially (e.g., now parses untrusted input). | — | — |
