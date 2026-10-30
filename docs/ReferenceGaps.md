# Reference coverage gaps

Last updated: October 30, 2026 at 22:55:14 GMT

Symbols tracked by the signature tracker that the analysis cannot currently answer for.

Snapshot: `14194`. Tracker: https://github.com/mrc4tt/cs2-signatures

## Offsets with no verdict from either route (21)

Neither an anchor/recipe nor the reference can produce a value for these, so the number in the gamedata is taken on trust. A reference record - vtable index, struct member, or an anchor pattern spanning the access - would close it.

| Symbol | Platforms | Used by | Value in gamedata | Reason |
|---|---|---|---|---|
| `CBaseEntity_IsPlayerPawn` | windows | CounterStrikeSharp | windows `171` | no_reference |
| `CBaseEntity_Teleport` | windows | CounterStrikeSharp | windows `165` | no_reference |
| `CBasePlayerPawn_CommitSuicide` | windows | CounterStrikeSharp | windows `387` | no_reference |
| `CCSGameRules_FindPickerEntity` | windows | CounterStrikeSharp | windows `25` | no_reference |
| `CCSPlayerController_ChangeTeam` | windows | CounterStrikeSharp | windows `105` | no_reference |
| `CCSPlayerController_InventoryServices::m_pInventory` | windows | WeaponPaints | windows `112` | no_reference |
| `CCSPlayerController_Respawn` | windows | CounterStrikeSharp | windows `274` | no_reference |
| `CCSPlayerInventory::m_pSOCache` | windows | WeaponPaints | windows `104` | no_reference |
| `CCSPlayer_ItemServices_DropActivePlayerWeapon` | windows | CounterStrikeSharp | windows `26` | no_reference |
| `CCSPlayer_ItemServices_GiveNamedItem` | windows | CounterStrikeSharp | windows `23` | no_reference |
| `CCSPlayer_ItemServices_RemoveWeapons` | windows | CounterStrikeSharp | windows `27` | no_reference |
| `CCSPlayer_WeaponServices::DropWeapon` | windows | WeaponPaints | windows `28` | no_reference |
| `CCSPlayer_WeaponServices_SelectItem` | windows | MatchZy | windows `30` | no_reference |
| `CEntityResourceManifest_AddResource` | windows | CounterStrikeSharp | windows `2` | no_reference |
| `CGCClientSharedObjectCache::m_Owner` | windows | WeaponPaints | windows `40` | no_reference |
| `CGameSceneNode_GetSkeletonInstance` | windows | CounterStrikeSharp | windows `12` | no_reference |
| `CTakeDamageInfo_HitGroup` | windows | CounterStrikeSharp | windows `104` | no_reference |
| `CheckTransmitPlayerSlot` | windows | CounterStrikeSharp | windows `576` | no_reference |
| `GameEntitySystem` | windows | CounterStrikeSharp | windows `88` | no_reference |
| `ISource2GameEntities::CheckTransmit` | windows | CounterStrikeSharp | windows `12` | no_reference |
| `SetStateChanged` | windows | CounterStrikeSharp | windows `28` | no_reference |

## Signatures whose symbol is not in the snapshot (52)

These signatures resolve in the binaries, but the snapshot has no record under this name, so nothing can say whether the pattern is still the one the analysis uses.

| Symbol | Platforms | Used by |
|---|---|---|
| `CAttributeList::SetOrAddAttributeValueByName` | windows | WeaponPaints |
| `CBaseEntity_DispatchSpawn` | windows | CounterStrikeSharp |
| `CBaseEntity_EmitSoundFilter` | windows | CounterStrikeSharp |
| `CBaseEntity_TakeDamage` | windows | CounterStrikeSharp |
| `CBaseEntity_TakeDamageOld` | windows | CounterStrikeSharp |
| `CBaseModelEntity_SetModel` | windows | CounterStrikeSharp |
| `CBasePlayerController_HandleCommand_JoinTeam` | windows | MatchZy |
| `CBasePlayerController_SetPawn` | windows | CounterStrikeSharp |
| `CBasePlayerPawn_RemovePlayerItem` | windows | CounterStrikeSharp |
| `CBaseTrigger_EndTouch` | windows | CounterStrikeSharp |
| `CBaseTrigger_StartTouch` | windows | CounterStrikeSharp |
| `CCSCustomHudLayout_SetDialogVariableString` | windows | CounterStrikeSharp |
| `CCSCustomHudLayout_SetDialogVariableStringForPlayer` | windows | CounterStrikeSharp |
| `CCSCustomHudLayout_SetHasClass` | windows | CounterStrikeSharp |
| `CCSCustomHudLayout_SetHasClassForPlayer` | windows | CounterStrikeSharp |
| `CCSCustomHudLayout_SetInputCaptureEnabled` | windows | CounterStrikeSharp |
| `CCSGameRules_PostCleanUp` | windows | MatchZy |
| `CCSGameRules_TerminateRound` | windows | CounterStrikeSharp |
| `CCSNavArea_IsValidNavMesh` | windows | CounterStrikeSharp |
| `CCSPlayerController_SwitchTeam` | windows | CounterStrikeSharp |
| `CCSPlayerInventory::GetItemInLoadout` | windows | WeaponPaints |
| `CCSPlayerInventory::SendInventoryUpdateEvent` | windows | WeaponPaints |
| `CCSPlayerPawn::SetModelFromClass` | windows | WeaponPaints |
| `CCSPlayerPawn::SetModelFromLoadout` | windows | WeaponPaints |
| `CCSPlayerPawnBase_PostThink` | windows | CounterStrikeSharp |
| `CCSPlayer_ItemServices::SetWearables` | windows | WeaponPaints |
| `CCSPlayer_ItemServices_CanAcquire` | windows | CounterStrikeSharp, RetakesAllocator |
| `CCSPlayer_WeaponServices_CanUse` | windows | CounterStrikeSharp |
| `CCSPointScript_OnCustomHudClicked` | windows | CounterStrikeSharp |
| `CDecoyProjectile_Create` | windows | MatchZy |
| `CEconItemView::CEconItemView` | windows | WeaponPaints |
| `CEconItemView::operator=` | windows | WeaponPaints |
| `CEntityIOOutput_FireOutputInternal` | windows | CounterStrikeSharp |
| `CEntityInstance_AcceptInput` | windows | CounterStrikeSharp |
| `CEntitySystem_AddEntityIOEvent` | windows | CounterStrikeSharp |
| `CGameEventManager_Init` | windows | CounterStrikeSharp |
| `CHEGrenadeProjectile_Create` | windows | MatchZy |
| `CMolotovProjectile_Create` | windows | MatchZy |
| `CSmokeGrenadeProjectile_Create` | windows | MatchZy |
| `CheckTransmit` | windows | CounterStrikeSharp |
| `ClientPrint` | windows | CounterStrikeSharp |
| `GetCSWeaponDataFromKey` | windows | CounterStrikeSharp, RetakesAllocator |
| `GiveNamedItem` | windows | CounterStrikeSharp |
| `GiveNamedItem2` | windows | RetakesAllocator |
| `Host_Say` | windows | CounterStrikeSharp |
| `IGameSystem_InitAllSystems_pFirst` | windows | CounterStrikeSharp |
| `LegacyGameEventListener` | windows | CounterStrikeSharp |
| `NetworkStateChanged` | windows | CounterStrikeSharp |
| `UTIL_ClientPrintAll` | windows | CounterStrikeSharp |
| `UTIL_CreateEntityByName` | windows | CounterStrikeSharp |
| `UTIL_Remove` | windows | CounterStrikeSharp |
| `UpdateItemView` | windows | WeaponPaints |

Looked up under an alias, in case the analysis files these under a different name:

* `CTakeDamageInfo_HitGroup` -> `CTakeDamageInfo_HitGroupInfo`
* `CheckTransmitPlayerSlot` -> `CCheckTransmitInfo_m_nPlayerSlot`
* `GameEntitySystem` -> `CGameResourceService_m_pEntitySystem`
* `ISource2GameEntities::CheckTransmit` -> `CSource2GameEntities_CheckTransmit`
* `SetStateChanged` -> `CEntityInstance_NetworkStateChanged`
* `CBaseEntity_TakeDamage` -> `CBaseEntity_TakeDamageOld`
* `CCSPlayerPawnBase_PostThink` -> `CCSPlayerPawn_PostThink`
* `CheckTransmit` -> `CSource2GameEntities_CheckTransmit`
* `ClientPrint` -> `ClientPrintToController`
* `GiveNamedItem2` -> `CCSPlayer_ItemServices_GiveNamedItem`

Generated from the tracker's own reports; it updates itself as symbols get covered.
