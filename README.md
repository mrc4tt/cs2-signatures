# CS2 Server Signatures Tracker

[![cs2 sigs](https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2Fbadge.json)](docs/CounterStrikeSharp.md)

Tracks the [CounterStrikeSharp](https://github.com/mrc4tt/CounterStrikeSharp)
gamedata signatures (from the **mrc4tt fork**) against live CS2 server
binaries. Inspired by [ianlucas/cs2-signatures](https://github.com/ianlucas/cs2-signatures),
scoped to one source and self-hosted on Forgejo.

On each CS2 update it re-downloads `libserver.so` + `server.dll` and scans every
signature: which still match (unique), which broke (0 matches), which went
ambiguous (>1 match). Full per-signature detail:
[**docs/CounterStrikeSharp.md**](docs/CounterStrikeSharp.md).

<!-- STATUS:START -->
## Signatures

* **Last updated:** July 2, 2026 at 8:44 PM UTC
* **Manifests:** [6854081659881519160](https://steamdb.info/depot/2347771/history/?changeid=M:6854081659881519160), [8851847688975518786](https://steamdb.info/depot/2347773/history/?changeid=M:8851847688975518786)
* **Validated:** 59 ok, 0 ambiguous, 1 broken (0 not-yet-validated)

<table>
<tr><th>Linux</th><th>Windows</th><th>Project</th><th></th></tr>
<tr><td>✅</td><td>❌</td><td><a href="https://github.com/mrc4tt/CounterStrikeSharp">CounterStrikeSharp</a></td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/CounterStrikeSharp.md">View signatures &rarr;</a></td></tr>
</table>

<details open><summary>&#9660; CounterStrikeSharp broken / ambiguous signatures (1)</summary>

<table>
<tr><th>Linux</th><th>Windows</th><th>Subroutine</th></tr>
<tr><td>✅</td><td>❌</td><td>CCSNavArea_IsValidNavMesh</td></tr>
</table>
</details>

<!-- STATUS:END -->

## How it works

```
check_update.py     DepotDownloader -manifest-only per depot -> changed?
fetch_gamedata.py   pull mrc4tt fork gamedata.json
download_bins.sh    DepotDownloader depots 2347771/2347773 -> server + engine2 (MB not GB)
validate_sigs.py    each sig -> bytes regex -> scan ELF/PE exec sections -> count
gen_report.py       -> README table + docs/CounterStrikeSharp.md + badge + history
```

Validation is pure-stdlib Python — no Ghidra, no third-party deps. It parses
ELF and PE section tables itself (`scripts/lib_sig.py`) and counts matches
**per executable section**.

Classification per entry/platform:

- `matches == 1` → **✅ ok**
- `matches == 0` → **❌ broken** (open Ghidra, regen with your `CS2Recipes.py`, PR the fork)
- `matches  > 1` → **⚠️ ambiguous** (sig too short / not unique)

Entries with only `offsets` (vtable slots) can't be byte-validated → shown as
offset-only.

### Better than the upstream tracker

- **Match count, not boolean.** ianlucas stops at the first hit (✅/❌). We count
  hits per executable section, so we also catch **⚠️ ambiguous** sigs that match
  in more than one place and aren't actually unique.
- **History trend** (`reports/history/*.json`) — per-day tally over time.
- **Auto-issue** on Forgejo when a sig breaks; auto-closes when green again.
- **Status badge** driven by `reports/badge.json`.

## VPS setup (x86-64)

Depots `2347771` (Windows) / `2347773` (Linux) are downloadable **anonymously**
— no Steam login needed.

1. Install .NET runtime + DepotDownloader:
   ```bash
   dotnet tool install -g DepotDownloader
   # or a release binary; then set DEPOTDOWNLOADER=/path/to/DepotDownloader
   ```
2. Run once by hand:
   ```bash
   bash scripts/run_all.sh
   ```
3. Register a **self-hosted Forgejo runner** on the VPS. The workflow
   (`.forgejo/workflows/track.yml`) then runs every 30 min and commits results.
4. For the auto-issue feature, add repo secret `FORGEJO_TOKEN` (scope: write
   issues). Steam login is optional — set `STEAM_USER`/`STEAM_PASS` secrets only
   if anonymous download fails on your host.

> Binaries are git-ignored — only derived reports/docs are committed. Badge
> needs the repo to be **public** so shields.io can read `reports/badge.json`.

## Layout

```
data/gamedata.json        snapshot of the fork's sigs (auto-refreshed)
data/manifest.json        last-seen per-depot manifest IDs
scripts/depots.py         depot IDs + file paths (single source of truth)
scripts/lib_sig.py        sig->regex + ELF/PE exec-section reader
scripts/check_update.py   per-depot manifest diff
scripts/fetch_gamedata.py pull upstream gamedata.json
scripts/download_bins.sh  DepotDownloader depot download
scripts/validate_sigs.py  scan + classify -> status.json
scripts/gen_report.py     -> README block + docs + badge + history
scripts/open_issue.py     Forgejo auto-issue on broken sigs
scripts/run_all.sh        full local pipeline
docs/CounterStrikeSharp.md  per-signature detail (CODE + IDA style)
reports/status.json       machine-readable result
reports/badge.json        shields.io endpoint
reports/history/*.json     per-run tally (drift over time)
.forgejo/workflows/        cron automation
```
