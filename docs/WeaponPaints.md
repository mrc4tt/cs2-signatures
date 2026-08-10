# WeaponPaints

Last updated: August 10, 2026 at 23:50:01 GMT

* Manifests: [5408352382264162408](https://steamdb.info/depot/2347771/history/?changeid=M:5408352382264162408), [4426952802600100986](https://steamdb.info/depot/2347773/history/?changeid=M:4426952802600100986)
* Repository: https://git.miksen.me/mikkel/weaponpaints
* Gamedata: https://git.miksen.me/mikkel/weaponpaints/src/branch/main/gamedata/weaponpaints.json

Cell status: ✅ unique (1 match) &middot; ⚠️ ambiguous (>1) &middot; ❌ broken (0) &middot; ❔ binary not downloaded.

## Signatures

### CAttributeList_SetOrAddAttributeValueByName

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x40\x53\x55\x41\x56\x48\x81\xEC\x2A\x2A\x2A\x2A\x0F\x29\x74\x24
</pre>
</td><td>
<pre>
40 53 55 41 56 48 81 EC ? ? ? ? 0F 29 74 24
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x41\x56\x49\x89\xFE\x41\x55\x41\x54\x53\x48\x89\xF3\x48\x83\xEC\x2A\xF3\x0F\x11\x85\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 41 56 49 89 FE 41 55 41 54 53 48 89 F3 48 83 EC ? F3 0F 11 85 ? ? ? ?
</pre>
</td></tr>
</table>

### UpdateItemView

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x54\x24\x2A\x48\x89\x4C\x24\x2A\x53\x57\x48\x81\xEC
</pre>
</td><td>
<pre>
48 89 54 24 ? 48 89 4C 24 ? 53 57 48 81 EC
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x49\x89\xF0\x48\x89\xE5\x41\x57\x41\x56\x49\x89\xFE\x41\x55\x41\x54\x53\x48\x81\xEC\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
55 49 89 F0 48 89 E5 41 57 41 56 49 89 FE 41 55 41 54 53 48 81 EC ? ? ? ?
</pre>
</td></tr>
</table>

### CCSPlayerInventory::GetItemInLoadout

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x8B\xC4\x56\x48\x83\xEC\x2A\x49\x63\xF0
</pre>
</td><td>
<pre>
48 8B C4 56 48 83 EC ? 49 63 F0
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x41\x56\x41\x55\x41\x54\x53\x48\x83\xEC\x18\x83\xFA\x38
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 41 56 41 55 41 54 53 48 83 EC 18 83 FA 38
</pre>
</td></tr>
</table>

### CEconItemView::CEconItemView

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x2A\x48\x89\x6C\x24\x2A\x48\x89\x74\x24\x2A\x57\x41\x54\x41\x55\x41\x56\x41\x57\x48\x83\xEC\x2A\x48\x8B\xF9\x48\x8D\x05
</pre>
</td><td>
<pre>
48 89 5C 24 ? 48 89 6C 24 ? 48 89 74 24 ? 57 41 54 41 55 41 56 41 57 48 83 EC ? 48 8B F9 48 8D 05
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x8D\x05\x2A\x2A\x2A\x2A\x66\x0F\xEF\xC0\x48\x89\xE5\x41\x57\x45\x31\xFF
</pre>
</td><td>
<pre>
55 48 8D 05 ? ? ? ? 66 0F EF C0 48 89 E5 41 57 45 31 FF
</pre>
</td></tr>
</table>

### CEconItemView::operator=

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x2A\x48\x89\x6C\x24\x2A\x48\x89\x74\x24\x2A\x48\x89\x7C\x24\x2A\x41\x56\x48\x83\xEC\x2A\x48\x8B\xF9\x48\x8B\xF2
</pre>
</td><td>
<pre>
48 89 5C 24 ? 48 89 6C 24 ? 48 89 74 24 ? 48 89 7C 24 ? 41 56 48 83 EC ? 48 8B F9 48 8B F2
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x41\x56\x41\x55\x41\x54\x49\x89\xF4\x53\x48\x89\xFB\x48\x83\xEC\x58\x48\x8B\x7F\x60
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 41 56 41 55 41 54 49 89 F4 53 48 89 FB 48 83 EC 58 48 8B 7F 60
</pre>
</td></tr>
</table>

### CCSPlayerInventory::SendInventoryUpdateEvent

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x83\x79\x2A\x2A\x0F\x10\x49
</pre>
</td><td>
<pre>
83 79 ? ? 0F 10 49
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x31\xC0\x83\x7F\x18\x01\x75\x2A
</pre>
</td><td>
<pre>
31 C0 83 7F 18 01 75 ?
</pre>
</td></tr>
</table>

### CCSPlayer_ItemServices::SetWearables

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x40\x55\x41\x56\x48\x83\xEC\x2A\x48\x83\x79
</pre>
</td><td>
<pre>
40 55 41 56 48 83 EC ? 48 83 79
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x41\x56\x41\x55\x41\x54\x49\x89\xFC\x53\x48\x83\xEC\x68\x48\x8B\x5F\x38
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 41 56 41 55 41 54 49 89 FC 53 48 83 EC 68 48 8B 5F 38
</pre>
</td></tr>
</table>

### CCSPlayerPawn::SetModelFromClass

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x2A\x56\x57\x41\x56\x48\x83\xEC\x2A\x48\x8B\xD9
</pre>
</td><td>
<pre>
48 89 5C 24 ? 56 57 41 56 48 83 EC ? 48 8B D9
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x56\x41\x55\x4C\x8D\xAF\xC8\x08\x00\x00\x41\x54\x53
</pre>
</td><td>
<pre>
55 48 89 E5 41 56 41 55 4C 8D AF C8 08 00 00 41 54 53
</pre>
</td></tr>
</table>

### CCSPlayerPawn::SetModelFromLoadout

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x40\x56\x57\x41\x54\x48\x83\xEC\x2A\x48\x8B\xF9\x45\x33\xE4
</pre>
</td><td>
<pre>
40 56 57 41 54 48 83 EC ? 48 8B F9 45 33 E4
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x41\x56\x41\x55\x41\x54\x53\x48\x89\xFB\x48\x83\xEC\x28\x8B\x8F\x90\x0E\x00\x00
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 41 56 41 55 41 54 53 48 89 FB 48 83 EC 28 8B 8F 90 0E 00 00
</pre>
</td></tr>
</table>
