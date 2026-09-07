# Waterfall workflow

Formal sequential phases with explicit phase gates. Select only when policy/contract requires sequential approvals or the repo declares `sdlc: waterfall`.

Requirements Gate (requirements PASS, human ack) → Design Gate (threat-model PASS, architecture-review PASS) → Implementation Gate (secure-coding + dependency/build evidence) → Verification Gate (test-verification, code-review, security-testing, security-review PASS) → Release Gate (release-integrity, human approval).

Rules: an earlier required phase may never be bypassed because implementation already began; discoveries in Verification return work to the invalidated phase and re-run downstream phases; each phase gate is recorded in the run's `run.json` `workflow.stages` with its evidence.
