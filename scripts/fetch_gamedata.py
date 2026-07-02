#!/usr/bin/env python3
"""Pull the latest gamedata.json from the mrc4tt CounterStrikeSharp fork.

Writes data/gamedata.json. Prints whether it changed vs the local copy so CI
can note "upstream sig set changed" separately from "game updated".
stdlib only (urllib).
"""
import argparse
import hashlib
import os
import sys
import urllib.request

RAW = ("https://raw.githubusercontent.com/mrc4tt/CounterStrikeSharp/main/"
       "configs/addons/counterstrikesharp/gamedata/gamedata.json")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=RAW)
    ap.add_argument("--out", default="data/gamedata.json")
    args = ap.parse_args()

    old = b""
    if os.path.isfile(args.out):
        with open(args.out, "rb") as fh:
            old = fh.read()

    req = urllib.request.Request(args.url, headers={"User-Agent": "cs2-sig-tracker"})
    new = urllib.request.urlopen(req, timeout=60).read()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "wb") as fh:
        fh.write(new)

    changed = sha(old) != sha(new)
    print("gamedata changed" if changed else "gamedata unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
