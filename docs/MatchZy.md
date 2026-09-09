# MatchZy

Last updated: September 9, 2026 at 22:35:01 GMT

* Manifests: [7475134589078180787](https://steamdb.info/depot/2347771/history/?changeid=M:7475134589078180787), [7308152089951763351](https://steamdb.info/depot/2347773/history/?changeid=M:7308152089951763351)
* Repository: https://git.miksen.me/mikkel/matchzy
* Gamedata: https://git.miksen.me/mikkel/matchzy/src/branch/main/gamedata/matchzy.json

Cell status: ✅ unique (1 match) &middot; ⚠️ ambiguous (>1) &middot; ❌ broken (0) &middot; ❔ binary not downloaded.

Reference column: ✅ matches the 14180 analysis &middot; 🕓 the analysis uses a different pattern &middot; ❔ no reference for this symbol.

## Signatures

### CBasePlayerController_HandleCommand_JoinTeam

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x2A\x44\x88\x44\x24\x2A\x55\x56\x57\x41\x54\x41\x55\x41\x56\x41\x57\x48\x8D\x6C\x24\x2A\x48\x81\xEC\x2A\x2A\x2A\x2A\x48\x8B\x3D\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
48 89 5C 24 ? 44 88 44 24 ? 55 56 57 41 54 41 55 41 56 41 57 48 8D 6C 24 ? 48 81 EC ? ? ? ? 48 8B 3D ? ? ? ?
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x41\x56\x41\x89\xD6\x41\x55\x41\x54\x41\x89\xF4\x53\x48\x89\xFB\x48\x81\xEC\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 41 56 41 89 D6 41 55 41 54 41 89 F4 53 48 89 FB 48 81 EC ? ? ? ?
</pre>
</td></tr>
</table>

### CCSGameRules_PostCleanUp

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x8B\xC4\x55\x41\x57\x48\x8D\xA8\x2A\x2A\x2A\x2A\x48\x81\xEC\x2A\x2A\x2A\x2A\x80\xB9\x2A\x01\x00\x00\x2A
</pre>
</td><td>
<pre>
48 8B C4 55 41 57 48 8D A8 ? ? ? ? 48 81 EC ? ? ? ? 80 B9 ? 01 00 00 ?
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x49\x89\xFF\x41\x56\x41\x55\x41\x54\x53\x48\x81\xEC\x2A\x2A\x2A\x2A\xE8\x2A\x2A\x2A\x2A\x66\x83\xF8\x2A
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 49 89 FF 41 56 41 55 41 54 53 48 81 EC ? ? ? ? E8 ? ? ? ? 66 83 F8 ?
</pre>
</td></tr>
</table>

### CSmokeGrenadeProjectile_Create

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x8B\xC4\x48\x89\x58\x2A\x48\x89\x68\x2A\x48\x89\x70\x2A\x57\x41\x56\x41\x57\x48\x81\xEC\x2A\x2A\x2A\x2A\x48\x8B\xB4\x24\x2A\x2A\x2A\x2A\x4D\x8B\xF8
</pre>
</td><td>
<pre>
48 8B C4 48 89 58 ? 48 89 68 ? 48 89 70 ? 57 41 56 41 57 48 81 EC ? ? ? ? 48 8B B4 24 ? ? ? ? 4D 8B F8
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x4C\x89\xC1\x48\x89\xE5\x41\x57\x49\x89\xFF\x41\x56\x45\x89\xCE
</pre>
</td><td>
<pre>
55 4C 89 C1 48 89 E5 41 57 49 89 FF 41 56 45 89 CE
</pre>
</td></tr>
</table>

### CHEGrenadeProjectile_Create

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x2A\x48\x89\x6C\x24\x2A\x48\x89\x74\x24\x2A\x57\x48\x83\xEC\x2A\x48\x8B\x6C\x24\x2A\x49\x8B\xF8\x4C\x8B\xC2\x0F\x29\x74\x24\x2A
</pre>
</td><td>
<pre>
48 89 5C 24 ? 48 89 6C 24 ? 48 89 74 24 ? 57 48 83 EC ? 48 8B 6C 24 ? 49 8B F8 4C 8B C2 0F 29 74 24 ?
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x4C\x89\xC1\x48\x89\xE5\x41\x57\x49\x89\xFF\x41\x56\x49\x89\xD6
</pre>
</td><td>
<pre>
55 4C 89 C1 48 89 E5 41 57 49 89 FF 41 56 49 89 D6
</pre>
</td></tr>
</table>

### CMolotovProjectile_Create

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x8B\xC4\x48\x89\x58\x2A\x4C\x89\x40\x2A\x48\x89\x48\x2A\x55\x56\x57\x41\x54\x41\x55\x41\x56\x41\x57\x48\x8D\x6C\x24\x2A
</pre>
</td><td>
<pre>
48 8B C4 48 89 58 ? 4C 89 40 ? 48 89 48 ? 55 56 57 41 54 41 55 41 56 41 57 48 8D 6C 24 ?
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x8D\x05\x2A\x2A\x2A\x2A\x48\x89\xE5\x41\x57\x41\x56\x41\x55\x41\x54\x49\x89\xFC\x53\x48\x81\xEC\x2A\x2A\x2A\x2A\x4C\x8D\x35\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
55 48 8D 05 ? ? ? ? 48 89 E5 41 57 41 56 41 55 41 54 49 89 FC 53 48 81 EC ? ? ? ? 4C 8D 35 ? ? ? ?
</pre>
</td></tr>
</table>

### CDecoyProjectile_Create

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x8B\xC4\x55\x56\x48\x81\xEC\x58\x01\x00\x00\x48\x89\x58\x08
</pre>
</td><td>
<pre>
48 8B C4 55 56 48 81 EC 58 01 00 00 48 89 58 08
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x49\x89\xFF\x41\x56\x41\x55\x41\x54\x53\x48\x83\xEC\x68\x48\x3B\x15\x15
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 49 89 FF 41 56 41 55 41 54 53 48 83 EC 68 48 3B 15 15
</pre>
</td></tr>
</table>

## Offsets

A vtable slot index or a struct-member byte offset. There are no bytes to scan, so these are checked by re-deriving the integer: `reference` reads it from the analysis snapshot (both platforms), `anchored` / `structural` / `structoffset` re-derive it from the binary itself (Linux only).

<table>
<tr><th>Entry</th><th>Windows</th><th>Linux</th><th>Checked by</th></tr>
<tr><td>CCSPlayer_WeaponServices_SelectItem</td><td>✅ 30</td><td>✅ 31</td><td>reference</td></tr>
</table>
