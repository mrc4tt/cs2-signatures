# CS2 Server Signatures Tracker

[![cs2 sigs](https://img.shields.io/endpoint?url=https%3A%2F%2Fgit.miksen.me%2Fmikkel%2Fcs2-signatures%2Fraw%2Fbranch%2Fmain%2Freports%2Fbadge.json)](docs/CounterStrikeSharp.md)

Tracks CS2 plugin gamedata signatures against live CS2 server binaries.
Inspired by [ianlucas/cs2-signatures](https://github.com/ianlucas/cs2-signatures),
self-hosted on Forgejo. Each tracked project is one CSS-format `gamedata.json`
in some GitHub repo — listed in [`data/projects.json`](data/projects.json) —
starting with the [CounterStrikeSharp](https://github.com/mrc4tt/CounterStrikeSharp)
**mrc4tt fork**. Add a plugin by appending to that file (see
[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)); no code change.

On each CS2 update it re-downloads `libserver.so` + `server.dll` and scans every
project's signatures: which still match (unique), which broke (0 matches), which
went ambiguous (>1 match). Per-project detail lives in `docs/<project>.md`.

<!-- STATUS:START -->
## Signatures

* **Last updated:** July 11, 2026 at 09:30:01 GMT
* **Manifests:** [7679405674131902105](https://steamdb.info/depot/2347771/history/?changeid=M:7679405674131902105), [5502194087696430282](https://steamdb.info/depot/2347773/history/?changeid=M:5502194087696430282)
* **Tracked projects:** 2
* **Validated:** 60 ok, 0 ambiguous, 0 broken (0 not-yet-validated)

<table>
<tr><th>Linux</th><th>Windows</th><th>Project</th><th></th></tr>
<tr><td>✅</td><td>✅</td><td><a href="https://github.com/mrc4tt/CounterStrikeSharp">CounterStrikeSharp</a></td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/CounterStrikeSharp.md">View signatures &rarr;</a></td></tr>
<tr><td>✅</td><td>✅</td><td><a href="https://github.com/mrc4tt/cs2-retakes-allocator">cs2-retakes-allocator</a></td><td><a href="https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/docs/RetakesAllocator.md">View signatures &rarr;</a></td></tr>
</table>

<!-- STATUS:END -->

---

Dev / ops notes (setup, cron, layout): [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).
