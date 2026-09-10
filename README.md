# CS2 Server Signatures Tracker

[![cs2 sigs](https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2Fbadge.json)](docs/CounterStrikeSharp.md)
[![python](https://img.shields.io/badge/python-3%20stdlib%20only-blue)](docs/DEVELOPMENT.md)
[![license](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

**Did the last Counter-Strike 2 update break your plugins?** This tracker
answers that. It re-downloads the CS2 dedicated-server binaries on every game
update, scans each tracked plugin's `gamedata.json` against them, and reports
which signatures still resolve, which broke, and which became ambiguous.

The table below is regenerated automatically. Green means the signatures a
plugin ships still point at exactly one function in the current binaries.

<!-- STATUS:START -->
## Current status

> ✅ **All 106 signature checks pass** on CS2 `1.41.8.1`.
>
> Last checked September 10, 2026 at 18:15:01 GMT &middot; 4 project(s) tracked

<table>
<tr><th>Project</th><th>Health</th><th>Signatures</th><th>Linux</th><th>Windows</th><th></th></tr>
<tr><td><a href="https://github.com/mrc4tt/CounterStrikeSharp">CounterStrikeSharp</a></td><td><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2FCounterStrikeSharp%2Fbadge.json" alt="CounterStrikeSharp"></td><td align="center">70/70</td><td align="center">✅</td><td align="center">✅</td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/CounterStrikeSharp.md">details &rarr;</a></td></tr>
<tr><td><a href="https://github.com/mrc4tt/cs2-retakes-allocator">cs2-retakes-allocator</a></td><td><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2FRetakesAllocator%2Fbadge.json" alt="cs2-retakes-allocator"></td><td align="center">6/6</td><td align="center">✅</td><td align="center">✅</td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/RetakesAllocator.md">details &rarr;</a></td></tr>
<tr><td><a href="https://git.miksen.me/mikkel/matchzy">MatchZy</a></td><td><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2FMatchZy%2Fbadge.json" alt="MatchZy"></td><td align="center">12/12</td><td align="center">✅</td><td align="center">✅</td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/MatchZy.md">details &rarr;</a></td></tr>
<tr><td><a href="https://git.miksen.me/mikkel/weaponpaints">WeaponPaints</a></td><td><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2FWeaponPaints%2Fbadge.json" alt="WeaponPaints"></td><td align="center">18/18</td><td align="center">✅</td><td align="center">✅</td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/WeaponPaints.md">details &rarr;</a></td></tr>
</table>

<details><summary>&#9660; CounterStrikeSharp outdated vs reference (1)</summary>

These still resolve in the current binaries. The upstream analysis has moved to a different pattern.

<table>
<tr><th>Subroutine</th><th>Platform</th></tr>
<tr><td>ClientPrint</td><td>linux, windows</td></tr>
</table>
</details>

<details><summary>&#9660; Run details</summary>

* **CS2 build:** `1.41.8.1`
* **Signatures:** 106 ok, 0 ambiguous, 0 broken (0 not-yet-validated)
* **Offsets:** 42 ok, 0 stale, 4 without a reference
* **Outdated:** 2 signature(s) still resolve but have been replaced upstream
* **Depot manifests:** [5806169188224907599](https://steamdb.info/depot/2347771/history/?changeid=M:5806169188224907599), [8639120305802825922](https://steamdb.info/depot/2347773/history/?changeid=M:8639120305802825922)
* **Fragility over time:** [docs/stats.md](docs/stats.md)

</details>
<!-- STATUS:END -->

## Reading the results

| Mark | Meaning | What to do |
|---|---|---|
| ✅ | The signature matches exactly one place in the binary. | Nothing. |
| ⚠️ | It matches more than once - ambiguous. | Treat as unreliable; the plugin may hook the wrong function. |
| ❌ | It matches nothing - broken. | The plugin needs a regenerated signature before it will work. |
| 🕓 | It still resolves, but the upstream analysis now uses a different pattern. | Advisory only. |

Each project's page lists every signature with its byte pattern in both
CODE-style (`\x48\x89...`) and IDA-style (`48 89 ...`), so a broken entry can be
compared against your own dump. Historic fragility - which signatures break
update after update - is in [docs/stats.md](docs/stats.md).

## If you run a CS2 server

1. **Before you update**, or right after a patch lands, check the row for the
   plugins you run. All green means their signatures still resolve against the
   binaries Valve just shipped.
2. **A red mark is not a crash report** - it means one function the plugin hooks
   can no longer be found. In practice the plugin loads but that feature
   misbehaves or the server crashes when the code path is hit.
3. **What to do:** wait for the plugin author's update, or take the proposed
   replacement signature from the linked issue or pull request. The tracker
   verifies a proposal matches exactly once; it does not run it, so treat it as
   a candidate, not a fix.
4. **The binaries used for a check** are published as releases, tagged by CS2
   version, if you want to reproduce a result yourself.

## Notifications

A run that changes a result can announce itself:

* **Discord** - one embed per run, delta-first: the verdict, what changed since
  the previous report, per-project health, and the broken entries in full.
  Healthy signatures are counted, not listed. When a replacement signature can
  be derived automatically, a patched `gamedata.json` is attached to the post.
* **Forgejo issue** - opened on breakage, closed when the signatures pass again.
* **Pull request** - projects that opt in with `"propose_pr": true` get a draft
  PR with the patched gamedata for review.

Runs that change nothing stay silent. See
[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md#notifications) for the layout and the
environment variables.

## Track your own plugin

Adding a plugin is a JSON append - no code change. Add an entry to
[`data/projects.json`](data/projects.json):

```json
{
  "id": "MyPlugin",
  "name": "My Plugin",
  "repo": "owner/my-plugin",
  "branch": "main",
  "path": "gamedata/myplugin.json",
  "private": false,
  "propose_pr": false
}
```

* `id` names the report files (`reports/MyPlugin/`, `docs/MyPlugin.md`).
* `path` points at a CounterStrikeSharp-format `gamedata.json` in that repo.
* `host` is optional and defaults to `github.com`; a Forgejo/Gitea host works
  too. Private repos need a token in `.env`.

Then validate just that project:

```bash
python3 scripts/fetch_gamedata.py --project MyPlugin
python3 scripts/validate_sigs.py --project MyPlugin \
  --linux bin_linux/game/csgo/bin/linuxsteamrt64/libserver.so \
  --windows bin_win/game/csgo/bin/win64/server.dll
```

<details><summary>&#9660; How it works</summary>

1. **Detect an update** by comparing per-depot manifest IDs against the last
   seen ones - no download unless something actually changed.
2. **Download only the binaries that matter** (server + engine2, Linux and
   Windows) through DepotDownloader. Megabytes, not a full game install.
3. **Scan** each signature against the binary's executable sections and count
   matches: exactly one is healthy, zero is broken, more than one is ambiguous.
   Offsets are checked against a reference analysis where one is available.
4. **Report**: the table above, the per-project pages under `docs/`, the status
   badges, the fragility history, and - when configured - a Discord post, an
   issue, and a draft PR with proposed replacement signatures.

The whole pipeline is Python 3 standard library plus DepotDownloader, so it runs
on a bare VPS with no package installs.

</details>

## Documentation

* [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) - setup, cron, pipeline internals,
  reference validation, repository layout.
* [docs/stats.md](docs/stats.md) - signature fragility over the tracked history.
* Per-project signature pages are linked from the table above.

---

Inspired by [ianlucas/cs2-signatures](https://github.com/ianlucas/cs2-signatures);
self-hosted on Forgejo. MIT licensed.
