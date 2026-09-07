# Claude Code secure-SDLC harness — user guide

## Daily use

1. Open **cmux** (Ghostty-based terminal with vertical tabs), open a tab in your project folder and start `claude`. That session is the **orchestrator** (Fable 5.1). It stays yours; it never blocks on workers.
2. Ask for a change in plain language, or `/harness <request>`.
3. The orchestrator opens a run, classifies risk (R0–R3), creates work packages, and spawns Sonnet (effort high) workers **into new cmux workspaces (vertical tabs)** named `<task-id> <agent>`, without stealing focus. Each shows a `harness` status pill; a cmux notification fires when a worker finishes. Watch them if you like; don't type into them.
4. When workers finish, the orchestrator runs the gate. You will see one of:
   - `PASS` → final report (what changed, what was verified, who reviewed, evidence paths).
   - `FAIL` → it routes fixes to the right worker and re-verifies (max 2 cycles), then reports BLOCKED if still failing.
   - `NEEDS_HUMAN` → it asks you for a decision and gives you the exact command, e.g. `! harness approve --run <id> --by human:<you>` (R3 changes always need this) or `! harness waiver --run <id> --finding F-1 --reason "..." --approved-by human:<you>`.
5. `harness status` / `/gate` any time. Everything is under `<project>/.harness/runs/<run-id>/`.

## One-time setup

- `harness doctor` — checks the CLI, agents, packs, hooks, and which terminal backend will be used. `harness doctor --tab-test` opens a throwaway tab to prove spawning works (run it inside cmux).
- cmux: `brew install --cask cmux` (installed). Its CLI talks to cmux over a Unix socket, so **no Accessibility permission is needed**. Start `claude` from inside a cmux tab so the harness can reach the socket (cmux's default socket mode only accepts its own child processes). Ghostty (⌘T keystrokes, needs Accessibility), iTerm, Terminal.app, tmux and a background mode remain as fallbacks.
- Optional per-repo policy: copy `~/.claude/harness/templates/project-pack.md` to `<repo>/.harness/policy/project-pack.md`.

## Configuration (`~/.claude/harness/config.json`)

`worker_model` (sonnet) · `worker_effort` (high) · `worker_permission_mode` (auto | acceptEdits | bypassPermissions) · `terminal` (auto | cmux | ghostty | iterm | terminal | tmux | bg; auto prefers cmux) · `return_to_main_tab` (true) · Ghostty tab key bindings · `max_remediation_cycles` (2) · `r3_requires_human_approval` (true).

## Commands you may type yourself

`! harness status` · `! harness report` · `! harness approve --by human:<you>` · `! harness waiver ...` · `! harness runs` · `! harness doctor`

Workers cannot run gate/waiver/approve; hooks block it.

## Tests

`python3 ~/.claude/harness/tests/test_gate.py`
