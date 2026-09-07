---
name: spawn
description: Spawn one Sonnet worker session into a new Ghostty tab for an existing harness run — creates the work package task and launches it. Usage: /spawn <task-id> <agent> <role> [--write] then the work package text.
---
# /spawn <task-id> <agent> <role> [--write] — <package text>

Parse `$ARGUMENTS` as: task id, agent name (must exist in ~/.claude/agents), role (see `harness task new --help`), optional `--write`, then the work package body. Use the latest run unless a `--run <id>` is present.

1. Write the package to a temp file under the scratchpad, then `harness task new --run <id> --id <task> --agent <agent> --role <role> [--write] --package-file <tmp>`.
2. `harness spawn --run <id> --task <task>` (respects `--depends` if given in the package as `Depends: a,b` — pass it to task new).
3. Start `harness wait --run <id> --task <task>` in the background and tell the human the tab name `<task> <agent>`.
Read-only roles must not get `--write`. Never spawn a second writer whose paths overlap an active writer.
