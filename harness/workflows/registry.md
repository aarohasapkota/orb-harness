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

## Required roles per risk level (enforced by `harness gate`)

The team is shaped like a small startup engineering team: a spec, an engineer, three peer reviewers in parallel, one fix pass, one final review. Deep security work runs weekly (`/security-weekly`), not on every change.

| Role (agent) | R0 | R1 | R2 | R3 |
|---|:-:|:-:|:-:|:-:|
| blueprint (blueprint, Opus) — spec as `BP:` comments, security baseline; before the implementer | – | – | M | M |
| implementer (secure-coding; orchestrator itself allowed for R0 docs) | M | M | M | M |
| code-review — correctness lens | M | M | M | M |
| test-verification — tests and failure lens | – | M | M | M |
| security-review — security lens, runs negative tests | – | – | M | M |
| final-review — only after a fix pass; closure and regression only | – | F | F | F |
| dependency-review (dependency-vetting) | – | C¹ | C¹ | C¹ |
| secrets scan evidence | – | – | M | M |
| blueprint comments stripped from code, kept in tests, backed up in `blueprints/<run>/` | – | – | M | M |
| human approval (`harness approve`) | – | – | – | M |
| findings blocking | crit/high | crit/high | crit/high | crit/high/medium |

M mandatory · F mandatory once an implementer retry (fix pass) exists; a passing final review on the current revision covers the first-round reviews, which are not repeated · C¹ when third_party_code_added or a manifest changed.
On call, never required by default: requirements, threat-model, architecture-review, governance, domain-specialist, security-testing, secure-defaults, build-security, release-integrity, ai-adversarial-testing. The orchestrator brings one in when a change clearly needs it; most of them run in the weekly security review.
Vulnerability-response mode adds: vulnerability-discovery, triage, remediation (replaces implementer), code-review, security-testing, and for R2+: root-cause, regression-prevention.
Tech-lead authority: the orchestrator may record any non-critical finding as follow-up (`harness followup`, with a reason); it then stops blocking and is listed in the report. Critical findings can never be deferred or waived.
Non-waivable: critical findings, author-as-reviewer, blueprint author or final reviewer acting as a first-round reviewer, reviewer wrote files, stale review revision (unless covered by the final review), failed required tests, invalid result records, blueprint comments left in code.
