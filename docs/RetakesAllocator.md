# cs2-retakes-allocator

Last updated: September 30, 2026 at 23:10:02 GMT

* Manifests: [8582617999835812788](https://steamdb.info/depot/2347771/history/?changeid=M:8582617999835812788), [5185162378762752449](https://steamdb.info/depot/2347773/history/?changeid=M:5185162378762752449)
* Repository: https://github.com/mrc4tt/cs2-retakes-allocator
* Gamedata: https://github.com/mrc4tt/cs2-retakes-allocator/blob/main/Resources/RetakesAllocator_gamedata.json

Cell status: ✅ unique (1 match) &middot; ⚠️ ambiguous (>1) &middot; ❌ broken (0) &middot; ❔ binary not downloaded.

Reference column: ✅ matches the 14186 analysis &middot; 🕓 the analysis uses a different pattern &middot; ❔ no reference for this symbol.

## Signatures

### GiveNamedItem2

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x83\xEC\x2A\x48\xC7\x44\x24\x2A\x2A\x2A\x2A\x2A\x45\x33\xC9\x45\x33\xC0\xC6\x44\x24\x2A\x2A\xE8\x2A\x2A\x2A\x2A\x48\x83\xC4\x2A\xC3\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\x48\x83\xEC
</pre>
</td><td>
<pre>
48 83 EC ? 48 C7 44 24 ? ? ? ? ? 45 33 C9 45 33 C0 C6 44 24 ? ? E8 ? ? ? ? 48 83 C4 ? C3 CC CC CC CC CC CC CC CC CC CC CC CC CC CC 48 83 EC
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x45\x31\xC9\x45\x31\xC0\x31\xC9\x31\xD2\xE9\x2A\x2A\x2A\x2A\xCC\x55\x45\x31\xC9
</pre>
</td><td>
<pre>
45 31 C9 45 31 C0 31 C9 31 D2 E9 ? ? ? ? CC 55 45 31 C9
</pre>
</td></tr>
</table>

### GetCSWeaponDataFromKey

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x08\x57\x48\x83\xEC\x20\x33\xFF\x4C\x8B\xCA\x8B\xD9\x8B\xC7\x48\x85\xD2\x74\x22\x38\x02\x74\x1E\x48\xC7\xC2\xFF\xFF\xFF\xFF\x48\xFF\xC2\x41\x38\x04\x11\x75\xF7\x41\xB8\x26\x59\x41\x31\x49\x8B\xC9\xE8\x2A\x2A\x2A\x2A\x89\x44\x24\x38\x85\xC0
</pre>
</td><td>
<pre>
48 89 5C 24 08 57 48 83 EC 20 33 FF 4C 8B CA 8B D9 8B C7 48 85 D2 74 22 38 02 74 1E 48 C7 C2 FF FF FF FF 48 FF C2 41 38 04 11 75 F7 41 B8 26 59 41 31 49 8B C9 E8 ? ? ? ? 89 44 24 38 85 C0
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x48\x85\xF6\x0F\x84\x2A\x2A\x2A\x2A\x55\x48\x89\xE5\x41\x57\x41\x56\x41\x55\x49\x89\xF5\x41\x54\x53\x48\x81\xEC\x2A\x2A\x2A\x2A\x80\x3E\x2A\x75\x2A\x31\xC0\x48\x81\xC4\x2A\x2A\x2A\x2A\x5B\x41\x5C\x41\x5D\x41\x5E\x41\x5F\x5D\xC3\x0F\x1F\x80\x2A\x2A\x2A\x2A\x4C\x8D\xA5\x2A\x2A\x2A\x2A\x89\xFB
</pre>
</td><td>
<pre>
48 85 F6 0F 84 ? ? ? ? 55 48 89 E5 41 57 41 56 41 55 49 89 F5 41 54 53 48 81 EC ? ? ? ? 80 3E ? 75 ? 31 C0 48 81 C4 ? ? ? ? 5B 41 5C 41 5D 41 5E 41 5F 5D C3 0F 1F 80 ? ? ? ? 4C 8D A5 ? ? ? ? 89 FB
</pre>
</td></tr>
</table>

### CCSPlayer_ItemServices_CanAcquire

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x44\x89\x44\x24\x2A\x48\x89\x54\x24\x2A\x48\x89\x4C\x24\x2A\x55\x53\x56\x57\x41\x54\x41\x55\x41\x56\x41\x57\x48\x8B\xEC
</pre>
</td><td>
<pre>
44 89 44 24 ? 48 89 54 24 ? 48 89 4C 24 ? 55 53 56 57 41 54 41 55 41 56 41 57 48 8B EC
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x41\x56\x49\x89\xF6\x41\x55\x41\x54\x49\x89\xCC\x53\x48\x89\xFB\x48\x83\xEC\x2A\x4C\x8B\x6F\x2A
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 41 56 49 89 F6 41 55 41 54 49 89 CC 53 48 89 FB 48 83 EC ? 4C 8B 6F ?
</pre>
</td></tr>
</table>
