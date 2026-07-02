#!/usr/bin/env python3
"""Validate CSS gamedata signatures against real CS2 server binaries.

For every entry with a `signatures` block, scan the matching platform+library
binary's executable sections and classify:

    matches == 1  -> ok        (unique, healthy)
    matches == 0  -> broken    (sig no longer present -> needs regen)
    matches  > 1  -> ambiguous (present but not unique -> weak sig)

The CSS `library` field ("server" / "engine2") picks which binary to scan.
Entries with only `offsets` (vtable slots) can't be byte-validated -> skipped.

Writes status.json (consumed by gen_report.py). Exit non-zero if any sig broke.

Edge over ianlucas/cs2-signatures: they scan the whole file and stop at the
first hit (boolean ok/broken). We scan per executable section and COUNT hits,
so we also flag `ambiguous` sigs (matches >1) that aren't actually unique.
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


def load_sections(path):
    if path and os.path.isfile(path):
        return exec_sections(path)
    return None


def validate(gamedata, bins):
    """bins = {(platform, library): sections_or_None}."""
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

        library = sigs.get("library", "server")
        plats = {}
        for plat in ("linux", "windows"):
            sig = sigs.get(plat)
            if not sig:
                plats[plat] = {"status": "missing_sig", "matches": None,
                               "library": library, "sig": None}
                continue
            secs = bins.get((plat, library))
            if secs is None:
                plats[plat] = {"status": "no_binary", "matches": None,
                               "library": library, "sig": sig}
                continue
            n = count_matches(sig_to_regex(sig), secs)
            plats[plat] = {"status": classify(n), "matches": n,
                           "library": library, "sig": sig}
        results.append({"name": name, "kind": "signature",
                        "library": library, "platforms": plats})
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gamedata", default="data/gamedata.json")
    ap.add_argument("--linux", default=None, help="libserver.so")
    ap.add_argument("--windows", default=None, help="server.dll")
    ap.add_argument("--linux-engine2", default=None, help="libengine2.so")
    ap.add_argument("--windows-engine2", default=None, help="engine2.dll")
    ap.add_argument("--manifest", default="data/manifest.json")
    ap.add_argument("--out", default="reports/status.json")
    args = ap.parse_args()

    with open(args.gamedata) as fh:
        gamedata = json.load(fh)

    manifest = None
    if os.path.isfile(args.manifest):
        with open(args.manifest) as fh:
            manifest = json.load(fh)

    bins = {
        ("linux", "server"): load_sections(args.linux),
        ("windows", "server"): load_sections(args.windows),
        ("linux", "engine2"): load_sections(args.linux_engine2),
        ("windows", "engine2"): load_sections(args.windows_engine2),
    }

    results = validate(gamedata, bins)

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
