# Signature fragility

Last updated: October 6, 2026 at 01:20:01 GMT

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
| CounterStrikeSharp | `CCSPointScript_OnCustomHudClicked` | linux | 2 | 0 | ok |
| CounterStrikeSharp | `CBaseModelEntity_SetModel` | linux | 1 | 0 | ok |
| CounterStrikeSharp | `CBasePlayerPawn_RemovePlayerItem` | linux | 1 | 0 | ok |
| CounterStrikeSharp | `CBaseTrigger_EndTouch` | linux | 1 | 0 | ok |
| CounterStrikeSharp | `CBaseTrigger_EndTouch` | windows | 1 | 0 | ok |
| CounterStrikeSharp | `CBaseTrigger_StartTouch` | linux | 1 | 0 | ok |
| CounterStrikeSharp | `CCSCustomHudLayout_SetHasClassForPlayer` | linux | 1 | 0 | ok |
| CounterStrikeSharp | `CCSCustomHudLayout_SetInputCaptureEnabled` | linux | 1 | 0 | ok |
| CounterStrikeSharp | `CCSCustomHudLayout_SetInputCaptureEnabled` | windows | 1 | 0 | ok |
| CounterStrikeSharp | `CCSPlayerPawnBase_PostThink` | linux | 1 | 0 | ok |
| CounterStrikeSharp | `CCSPlayerPawnBase_PostThink` | windows | 0 | 1 | ok |
| CounterStrikeSharp | `CCSPlayer_ItemServices_CanAcquire` | linux | 1 | 0 | ok |
| CounterStrikeSharp | `CCSPlayer_ItemServices_CanAcquire` | windows | 1 | 0 | ok |
| CounterStrikeSharp | `CCSPlayer_WeaponServices_CanUse` | linux | 1 | 0 | ok |

## Per project

- **CounterStrikeSharp** - 116 tracked sig/platform pairs, 35 breakage episode(s), 89 never broken, 63 snapshot(s) of history.
- **RetakesAllocator** - 6 tracked sig/platform pairs, 2 breakage episode(s), 4 never broken, 42 snapshot(s) of history.
- **MatchZy** - 16 tracked sig/platform pairs, 3 breakage episode(s), 13 never broken, 44 snapshot(s) of history.
- **WeaponPaints** - 28 tracked sig/platform pairs, 3 breakage episode(s), 25 never broken, 38 snapshot(s) of history.
