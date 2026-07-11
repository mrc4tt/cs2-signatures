#!/usr/bin/env bash
# Extract game/csgo/scripts/items/items_game.txt from the CS2 content depot
# without pulling the whole ~60 GB install.
#
#   1. download pak01_dir.vpk (index, ~7 MB) from depot 2347770
#   2. read the index to find which numbered archive holds items_game.txt
#   3. download only that one pak01_<NNN>.vpk (~100 MB)
#   4. slice the file out of the archive with scripts/vpk.py
#
# The archive index moves between game updates, so steps 1-2 pick it at runtime.
# Prints `ITEMS_GAME=<path>` on success for run_all.sh to attach to the release.
#
# Anonymous like download_bins.sh; set STEAM_USER/STEAM_PASS only if needed.
set -euo pipefail

DD="${DEPOTDOWNLOADER:-DepotDownloader}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
APP=730
DEPOT_CONTENT=2347770
OUTDIR="$ROOT/bin_content"
VPK_DIR="$OUTDIR/game/csgo/pak01_dir.vpk"
INTERNAL="scripts/items/items_game.txt"
OUT="$OUTDIR/items_game.txt"
FL="$(mktemp)"
trap 'rm -f "$FL"' EXIT

auth=()
if [ -n "${STEAM_USER:-}" ]; then
  auth=(-username "$STEAM_USER" -password "${STEAM_PASS:-}" -remember-password)
fi

echo ">> content depot $DEPOT_CONTENT (pak01_dir.vpk)" >&2
printf 'game/csgo/pak01_dir.vpk\n' > "$FL"
"$DD" -app "$APP" -depot "$DEPOT_CONTENT" -filelist "$FL" -dir "$OUTDIR" \
  "${auth[@]}" >&2

ARCHIVE="$(python3 "$HERE/vpk.py" locate "$VPK_DIR" "$INTERNAL")"
echo ">> items_game.txt lives in archive $ARCHIVE" >&2

# -1 = bytes are inline in the dir vpk (no numbered archive to fetch).
if [ "$ARCHIVE" != "-1" ]; then
  PAK="$(printf 'pak01_%03d.vpk' "$ARCHIVE")"
  echo ">> content depot $DEPOT_CONTENT ($PAK)" >&2
  printf 'game/csgo/%s\n' "$PAK" > "$FL"
  "$DD" -app "$APP" -depot "$DEPOT_CONTENT" -filelist "$FL" -dir "$OUTDIR" \
    "${auth[@]}" >&2
fi

python3 "$HERE/vpk.py" extract "$VPK_DIR" "$INTERNAL" -o "$OUT" >&2
echo "ITEMS_GAME=$OUT"
