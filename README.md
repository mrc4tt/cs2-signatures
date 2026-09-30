# CS2 Server Signatures Tracker

[![cs2 sigs](https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2Fbadge.json)](docs/USAGE.md)
[![python](https://img.shields.io/badge/python-3%20stdlib%20only-blue)](docs/DEVELOPMENT.md)
[![license](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

**Did the last Counter-Strike 2 update break your plugins?** This tracker
re-downloads the CS2 dedicated-server binaries on every game update and checks
each tracked plugin's signatures against them. Green means a signature still
points at exactly one function in the binaries Valve ships right now.

<!-- STATUS:START -->
## Current status

> ✅ **All 106 signature checks pass** on CS2 `1.41.8.6`.
>
> Last checked September 30, 2026 at 23:10:02 GMT &middot; 4 project(s) tracked

<table>
<tr><th>Project</th><th>Health</th><th>Signatures</th><th>Linux</th><th>Windows</th><th></th></tr>
<tr><td><a href="https://github.com/mrc4tt/CounterStrikeSharp">CounterStrikeSharp</a></td><td><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2FCounterStrikeSharp%2Fbadge.json" alt="CounterStrikeSharp"></td><td align="center">70/70</td><td align="center">✅</td><td align="center">✅</td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/CounterStrikeSharp.md">details &rarr;</a></td></tr>
<tr><td><a href="https://github.com/mrc4tt/cs2-retakes-allocator">cs2-retakes-allocator</a></td><td><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2FRetakesAllocator%2Fbadge.json" alt="cs2-retakes-allocator"></td><td align="center">6/6</td><td align="center">✅</td><td align="center">✅</td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/RetakesAllocator.md">details &rarr;</a></td></tr>
<tr><td><a href="https://git.miksen.me/mikkel/matchzy">MatchZy</a></td><td><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2FMatchZy%2Fbadge.json" alt="MatchZy"></td><td align="center">12/12</td><td align="center">✅</td><td align="center">✅</td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/MatchZy.md">details &rarr;</a></td></tr>
<tr><td><a href="https://git.miksen.me/mikkel/weaponpaints">WeaponPaints</a></td><td><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2FWeaponPaints%2Fbadge.json" alt="WeaponPaints"></td><td align="center">18/18</td><td align="center">✅</td><td align="center">✅</td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/WeaponPaints.md">details &rarr;</a></td></tr>
</table>

<details><summary>&#9660; Run details</summary>

* **CS2 build:** `1.41.8.6`
* **Signatures:** 106 ok, 0 ambiguous, 0 broken (0 not-yet-validated)
* **Offsets:** 44 ok, 0 stale, 0 without a reference
* **Depot manifests:** [8582617999835812788](https://steamdb.info/depot/2347771/history/?changeid=M:8582617999835812788), [5185162378762752449](https://steamdb.info/depot/2347773/history/?changeid=M:5185162378762752449)
* **Fragility over time:** [docs/stats.md](docs/stats.md)

</details>
<!-- STATUS:END -->

✅ unique match &middot; ⚠️ ambiguous &middot; ❌ broken &middot; 🕓 still resolves, replaced upstream

* **[What the results mean, and what to do about them](docs/USAGE.md)** - for
  server owners, plus how to track your own plugin.
* [Reference coverage gaps](docs/ReferenceGaps.md) - tracked symbols the
  analysis cannot vouch for yet, updated every run.
* [Setup, pipeline internals, notifications](docs/DEVELOPMENT.md)
* [Signature fragility over time](docs/stats.md)

---

Inspired by [ianlucas/cs2-signatures](https://github.com/ianlucas/cs2-signatures);
self-hosted on Forgejo. MIT licensed.
