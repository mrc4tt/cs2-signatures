# Development / operations

## How it works

```
projects.py         registry: data/projects.json -> tracked projects + path/URL layout
check_update.py     DepotDownloader -manifest-only per depot -> changed?
fetch_gamedata.py   pull each project's gamedata.json -> data/<id>/gamedata.json
download_bins.sh    DepotDownloader depots 2347771/2347773 -> server + engine2 (MB not GB)
validate_sigs.py    each sig -> bytes regex -> scan ELF/PE exec sections -> count (per project)
gen_report.py       -> README table (one row/project) + docs/<id>.md + aggregate badge + history
```

### Multiple projects

Every tracked plugin is one CSS-format `gamedata.json` (signatures + offsets)
in some GitHub repo. They all share the same CS2 game binaries, so the download
+ manifest-diff steps stay game-global; only fetch / validate / report loop over
projects.

Add a project by appending to `data/projects.json` - no code change:

```json
{
  "id": "MyPlugin",
  "name": "cs2-my-plugin",
  "repo": "owner/cs2-my-plugin",
  "branch": "main",
  "path": "Resources/MyPlugin_gamedata.json",
  "private": false
}
```

`id` is the stable slug driving `data/<id>/`, `reports/<id>/status.json`, and
`docs/<id>.md`. `private: true` means the fetch needs `GITHUB_TOKEN`. Next run
picks it up: fetches, validates, adds a README row + `docs/<id>.md`.

Validation is pure-stdlib Python - no Ghidra, no third-party deps. It parses
ELF and PE section tables itself (`scripts/lib_sig.py`) and counts matches
**per executable section**.

Classification per entry/platform:

- `matches == 1` → **✅ ok**
- `matches == 0` → **❌ broken** (open Ghidra, regen with `CS2Recipes.py`, PR the fork)
- `matches  > 1` → **⚠️ ambiguous** (sig too short / not unique)

Offset-only entries (vtable slots) are not tracked here - signatures only.

### Better than the upstream tracker

- **Match count, not boolean.** ianlucas stops at the first hit (✅/❌). We count
  hits per executable section, so we also catch **⚠️ ambiguous** sigs.
- **History trend** (`reports/history/*.json`) - per-run tally over time.
- **Auto-issue** on Forgejo when a sig breaks; auto-closes when green again.
- **Status badge** driven by `reports/badge.json`.

## VPS setup (x86-64)

Depots `2347771` (Windows) / `2347773` (Linux) download **anonymously** - no
Steam login. The gamedata fetch needs a GitHub token because the fork is private.

1. Clone + configure env:
   ```bash
   git clone https://git.miksen.me/mikkel/cs2-signatures.git
   cd cs2-signatures
   cp .env.example .env && nano .env      # GITHUB_TOKEN + DEPOTDOWNLOADER path
   git config --global credential.helper store   # cache Forgejo push creds once
   ```
2. Run once by hand:
   ```bash
   bash scripts/run_all.sh
   ```
   It validates, regenerates the README/docs, and auto-commits + pushes results
   (`NO_PUSH=1` to skip the push).
3. Automate with cron (every 30 min):
   ```bash
   crontab -e
   */30 * * * * /root/cs2-signatures/scripts/cron.sh
   ```
   `cron.sh` loads `.env`, runs the pipeline, logs to `reports/cron.log`.
4. Optional auto-issue on broken sigs: set `FORGEJO_TOKEN` + `FORGEJO_SERVER` +
   `FORGEJO_REPO` in `.env` (token needs write-issue scope). `run_all.sh` opens
   the issue automatically and closes it when green again.

> Binaries are git-ignored - only derived reports/docs are committed. Badge
> needs the repo **public** so shields.io can read `reports/badge.json`.

## Layout

```
data/projects.json        tracked-project registry (id/repo/branch/path/private)
data/<id>/gamedata.json   snapshot of each project's sigs (auto-refreshed)
data/manifest.json        last-seen per-depot manifest IDs (game-global)
scripts/projects.py       project registry loader + path/URL layout
scripts/depots.py         depot IDs + file paths (single source of truth)
scripts/lib_sig.py        sig->regex + ELF/PE exec-section reader
scripts/check_update.py   per-depot manifest diff (game-global)
scripts/fetch_gamedata.py pull each project's gamedata.json (authenticated)
scripts/download_bins.sh  DepotDownloader depot download (shared bins)
scripts/validate_sigs.py  scan + classify per project -> reports/<id>/status.json
scripts/gen_report.py     -> README block + docs/<id>.md + aggregate badge + history
scripts/open_issue.py     Forgejo auto-issue on broken sigs (across all projects)
scripts/post_gate.py      is the change worth announcing? (exit 10 = yes)
scripts/post_discord.py   Discord webhook summary (across all projects)
scripts/run_all.sh        full pipeline (validate + commit + push)
scripts/cron.sh           cron entrypoint (loads .env, logs)
docs/<id>.md              per-signature detail per project (CODE + IDA style)
reports/<id>/status.json  machine-readable result per project
reports/badge.json        shields.io endpoint (aggregate)
reports/history/*.json    per-run tally + per-project breakdown (drift over time)
```
