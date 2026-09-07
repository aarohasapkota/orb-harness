---
name: harness
description: Run a change request through the secure-SDLC harness end to end — open a run, classify risk, create work packages, spawn Sonnet workers into Ghostty tabs, wait in the background, evaluate the gate, and report. Use for any change-producing request ("add", "fix", "implement", "refactor", "migrate", "upgrade", "deploy", "patch vulnerability").
---
# /harness <request>

You are the Engineering Orchestrator (see ~/.claude/CLAUDE.md). Execute the procedure exactly:

1. `harness run new --request "$ARGUMENTS" --mode <CHANGE|VULNERABILITY_RESPONSE|RELEASE>`; note pre-existing changes.
2. Gather targeted context; `harness classify <paths>`; decide change types, flags, ai_scope, languages, risk; `harness run set ...`. State the risk level and why in one line to the human.
3. Read the gate matrix in ~/.claude/harness/workflows/registry.md; create every mandatory task with `harness task new` (work package on stdin, template in CLAUDE.md). Record `na.<role>="reason"` for optional roles you skip.
4. Spawn in dependency order with `harness spawn`; for each wave run `harness wait --run <id> --task <ids>` in the background (`run_in_background: true`). Keep the conversation available. On completion read result summaries and continue; parallelize the read-only verification wave.
5. `harness gate --run <id>`. FAIL → route per `remediation_routes` (retry task with `--retry-of`, re-spawn verifiers after code changes, `--count-cycle`, stop after 2 cycles). NEEDS_HUMAN → give the human the exact `! harness approve ...` / `! harness waiver ...` command and wait for them. PASS → `harness report --run <id>`.
6. Deliver the report (Status, Risk, Summary, Changed, Tested/Verified, Independent Review, Security/Policy, Evidence, Uncertainties, Follow-up).

Never implement R1+ code yourself, never review alone, never approve, never block the tab.
