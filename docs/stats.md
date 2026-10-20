# Signature fragility

Last updated: October 20, 2026 at 22:40:01 GMT

How often each signature has gone broken or ambiguous across the tracked history (each counted transition is one episode, not one run). Signatures with no episodes are summarised, not listed.

## Most fragile

| Project | Signature | Platform | Breaks | Ambiguous | Now |
|---|---|---|---|---|---|
| CounterStrikeSharp | `CBaseModelEntity_SetModel` | windows | 3 | 0 | ok |
| CounterStrikeSharp | `CCSCustomHudLayout_SetDialogVariableStringForPlayer` | linux | 2 | 0 | ok |
| CounterStrikeSharp | `CCSCustomHudLayout_SetDialogVariableStringForPlayer` | windows | 2 | 0 | ok |
| CounterStrikeSharp | `CCSCustomHudLayout_SetHasClass` | linux | 2 | 0 | ok |
| CounterStrikeSharp | `CCSCustomHudLayout_SetHasClassForPlayer` | windows | 2 | 0 | ok |
| CounterStrikeSharp | `CCSGameRules_TerminateRound` | linux | 2 | 0 | ok |
| CounterStrikeSharp | `CCSPlayerPawnBase_PostThink` | linux | 2 | 0 | ok |
| CounterStrikeSharp | `CCSPointScript_OnCustomHudClicked` | linux | 2 | 0 | ok |
| WeaponPaints | `CCSPlayer_ItemServices::SetWearables` | linux | 2 | 0 | ok |
| CounterStrikeSharp | `CBaseModelEntity_SetModel` | linux | 1 | 0 | ok |
| CounterStrikeSharp | `CBasePlayerPawn_RemovePlayerItem` | linux | 1 | 0 | ok |
| CounterStrikeSharp | `CBaseTrigger_EndTouch` | linux | 1 | 0 | ok |
| CounterStrikeSharp | `CBaseTrigger_EndTouch` | windows | 1 | 0 | ok |
| CounterStrikeSharp | `CBaseTrigger_StartTouch` | linux | 1 | 0 | ok |
| CounterStrikeSharp | `CCSCustomHudLayout_SetHasClassForPlayer` | linux | 1 | 0 | ok |
| CounterStrikeSharp | `CCSCustomHudLayout_SetInputCaptureEnabled` | linux | 1 | 0 | ok |
| CounterStrikeSharp | `CCSCustomHudLayout_SetInputCaptureEnabled` | windows | 1 | 0 | ok |
| CounterStrikeSharp | `CCSPlayerPawnBase_PostThink` | windows | 0 | 1 | ok |
| CounterStrikeSharp | `CCSPlayer_ItemServices_CanAcquire` | linux | 1 | 0 | ok |
| CounterStrikeSharp | `CCSPlayer_ItemServices_CanAcquire` | windows | 1 | 0 | ok |

## Per project

- **CounterStrikeSharp** - 118 tracked sig/platform pairs, 36 breakage episode(s), 91 never broken, 71 snapshot(s) of history.
- **RetakesAllocator** - 6 tracked sig/platform pairs, 2 breakage episode(s), 4 never broken, 49 snapshot(s) of history.
- **MatchZy** - 16 tracked sig/platform pairs, 3 breakage episode(s), 13 never broken, 51 snapshot(s) of history.
- **WeaponPaints** - 28 tracked sig/platform pairs, 7 breakage episode(s), 22 never broken, 46 snapshot(s) of history.
