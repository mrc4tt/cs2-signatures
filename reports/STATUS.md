# CS2 Signature Tracker

Auto-validated signatures from [mrc4tt/CounterStrikeSharp](https://github.com/mrc4tt/CounterStrikeSharp/blob/main/configs/addons/counterstrikesharp/gamedata/gamedata.json).

- **Updated:** 2026-07-02
- **Manifest:** `unknown`

| status | count |
|---|---|
| :white_check_mark: ok | 0 |
| :warning: ambiguous | 0 |
| :x: broken | 0 |
| :grey_question: no binary | 60 |
| :arrows_counterclockwise: offset-only | 18 |

Cell value = match count. `1` = unique+healthy, `0` = :x: gone, `>1` = :warning: not unique.

| entry | linux | windows |
|---|---|---|
| `UTIL_ClientPrintAll` | :grey_question: | :grey_question: |
| `ClientPrint` | :grey_question: | :grey_question: |
| `CCSPlayerController_SwitchTeam` | :grey_question: | :grey_question: |
| `CCSPlayerController_ChangeTeam` | :arrows_counterclockwise: offset | :arrows_counterclockwise: offset |
| `CCSPlayerController_Respawn` | :arrows_counterclockwise: offset | :arrows_counterclockwise: offset |
| `CBasePlayerController_SetPawn` | :grey_question: | :grey_question: |
| `CCSPlayerPawnBase_PostThink` | :grey_question: | :grey_question: |
| `CGameEventManager_Init` | :grey_question: | :grey_question: |
| `GiveNamedItem` | :grey_question: | :grey_question: |
| `UTIL_Remove` | :grey_question: | :grey_question: |
| `CBaseModelEntity_SetModel` | :grey_question: | :grey_question: |
| `CCSPlayer_WeaponServices_CanUse` | :grey_question: | :grey_question: |
| `CCSPlayer_WeaponServices_SelectItem` | :arrows_counterclockwise: offset | :arrows_counterclockwise: offset |
| `CCSPlayer_ItemServices_CanAcquire` | :grey_question: | :grey_question: |
| `GetCSWeaponDataFromKey` | :grey_question: | :grey_question: |
| `CCSPlayer_ItemServices_GiveNamedItem` | :arrows_counterclockwise: offset | :arrows_counterclockwise: offset |
| `CCSPlayer_ItemServices_DropActivePlayerWeapon` | :arrows_counterclockwise: offset | :arrows_counterclockwise: offset |
| `CCSPlayer_ItemServices_RemoveWeapons` | :arrows_counterclockwise: offset | :arrows_counterclockwise: offset |
| `CGameSceneNode_GetSkeletonInstance` | :arrows_counterclockwise: offset | :arrows_counterclockwise: offset |
| `CCSGameRules_TerminateRound` | :grey_question: | :grey_question: |
| `CCSGameRules_FindPickerEntity` | :arrows_counterclockwise: offset | :arrows_counterclockwise: offset |
| `CTakeDamageInfo_HitGroup` | :arrows_counterclockwise: offset | :arrows_counterclockwise: offset |
| `UTIL_CreateEntityByName` | :grey_question: | :grey_question: |
| `CBaseEntity_DispatchSpawn` | :grey_question: | :grey_question: |
| `CBaseEntity_EmitSoundFilter` | :grey_question: | :grey_question: |
| `CEntityInstance_AcceptInput` | :grey_question: | :grey_question: |
| `CBaseEntity_IsPlayerPawn` | :arrows_counterclockwise: offset | :arrows_counterclockwise: offset |
| `CEntitySystem_AddEntityIOEvent` | :grey_question: | :grey_question: |
| `LegacyGameEventListener` | :grey_question: | :grey_question: |
| `CBasePlayerPawn_CommitSuicide` | :arrows_counterclockwise: offset | :arrows_counterclockwise: offset |
| `CBasePlayerPawn_RemovePlayerItem` | :grey_question: | :grey_question: |
| `CBaseEntity_Teleport` | :arrows_counterclockwise: offset | :arrows_counterclockwise: offset |
| `CBaseEntity_TakeDamageOld` | :grey_question: | :grey_question: |
| `CBaseEntity_TakeDamage` | :grey_question: | :grey_question: |
| `CBaseTrigger_StartTouch` | :grey_question: | :grey_question: |
| `CBaseTrigger_EndTouch` | :grey_question: | :grey_question: |
| `GameEntitySystem` | :arrows_counterclockwise: offset | :arrows_counterclockwise: offset |
| `GameEventManager` | :arrows_counterclockwise: offset | :arrows_counterclockwise: offset |
| `CEntityIOOutput_FireOutputInternal` | :grey_question: | :grey_question: |
| `IGameSystem_InitAllSystems_pFirst` | :grey_question: | :grey_question: |
| `CEntityResourceManifest_AddResource` | :arrows_counterclockwise: offset | :arrows_counterclockwise: offset |
| `CheckTransmit` | :grey_question: | :grey_question: |
| `CheckTransmitPlayerSlot` | :arrows_counterclockwise: offset | :arrows_counterclockwise: offset |
| `NetworkStateChanged` | :grey_question: | :grey_question: |
| `SetStateChanged` | :arrows_counterclockwise: offset | :arrows_counterclockwise: offset |
| `ISource2GameEntities::CheckTransmit` | :arrows_counterclockwise: offset | :arrows_counterclockwise: offset |
| `Host_Say` | :grey_question: | :grey_question: |
| `CCSNavArea_IsValidNavMesh` | :grey_question: | :grey_question: |
