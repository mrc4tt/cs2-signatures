#!/usr/bin/env python3
"""Detect a CS2 update by comparing the public-branch buildid.

Runs `steamcmd +login anonymous +app_info_update 1 +app_info_print 730 +quit`,
extracts the `public` branch buildid from the VDF dump, and compares it to the
stored value in data/manifest.txt.

Exit code 10 = changed (CI should proceed to download+validate).
Exit code  0 = unchanged.
Exit code  1 = error (couldn't determine buildid).

Prints the buildid to stdout on success so CI can capture it.

Note: app_info for 730 needs a real (non-anonymous) Steam login on some setups
to see branch data. Pass --steamcmd to point at your steamcmd binary and
--login to force a specific account; anonymous is the default.
"""
import argparse
import os
import re
import subprocess
import sys


def query_buildid(steamcmd, login):
    cmd = [steamcmd, "+login", login,
           "+app_info_update", "1", "+app_info_print", "730", "+quit"]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=300).stdout
    # Find the "public" branch block, then its buildid.
    m = re.search(r'"public"\s*\{(.*?)\}', out, re.S)
    block = m.group(1) if m else out
    b = re.search(r'"buildid"\s*"(\d+)"', block)
    if not b:
        # Fall back to first buildid anywhere in the dump.
        b = re.search(r'"buildid"\s*"(\d+)"', out)
    return b.group(1) if b else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steamcmd", default="steamcmd")
    ap.add_argument("--login", default="anonymous")
    ap.add_argument("--manifest", default="data/manifest.txt")
    args = ap.parse_args()

    try:
        buildid = query_buildid(args.steamcmd, args.login)
    except Exception as e:  # noqa: BLE001
        print("error querying steamcmd: %s" % e, file=sys.stderr)
        return 1
    if not buildid:
        print("could not parse buildid", file=sys.stderr)
        return 1

    old = None
    if os.path.isfile(args.manifest):
        with open(args.manifest) as fh:
            old = fh.read().strip()

    print(buildid)
    if buildid != old:
        print("CHANGED old=%s new=%s" % (old, buildid), file=sys.stderr)
        # Persist immediately so a mid-run crash doesn't loop forever.
        with open(args.manifest, "w") as fh:
            fh.write(buildid + "\n")
        return 10
    print("unchanged (%s)" % buildid, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
