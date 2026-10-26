# Using the tracker

This is the guide the [README](../README.md) dashboard links to: what the marks
mean, what to do when one goes red, and how to get your own plugin tracked. For
setup, cron and pipeline internals see [DEVELOPMENT.md](DEVELOPMENT.md).

## Reading the results

| Mark | Meaning | What to do |
|---|---|---|
| ✅ | The signature matches exactly one place in the binary. | Nothing. |
| ⚠️ | It matches more than once - ambiguous. | Treat as unreliable; the plugin may hook the wrong function. |
| ❌ | It matches nothing - broken. | The plugin needs a regenerated signature before it will work. |
| 🕓 | It still resolves, but the upstream analysis now uses a different pattern. | Advisory only. |

Each project's page - linked from the dashboard - lists every signature with its
byte pattern in both CODE-style (`\x48\x89...`) and IDA-style (`48 89 ...`), so a
broken entry can be compared against your own dump. Historic fragility - which
signatures break update after update - is in [stats.md](stats.md).

## If you run a CS2 server

1. **Before you update**, or right after a patch lands, check the row for the
   plugins you run. All green means their signatures still resolve against the
   binaries Valve just shipped.
2. **A red mark is not a crash report** - it means one function the plugin hooks
   can no longer be found. In practice the plugin loads but that feature
   misbehaves or the server crashes when the code path is hit.
3. **What to do:** wait for the plugin author's update.
4. **The binaries used for a check** are published as releases, tagged by CS2
   version, if you want to reproduce a result yourself.

## Notifications

A run that changes a result can announce itself:

* **Discord** - one embed per run, delta-first: the verdict, what changed since
  the previous report, per-project health, and the broken entries in full.
  Healthy signatures are counted, not listed.
* **GitHub issue** - opened on breakage, closed when the signatures pass again.

Runs that change nothing stay silent. See
[DEVELOPMENT.md](DEVELOPMENT.md#notifications) for the layout and the
environment variables.

## Track your own plugin

Adding a plugin is a JSON append - no code change. Add an entry to
[`data/projects.json`](../data/projects.json):

```json
{
  "id": "MyPlugin",
  "name": "My Plugin",
  "repo": "owner/my-plugin",
  "branch": "main",
  "path": "gamedata/myplugin.json",
  "private": false
}
```

* `id` names the report files (`reports/MyPlugin/`, `docs/MyPlugin.md`).
* `path` points at a CounterStrikeSharp-format `gamedata.json` in that repo.
* `host` is optional and defaults to `github.com`; a Forgejo/Gitea host works
  too. Private repos need a token in `.env`.

Then validate just that project:

```bash
python3 scripts/fetch_gamedata.py --project MyPlugin
python3 scripts/validate_sigs.py --project MyPlugin \
  --linux bin_linux/game/csgo/bin/linuxsteamrt64/libserver.so \
  --windows bin_win/game/csgo/bin/win64/server.dll
```

<details><summary>&#9660; How it works</summary>

1. **Detect an update** by comparing per-depot manifest IDs against the last
   seen ones - no download unless something actually changed.
2. **Download only the binaries that matter** (server + engine2, Linux and
   Windows) through DepotDownloader. Megabytes, not a full game install.
3. **Scan** each signature against the binary's executable sections and count
   matches: exactly one is healthy, zero is broken, more than one is ambiguous.
   Offsets are checked against a reference analysis where one is available.
4. **Report**: the [README dashboard](../README.md), the per-project pages under
   `docs/`, the status
   badges, the fragility history, and - when configured - a Discord post and an
   issue.

The whole pipeline is Python 3 standard library plus DepotDownloader, so it runs
on a bare server with no package installs.

</details>
