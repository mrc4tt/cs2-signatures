# Signature fragility

Last updated: September 22, 2026 at 23:40:01 GMT

How often each signature has gone broken or ambiguous across the tracked history (each counted transition is one episode, not one run). Signatures with no episodes are summarised, not listed.

## Most fragile

| Project | Signature | Platform | Breaks | Ambiguous | Now |
|---|---|---|---|---|---|
| CounterStrikeSharp | `CBaseModelEntity_SetModel` | windows | 2 | 0 | ok |
| CounterStrikeSharp | `CBaseModelEntity_SetModel` | linux | 1 | 0 | ok |
| CounterStrikeSharp | `CCSCustomHudLayout_SetDialogVariableStringForPlayer` | linux | 1 | 0 | ok |
| CounterStrikeSharp | `CCSCustomHudLayout_SetDialogVariableStringForPlayer` | windows | 1 | 0 | ok |
| CounterStrikeSharp | `CCSCustomHudLayout_SetHasClass` | linux | 1 | 0 | ok |
| CounterStrikeSharp | `CCSCustomHudLayout_SetHasClassForPlayer` | windows | 1 | 0 | ok |
| CounterStrikeSharp | `CCSGameRules_TerminateRound` | linux | 1 | 0 | ok |
| MatchZy | `CDecoyProjectile_Create` | linux | 1 | 0 | ok |

## Per project

- **CounterStrikeSharp** - 116 tracked sig/platform pairs, 8 breakage episode(s), 109 never broken, 42 snapshot(s) of history.
- **RetakesAllocator** - 6 tracked sig/platform pairs, 0 breakage episode(s), 6 never broken, 25 snapshot(s) of history.
- **MatchZy** - 16 tracked sig/platform pairs, 1 breakage episode(s), 15 never broken, 25 snapshot(s) of history.
- **WeaponPaints** - 28 tracked sig/platform pairs, 0 breakage episode(s), 28 never broken, 21 snapshot(s) of history.
