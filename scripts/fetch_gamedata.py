#!/usr/bin/env python3
"""Pull each tracked project's gamedata.json from its forge repo.

Projects come from data/projects.json (see scripts/projects.py). For every
project it fetches repo/branch/path and writes data/<id>/gamedata.json,
reporting per-project whether the bytes changed. Each project's `host` field
selects the forge (default github.com; e.g. git.miksen.me for Forgejo/Gitea).

Private repos (e.g. the mrc4tt CounterStrikeSharp fork) need a token:
  - github.com  -> GITHUB_TOKEN / GH_TOKEN (fine-grained Contents:read, or
                   classic `repo` scope)
  - Forgejo/Gitea host -> FORGEJO_TOKEN (scope: read:repository)
Public repos fetch anonymously — the token is sent anyway when present, which
is harmless.

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


def fetch(proj, token):
    repo, branch, path = proj["repo"], proj["branch"], proj["path"]
    if P.is_github(proj):
        url = "https://api.github.com/repos/%s/contents/%s?ref=%s" % (
            repo, path, branch)
        # raw media type -> body is the file bytes, not JSON-wrapped base64.
        accept, auth = "application/vnd.github.raw", "Bearer %s" % token
    else:
        # Forgejo/Gitea raw-file endpoint returns the bytes directly.
        url = "https://%s/api/v1/repos/%s/raw/%s?ref=%s" % (
            P.host(proj), repo, path, branch)
        accept, auth = None, "token %s" % token
    req = urllib.request.Request(url)
    # Descriptive UA — some hosts (Cloudflare) 403 the default urllib UA.
    req.add_header("User-Agent",
                   "cs2-sig-tracker (+https://git.miksen.me/mikkel/cs2-signatures)")
    if accept:
        req.add_header("Accept", accept)
    if token:
        req.add_header("Authorization", auth)
    raw = urllib.request.urlopen(req, timeout=60).read()
    # Some forges serve UTF-8 files with a BOM; strip it so plain json.load
    # (validate_sigs) parses the snapshot.
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw


def token_for(proj, gh_token, fj_token):
    return gh_token if P.is_github(proj) else fj_token


def fetch_project(proj, gh_token, fj_token):
    """Fetch one project into data/<id>/gamedata.json. Return True on success."""
    out = P.gamedata_path(proj)
    old = b""
    if os.path.isfile(out):
        with open(out, "rb") as fh:
            old = fh.read()

    token = token_for(proj, gh_token, fj_token)
    tok = token if proj.get("private") else (token or None)
    try:
        new = fetch(proj, tok)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 404) and proj.get("private") and not token:
            env = "GITHUB_TOKEN/GH_TOKEN" if P.is_github(proj) else "FORGEJO_TOKEN"
            print("[%s] HTTP %d — repo is private; set %s to a token that can "
                  "read it." % (proj["id"], e.code, env), file=sys.stderr)
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

    gh_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    fj_token = os.environ.get("FORGEJO_TOKEN")
    projects = P.load(args.projects, only=args.project)

    failed = 0
    for proj in projects:
        if not fetch_project(proj, gh_token, fj_token):
            failed += 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
