#!/usr/bin/env bash
# Full local run: check update -> fetch gamedata -> download bins -> validate ->
# report. Safe to run by hand on the VPS. CI does the same steps individually.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
cd "$ROOT"

DATE="$(date +%F)"

# 1. Game updated? (exit 10 = changed). Don't abort the whole run on "unchanged"
#    — we still refresh gamedata + report.
set +e
python3 scripts/check_update.py --manifest data/manifest.txt
UPD=$?
set -e
[ "$UPD" -eq 1 ] && { echo "check_update failed"; exit 1; }

# 2. Latest upstream sig set.
python3 scripts/fetch_gamedata.py --out data/gamedata.json

# 3. Binaries (needs STEAM_USER/STEAM_PASS in env).
eval "$(bash scripts/download_bins.sh | grep -E '^(LINUX_SO|WIN_DLL)=')"

# 4. Validate.
set +e
python3 scripts/validate_sigs.py \
  --gamedata data/gamedata.json \
  --linux "${LINUX_SO:-}" --windows "${WIN_DLL:-}" \
  --manifest data/manifest.txt \
  --out reports/status.json
VAL=$?
set -e

# 5. Report (always, even if broken sigs -> exit was non-zero).
python3 scripts/gen_report.py --status reports/status.json \
  --out reports/STATUS.md --history-dir reports/history --date "$DATE"

echo "done (validate exit=$VAL, update=$UPD)"
exit "$VAL"
