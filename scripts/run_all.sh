#!/usr/bin/env bash
# Full local run: check update -> fetch gamedata -> download bins -> validate ->
# report. Safe to run by hand on the VPS. CI does the same steps individually.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
cd "$ROOT"

# Load repo env (DEPOTDOWNLOADER, tokens, GIT_NAME/EMAIL, ...) so manual runs
# work like cron runs; cron.sh loading it first is harmless (same values).
if [ -f "$ROOT/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  . "$ROOT/.env"
  set +a
fi

ISO="$(LC_ALL=C date -u +%F)"
DISP="$(LC_ALL=C date -u '+%B %-d, %Y at %H:%M:%S GMT')"

# 1. Game updated? (exit 10 = changed). Don't abort on "unchanged" - still
#    refresh gamedata + regenerate report.
set +e
python3 scripts/check_update.py --manifest data/manifest.json
UPD=$?
set -e
[ "$UPD" -eq 1 ] && { echo "check_update failed"; exit 1; }

# 2. Latest upstream sig set for every tracked project. Non-fatal: private
#    repos need GITHUB_TOKEN; if a fetch fails we keep the committed snapshot.
set +e
FETCH_OUT="$(python3 scripts/fetch_gamedata.py 2>&1)"
[ $? -ne 0 ] && echo "WARN: gamedata fetch failed for a project - using existing snapshot"
set -e
echo "$FETCH_OUT"

# 2.1 Nothing to do? Game unchanged + every gamedata unchanged + every project
#     already has a status.json + no half-finished state in the tree -> the
#     validate result cannot differ from last run. Skip the binary download and
#     the ~80 MB scans; exit with the same ok/broken code a full run would.
if [ "$UPD" -eq 0 ] \
   && ! echo "$FETCH_OUT" | grep -q " gamedata changed" \
   && [ -z "$(git status --porcelain data/ reports/)" ]; then
  BROKEN=$(python3 - <<'PY'
import json, os, sys
sys.path.insert(0, "scripts")
import projects as P
broken = 0
for proj in P.load():
    path = P.status_path(proj)
    if not os.path.isfile(path):
        sys.exit(2)  # new project - needs a full run
    with open(path) as fh:
        broken += json.load(fh).get("tally", {}).get("broken", 0)
print(broken)
PY
) || BROKEN=""
  if [ -n "$BROKEN" ]; then
    echo "no game/gamedata change - skipping binary scan (broken=$BROKEN)"
    [ "$BROKEN" -gt 0 ] && exit 1
    exit 0
  fi
fi

# 2.5 Game updated -> the binaries on disk are still the PREVIOUS build.
#     Snapshot them (git-ignored bin_prev/) before step 3 overwrites them, so
#     propose_sigs.py can diff old vs new when a signature breaks.
if [ "$UPD" -eq 10 ]; then
  mkdir -p "$ROOT/bin_prev"
  for n in libserver.so libengine2.so; do
    src="$(find "$ROOT/bin_linux" -name "$n" 2>/dev/null | head -1 || true)"
    [ -n "$src" ] && cp -f "$src" "$ROOT/bin_prev/$n"
  done
  for n in server.dll engine2.dll; do
    src="$(find "$ROOT/bin_win" -name "$n" 2>/dev/null | head -1 || true)"
    [ -n "$src" ] && cp -f "$src" "$ROOT/bin_prev/$n"
  done
  echo "snapshotted previous build to bin_prev/"
fi

# 3. Binaries (anonymous; set STEAM_USER/STEAM_PASS only if needed). Shared by
#    all projects - the game binaries are the same regardless of plugin.
eval "$(bash scripts/download_bins.sh | grep -E '^(LINUX_SO|LINUX_ENGINE2|LINUX_CLIENT|WIN_DLL|WIN_ENGINE2)=')"

# The eval|grep above swallows a download_bins.sh failure (command substitution
# exit status is lost), so check the result explicitly. Without binaries,
# validation would mark every sig no_binary and step 5 would commit + post that
# as a "change". Abort instead - the next cron tick retries in 15 minutes.
if [ -z "${LINUX_SO:-}" ] || [ -z "${WIN_DLL:-}" ]; then
  echo "binary download failed (LINUX_SO='${LINUX_SO:-}', WIN_DLL='${WIN_DLL:-}') - aborting before validate/commit/post"
  exit 1
fi

# 4. Validate every project against the shared binaries -> reports/<id>/status.json.
set +e
python3 scripts/validate_sigs.py \
  --linux "${LINUX_SO:-}" --windows "${WIN_DLL:-}" \
  --linux-engine2 "${LINUX_ENGINE2:-}" --windows-engine2 "${WIN_ENGINE2:-}" \
  --manifest data/manifest.json
VAL=$?
set -e

# 4.5 Propose replacement sigs for broken/ambiguous entries by diffing the
#     previous build (bin_prev/, step 2.5) against the new one. Advisory only -
#     writes reports/<id>/proposals.json for the issue/Discord steps, never
#     edits gamedata. Cheap when everything is healthy (reads statuses, exits);
#     also removes stale proposals once sigs pass again. Runs unconditionally
#     because ambiguous entries don't affect $VAL.
python3 scripts/propose_sigs.py \
  --old-dir "$ROOT/bin_prev" \
  --linux "${LINUX_SO:-}" --windows "${WIN_DLL:-}" \
  --linux-engine2 "${LINUX_ENGINE2:-}" --windows-engine2 "${WIN_ENGINE2:-}" \
  || true

# 5. Did anything MEANINGFUL change? Each status.json holds manifest + statuses
#    + sig strings but NO timestamp, so it only differs on a real change. Diff
#    every project's status.json vs its committed version so we don't churn a
#    push each run just because the "Last updated" clock moved. A brand-new
#    project (no committed status yet) counts as changed.
CHANGED=0
for f in reports/*/status.json; do
  if ! git show "HEAD:$f" 2>/dev/null | diff -q - "$f" >/dev/null 2>&1; then
    CHANGED=1
  fi
done

if [ "$CHANGED" -eq 0 ]; then
  echo "no signature/manifest change - skipping report + push"
  echo "done (validate exit=$VAL, update=$UPD)"
  exit "$VAL"
fi

# 6. Regenerate reports (only now stamp a fresh timestamp) + commit + push.
python3 scripts/gen_report.py \
  --readme README.md --docs-dir docs \
  --history-dir reports/history --date "$DISP" --iso "$ISO"
python3 scripts/gen_stats.py --out docs/stats.md --date "$DISP" || true

if [ "${NO_PUSH:-0}" != "1" ]; then
  git add data/manifest.json data/projects.json data/*/gamedata.json \
    README.md docs/ reports/
  if git diff --cached --quiet; then
    echo "no changes to push"
  else
    git -c user.name="${GIT_NAME:-sig-tracker}" \
        -c user.email="${GIT_EMAIL:-sig-tracker@localhost}" \
        commit -q -m "track: $(tr -d '\n ' < data/manifest.json) ($ISO)"
    git push -q origin HEAD && echo "pushed results"
  fi
fi

# 7. Optional Forgejo auto-issue on broken sigs, across all projects (needs
#    FORGEJO_TOKEN + FORGEJO_SERVER + FORGEJO_REPO in .env). Silent if unset.
if [ -n "${FORGEJO_TOKEN:-}" ]; then
  python3 scripts/open_issue.py || true
fi

# 7.5 Optional: draft PR with the patched gamedata against each project repo
#     that opts in via "propose_pr": true (needs a push-capable token). Stable
#     branch -> re-runs update the same PR. Human reviews and merges.
if ls reports/*/proposals.json >/dev/null 2>&1; then
  python3 scripts/open_pr.py || true
fi

# 8. Optional Discord webhook post, across all projects (needs DISCORD_WEBHOOK).
#    Only runs on a real change (past the CHANGED gate). Preview locally with:
#    python3 scripts/post_discord.py --preview [--example]
if [ -n "${DISCORD_WEBHOOK:-}" ]; then
  python3 scripts/post_discord.py || true
fi

# 9. Optional: publish the CS2 binaries as Forgejo release assets so users can
#    download the exact .so/.dll this run validated against. Git-ignored in the
#    tree; kept as the newest 2 releases (tag = CS2 ClientVersion). Needs
#    FORGEJO_TOKEN + server/repo. Skipped silently if unset or bins missing.
#    ONLY on a real game update (check_update exit 10 = new bins). A sig-only
#    change reuses the same version tag, so republishing would just re-upload
#    identical binaries and churn the Releases page - skip it.
if [ -n "${FORGEJO_TOKEN:-}" ] && [ "$UPD" -eq 10 ]; then
  python3 scripts/publish_bins.py \
    --linux "${LINUX_SO:-}" --windows "${WIN_DLL:-}" \
    --linux-engine2 "${LINUX_ENGINE2:-}" --windows-engine2 "${WIN_ENGINE2:-}" \
    --linux-client "${LINUX_CLIENT:-}" \
    --keep "${BINS_KEEP:-2}" --iso "$ISO" || true
elif [ -n "${FORGEJO_TOKEN:-}" ]; then
  echo "no game update (UPD=$UPD) - skipping binary release"
fi

echo "done (validate exit=$VAL, update=$UPD)"
exit "$VAL"
