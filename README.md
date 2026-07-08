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

* **Last updated:** July 8, 2026 at 00:45:01 GMT
* **Manifests:** [3747240284300062741](https://steamdb.info/depot/2347771/history/?changeid=M:3747240284300062741), [801866638738702671](https://steamdb.info/depot/2347773/history/?changeid=M:801866638738702671)
* **Validated:** 0 ok, 0 ambiguous, 0 broken (60 not-yet-validated)

<table>
<tr><th>Linux</th><th>Windows</th><th>Project</th><th></th></tr>
<tr><td>❔</td><td>❔</td><td><a href="https://github.com/mrc4tt/CounterStrikeSharp">CounterStrikeSharp</a></td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/CounterStrikeSharp.md">View signatures &rarr;</a></td></tr>
</table>

<!-- STATUS:END -->

---

Dev / ops notes (setup, cron, layout): [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).
