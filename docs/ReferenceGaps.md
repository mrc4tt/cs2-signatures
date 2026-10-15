# Reference coverage gaps

Last updated: October 15, 2026 at 00:30:02 GMT

Symbols tracked by the signature tracker that the analysis cannot currently answer for.

## Offsets with no verdict from either route (6)

Neither an anchor/recipe nor the reference can produce a value for these, so the number in the gamedata is taken on trust. A reference record - vtable index, struct member, or an anchor pattern spanning the access - would close it.

| Symbol | Platforms | Used by | Value in gamedata | Reason |
|---|---|---|---|---|
| `CCSPlayerController_ChangeTeam` | linux | CounterStrikeSharp | linux `104` | target-sig-none |
| `CCSPlayer_WeaponServices_SelectItem` | linux | MatchZy | linux `31` | - |
| `CEntityResourceManifest_AddResource` | linux | CounterStrikeSharp | linux `0` | no-vtable |
| `CTakeDamageInfo_HitGroup` | linux | CounterStrikeSharp | linux `104` | offset_sig-missing |
| `GameEntitySystem` | linux | CounterStrikeSharp | linux `80` | offset_sig-missing |
| `ISource2GameEntities::CheckTransmit` | linux | CounterStrikeSharp | linux `13` | target-sig-none |

Looked up under an alias, in case the analysis files these under a different name:

* `CTakeDamageInfo_HitGroup` -> `CTakeDamageInfo_HitGroupInfo`
* `GameEntitySystem` -> `CGameResourceService_m_pEntitySystem`
* `ISource2GameEntities::CheckTransmit` -> `CSource2GameEntities_CheckTransmit`

Generated from the tracker's own reports; it updates itself as symbols get covered.
