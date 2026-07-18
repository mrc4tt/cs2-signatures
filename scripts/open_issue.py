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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import projects as P  # noqa: E402

MARKER = "[sig-tracker] Broken signatures"


def api(server, token, method, path, body=None):
    url = "%s/api/v1%s" % (server.rstrip("/"), path)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "token %s" % token)
    req.add_header("Content-Type", "application/json")
    # Forgejo behind Cloudflare 403s the default urllib UA (error 1010).
    req.add_header("User-Agent",
                   "cs2-signatures-tracker (urllib, "
                   "+https://git.miksen.me/mikkel/cs2-signatures)")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        print("API %s %s -> %s: %s" % (method, path, e.code, e.read()[:300]),
              file=sys.stderr)
        raise


def load_statuses(projects_path, status_override=None):
    """Return [(project_id, status_dict), ...] across all tracked projects.

    status_override forces a single explicit status.json (single-project mode,
    used by tests / manual runs)."""
    if status_override:
        with open(status_override) as fh:
            s = json.load(fh)
        return [(s.get("project", "project"), s)]
    out = []
    for proj in P.load(projects_path):
        path = P.status_path(proj)
        if os.path.isfile(path):
            with open(path) as fh:
                out.append((proj["id"], json.load(fh)))
    return out


def broken_list(statuses):
    """[(project_id, "name (plat)"), ...] for every broken platform entry."""
    out = []
    for pid, status in statuses:
        for r in status["results"]:
            for plat, info in r.get("platforms", {}).items():
                if info.get("status") == "broken":
                    out.append((pid, "%s (%s)" % (r["name"], plat)))
    return out


def load_proposals(projects_path):
    """{(project_id, "name (plat)"): candidate_sig} from proposals.json files
    written by propose_sigs.py. Empty dict when none exist."""
    out = {}
    try:
        projects = P.load(projects_path)
    except Exception:  # noqa: BLE001 - proposals are optional decoration
        return out
    for proj in projects:
        path = P.proposals_path(proj)
        if not os.path.isfile(path):
            continue
        try:
            with open(path) as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            continue
        for pr in data.get("proposals", []):
            if pr.get("candidate"):
                key = (proj["id"], "%s (%s)" % (pr["name"], pr["platform"]))
                out[key] = pr["candidate"]
    return out


def body_text(statuses, broken, proposals=None):
    manifest = next((s.get("manifest") for _, s in statuses if s.get("manifest")),
                    None)
    proposals = proposals or {}
    lines = ["%s" % MARKER, "",
             "Manifest / buildid: `%s`" % (manifest or "unknown"),
             "", "**Broken (%d):**" % len(broken), ""]
    lines += ["- `[%s] %s`" % (pid, b) for pid, b in broken]
    proposed = [(pid, b) for pid, b in broken if (pid, b) in proposals]
    if proposed:
        lines += ["", "**Proposed replacements** (diffed against the previous "
                  "build - verify `matches == 1` before PRing upstream):", ""]
        for pid, b in proposed:
            lines += ["- `[%s] %s`" % (pid, b),
                      "  ```", "  %s" % proposals[(pid, b)], "  ```"]
    lines += ["", "Regenerate the affected project's gamedata with the Ghidra "
              "toolbox and PR its repo. See `docs/<project>.md` for the full "
              "per-signature table."]
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
    ap.add_argument("--projects", default=P.REGISTRY)
    ap.add_argument("--status", default=None,
                    help="single status.json override (default: all projects)")
    ap.add_argument("--server", default=os.environ.get("FORGEJO_SERVER")
                    or os.environ.get("GITHUB_SERVER_URL"))
    ap.add_argument("--repo", default=os.environ.get("FORGEJO_REPO")
                    or os.environ.get("GITHUB_REPOSITORY"))
    ap.add_argument("--token", default=os.environ.get("FORGEJO_TOKEN"))
    args = ap.parse_args()

    if not (args.server and args.repo and args.token):
        print("missing --server/--repo/--token (or env)", file=sys.stderr)
        return 1

    statuses = load_statuses(args.projects, args.status)
    broken = broken_list(statuses)
    existing = find_open_issue(args.server, args.token, args.repo)

    if not broken:
        if existing:
            api(args.server, args.token, "POST",
                "/repos/%s/issues/%d/comments" % (args.repo, existing["number"]),
                {"body": "All signatures pass again - closing."})
            api(args.server, args.token, "PATCH",
                "/repos/%s/issues/%d" % (args.repo, existing["number"]),
                {"state": "closed"})
            print("closed issue #%d" % existing["number"])
        else:
            print("nothing broken, no open issue")
        return 0

    title = "%s (%d)" % (MARKER, len(broken))
    body = body_text(statuses, broken, load_proposals(args.projects))
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
