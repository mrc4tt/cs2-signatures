# GameBanFix

Last updated: November 5, 2026 at 01:20:13 GMT

* Manifests: [3019944380727688040](https://steamdb.info/depot/2347771/history/?changeid=M:3019944380727688040), [8513165868182791792](https://steamdb.info/depot/2347773/history/?changeid=M:8513165868182791792)
* Repository: https://github.com/mrc4tt/GameBanFix
* Fork of: [Cruze03/GameBanFix](https://github.com/Cruze03/GameBanFix)
* Gamedata: https://github.com/mrc4tt/GameBanFix/blob/main/gamedata/gamebanfix.games.txt

Cell status: ✅ unique (1 match) &middot; ⚠️ ambiguous (>1) &middot; ❌ broken (0) &middot; ❔ binary not downloaded.

Reference column: ✅ matches the 14196 analysis &middot; 🕓 the analysis uses a different pattern &middot; ❔ no reference for this symbol.

## Signatures

### GameSystem_Think_CheckSteamBan

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>❔</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x41\x54\x48\x81\xEC\x2A\x2A\x2A\x2A\x48\x8B\x05\x2A\x2A\x2A\x2A\x44\x8B\x60\x2A
</pre>
</td><td>
<pre>
41 54 48 81 EC ? ? ? ? 48 8B 05 ? ? ? ? 44 8B 60 ?
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x41\x56\x41\x55\x41\x54\x53\x48\x83\xEC\x2A\x48\x8B\x05\x2A\x2A\x2A\x2A\x44\x8B\x68\x2A\x45\x85\xED\x0F\x8E\x2A\x2A\x2A\x2A\x8B\x15\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 41 56 41 55 41 54 53 48 83 EC ? 48 8B 05 ? ? ? ? 44 8B 68 ? 45 85 ED 0F 8E ? ? ? ? 8B 15 ? ? ? ?
</pre>
</td></tr>
</table>

### CCSGameRules__sm_mapGcBanInformation

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>❔</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x8D\x0D\x2A\x2A\x2A\x2A\x45\x33\xC0\x4C\x89\x74\x24\x2A
</pre>
</td><td>
<pre>
48 8D 0D ? ? ? ? 45 33 C0 4C 89 74 24 ?
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x48\x8D\x35\x2A\x2A\x2A\x2A\x89\xC2\x48\x63\x46\x2A
</pre>
</td><td>
<pre>
48 8D 35 ? ? ? ? 89 C2 48 63 46 ?
</pre>
</td></tr>
</table>
