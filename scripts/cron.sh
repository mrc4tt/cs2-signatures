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

# Self-update, then restart on the new copy of this script. Nothing else ever
# pulls this checkout, so without it a pushed fix never reached the box, and the
# next results push was rejected as non-fast-forward (silently: it is inside an
# `if`). Rebase, not ff-only: this box's own track: commits may be unpushed.
# GITHUB_TOKEN from .env is for the API (issues, releases) and has no Contents write on
# this repo; the gh credential helper prefers it over the gh login, so every push was a
# 403 "Permission to mrc4tt/cs2-signatures.git denied". Git talks to the remote as the
# gh login; run_all.sh strips the same two variables for its pull and push.
git_remote() { env -u GITHUB_TOKEN -u GH_TOKEN git "$@"; }
if [ "${SIG_TRACKER_UPDATED:-0}" != "1" ]; then
  git_remote -c user.name="${GIT_NAME:-sig-tracker}" -c user.email="${GIT_EMAIL:-sig-tracker@localhost}" \
    pull -q --rebase --autostash origin main \
    || echo "WARN: self-update failed - running the checked-out version"
  SIG_TRACKER_UPDATED=1 exec bash "$0" "$@"
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
