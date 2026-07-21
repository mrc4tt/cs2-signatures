#!/usr/bin/env bash
# vps_regen.sh - headless linux gamedata refresh for a VPS shell (no GUI/desktop).
# ---------------------------------------------------------------------------
# Glues the pieces that already run headless into one command:
#
#   1. VALIDATE   validate_sigs.py  -> reports/<id>/status.json
#                 (pure Python, no IDA): every linux signature + 14/18 offsets,
#                 stale offsets carry the re-derived index (found_linux).
#   2. OFFSETS    apply_offsets.py   -> re-index stale offsets in gamedata.json
#                 (pure Python, no IDA). This IS offset regeneration.
#   3. SIGS opt.  regen_css_linux.py -> relocate + regenerate moved/broken linux
#                 signatures via headless idalib-mcp. Needs an IDA license on the
#                 VPS; skipped unless --regen-sigs and the script is found.
#   4. REPORT     what got re-indexed, what still needs GDT/manual.
#
# Offsets + all validation need NO IDA and run on any Linux shell. Only the
# optional signature regeneration (step 3) needs idalib.
#
# Usage:
#   scripts/vps_regen.sh --project CounterStrikeSharp --linux /path/libserver.so
#   scripts/vps_regen.sh -p CounterStrikeSharp -l ...libserver.so --write
#   scripts/vps_regen.sh -p CounterStrikeSharp -l ... --write --regen-sigs
#
# Flags:
#   -p|--project ID     tracked project (default: CounterStrikeSharp)
#   -l|--linux PATH     libserver.so to check (default: auto = current/newest
#                       build under --bin-root)
#   -g|--gamever N      use bin/<N>/server/libserver.so under --bin-root
#   --bin-root PATH     build root (default: $CS2_VIBE_REPO/bin)
#   --write             apply offset re-indexing to gamedata (default: dry-run)
#   --regen-sigs        also run headless idalib sig regeneration (needs IDA)
#   --vibe-repo PATH    CS2_VibeSignatures checkout (default: $CS2_VIBE_REPO or
#                       ~/CS2_VibeSignatures)
#
# "Current game version" = newest numeric build under --bin-root, picked
# automatically when neither --linux nor --gamever is given. (For the LIVE Steam
# build, run_all.sh already detects the update + downloads the binaries, then
# validate_sigs.py validates sigs AND offsets.)
# ---------------------------------------------------------------------------
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PROJECT="CounterStrikeSharp"
LINUX_SO=""
GAMEVER=""
WRITE=0
REGEN_SIGS=0
VIBE_REPO="${CS2_VIBE_REPO:-$HOME/CS2_VibeSignatures}"
BIN_ROOT=""

while [ $# -gt 0 ]; do
  case "$1" in
    -p|--project) PROJECT="$2"; shift 2;;
    -l|--linux)   LINUX_SO="$2"; shift 2;;
    -g|--gamever) GAMEVER="$2"; shift 2;;
    --bin-root)   BIN_ROOT="$2"; shift 2;;
    --write)      WRITE=1; shift;;
    --regen-sigs) REGEN_SIGS=1; shift;;
    --vibe-repo)  VIBE_REPO="$2"; shift 2;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
done

log() { echo "[vps_regen] $*"; }

BIN_ROOT="${BIN_ROOT:-$VIBE_REPO/bin}"

# Resolve the binary: explicit --linux wins; else --gamever under bin-root; else
# the newest numeric build under bin-root = the current game version.
if [ -z "$LINUX_SO" ]; then
  if [ -z "$GAMEVER" ]; then
    [ -d "$BIN_ROOT" ] || { echo "[vps_regen] bin root not found: $BIN_ROOT (pass --linux or --bin-root)" >&2; exit 2; }
    GAMEVER="$(ls -1 "$BIN_ROOT" 2>/dev/null | grep -E '^[0-9]+$' | sort -n | tail -1)"
    [ -n "$GAMEVER" ] || { echo "[vps_regen] no numeric build under $BIN_ROOT" >&2; exit 2; }
    log "auto-selected current (newest) build: $GAMEVER"
  fi
  LINUX_SO="$BIN_ROOT/$GAMEVER/server/libserver.so"
fi

[ -f "$LINUX_SO" ] || { echo "[vps_regen] not found: $LINUX_SO" >&2; exit 2; }

log "project : $PROJECT"
log "gamever : ${GAMEVER:-(explicit path)}"
log "linux   : $LINUX_SO"
log "mode    : $([ $WRITE -eq 1 ] && echo WRITE || echo dry-run)"

# --- 1. validate (no IDA): sigs + offsets -> status.json --------------------
log "1/3 validate (sigs + offsets, no IDA)"
set +e
python3 scripts/validate_sigs.py --project "$PROJECT" --linux "$LINUX_SO" \
  --manifest data/manifest.json
VAL=$?
set -e

# --- 2. apply re-indexed offsets (no IDA) -----------------------------------
log "2/3 apply stale-offset re-indexing (no IDA)"
APPLY_ARGS=(--project "$PROJECT")
[ $WRITE -eq 1 ] && APPLY_ARGS+=(--write)
python3 scripts/apply_offsets.py "${APPLY_ARGS[@]}"

# --- 3. optional headless signature regeneration (needs idalib/IDA) ---------
if [ $REGEN_SIGS -eq 1 ]; then
  REGEN="$VIBE_REPO/regen_css_linux.py"
  if [ -f "$REGEN" ]; then
    log "3/3 sig regen via headless idalib ($REGEN)"
    GAMEDATA="$(python3 -c "import sys;sys.path.insert(0,'scripts');import projects as P;print(P.gamedata_path(P.load(only='$PROJECT')[0]))")"
    [ -n "$GAMEVER" ] || GAMEVER="$(basename "$(dirname "$(dirname "$LINUX_SO")")")"
    ( cd "$VIBE_REPO" && \
      uv run regen_css_linux.py -gamever "$GAMEVER" -gamedata "$GAMEDATA" \
        $([ $WRITE -eq 1 ] && echo -write) ) \
      || log "sig regen failed (idalib/IDA available?) - offsets already applied"
  else
    log "3/3 sig regen skipped: $REGEN not found (set --vibe-repo / CS2_VIBE_REPO)"
  fi
else
  log "3/3 sig regen skipped (pass --regen-sigs to enable; needs IDA license)"
fi

log "done. validate exit=$VAL"
[ $WRITE -eq 1 ] || log "dry-run: re-run with --write to apply changes"
