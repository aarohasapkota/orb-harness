# orb-harness

An AI engineering team for a technical founder. You set the requirements and the architecture. One always-available **tech lead** session (Claude Code running Fable 5.1, or the Codex CLI) works the design out with you, splits the work into small changes, and runs a team that behaves like a good 5–10 person startup team:

- **Opus writes the spec.** For medium and high risk changes a `blueprint` worker writes pseudocode comments (`# BP: ...`) into every code and test file the change needs, including the security rules for that change. Nothing is left for the coder to design.
- **Sonnet builds.** A `secure-coding` worker writes the code under the comments. When the tests pass, `harness blueprint strip` removes the comments from the code, keeps them in the tests, and backs the originals up under `blueprints/<run>/` (committed to git, so the specs have a history).
- **Three peers review once, in parallel**: correctness, security (it attacks the change, not just reads it), tests and failure paths. The tech lead merges the findings and decides what is fixed now and what becomes follow-up. One fix pass, then **one final review** that only checks the fixes. No review loops.
- **A deterministic final check (`harness gate`)** decides pass or fail from evidence files, not from anyone's say-so. High-risk changes need your approval. Critical findings can never be waved through.
- **Security goes deep once a week** (`/security-weekly`): threat model, real security tests, defaults, dependencies, build and release. NIST SSDF (SP 800-218 / 218A) and OWASP stay the reference, through practice packs the blueprint and the reviewers read, without putting a dozen gatekeepers in front of every change.

```
you ──▶ tech lead (Fable / Codex) ──▶ harness run new · classify · brief
                              ──▶ cmux tab: bp-1   blueprint       (Opus, writes BP: comments)
                              ──▶ cmux tab: impl-1 secure-coding   (Sonnet, builds, strips)
                              ──▶ cmux tabs: cr-1 │ sr-1 │ tv-1     (Sonnet reviewers, in parallel, once)
                              ──▶ one fix pass ──▶ fr-1 final-review
                              ──▶ harness gate ──▶ PASS / FAIL / NEEDS_HUMAN ──▶ harness report
weekly ──▶ /security-weekly
```

## Requirements

| | |
|---|---|
| macOS | cmux is macOS-only |
| **cmux** | **Required.** `brew install --cask cmux`. Workers are spawned as cmux workspaces over its Unix socket, so start the orchestrator from inside a cmux tab. |
| Claude Code CLI | Workers are `claude` sessions: Sonnet for engineers and reviewers, Opus 4.7 for the blueprint (`agent_models` in `config.json`). Fable if you run the tech lead in Claude Code. |
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
- copies 25 agent definitions to `~/.claude/agents/` and the `/harness`, `/spawn`, `/gate`, `/security-weekly` skills to `~/.claude/skills/`;
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

- **Risk levels.** R0 docs only · R1 small local change · R2 outside input, a public interface, data, a new dependency, a migration, CI config · R3 login, permissions, crypto, secrets, releases, infrastructure, AI tool use, destructive data work. `harness classify` gives hints the tech lead may raise but not lower without a reason.
- **Who works on what** (`harness/workflows/registry.md`). R0: a writer and one reviewer. R1: engineer, then two reviewers in parallel. R2 and R3: blueprint, engineer, three reviewers in parallel; R3 also needs your approval. A final review is required only when the reviewers' findings led to a fix. Dependency vetting joins whenever a package changes. Every other specialist (threat modeling, architecture review, security testing, migrations, CI/CD and more) is on call, and most run in the weekly security review.
- **Tech-lead authority.** The tech lead may record any non-critical finding as follow-up with a reason (`harness followup`); it stops blocking and shows up in the report. Critical findings can never be deferred or waived.
- **Independence.** Nobody reviews their own work. The blueprint author and the final reviewer are never first-round reviewers. Reviewers cannot edit code. A `PreToolUse` hook enforces this by reading the command that would actually run, so a worker writing a document that mentions `git commit` is not blocked, but a worker running it is. Blueprint workers can only write inside the paths the tech lead gave them, and no worker can edit the files that define its own task, commit, or push.
- **Evidence.** Each worker writes `result.json` with commands, exit codes and findings; the `Stop` hook validates it. Everything lives under `<project>/.harness/runs/<run-id>/` with a hash-chained audit log. Workers also report what slowed them down (`friction`), and the tech lead turns that into proposed prompt and hook fixes in `~/.claude/harness/lessons.md`.
- **Plain language.** The tech lead and the workers are instructed to put the answer first, use everyday words, explain any harness term the first time it appears, and describe behaviour instead of mechanics. `harness report` says what the status and the risk level mean in plain words.
- **Practice packs** (`harness/packs/`). Eighteen technology and domain packs resolved per task by `harness packs`. Add a project overlay by copying `harness/templates/project-pack.md` to `<repo>/.harness/policy/project-pack.md`.

## Repository layout

```
install.sh · uninstall.sh
harness/            control plane installed to ~/.claude/harness
  bin/harness       the CLI (Python, stdlib only)
  packs/ policy/ workflows/ schemas/ templates/ tests/ docs/ config.json README.md
agents/             25 agent definitions installed to ~/.claude/agents
skills/             /harness /spawn /gate /security-weekly installed to ~/.claude/skills
claude/CLAUDE.md    orchestrator instructions appended to ~/.claude/CLAUDE.md
claude/hooks.json   the hooks merged into ~/.claude/settings.json
codex/AGENTS.md     orchestrator instructions for the Codex CLI (--codex)
docs/spec/          the design documents the harness was built from
docs/IMPLEMENTATION-REPORT.md
```

Tests: `python3 harness/tests/test_gate.py`.

## Configuration

`~/.claude/harness/config.json`: `worker_model` (sonnet), `worker_effort` (high), `agent_models` (per-agent model, ships with `blueprint: claude-opus-4-7`), `agent_efforts` (per-agent effort; reviewers default to medium), `worker_permission_mode` (auto | acceptEdits | bypassPermissions), `terminal` (cmux), `cmux_focus_new_workspace` (false), `max_remediation_cycles` (2), `r3_requires_human_approval` (true). An existing config is kept on reinstall: new keys are added, your values are never changed, and the shipped file is saved beside it as `config.json.dist`.

## Things to know before installing

- The hooks are global to your Claude Code installation. In sessions with no harness run they only print a one-line banner; in worker sessions they enforce read-only roles and validate results.
- Workers run with `worker_permission_mode: auto` by default. Set `acceptEdits` in `config.json` if you want to approve every command in worker tabs yourself.
- The per-change flow is deliberately lighter than a full SSDF pipeline: deep security work is weekly, and the tech lead can defer non-critical findings. If you need every change to carry a threat model and security testing, add those roles to a project policy in `.harness/policy/gate-policy.json`.
- The orchestrator instructions tell the model to never write R1+ code itself, never self-review, and never approve or waive. Those are policy, enforced by the gate and hooks, not by trust in the model.
- A PASS means the policy was satisfied for that revision with the evidence recorded. It is not a proof that the code is bug-free.

## License

MIT. See `LICENSE`.
