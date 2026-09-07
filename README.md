# orb-harness

A secure-SDLC harness for AI-assisted coding. One always-available **orchestrator** session (Claude Code running Fable 5.1, or the Codex CLI) talks to you, classifies each change by risk (R0–R3), and delegates the work to specialist **worker** sessions that open as tabs in [cmux](https://www.cmux.dev/). A deterministic **gate** decides whether the change passed, based on evidence files rather than anyone's say-so. You alone can approve or waive.

The design follows NIST SSDF (SP 800-218) and its AI profile (SP 800-218A): requirements, threat modeling, secure implementation, independent review, security testing, secure defaults, release integrity, and vulnerability response each have a dedicated agent, a practice pack, and a place in the gate matrix.

```
you ──▶ orchestrator (Fable / Codex) ──▶ harness run new · classify · task new
                                    ──▶ harness spawn ──▶ cmux tab: req-1 requirements   (Sonnet)
                                                     ──▶ cmux tab: tm-1  threat-modeling (Sonnet)
                                                     ──▶ cmux tab: impl-1 secure-coding  (Sonnet, write)
                                                     ──▶ cmux tab: cr-1  code-review     (Sonnet)  …
                                    ──▶ harness gate ──▶ PASS / FAIL / NEEDS_HUMAN
                                    ──▶ harness report
```

## Requirements

| | |
|---|---|
| macOS | cmux is macOS-only |
| **cmux** | **Required.** `brew install --cask cmux`. Workers are spawned as cmux workspaces over its Unix socket, so start the orchestrator from inside a cmux tab. |
| Claude Code CLI | Workers are `claude` sessions (`--model sonnet --effort high`). Needs an account with access to Sonnet, and to Fable if you run the orchestrator in Claude Code. |
| python3 ≥ 3.9 | The `harness` CLI is a single Python file with no third-party dependencies. |
| Codex CLI (optional) | To drive the harness from Codex instead of Claude Code, see below. |

## Install

```bash
git clone https://github.com/aarohasapkota/orb-harness.git
cd orb-harness
./install.sh            # add --codex to also install the Codex orchestrator instructions
```

The installer is idempotent and reversible. It:

- copies the control plane to `~/.claude/harness/` (CLI, 18 practice packs, gate policy, 6 workflow definitions, schemas, templates, tests, docs);
- copies 23 agent definitions to `~/.claude/agents/` and the `/harness`, `/spawn`, `/gate` skills to `~/.claude/skills/`;
- appends the orchestrator instructions to `~/.claude/CLAUDE.md` between `<!-- orb-harness:begin/end -->` markers, leaving your own content alone;
- merges three hooks (`SessionStart`, `PreToolUse`, `Stop`) and `env.HARNESS_HOME` into `~/.claude/settings.json` after taking a timestamped backup;
- symlinks `~/.local/bin/harness`;
- runs `harness doctor`.

Use `./install.sh --dry-run` to see the changes first. `./uninstall.sh` reverses all of it (project evidence under `<project>/.harness/` is left in place).

## Use

**From Claude Code.** Open cmux, open a tab in your project, run `claude`. The session banner says `[harness] orchestrator session`. Then either ask for a change in plain language or type:

```
/harness add rate limiting to the login endpoint
```

The orchestrator opens a run, states the risk level, creates work packages, and spawns workers into new cmux tabs named `<task-id> <agent>` without stealing focus. When they finish it runs the gate and prints the report. Useful commands you can type yourself:

```
! harness status
! harness report
! harness approve --run <id> --by human:<you>          # R3 changes always need this
! harness waiver --run <id> --finding F-1 --reason "..." --approved-by human:<you>
! harness doctor --tab-test                              # prove worker tabs open
```

**From the Codex CLI.** Install with `--codex`, which appends the orchestrator instructions to `~/.codex/AGENTS.md`. Start `codex` inside a cmux tab in your project and ask for a change. Codex drives the same `harness` CLI; workers are still Claude Code sessions, so the Claude Code CLI must be installed and authenticated.

**From any other agent.** The `harness` CLI never calls a model and has no dependency on who is orchestrating. Point your agent at `codex/AGENTS.md` for the procedure, and at `harness --help` for the commands.

## How it works

- **Risk classes.** R0 docs only · R1 localized change · R2 externally reachable, untrusted input, new dependency, migration, CI config · R3 auth, crypto, secrets, release trust, infra privileges, LLM tool calling, destructive data ops. The orchestrator classifies; `harness classify` gives deterministic hints it may raise but never lower without justification.
- **Gate matrix** (`harness/workflows/registry.md`). Each risk level has mandatory roles. R1 needs requirements, implementer, test-verification and code-review. R2 adds threat-model, security-review, security-testing and a secrets scan. R3 adds architecture-review, secure-defaults and human approval.
- **Separation of duties.** Every worker runs as its own principal. The `PreToolUse` hook makes review roles read-only for product code and blocks workers from running `harness gate`, `waiver`, `approve` or editing the run's classification. Reviews are bound to the exact revision they looked at; stale evidence is rejected.
- **Evidence.** Each worker writes `result.json` (schema `harness-result/1`) with commands, exit codes, findings and a requirement-to-change map; the `Stop` hook validates it. Everything lives under `<project>/.harness/runs/<run-id>/` with a hash-chained audit log.
- **Practice packs** (`harness/packs/`). Eighteen technology and domain packs (web/API, auth, crypto, dependencies, CI/CD, containers, IaC, data/migration, AI/agent security, and more) resolved per task by `harness packs`. Add a project overlay by copying `harness/templates/project-pack.md` to `<repo>/.harness/policy/project-pack.md`.

## Repository layout

```
install.sh · uninstall.sh
harness/            control plane installed to ~/.claude/harness
  bin/harness       the CLI (Python, stdlib only)
  packs/ policy/ workflows/ schemas/ templates/ tests/ docs/ config.json README.md
agents/             23 agent definitions installed to ~/.claude/agents
skills/             /harness /spawn /gate installed to ~/.claude/skills
claude/CLAUDE.md    orchestrator instructions appended to ~/.claude/CLAUDE.md
claude/hooks.json   the hooks merged into ~/.claude/settings.json
codex/AGENTS.md     orchestrator instructions for the Codex CLI (--codex)
docs/spec/          the design documents the harness was built from
docs/IMPLEMENTATION-REPORT.md
```

Tests: `python3 harness/tests/test_gate.py`.

## Configuration

`~/.claude/harness/config.json`: `worker_model` (sonnet), `worker_effort` (high), `worker_permission_mode` (auto | acceptEdits | bypassPermissions), `terminal` (cmux), `cmux_focus_new_workspace` (false), `max_remediation_cycles` (2), `r3_requires_human_approval` (true). An existing config is kept on reinstall; the shipped one is saved beside it as `config.json.dist`.

## Things to know before installing

- The hooks are global to your Claude Code installation. In sessions with no harness run they only print a one-line banner; in worker sessions they enforce read-only roles and validate results.
- Workers run with `worker_permission_mode: auto` by default. Set `acceptEdits` in `config.json` if you want to approve every command in worker tabs yourself.
- The orchestrator instructions tell the model to never write R1+ code itself, never self-review, and never approve or waive. Those are policy, enforced by the gate and hooks, not by trust in the model.
- A PASS means the policy was satisfied for that revision with the evidence recorded. It is not a proof that the code is bug-free.

## License

MIT. See `LICENSE`.
