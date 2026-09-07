#!/usr/bin/env bash
# orb-harness uninstaller — reverses install.sh.
# Removes hooks + env.HARNESS_HOME from settings.json, the orchestrator block from
# ~/.claude/CLAUDE.md (and ~/.codex/AGENTS.md), the harness agents and skills, the CLI
# symlink, and ~/.claude/harness. Project evidence under <project>/.harness/ is never touched.
set -euo pipefail

CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
HARNESS_HOME="$CLAUDE_DIR/harness"
BIN_DIR="${ORB_BIN_DIR:-$HOME/.local/bin}"
CODEX_DIR="${CODEX_HOME:-$HOME/.codex}"
BEGIN_MARK="<!-- orb-harness:begin -->"
END_MARK="<!-- orb-harness:end -->"
YES=0
KEEP_HOME=0

for arg in "$@"; do
  case "$arg" in
    -y|--yes) YES=1 ;;
    --keep-harness-home) KEEP_HOME=1 ;;
    -h|--help) echo "usage: ./uninstall.sh [-y|--yes] [--keep-harness-home]"; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

log()  { printf '\033[1;34m[orb-harness]\033[0m %s\n' "$*"; }

if [ "$YES" = 0 ]; then
  printf 'This removes orb-harness from %s (settings hooks, CLAUDE.md block, agents, skills, %s). Continue? [y/N] ' "$CLAUDE_DIR" "$HARNESS_HOME"
  read -r ans; case "$ans" in y|Y|yes) ;; *) echo "aborted"; exit 1 ;; esac
fi

# settings.json
if [ -f "$CLAUDE_DIR/settings.json" ]; then
  python3 - "$CLAUDE_DIR/settings.json" <<'PY'
import json, shutil, sys, time
p = sys.argv[1]
with open(p, encoding="utf-8") as f: raw = f.read().strip()
s = json.loads(raw) if raw else {}
changed = False
hooks = s.get("hooks", {})
for event in list(hooks):
    kept = [g for g in hooks[event] if not any("harness hook" in (h.get("command") or "") for h in g.get("hooks", []))]
    if len(kept) != len(hooks[event]): changed = True
    if kept: hooks[event] = kept
    else: del hooks[event]
if "hooks" in s and not hooks: del s["hooks"]
env = s.get("env", {})
if "HARNESS_HOME" in env:
    del env["HARNESS_HOME"]; changed = True
    if not env: del s["env"]
if changed:
    shutil.copy2(p, f"{p}.orb-harness.bak.{time.strftime('%Y%m%d%H%M%S')}")
    with open(p, "w", encoding="utf-8") as f: json.dump(s, f, indent=2); f.write("\n")
    print(f"  removed harness hooks/env from {p}")
else:
    print(f"  no harness entries in {p}")
PY
fi

# marker blocks
remove_block() {
  local target="$1"
  [ -f "$target" ] || return 0
  python3 - "$target" "$BEGIN_MARK" "$END_MARK" <<'PY'
import os, sys
t, b, e = sys.argv[1:4]
with open(t, encoding="utf-8") as f: cur = f.read()
if b in cur and e in cur:
    pre, rest = cur.split(b, 1); _, post = rest.split(e, 1)
    new = (pre.rstrip("\n") + "\n" + post.lstrip("\n")) if pre.strip() or post.strip() else ""
    if new.strip():
        with open(t, "w", encoding="utf-8") as f: f.write(new)
    else:
        os.remove(t)
    print(f"  removed orchestrator block from {t}")
PY
}
remove_block "$CLAUDE_DIR/CLAUDE.md"
remove_block "$CODEX_DIR/AGENTS.md"

# agents + skills (from manifest when present, else the shipped list)
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$HARNESS_HOME/.orb-harness-manifest" ]; then
  while IFS= read -r line; do
    case "$line" in \#*|"") continue ;; esac
    rm -rf "$line"
  done < "$HARNESS_HOME/.orb-harness-manifest"
  log "removed agents and skills listed in the manifest"
else
  for f in "$REPO_DIR"/agents/*.md; do rm -f "$CLAUDE_DIR/agents/$(basename "$f")"; done
  for s in harness spawn gate; do rm -rf "$CLAUDE_DIR/skills/$s"; done
  log "removed shipped agents and skills"
fi

# CLI symlink
if [ -L "$BIN_DIR/harness" ]; then rm -f "$BIN_DIR/harness"; log "removed $BIN_DIR/harness"; fi

# harness home
if [ "$KEEP_HOME" = 1 ]; then
  log "kept $HARNESS_HOME (--keep-harness-home)"
elif [ -d "$HARNESS_HOME" ]; then
  rm -rf "$HARNESS_HOME"; log "removed $HARNESS_HOME"
fi
log "uninstalled. Project evidence under <project>/.harness/ was left in place."
