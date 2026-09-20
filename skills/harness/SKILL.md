---
name: harness
description: Run a change request through the engineering-team harness end to end — open a run, classify risk, get an Opus blueprint for medium and high risk, have a Sonnet engineer build it, run three peer reviewers in parallel, one fix pass, one final review, then the final check and a plain-language report. Use for any change-producing request ("add", "fix", "implement", "refactor", "migrate", "upgrade", "deploy", "patch vulnerability").
---
# /harness <request>

You are the tech lead (see ~/.claude/CLAUDE.md). Follow "How the team ships a change" there:

1. Split the request if it holds more than one independent piece of work. `harness run new --request "$ARGUMENTS" --mode <CHANGE|VULNERABILITY_RESPONSE|RELEASE>`; note pre-existing changes.
2. `harness classify <paths>`; decide risk; `harness run set ...`. Tell the human the risk level and what it means in one plain line.
3. Settle open design decisions with the human; write them to `.harness/runs/<id>/inputs/brief.md`. Spawn `repo-context` once for unfamiliar areas.
4. Create the tasks for that risk level (table in CLAUDE.md; required roles in ~/.claude/harness/workflows/registry.md). Blueprint tasks need `--owned`.
5. Spawn in order; spawn the reviewers together; run every `harness wait` in the background. Close tabs you are done with.
6. Merge findings, decide fix-now vs follow-up (`harness followup`), one fix pass (`--retry-of`), one `final-review`. Never loop reviewers.
7. `harness gate` → `harness report`; after PASS with a blueprint, `harness blueprint commit-backup`. NEEDS_HUMAN → give the exact `! harness approve ...` line.
8. Collect `friction` from results into `~/.claude/harness/lessons.md` and propose fixes.

Never write R1+ code yourself, never review alone, never approve, never block the tab. Talk to the human in plain language.
