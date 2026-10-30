# MatchZy

Last updated: October 30, 2026 at 22:15:31 GMT

* Manifests: [4494425425081083634](https://steamdb.info/depot/2347771/history/?changeid=M:4494425425081083634), [6232960523750647649](https://steamdb.info/depot/2347773/history/?changeid=M:6232960523750647649)
* Repository: https://github.com/mrc4tt/MatchZy
* Gamedata: https://github.com/mrc4tt/MatchZy/blob/main/gamedata/matchzy.json

Cell status: ✅ unique (1 match) &middot; ⚠️ ambiguous (>1) &middot; ❌ broken (0) &middot; ❔ binary not downloaded.

Reference column: ✅ matches the 14193 analysis &middot; 🕓 the analysis uses a different pattern &middot; ❔ no reference for this symbol.

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
\x55\x48\x89\xE5\x41\x57\x41\x56\x41\x55\x41\x54\x41\x89\xF4\x53\x48\x89\xFB\x48\x81\xEC\x2A\x2A\x2A\x2A\x48\x8D\x05\x2A\x2A\x2A\x2A\x89\x95\x2A\x2A\x2A\x2A\x4C\x8B\x28\x4C\x89\xEF\xE8\x2A\x2A\x2A\x2A\x84\xC0\x0F\x85\x2A\x2A\x2A\x2A\x48\x89\xDF\x45\x31\xFF\xE8
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 41 56 41 55 41 54 41 89 F4 53 48 89 FB 48 81 EC ? ? ? ? 48 8D 05 ? ? ? ? 89 95 ? ? ? ? 4C 8B 28 4C 89 EF E8 ? ? ? ? 84 C0 0F 85 ? ? ? ? 48 89 DF 45 31 FF E8
</pre>
</td></tr>
</table>

### CCSGameRules_PostCleanUp

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x8B\xC4\x55\x41\x57\x48\x8D\xA8\x2A\x2A\x2A\x2A\x48\x81\xEC\x2A\x2A\x2A\x2A\x80\xB9\x2A\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
48 8B C4 55 41 57 48 8D A8 ? ? ? ? 48 81 EC ? ? ? ? 80 B9 ? ? ? ? ?
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
\x48\x89\x5C\x24\x2A\x48\x89\x6C\x24\x2A\x48\x89\x74\x24\x2A\x57\x41\x56\x41\x57\x48\x83\xEC\x2A\x48\x8B\xB4\x24\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
48 89 5C 24 ? 48 89 6C 24 ? 48 89 74 24 ? 57 41 56 41 57 48 83 EC ? 48 8B B4 24 ? ? ? ?
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x4C\x89\xC1\x48\x89\xE5\x41\x57\x41\x56
</pre>
</td><td>
<pre>
55 4C 89 C1 48 89 E5 41 57 41 56
</pre>
</td></tr>
</table>

### CHEGrenadeProjectile_Create

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x2A\x48\x89\x6C\x24\x2A\x48\x89\x74\x24\x2A\x57\x48\x83\xEC\x2A\x48\x8B\xAC\x24\x2A\x2A\x2A\x2A\x49\x8B\xF8
</pre>
</td><td>
<pre>
48 89 5C 24 ? 48 89 6C 24 ? 48 89 74 24 ? 57 48 83 EC ? 48 8B AC 24 ? ? ? ? 49 8B F8
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
\x48\x8B\xC4\x48\x89\x58\x2A\x48\x89\x70\x2A\x48\x89\x78\x2A\x4C\x89\x40\x2A\x55\x41\x54\x41\x55\x41\x56\x41\x57\x48\x8D\x6C\x24\x2A
</pre>
</td><td>
<pre>
48 8B C4 48 89 58 ? 48 89 70 ? 48 89 78 ? 4C 89 40 ? 55 41 54 41 55 41 56 41 57 48 8D 6C 24 ?
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
\x40\x55\x56\x48\x83\xEC\x2A\x48\x89\x5C\x24\x2A\x48\x8B\xD9
</pre>
</td><td>
<pre>
40 55 56 48 83 EC ? 48 89 5C 24 ? 48 8B D9
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x4C\x89\xC1\x48\x89\xE5\x41\x57\x45\x89\xCF\x41\x56\x49\x89\xFE\x41\x55\x49\x89\xD5\x48\x89\xF2\x48\x89\xFE\x41\x54\x48\x8D\x3D\x2A\x2A\x2A\x2A\x4D\x89\xC4\x53\x48\x83\xEC\x2A\xE8\x2A\x2A\x2A\x2A\x45\x31\xC0
</pre>
</td><td>
<pre>
55 4C 89 C1 48 89 E5 41 57 45 89 CF 41 56 49 89 FE 41 55 49 89 D5 48 89 F2 48 89 FE 41 54 48 8D 3D ? ? ? ? 4D 89 C4 53 48 83 EC ? E8 ? ? ? ? 45 31 C0
</pre>
</td></tr>
</table>

## Offsets

A vtable slot index or a struct-member byte offset. There are no bytes to scan, so these are checked by re-deriving the integer: `reference` reads it from the analysis snapshot (both platforms), `anchored` / `structural` / `structoffset` re-derive it from the binary itself (Linux only).

<table>
<tr><th>Entry</th><th>Windows</th><th>Linux</th><th>Checked by</th></tr>
<tr><td>CCSPlayer_WeaponServices_SelectItem</td><td>✅ 30</td><td>✅ 31</td><td>reference</td></tr>
</table>
