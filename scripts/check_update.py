#!/usr/bin/env python3
"""Detect a CS2 update via per-depot manifest IDs (DepotDownloader).

Runs `DepotDownloader -app 730 -depot <D> -manifest-only` for each platform
depot, parses `Manifest <id>`, and compares to the stored data/manifest.json.
Manifest IDs give exact SteamDB links (better than a single buildid).

Exit 10 = at least one depot manifest changed (CI proceeds).
Exit  0 = unchanged.
Exit  1 = error.

Anonymous by default (these depots are public). Pass STEAM_USER/STEAM_PASS env
to use a login if your setup needs it.
"""
import argparse
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from depots import APP, DEPOTS  # noqa: E402


def query_manifest(dd, depot):
    cmd = [dd, "-app", str(APP), "-depot", str(depot), "-manifest-only"]
    user = os.environ.get("STEAM_USER")
    if user:
        cmd += ["-username", user, "-password", os.environ.get("STEAM_PASS", ""),
                "-remember-password"]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=300).stdout
    m = re.search(r"Manifest\s+(\d+)", out)
    return m.group(1) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--depotdownloader", default=os.environ.get(
        "DEPOTDOWNLOADER", "DepotDownloader"))
    ap.add_argument("--manifest", default="data/manifest.json")
    args = ap.parse_args()

    old = {}
    if os.path.isfile(args.manifest):
        with open(args.manifest) as fh:
            old = json.load(fh)

    new = {}
    for plat, depot in DEPOTS.items():
        try:
            mid = query_manifest(args.depotdownloader, depot)
        except Exception as e:  # noqa: BLE001
            print("error querying depot %s: %s" % (depot, e), file=sys.stderr)
            return 1
        if not mid:
            print("could not parse manifest for depot %s" % depot,
                  file=sys.stderr)
            return 1
        new[str(depot)] = mid

    print(json.dumps(new))
    changed = new != old
    if changed:
        os.makedirs(os.path.dirname(args.manifest) or ".", exist_ok=True)
        with open(args.manifest, "w") as fh:
            json.dump(new, fh, indent=2)
        print("CHANGED %s -> %s" % (old, new), file=sys.stderr)
        return 10
    print("unchanged %s" % new, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
