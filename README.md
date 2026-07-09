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

* **Last updated:** July 9, 2026 at 19:15:01 GMT
* **Manifests:** [2853479544375896262](https://steamdb.info/depot/2347771/history/?changeid=M:2853479544375896262), [2410782554857596728](https://steamdb.info/depot/2347773/history/?changeid=M:2410782554857596728)
* **Validated:** 56 ok, 0 ambiguous, 2 broken (0 not-yet-validated)

<table>
<tr><th>Linux</th><th>Windows</th><th>Project</th><th></th></tr>
<tr><td>✅</td><td>❌</td><td><a href="https://github.com/mrc4tt/CounterStrikeSharp">CounterStrikeSharp</a></td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/CounterStrikeSharp.md">View signatures &rarr;</a></td></tr>
</table>

<details open><summary>&#9660; CounterStrikeSharp broken / ambiguous signatures (2)</summary>

<table>
<tr><th>Linux</th><th>Windows</th><th>Subroutine</th></tr>
<tr><td>✅</td><td>❌</td><td>GiveNamedItem</td></tr>
<tr><td>✅</td><td>❌</td><td>CBaseTrigger_EndTouch</td></tr>
</table>
</details>

<!-- STATUS:END -->

---

Dev / ops notes (setup, cron, layout): [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).
