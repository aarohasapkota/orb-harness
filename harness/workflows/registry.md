# Workflow registry (SDLC Orchestration layer)

The SDLC layer decides WHEN work happens and in what order. Specialist agents decide WHAT security work happens. Practice packs say HOW. The gate proves it HAPPENED.

| Workflow | File | Default? | Select when |
|---|---|---|---|
| Risk-based Agile + DevSecOps | `risk-based.md` | **Yes** | No repository/project/user SDLC instruction. Ordinary AI-assisted coding. |
| Agile | `agile.md` | no | Repo/project works in stories/iterations without CI/CD emphasis, or `sdlc: agile` declared. |
| Waterfall | `waterfall.md` | no | Formal sequential phase approvals required by policy/contract, or `sdlc: waterfall` declared. |
| DevSecOps | `devsecops.md` | no | CI/CD, frequent deployment, telemetry central; `sdlc: devsecops`. |
| Emergency fix overlay | `emergency.md` | overlay | Active exploitation / severe production vulnerability. Accelerates order, never removes obligations. |
| Rollback | `rollback.md` | special | Restore known-good state; corrective work re-enters normal SDLC. |

Selection priority (highest first): system/org security requirements → repository policy or declared SDLC (`.harness/policy/project-pack.md` `sdlc:` or CONTRIBUTING/AGENTS docs) → explicit user request → repository conventions → default (risk-based).

Invariants for every workflow: security is not a final phase; required agents run at their injection points; mandatory gates pass before protected transitions; reclassify when scope/risk changes; failed mandatory gate never counts as pass; `not_applicable` needs a rationale; backfill earlier stages when late discoveries invalidate them; AI-generated code gets the same scrutiny.

## Gate matrix (mandatory task roles per risk level, enforced by `harness gate`)

| Role (agent) | R0 | R1 | R2 | R3 |
|---|:-:|:-:|:-:|:-:|
| implementer (secure-coding; orchestrator itself allowed for R0 docs) | M | M | M | M |
| code-review | M | M | M | M |
| requirements | – | M | M | M |
| test-verification | – | M | M | M |
| threat-model (threat-modeling) | – | – | M | M |
| security-review | – | – | M | M |
| security-testing | – | – | M | M |
| architecture-review (before implementation) | – | – | – | M |
| secure-defaults | – | – | – | M |
| dependency-review (dependency-vetting) | – | C¹ | C¹ | C¹ |
| domain-specialist (data-migration / ci-cd-platform / ai-agent-security) | – | C² | C² | C² |
| build-security | – | – | C³ | C³ |
| release-integrity | – | – | – | C³ |
| ai-adversarial-testing | – | – | A | A |
| secrets scan evidence | – | – | M | M |
| human approval (`harness approve`) | – | – | – | M |
| findings blocking | crit/high | crit/high | crit/high | crit/high/medium |

M mandatory · C conditional (¹ third_party_code_added or manifest diff · ² persistent_data_affected / AI scope / build path · ³ build_or_release_path_affected) · A mandatory when ai_scope ≠ none.
Vulnerability-response mode adds: vulnerability-discovery, triage, remediation (replaces implementer), code-review, security-testing, and for R2+: root-cause, regression-prevention.
Non-waivable: critical findings, author-as-reviewer, reviewer wrote files, stale review revision, failed required tests, invalid result records. High/medium findings are waivable only by the human via `harness waiver`.
