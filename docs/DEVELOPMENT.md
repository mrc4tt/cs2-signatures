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

`offsets` entries hold an integer (a vtable slot or a struct-member byte
offset), so there are no bytes to scan. They are validated separately: see
`lib_offset.py` for the recipe-driven Linux check and **Reference validation**
below for the snapshot-driven one that also covers Windows.

### Better than the upstream tracker

- **Match count, not boolean.** ianlucas stops at the first hit (✅/❌). We count
  hits per executable section, so we also catch **⚠️ ambiguous** sigs.
- **History trend** (`reports/history/*.json`) - per-run tally over time.
- **Auto-issue** on Forgejo when a sig breaks; auto-closes when green again.
- **Status badge** driven by `reports/badge.json`.

### Reference validation (CS2_VibeSignatures)

Byte-scanning answers "does this pattern still resolve in the binary we
downloaded". It cannot answer "is this still the pattern upstream uses", and for
an `offsets` entry it cannot answer anything at all without a hand-written
recipe.

A CS2_VibeSignatures snapshot answers both. It is one JSON file per game version
listing every symbol the upstream analysis resolved, for Linux **and** Windows:
function signatures, vtable indices, struct-member offsets, full vtable dumps,
globals and patches.

```bash
python3 scripts/fetch_symbols.py --list                          # versions on the site
python3 scripts/fetch_symbols.py --gamever 14178b                # -> data/symbols/14178b.json
python3 scripts/fetch_symbols.py --backend git --upstream --gamever 14180
python3 scripts/check_reference.py --gamever 14178b              # read-only report
```

Two backends, one output shape:

- **site** (default) pulls the content-addressed JSON from `sig.miksen.me` and
  verifies it against the `sha256` and `size` in `gamesymbols/index.json` before
  writing it. One request per version, no auth, no rate limit.
- **git** does a blob-filtered sparse checkout of the analysis repo and parses
  `bin_artifacts/<gamever>/<module>/*.yaml` plus `binary_locks/<gamever>.json`.
  Slower, but it reaches a game version the moment it is committed, which is how
  a build gets covered before it reaches the site. Verified to reproduce the
  site payload byte for byte.

The GitHub contents API is deliberately not used anywhere: it caps anonymous
callers at 60 requests an hour and one game version is over 3500 files.

`check_reference.py` first states how the local binaries relate to the snapshot,
by comparing their SHA-256 against the `binaries` block. `exact` means the
reference describes the very bytes being scanned; `different_build` means an
`outdated` verdict may be a version gap rather than a stale signature.

Verdicts per entry per platform:

- signatures: `match`, `outdated` (two concrete bytes disagree), `no_sig` (the
  symbol was analysed but the record carries no byte pattern), `no_reference`
- offsets: `match`, `mismatch`, `no_reference`

A signature that differs only by a wildcard, or that is a shorter cut of the
same function head, counts as `match`: both patterns describe the same function.
Only a genuine byte conflict is `outdated`.

Name spellings are folded (`A::b`, `A.b` and `A_b` are one key). A genuine
rename is not a spelling problem, so feed those in through the optional
`data/symbol_aliases.json` (`{"gamedata name": "reference name"}`).

`run_all.sh` step 3.5 does this automatically. It resolves the game version from
`data/manifest.json` against `binary_locks/`, fetches that snapshot if it is not
cached, and passes it to `validate_sigs.py`. The whole step is optional and
non-fatal: no network, no git, or an analysis that has not caught up with the
current build all leave the pipeline byte-scanning exactly as it did before.

```bash
NO_SYMBOLS=1 bash scripts/run_all.sh                    # skip the reference tier
SYMBOLS_REPO=https://github.com/HLND2T/CS2_VibeSignatures.git bash scripts/run_all.sh
```

`check_reference.py` stays a read-only debugging view of the same comparison.

What the reference adds to `reports/<id>/status.json`:

- every signature platform block gains a `reference` sub-block (`match`,
  `outdated`, `no_sig`, `no_reference`). The scan still owns the
  ok/broken/ambiguous verdict, so an outdated signature never fails the run: it
  resolves fine, it has just been replaced upstream.
- offset entries gain a **windows** platform block. Nothing else produces one;
  the RTTI walk in `lib_offset` is Linux-only. Where the recipe path had no
  answer (`no_recipe`/`review`) the reference supplies a real verdict, and a
  disagreement between the two routes is kept visible rather than resolved
  silently.
- the tally gains `sig_outdated`, and `reference` names the game version. The
  snapshot commit sha is deliberately **not** stored: it moves on every upstream
  push and would churn a commit out of every run.

`post_gate.py` announces the first `outdated` on an entry, and ignores reference
COVERAGE changes: a symbol appearing in a newer snapshot flips an offset from
`no_recipe` to a real verdict without anything about the game or the gamedata
having changed, so `no_recipe` blocks are left out of the fingerprint.

#### Anchors: reading the offset out of our own binary

Comparing our integer against the reference's integer compares two opinions, and
the reference's opinion is only as current as the snapshot. An anchor removes
that dependency. Both anchor kinds pin the instruction that carries the offset,
with the value sitting in the operand:

```
virtualFunction  vfunc_sig   FF 90 E8 00 00 00     call [rax+0xE8]  -> slot 29
structMember     offset_sig  48 8B 7F 68           mov rdi,[rdi+0x68]
```

So `lib_anchor.py` reads the value back out of the binaries we downloaded. The
answer describes THIS build whichever version the snapshot came from, which is
what makes it usable while the analysis lags the game. It needs nothing but byte
scanning, so unlike the RTTI walk in `lib_offset` it works on Windows.

Order matters. When the anchor spells the displacement out, the strongest test is
whether that exact pattern still occurs: if it does, the instruction still carries
that displacement, with no widening and therefore no ambiguity. Only when the
exact pattern is gone is the hole punched and the replacement read back, and there
every match must agree, since wildcarding four bytes can let a pattern catch
unrelated call sites. Anchors that ship with the displacement already wildcarded
(`offset_sig_disp: N`, meaning the Nth wildcard run) go straight to read back.

Anchor outranks both the recipe and the reference, because those describe how a
value was derived somewhere else and this one is measured here. A disagreement is
a real `stale`, not a version gap.

A separate cheap check needs no anchor at all: an index at or past
`vtable_numvfunc` is wrong on its own terms, and the vtable dumps cover every
class on both platforms.

#### Cross-version diff

```bash
python3 scripts/diff_symbols.py 14178b 14180 --tracked
```

The other checks answer "is this offset right today". This answers "what did the
game move", which is the question worth asking after an update and before
anything has broken: a vtable that gained a slot shifts every index below the
insertion point. `--tracked` narrows it to symbols the registry actually uses.

## VPS setup (x86-64)

Depots `2347771` (Windows) / `2347773` (Linux) download **anonymously** - no
Steam login. Every tracked GitHub repo is public, so the gamedata fetch needs no
token; set `GITHUB_TOKEN` only if a project is marked `"private": true`.

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
data/symbols/<ver>.json   cached CS2_VibeSignatures snapshot (git-ignored clone in .repo/)
data/symbol_aliases.json  optional {gamedata name: reference name} renames
scripts/projects.py       project registry loader + path/URL layout
scripts/depots.py         depot IDs + file paths (single source of truth)
scripts/lib_sig.py        sig->regex + ELF/PE exec-section reader
scripts/lib_symbols.py    reference-snapshot lookup (sigs, offsets, vtables)
scripts/lib_anchor.py     re-derive an offset from our own binary via a reference anchor
scripts/diff_symbols.py   what moved between two snapshots
scripts/fetch_symbols.py  pull a snapshot -> data/symbols/<gamever>.json
scripts/check_reference.py  gamedata vs reference snapshot (read-only report)
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
