#!/usr/bin/env bash
# Cron entrypoint. Cron runs with a minimal env, so load .env for the repo,
# then run the full pipeline (which validates + commits + pushes). Logs to
# reports/cron.log (git-ignored).
#
# Install (every 30 min):
#   crontab -e
#   */30 * * * * /root/cs2-signatures/scripts/cron.sh
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
cd "$ROOT"

# Load repo env (GITHUB_TOKEN, DEPOTDOWNLOADER, GIT_NAME/EMAIL, ...).
if [ -f "$ROOT/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  . "$ROOT/.env"
  set +a
fi

echo "===== $(date -u '+%F %H:%M:%S GMT') ====="

# Did the analysis box publish a new snapshot since the last tick? That is the
# one change the pipeline cannot work out for itself: the game and the tracked
# gamedata can both sit still while the published reference moves, and a
# re-publish of the same build only shows up as a new configSha256. Exit 10 =
# moved; anything else (including a network error) leaves the run on its normal
# course, where check_update.py and fetch_gamedata.py decide as they always did.
set +e
python3 scripts/poll_latest.py
POLL=$?
set -e
if [ "$POLL" -eq 10 ]; then
  export REFERENCE_CHANGED=1
fi

bash scripts/run_all.sh
