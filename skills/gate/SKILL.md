---
name: gate
description: Evaluate the harness policy gate for the current run and print the final report; routes failures. Usage: /gate [run-id].
---
# /gate [run-id]

1. `harness status --run <id>` — confirm every spawned task has a result; if some are pending, say which tabs are still working and stop (do not gate half-done work).
2. `harness gate --run <id>`; interpret exit code: 0 PASS, 1 FAIL, 2 NEEDS_HUMAN, 3 NOT_APPLICABLE.
3. FAIL: list `reason_codes` and `remediation_routes`; propose the retry tasks (role, findings) and, unless the human objects, create/spawn them (`--retry-of`), re-spawning read-only verifiers after code changes; `harness gate --count-cycle` on the next evaluation; stop after 2 cycles.
4. NEEDS_HUMAN: print the exact human command (`! harness approve --run <id> --by human:<name>` or `! harness waiver --run <id> --finding <F> --reason "..." --approved-by human:<name>`). Do not run it.
5. PASS: `harness report --run <id>`; deliver it verbatim plus a two-line plain-language summary.
