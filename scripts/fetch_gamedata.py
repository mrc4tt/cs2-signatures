#!/usr/bin/env python3
"""Pull each tracked project's gamedata.json from its GitHub repo.

Projects come from data/projects.json (see scripts/projects.py). For every
project it fetches repo/branch/path and writes data/<id>/gamedata.json,
reporting per-project whether the bytes changed.

Private repos (e.g. the mrc4tt CounterStrikeSharp fork) need a token: set
GITHUB_TOKEN / GH_TOKEN to a PAT that can read them (fine-grained: Contents
read; classic: `repo` scope). Public repos fetch anonymously — the token is
sent anyway when present, which is harmless.

Use --project ID to fetch a single project. stdlib only. Exit non-zero if any
project fails to fetch (existing snapshots are left untouched for those).
"""
import argparse
import hashlib
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import projects as P  # noqa: E402


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


def fetch_project(proj, token):
    """Fetch one project into data/<id>/gamedata.json. Return True on success."""
    out = P.gamedata_path(proj)
    old = b""
    if os.path.isfile(out):
        with open(out, "rb") as fh:
            old = fh.read()

    tok = token if proj.get("private") else (token or None)
    try:
        new = fetch(proj["repo"], proj["branch"], proj["path"], tok)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 404) and proj.get("private") and not token:
            print("[%s] HTTP %d — repo is private; set GITHUB_TOKEN (or "
                  "GH_TOKEN) to a PAT with Contents:read." % (proj["id"], e.code),
                  file=sys.stderr)
        else:
            print("[%s] HTTP %d fetching %s: %s"
                  % (proj["id"], e.code, proj["path"], e.reason), file=sys.stderr)
        return False

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "wb") as fh:
        fh.write(new)
    print("[%s] gamedata %s"
          % (proj["id"], "changed" if sha(old) != sha(new) else "unchanged"))
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects", default=P.REGISTRY)
    ap.add_argument("--project", default=None, help="fetch only this project id")
    args = ap.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    projects = P.load(args.projects, only=args.project)

    failed = 0
    for proj in projects:
        if not fetch_project(proj, token):
            failed += 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
