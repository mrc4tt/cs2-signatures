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

* **Last updated:** August 4, 2026 at 11:35:33 GMT
* **Manifests:** [3132779792492138697](https://steamdb.info/depot/2347771/history/?changeid=M:3132779792492138697), [8127770850217610141](https://steamdb.info/depot/2347773/history/?changeid=M:8127770850217610141)
* **Tracked projects:** 5
* **Validated:** 101 ok, 0 ambiguous, 1 broken (0 not-yet-validated)

<table>
<tr><th>Status</th><th>Linux</th><th>Windows</th><th>Project</th><th></th></tr>
<tr><td><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2FCounterStrikeSharp%2Fbadge.json" alt="CounterStrikeSharp"></td><td>✅</td><td>✅</td><td><a href="https://github.com/mrc4tt/CounterStrikeSharp">CounterStrikeSharp</a></td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/CounterStrikeSharp.md">View signatures &rarr;</a></td></tr>
<tr><td><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2FRetakesAllocator%2Fbadge.json" alt="cs2-retakes-allocator"></td><td>✅</td><td>✅</td><td><a href="https://github.com/mrc4tt/cs2-retakes-allocator">cs2-retakes-allocator</a></td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/RetakesAllocator.md">View signatures &rarr;</a></td></tr>
<tr><td><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2FRayTrace%2Fbadge.json" alt="Ray-Trace"></td><td>✅</td><td>✅</td><td><a href="https://git.miksen.me/mikkel/Ray-Trace">Ray-Trace</a></td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/RayTrace.md">View signatures &rarr;</a></td></tr>
<tr><td><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2FMatchZy%2Fbadge.json" alt="MatchZy"></td><td>✅</td><td>✅</td><td><a href="https://git.miksen.me/mikkel/matchzy">MatchZy</a></td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/MatchZy.md">View signatures &rarr;</a></td></tr>
<tr><td><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2FWeaponPaints%2Fbadge.json" alt="WeaponPaints"></td><td>✅</td><td>❌</td><td><a href="https://git.miksen.me/mikkel/weaponpaints">WeaponPaints</a></td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/WeaponPaints.md">View signatures &rarr;</a></td></tr>
</table>

<details open><summary>&#9660; WeaponPaints broken / ambiguous signatures (1)</summary>

<table>
<tr><th>Linux</th><th>Windows</th><th>Subroutine</th></tr>
<tr><td>✅</td><td>❌</td><td>UpdateItemView</td></tr>
</table>
</details>

<!-- STATUS:END -->

---

Setup, cron, and layout notes: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).
