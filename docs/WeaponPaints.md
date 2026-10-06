# WeaponPaints

Last updated: October 6, 2026 at 01:20:01 GMT

* Manifests: [459013114122940128](https://steamdb.info/depot/2347771/history/?changeid=M:459013114122940128), [8082014506965878039](https://steamdb.info/depot/2347773/history/?changeid=M:8082014506965878039)
* Repository: https://git.miksen.me/mikkel/weaponpaints
* Gamedata: https://git.miksen.me/mikkel/weaponpaints/src/branch/main/gamedata/weaponpaints.json

Cell status: ✅ unique (1 match) &middot; ⚠️ ambiguous (>1) &middot; ❌ broken (0) &middot; ❔ binary not downloaded.

Reference column: ✅ matches the 14189 analysis &middot; 🕓 the analysis uses a different pattern &middot; ❔ no reference for this symbol.

## Signatures

### CAttributeList::SetOrAddAttributeValueByName

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x4C\x24\x2A\x53\x41\x55\x41\x56
</pre>
</td><td>
<pre>
48 89 4C 24 ? 53 41 55 41 56
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x41\x56\x41\x55\x49\x89\xFD\x41\x54\x53\x48\x89\xF3\x48\x83\xEC\x2A\xF3\x0F\x11\x85\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 41 56 41 55 49 89 FD 41 54 53 48 89 F3 48 83 EC ? F3 0F 11 85 ? ? ? ?
</pre>
</td></tr>
</table>

### UpdateItemView

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x54\x24\x2A\x48\x89\x4C\x24\x2A\x53\x57\x48\x81\xEC\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
48 89 54 24 ? 48 89 4C 24 ? 53 57 48 81 EC ? ? ? ?
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x49\x89\xF0\x48\x89\xE5\x41\x57\x41\x56\x49\x89\xFE
</pre>
</td><td>
<pre>
55 49 89 F0 48 89 E5 41 57 41 56 49 89 FE
</pre>
</td></tr>
</table>

### CCSPlayerInventory::GetItemInLoadout

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x8B\xC4\x56\x48\x83\xEC\x2A\x49\x63\xF0
</pre>
</td><td>
<pre>
48 8B C4 56 48 83 EC ? 49 63 F0
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x41\x56\x41\x55\x41\x54\x53\x48\x83\xEC\x2A\x83\xFA\x2A
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 41 56 41 55 41 54 53 48 83 EC ? 83 FA ?
</pre>
</td></tr>
</table>

### CEconItemView::CEconItemView

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x2A\x48\x89\x6C\x24\x2A\x48\x89\x74\x24\x2A\x57\x41\x54\x41\x55\x41\x56\x41\x57\x48\x83\xEC\x2A\x48\x8B\xF9\x48\x8D\x05\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
48 89 5C 24 ? 48 89 6C 24 ? 48 89 74 24 ? 57 41 54 41 55 41 56 41 57 48 83 EC ? 48 8B F9 48 8D 05 ? ? ? ?
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
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
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x2A\x48\x89\x6C\x24\x2A\x48\x89\x74\x24\x2A\x48\x89\x7C\x24\x2A\x41\x56\x48\x83\xEC\x2A\x48\x8B\xF9\x48\x8B\xF2
</pre>
</td><td>
<pre>
48 89 5C 24 ? 48 89 6C 24 ? 48 89 74 24 ? 48 89 7C 24 ? 41 56 48 83 EC ? 48 8B F9 48 8B F2
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x41\x56\x41\x55\x41\x54\x49\x89\xF4\x53\x48\x89\xFB\x48\x83\xEC\x2A\x48\x8B\x7F\x2A\x48\x85\xFF\x74\x2A
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 41 56 41 55 41 54 49 89 F4 53 48 89 FB 48 83 EC ? 48 8B 7F ? 48 85 FF 74 ?
</pre>
</td></tr>
</table>

### CCSPlayerInventory::SendInventoryUpdateEvent

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x83\x79\x2A\x2A\x0F\x10\x49\x2A
</pre>
</td><td>
<pre>
83 79 ? ? 0F 10 49 ?
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x31\xC0\x83\x7F\x2A\x2A\x75\x2A\x48\x8B\x47\x2A\x48\x89\xC7
</pre>
</td><td>
<pre>
31 C0 83 7F ? ? 75 ? 48 8B 47 ? 48 89 C7
</pre>
</td></tr>
</table>

### CCSPlayer_ItemServices::SetWearables

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x40\x55\x41\x56\x48\x83\xEC\x2A\x48\x83\x79\x2A\x2A
</pre>
</td><td>
<pre>
40 55 41 56 48 83 EC ? 48 83 79 ? ?
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x41\x56\x41\x55\x41\x54\x53\x48\x89\xFB\x48\x83\xEC\x2A\x4C\x8B\x67\x2A\x4D\x85\xE4\x0F\x84\x2A\x2A\x2A\x2A\x48\x89\xDF
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 41 56 41 55 41 54 53 48 89 FB 48 83 EC ? 4C 8B 67 ? 4D 85 E4 0F 84 ? ? ? ? 48 89 DF
</pre>
</td></tr>
</table>

### CCSPlayerPawn::SetModelFromClass

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x2A\x56\x57\x41\x56\x48\x83\xEC\x2A\x48\x8B\xD9
</pre>
</td><td>
<pre>
48 89 5C 24 ? 56 57 41 56 48 83 EC ? 48 8B D9
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x56\x41\x55\x4C\x8D\xAF\x2A\x2A\x2A\x2A\x41\x54\x53\x48\x89\xFB
</pre>
</td><td>
<pre>
55 48 89 E5 41 56 41 55 4C 8D AF ? ? ? ? 41 54 53 48 89 FB
</pre>
</td></tr>
</table>

### CCSPlayerPawn::SetModelFromLoadout

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x40\x56\x57\x41\x54\x48\x83\xEC\x2A\x48\x8B\xF9\x45\x33\xE4
</pre>
</td><td>
<pre>
40 56 57 41 54 48 83 EC ? 48 8B F9 45 33 E4
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x41\x56\x41\x55\x41\x54\x53\x48\x89\xFB\x48\x83\xEC\x2A\x8B\x8F\x2A\x2A\x2A\x2A\x83\xF9\x2A\x0F\x84\x2A\x2A\x2A\x2A\x48\x8B\x35\x2A\x2A\x2A\x2A\x48\x85\xF6\x0F\x84\x2A\x2A\x2A\x2A\x83\xF9\x2A\x0F\x84\x2A\x2A\x2A\x2A\x0F\xB7\x87\x2A\x2A\x00\x00\x48\x89\xC2\x48\xC1\xEA\x2A\x83\xE2\x2A\x48\x8B\x14\xD6\x48\x85\xD2\x0F\x84\x2A\x2A\x2A\x2A\x25\x2A\x2A\x2A\x2A\x48\x6B\xC0\x2A\x48\x01\xD0\x3B\x48\x2A\x0F\x85\x2A\x2A\x2A\x2A\x4C\x8B\x28
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 41 56 41 55 41 54 53 48 89 FB 48 83 EC ? 8B 8F ? ? ? ? 83 F9 ? 0F 84 ? ? ? ? 48 8B 35 ? ? ? ? 48 85 F6 0F 84 ? ? ? ? 83 F9 ? 0F 84 ? ? ? ? 0F B7 87 ? ? 00 00 48 89 C2 48 C1 EA ? 83 E2 ? 48 8B 14 D6 48 85 D2 0F 84 ? ? ? ? 25 ? ? ? ? 48 6B C0 ? 48 01 D0 3B 48 ? 0F 85 ? ? ? ? 4C 8B 28
</pre>
</td></tr>
</table>

## Offsets

A vtable slot index or a struct-member byte offset. There are no bytes to scan, so these are checked by re-deriving the integer: `reference` reads it from the analysis snapshot (both platforms), `anchored` / `structural` / `structoffset` re-derive it from the binary itself (Linux only).

<table>
<tr><th>Entry</th><th>Windows</th><th>Linux</th><th>Checked by</th></tr>
<tr><td>CCSPlayerController_InventoryServices::m_pInventory</td><td>✅ 112</td><td>✅ 112</td><td>anchor</td></tr>
<tr><td>CCSPlayerInventory::m_pSOCache</td><td>✅ 104</td><td>✅ 104</td><td>anchor</td></tr>
<tr><td>CGCClientSharedObjectCache::m_Owner</td><td>✅ 40</td><td>✅ 40</td><td>anchor</td></tr>
<tr><td>CCSPlayer_WeaponServices::DropWeapon</td><td>✅ 28</td><td>✅ 29</td><td>anchor</td></tr>
</table>
