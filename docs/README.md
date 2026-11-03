# Documentation

Last updated: November 3, 2026 at 02:00:09 GMT

* [USAGE.md](USAGE.md) - what the marks mean, what to do about a broken signature, and how to get a plugin tracked.
* [DEVELOPMENT.md](DEVELOPMENT.md) - how the pipeline works, notifications, reference validation, server setup, and the repository layout.
* [stats.md](stats.md) - signature fragility: which signatures break most often across the tracked history.

## Per-project signature pages

One page per tracked project, regenerated on every run. Each lists every signature and offset with its match state per platform, plus the byte pattern in CODE-style and IDA-style.

* [CounterStrikeSharp](CounterStrikeSharp.md) - `https://github.com/mrc4tt/CounterStrikeSharp` (fork of [roflmuffin/CounterStrikeSharp](https://github.com/roflmuffin/CounterStrikeSharp))
* [cs2-retakes-allocator](RetakesAllocator.md) - `https://github.com/mrc4tt/cs2-retakes-allocator` (fork of [yonilerner/cs2-retakes-allocator](https://github.com/yonilerner/cs2-retakes-allocator))
* [MatchZy](MatchZy.md) - `https://github.com/mrc4tt/MatchZy` (fork of [shobhit-pathak/MatchZy](https://github.com/shobhit-pathak/MatchZy))
* [WeaponPaints](WeaponPaints.md) - `https://github.com/mrc4tt/cs2-WeaponPaints` (fork of [Nereziel/cs2-WeaponPaints](https://github.com/Nereziel/cs2-WeaponPaints))
* [GameBanFix](GameBanFix.md) - `https://github.com/mrc4tt/GameBanFix` (fork of [Cruze03/GameBanFix](https://github.com/Cruze03/GameBanFix))

The project list lives in [`data/projects.json`](../data/projects.json); adding one there adds a page here on the next run.
