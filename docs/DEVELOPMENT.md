# Development / operations

## How it works

```
projects.py         registry: data/projects.json -> tracked projects + path/URL layout
check_update.py     DepotDownloader -manifest-only per depot -> changed?
fetch_gamedata.py   pull each project's gamedata.json -> data/<id>/gamedata.json
download_bins.sh    DepotDownloader depots 2347771/2347773 -> server + engine2 (MB not GB)
validate_sigs.py    each sig -> bytes regex -> scan ELF/PE exec sections -> count (per project)
gen_report.py       -> README dashboard + docs/<id>.md + aggregate badge + history
post_gate.py        is this change worth announcing? + named delta for the report
post_discord.py     delta-first Discord embed (see Notifications)
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

A third anchor source covers the case where the analysis files a member as a plain
`function` whose pattern happens to span the access instruction:

```
48 83 C1 70 E9 D7 EC 44 00      add rcx, 0x70
```

There is no recorded integer to pair that with, so the gamedata's own value is
used to locate the displacement, and the check becomes "does our binary still
encode that offset at the site the analysis found". Weaker, since it cannot
produce a value from nothing, but it still catches a moved offset: once the exact
pattern stops matching, the read back reports what replaced it. The status block
records which source answered under `anchor.via`.

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

## Notifications

Every announcement is gated twice. `run_all.sh` step 5 decides whether anything
changed at all (commit + push); step 5.5 runs `post_gate.py`, which decides
whether the change is worth telling anyone about. A gamedata rename, a key
reorder, or a new CS2 build where every signature still resolves passes the
first gate and is stopped by the second.

### Discord (`post_discord.py`)

Default layout is delta-first: one embed answering "what changed", not "what
exists". Healthy signatures are counted; broken and ambiguous ones are listed in
full. Sections appear only when they have content:

```
CS2 Signatures - 1.41.8.1                              [colour = worst verdict]

🔴 1 broken of 106 signature checks - regenerate
`105 ok` · `0 ambiguous` · `1 broken` · `0 not validated`
Offsets: `39 ok` · `0 stale` · `7 no reference`
Since last report: 1 new break · 1 re-signed
Game build: `1.41.8.0` → `1.41.8.1`
Updated 2 minutes ago · Full report · Fragility · This run

Changes (2)
  🔴 `CDecoyProjectile_Create` · linux · ok → broken
  🔁 `CMolotovProjectile_Create` · windows · re-signed
Broken / ambiguous (1)
  🔴 `CDecoyProjectile_Create` 🔥 · linux · broken · 🔧 fix proposed
Projects (4)
  🟢 CounterStrikeSharp     `██████████` 70/70 · W 35/35 · L 35/35
  🔴 MatchZy                `█████████░` 11/12 · W 6/6 · L 5/6
  ...
Manifests  5806169…  8639120…
```

Three inputs beyond the statuses, all optional - a missing one costs that
section and nothing else:

| Input | Written by | Used for |
|---|---|---|
| `reports/delta.json` | `post_gate.py --write-delta` (step 5.5) | the Changes section |
| `reports/fragility.json` | `gen_stats.py --json` (step 6) | the 🔥 habitual-breaker marker |
| `reports/history/*.json` | `gen_report.py` (step 6) | the previous CS2 build, for `old -> new` |

Both scratch files are git-ignored: they are derived from committed data and
rewritten every run.

The delta has to be handed over on disk because the Discord step runs *after*
the commit - by then `HEAD` is the new state and the diff is no longer
computable. When the file is missing or older than the statuses it describes,
`post_discord.py` recomputes the delta against `HEAD` itself, which is what a
manual pre-commit `--preview` wants.

Modes and switches:

```bash
python3 scripts/post_discord.py --preview             # default report, not sent
python3 scripts/post_discord.py --preview --example   # synthetic breakage
python3 scripts/post_discord.py --full                # every signature listed
python3 scripts/post_discord.py --separate            # one card per project
python3 scripts/post_discord.py --delete-message ID   # remove a post again
```

`DISCORD_WEBHOOK` may hold several comma- or whitespace-separated URLs to mirror
the report into more than one server. `DISCORD_MENTION` (a numeric **user** id,
which is global, unlike a per-guild role id) pings only when something is broken
or ambiguous.

### Reference gaps back to the analysis

The two repos run on different machines and share nothing but published
artifacts: the tracker reads snapshots from CS2_VibeSignatures, and this is the
one path back. `reference_gaps.py` collects the tracked symbols the analysis
cannot answer for, worst first:

| Category | Meaning |
|---|---|
| `no_verdict` | an offset with neither a working recipe/anchor nor a reference. Nothing checks that value; the gamedata number is taken on trust. |
| `missing_symbol` | a signature whose symbol is absent from the snapshot, so nothing can say whether the pattern is still the one upstream uses. |
| `missing_pattern` | the symbol was analysed, but the record carries no byte pattern to compare against. |

Only symbols in `data/projects.json` are reported; a snapshot covers thousands
nobody here tracks, and a request list has to be short to be acted on.

`open_gap_issue.py` keeps **one** issue in the analysis repo in sync with that
list. The body carries a fingerprint of the gap SET, deliberately excluding the
snapshot version: a new game build with the same holes is not news, and an
unchanged fingerprint makes the run do nothing at all. When the last gap closes,
the issue is updated once more and closed; if a gap comes back it reopens.

```bash
python3 scripts/reference_gaps.py                  # summary
python3 scripts/reference_gaps.py --markdown       # the issue body
python3 scripts/open_gap_issue.py --dry-run        # print, call no API
python3 scripts/open_gap_issue.py                  # create or update
```

Target repo defaults to the one `fetch_symbols.py` reads (`SYMBOLS_ISSUE_REPO`
overrides). Needs `GITHUB_TOKEN`/`GH_TOKEN` with issue write; without it,
`run_all.sh` step 7.6 skips silently. `NO_GAP_ISSUE=1` turns it off.

### Issues and pull requests

`open_issue.py` opens a Forgejo issue on breakage and closes it when the
signatures pass again. `open_pr.py` opens a draft PR with the patched gamedata
against each project that sets `"propose_pr": true`. Both need `FORGEJO_TOKEN`
and are skipped silently when it is unset.

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
scripts/post_discord.py   Discord webhook report (across all projects)
scripts/gen_stats.py      signature fragility mined from git history -> docs/stats.md
scripts/reference_gaps.py what the reference cannot answer for (tracked symbols only)
scripts/open_gap_issue.py one stable issue in the analysis repo, kept in sync
scripts/test.sh           syntax check + unit tests
scripts/run_all.sh        full pipeline (validate + commit + push)
scripts/cron.sh           cron entrypoint (loads .env, logs)
docs/<id>.md              per-signature detail per project (CODE + IDA style)
reports/<id>/status.json  machine-readable result per project
reports/badge.json        shields.io endpoint (aggregate)
reports/history/*.json    per-run tally + CS2 build + per-project breakdown
reports/delta.json        per-run named delta, post_gate -> post_discord (ignored)
reports/fragility.json    per-run breakage counts, gen_stats -> post_discord (ignored)
reports/reference_gaps.json  symbols the reference cannot answer for (ignored)
docs/stats.md             signature fragility over the tracked history
```
