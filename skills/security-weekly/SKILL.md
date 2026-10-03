---
name: security-weekly
description: Weekly deep security review of the project, the job a security engineer does on a small team. Covers the last 7 days of changes (or a range you give) with a threat model, real security tests, secure-defaults, dependency, build and release checks, then writes a plain-language report and turns findings into small change requests. Usage: /security-weekly [since, e.g. "14 days ago" or a commit].
---
# /security-weekly [since]

Per-change reviews stay light on purpose: the blueprint sets the security baseline and one security reviewer checks it. This weekly pass is where the deep work happens. It reads and tests; it changes no product code.

1. Scope. `since` = `$ARGUMENTS` or "7 days ago". List what changed: `git log --since="<since>" --stat --no-merges` and the run folders under `.harness/runs/` from that period (their reports, follow-ups recorded with `harness followup`, and blueprint backups under `blueprints/`). If nothing changed, write a one-paragraph report saying so and stop.
2. Open a run: `harness run new --request "Weekly security review since <since>" --mode READ_ONLY`, then set the highest risk level seen that week so the workers load the right practice packs (`harness run set risk=R? ...`).
3. Spawn these read-only workers together, each with the change list, the week's briefs and the repo map as inputs, and wait in the background:
   - `threat-modeling` (role `threat-model`): what the week's changes expose, ranked, with a mitigation for each.
   - `security-testing` (role `security-testing`): run negative and abuse tests against the current code for those threats and for every protected action touched that week.
   - `secure-defaults` (role `secure-defaults`): settings added or changed that week.
   - `dependency-vetting` (role `dependency-review`) only if manifests or lockfiles changed.
   - `build-security` / `release-integrity` only if build, CI or release files changed; `ai-adversarial-testing` only if AI prompts, tools or agents changed.
   Tell each worker: a problem in shipped code is a finding; do not fail the review for work that was never planned.
4. Merge the findings, drop duplicates, and rank them. You are the tech lead: say which need a fix this week and which can wait, and why. Critical findings are never "later".
5. Write `security-reviews/<YYYY-MM-DD>.md` in the project: what was checked, what was tested (commands and results), findings in plain language (what could happen, to whom, how likely), the week's deferred follow-ups and whether they still stand, and the proposed fixes as small change requests. The session banner uses this file's date to know the review ran.
6. Tell the human the result first: how many findings by severity, the one or two that matter, and the change requests you propose. Start the fixes as normal runs only when they say so. Commit nothing yourself.

To make it automatic, the human can schedule it (for example `/loop 7d /security-weekly`), or simply run it when the banner says it is due.
