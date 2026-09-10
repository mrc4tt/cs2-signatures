# Signature fragility

Last updated: September 10, 2026 at 16:10:01 GMT

How often each signature has gone broken or ambiguous across the tracked history (each counted transition is one episode, not one run). Signatures with no episodes are summarised, not listed.

## Most fragile

| Project | Signature | Platform | Breaks | Ambiguous | Now |
|---|---|---|---|---|---|
| CounterStrikeSharp | `CBaseModelEntity_SetModel` | windows | 2 | 0 | broken |
| CounterStrikeSharp | `CBaseModelEntity_SetModel` | linux | 1 | 0 | ok |
| CounterStrikeSharp | `CCSCustomHudLayout_SetDialogVariableStringForPlayer` | linux | 1 | 0 | broken |
| CounterStrikeSharp | `CCSCustomHudLayout_SetDialogVariableStringForPlayer` | windows | 1 | 0 | broken |
| CounterStrikeSharp | `CCSCustomHudLayout_SetHasClass` | linux | 1 | 0 | broken |
| CounterStrikeSharp | `CCSCustomHudLayout_SetHasClassForPlayer` | windows | 1 | 0 | broken |
| CounterStrikeSharp | `CCSGameRules_TerminateRound` | linux | 1 | 0 | ok |
| MatchZy | `CDecoyProjectile_Create` | linux | 1 | 0 | broken |

## Per project

- **CounterStrikeSharp** - 116 tracked sig/platform pairs, 8 breakage episode(s), 109 never broken, 35 snapshot(s) of history.
- **RetakesAllocator** - 6 tracked sig/platform pairs, 0 breakage episode(s), 6 never broken, 24 snapshot(s) of history.
- **MatchZy** - 16 tracked sig/platform pairs, 1 breakage episode(s), 15 never broken, 23 snapshot(s) of history.
- **WeaponPaints** - 28 tracked sig/platform pairs, 0 breakage episode(s), 28 never broken, 19 snapshot(s) of history.
