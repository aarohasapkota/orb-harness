# Risk-based Agile + DevSecOps (default)

Depth scales with R-level. Every stage maps to task roles the gate checks.

```
Context ─▶ Classify (mode, change types, flags, R-level, ai_scope) ─▶ Requirements
   ─▶ [R2+] Threat model ─▶ [R3] Architecture review (must PASS before implementation)
   ─▶ [conditional] Dependency vetting / Domain specialist (before implementation depends on it)
   ─▶ Implementation (secure-coding, write-capable)  ── the only writer of product code
   ─▶ Verification fan-out (parallel, all read-only, all bound to the same revision):
        test-verification │ code-review │ [R2+] security-testing │ [R2+] security-review
        │ [AI] ai-adversarial-testing │ [cond] build-security │ [R3] secure-defaults
   ─▶ Gate (harness gate) ─▶ PASS → report / FAIL → route → remediate → re-verify (max 2 cycles) / NEEDS_HUMAN → ask
   ─▶ [R3] human approval (harness approve) ─▶ COMPLETE
```

| Risk | Stages executed |
|---|---|
| R0 | context (orchestrator) → implement (orchestrator or secure-coding) → code-review → gate |
| R1 | context → requirements → implement → test-verification ∥ code-review → gate |
| R2 | + threat-model before implementation; + security-testing ∥ security-review after; + domain specialist / dependency-vetting when triggered; secrets scan |
| R3 | + architecture-review PASS before implementation; + secure-defaults; + release-integrity when release path affected; + human approval; medium findings block |

Entry criteria per stage: upstream results PASS (the spawner enforces `--depends`). Exit criteria: result.json validates. Iteration: a FAIL routes to the earliest invalidated stage per the routing matrix in `04-EVIDENCE-AND-GATES` (coding defect → implementation; threat/architecture defect → design; requirement gap → requirements). After remediation, ALL read-only verification re-runs against the new revision (stale evidence is rejected automatically).
