# CS2 Server Signatures Tracker

[![cs2 sigs](https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2Fbadge.json)](docs/CounterStrikeSharp.md)

Validates Counter-Strike 2 plugin gamedata signatures against the live CS2
dedicated-server binaries. Each tracked project is a CounterStrikeSharp-format
`gamedata.json`; on every game update the tracker re-downloads the server
binaries and reports which signatures still resolve, which broke, and which
became ambiguous.

Tracked projects live in [`data/projects.json`](data/projects.json) - currently
the [CounterStrikeSharp](https://github.com/mrc4tt/CounterStrikeSharp) fork and
[cs2-retakes-allocator](https://github.com/mrc4tt/cs2-retakes-allocator). Adding
a project needs no code change; see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

Inspired by [ianlucas/cs2-signatures](https://github.com/ianlucas/cs2-signatures);
self-hosted on Forgejo.

## How it works

1. Detects a CS2 update by comparing per-depot manifest IDs.
2. Downloads only the server/engine binaries - a handful of files via
   DepotDownloader, not the full install.
3. Scans each signature against the binary's executable sections and counts
   matches: exactly one is healthy, zero is broken, more than one is ambiguous.
4. Regenerates the table below, the per-project pages under `docs/`, the status
   badge, and - when configured - a Discord post and a Forgejo issue on breakage.

<!-- STATUS:START -->
## Signatures

* **Last updated:** September 9, 2026 at 22:50:01 GMT
* **Manifests:** [5806169188224907599](https://steamdb.info/depot/2347771/history/?changeid=M:5806169188224907599), [8639120305802825922](https://steamdb.info/depot/2347773/history/?changeid=M:8639120305802825922)
* **Tracked projects:** 4
* **Validated:** 100 ok, 0 ambiguous, 6 broken (0 not-yet-validated)
* **Offsets:** 18 ok, 0 stale, 5 without a reference

<table>
<tr><th>Status</th><th>Linux</th><th>Windows</th><th>Project</th><th></th></tr>
<tr><td><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2FCounterStrikeSharp%2Fbadge.json" alt="CounterStrikeSharp"></td><td>❌</td><td>❌</td><td><a href="https://github.com/mrc4tt/CounterStrikeSharp">CounterStrikeSharp</a></td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/CounterStrikeSharp.md">View signatures &rarr;</a></td></tr>
<tr><td><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2FRetakesAllocator%2Fbadge.json" alt="cs2-retakes-allocator"></td><td>✅</td><td>✅</td><td><a href="https://github.com/mrc4tt/cs2-retakes-allocator">cs2-retakes-allocator</a></td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/RetakesAllocator.md">View signatures &rarr;</a></td></tr>
<tr><td><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2FMatchZy%2Fbadge.json" alt="MatchZy"></td><td>❌</td><td>✅</td><td><a href="https://git.miksen.me/mikkel/matchzy">MatchZy</a></td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/MatchZy.md">View signatures &rarr;</a></td></tr>
<tr><td><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2FWeaponPaints%2Fbadge.json" alt="WeaponPaints"></td><td>✅</td><td>✅</td><td><a href="https://git.miksen.me/mikkel/weaponpaints">WeaponPaints</a></td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/WeaponPaints.md">View signatures &rarr;</a></td></tr>
</table>

<details open><summary>&#9660; CounterStrikeSharp broken / ambiguous signatures (4)</summary>

<table>
<tr><th>Linux</th><th>Windows</th><th>Subroutine</th></tr>
<tr><td>✅</td><td>❌</td><td>CBaseModelEntity_SetModel</td></tr>
<tr><td>❌</td><td>❌</td><td>CCSCustomHudLayout_SetDialogVariableStringForPlayer</td></tr>
<tr><td>❌</td><td>✅</td><td>CCSCustomHudLayout_SetHasClass</td></tr>
<tr><td>✅</td><td>❌</td><td>CCSCustomHudLayout_SetHasClassForPlayer</td></tr>
</table>
</details>

<details open><summary>&#9660; MatchZy broken / ambiguous signatures (1)</summary>

<table>
<tr><th>Linux</th><th>Windows</th><th>Subroutine</th></tr>
<tr><td>❌</td><td>✅</td><td>CDecoyProjectile_Create</td></tr>
</table>
</details>

<!-- STATUS:END -->

---

Setup, cron, and layout notes: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).
