#!/usr/bin/env bash
# Full local run: check update -> fetch gamedata -> download bins -> validate ->
# report. Safe to run by hand on the server. CI does the same steps individually.
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

# 2.05 Reference snapshot. binary_locks/<ver>.json binds a game version to the
#      exact depot manifests, so the version is resolved from data/manifest.json
#      rather than guessed. Runs before the skip below because the reference is
#      now one of the things that can change a verdict: a symbol appearing in a
#      newer snapshot turns a no_recipe offset into a real one without the game
#      or the gamedata having moved at all.
#
#      Entirely optional and entirely non-fatal: no network, no git, or an
#      analysis that has not caught up with this build all leave SYMBOLS empty
#      and the pipeline byte-scanning exactly as it did before. Set NO_SYMBOLS=1
#      to skip, SYMBOLS_REPO to read another fork.
SYMBOLS=""
GAMEVER=""
if [ "${NO_SYMBOLS:-0}" != "1" ]; then
  SYM_ARGS=()
  [ -n "${SYMBOLS_REPO:-}" ] && SYM_ARGS+=(--repo "$SYMBOLS_REPO")
  set +e
  GAMEVER="$(python3 scripts/fetch_symbols.py --resolve "${SYM_ARGS[@]+"${SYM_ARGS[@]}"}" 2>/dev/null)"
  set -e
  if [ -n "$GAMEVER" ]; then
    # REFERENCE_CHANGED=1 (cron.sh, from poll_latest.py) means the box published
    # since the last tick. The version string can be the same one we already
    # have on disk - a re-publish of the same build - so the cached snapshot is
    # stale and has to be pulled again rather than reused.
    if [ ! -f "data/symbols/$GAMEVER.json" ] || [ "${REFERENCE_CHANGED:-0}" = "1" ]; then
      python3 scripts/fetch_symbols.py --backend git --gamever "$GAMEVER" \
        "${SYM_ARGS[@]+"${SYM_ARGS[@]}"}" || true
    fi
    [ -f "data/symbols/$GAMEVER.json" ] && SYMBOLS="data/symbols/$GAMEVER.json"
  fi
  if [ -n "$SYMBOLS" ]; then
    echo "reference snapshot $GAMEVER"
  else
    echo "no reference snapshot for this build - scanning only"
    GAMEVER=""
  fi
fi

# 2.1 Nothing to do? Game unchanged + published reference unchanged + every
#     gamedata unchanged + every project already has a status.json + no
#     half-finished state in the tree -> the validate result cannot differ from
#     last run. Skip the binary download and the ~80 MB scans; exit with the
#     same ok/broken code a full run would.
if [ "$UPD" -eq 0 ] \
   && [ "${REFERENCE_CHANGED:-0}" != "1" ] \
   && ! echo "$FETCH_OUT" | grep -q " gamedata changed" \
   && [ -z "$(git status --porcelain data/ reports/)" ]; then
  BROKEN=$(REF="${GAMEVER:-}" python3 - <<'PY'
import json, os, subprocess, sys
sys.path.insert(0, "scripts")
import projects as P
want = os.environ.get("REF") or None

def committed_at(path):
    out = subprocess.run(["git", "log", "-1", "--format=%ct", "--", path],
                         capture_output=True, text=True).stdout.strip()
    return int(out) if out else 0

broken = 0
for proj in P.load():
    path = P.status_path(proj)
    if not os.path.isfile(path):
        sys.exit(2)  # new project - needs a full run
    # Gamedata committed by hand (not by a pipeline run) was never validated:
    # fetch now reports it unchanged, so only the commit order gives it away.
    if committed_at(P.gamedata_path(proj)) > committed_at(path):
        sys.exit(2)
    with open(path) as fh:
        status = json.load(fh)
    # The reference moved (or arrived, or went away) since the last run, so a
    # verdict can differ even though the game and the gamedata did not.
    if status.get("reference") != want:
        sys.exit(2)
    broken += status.get("tally", {}).get("broken", 0)
print(broken)
PY
) || BROKEN=""
  if [ -n "$BROKEN" ]; then
    echo "no game/gamedata change - skipping binary scan (broken=$BROKEN)"
    [ "$BROKEN" -gt 0 ] && exit 1
    exit 0
  fi
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
  --manifest data/manifest.json \
  ${SYMBOLS:+--symbols "$SYMBOLS"}
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
  echo "no signature/manifest change - skipping report + push"
  echo "done (validate exit=$VAL, update=$UPD)"
  exit "$VAL"
fi

# 5.5 Is the change worth ANNOUNCING? The gate above is deliberately wide (any
#     status.json byte) so commits stay faithful, but an upstream gamedata
#     rename, a key reorder, or a new CS2 build where everything still resolves
#     is not news for a Discord channel. post_gate.py diffs only the sig bytes,
#     offsets and statuses - names excluded - against HEAD, so it must run
#     BEFORE step 6 commits. Exit 10 = announce. Set POST_ON_GAME_UPDATE=1 to
#     also announce a manifest-only change.
#     --write-delta hands the NAMED delta to the Discord step: by then the
#     commit below has moved HEAD, so it could no longer work out what changed.
GATE_ARGS=(--write-delta reports/delta.json)
[ "${POST_ON_GAME_UPDATE:-0}" = "1" ] && GATE_ARGS+=(--include-manifest)
set +e
python3 scripts/post_gate.py "${GATE_ARGS[@]}"
ANNOUNCE=$?
set -e
[ "$ANNOUNCE" -eq 1 ] && { echo "post_gate failed"; exit 1; }

# 6. Regenerate reports (only now stamp a fresh timestamp) + commit + push.
python3 scripts/gen_report.py \
  --readme README.md --docs-dir docs \
  --history-dir reports/history --date "$DISP" --iso "$ISO"
python3 scripts/gen_stats.py --out docs/stats.md --date "$DISP" \
  --json reports/fragility.json || true
# Reference coverage gaps as a page, current after every run (replaces the
# GitHub issue in the analysis repo, which flipped open/closed with every change).
python3 scripts/reference_gaps.py --out reports/reference_gaps.json \
  --page docs/ReferenceGaps.md --date "$DISP" || true

if [ "${NO_PUSH:-0}" != "1" ]; then
  git add data/manifest.json data/projects.json data/*/gamedata.json \
    README.md docs/ reports/
  if git diff --cached --quiet; then
    echo "no changes to push"
  else
    git -c user.name="${GIT_NAME:-sig-tracker}" \
        -c user.email="${GIT_EMAIL:-sig-tracker@localhost}" \
        commit -q -m "track: $(tr -d '\n ' < data/manifest.json) ($ISO)"
    # The remote may have moved since cron.sh pulled (a code push mid-run).
    # As the gh login, not .env's GITHUB_TOKEN (no Contents write here; see cron.sh).
    env -u GITHUB_TOKEN -u GH_TOKEN git -c user.name="${GIT_NAME:-sig-tracker}" \
        -c user.email="${GIT_EMAIL:-sig-tracker@localhost}" \
        pull -q --rebase origin main || echo "WARN: rebase onto origin failed"
    env -u GITHUB_TOKEN -u GH_TOKEN git push -q origin HEAD && echo "pushed results" || echo "WARN: push failed"
  fi
fi

# 7. Optional auto-issue on broken sigs, across all projects. Needs ISSUE_REPO
#    (e.g. mrc4tt/cs2-signatures) + GITHUB_TOKEN in .env, or the FORGEJO_*
#    trio. Silent if unset.
if [ -n "${ISSUE_REPO:-}${FORGEJO_TOKEN:-}" ]; then
  python3 scripts/open_issue.py || true
fi

# 7.6 Opt-in (GAP_ISSUE=1): also mirror the gap page into one GitHub issue in the
#     analysis repo. Off by default - docs/ReferenceGaps.md (written above) is the
#     place to look, and the issue flipped open/closed whenever the set moved.
if [ "${GAP_ISSUE:-0}" = "1" ] && [ -n "${GITHUB_TOKEN:-}${GH_TOKEN:-}" ]; then
  python3 scripts/open_gap_issue.py || true
fi

# 8. Optional Discord webhook post, across all projects (needs DISCORD_WEBHOOK,
#    which may hold several comma/space-separated URLs for multiple servers).
#    Gated on step 5.5: a signature/offset RESULT must have changed, not just
#    the file. Preview locally with:
#    python3 scripts/post_discord.py --preview [--example]
if [ -n "${DISCORD_WEBHOOK:-}" ] && [ "$ANNOUNCE" -eq 10 ]; then
  python3 scripts/post_discord.py || true
elif [ -n "${DISCORD_WEBHOOK:-}" ]; then
  echo "no post-worthy result change - skipping discord post"
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
