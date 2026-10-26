#!/usr/bin/env python3
"""Report the tracker's reference gaps back to the analysis repo as one issue.

`reference_gaps.py` works out which tracked symbols CS2_VibeSignatures cannot
answer for. That list is only useful where the analysis happens, so this keeps a
single issue in the analysis repo in sync with it.

One stable issue, updated in place - never a new one per run, and never a
comment per game build. The body carries a fingerprint of the gap SET (not the
snapshot version), and an unchanged fingerprint means the run does nothing at
all: a new game version with the same holes is not news, and an issue that
pings every half hour is an issue nobody reads. When the last gap closes, the
issue is updated one final time and closed.

The two repos live on different machines and share nothing but published
artifacts, so this is deliberately a plain GitHub issue: no endpoint to run, no
credentials on the other side, and it degrades to "do nothing" when the token
is absent.

    python3 scripts/open_gap_issue.py --dry-run     # print, call nothing
    python3 scripts/open_gap_issue.py               # create or update

Auth: GITHUB_TOKEN or GH_TOKEN, needs issue write on the target repo.
stdlib only (urllib). Never hard-code a token.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import projects as P  # noqa: E402
import reference_gaps as G  # noqa: E402
from fetch_symbols import REPO as SYMBOLS_REPO  # noqa: E402

TITLE = "Symbol coverage gaps reported by the cs2-signatures tracker"
TRACKER_URL = "https://github.com/mrc4tt/cs2-signatures"
MARKER = "<!-- gap-fingerprint: %s -->"
MARKER_RE = re.compile(r"<!-- gap-fingerprint: ([0-9a-f]{64}) -->")
UA = "cs2-sig-tracker (+%s)" % TRACKER_URL


class ApiError(Exception):
    def __init__(self, code, body):
        super().__init__("HTTP %d: %s" % (code, body[:200]))
        self.code = code


def repo_slug(url):
    """owner/name out of the analysis repo's clone URL."""
    return re.sub(r"\.git$", "", url.split("github.com/")[-1].strip("/"))


def api(token, method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request("https://api.github.com" + path, data=data,
                                 method=method)
    req.add_header("Authorization", "Bearer %s" % token)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", UA)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        raise ApiError(e.code, e.read().decode(errors="replace")) from None


def find_issue(token, repo, title):
    """The tracker's issue in `repo`, open or closed, or None.

    Matched by exact title rather than by a label, so it works on a repo that
    has never been set up for this and needs no write access beyond issues.
    """
    for state in ("open", "closed"):
        page = api(token, "GET",
                   "/repos/%s/issues?state=%s&per_page=100" % (repo, state))
        for issue in page or []:
            if issue.get("title") == title and "pull_request" not in issue:
                return issue
    return None


def body_fingerprint(body):
    m = MARKER_RE.search(body or "")
    return m.group(1) if m else None


def build_body(report):
    return "%s\n%s\n" % (G.render_markdown(report, TRACKER_URL),
                         MARKER % report["fingerprint"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects", default=P.REGISTRY)
    ap.add_argument("--aliases", default=G.ALIASES)
    ap.add_argument("--repo", default=os.environ.get("SYMBOLS_ISSUE_REPO")
                    or repo_slug(SYMBOLS_REPO),
                    help="owner/name of the analysis repo (default: the repo "
                         "fetch_symbols.py reads)")
    ap.add_argument("--title", default=TITLE)
    ap.add_argument("--token", default=os.environ.get("GITHUB_TOKEN")
                    or os.environ.get("GH_TOKEN"))
    ap.add_argument("--out", default=os.path.join("reports",
                                                  "reference_gaps.json"),
                    help="also write the machine-readable report here")
    ap.add_argument("--dry-run", action="store_true",
                    help="print what would be posted, call no API")
    ap.add_argument("--force", action="store_true",
                    help="update even when the gap set is unchanged")
    args = ap.parse_args()

    report = G.collect(args.projects, args.aliases)
    report["fingerprint"] = G.fingerprint(report)
    if args.out:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w") as fh:
            json.dump(report, fh, indent=2)

    body = build_body(report)
    if args.dry_run:
        print("repo:  %s" % args.repo)
        print("title: %s" % args.title)
        print()
        print(body, end="")
        return 0

    if not args.token:
        print("no GITHUB_TOKEN/GH_TOKEN - skipping gap issue", file=sys.stderr)
        return 0

    try:
        issue = find_issue(args.token, args.repo, args.title)
        if issue is None:
            if not report["gaps"]:
                print("no reference gaps and no issue open - nothing to do")
                return 0
            new = api(args.token, "POST", "/repos/%s/issues" % args.repo,
                      {"title": args.title, "body": body})
            print("opened %s#%d (%d gap(s))"
                  % (args.repo, new["number"], len(report["gaps"])))
            return 0

        unchanged = body_fingerprint(issue.get("body")) == report["fingerprint"]
        if unchanged and not args.force and \
                issue["state"] == ("closed" if not report["gaps"] else "open"):
            print("gap set unchanged - leaving %s#%d alone"
                  % (args.repo, issue["number"]))
            return 0

        patch = {"body": body}
        if not report["gaps"]:
            patch["state"] = "closed"
        elif issue["state"] == "closed":
            # Gaps came back (a symbol dropped out of a newer snapshot).
            patch["state"] = "open"
        api(args.token, "PATCH",
            "/repos/%s/issues/%d" % (args.repo, issue["number"]), patch)
        print("updated %s#%d (%d gap(s)%s)"
              % (args.repo, issue["number"], len(report["gaps"]),
                 ", closed" if patch.get("state") == "closed" else ""))
    except (ApiError, urllib.error.URLError) as e:
        # The analysis repo being unreachable is not a reason to fail a run.
        print("gap issue failed: %s" % e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
