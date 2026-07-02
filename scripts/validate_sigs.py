#!/usr/bin/env python3
"""Validate CSS gamedata signatures against real CS2 server binaries.

For every entry that has a `signatures` block, scan the matching platform
binary's executable sections and classify:

    matches == 1  -> ok        (unique, healthy)
    matches == 0  -> broken    (sig no longer present -> needs regen)
    matches  > 1  -> ambiguous (present but not unique -> weak sig)

Entries with only `offsets` (vtable slots) can't be validated from raw bytes,
so they're reported as `offset_only` and skipped.

Writes status.json (consumed by gen_report.py). Exit code is non-zero when any
signature is broken, so CI can gate on it.

Usage:
    validate_sigs.py --gamedata data/gamedata.json \
        --linux bin_linux/.../libserver.so \
        --windows bin_win/.../server.dll \
        --manifest data/manifest.txt \
        --out reports/status.json
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_sig import sig_to_regex, count_matches, exec_sections  # noqa: E402


def classify(n):
    if n == 1:
        return "ok"
    if n == 0:
        return "broken"
    return "ambiguous"


def validate(gamedata, binaries):
    """binaries = {'linux': path_or_None, 'windows': path_or_None}.

    Returns (results_list, sections_cache) where results_list is per-entry.
    """
    # Parse each binary's exec sections once.
    sections = {}
    for plat, path in binaries.items():
        if path and os.path.isfile(path):
            sections[plat] = exec_sections(path)
        else:
            sections[plat] = None

    results = []
    for name, entry in gamedata.items():
        sigs = entry.get("signatures")
        if not sigs:
            results.append({
                "name": name,
                "kind": "offset_only" if entry.get("offsets") else "unknown",
                "platforms": {},
            })
            continue

        plats = {}
        for plat in ("linux", "windows"):
            sig = sigs.get(plat)
            if not sig:
                plats[plat] = {"status": "missing_sig", "matches": None}
                continue
            if sections.get(plat) is None:
                plats[plat] = {"status": "no_binary", "matches": None}
                continue
            pattern = sig_to_regex(sig)
            n = count_matches(pattern, sections[plat])
            plats[plat] = {"status": classify(n), "matches": n}

        results.append({"name": name, "kind": "signature", "platforms": plats})
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gamedata", default="data/gamedata.json")
    ap.add_argument("--linux", default=None)
    ap.add_argument("--windows", default=None)
    ap.add_argument("--manifest", default="data/manifest.txt")
    ap.add_argument("--out", default="reports/status.json")
    args = ap.parse_args()

    with open(args.gamedata) as fh:
        gamedata = json.load(fh)

    manifest = None
    if os.path.isfile(args.manifest):
        with open(args.manifest) as fh:
            manifest = fh.read().strip()

    results = validate(gamedata, {"linux": args.linux, "windows": args.windows})

    # Tally.
    tally = {"ok": 0, "broken": 0, "ambiguous": 0, "no_binary": 0,
             "missing_sig": 0, "offset_only": 0}
    broken = []
    for r in results:
        if r["kind"] == "offset_only":
            tally["offset_only"] += 1
            continue
        for plat, info in r["platforms"].items():
            st = info["status"]
            tally[st] = tally.get(st, 0) + 1
            if st == "broken":
                broken.append("%s (%s)" % (r["name"], plat))

    out = {
        "manifest": manifest,
        "gamedata_source":
            "mrc4tt/CounterStrikeSharp "
            "configs/addons/counterstrikesharp/gamedata/gamedata.json",
        "tally": tally,
        "results": results,
    }
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2)

    print("validated %d entries -> %s" % (len(results), args.out))
    print("tally:", json.dumps(tally))
    if broken:
        print("BROKEN:", ", ".join(broken))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
