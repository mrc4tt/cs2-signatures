#!/usr/bin/env python3
"""Open (or refresh) a draft PR with proposed signature fixes.

For every project that has reports/<id>/proposals.json with at least one
candidate AND `"propose_pr": true` in data/projects.json, push the patched
gamedata (reports/<id>/gamedata.proposed.json) to a `sig-tracker/proposals`
branch in that project's repo and open a PR against its tracked branch.

The branch name is stable, so a later run with fresher proposals updates
the same branch/PR instead of spamming new ones. Once nothing is broken,
proposals disappear and the PR is simply left for a human to close/merge —
we never merge or close anything automatically.

Works for repos the token can push to (all tracked projects live under the
user's own accounts). GitHub uses GITHUB_TOKEN/GH_TOKEN, Forgejo/Gitea
hosts use FORGEJO_TOKEN — same selection as fetch_gamedata.py.

--dry-run prints what would happen without calling any API.
stdlib only (urllib). Never hard-code a token.
"""
import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import projects as P  # noqa: E402

BRANCH = "sig-tracker/proposals"
TITLE = "Proposed signature updates (sig-tracker)"
UA = ("cs2-signatures-tracker (urllib, "
      "+https://git.miksen.me/mikkel/cs2-signatures)")


class ApiError(Exception):
    def __init__(self, code, body):
        super().__init__("HTTP %d: %s" % (code, body[:200]))
        self.code = code


def api(proj, token, method, path, body=None):
    if P.is_github(proj):
        url = "https://api.github.com" + path
        auth = "Bearer %s" % token
    else:
        url = "https://%s/api/v1%s" % (P.host(proj), path)
        auth = "token %s" % token
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", auth)
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", UA)
    if P.is_github(proj):
        req.add_header("Accept", "application/vnd.github+json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        raise ApiError(e.code, e.read().decode(errors="replace")) from None


def pr_body(proposals):
    lines = ["Automated proposal from the signature tracker.",
             "",
             "The previous game build was diffed against the current one to "
             "re-locate each function and regenerate its signature. Every "
             "candidate matches exactly once in the current build, but has "
             "NOT been runtime-tested — review before merging.",
             ""]
    for pr in proposals:
        if not pr.get("candidate"):
            continue
        lines += ["**%s** (%s, %s):" % (pr["name"], pr["platform"],
                                        pr.get("reason", "broken")),
                  "```",
                  "- %s" % pr["old_sig"],
                  "+ %s" % pr["candidate"],
                  "```", ""]
    return "\n".join(lines)


def ensure_branch(proj, token, base):
    """Create BRANCH at base's head (reset it there if it already exists on
    GitHub; Forgejo keeps the existing branch — contents update still works)."""
    repo = proj["repo"]
    if P.is_github(proj):
        ref = api(proj, token, "GET",
                  "/repos/%s/git/ref/heads/%s" % (repo, base))
        sha = ref["object"]["sha"]
        try:
            api(proj, token, "POST", "/repos/%s/git/refs" % repo,
                {"ref": "refs/heads/%s" % BRANCH, "sha": sha})
        except ApiError as e:
            if e.code != 422:  # 422 = already exists
                raise
            api(proj, token, "PATCH",
                "/repos/%s/git/refs/heads/%s" % (repo, BRANCH),
                {"sha": sha, "force": True})
    else:
        try:
            api(proj, token, "POST", "/repos/%s/branches" % repo,
                {"new_branch_name": BRANCH, "old_branch_name": base})
        except ApiError as e:
            if e.code != 409:  # 409 = already exists
                raise


def put_file(proj, token, content):
    """Create/update the gamedata file on BRANCH."""
    repo, path = proj["repo"], proj["path"]
    quoted = urllib.parse.quote(path)
    sha = None
    try:
        cur = api(proj, token, "GET",
                  "/repos/%s/contents/%s?ref=%s"
                  % (repo, quoted, urllib.parse.quote(BRANCH)))
        sha = (cur or {}).get("sha")
    except ApiError as e:
        if e.code != 404:
            raise
    body = {"message": "Update signatures (sig-tracker proposal)",
            "content": base64.b64encode(content).decode(),
            "branch": BRANCH}
    if sha:
        body["sha"] = sha
    api(proj, token, "PUT", "/repos/%s/contents/%s" % (repo, quoted), body)


def ensure_pr(proj, token, base, body):
    repo = proj["repo"]
    owner = repo.split("/")[0]
    try:
        pr = api(proj, token, "POST", "/repos/%s/pulls" % repo,
                 {"title": TITLE, "head": BRANCH, "base": base, "body": body})
        return pr.get("number") or pr.get("index"), True
    except ApiError as e:
        if e.code not in (409, 422):  # already exists
            raise
    if P.is_github(proj):
        prs = api(proj, token, "GET",
                  "/repos/%s/pulls?state=open&head=%s"
                  % (repo, urllib.parse.quote("%s:%s" % (owner, BRANCH))))
    else:
        prs = [p for p in (api(proj, token, "GET",
                               "/repos/%s/pulls?state=open" % repo) or [])
               if p.get("head", {}).get("ref") == BRANCH]
    if prs:
        num = prs[0].get("number") or prs[0].get("index")
        api(proj, token, "PATCH", "/repos/%s/pulls/%s" % (repo, num),
            {"body": body})
        return num, False
    return None, False


def process(proj, dry):
    if not proj.get("propose_pr"):
        return
    ppath = P.proposals_path(proj)
    gpath = P.proposed_gamedata_path(proj)
    if not (os.path.isfile(ppath) and os.path.isfile(gpath)):
        return
    with open(ppath) as fh:
        proposals = json.load(fh).get("proposals", [])
    candidates = [pr for pr in proposals if pr.get("candidate")]
    if not candidates:
        return

    base = proj["branch"]
    body = pr_body(proposals)
    if dry:
        print("[%s] DRY RUN: would push %s to %s:%s and PR -> %s (%d sig(s))"
              % (proj["id"], gpath, proj["repo"], BRANCH, base,
                 len(candidates)))
        return

    token = (os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
             if P.is_github(proj) else os.environ.get("FORGEJO_TOKEN"))
    if not token:
        print("[%s] no token for %s — skipping PR"
              % (proj["id"], P.host(proj)), file=sys.stderr)
        return

    with open(gpath, "rb") as fh:
        content = fh.read()
    ensure_branch(proj, token, base)
    put_file(proj, token, content)
    num, created = ensure_pr(proj, token, base, body)
    if num:
        print("[%s] %s PR #%s on %s"
              % (proj["id"], "opened" if created else "updated", num,
                 P.repo_url(proj)))
    else:
        print("[%s] pushed proposals to %s but found no PR to update"
              % (proj["id"], BRANCH), file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects", default=P.REGISTRY)
    ap.add_argument("--project", default=None, help="only this project id")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    for proj in P.load(args.projects, only=args.project):
        try:
            process(proj, args.dry_run)
        except Exception as e:  # noqa: BLE001 — advisory step, never fatal
            print("[%s] PR step failed: %s" % (proj["id"], e), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
