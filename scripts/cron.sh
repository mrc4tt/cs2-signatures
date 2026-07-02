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
bash scripts/run_all.sh
