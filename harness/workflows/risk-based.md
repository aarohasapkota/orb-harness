# Risk-based team flow (default)

Depth scales with the risk level. Every stage maps to task roles the gate checks.

```
Classify ─▶ settle the design with the human (brief.md) ─▶ [R2+] Blueprint (Opus: BP: comments in code + tests, security baseline)
   ─▶ Implementation (secure-coding) ─▶ tests pass ─▶ harness blueprint strip ─▶ tests pass again
   ─▶ Review round, once, in parallel:  code-review │ test-verification │ [R2+] security-review
   ─▶ orchestrator merges findings: fix now / follow-up (harness followup; never for critical)
   ─▶ [if anything to fix] one fix pass ─▶ one final-review (closure + regression only)
   ─▶ Gate ─▶ PASS → report → harness blueprint commit-backup   /   [R3] human approval first
Weekly: /security-weekly (threat model, security tests, secure defaults, dependencies, build, release)
```

| Risk | Stages |
|---|---|
| R0 | implement (orchestrator or secure-coding) → code-review → gate |
| R1 | implement → code-review ∥ test-verification → [fix → final-review] → gate |
| R2 | blueprint → implement + strip → code-review ∥ security-review ∥ test-verification → [fix → final-review] → gate |
| R3 | as R2, medium findings block unless deferred by the orchestrator, then human approval |

Findings flow forward, never back into another planning round. After two failed fix rounds on the same problem the run stops and goes to the human.
