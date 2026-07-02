#!/usr/bin/env bash
# Full local run: check update -> fetch gamedata -> download bins -> validate ->
# report. Safe to run by hand on the VPS. CI does the same steps individually.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
cd "$ROOT"

ISO="$(date -u +%F)"
DISP="$(date -u '+%B %-d, %Y at %H:%M:%S GMT')"

# 1. Game updated? (exit 10 = changed). Don't abort on "unchanged" — still
#    refresh gamedata + regenerate report.
set +e
python3 scripts/check_update.py --manifest data/manifest.json
UPD=$?
set -e
[ "$UPD" -eq 1 ] && { echo "check_update failed"; exit 1; }

# 2. Latest upstream sig set. Non-fatal: private fork needs GITHUB_TOKEN; if it
#    fails we keep validating the committed snapshot.
set +e
python3 scripts/fetch_gamedata.py --out data/gamedata.json
[ $? -ne 0 ] && echo "WARN: gamedata fetch failed — using existing snapshot"
set -e

# 3. Binaries (anonymous; set STEAM_USER/STEAM_PASS only if needed).
eval "$(bash scripts/download_bins.sh | grep -E '^(LINUX_SO|LINUX_ENGINE2|WIN_DLL|WIN_ENGINE2)=')"

# 4. Validate.
set +e
python3 scripts/validate_sigs.py \
  --gamedata data/gamedata.json \
  --linux "${LINUX_SO:-}" --windows "${WIN_DLL:-}" \
  --linux-engine2 "${LINUX_ENGINE2:-}" --windows-engine2 "${WIN_ENGINE2:-}" \
  --manifest data/manifest.json \
  --out reports/status.json
VAL=$?
set -e

# 5. Report (always, even if broken sigs).
python3 scripts/gen_report.py --status reports/status.json \
  --readme README.md --docs docs/CounterStrikeSharp.md \
  --history-dir reports/history --date "$DISP" --iso "$ISO"

# 6. Auto commit + push results (set NO_PUSH=1 to skip). Binaries are
#    git-ignored, so only data/reports/docs/README get committed.
if [ "${NO_PUSH:-0}" != "1" ]; then
  git add data/manifest.json data/gamedata.json README.md docs/ reports/
  if git diff --cached --quiet; then
    echo "no changes to push"
  else
    git -c user.name="${GIT_NAME:-sig-tracker}" \
        -c user.email="${GIT_EMAIL:-sig-tracker@localhost}" \
        commit -q -m "track: $(tr -d '\n ' < data/manifest.json) ($ISO)"
    git push -q origin HEAD && echo "pushed results"
  fi
fi

echo "done (validate exit=$VAL, update=$UPD)"
exit "$VAL"
