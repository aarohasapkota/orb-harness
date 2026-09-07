#!/usr/bin/env bash
# orb-harness installer
#
# Installs the Claude Code secure-SDLC harness into ~/.claude:
#   ~/.claude/harness/            control plane (CLI, packs, policy, workflows, schemas, templates, tests, docs)
#   ~/.claude/agents/*.md         23 specialist agent definitions
#   ~/.claude/skills/{harness,spawn,gate}
#   ~/.claude/CLAUDE.md           orchestrator instructions (appended between markers)
#   ~/.claude/settings.json       hooks (SessionStart / PreToolUse / Stop) + env.HARNESS_HOME (merged)
#   ~/.local/bin/harness          symlink to the CLI
# Optional (--codex): ~/.codex/AGENTS.md orchestrator instructions for the Codex CLI.
#
# cmux is REQUIRED: workers are spawned as cmux workspaces over its Unix socket.
#
# Every change is reversible with ./uninstall.sh. Existing settings, CLAUDE.md content
# and an existing ~/.claude/harness/config.json are preserved.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
HARNESS_HOME="$CLAUDE_DIR/harness"
BIN_DIR="${ORB_BIN_DIR:-$HOME/.local/bin}"
CODEX_DIR="${CODEX_HOME:-$HOME/.codex}"
BEGIN_MARK="<!-- orb-harness:begin -->"
END_MARK="<!-- orb-harness:end -->"

INSTALL_CODEX=0
SKIP_CMUX=0
DRY_RUN=0
RUN_DOCTOR=1

usage() {
  cat <<USAGE
usage: ./install.sh [--codex] [--skip-cmux-check] [--dry-run] [--no-doctor]

  --codex             also install orchestrator instructions for the Codex CLI (~/.codex/AGENTS.md)
  --skip-cmux-check   install even if the cmux CLI is missing (spawning will NOT work until cmux is installed)
  --dry-run           print what would change, change nothing
  --no-doctor         skip the final 'harness doctor'

Environment: CLAUDE_CONFIG_DIR (default ~/.claude), ORB_BIN_DIR (default ~/.local/bin), CODEX_HOME (default ~/.codex)
USAGE
}

for arg in "$@"; do
  case "$arg" in
    --codex) INSTALL_CODEX=1 ;;
    --skip-cmux-check) SKIP_CMUX=1 ;;
    --dry-run) DRY_RUN=1 ;;
    --no-doctor) RUN_DOCTOR=0 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $arg" >&2; usage; exit 2 ;;
  esac
done

log()  { printf '\033[1;34m[orb-harness]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[orb-harness] WARNING:\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[orb-harness] ERROR:\033[0m %s\n' "$*" >&2; exit 1; }
run()  { if [ "$DRY_RUN" = 1 ]; then echo "  (dry-run) $*"; else "$@"; fi; }

# ---------------------------------------------------------------- prerequisites
[ -d "$REPO_DIR/harness/bin" ] && [ -d "$REPO_DIR/agents" ] || die "run this script from a clone of orb-harness"

case "$(uname -s)" in
  Darwin) ;;
  *) warn "orb-harness is built for macOS (cmux is macOS-only). Continuing, but spawning into tabs will not work." ;;
esac

command -v python3 >/dev/null 2>&1 || die "python3 is required (the harness CLI is Python; 3.9+)"
python3 - <<'PY' || die "python3 >= 3.9 is required"
import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)
PY

if ! command -v claude >/dev/null 2>&1 && [ ! -x "$HOME/.local/bin/claude" ]; then
  warn "Claude Code CLI ('claude') not found on PATH. Install it first: https://docs.claude.com/en/docs/claude-code  (workers are Claude Code sessions)"
fi

if ! command -v cmux >/dev/null 2>&1; then
  if [ "$SKIP_CMUX" = 1 ]; then
    warn "cmux CLI not found; continuing because --skip-cmux-check was given. Install it with: brew install --cask cmux"
  else
    die "cmux is required (workers open as cmux workspaces). Install it with:  brew install --cask cmux
       then start 'claude' from inside a cmux tab. To install anyway: ./install.sh --skip-cmux-check"
  fi
fi

# ------------------------------------------------------------------ files
log "installing into $CLAUDE_DIR"
run mkdir -p "$CLAUDE_DIR/agents" "$CLAUDE_DIR/skills" "$HARNESS_HOME" "$BIN_DIR"

# harness control plane: replace every shipped directory, keep runtime state (launch/) and an existing config.json
for d in bin packs policy schemas templates tests workflows docs; do
  run rm -rf "$HARNESS_HOME/$d"
  run cp -R "$REPO_DIR/harness/$d" "$HARNESS_HOME/$d"
done
run cp "$REPO_DIR/harness/README.md" "$HARNESS_HOME/README.md"
run chmod 755 "$HARNESS_HOME/bin/harness"
if [ -f "$HARNESS_HOME/config.json" ]; then
  log "keeping existing $HARNESS_HOME/config.json (shipped version saved as config.json.dist)"
  run cp "$REPO_DIR/harness/config.json" "$HARNESS_HOME/config.json.dist"
else
  run cp "$REPO_DIR/harness/config.json" "$HARNESS_HOME/config.json"
fi

# agents and skills
run cp "$REPO_DIR"/agents/*.md "$CLAUDE_DIR/agents/"
for s in harness spawn gate; do
  run rm -rf "$CLAUDE_DIR/skills/$s"
  run cp -R "$REPO_DIR/skills/$s" "$CLAUDE_DIR/skills/$s"
done

# manifest for uninstall
if [ "$DRY_RUN" = 0 ]; then
  {
    echo "# files installed by orb-harness $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    for f in "$REPO_DIR"/agents/*.md; do echo "$CLAUDE_DIR/agents/$(basename "$f")"; done
    for s in harness spawn gate; do echo "$CLAUDE_DIR/skills/$s"; done
  } > "$HARNESS_HOME/.orb-harness-manifest"
fi

# CLI symlink
run ln -sfn "$HARNESS_HOME/bin/harness" "$BIN_DIR/harness"
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) warn "$BIN_DIR is not on your PATH. Add:  export PATH=\"$BIN_DIR:\$PATH\"" ;;
esac

# ------------------------------------------------------------ settings.json
merge_settings() {
  python3 - "$CLAUDE_DIR/settings.json" "$REPO_DIR/claude/hooks.json" "$HARNESS_HOME" "$DRY_RUN" <<'PY'
import json, os, shutil, sys, time
settings_path, hooks_path, harness_home, dry = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] == "1"
settings = {}
if os.path.exists(settings_path):
    with open(settings_path, encoding="utf-8") as f:
        raw = f.read().strip()
    settings = json.loads(raw) if raw else {}
with open(hooks_path, encoding="utf-8") as f:
    shipped = json.load(f)["hooks"]

hooks = settings.setdefault("hooks", {})
added = 0
for event, groups in shipped.items():
    existing = hooks.setdefault(event, [])
    have = {h.get("command") for g in existing for h in g.get("hooks", [])}
    for g in groups:
        cmds = {h.get("command") for h in g.get("hooks", [])}
        if cmds & have:
            continue
        existing.append(g); added += 1
env = settings.setdefault("env", {})
env["HARNESS_HOME"] = harness_home

if dry:
    print(f"  (dry-run) would add {added} hook group(s) and env.HARNESS_HOME to {settings_path}")
    sys.exit(0)
if os.path.exists(settings_path):
    backup = f"{settings_path}.orb-harness.bak.{time.strftime('%Y%m%d%H%M%S')}"
    shutil.copy2(settings_path, backup)
    print(f"  backup: {backup}")
os.makedirs(os.path.dirname(settings_path), exist_ok=True)
tmp = settings_path + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(settings, f, indent=2); f.write("\n")
os.replace(tmp, settings_path)
print(f"  hooks merged into {settings_path} ({added} new group(s); existing entries untouched)")
PY
}
log "merging hooks into settings.json"
merge_settings

# ------------------------------------------------------------- CLAUDE.md
install_block() {  # $1 target file, $2 source file
  local target="$1" source="$2"
  if [ "$DRY_RUN" = 1 ]; then echo "  (dry-run) would install block into $target"; return; fi
  python3 - "$target" "$source" "$BEGIN_MARK" "$END_MARK" <<'PY'
import os, sys
target, source, b, e = sys.argv[1:5]
with open(source, encoding="utf-8") as f: body = f.read().rstrip("\n")
block = f"{b}\n{body}\n{e}\n"
cur = ""
if os.path.exists(target):
    with open(target, encoding="utf-8") as f: cur = f.read()
if b in cur and e in cur:
    pre, rest = cur.split(b, 1); _, post = rest.split(e, 1)
    new = pre + block.rstrip("\n") + post
    action = "updated"
else:
    new = (cur.rstrip("\n") + "\n\n" if cur.strip() else "") + block
    action = "appended"
os.makedirs(os.path.dirname(target), exist_ok=True)
with open(target, "w", encoding="utf-8") as f: f.write(new)
print(f"  {action} orchestrator block in {target}")
PY
}
log "installing orchestrator instructions"
install_block "$CLAUDE_DIR/CLAUDE.md" "$REPO_DIR/claude/CLAUDE.md"
if [ "$INSTALL_CODEX" = 1 ]; then
  install_block "$CODEX_DIR/AGENTS.md" "$REPO_DIR/codex/AGENTS.md"
fi

# ---------------------------------------------------------------- finish
if [ "$DRY_RUN" = 1 ]; then log "dry run complete; nothing was changed"; exit 0; fi
log "installed."
if [ "$RUN_DOCTOR" = 1 ]; then
  echo
  HARNESS_HOME="$HARNESS_HOME" "$HARNESS_HOME/bin/harness" doctor || warn "harness doctor reported problems (see above)"
fi
cat <<NEXT

Next steps
  1. Open cmux, open a tab in a project directory, run:  claude
     (the SessionStart hook prints "[harness] orchestrator session")
  2. Ask for a change in plain language or type:  /harness <request>
  3. Inside cmux run  harness doctor --tab-test  once to prove worker tabs open.
  Uninstall any time with:  $REPO_DIR/uninstall.sh
NEXT
