#!/usr/bin/env python3
"""Publish the downloaded CS2 server/engine2 binaries as Forgejo release assets.

The binaries are git-ignored (copyright + size), but on a self-hosted Forgejo we
still want them downloadable. Each CS2 update this attaches the four files to a
release tagged by the CS2 patch version, so users can grab the exact `.so`/`.dll`
that a signature set was validated against — without bloating git history.

    libserver.so  libengine2.so  server.dll  engine2.dll  ->  release <version>

Retention: keep only the newest --keep releases that WE manage (marked in the
release body); older managed releases + their tags are deleted. Unrelated
releases are never touched.

Version: --version wins; else CS2 ClientVersion from steam.inf (--steam-inf);
else the linux depot manifest id from data/manifest.json; else the --iso date.

Auth: FORGEJO_TOKEN + server/repo (env GITHUB_SERVER_URL + GITHUB_REPOSITORY on
Forgejo Actions, or --server/--repo). stdlib only. Mirrors open_issue.py.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from depots import DEPOTS  # noqa: E402

# Marks releases created by this script so retention never deletes unrelated
# releases someone made by hand.
MARKER = "<!-- cs2-sig-tracker:bins -->"

# The four assets, resolved from the download dirs by run_all / CLI.
ASSET_ARGS = ("linux", "linux_engine2", "windows", "windows_engine2")


def api(server, token, method, path, body=None):
    url = "%s/api/v1%s" % (server.rstrip("/"), path)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "token %s" % token)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        print("API %s %s -> %s: %s" % (method, path, e.code, e.read()[:300]),
              file=sys.stderr)
        raise


def upload_asset(server, token, repo, release_id, path):
    """Multipart upload one file as a release asset (stdlib, no requests)."""
    name = os.path.basename(path)
    with open(path, "rb") as fh:
        content = fh.read()
    boundary = "----cs2sigbins7f3a9c"  # fixed: no randomness available in-script
    pre = ("--%s\r\nContent-Disposition: form-data; name=\"attachment\"; "
           "filename=\"%s\"\r\nContent-Type: application/octet-stream\r\n\r\n"
           % (boundary, name)).encode()
    post = ("\r\n--%s--\r\n" % boundary).encode()
    data = pre + content + post
    url = ("%s/api/v1/repos/%s/releases/%d/assets?name=%s"
           % (server.rstrip("/"), repo, release_id,
              urllib.parse.quote(name)))
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", "token %s" % token)
    req.add_header("Content-Type", "multipart/form-data; boundary=%s" % boundary)
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.status


def ensure_release(server, token, repo, tag, name):
    """Get the release for `tag`, creating it (marked) if missing."""
    try:
        rel = api(server, token, "GET",
                  "/repos/%s/releases/tags/%s" % (repo, urllib.parse.quote(tag)))
        if rel:
            return rel
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
    return api(server, token, "POST", "/repos/%s/releases" % repo,
               {"tag_name": tag, "name": name,
                "body": "%s\nCS2 server + engine2 binaries for `%s`." % (MARKER, tag)})


def replace_assets(server, token, repo, rel, paths):
    """Delete same-named existing assets, then upload each path fresh."""
    existing = {a["name"]: a["id"] for a in rel.get("assets") or []}
    for path in paths:
        nm = os.path.basename(path)
        if nm in existing:
            api(server, token, "DELETE",
                "/repos/%s/releases/%d/assets/%d"
                % (repo, rel["id"], existing[nm]))
        upload_asset(server, token, repo, rel["id"], path)
        print("uploaded %s" % nm)


def prune(server, token, repo, keep, current_tag):
    """Delete managed releases beyond the newest `keep` (by created date)."""
    rels = api(server, token, "GET",
               "/repos/%s/releases?limit=50" % repo) or []
    mine = [r for r in rels if MARKER in (r.get("body") or "")]
    mine.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    for r in mine[keep:]:
        rid, tag = r["id"], r.get("tag_name", "")
        api(server, token, "DELETE", "/repos/%s/releases/%d" % (repo, rid))
        if tag:
            try:
                api(server, token, "DELETE",
                    "/repos/%s/tags/%s" % (repo, urllib.parse.quote(tag)))
            except urllib.error.HTTPError:
                pass  # tag delete is best-effort
        print("pruned release %s" % (tag or rid))


def client_version(steam_inf):
    if steam_inf and os.path.isfile(steam_inf):
        with open(steam_inf, errors="ignore") as fh:
            m = re.search(r"ClientVersion=(\d+)", fh.read())
            if m:
                return m.group(1)
    return None


def resolve_version(args):
    if args.version:
        return args.version
    cv = client_version(args.steam_inf)
    if cv:
        return cv
    if os.path.isfile(args.manifest):
        with open(args.manifest) as fh:
            man = json.load(fh)
        mid = man.get(str(DEPOTS["linux"]))
        if mid:
            return mid
    return args.iso or "unknown"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--linux", help="libserver.so path")
    ap.add_argument("--linux-engine2", dest="linux_engine2", help="libengine2.so")
    ap.add_argument("--windows", help="server.dll path")
    ap.add_argument("--windows-engine2", dest="windows_engine2", help="engine2.dll")
    ap.add_argument("--version", default=None, help="release tag override")
    ap.add_argument("--steam-inf", default="bin_linux/game/csgo/steam.inf",
                    help="steam.inf to read CS2 ClientVersion from")
    ap.add_argument("--manifest", default="data/manifest.json")
    ap.add_argument("--iso", default=None, help="date fallback for the tag")
    ap.add_argument("--keep", type=int, default=2,
                    help="how many recent binary releases to retain")
    ap.add_argument("--server", default=os.environ.get("FORGEJO_SERVER")
                    or os.environ.get("GITHUB_SERVER_URL"))
    ap.add_argument("--repo", default=os.environ.get("FORGEJO_REPO")
                    or os.environ.get("GITHUB_REPOSITORY"))
    ap.add_argument("--token", default=os.environ.get("FORGEJO_TOKEN"))
    args = ap.parse_args()

    if not (args.server and args.repo and args.token):
        print("missing --server/--repo/--token (or env)", file=sys.stderr)
        return 1

    paths = [getattr(args, k) for k in ASSET_ARGS]
    paths = [p for p in paths if p and os.path.isfile(p)]
    if not paths:
        print("no binary files found to upload", file=sys.stderr)
        return 1

    version = resolve_version(args)
    tag = "bins-%s" % version
    rel = ensure_release(args.server, args.token, args.repo, tag,
                         "CS2 binaries %s" % version)
    replace_assets(args.server, args.token, args.repo, rel, paths)
    prune(args.server, args.token, args.repo, args.keep, tag)
    print("published %d assets to release %s" % (len(paths), tag))
    return 0


if __name__ == "__main__":
    sys.exit(main())
