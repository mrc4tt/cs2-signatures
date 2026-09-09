#!/usr/bin/env python3
"""Diff two reference snapshots: what the game moved between two builds.

The other checks answer "is this offset right today". This one answers "what
changed", which is the question you want after a game update and before anything
has broken. A vtable that gained a slot shifts every index below the insertion
point, so the entries at risk are knowable before any plugin notices.

    python3 scripts/diff_symbols.py 14178b 14180
    python3 scripts/diff_symbols.py 14178b 14180 --tracked

--tracked narrows the report to symbols the projects in data/projects.json
actually use, which is usually the only part worth reading.

stdlib only. Reads the cached snapshots written by fetch_symbols.py.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_symbols as SYM  # noqa: E402
import projects as P  # noqa: E402

SYMBOL_DIR = os.path.join("data", "symbols")
PLATFORMS = ("linux", "windows")


def load(gamever):
    path = os.path.join(SYMBOL_DIR, "%s.json" % gamever)
    if not os.path.isfile(path):
        raise SystemExit("no snapshot at %s; run fetch_symbols.py first" % path)
    with open(path) as fh:
        return json.load(fh)


def index(snapshot):
    """{(key, platform): record} plus {(class, platform): slot count}."""
    records, vtables = {}, {}
    for rec in snapshot.get("records", []):
        records[(SYM.norm(rec["artifact"]), rec["platform"])] = rec
        if rec["kind"] == "vtable":
            key = SYM.norm(rec["payload"]["vtable_class"])
            vtables[(key, rec["platform"])] = rec["payload"].get("vtable_numvfunc")
    return records, vtables


def offset_of(rec):
    """The integer this record pins, or None when it pins none."""
    p = rec["payload"]
    if rec["kind"] == "virtualFunction" and "vfunc_index" in p:
        return int(p["vfunc_index"])
    if rec["kind"] == "structMember" and "offset" in p:
        return int(str(p["offset"]), 16)
    return None


def tracked_keys(aliases):
    """{normalised key: [entry names]} for everything the projects reference."""
    out = {}
    for proj in P.load():
        path = P.gamedata_path(proj)
        if not os.path.isfile(path):
            continue
        with open(path) as fh:
            gamedata = json.load(fh)
        for name in gamedata:
            key = SYM.norm(name)
            key = aliases.get(key, key)
            out.setdefault(key, []).append("%s/%s" % (proj["id"], name))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--tracked", action="store_true",
                    help="only symbols the tracked projects use")
    args = ap.parse_args()

    old_rec, old_vt = index(load(args.old))
    new_rec, new_vt = index(load(args.new))
    aliases = {SYM.norm(k): SYM.norm(v) for k, v in SYM.load_aliases().items()}
    keep = tracked_keys(aliases) if args.tracked else None

    print("%s -> %s" % (args.old, args.new))
    print()

    grown = []
    for (cls, plat), old_len in sorted(old_vt.items()):
        new_len = new_vt.get((cls, plat))
        if new_len is not None and new_len != old_len:
            grown.append((cls, plat, old_len, new_len))
    if grown:
        print("vtables that changed size (every index below an insertion moves):")
        for cls, plat, a, b in grown:
            print("  %-40s %-8s %d -> %d" % (cls, plat, a, b))
        print()

    moved, added, removed = [], [], []
    for key, rec in sorted(new_rec.items()):
        if keep is not None and key[0] not in keep:
            continue
        old = old_rec.get(key)
        if old is None:
            added.append(key)
            continue
        a, b = offset_of(old), offset_of(rec)
        if a is not None and b is not None and a != b:
            moved.append((key, a, b))
    for key in sorted(old_rec):
        if keep is not None and key[0] not in keep:
            continue
        if key not in new_rec:
            removed.append(key)

    if moved:
        print("offsets that moved:")
        for (key, plat), a, b in moved:
            who = " ".join(keep.get(key, [])) if keep else ""
            print("  %-40s %-8s %s -> %s  %s" % (key, plat, a, b, who))
        print()
    else:
        print("no offset moved%s." % (" among tracked symbols" if keep else ""))
        print()

    sig_changed = []
    for key, rec in sorted(new_rec.items()):
        if keep is not None and key[0] not in keep:
            continue
        old = old_rec.get(key)
        if not old:
            continue
        a = old["payload"].get("func_sig")
        b = rec["payload"].get("func_sig")
        if a and b and SYM.sig_relation(a, b) == "conflict":
            sig_changed.append((key, a, b))
    if sig_changed:
        print("signatures the analysis replaced:")
        for (key, plat), a, b in sig_changed:
            print("  %-40s %-8s" % (key, plat))
            print("      was: %s" % a)
            print("      now: %s" % b)
        print()

    print("summary: %d moved, %d signature(s) replaced, %d added, %d removed"
          % (len(moved), len(sig_changed), len(added), len(removed)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
