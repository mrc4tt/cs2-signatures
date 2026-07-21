#!/usr/bin/env python3
"""Apply regenerated offset values from a validation report back into gamedata.

validate_sigs.py already re-derives the correct offset when an entry goes stale
(lib_offset reports `found_linux`). This writer takes those stale->found results
and writes the new value into the gamedata JSON. Pure Python, no IDA.

Only the platform side that was validated (linux for now) is touched; the other
platform's value is preserved. `stale` entries with a null `found_linux`
(couldn't re-derive) and `review`/`no_recipe` entries are reported, never
guessed.

Usage:
  python3 scripts/apply_offsets.py --project CounterStrikeSharp [--write]
  python3 scripts/apply_offsets.py --status reports/X/status.json \
      --gamedata path/to/gamedata.json [--platform linux] [--write] [--out P]

Dry-run by default (reports what would change). --write applies with a
timestamped backup.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import projects as P  # noqa: E402


def collect_updates(status, platform):
    """From a status.json, return {name: new_offset} for stale->found entries,
    plus lists of unresolved (stale-but-no-value) and needs-attention entries."""
    updates, unresolved, attention = {}, [], []
    for r in status.get("results", []):
        if r.get("kind") != "offset":
            continue
        info = (r.get("platforms") or {}).get(platform)
        if not info:
            continue
        st = info.get("status")
        if st == "stale":
            found = info.get("found_linux")
            if isinstance(found, int):
                updates[r["name"]] = found
            else:
                unresolved.append(r["name"])
        elif st in ("review", "no_recipe"):
            attention.append((r["name"], info.get("resolve") or st,
                              info.get("reason")))
    return updates, unresolved, attention


def apply_updates(gamedata, updates, platform):
    changed = []
    for name, val in updates.items():
        ent = gamedata.get(name)
        if not ent or "offsets" not in ent:
            continue
        old = ent["offsets"].get(platform)
        if old != val:
            ent["offsets"][platform] = val
            changed.append((name, old, val))
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=None, help="derive status+gamedata paths")
    ap.add_argument("--status", default=None)
    ap.add_argument("--gamedata", default=None)
    ap.add_argument("--out", default=None, help="write target (default: in place)")
    ap.add_argument("--platform", default="linux")
    ap.add_argument("--write", action="store_true", help="apply (default: dry-run)")
    ap.add_argument("--no-backup", dest="backup", action="store_false")
    args = ap.parse_args()

    if args.project:
        proj = P.load(only=args.project)
        if not proj:
            print("unknown project: %s" % args.project)
            return 2
        proj = proj[0]
        status_path = args.status or P.status_path(proj)
        gd_path = args.gamedata or P.gamedata_path(proj)
    else:
        if not args.status or not args.gamedata:
            print("need --project OR both --status and --gamedata")
            return 2
        status_path, gd_path = args.status, args.gamedata

    if not os.path.isfile(status_path):
        print("no status file: %s" % status_path)
        return 1
    with open(status_path) as fh:
        status = json.load(fh)
    with open(gd_path) as fh:
        gamedata = json.load(fh)

    updates, unresolved, attention = collect_updates(status, args.platform)
    changed = apply_updates(gamedata, updates, args.platform)

    print("[apply_offsets] %s (%s)" % (gd_path, args.platform))
    if changed:
        for name, old, new in changed:
            print("  RE-INDEX %-44s %s -> %s" % (name, old, new))
    else:
        print("  no stale offsets to re-index")
    if unresolved:
        print("  stale but NOT re-derivable (needs regen): %s" % ", ".join(unresolved))
    if attention:
        print("  needs attention (GDT/manual):")
        for name, how, why in attention:
            print("    %-44s resolve=%s %s" % (name, how, why or ""))

    if not changed:
        return 0
    if not args.write:
        print("  (dry-run) pass --write to apply %d change(s)" % len(changed))
        return 0

    out = args.out or gd_path
    if args.backup and os.path.abspath(out) == os.path.abspath(gd_path):
        bak = gd_path + ".bak.%d" % int(os.path.getmtime(gd_path))
        with open(bak, "w") as fh:
            json.dump(gamedata, fh, indent=2)
        print("  backup -> %s" % bak)
    with open(out, "w") as fh:
        json.dump(gamedata, fh, indent=2)
        fh.write("\n")
    print("  wrote %d re-indexed offset(s) -> %s" % (len(changed), out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
