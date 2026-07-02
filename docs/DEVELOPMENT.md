# Development / operations

## How it works

```
check_update.py     DepotDownloader -manifest-only per depot -> changed?
fetch_gamedata.py   pull mrc4tt fork gamedata.json (authenticated; fork is private)
download_bins.sh    DepotDownloader depots 2347771/2347773 -> server + engine2 (MB not GB)
validate_sigs.py    each sig -> bytes regex -> scan ELF/PE exec sections -> count
gen_report.py       -> README table + docs/CounterStrikeSharp.md + badge + history
```

Validation is pure-stdlib Python — no Ghidra, no third-party deps. It parses
ELF and PE section tables itself (`scripts/lib_sig.py`) and counts matches
**per executable section**.

Classification per entry/platform:

- `matches == 1` → **✅ ok**
- `matches == 0` → **❌ broken** (open Ghidra, regen with `CS2Recipes.py`, PR the fork)
- `matches  > 1` → **⚠️ ambiguous** (sig too short / not unique)

Offset-only entries (vtable slots) are not tracked here — signatures only.

### Better than the upstream tracker

- **Match count, not boolean.** ianlucas stops at the first hit (✅/❌). We count
  hits per executable section, so we also catch **⚠️ ambiguous** sigs.
- **History trend** (`reports/history/*.json`) — per-run tally over time.
- **Auto-issue** on Forgejo when a sig breaks; auto-closes when green again.
- **Status badge** driven by `reports/badge.json`.

## VPS setup (x86-64)

Depots `2347771` (Windows) / `2347773` (Linux) download **anonymously** — no
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
4. Optional auto-issue: set `FORGEJO_TOKEN` in `.env` (write-issue scope).

> Binaries are git-ignored — only derived reports/docs are committed. Badge
> needs the repo **public** so shields.io can read `reports/badge.json`.

## Layout

```
data/gamedata.json        snapshot of the fork's sigs (auto-refreshed)
data/manifest.json        last-seen per-depot manifest IDs
scripts/depots.py         depot IDs + file paths (single source of truth)
scripts/lib_sig.py        sig->regex + ELF/PE exec-section reader
scripts/check_update.py   per-depot manifest diff
scripts/fetch_gamedata.py pull upstream gamedata.json (authenticated)
scripts/download_bins.sh  DepotDownloader depot download
scripts/validate_sigs.py  scan + classify -> status.json
scripts/gen_report.py     -> README block + docs + badge + history
scripts/open_issue.py     Forgejo auto-issue on broken sigs
scripts/run_all.sh        full pipeline (validate + commit + push)
scripts/cron.sh           cron entrypoint (loads .env, logs)
docs/CounterStrikeSharp.md  per-signature detail (CODE + IDA style)
reports/status.json       machine-readable result
reports/badge.json        shields.io endpoint
reports/history/*.json    per-run tally (drift over time)
.forgejo/workflows/       Forgejo Actions alternative to cron
```
