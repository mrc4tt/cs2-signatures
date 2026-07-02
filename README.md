# cs2-sig-tracker

Tracks the [CounterStrikeSharp](https://github.com/mrc4tt/CounterStrikeSharp)
gamedata signatures (from the **mrc4tt fork**) against live CS2 server
binaries. Inspired by [ianlucas/cs2-signatures](https://github.com/ianlucas/cs2-signatures),
scoped to one source and self-hosted on Forgejo.

On each CS2 update it re-downloads `server.so` + `server.dll`, scans every
signature, and publishes a traffic-light dashboard: which sigs still match,
which broke, which went ambiguous.

## Status

See [`reports/STATUS.md`](reports/STATUS.md).

| symbol | meaning |
|---|---|
| :white_check_mark: | 1 match — unique + healthy |
| :warning: | >1 match — present but not unique |
| :x: | 0 matches — sig broke, needs regen |
| :arrows_counterclockwise: | offset-only entry (vtable slot, not byte-validated) |

## How it works

```
check_update.py     steamcmd buildid changed? (exit 10 = yes)
fetch_gamedata.py   pull mrc4tt fork gamedata.json
download_bins.sh    DepotDownloader -> server.so + server.dll (filelist regex, MB not GB)
validate_sigs.py    each sig -> bytes regex -> scan ELF/PE exec sections -> count
gen_report.py       status.json -> STATUS.md + reports/history/DATE.json
```

Validation is pure-stdlib Python — no Ghidra, no third-party deps. It parses
ELF and PE section tables itself (`scripts/lib_sig.py`) and counts matches
**per executable section** so a pattern can't straddle a section boundary.

Classification per entry/platform:

- `matches == 1` → **ok**
- `matches == 0` → **broken** (open Ghidra, regen with your `CS2Recipes.py`, PR the fork)
- `matches  > 1` → **ambiguous** (sig too short / not unique)

Entries with only `offsets` (vtable slots) can't be byte-validated → reported
`offset-only`.

## VPS setup (x86-64, real Steam login)

1. Install .NET runtime + DepotDownloader:
   ```bash
   dotnet tool install -g DepotDownloader
   # or grab the release binary and set DEPOTDOWNLOADER=/path/to/DepotDownloader
   ```
2. Install `steamcmd` (for update detection).
3. First manual run to seed the SteamGuard session (cached afterwards):
   ```bash
   STEAM_USER=acct STEAM_PASS=pw bash scripts/run_all.sh
   ```
4. Register a **self-hosted Forgejo runner** on the VPS, add repo secrets
   `STEAM_USER` / `STEAM_PASS`. The workflow (`.forgejo/workflows/track.yml`)
   then runs every 30 min and commits results.

> Binaries are git-ignored — never commit copyrighted game files. Only the
> derived status/report is committed.

## Manual run

```bash
STEAM_USER=acct STEAM_PASS=pw bash scripts/run_all.sh
# or step by step:
python3 scripts/fetch_gamedata.py
python3 scripts/validate_sigs.py --linux bin_linux/.../libserver.so \
    --windows bin_win/.../server.dll
python3 scripts/gen_report.py --date "$(date +%F)"
```

## Layout

```
data/gamedata.json        snapshot of the fork's sigs (auto-refreshed)
data/manifest.txt         last-seen CS2 buildid
scripts/lib_sig.py        sig->regex + ELF/PE exec-section reader
scripts/check_update.py   buildid diff via steamcmd
scripts/fetch_gamedata.py pull upstream gamedata.json
scripts/download_bins.sh  DepotDownloader filelist download
scripts/validate_sigs.py  scan + classify -> status.json
scripts/gen_report.py     status.json -> STATUS.md + history
scripts/run_all.sh        full local pipeline
reports/STATUS.md         dashboard
reports/history/*.json    per-day tallies (drift over time)
.forgejo/workflows/       cron automation
```

## Notes / gotchas

- CS2 dedicated-server depots usually need a **real** Steam account, not
  anonymous — hence VPS + login (you confirmed x86-64 + login).
- `app_info_print 730` branch data may also need the real login; `check_update.py`
  takes `--login` if anonymous doesn't surface the buildid.
- Filelist regex targets `bin/linuxsteamrt64/libserver.so` and `bin/win64/server.dll`.
  If Valve moves the path, update `scripts/filelist_*.txt`.
- When a sig breaks, this repo tells you **what** + **when**. Regen still happens
  in your Ghidra toolbox (`CS2SigMaker.py` / `CS2Recipes.py`), then PR the fork.
```
