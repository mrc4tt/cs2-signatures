#!/usr/bin/env bash
# Full local run: check update -> fetch gamedata -> download bins -> validate ->
# report. Safe to run by hand on the VPS. CI does the same steps individually.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
cd "$ROOT"

ISO="$(LC_ALL=C date -u +%F)"
DISP="$(LC_ALL=C date -u '+%B %-d, %Y at %H:%M:%S GMT')"

# 1. Game updated? (exit 10 = changed). Don't abort on "unchanged" — still
#    refresh gamedata + regenerate report.
set +e
python3 scripts/check_update.py --manifest data/manifest.json
UPD=$?
set -e
[ "$UPD" -eq 1 ] && { echo "check_update failed"; exit 1; }

# 2. Latest upstream sig set for every tracked project. Non-fatal: private
#    repos need GITHUB_TOKEN; if a fetch fails we keep the committed snapshot.
set +e
python3 scripts/fetch_gamedata.py
[ $? -ne 0 ] && echo "WARN: gamedata fetch failed for a project — using existing snapshot"
set -e

# 3. Binaries (anonymous; set STEAM_USER/STEAM_PASS only if needed). Shared by
#    all projects — the game binaries are the same regardless of plugin.
eval "$(bash scripts/download_bins.sh | grep -E '^(LINUX_SO|LINUX_ENGINE2|WIN_DLL|WIN_ENGINE2)=')"

# 4. Validate every project against the shared binaries -> reports/<id>/status.json.
set +e
python3 scripts/validate_sigs.py \
  --linux "${LINUX_SO:-}" --windows "${WIN_DLL:-}" \
  --linux-engine2 "${LINUX_ENGINE2:-}" --windows-engine2 "${WIN_ENGINE2:-}" \
  --manifest data/manifest.json
VAL=$?
set -e

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
  echo "no signature/manifest change — skipping report + push"
  echo "done (validate exit=$VAL, update=$UPD)"
  exit "$VAL"
fi

# 6. Regenerate reports (only now stamp a fresh timestamp) + commit + push.
python3 scripts/gen_report.py \
  --readme README.md --docs-dir docs \
  --history-dir reports/history --date "$DISP" --iso "$ISO"

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
#    identical binaries and churn the Releases page — skip it.
if [ -n "${FORGEJO_TOKEN:-}" ] && [ "$UPD" -eq 10 ]; then
  # Also pull items_game.txt out of the content-depot VPK (~100 MB one-off) and
  # attach it to the same release. Non-fatal: a VPK layout change must not block
  # the binary release.
  ITEMS_GAME=""
  set +e
  IG_LINE="$(bash scripts/extract_items_game.sh | grep -E '^ITEMS_GAME=')"
  [ $? -eq 0 ] && eval "$IG_LINE" || echo "WARN: items_game.txt extract failed"
  set -e
  python3 scripts/publish_bins.py \
    --linux "${LINUX_SO:-}" --windows "${WIN_DLL:-}" \
    --linux-engine2 "${LINUX_ENGINE2:-}" --windows-engine2 "${WIN_ENGINE2:-}" \
    ${ITEMS_GAME:+--items-game "$ITEMS_GAME"} \
    --keep "${BINS_KEEP:-2}" --iso "$ISO" || true
elif [ -n "${FORGEJO_TOKEN:-}" ]; then
  echo "no game update (UPD=$UPD) — skipping binary release"
fi

echo "done (validate exit=$VAL, update=$UPD)"
exit "$VAL"
