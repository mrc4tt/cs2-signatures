# CounterStrikeSharp

Last updated: October 23, 2026 at 03:50:02 GMT

* Manifests: [5751660862748360256](https://steamdb.info/depot/2347771/history/?changeid=M:5751660862748360256), [5491505037461703699](https://steamdb.info/depot/2347773/history/?changeid=M:5491505037461703699)
* Repository: https://github.com/mrc4tt/CounterStrikeSharp
* Gamedata: https://github.com/mrc4tt/CounterStrikeSharp/blob/main/configs/addons/counterstrikesharp/gamedata/gamedata.json

Cell status: ✅ unique (1 match) &middot; ⚠️ ambiguous (>1) &middot; ❌ broken (0) &middot; ❔ binary not downloaded.

Reference column: ✅ matches the 14192 analysis &middot; 🕓 the analysis uses a different pattern &middot; ❔ no reference for this symbol.

## Signatures

### UTIL_ClientPrintAll

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x2A\x48\x89\x6C\x24\x2A\x48\x89\x74\x24\x2A\x57\x48\x83\xEC\x2A\x8B\xE9\x49\x8B\xD9
</pre>
</td><td>
<pre>
48 89 5C 24 ? 48 89 6C 24 ? 48 89 74 24 ? 57 48 83 EC ? 8B E9 49 8B D9
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x4D\x89\xCF\x41\x56\x4D\x89\xC6\x41\x55\x49\x89\xCD\x41\x54\x49\x89\xD4\x53\x48\x8D\x5D\x2A
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 4D 89 CF 41 56 4D 89 C6 41 55 49 89 CD 41 54 49 89 D4 53 48 8D 5D ?
</pre>
</td></tr>
</table>

### ClientPrint

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x85\xC9\x0F\x84\x2A\x2A\x2A\x2A\x48\x89\x5C\x24\x2A\x48\x89\x74\x24\x2A
</pre>
</td><td>
<pre>
48 85 C9 0F 84 ? ? ? ? 48 89 5C 24 ? 48 89 74 24 ?
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x41\x56\x41\x55\x41\x54\x53\x48\x83\xEC\x2A\x4C\x89\x45\x2A\x4C\x89\x4D\x2A
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 41 56 41 55 41 54 53 48 83 EC ? 4C 89 45 ? 4C 89 4D ?
</pre>
</td></tr>
</table>

### CCSPlayerController_SwitchTeam

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x40\x53\x57\x48\x81\xEC\x2A\x2A\x2A\x2A\x48\x8B\xD9\x8B\xFA
</pre>
</td><td>
<pre>
40 53 57 48 81 EC ? ? ? ? 48 8B D9 8B FA
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
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
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x44\x88\x4C\x24\x2A\x53
</pre>
</td><td>
<pre>
44 88 4C 24 ? 53
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x8D\x87\x2A\x2A\x2A\x2A\x48\x89\xE5\x41\x57\x41\x56\x41\x89\xCE
</pre>
</td><td>
<pre>
55 48 8D 87 ? ? ? ? 48 89 E5 41 57 41 56 41 89 CE
</pre>
</td></tr>
</table>

### CCSPlayerPawnBase_PostThink

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x40\x55\x53\x56\x57\x41\x54\x48\x8B\xEC\x48\x83\xEC\x2A\x4C\x89\xAC\x24\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
40 55 53 56 57 41 54 48 8B EC 48 83 EC ? 4C 89 AC 24 ? ? ? ?
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x41\x56\x41\x55\x41\x54\x53\x48\x89\xFB\x48\x83\xEC\x2A\xE8\x2A\x2A\x2A\x2A\x80\xBB\x2A\x2A\x2A\x2A\x2A\x74\x2A\xC6\x83\x2A\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 41 56 41 55 41 54 53 48 89 FB 48 83 EC ? E8 ? ? ? ? 80 BB ? ? ? ? ? 74 ? C6 83 ? ? ? ? ?
</pre>
</td></tr>
</table>

### CGameEventManager_Init

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x40\x53\x48\x83\xEC\x2A\x48\x8B\x01\x48\x8B\xD9\xFF\x50\x2A\x48\x8B\x03
</pre>
</td><td>
<pre>
40 53 48 83 EC ? 48 8B 01 48 8B D9 FF 50 ? 48 8B 03
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x53\x48\x89\xFB\x48\x83\xEC\x2A\x48\x8B\x07\xFF\x50\x2A\x48\x8B\x03
</pre>
</td><td>
<pre>
55 48 89 E5 53 48 89 FB 48 83 EC ? 48 8B 07 FF 50 ? 48 8B 03
</pre>
</td></tr>
</table>

### GiveNamedItem

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x2A\x48\x89\x74\x24\x2A\x48\x89\x7C\x24\x2A\x44\x89\x44\x24\x2A
</pre>
</td><td>
<pre>
48 89 5C 24 ? 48 89 74 24 ? 48 89 7C 24 ? 44 89 44 24 ?
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
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
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x85\xC9\x74\x2A\x48\x8B\xD1\x48\x8B\x0D\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
48 85 C9 74 ? 48 8B D1 48 8B 0D ? ? ? ?
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\xFE\x48\x85\xFF
</pre>
</td><td>
<pre>
48 89 FE 48 85 FF
</pre>
</td></tr>
</table>

### CBaseModelEntity_SetModel

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x40\x53\x48\x83\xEC\x2A\x48\x8B\xD9\x4C\x8B\xC2\x48\x8B\x0D\x2A\x2A\x2A\x2A\x48\x8D\x54\x24\x2A\x48\x8B\x01\xFF\x50\x2A\x48\x8B\x54\x24\x2A\x48\x8B\xCB\xE8\x2A\x2A\x2A\x2A\x48\x83\xC4\x2A\x5B\xC3\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\x48\x89\x5C\x24\x2A
</pre>
</td><td>
<pre>
40 53 48 83 EC ? 48 8B D9 4C 8B C2 48 8B 0D ? ? ? ? 48 8D 54 24 ? 48 8B 01 FF 50 ? 48 8B 54 24 ? 48 8B CB E8 ? ? ? ? 48 83 C4 ? 5B C3 CC CC CC CC CC CC CC CC CC CC CC CC CC CC CC 48 89 5C 24 ?
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x53\x48\x89\xFB\x48\x83\xEC\x2A\x48\x8D\x05\x2A\x2A\x2A\x2A\x48\x8B\x38\x48\x8B\x07\xFF\x50\x2A\x48\x89\xDF\x48\x8B\x5D\x2A\xC9\x48\x89\xC6\xE9\x2A\x2A\x2A\x2A\x2A\x2A\x2A\x2A\x55
</pre>
</td><td>
<pre>
55 48 89 E5 53 48 89 FB 48 83 EC ? 48 8D 05 ? ? ? ? 48 8B 38 48 8B 07 FF 50 ? 48 89 DF 48 8B 5D ? C9 48 89 C6 E9 ? ? ? ? ? ? ? ? 55
</pre>
</td></tr>
</table>

### CCSPlayer_WeaponServices_CanUse

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x2A\x48\x89\x6C\x24\x2A\x56\x57\x41\x54\x41\x56\x41\x57\x48\x83\xEC\x2A\x48\x8B\x01\x48\x8B\xFA
</pre>
</td><td>
<pre>
48 89 5C 24 ? 48 89 6C 24 ? 56 57 41 54 41 56 41 57 48 83 EC ? 48 8B 01 48 8B FA
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x8D\x15\x2A\x2A\x2A\x2A\x48\x89\xE5\x41\x55\x41\x54\x49\x89\xF4\x53\x48\x89\xFB\x48\x83\xEC\x2A\x48\x8B\x07\x48\x8B\x80\x2A\x2A\x2A\x2A\x48\x39\xD0\x0F\x85\x2A\x2A\x2A\x2A\x80\xBF\x2A\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
55 48 8D 15 ? ? ? ? 48 89 E5 41 55 41 54 49 89 F4 53 48 89 FB 48 83 EC ? 48 8B 07 48 8B 80 ? ? ? ? 48 39 D0 0F 85 ? ? ? ? 80 BF ? ? ? ? ?
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

### GetCSWeaponDataFromKey

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x2A\x57\x48\x83\xEC\x2A\x33\xFF\x4C\x8B\xCA\x8B\xD9
</pre>
</td><td>
<pre>
48 89 5C 24 ? 57 48 83 EC ? 33 FF 4C 8B CA 8B D9
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x31\xD2\x48\x89\xE5\x41\x57\x41\x56\x41\x55\x41\x54\x41\x89\xFC
</pre>
</td><td>
<pre>
55 31 D2 48 89 E5 41 57 41 56 41 55 41 54 41 89 FC
</pre>
</td></tr>
</table>

### CCSGameRules_TerminateRound

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x8B\xC4\x4C\x89\x48\x2A\x48\x89\x48\x2A\x55\x41\x54
</pre>
</td><td>
<pre>
48 8B C4 4C 89 48 ? 48 89 48 ? 55 41 54
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x41\x56\x49\x89\xFE\x41\x55\x41\x54\x53\x48\x81\xEC\x2A\x2A\x2A\x2A\x48\x8D\x05\x2A\x2A\x2A\x2A\xF3\x0F\x11\x85\x2A\x2A\x2A\x2A\x89\xB5\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 41 56 49 89 FE 41 55 41 54 53 48 81 EC ? ? ? ? 48 8D 05 ? ? ? ? F3 0F 11 85 ? ? ? ? 89 B5 ? ? ? ?
</pre>
</td></tr>
</table>

### UTIL_CreateEntityByName

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x83\xEC\x2A\xC6\x44\x24\x2A\x2A\x4C\x8B\xC1
</pre>
</td><td>
<pre>
48 83 EC ? C6 44 24 ? ? 4C 8B C1
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
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
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x2A\x57\x48\x83\xEC\x2A\x48\x8B\xDA\x48\x8B\xF9\x48\x85\xC9\x0F\x84\x2A\x2A\x2A\x2A\x48\x85\xD2
</pre>
</td><td>
<pre>
48 89 5C 24 ? 57 48 83 EC ? 48 8B DA 48 8B F9 48 85 C9 0F 84 ? ? ? ? 48 85 D2
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
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
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x40\x53\x48\x83\xEC\x2A\x4C\x89\x4C\x24\x2A\x48\x8B\xD9\x45\x8B\xC8
</pre>
</td><td>
<pre>
40 53 48 83 EC ? 4C 89 4C 24 ? 48 8B D9 45 8B C8
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x48\xB8\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x55\x48\x89\xE5\x41\x57\x41\x56\x41\x55\x41\x54\x53\x48\x89\xFB\x48\x81\xEC\x2A\x2A\x2A\x2A\x48\x89\x07\x48\x8D\x05\x2A\x2A\x2A\x2A\x48\xC7\x47\x08\x00\x00\x00\x00
</pre>
</td><td>
<pre>
48 B8 00 00 00 00 FF FF FF FF 55 48 89 E5 41 57 41 56 41 55 41 54 53 48 89 FB 48 81 EC ? ? ? ? 48 89 07 48 8D 05 ? ? ? ? 48 C7 47 08 00 00 00 00
</pre>
</td></tr>
</table>

### CEntityInstance_AcceptInput

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x2A\x48\x89\x6C\x24\x2A\x56\x57\x41\x56\x48\x81\xEC\x2A\x2A\x2A\x2A\x4D\x8B\xF0\x48\x8B\xF1
</pre>
</td><td>
<pre>
48 89 5C 24 ? 48 89 6C 24 ? 56 57 41 56 48 81 EC ? ? ? ? 4D 8B F0 48 8B F1
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x49\x89\xFF\x41\x56\x48\x8D\xBD\x2A\x2A\x2A\x2A\x41\x55\x4C\x8D\xAD\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 49 89 FF 41 56 48 8D BD ? ? ? ? 41 55 4C 8D AD ? ? ? ?
</pre>
</td></tr>
</table>

### CEntitySystem_AddEntityIOEvent

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x2A\x48\x89\x74\x24\x2A\x57\x48\x83\xEC\x2A\x49\x8B\xF1\x48\x8B\xF9
</pre>
</td><td>
<pre>
48 89 5C 24 ? 48 89 74 24 ? 57 48 83 EC ? 49 8B F1 48 8B F9
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x55\x49\x89\xCD\x41\x54\x49\x89\xFC\x53\xBB\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
55 48 89 E5 41 55 49 89 CD 41 54 49 89 FC 53 BB ? ? ? ?
</pre>
</td></tr>
</table>

### LegacyGameEventListener

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x8B\x15\x2A\x2A\x2A\x2A\x48\x85\xD2\x74\x2A\x85\xC9
</pre>
</td><td>
<pre>
48 8B 15 ? ? ? ? 48 85 D2 74 ? 85 C9
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x48\x8B\x05\x2A\x2A\x2A\x2A\x48\x85\xC0\x74\x2A\x83\xFF\x2A\x77\x2A\x48\x63\xFF\x48\xC1\xE7\x2A\x48\x8D\x44\x38\x2A
</pre>
</td><td>
<pre>
48 8B 05 ? ? ? ? 48 85 C0 74 ? 83 FF ? 77 ? 48 63 FF 48 C1 E7 ? 48 8D 44 38 ?
</pre>
</td></tr>
</table>

### CBasePlayerPawn_RemovePlayerItem

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x85\xD2\x0F\x84\x2A\x2A\x2A\x2A\x48\x89\x5C\x24\x2A\x57\x48\x83\xEC\x2A\x48\x8B\xDA\x48\x8B\xF9\xE8\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
48 85 D2 0F 84 ? ? ? ? 48 89 5C 24 ? 57 48 83 EC ? 48 8B DA 48 8B F9 E8 ? ? ? ?
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x48\x85\xF6\x74\x2A\xE9\x2A\x2A\x2A\x2A\x66\x0F\x1F\x44\x00\x00\xC3\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\x55\x48\x89\xE5\x41\x54\x41\x89\xF4
</pre>
</td><td>
<pre>
48 85 F6 74 ? E9 ? ? ? ? 66 0F 1F 44 00 00 C3 CC CC CC CC CC CC CC CC CC CC CC CC CC CC CC 55 48 89 E5 41 54 41 89 F4
</pre>
</td></tr>
</table>

### CBaseEntity_TakeDamageOld

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x40\x55\x53\x56\x57\x41\x54\x48\x8D\x6C\x24\x2A\x48\x81\xEC\x2A\x2A\x2A\x2A\x4D\x8B\xE0
</pre>
</td><td>
<pre>
40 55 53 56 57 41 54 48 8D 6C 24 ? 48 81 EC ? ? ? ? 4D 8B E0
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
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
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x40\x57\x41\x56\x48\x83\xEC\x2A\x48\x8B\x01
</pre>
</td><td>
<pre>
40 57 41 56 48 83 EC ? 48 8B 01
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x54\x49\x89\xF4\x53\x48\x8B\x07\x48\x89\xFB\xFF\x90\x2A\x2A\x2A\x2A\x84\xC0\x75\x2A\x5B\x41\x5C\x5D\xC3\x90\x4C\x89\xE6\x48\x89\xDF\x5B\x41\x5C\x5D\xE9\x2A\x2A\x2A\x2A\x2A\x49\x8B\x40\x2A
</pre>
</td><td>
<pre>
55 48 89 E5 41 54 49 89 F4 53 48 8B 07 48 89 FB FF 90 ? ? ? ? 84 C0 75 ? 5B 41 5C 5D C3 90 4C 89 E6 48 89 DF 5B 41 5C 5D E9 ? ? ? ? ? 49 8B 40 ?
</pre>
</td></tr>
</table>

### CBaseTrigger_EndTouch

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x85\xD2\x0F\x84\x2A\x2A\x2A\x2A\x53\x55\x48\x83\xEC\x2A\x4C\x8B\x42\x10
</pre>
</td><td>
<pre>
48 85 D2 0F 84 ? ? ? ? 53 55 48 83 EC ? 4C 8B 42 10
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x48\x85\xF6\x74\x2A\xE9\x2A\x2A\x2A\x2A\x66\x0F\x1F\x44\x00\x2A\xC3\x2A\x2A\x2A\x2A\x2A\x2A\x2A\x2A\x2A\x2A\x2A\x2A\x2A\x2A\x2A\x55\x48\x89\xE5\x41\x55
</pre>
</td><td>
<pre>
48 85 F6 74 ? E9 ? ? ? ? 66 0F 1F 44 00 ? C3 ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? 55 48 89 E5 41 55
</pre>
</td></tr>
</table>

### CEntityIOOutput_FireOutputInternal

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x8B\xC4\x48\x89\x58\x2A\x48\x89\x70\x2A\x48\x89\x48\x2A\x55
</pre>
</td><td>
<pre>
48 8B C4 48 89 58 ? 48 89 70 ? 48 89 48 ? 55
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x49\x89\xFF\x41\x56\x41\x55\x41\x54\x49\x89\xD4\x53\x48\x89\xF3\x48\x81\xEC\x2A\x2A\x2A\x2A\x48\x8D\x05\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 49 89 FF 41 56 41 55 41 54 49 89 D4 53 48 89 F3 48 81 EC ? ? ? ? 48 8D 05 ? ? ? ?
</pre>
</td></tr>
</table>

### IGameSystem_InitAllSystems_pFirst

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x8B\x1D\x2A\x2A\x2A\x2A\x48\x85\xDB\x0F\x84\x2A\x2A\x2A\x2A\xBD\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
48 8B 1D ? ? ? ? 48 85 DB 0F 84 ? ? ? ? BD ? ? ? ?
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x4C\x8B\x35\x2A\x2A\x2A\x2A\x4D\x85\xF6\x75\x2A\xE9\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
4C 8B 35 ? ? ? ? 4D 85 F6 75 ? E9 ? ? ? ?
</pre>
</td></tr>
</table>

### CheckTransmit

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x8B\xC4\x4C\x89\x48\x2A\x48\x89\x50\x2A\x48\x89\x48\x2A\x55\x48\x8D\xA8\x2A\x2A\x2A\x2A
</pre>
</td><td>
<pre>
48 8B C4 4C 89 48 ? 48 89 50 ? 48 89 48 ? 55 48 8D A8 ? ? ? ?
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x49\x89\xCA\x48\x89\xE5\x41\x57\x41\x89\xD7
</pre>
</td><td>
<pre>
55 49 89 CA 48 89 E5 41 57 41 89 D7
</pre>
</td></tr>
</table>

### NetworkStateChanged

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x4C\x8B\xC2\x48\x8B\xD1\x48\x8B\x09
</pre>
</td><td>
<pre>
4C 8B C2 48 8B D1 48 8B 09
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x48\x8B\x07\x48\x85\xC0\x74\x2A\x48\x8B\x50
</pre>
</td><td>
<pre>
48 8B 07 48 85 C0 74 ? 48 8B 50
</pre>
</td></tr>
</table>

### Host_Say

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x44\x89\x4C\x24\x2A\x44\x88\x44\x24\x2A
</pre>
</td><td>
<pre>
44 89 4C 24 ? 44 88 44 24 ?
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
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
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x83\x3D\x2A\x2A\x2A\x2A\x2A\x0F\x95\xC0\xC3\x2A\x2A\x2A\x2A\xC2\x2A\x2A
</pre>
</td><td>
<pre>
48 83 3D ? ? ? ? ? 0F 95 C0 C3 ? ? ? ? C2 ? ?
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x48\x8D\x05\x2A\x2A\x2A\x2A\x48\x83\x38\x2A\x0F\x95\xC0\xC3
</pre>
</td><td>
<pre>
48 8D 05 ? ? ? ? 48 83 38 ? 0F 95 C0 C3
</pre>
</td></tr>
</table>

### CCSCustomHudLayout_SetDialogVariableString

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x2A\x48\x89\x6C\x24\x2A\x48\x89\x74\x24\x2A\x57\x48\x83\xEC\x2A\x49\x8B\xF0\x33\xED\x4C\x8D\x44\x24\x2A\x66\x89\x6C\x24\x2A\x49\x8B\xF9
</pre>
</td><td>
<pre>
48 89 5C 24 ? 48 89 6C 24 ? 48 89 74 24 ? 57 48 83 EC ? 49 8B F0 33 ED 4C 8D 44 24 ? 66 89 6C 24 ? 49 8B F9
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x55\x49\x89\xCD\x41\x54\x49\x89\xD4\x31\xD2
</pre>
</td><td>
<pre>
55 48 89 E5 41 55 49 89 CD 41 54 49 89 D4 31 D2
</pre>
</td></tr>
</table>

### CCSCustomHudLayout_SetDialogVariableStringForPlayer

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x85\xD2\x0F\x88\x2A\x2A\x2A\x2A\x53\x55\x56\x48\x83\xEC\x2A\x48\x63\xDA\x49\x8B\xE9\x49\x8B\xC0\x48\x8B\xF1\x48\x89\x7C\x24\x2A\x3B\x99\x2A\x2A\x2A\x2A\x0F\x8D\x2A\x2A\x2A\x2A\x4C\x89\x74\x24\x2A\x4C\x8D\x44\x24\x2A\x45\x33\xF6\x48\x8B\xD0\x66\x44\x89\x74\x24\x2A\xE8\x2A\x2A\x2A\x2A\x84\xC0\x74\x2A\x4C\x8D\x44\x24\x2A\x66\x44\x89\x74\x24\x2A\x48\x8B\xD5\x48\x8B\xCE\xE8\x2A\x2A\x2A\x2A\x84\xC0\x74\x2A\x0F\xB6\x86\x2A\x2A\x2A\x2A\xA8\x02\x74\x2A\xA8\x01\x75\x2A\x4C\x8D\x44\x24\x2A\x48\xC7\x44\x24\x2A\xFF\xFF\xFF\xFF\xB2\x03\x48\x8D\x8E\x2A\x2A\x2A\x2A\xE8\x2A\x2A\x2A\x2A\x4C\x8B\x4C\x24\x2A
</pre>
</td><td>
<pre>
85 D2 0F 88 ? ? ? ? 53 55 56 48 83 EC ? 48 63 DA 49 8B E9 49 8B C0 48 8B F1 48 89 7C 24 ? 3B 99 ? ? ? ? 0F 8D ? ? ? ? 4C 89 74 24 ? 4C 8D 44 24 ? 45 33 F6 48 8B D0 66 44 89 74 24 ? E8 ? ? ? ? 84 C0 74 ? 4C 8D 44 24 ? 66 44 89 74 24 ? 48 8B D5 48 8B CE E8 ? ? ? ? 84 C0 74 ? 0F B6 86 ? ? ? ? A8 02 74 ? A8 01 75 ? 4C 8D 44 24 ? 48 C7 44 24 ? FF FF FF FF B2 03 48 8D 8E ? ? ? ? E8 ? ? ? ? 4C 8B 4C 24 ?
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x56\x41\x55\x41\x54\x53\x89\xF3\x48\x83\xEC\x2A\x85\xF6\x78\x2A\x49\x89\xFD\x39\xB7\x2A\x2A\x2A\x2A\x7F\x2A\x48\x83\xC4\x2A\x5B\x41\x5C\x41\x5D\x41\x5E\x5D\xC3\x0F\x1F\x00\x48\x89\xD6\x31\xD2\x49\x89\xCE\x66\x89\x55\x2A\x48\x8D\x55\x2A\x4D\x89\xC4
</pre>
</td><td>
<pre>
55 48 89 E5 41 56 41 55 41 54 53 89 F3 48 83 EC ? 85 F6 78 ? 49 89 FD 39 B7 ? ? ? ? 7F ? 48 83 C4 ? 5B 41 5C 41 5D 41 5E 5D C3 0F 1F 00 48 89 D6 31 D2 49 89 CE 66 89 55 ? 48 8D 55 ? 4D 89 C4
</pre>
</td></tr>
</table>

### CCSCustomHudLayout_SetHasClass

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x48\x89\x5C\x24\x2A\x48\x89\x6C\x24\x2A\x48\x89\x74\x24\x2A\x57\x48\x83\xEC\x2A\x49\x8B\xF0\x33\xED\x4C\x8D\x44\x24\x2A\x66\x89\x6C\x24\x2A\x41\x8B\xF9
</pre>
</td><td>
<pre>
48 89 5C 24 ? 48 89 6C 24 ? 48 89 74 24 ? 57 48 83 EC ? 49 8B F0 33 ED 4C 8D 44 24 ? 66 89 6C 24 ? 41 8B F9
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x49\x89\xD7\x41\x56\x48\x8D\x55\x2A
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 49 89 D7 41 56 48 8D 55 ?
</pre>
</td></tr>
</table>

### CCSCustomHudLayout_SetHasClassForPlayer

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x85\xD2\x0F\x88\x2A\x2A\x2A\x2A\x53\x55\x56\x48\x83\xEC\x2A\x48\x63\xDA\x49\x8B\xE9\x49\x8B\xC0\x48\x8B\xF1\x48\x89\x7C\x24\x2A\x3B\x99\x2A\x2A\x2A\x2A\x0F\x8D\x2A\x2A\x2A\x2A\x4C\x89\x74\x24\x2A\x4C\x8D\x44\x24\x2A\x45\x33\xF6\x48\x8B\xD0\x66\x44\x89\x74\x24\x2A\xE8\x2A\x2A\x2A\x2A\x84\xC0\x74\x2A\x4C\x8D\x44\x24\x2A\x66\x44\x89\x74\x24\x2A\x48\x8B\xD5\x48\x8B\xCE\xE8\x2A\x2A\x2A\x2A\x84\xC0\x74\x2A\x0F\xB6\x86\x2A\x2A\x2A\x2A\xA8\x02\x74\x2A\xA8\x01\x75\x2A\x4C\x8D\x44\x24\x2A\x48\xC7\x44\x24\x2A\xFF\xFF\xFF\xFF\xB2\x03\x48\x8D\x8E\x2A\x2A\x2A\x2A\xE8\x2A\x2A\x2A\x2A\x44\x8B\x4C\x24\x2A
</pre>
</td><td>
<pre>
85 D2 0F 88 ? ? ? ? 53 55 56 48 83 EC ? 48 63 DA 49 8B E9 49 8B C0 48 8B F1 48 89 7C 24 ? 3B 99 ? ? ? ? 0F 8D ? ? ? ? 4C 89 74 24 ? 4C 8D 44 24 ? 45 33 F6 48 8B D0 66 44 89 74 24 ? E8 ? ? ? ? 84 C0 74 ? 4C 8D 44 24 ? 66 44 89 74 24 ? 48 8B D5 48 8B CE E8 ? ? ? ? 84 C0 74 ? 0F B6 86 ? ? ? ? A8 02 74 ? A8 01 75 ? 4C 8D 44 24 ? 48 C7 44 24 ? FF FF FF FF B2 03 48 8D 8E ? ? ? ? E8 ? ? ? ? 44 8B 4C 24 ?
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x56\x41\x55\x41\x54\x53\x89\xF3\x48\x83\xEC\x2A\x85\xF6\x78\x2A\x49\x89\xFD\x39\xB7\x2A\x2A\x2A\x2A\x7F\x2A\x48\x83\xC4\x2A\x5B\x41\x5C\x41\x5D\x41\x5E\x5D\xC3\x0F\x1F\x00\x48\x89\xD6\x31\xD2\x49\x89\xCE\x66\x89\x55\x2A\x48\x8D\x55\x2A\x45\x89\xC4
</pre>
</td><td>
<pre>
55 48 89 E5 41 56 41 55 41 54 53 89 F3 48 83 EC ? 85 F6 78 ? 49 89 FD 39 B7 ? ? ? ? 7F ? 48 83 C4 ? 5B 41 5C 41 5D 41 5E 5D C3 0F 1F 00 48 89 D6 31 D2 49 89 CE 66 89 55 ? 48 8D 55 ? 45 89 C4
</pre>
</td></tr>
</table>

### CCSPointScript_OnCustomHudClicked

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x4C\x89\x44\x24\x2A\x55\x53\x56\x41\x55\x41\x57\x48\x8B\xEC\x48\x81\xEC\x2A\x2A\x2A\x2A\x44\x8B\x15\xD3\x46\x2A\x2A
</pre>
</td><td>
<pre>
4C 89 44 24 ? 55 53 56 41 55 41 57 48 8B EC 48 81 EC ? ? ? ? 44 8B 15 D3 46 ? ?
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x57\x41\x56\x49\x89\xF6\x41\x55\x49\x89\xD5\x41\x54\x49\x89\xCC\x53\x48\x89\xFB\x48\x83\xEC\x2A\x0F\xB6\x05\x2A\x2A\x2A\x2A\x84\xC0\x0F\x84\x2A\x2A\x2A\x2A\x80\x7B\x30\x00\x75\x2A\x48\x83\xC4\x58\x5B\x41\x5C\x41\x5D\x41\x5E\x41\x5F\x5D\xC3\x0F\x1F\x80\x00\x00\x00\x00\x4C\x8B\x3D\x2A\x2A\x2A\x2A\x48\x8D\x45\xB0\x48\x89\xDF\x48\x89\xC6\x48\x89\x45\x90\x4C\x89\x7D\xB0\xE8\x2A\x2A\x2A\x2A\x84\xC0\x74\x2A\x48\x89\xDF\xE8\x2A\x2A\x2A\x2A\xE8\x2A\x2A\x2A\x2A\x48\x89\xC7\x48\x89\x45\x98\xE8\x2A\x2A\x2A\x2A\x48\x8B\x75\x98\x48\x8B\x7D\x90\xE8\x2A\x2A\x2A\x2A\x48\x89\xDF\xE8\x2A\x2A\x2A\x2A\x48\x89\xC7\x48\x89\x45\x80
</pre>
</td><td>
<pre>
55 48 89 E5 41 57 41 56 49 89 F6 41 55 49 89 D5 41 54 49 89 CC 53 48 89 FB 48 83 EC ? 0F B6 05 ? ? ? ? 84 C0 0F 84 ? ? ? ? 80 7B 30 00 75 ? 48 83 C4 58 5B 41 5C 41 5D 41 5E 41 5F 5D C3 0F 1F 80 00 00 00 00 4C 8B 3D ? ? ? ? 48 8D 45 B0 48 89 DF 48 89 C6 48 89 45 90 4C 89 7D B0 E8 ? ? ? ? 84 C0 74 ? 48 89 DF E8 ? ? ? ? E8 ? ? ? ? 48 89 C7 48 89 45 98 E8 ? ? ? ? 48 8B 75 98 48 8B 7D 90 E8 ? ? ? ? 48 89 DF E8 ? ? ? ? 48 89 C7 48 89 45 80
</pre>
</td></tr>
</table>

### CCSCustomHudLayout_SetInputCaptureEnabled

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>✅</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x85\xD2\x78\x2A\x48\x89\x5C\x24\x2A\x56
</pre>
</td><td>
<pre>
85 D2 78 ? 48 89 5C 24 ? 56
</pre>
</td></tr>
<tr><td>✅</td><td>✅</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x48\x89\xE5\x41\x55\x41\x54\x53\x48\x63\xDE\x48\x83\xEC\x2A
</pre>
</td><td>
<pre>
55 48 89 E5 41 55 41 54 53 48 63 DE 48 83 EC ?
</pre>
</td></tr>
</table>

### CBaseEntity_TakeDamage

<table>
<tr><th>Status</th><th>Ref</th><th>Platform</th><th>Library</th><th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>
<tr><td>✅</td><td>❔</td><td>Windows</td><td>server</td><td>1</td><td>
<pre>
\x40\x55\x53\x56\x57\x41\x54\x48\x8D\x6C\x24\x2A\x48\x81\xEC\x2A\x2A\x2A\x2A\x4D\x8B\xE0
</pre>
</td><td>
<pre>
40 55 53 56 57 41 54 48 8D 6C 24 ? 48 81 EC ? ? ? ? 4D 8B E0
</pre>
</td></tr>
<tr><td>✅</td><td>❔</td><td>Linux</td><td>server</td><td>1</td><td>
<pre>
\x55\x66\x0F\xEF\xC0\x48\x89\xE5\x41\x57\x41\x56\x41\x55\x49\x89\xFD\x31\xFF
</pre>
</td><td>
<pre>
55 66 0F EF C0 48 89 E5 41 57 41 56 41 55 49 89 FD 31 FF
</pre>
</td></tr>
</table>

## Offsets

A vtable slot index or a struct-member byte offset. There are no bytes to scan, so these are checked by re-deriving the integer: `reference` reads it from the analysis snapshot (both platforms), `anchored` / `structural` / `structoffset` re-derive it from the binary itself (Linux only).

<table>
<tr><th>Entry</th><th>Windows</th><th>Linux</th><th>Checked by</th></tr>
<tr><td>CCSPlayerController_ChangeTeam</td><td>✅ 105</td><td>✅ 104</td><td>reference</td></tr>
<tr><td>CCSPlayerController_Respawn</td><td>✅ 274</td><td>✅ 276</td><td>reference / anchored</td></tr>
<tr><td>CCSPlayer_ItemServices_GiveNamedItem</td><td>✅ 23</td><td>✅ 24</td><td>reference / structural</td></tr>
<tr><td>CCSPlayer_ItemServices_DropActivePlayerWeapon</td><td>✅ 26</td><td>✅ 27</td><td>anchor</td></tr>
<tr><td>CCSPlayer_ItemServices_RemoveWeapons</td><td>✅ 27</td><td>✅ 28</td><td>reference / anchored</td></tr>
<tr><td>CGameSceneNode_GetSkeletonInstance</td><td>✅ 12</td><td>✅ 14</td><td>anchor</td></tr>
<tr><td>CCSGameRules_FindPickerEntity</td><td>✅ 25</td><td>✅ 26</td><td>reference / anchored</td></tr>
<tr><td>CTakeDamageInfo_HitGroup</td><td>✅ 104</td><td>✅ 104</td><td>anchor</td></tr>
<tr><td>CBaseEntity_IsPlayerPawn</td><td>✅ 171</td><td>✅ 170</td><td>anchor</td></tr>
<tr><td>CBasePlayerPawn_CommitSuicide</td><td>✅ 387</td><td>✅ 387</td><td>anchor</td></tr>
<tr><td>CBaseEntity_Teleport</td><td>✅ 165</td><td>✅ 164</td><td>anchor</td></tr>
<tr><td>GameEntitySystem</td><td>✅ 88</td><td>✅ 80</td><td>anchor</td></tr>
<tr><td>CEntityResourceManifest_AddResource</td><td>✅ 2</td><td>✅ 0</td><td>reference</td></tr>
<tr><td>CheckTransmitPlayerSlot</td><td>✅ 576</td><td>✅ 576</td><td>anchor</td></tr>
<tr><td>SetStateChanged</td><td>✅ 28</td><td>✅ 29</td><td>reference / anchored</td></tr>
<tr><td>ISource2GameEntities::CheckTransmit</td><td>✅ 12</td><td>✅ 13</td><td>reference</td></tr>
</table>
