# CounterStrikeSharp

Last updated: August 4, 2026 at 11:35:33 GMT

* Manifests: [3132779792492138697](https://steamdb.info/depot/2347771/history/?changeid=M:3132779792492138697), [8127770850217610141](https://steamdb.info/depot/2347773/history/?changeid=M:8127770850217610141)
* Repository: https://github.com/mrc4tt/CounterStrikeSharp
* Gamedata: https://github.com/mrc4tt/CounterStrikeSharp/blob/main/configs/addons/counterstrikesharp/gamedata/gamedata.json

Cell status: ✅ unique (1 match) &middot; ⚠️ ambiguous (>1) &middot; ❌ broken (0) &middot; ❔ binary not downloaded.

## Signatures

### UTIL_ClientPrintAll

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x08\x48\x89\x6C\x24\x10\x48\x89\x74\x24\x18\x57\x48\x83\xEC\x60\x8B\xE9\x49\x8B\xD9\x48\x8D\x4C\x24\x40\x49\x8B\xF8\x48\x8B\xF2\xE8\x2A\x2A\x2A\x2A\x48\x8D\x05\x2A\x2A\x2A\x2A\x48\x8D\x4C\x24\x40\x48\x89\x44\x24\x40\xE8\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
48 89 5C 24 08 48 89 6C 24 10 48 89 74 24 18 57 48 83 EC 60 8B E9 49 8B D9 48 8D 4C 24 40 49 8B F8 48 8B F2 E8 ? ? ? ? 48 8D 05 ? ? ? ? 48 8D 4C 24 40 48 89 44 24 40 E8 ? ? ? ?
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x4D\x89\xCF\x41\x56\x4D\x89\xC6\x41\x55\x49\x89\xCD\x41\x54\x49\x89\xD4\x53\x48\x8D\x5D
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 4D 89 CF 41 56 4D 89 C6 41 55 49 89 CD 41 54 49 89 D4 53 48 8D 5D
</pre>
</td></tr>
</table>

### ClientPrint

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x08\x48\x89\x74\x24\x18\x48\x89\x7C\x24\x20\x55\x41\x56\x41\x57\x48\x8D\x6C\x24\xD1\x48\x81\xEC\xC0\x00\x00\x00\x4D\x8B\xF0\x48\x89\x4D\xAF\x8B\xDA\xC6\x45\xCB\xFF\x48\x8D\x05\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
48 89 5C 24 08 48 89 74 24 18 48 89 7C 24 20 55 41 56 41 57 48 8D 6C 24 D1 48 81 EC C0 00 00 00 4D 8B F0 48 89 4D AF 8B DA C6 45 CB FF 48 8D 05 ? ? ? ?
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x8D\x05\x2A\x2A\x2A\x2A\x48\x89\xE5\x41\x57\x4D\x89\xCF
</pre>
</td><td>
<pre>
55 48 8D 05 ? ? ? ? 48 89 E5 41 57 4D 89 CF
</pre>
</td></tr>
</table>

### CCSPlayerController_SwitchTeam

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x40\x53\x57\x48\x81\xEC\x88\x00\x00\x00\x48\x8B\xD9\x8B\xFA\x8B\xCA\xE8\x2A\x2A\x2A\x2A\x48\x85\xC0\x0F\x84\x2A\x2A\x2A\x2A\x8D\x47\xFE\x83\xF8\x01\x0F\x87\x2A\x2A\x2A\x2A\x0F\xB6\x83\x44\x03\x00\x00\x3B\xF8\x0F\x84\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
40 53 57 48 81 EC 88 00 00 00 48 8B D9 8B FA 8B CA E8 ? ? ? ? 48 85 C0 0F 84 ? ? ? ? 8D 47 FE 83 F8 01 0F 87 ? ? ? ? 0F B6 83 44 03 00 00 3B F8 0F 84 ? ? ? ?
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x54\x49\x89\xFC\x89\xF7
</pre>
</td><td>
<pre>
55 48 89 E5 41 54 49 89 FC 89 F7
</pre>
</td></tr>
</table>

### CBasePlayerController_SetPawn

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x44\x88\x4C\x24\x2A\x53\x57
</pre>
</td><td>
<pre>
44 88 4C 24 ? 53 57
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x41\x56\x41\x55\x4C\x8D\xAF\x2A\x2A\x2A\x2A\x41\x54\x41\x89\xCC
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 41 56 41 55 4C 8D AF ? ? ? ? 41 54 41 89 CC
</pre>
</td></tr>
</table>

### CCSPlayerPawnBase_PostThink

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x40\x55\x56\x41\x54\x48\x8B\xEC
</pre>
</td><td>
<pre>
40 55 56 41 54 48 8B EC
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x56\x41\x55\x41\x54\x53\x48\x89\xFB\x48\x83\xEC\x2A\xE8\x2A\x2A\x2A\x2A\x80\xBB
</pre>
</td><td>
<pre>
55 48 89 E5 41 56 41 55 41 54 53 48 89 FB 48 83 EC ? E8 ? ? ? ? 80 BB
</pre>
</td></tr>
</table>

### CGameEventManager_Init

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x40\x53\x48\x83\xEC\x2A\x48\x8B\x01\x48\x8B\xD9\xFF\x50\x2A\x48\x8B\x03
</pre>
</td><td>
<pre>
40 53 48 83 EC ? 48 8B 01 48 8B D9 FF 50 ? 48 8B 03
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x53\x48\x89\xFB\x48\x83\xEC\x08\x48\x8B\x07\xFF\x50\x2A\x48\x8B\x03
</pre>
</td><td>
<pre>
55 48 89 E5 53 48 89 FB 48 83 EC 08 48 8B 07 FF 50 ? 48 8B 03
</pre>
</td></tr>
</table>

### GiveNamedItem

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x2A\x48\x89\x74\x24\x2A\x48\x89\x7C\x24\x2A\x44\x89\x44\x24
</pre>
</td><td>
<pre>
48 89 5C 24 ? 48 89 74 24 ? 48 89 7C 24 ? 44 89 44 24
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x41\x56\x41\x55\x41\x54\x53\x48\x81\xEC\x2A\x2A\x2A\x2A\x48\x89\xBD\x2A\x2A\x2A\x2A\x89\x95\x2A\x2A\x2A\x2A\x48\x89\x8D\x2A\x2A\x2A\x2A\x44\x89\x85\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 41 56 41 55 41 54 53 48 81 EC ? ? ? ? 48 89 BD ? ? ? ? 89 95 ? ? ? ? 48 89 8D ? ? ? ? 44 89 85 ? ? ? ?
</pre>
</td></tr>
</table>

### UTIL_Remove

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x85\xC9\x74\x0F\x48\x8B\xD1\x48\x8B\x0D\x2A\x2A\x2A\x2A\xE9\x2A\x2A\x2A\x2A\xC3
</pre>
</td><td>
<pre>
48 85 C9 74 0F 48 8B D1 48 8B 0D ? ? ? ? E9 ? ? ? ? C3
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\xFE\x48\x85\xFF\x74\x2A\x48\x8D\x05\x2A\x2A\x2A\x2A\x48
</pre>
</td><td>
<pre>
48 89 FE 48 85 FF 74 ? 48 8D 05 ? ? ? ? 48
</pre>
</td></tr>
</table>

### CBaseModelEntity_SetModel

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x40\x53\x48\x83\xEC\x2A\x48\x8B\xD9\x4C\x8B\xC2\x48\x8B\x0D\x2A\x2A\x2A\x2A\x48\x8D\x54\x24\x2A\x48\x8B\x01\xFF\x50\x2A\x48\x8B\x54\x24\x2A\x48\x8B\xCB\xE8\x2A\x2A\x2A\x2A\x48\x83\xC4\x2A\x5B\xC3\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\x48\x8B\x01
</pre>
</td><td>
<pre>
40 53 48 83 EC ? 48 8B D9 4C 8B C2 48 8B 0D ? ? ? ? 48 8D 54 24 ? 48 8B 01 FF 50 ? 48 8B 54 24 ? 48 8B CB E8 ? ? ? ? 48 83 C4 ? 5B C3 CC CC CC CC CC CC CC CC CC CC CC CC CC CC CC 48 8B 01
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x53\x48\x89\xFB\x48\x83\xEC\x2A\x48\x8D\x05\x2A\x2A\x2A\x2A\x48\x8B\x38\x48\x8B\x07\xFF\x50\x2A\x48\x89\xDF\x48\x8B\x5D\x2A\xC9\x48\x89\xC6\xE9\x2A\x2A\x2A\x2A\xCC\xCC\xCC\xCC\x55
</pre>
</td><td>
<pre>
55 48 89 E5 53 48 89 FB 48 83 EC ? 48 8D 05 ? ? ? ? 48 8B 38 48 8B 07 FF 50 ? 48 89 DF 48 8B 5D ? C9 48 89 C6 E9 ? ? ? ? CC CC CC CC 55
</pre>
</td></tr>
</table>

### CCSPlayer_WeaponServices_CanUse

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x2A\x48\x89\x6C\x24\x2A\x56\x57\x41\x54\x41\x56\x41\x57\x48\x83\xEC\x2A\x48\x8B\x01\x48\x8B\xFA
</pre>
</td><td>
<pre>
48 89 5C 24 ? 48 89 6C 24 ? 56 57 41 54 41 56 41 57 48 83 EC ? 48 8B 01 48 8B FA
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x8D\x15\x2A\x2A\x2A\x2A\x48\x89\xE5\x41\x55\x41\x54\x49\x89\xFC\x53\x48\x89\xF3\x48\x83\xEC\x2A\x48\x8B\x07\x48\x8B\x80
</pre>
</td><td>
<pre>
55 48 8D 15 ? ? ? ? 48 89 E5 41 55 41 54 49 89 FC 53 48 89 F3 48 83 EC ? 48 8B 07 48 8B 80
</pre>
</td></tr>
</table>

### CCSPlayer_ItemServices_CanAcquire

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x44\x89\x44\x24\x18\x48\x89\x54\x24\x10\x48\x89\x4C\x24\x08\x55\x53\x56\x57\x41\x55\x41\x56\x41\x57\x48\x8B\xEC\x48\x81\xEC\x2A\x2A\x2A\x2A\x48\x83\x79\x38\x00\x49\x8B\xD9\x45\x8B\xE8\x4C\x8B\xFA\x48\x8B\xF9\x75\x05\xE8\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
44 89 44 24 18 48 89 54 24 10 48 89 4C 24 08 55 53 56 57 41 55 41 56 41 57 48 8B EC 48 81 EC ? ? ? ? 48 83 79 38 00 49 8B D9 45 8B E8 4C 8B FA 48 8B F9 75 05 E8 ? ? ? ?
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x41\x56\x41\x55\x49\x89\xCD\x41\x54\x49\x89\xFC\x53\x48\x89\xF3\x48\x83\xEC\x78\x4C\x8B\x77\x38\x89\x55\xBC\x4D\x85\xF6\x0F\x84\x2A\x2A\x2A\x2A\x48\x8D\x45\xCC\x4D\x85\xED\x4C\x0F\x44\xE8\x41\xC7\x45\x00\x00\x00\x00\x00\x48\x85\xDB
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 41 56 41 55 49 89 CD 41 54 49 89 FC 53 48 89 F3 48 83 EC 78 4C 8B 77 38 89 55 BC 4D 85 F6 0F 84 ? ? ? ? 48 8D 45 CC 4D 85 ED 4C 0F 44 E8 41 C7 45 00 00 00 00 00 48 85 DB
</pre>
</td></tr>
</table>

### GetCSWeaponDataFromKey

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x08\x57\x48\x83\xEC\x20\x33\xFF\x4C\x8B\xCA\x8B\xD9\x8B\xC7\x48\x85\xD2\x74\x22\x38\x02\x74\x1E\x48\xC7\xC2\xFF\xFF\xFF\xFF\x48\xFF\xC2\x41\x38\x04\x11\x75\xF7\x41\xB8\x26\x59\x41\x31\x49\x8B\xC9\xE8\x2A\x2A\x2A\x2A\x89\x44\x24\x38\x85\xC0
</pre>
</td><td>
<pre>
48 89 5C 24 08 57 48 83 EC 20 33 FF 4C 8B CA 8B D9 8B C7 48 85 D2 74 22 38 02 74 1E 48 C7 C2 FF FF FF FF 48 FF C2 41 38 04 11 75 F7 41 B8 26 59 41 31 49 8B C9 E8 ? ? ? ? 89 44 24 38 85 C0
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x48\x85\xF6\x0F\x84\x2A\x2A\x2A\x2A\x55\x48\x89\xE5\x41\x57\x41\x56\x41\x55\x49\x89\xF5\x41\x54\x53\x48\x81\xEC\x2A\x2A\x2A\x2A\x80\x3E\x2A\x75\x2A\x31\xC0\x48\x81\xC4\x2A\x2A\x2A\x2A\x5B\x41\x5C\x41\x5D\x41\x5E\x41\x5F\x5D\xC3\x0F\x1F\x80\x2A\x2A\x2A\x2A\x4C\x8D\xA5\x2A\x2A\x2A\x2A\x89\xFB
</pre>
</td><td>
<pre>
48 85 F6 0F 84 ? ? ? ? 55 48 89 E5 41 57 41 56 41 55 49 89 F5 41 54 53 48 81 EC ? ? ? ? 80 3E ? 75 ? 31 C0 48 81 C4 ? ? ? ? 5B 41 5C 41 5D 41 5E 41 5F 5D C3 0F 1F 80 ? ? ? ? 4C 8D A5 ? ? ? ? 89 FB
</pre>
</td></tr>
</table>

### CCSGameRules_TerminateRound

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x8B\xC4\x4C\x89\x48\x2A\x48\x89\x48\x2A\x55\x41\x54
</pre>
</td><td>
<pre>
48 8B C4 4C 89 48 ? 48 89 48 ? 55 41 54
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x41\x89\xF7\x41\x56\x48\x8D\x35
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 41 89 F7 41 56 48 8D 35
</pre>
</td></tr>
</table>

### UTIL_CreateEntityByName

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x83\xEC\x48\xC6\x44\x24\x30\x00\x4C\x8B\xC1\x48\x8B\x0D\x2A\x2A\x2A\x2A\x45\x33\xC9\xC7\x44\x24\x28\xFF\xFF\xFF\xFF\x89\x54\x24\x20\xBA\xFF\xFF\xFF\xFF\xE8\x2A\x2A\x2A\x2A\x48\x83\xC4\x48\xC3
</pre>
</td><td>
<pre>
48 83 EC 48 C6 44 24 30 00 4C 8B C1 48 8B 0D ? ? ? ? 45 33 C9 C7 44 24 28 FF FF FF FF 89 54 24 20 BA FF FF FF FF E8 ? ? ? ? 48 83 C4 48 C3
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
\x48\x89\x5C\x24\x10\x57\x48\x83\xEC\x30\x48\x8B\xDA\x48\x8B\xF9\x48\x85\xC9\x0F\x84\x2A\x2A\x2A\x2A\x48\x85\xD2\x75\x2A\xB9\x38\x00\x00\x00\x48\x89\x74\x24\x40\xE8\x2A\x2A\x2A\x2A\x48\x8B\xD8\x48\x85\xC0\x74\x2A\x45\x33\xC0\x33\xD2\x48\x8B\xC8\xE8
</pre>
</td><td>
<pre>
48 89 5C 24 10 57 48 83 EC 30 48 8B DA 48 8B F9 48 85 C9 0F 84 ? ? ? ? 48 85 D2 75 ? B9 38 00 00 00 48 89 74 24 40 E8 ? ? ? ? 48 8B D8 48 85 C0 74 ? 45 33 C0 33 D2 48 8B C8 E8
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

### CBaseEntity_EmitSoundFilter

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x74\x24\x18\x57\x41\x56\x41\x57\x48\x83\xEC\x40\xBE\xFF\xFF\xFF\xFF\x4C\x8B\xFA\x48\x8B\xF9\x89\x74\x24\x78\x8B\xD6\x48\x8D\x0D\x2A\x2A\x2A\x2A\x4D\x8B\xF0\xE8\x2A\x2A\x2A\x2A\x48\x85\xC0\x75\x0B\x48\x8B\x05\x2A\x2A\x2A\x2A\x48\x8B\x40\x08\x80\x38
</pre>
</td><td>
<pre>
48 89 74 24 18 57 41 56 41 57 48 83 EC 40 BE FF FF FF FF 4C 8B FA 48 8B F9 89 74 24 78 8B D6 48 8D 0D ? ? ? ? 4D 8B F0 E8 ? ? ? ? 48 85 C0 75 0B 48 8B 05 ? ? ? ? 48 8B 40 08 80 38
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x53\x48\x89\xFB\x48\x83\xEC\x08\xE8\x2A\x2A\x2A\x2A\x48\x89\xD8\x48\x8B\x5D\xF8\xC9\xC3\xCC\xCC\xCC\xCC\xCC\xCC\x48\xB8
</pre>
</td><td>
<pre>
55 48 89 E5 53 48 89 FB 48 83 EC 08 E8 ? ? ? ? 48 89 D8 48 8B 5D F8 C9 C3 CC CC CC CC CC CC 48 B8
</pre>
</td></tr>
</table>

### CEntityInstance_AcceptInput

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x2A\x48\x89\x74\x24\x2A\x57\x48\x83\xEC\x2A\x49\x8B\xF0\x48\x8B\xD9\x48\x8B\x0D\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
48 89 5C 24 ? 48 89 74 24 ? 57 48 83 EC ? 49 8B F0 48 8B D9 48 8B 0D ? ? ? ?
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
\x48\x89\x5C\x24\x18\x4C\x89\x4C\x24\x20\x48\x89\x4C\x24\x08\x55\x56\x57\x41\x54\x41\x55\x41\x56\x41\x57\x48\x83\xEC\x20\x49\x8B\xF9\x4C\x8B\xC9\x41\xBD\xFF\x7F\x00\x00\x48\x85\xD2\x74\x2A\x48\x8B\x42\x10\x48\x85\xC0\x74\x2A\x8B\x50\x10
</pre>
</td><td>
<pre>
48 89 5C 24 18 4C 89 4C 24 20 48 89 4C 24 08 55 56 57 41 54 41 55 41 56 41 57 48 83 EC 20 49 8B F9 4C 8B C9 41 BD FF 7F 00 00 48 85 D2 74 ? 48 8B 42 10 48 85 C0 74 ? 8B 50 10
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

### LegacyGameEventListener

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x8B\x15\x2A\x2A\x2A\x2A\x48\x85\xD2\x74\x2A\x85\xC9
</pre>
</td><td>
<pre>
48 8B 15 ? ? ? ? 48 85 D2 74 ? 85 C9
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x48\x8B\x05\x2A\x2A\x2A\x2A\x48\x85\xC0\x74\x2A\x83\xFF\x3F\x77\x2A\x48\x63\xFF\x48\xC1\xE7\x04\x48\x8D\x44\x38
</pre>
</td><td>
<pre>
48 8B 05 ? ? ? ? 48 85 C0 74 ? 83 FF 3F 77 ? 48 63 FF 48 C1 E7 04 48 8D 44 38
</pre>
</td></tr>
</table>

### CBasePlayerPawn_RemovePlayerItem

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x85\xD2\x0F\x84\x2A\x2A\x2A\x2A\x48\x89\x5C\x24\x08\x57\x48\x83\xEC\x30\x48\x8B\xDA\x48\x8B\xF9\xE8\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
48 85 D2 0F 84 ? ? ? ? 48 89 5C 24 08 57 48 83 EC 30 48 8B DA 48 8B F9 E8 ? ? ? ?
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x54\x49\x89\xFC\x53\x48\x89\xF3\xE8\x2A\x2A\x2A\x2A\x48\x39\xC3\x74\x2A\x4C\x89\xE7\xE8\x2A\x2A\x2A\x2A\x48\x39\xC3\x74\x2A\x4C\x89\xE7\x48\x89\xDE\xE8\x2A\x2A\x2A\x2A\x48\x89\xDF\x5B\x41\x5C\x5D\xE9\x2A\x2A\x2A\x2A\x0F\x1F\x44\x00\x00
</pre>
</td><td>
<pre>
55 48 89 E5 41 54 49 89 FC 53 48 89 F3 E8 ? ? ? ? 48 39 C3 74 ? 4C 89 E7 E8 ? ? ? ? 48 39 C3 74 ? 4C 89 E7 48 89 DE E8 ? ? ? ? 48 89 DF 5B 41 5C 5D E9 ? ? ? ? 0F 1F 44 00 00
</pre>
</td></tr>
</table>

### CBaseEntity_TakeDamageOld

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x40\x55\x53\x56\x57\x41\x54\x48\x8D\x6C\x24\x2A\x48\x81\xEC\x2A\x2A\x2A\x2A\x4D\x8B\xE0
</pre>
</td><td>
<pre>
40 55 53 56 57 41 54 48 8D 6C 24 ? 48 81 EC ? ? ? ? 4D 8B E0
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x66\x0F\xEF\xC0\x48\x89\xE5\x41\x57\x41\x56\x41\x55\x49\x89\xFD\x31\xFF
</pre>
</td><td>
<pre>
55 66 0F EF C0 48 89 E5 41 57 41 56 41 55 49 89 FD 31 FF
</pre>
</td></tr>
</table>

### CBaseTrigger_StartTouch

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x40\x57\x41\x56\x48\x83\xEC\x28\x48\x8B\x01\x4C\x8B\xF2\x48\x8B\xF9\xFF\x90\x2A\x2A\x00\x00\x84\xC0\x0F\x84\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
40 57 41 56 48 83 EC 28 48 8B 01 4C 8B F2 48 8B F9 FF 90 ? ? 00 00 84 C0 0F 84 ? ? ? ?
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x56\x41\x55\x49\x89\xF5\x41\x54\x53\x48\x89\xFB\x48\x83\xEC\x2A\x48\x8B\x07\xFF\x90\x2A\x2A\x2A\x2A\x84\xC0
</pre>
</td><td>
<pre>
55 48 89 E5 41 56 41 55 49 89 F5 41 54 53 48 89 FB 48 83 EC ? 48 8B 07 FF 90 ? ? ? ? 84 C0
</pre>
</td></tr>
</table>

### CBaseTrigger_EndTouch

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x85\xD2\x0F\x84\x2A\x2A\x2A\x2A\x53\x41\x57\x48\x83\xEC\x2A\x4C\x8B\x42
</pre>
</td><td>
<pre>
48 85 D2 0F 84 ? ? ? ? 53 41 57 48 83 EC ? 4C 8B 42
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\xBA\xFF\xFF\xFF\xFF\x48\x89\xE5\x41\x57\x41\x56\x41\x55\x49\x89\xF5\x41
</pre>
</td><td>
<pre>
55 BA FF FF FF FF 48 89 E5 41 57 41 56 41 55 49 89 F5 41
</pre>
</td></tr>
</table>

### CEntityIOOutput_FireOutputInternal

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x4C\x89\x4C\x24\x2A\x48\x89\x4C\x24\x2A\x53\x56\x57\x41\x55\x41\x56\x41\x57\x48\x81\xEC\x2A\x2A\x2A\x2A\x48\x8B\x05\x2A\x2A\x2A\x2A\x4D\x8B\xF0
</pre>
</td><td>
<pre>
4C 89 4C 24 ? 48 89 4C 24 ? 53 56 57 41 55 41 56 41 57 48 81 EC ? ? ? ? 48 8B 05 ? ? ? ? 4D 8B F0
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x49\x89\xFF\x41\x56\x41\x55\x41\x54\x49\x89\xD4\x53\x48\x89\xF3\x48\x83\xEC\x2A\x48\x8D\x05
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 49 89 FF 41 56 41 55 41 54 49 89 D4 53 48 89 F3 48 83 EC ? 48 8D 05
</pre>
</td></tr>
</table>

### IGameSystem_InitAllSystems_pFirst

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x8B\x1D\x2A\x2A\x2A\x2A\x48\x85\xDB\x0F\x84\x2A\x2A\x2A\x2A\xBD
</pre>
</td><td>
<pre>
48 8B 1D ? ? ? ? 48 85 DB 0F 84 ? ? ? ? BD
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x4C\x8B\x35\x2A\x2A\x2A\x2A\x4D\x85\xF6\x75\x2A\xE9
</pre>
</td><td>
<pre>
4C 8B 35 ? ? ? ? 4D 85 F6 75 ? E9
</pre>
</td></tr>
</table>

### CheckTransmit

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x8B\xC4\x4C\x89\x48\x2A\x48\x89\x50\x2A\x48\x89\x48\x2A\x55\x48\x8D\xA8\x2A\x2A\x2A\x2A\x48\x81\xEC\x2A\x2A\x2A\x2A\x48\x89\x58\x2A\x48\x89\x70\x2A
</pre>
</td><td>
<pre>
48 8B C4 4C 89 48 ? 48 89 50 ? 48 89 48 ? 55 48 8D A8 ? ? ? ? 48 81 EC ? ? ? ? 48 89 58 ? 48 89 70 ?
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x49\x89\xFF\x41\x56\x48\x8D\x3D\x2A\x2A\x2A\x2A\x41\x55\x4C\x63\xEA
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 49 89 FF 41 56 48 8D 3D ? ? ? ? 41 55 4C 63 EA
</pre>
</td></tr>
</table>

### NetworkStateChanged

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x08\x48\x89\x6C\x24\x10\x48\x89\x74\x24\x18\x57\x48\x83\xEC\x20\x48\x8B\x42\x10\x48\x8D\x35\x2A\x2A\x2A\x2A\x48\x8B\xEA\x48\x8B\xD9\x48\x8B\xFE\x48\x8D\x15\x2A\x2A\x2A\x2A\x4C\x8B\x40\x20\x4D\x85\xC0\x49\x0F\x45\xF8
</pre>
</td><td>
<pre>
48 89 5C 24 08 48 89 6C 24 10 48 89 74 24 18 57 48 83 EC 20 48 8B 42 10 48 8D 35 ? ? ? ? 48 8B EA 48 8B D9 48 8B FE 48 8D 15 ? ? ? ? 4C 8B 40 20 4D 85 C0 49 0F 45 F8
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x55\x41\x54\x53\x48\x89\xFB\x48\x83\xEC\x2A\x0F\xB6\x7E
</pre>
</td><td>
<pre>
55 48 89 E5 41 55 41 54 53 48 89 FB 48 83 EC ? 0F B6 7E
</pre>
</td></tr>
</table>

### Host_Say

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x44\x89\x4C\x24\x20\x44\x88\x44\x24\x18\x55\x53\x56\x57\x41\x54\x41\x56\x48\x8D\xAC\x24\x78\xFE\xFF\xFF\x48\x81\xEC\x88\x02\x00\x00\x8B\x82\x38\x04\x00\x00\x4C\x8D\x35\x2A\x2A\x2A\x2A\x41\x0F\xB6\xF0\x48\x8B\xDA\x4C\x8B\xE1\x85\xC0
</pre>
</td><td>
<pre>
44 89 4C 24 20 44 88 44 24 18 55 53 56 57 41 54 41 56 48 8D AC 24 78 FE FF FF 48 81 EC 88 02 00 00 8B 82 38 04 00 00 4C 8D 35 ? ? ? ? 41 0F B6 F0 48 8B DA 4C 8B E1 85 C0
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x49\x89\xF7\x41\x56\x41\x55\x41\x89\xD5
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 49 89 F7 41 56 41 55 41 89 D5
</pre>
</td></tr>
</table>

### CCSNavArea_IsValidNavMesh

<table>
<tr><th>Status</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x83\x3D\x2A\x2A\x2A\x2A\x2A\x0F\x95\xC0\xC3\xCC\xCC\xCC\xCC\xC2
</pre>
</td><td>
<pre>
48 83 3D ? ? ? ? ? 0F 95 C0 C3 CC CC CC CC C2
</pre>
</td></tr>
<tr><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x48\x8D\x05\x2A\x2A\x2A\x2A\x48\x83\x38\x2A\x0F\x95\xC0\xC3
</pre>
</td><td>
<pre>
48 8D 05 ? ? ? ? 48 83 38 ? 0F 95 C0 C3
</pre>
</td></tr>
</table>
