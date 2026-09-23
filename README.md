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

> ❌ **28 of 106 signature checks are broken** on CS2 `1.41.8.2` - the affected plugins need regenerated signatures.
>
> Last checked September 23, 2026 at 17:55:02 GMT &middot; 4 project(s) tracked

<table>
<tr><th>Project</th><th>Health</th><th>Signatures</th><th>Linux</th><th>Windows</th><th></th></tr>
<tr><td><a href="https://github.com/mrc4tt/CounterStrikeSharp">CounterStrikeSharp</a></td><td><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2FCounterStrikeSharp%2Fbadge.json" alt="CounterStrikeSharp"></td><td align="center">45/70</td><td align="center">❌</td><td align="center">❌</td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/CounterStrikeSharp.md">details &rarr;</a></td></tr>
<tr><td><a href="https://github.com/mrc4tt/cs2-retakes-allocator">cs2-retakes-allocator</a></td><td><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2FRetakesAllocator%2Fbadge.json" alt="cs2-retakes-allocator"></td><td align="center">4/6</td><td align="center">❌</td><td align="center">❌</td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/RetakesAllocator.md">details &rarr;</a></td></tr>
<tr><td><a href="https://git.miksen.me/mikkel/matchzy">MatchZy</a></td><td><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2FMatchZy%2Fbadge.json" alt="MatchZy"></td><td align="center">10/12</td><td align="center">✅</td><td align="center">❌</td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/MatchZy.md">details &rarr;</a></td></tr>
<tr><td><a href="https://git.miksen.me/mikkel/weaponpaints">WeaponPaints</a></td><td><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2FWeaponPaints%2Fbadge.json" alt="WeaponPaints"></td><td align="center">17/18</td><td align="center">✅</td><td align="center">❌</td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/WeaponPaints.md">details &rarr;</a></td></tr>
</table>

<details open><summary>&#9660; CounterStrikeSharp broken / ambiguous signatures (18)</summary>

<table>
<tr><th>Linux</th><th>Windows</th><th>Subroutine</th></tr>
<tr><td>❌</td><td>⚠️</td><td>CCSPlayerPawnBase_PostThink</td></tr>
<tr><td>✅</td><td>❌</td><td>CBaseModelEntity_SetModel</td></tr>
<tr><td>❌</td><td>✅</td><td>CCSPlayer_WeaponServices_CanUse</td></tr>
<tr><td>❌</td><td>❌</td><td>CCSPlayer_ItemServices_CanAcquire</td></tr>
<tr><td>❌</td><td>✅</td><td>CCSGameRules_TerminateRound</td></tr>
<tr><td>✅</td><td>❌</td><td>CEntityInstance_AcceptInput</td></tr>
<tr><td>✅</td><td>❌</td><td>CEntitySystem_AddEntityIOEvent</td></tr>
<tr><td>❌</td><td>✅</td><td>CBasePlayerPawn_RemovePlayerItem</td></tr>
<tr><td>❌</td><td>✅</td><td>CBaseTrigger_StartTouch</td></tr>
<tr><td>❌</td><td>❌</td><td>CBaseTrigger_EndTouch</td></tr>
<tr><td>❌</td><td>❌</td><td>CEntityIOOutput_FireOutputInternal</td></tr>
<tr><td>⚠️</td><td>✅</td><td>IGameSystem_InitAllSystems_pFirst</td></tr>
<tr><td>❌</td><td>✅</td><td>CheckTransmit</td></tr>
<tr><td>❌</td><td>❌</td><td>CCSCustomHudLayout_SetDialogVariableStringForPlayer</td></tr>
<tr><td>❌</td><td>✅</td><td>CCSCustomHudLayout_SetHasClass</td></tr>
<tr><td>❌</td><td>❌</td><td>CCSCustomHudLayout_SetHasClassForPlayer</td></tr>
<tr><td>❌</td><td>✅</td><td>CCSPointScript_OnCustomHudClicked</td></tr>
<tr><td>❌</td><td>❌</td><td>CCSCustomHudLayout_SetInputCaptureEnabled</td></tr>
</table>
</details>

<details open><summary>&#9660; cs2-retakes-allocator broken / ambiguous signatures (1)</summary>

<table>
<tr><th>Linux</th><th>Windows</th><th>Subroutine</th></tr>
<tr><td>❌</td><td>❌</td><td>CCSPlayer_ItemServices_CanAcquire</td></tr>
</table>
</details>

<details open><summary>&#9660; MatchZy broken / ambiguous signatures (2)</summary>

<table>
<tr><th>Linux</th><th>Windows</th><th>Subroutine</th></tr>
<tr><td>✅</td><td>❌</td><td>CHEGrenadeProjectile_Create</td></tr>
<tr><td>✅</td><td>❌</td><td>CMolotovProjectile_Create</td></tr>
</table>
</details>

<details open><summary>&#9660; WeaponPaints broken / ambiguous signatures (1)</summary>

<table>
<tr><th>Linux</th><th>Windows</th><th>Subroutine</th></tr>
<tr><td>✅</td><td>❌</td><td>CAttributeList::SetOrAddAttributeValueByName</td></tr>
</table>
</details>

<details><summary>&#9660; Run details</summary>

* **CS2 build:** `1.41.8.2`
* **Signatures:** 76 ok, 2 ambiguous, 28 broken (0 not-yet-validated)
* **Offsets:** 12 ok, 4 stale, 6 without a reference
* **Depot manifests:** [3417992560980425656](https://steamdb.info/depot/2347771/history/?changeid=M:3417992560980425656), [2116299376055199661](https://steamdb.info/depot/2347773/history/?changeid=M:2116299376055199661)
* **Fragility over time:** [docs/stats.md](docs/stats.md)

</details>
<!-- STATUS:END -->

✅ unique match &middot; ⚠️ ambiguous &middot; ❌ broken &middot; 🕓 still resolves, replaced upstream

* **[What the results mean, and what to do about them](docs/USAGE.md)** - for
  server owners, plus how to track your own plugin.
* [Setup, pipeline internals, notifications](docs/DEVELOPMENT.md)
* [Signature fragility over time](docs/stats.md)

---

Inspired by [ianlucas/cs2-signatures](https://github.com/ianlucas/cs2-signatures);
self-hosted on Forgejo. MIT licensed.
