# Ray-Trace

Last updated: August 12, 2026 at 22:50:01 GMT

* Manifests: [358563799254497787](https://steamdb.info/depot/2347771/history/?changeid=M:358563799254497787), [3612056480687749066](https://steamdb.info/depot/2347773/history/?changeid=M:3612056480687749066)
* Repository: https://git.miksen.me/mikkel/Ray-Trace
* Gamedata: https://git.miksen.me/mikkel/Ray-Trace/src/branch/main/configs/addons/RayTrace/gamedata.json

Cell status: ✅ unique (1 match) &middot; ⚠️ ambiguous (>1) &middot; ❌ broken (0) &middot; ❔ binary not downloaded.

## Signatures

### UTIL_CreateEntityByName

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x83\xEC\x48\xC6\x44\x24\x30\x00
</pre>
</td><td>
<pre>
48 83 EC 48 C6 44 24 30 00
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x48\x8D\x05\x2A\x2A\x2A\x2A\x55\x48\x89\xFA
</pre>
</td><td>
<pre>
48 8D 05 ? ? ? ? 55 48 89 FA
</pre>
</td></tr>
</table>

### CBaseEntity_DispatchSpawn

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x10\x57\x48\x83\xEC\x30\x48\x8B\xDA\x48\x8B\xF9\x48\x85\xC9
</pre>
</td><td>
<pre>
48 89 5C 24 10 57 48 83 EC 30 48 8B DA 48 8B F9 48 85 C9
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x48\x85\xFF\x74\x2A\x55\x48\x89\xE5\x41\x55\x41\x54\x49\x89\xFC
</pre>
</td><td>
<pre>
48 85 FF 74 ? 55 48 89 E5 41 55 41 54 49 89 FC
</pre>
</td></tr>
</table>

### CEntityInstance_AcceptInput

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x2A\x48\x89\x74\x24\x2A\x57\x48\x83\xEC\x2A\x49\x8B\xF0\x48\x8B\xD9\x48\x8B\x0D
</pre>
</td><td>
<pre>
48 89 5C 24 ? 48 89 74 24 ? 57 48 83 EC ? 49 8B F0 48 8B D9 48 8B 0D
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x56\x49\x89\xFE\x41\x55\x48\x8D\x7D
</pre>
</td><td>
<pre>
55 48 89 E5 41 56 49 89 FE 41 55 48 8D 7D
</pre>
</td></tr>
</table>

### CEntitySystem_AddEntityIOEvent

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x18\x4C\x89\x4C\x24\x20\x48\x89\x4C\x24\x08\x55\x56\x57\x41\x54\x41\x55\x41\x56\x41\x57\x48\x83\xEC\x20
</pre>
</td><td>
<pre>
48 89 5C 24 18 4C 89 4C 24 20 48 89 4C 24 08 55 56 57 41 54 41 55 41 56 41 57 48 83 EC 20
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x55\x49\x89\xCD\x41\x54\x49\x89\xFC\x53\xBB
</pre>
</td><td>
<pre>
55 48 89 E5 41 55 49 89 CD 41 54 49 89 FC 53 BB
</pre>
</td></tr>
</table>
