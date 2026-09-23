# Documentation

Last updated: September 23, 2026 at 21:20:01 GMT

* [USAGE.md](USAGE.md) - what the marks mean, what to do about a broken signature, and how to get a plugin tracked.
* [DEVELOPMENT.md](DEVELOPMENT.md) - how the pipeline works, notifications, reference validation, VPS setup, and the repository layout.
* [stats.md](stats.md) - signature fragility: which signatures break most often across the tracked history.

## Per-project signature pages

One page per tracked project, regenerated on every run. Each lists every signature and offset with its match state per platform, plus the byte pattern in CODE-style and IDA-style.

* [CounterStrikeSharp](CounterStrikeSharp.md) - `https://github.com/mrc4tt/CounterStrikeSharp`
* [cs2-retakes-allocator](RetakesAllocator.md) - `https://github.com/mrc4tt/cs2-retakes-allocator`
* [MatchZy](MatchZy.md) - `https://git.miksen.me/mikkel/matchzy`
* [WeaponPaints](WeaponPaints.md) - `https://git.miksen.me/mikkel/weaponpaints`

The project list lives in [`data/projects.json`](../data/projects.json); adding one there adds a page here on the next run.
