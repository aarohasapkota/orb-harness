---
id: project.policy
version: "1"
source: "this repository"
priority: 1-project
applies_when: [always]
agents: ["*"]
---
# Project policy overlay (copy to <repo>/.harness/policy/project-pack.md and edit)

Rules here can ADD requirements or make baseline ones stricter. They cannot weaken a baseline MUST.

| ID | Strength | Requirement |
|---|---|---|
| PROJ-01 | MUST | Run `<your test command>` before any result is written. |
| PROJ-02 | MUST | Never modify files under `<protected paths>` without an R3 run. |
| PROJ-03 | SHOULD | Follow `<style/lint>` conventions. |

## SDLC declaration (optional)
`sdlc: agile+devsecops` — one of `agile`, `waterfall`, `devsecops`, `agile+devsecops`, `risk-based`. The orchestrator honors this over its default.
