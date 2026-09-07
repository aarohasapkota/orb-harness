# Harness architecture

One Fable 5.1 session (the Engineering Orchestrator, in the human's cmux tab) decides. Sonnet (effort high) worker sessions, each in its own tab, do the specialist work and write evidence. A deterministic gate decides whether the change may proceed.

```mermaid
flowchart TD
    U[Human in cmux tab] --> EO[Engineering Orchestrator<br/>Fable 5.1 · ~/.claude/CLAUDE.md]
    EO --> CL[Request + Risk classification<br/>harness run new / run set / classify]
    CL --> SDLC[SDLC selection<br/>workflows/registry.md · default risk-based Agile+DevSecOps]
    SDLC --> WP[Work packages<br/>harness task new]
    WP --> SP[harness spawn → new terminal tab<br/>claude --model sonnet --effort high --agent X]

    subgraph Workers["Sonnet workers (one tab each, ~/.claude/agents/*.md)"]
        direction LR
        PO[Prepare: repo-context · requirements · governance]
        PW1[Design: threat-modeling · architecture-review · ai-agent-security · dependency-vetting · data-migration]
        IMPL[Implement (write): secure-coding · remediation · ci-cd-platform · data-migration · regression-prevention]
        VER[Verify (read-only): test-verification · code-review · security-review · security-testing · ai-adversarial-testing · build-security · secure-defaults · release-integrity]
        RV[Respond: vulnerability-discovery · triage · root-cause]
    end
    SP --> Workers
    PK[Practice packs<br/>harness packs → nist-ssdf, nist-ssdf-ai, owasp-*, openssf, supply-chain, web-api, auth, crypto, secrets, migration, ci-cd, ai-tools, vuln, release, language/*] --> Workers
    Workers --> EV[Evidence: .harness/runs/ID/tasks/TASK/result.json<br/>validated by Stop hook + harness result validate]
    HK[Hooks: PreToolUse read-only guard · Stop contract check · SessionStart banner] -.enforce.- Workers
    EV --> GATE[Policy gate · harness gate<br/>policy/gate-policy.json · deterministic]
    GATE -->|PASS| REP[harness report → Final Output Contract]
    GATE -->|FAIL| RT[Remediation routing → retry task → re-verify (max 2 cycles)]
    RT --> WP
    GATE -->|NEEDS_HUMAN| HU[Human: ! harness approve / ! harness waiver]
    HU --> GATE
    AUD[audit.jsonl hash-chained · gate-history.jsonl] -.- GATE
```

## Layers → implementation

| Spec layer | Where it lives | How it executes |
|---|---|---|
| 1 Engineering Orchestrator | `~/.claude/CLAUDE.md`, `/harness` skill | Fable session; classification, planning, delegation, SoD assignment, completion |
| 2 SDLC Orchestration | `workflows/*.md`, `run.json.workflow`, `--depends` ordering in `harness spawn` | Orchestrator picks the workflow; spawner enforces required serialization |
| 3 Specialist agents | `~/.claude/agents/*.md` (23) | `harness spawn` launches `claude --agent <name>` in a tab; preamble appends the worker protocol |
| 4 Practice packs | `packs/*.md`, resolver `harness packs` | Deterministic applicability from run classification; agents cite requirement IDs |
| 5 Evidence + gates | `schemas/result.schema.json`, `harness result validate`, Stop hook, `harness gate`, `policy/gate-policy.json`, `audit.jsonl` | Evidence bound to `harness rev`; gate computes PASS/FAIL/NEEDS_HUMAN/NOT_APPLICABLE from files only |

## Identity and separation of duties

Each agent name is a principal (`agent:<name>`); the orchestrator is `orchestrator:fable-5.1`; the human is `human:<name>`. The gate fails, non-waivably, when the implementer principal equals any reviewer principal, when a reviewer reports `files_changed`, when code review and security testing share a principal, when R3 security review shares the code-review principal, or when review evidence is bound to a revision other than the final tree. Hooks make reviewer writes impossible in practice; the gate makes them fatal if they slip through.

## Runtime layout

```
~/.claude/
  CLAUDE.md                 orchestrator instructions (every project)
  settings.json             hooks (SessionStart, PreToolUse, Stop) + HARNESS_HOME
  agents/*.md               23 specialist agents (model: sonnet)
  skills/{harness,spawn,gate}/SKILL.md
  harness/
    bin/harness             control-plane CLI (python3, no deps)   → also ~/.local/bin/harness
    config.json             worker model/effort/permission mode, terminal backend, tab keys
    policy/gate-policy.json risk profiles, thresholds, routes, SoD
    schemas/result.schema.json
    packs/                  practice packs + registry.json
    workflows/              registry (gate matrix) + 6 workflows
    templates/              worker-preamble.md, project-pack.md
    launch/                 generated per-task launch scripts (short path for AppleScript typing)
    tests/test_gate.py      deterministic scenario suite
<project>/.harness/
  runs/<run-id>/run.json · audit.jsonl · gate.json · gate-history.jsonl
  runs/<run-id>/tasks/<task>/ task.json · package.md · envelope.json · system-append.md · launch.sh · result.json · <artifacts>.md
  runs/<run-id>/waivers/*.json · approvals/*.json
  policy/project-pack.md (optional overlay; may declare `sdlc:`)
```

`.harness/` is added to `.git/info/exclude` automatically (evidence stays local unless you choose to commit it).

## Terminal tab spawning

`harness spawn` writes `launch/<run>-<task>.sh` (cd project, export `HARNESS_*` env, `exec claude --model sonnet --effort high --agent <agent> --name "<task> <agent>" --permission-mode <mode> --append-system-prompt <protocol+envelope> "<work package>"`) and opens it in a tab:

| Backend | How | Notes |
|---|---|---|
| **cmux** (default when `CMUX_WORKSPACE_ID` is set or the cmux socket `~/.local/state/cmux/cmux.sock` exists) | `cmux new-workspace --name "<task> <agent>" --cwd <project> --command "bash <launch>" --focus false`, then `cmux set-status`; Stop hook sends `cmux notify` on completion | Socket API, no Accessibility permission. Start `claude` inside a cmux tab (default socket mode admits cmux child processes only). |
| ghostty | AppleScript: activate Ghostty, ⌘T (key code), type `bash <launch>`, ⏎, then ⌘⇧[ back to your tab | Requires Accessibility permission for Ghostty. Keys configurable in `config.json`. |
| iterm | native AppleScript `create tab` | |
| terminal | `Terminal.app do script` (new window) | |
| tmux | `tmux new-window -d` | when `$TMUX` is set |
| bg | `nohup bash launch.sh` → `tasks/<task>/worker.log` | fallback / `--headless` (`-p`) |

The orchestrator never blocks on workers: `harness wait` runs as a background Bash and returns JSON when results appear.

## Agent registry

| ID (agent) | Role(s) | Parent (SSDF group) | Invoked when | Writes product code? | Outputs / evidence |
|---|---|---|---|---|---|
| repo-context | context | Orchestrator (PO) | unfamiliar/large area before planning | no | instruction inventory, component map, risk-elevating facts |
| requirements | requirements | Prepare (PO.1) | every R1+ change | no | requirements.md (REQ-F/REQ-S with verifiers) |
| governance | governance | Prepare (PO.2–5, PS.1) | R2/R3 pre-checks | no | role map, tool matrix, secrets-scan, branch protection facts |
| threat-modeling | threat-model | Secure Eng (PW.1) | R2/R3 | no | threat-model.md, threat→mitigation→verifier→test map |
| architecture-review | architecture-review | Secure Eng (PW.2) | R3 (before implementation) | no | requirement/design mapping, verdict |
| dependency-vetting | dependency-review | Secure Eng (PW.4) | dependency/model/service added or changed | no | vetting.md, audit tool output, adopt/reject |
| ai-agent-security | domain-specialist (AI) | Secure Eng / Protect (218A) | ai_scope ≠ none | no | trust boundaries, tool capability table, provenance, adversarial plan |
| data-migration | domain-specialist / implementer | Secure Eng | schema/data changes | when assigned | forward/rollback runs, compat + data-loss analysis |
| ci-cd-platform | domain-specialist / implementer | Secure Eng / Protect (PW.6, PS.1) | pipeline/infra changes | when assigned | validated pipeline diff, permission/trigger record |
| secure-coding | implementer | Secure Eng (PW.5) | every R1+ code change | **yes** | minimal patch, tests, diff/test-run/secrets-scan evidence |
| test-verification | test-verification | Secure Eng (PW.8 functional) | R1+ | no | criterion→evidence map, full test/build/lint runs |
| code-review | code-review | Secure Eng (PW.7) | every change | no | individual findings, APPROVE/REQUEST_CHANGES, revision-bound |
| security-review | security-review | Secure Eng (PW.7 security) | R2/R3 | no | requirement/threat/mitigation/evidence matrix |
| security-testing | security-testing | Secure Eng (PW.8) | R2/R3, R1 runtime | no | executed negative/abuse tests, reproductions |
| ai-adversarial-testing | ai-adversarial-testing | Secure Eng (218A PW.8) | R2/R3 AI | no | attack-case table, sanitized transcripts |
| build-security | build-security | Secure Eng (PW.6) | build/CI path affected | no | build run, tool versions, artifact hashes, CI trust review |
| secure-defaults | secure-defaults | Secure Eng (PW.9) | R3; config defaults change | no | settings table, default tests |
| release-integrity | release-integrity | Protect (PS.2, PS.3) | release path / RELEASE mode | no | artifact hashes, signature status, SBOM/lineage gaps |
| vulnerability-discovery | vulnerability-discovery | Respond (RV.1) | vuln mode | no | vulnerability record, safe reproduction |
| triage | triage | Respond (RV.2.1) | vuln mode | no | severity rationale, acceptance criteria |
| remediation | remediation (implementer) | Respond (RV.2.2) | vuln mode | **yes** | fix, before/after reproducer, regression test |
| root-cause | root-cause | Respond (RV.3.1–2) | R2+ vuln | no | cause/escape analysis, control gaps |
| regression-prevention | regression-prevention | Respond (RV.3.3–4) | R2+ vuln | tests/rules only | new test/rule with before/after proof |

Every agent returns the shared contract `harness-result/1` (`schemas/result.schema.json`): status, revision, files_changed, evidence[], findings[], tests, claims→evidence, unresolved, handoff.

## Workflow registry

See `workflows/registry.md`. Default: **risk-based Agile + DevSecOps** (composition). Agile, Waterfall, DevSecOps selectable by repository declaration (`.harness/policy/project-pack.md` `sdlc:`), policy, or user request. Emergency-fix overlay and Rollback are special paths that never delete obligations.

## Gate matrix

In `workflows/registry.md` (mandatory roles per R0–R3, conditional triggers, findings thresholds, human approval at R3, non-waivable conditions). Enforced by `policy/gate-policy.json` + `harness gate`.

## Practice pack registry

`packs/registry.json`: nist-ssdf, nist-ssdf-ai, secrets (always), owasp-appsec, owasp-llm, openssf-dependencies, supply-chain-provenance, web-api, auth-identity, cryptography, data-migration, ci-cd-build-integrity, ai-agent-tool-execution, vulnerability-response, release-integrity, language.python, language.javascript-typescript, language.go, plus the optional project overlay.

## Tests

`python3 ~/.claude/harness/tests/test_gate.py` — 39 deterministic checks covering: R0 docs (pass; executable file → reclassify), R1 (pass; missing roles; author-as-reviewer; reviewer wrote files; stale review), R2 dependency + API (failed dependency review → retry; failed security test → remediation → stale verifiers → re-verify → pass), R3 auth + AI tool-use (pack loading; failed review with critical finding; critical non-waivable; medium blocks at R3; waiver; NEEDS_HUMAN; approve → PASS WITH_WAIVERS; security review independence; architecture-before-implementation ordering), vulnerability-response chain, hooks (read-only deny, gate/waiver deny for workers, git deny, Stop block/allow), result contract validation, secrets scanner, classify hints, spawn dry-run, dependency serialization, --write refusal, downgrade justification, audit hash chain.

## Remaining gaps (explicit)

- **Terminal backend**: cmux (installed 2026-09-05, v0.64.22) is the primary backend via its socket CLI. Its default socket mode only admits cmux child processes, so the orchestrator must be started inside a cmux tab; from other terminals the harness falls back to Ghostty keystrokes (Accessibility permission), iTerm, Terminal.app, tmux, or background mode. Live cmux spawning could only be verified to the extent the socket admitted this build session (see IMPLEMENTATION-REPORT).
- **Principal identity is by agent definition, not cryptographic.** Two tasks using different agent names are treated as independent principals because they are separate sessions with separate prompts and no shared context; there is no signing of result records. Result digests are recorded in the audit chain.
- **Dependency-review evidence binds to the task's revision but the gate does not yet recompute a manifest/lock digest at gate time**; it re-requires dependency review only if manifests are changed versus HEAD without any passing dependency-review result.
- **Scanners are heuristics.** `harness scan secrets` and `scan deps` are regex/diff based. Real SAST/SCA/SBOM tooling must be present in the repository for stronger evidence; agents record `not_run` otherwise.
- **Worker permission mode** defaults to `auto`; in a repository where auto mode is unavailable, set `worker_permission_mode` to `acceptEdits` (workers then prompt in their tab for Bash) or, for sandboxes, `bypassPermissions`.
- **No cross-session messaging** is used; coordination is file-based (`result.json`, `harness wait`). This keeps the orchestrator's tab free and the protocol inspectable, at the cost of a polling delay (default 10 s).
- **Human approval and waivers are single-principal** (`human:<name>`); there is no multi-approver quorum.
- Emergency and rollback workflows are documented procedures the orchestrator follows; they have no additional automation beyond `VULNERABILITY_RESPONSE` mode and the standard chain.
