#!/usr/bin/env python3
"""Pull the latest gamedata.json from the mrc4tt CounterStrikeSharp fork.

The fork is **private**, so this uses the authenticated GitHub contents API
(raw media type) with a token. Set one of GITHUB_TOKEN / GH_TOKEN to a PAT that
can read the repo (fine-grained: Contents read; classic: `repo` scope).

If you make the fork public, the token is optional and the plain raw URL works.

Writes data/gamedata.json. Reports whether it changed. stdlib only.
"""
import argparse
import hashlib
import os
import sys
import urllib.error
import urllib.request

REPO = "mrc4tt/CounterStrikeSharp"
BRANCH = "main"
PATH = "configs/addons/counterstrikesharp/gamedata/gamedata.json"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def fetch(repo, branch, path, token):
    api = "https://api.github.com/repos/%s/contents/%s?ref=%s" % (
        repo, path, branch)
    req = urllib.request.Request(api)
    req.add_header("User-Agent", "cs2-sig-tracker")
    # raw media type -> body is the file bytes, not JSON-wrapped base64.
    req.add_header("Accept", "application/vnd.github.raw")
    if token:
        req.add_header("Authorization", "Bearer %s" % token)
    return urllib.request.urlopen(req, timeout=60).read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--branch", default=BRANCH)
    ap.add_argument("--path", default=PATH)
    ap.add_argument("--out", default="data/gamedata.json")
    args = ap.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    old = b""
    if os.path.isfile(args.out):
        with open(args.out, "rb") as fh:
            old = fh.read()

    try:
        new = fetch(args.repo, args.branch, args.path, token)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 404) and not token:
            print("HTTP %d — the fork is private; set GITHUB_TOKEN (or GH_TOKEN) "
                  "to a PAT with Contents:read, or make the fork public."
                  % e.code, file=sys.stderr)
        else:
            print("HTTP %d fetching gamedata: %s" % (e.code, e.reason),
                  file=sys.stderr)
        return 1

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "wb") as fh:
        fh.write(new)

    print("gamedata changed" if sha(old) != sha(new) else "gamedata unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
