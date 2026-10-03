# orb-harness — user guide

## Daily use

You are the technical CEO; the harness is your engineering team.

1. Open **cmux**, open a tab in your project folder and start `claude`. That session is your **tech lead** (Fable 5.1). It stays yours; it never blocks on workers.
2. Say what you want in plain language, or `/harness <request>`. Settle the architecture and integration choices with the tech lead; it writes them into a brief.
3. The tech lead splits the work into small runs and gives each a risk level: R0 docs, R1 small local change, R2 medium (outside input, data, dependencies, public interfaces), R3 high (login, permissions, secrets, releases, infrastructure, AI tool use).
4. For R2 and R3 an **Opus** worker writes the spec as `BP:` comments into the code and test files. A **Sonnet** engineer builds under them. When tests pass, the comments are removed from the code, kept in the tests, and backed up under `blueprints/<run-id>/`.
5. **Three Sonnet reviewers** look once, in parallel (correctness, security, tests). The tech lead merges what they found, decides what is fixed now and what becomes follow-up, runs **one fix**, then **one final review**. Workers open as cmux tabs named `<task-id> <agent>`; don't type into them.
6. The final check (`harness gate`) gives one of:
   - `PASS` → a plain-language report, and the blueprint backup is committed (only that folder, never pushed).
   - `FAIL` → one more fix and final review at most, then it comes to you.
   - `NEEDS_HUMAN` → R3 changes need your sign-off: `! harness approve --run <id> --by human:<you>`.
7. Once a week, when the banner says it is due, run `/security-weekly` for the deep security pass.

## One-time setup

- `harness doctor` — checks the CLI, agents, packs, hooks, and which terminal backend will be used. `harness doctor --tab-test` opens a throwaway tab to prove spawning works (run it inside cmux).
- cmux: `brew install --cask cmux` (installed). Its CLI talks to cmux over a Unix socket, so **no Accessibility permission is needed**. Start `claude` from inside a cmux tab so the harness can reach the socket (cmux's default socket mode only accepts its own child processes). Ghostty (⌘T keystrokes, needs Accessibility), iTerm, Terminal.app, tmux and a background mode remain as fallbacks.
- Optional per-repo policy: copy `~/.claude/harness/templates/project-pack.md` to `<repo>/.harness/policy/project-pack.md`.

## Configuration (`~/.claude/harness/config.json`)

`worker_model` (sonnet) · `worker_effort` (high) · `agent_models` (per agent; `blueprint` ships as `claude-opus-4-7`) · `agent_efforts` (per agent; reviewers ship as medium) · `worker_permission_mode` (auto | acceptEdits | bypassPermissions) · `terminal` (auto | cmux | ghostty | iterm | terminal | tmux | bg; auto prefers cmux) · `return_to_main_tab` (true) · Ghostty tab key bindings · `max_remediation_cycles` (2) · `r3_requires_human_approval` (true).

## Commands you may type yourself

`! harness status` · `! harness report` · `! harness blueprint check` · `! harness approve --by human:<you>` · `! harness waiver ...` · `! harness runs` · `! harness doctor`

Workers cannot run gate, waiver, approve, followup or the backup commit, and cannot commit or push; hooks block it.

## Tests

`python3 ~/.claude/harness/tests/test_gate.py` (70 checks; tests the copy it sits in)
