#!/usr/bin/env python3
"""Open (or update) a Forgejo issue when signatures are broken.

Reads reports/status.json. If any entry/platform is `broken`, ensures there is
a single open tracking issue:
  - none open  -> create one
  - already open (title marker match) -> post a comment with the new state

De-dupes on the title marker so game updates don't spam a new issue each run.
When nothing is broken, closes any open tracker issue.

Auth: Forgejo API token via env FORGEJO_TOKEN. Server + repo from env
GITHUB_SERVER_URL + GITHUB_REPOSITORY (Forgejo Actions set these), or pass
--server / --repo explicitly.

stdlib only (urllib). Never hard-code the token.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

MARKER = "[sig-tracker] Broken signatures"


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


def broken_list(status):
    out = []
    for r in status["results"]:
        for plat, info in r.get("platforms", {}).items():
            if info.get("status") == "broken":
                out.append("%s (%s)" % (r["name"], plat))
    return out


def body_text(status, broken):
    lines = ["%s" % MARKER, "",
             "Manifest / buildid: `%s`" % (status.get("manifest") or "unknown"),
             "", "**Broken (%d):**" % len(broken), ""]
    lines += ["- `%s`" % b for b in broken]
    lines += ["", "Regenerate with the Ghidra toolbox (`CS2Recipes.py`) and "
              "PR the mrc4tt fork. See `reports/STATUS.md` for the full table."]
    return "\n".join(lines)


def find_open_issue(server, token, repo):
    issues = api(server, token, "GET",
                 "/repos/%s/issues?state=open&type=issues&limit=50" % repo) or []
    for it in issues:
        if it.get("title", "").startswith(MARKER):
            return it
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", default="reports/status.json")
    ap.add_argument("--server", default=os.environ.get("GITHUB_SERVER_URL"))
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"))
    ap.add_argument("--token", default=os.environ.get("FORGEJO_TOKEN"))
    args = ap.parse_args()

    if not (args.server and args.repo and args.token):
        print("missing --server/--repo/--token (or env)", file=sys.stderr)
        return 1

    with open(args.status) as fh:
        status = json.load(fh)
    broken = broken_list(status)
    existing = find_open_issue(args.server, args.token, args.repo)

    if not broken:
        if existing:
            api(args.server, args.token, "POST",
                "/repos/%s/issues/%d/comments" % (args.repo, existing["number"]),
                {"body": "All signatures pass again — closing."})
            api(args.server, args.token, "PATCH",
                "/repos/%s/issues/%d" % (args.repo, existing["number"]),
                {"state": "closed"})
            print("closed issue #%d" % existing["number"])
        else:
            print("nothing broken, no open issue")
        return 0

    title = "%s (%d)" % (MARKER, len(broken))
    body = body_text(status, broken)
    if existing:
        api(args.server, args.token, "POST",
            "/repos/%s/issues/%d/comments" % (args.repo, existing["number"]),
            {"body": body})
        api(args.server, args.token, "PATCH",
            "/repos/%s/issues/%d" % (args.repo, existing["number"]),
            {"title": title})
        print("updated issue #%d" % existing["number"])
    else:
        it = api(args.server, args.token, "POST",
                 "/repos/%s/issues" % args.repo, {"title": title, "body": body})
        print("opened issue #%d" % it["number"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
