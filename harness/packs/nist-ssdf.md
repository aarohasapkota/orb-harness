---
id: nist-ssdf
version: "1.1+harness.1"
source: "NIST SP 800-218, Secure Software Development Framework (SSDF) v1.1"
priority: 4-baseline
applies_when: [always]
agents: ["*"]
---
# NIST SSDF 1.1 baseline pack

Practice and task IDs are NIST's. "Harness check" is locally defined and is NOT NIST text. Notional implementation examples are not requirements.

| ID | Strength | Practice / task (paraphrased) | Harness check | Evidence | Verifier |
|---|---|---|---|---|---|
| PO.1.1 | MUST | Identify and document security requirements for the development infrastructure and process. | Requirements result exists for R1+; lists process requirements (review, testing, evidence). | requirements.md | requirements |
| PO.1.2 | MUST | Identify and document security requirements for the software itself, maintained over time. | REQ-S-n set, testable, with verifiers. | requirements.md | requirements |
| PO.1.3 | SHOULD | Communicate requirements to third parties (dependencies/services). | Dependency vetting records usage constraints. | vetting.md | dependency-vetting |
| PO.2.1 | MUST | Define roles and responsibilities for SDLC security. | Task roles assigned with distinct principals; SoD verified by gate. | task.json, gate.json | governance / gate |
| PO.3.2 | MUST | Follow recommended security practices for toolchain deployment/operation. | Pinned tool versions; least-privilege tool credentials. | build-security.md | build-security |
| PO.3.3 | MUST | Configure tools to generate artifacts supporting secure development practices. | Every check is recorded as command evidence with exit code. | result.json evidence[] | all |
| PO.4.1 | MUST | Define criteria for software security checks and track through the SDLC. | gate-policy.json risk profiles; findings thresholds. | gate.json | gate |
| PO.4.2 | MUST | Implement processes and mechanisms to gather and safeguard information needed to support security-check criteria. | Append-only audit.jsonl; results are immutable once superseded. | audit.jsonl | harness |
| PO.5.1 | SHOULD | Separate and protect development environments. | No plaintext secrets; untrusted code runs isolated. | secrets-scan | governance |
| PS.1.1 | MUST | Store all forms of code based on least privilege; protect from unauthorized changes. | Branch protection / review path exists; automation tokens scoped. | governance.md | governance |
| PS.2.1 | SHOULD | Make software integrity verification information available to acquirers. | Artifact hashes recorded; signatures per policy. | artifact-hash | release-integrity |
| PS.3.1 | SHOULD | Securely archive necessary release files and supporting data. | Release manifest with versions and lineage. | release-integrity.md | release-integrity |
| PS.3.2 | SHOULD | Collect, safeguard, maintain, and share provenance data for all software components (e.g., SBOM). | Dependency inventory; unknown lineage explicit. | release-integrity.md | release-integrity |
| PW.1.1 | MUST (R2+) | Use forms of risk modeling (threat modeling, attack modeling, attack surface mapping). | threat-model.md with boundaries, threats, mitigations, verifiers. | threat-model.md | threat-modeling |
| PW.1.2 | MUST | Track and maintain the software's security requirements, risks, and design decisions. | Requirement→design→evidence matrices. | security-review.md | security-review |
| PW.2.1 | MUST (R3) | Independent design review by qualified people not involved in the design, and/or automated processes. | architecture-review PASS before implementation, distinct principal. | architecture-review.md | architecture-review |
| PW.4.1 | SHOULD | Acquire and maintain well-secured components from third parties. | Vetting before adoption. | vetting.md | dependency-vetting |
| PW.4.4 | MUST | Verify acquired components comply with requirements before use (vulnerabilities, integrity, provenance). | Audit tool output; hash/lock verification. | command evidence | dependency-vetting |
| PW.5.1 | MUST | Follow secure coding practices appropriate to the language and environment (validate inputs, encode outputs, avoid unsafe functions). | Language pack rules verified in code review. | review.md | secure-coding, code-review |
| PW.6.1/6.2 | MUST (build changes) | Use compiler/interpreter/build tools that offer security features; use them. | Secure flags; controlled configuration. | build-security.md | build-security |
| PW.7.1/7.2 | MUST | Determine and perform code review/analysis; record and triage issues. | Independent code-review result with individual findings. | review.md | code-review |
| PW.8.1/8.2 | MUST (runtime changes) | Determine and perform executable security testing; record and triage issues. | security-testing result with executed test evidence. | security-tests.md | security-testing |
| PW.9.1/9.2 | MUST (config changes) | Define and implement secure-by-default configuration. | secure-defaults result. | secure-defaults.md | secure-defaults |
| RV.1.1–1.3 | MUST (vuln mode) | Gather vulnerability information; review, analyze, confirm; have a disclosure/response policy. | vulnerability-record.md | — | vulnerability-discovery |
| RV.2.1/2.2 | MUST (vuln mode) | Analyze each vulnerability to plan risk response; remediate. | triage.md; remediation with regression test. | — | triage, remediation |
| RV.3.1–3.4 | MUST (R2+ vuln) | Root cause analysis; review similar software for the same issue; update SDLC/tools to prevent recurrence. | root-cause.md; prevention.md with before/after proof. | — | root-cause, regression-prevention |

Global prohibitions (harness-defined, derived from SSDF intent): self-approval; treating an assertion as evidence; disabling a check to pass; unknown provenance recorded as known.
