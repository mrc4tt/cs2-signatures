#!/usr/bin/env python3
"""Decide whether a run is worth a Discord post.

`run_all.sh` step 5 already gates commit/push on "did any status.json change".
That gate is deliberately wide: it fires on anything, including edits that carry
no news - renaming an entry in an upstream gamedata.json (say
`CAttributeList_SetOrAddAttributeValueByName` ->
`CAttributeList::SetOrAddAttributeValueByName`), reordering keys, or a fresh CS2
build where every signature still resolves. Committing those is correct; pinging
a Discord channel about them is noise.

So this script builds a narrower fingerprint per project and diffs it against
the committed (HEAD) status.json. The fingerprint keeps only what a reader would
call news:

    signature entries -> (platform, status, sig bytes)
    offset entries    -> (platform, status, offset value)

Names are NOT part of it - entries are compared as an unordered multiset, so a
pure rename is invisible. Deliberately excluded too: `matches` counts, `library`,
`method`, and `func_va` (a resolved address moves on every game build). The
manifest is excluded unless --include-manifest is passed, so a CS2 update that
breaks nothing stays silent.

Exit codes (mirroring check_update.py): 10 = post-worthy change, 0 = nothing to
announce, 1 = error. Run must happen BEFORE step 6 commits, since the comparison
baseline is HEAD.

stdlib only.
"""
import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import projects as P  # noqa: E402


def committed(path):
    """Parsed `git show HEAD:<path>`, or None when the file is not in HEAD
    (brand-new project) or the blob is unreadable."""
    try:
        raw = subprocess.run(["git", "show", "HEAD:%s" % path],
                             cwd=P.ROOT, capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    try:
        return json.loads(raw.decode("utf-8-sig"))
    except ValueError:
        return None


def fingerprint(status):
    """The news-carrying facts in one status.json, as a comparable structure."""
    items = []
    for r in status.get("results", []):
        kind = r.get("kind")
        offsets = r.get("offsets") or {}
        for plat, info in sorted(r.get("platforms", {}).items()):
            st = info.get("status")
            if kind == "signature":
                items.append((kind, plat, st, info.get("sig")))
            else:
                # Offset value lives under the platform key in `offsets`, and is
                # echoed inside the platform block; prefer the former.
                items.append((kind, plat, st,
                              offsets.get(plat, info.get(plat))))
    items.sort(key=lambda t: tuple("" if v is None else str(v) for v in t))
    return {"entries": items}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects", default=P.REGISTRY)
    ap.add_argument("--include-manifest", action="store_true",
                    help="treat a new game manifest as post-worthy even when "
                         "every signature still resolves the same way")
    ap.add_argument("--quiet", action="store_true",
                    help="exit code only, no explanation on stdout")
    args = ap.parse_args()

    try:
        projects = P.load(args.projects)
    except (OSError, ValueError) as e:
        print("cannot read project registry: %s" % e, file=sys.stderr)
        return 1

    changed = []
    for proj in projects:
        path = P.status_path(proj)
        full = os.path.join(P.ROOT, path)
        if not os.path.isfile(full):
            continue  # not validated this run - step 5 handles that case
        try:
            with open(full) as fh:
                current = json.load(fh)
        except (OSError, ValueError) as e:
            print("cannot read %s: %s" % (path, e), file=sys.stderr)
            return 1

        old = committed(path)
        if old is None:
            changed.append("%s (no committed status yet)" % proj["id"])
            continue
        if fingerprint(current)["entries"] != fingerprint(old)["entries"]:
            changed.append("%s (signature/offset result changed)" % proj["id"])
        elif args.include_manifest and \
                current.get("manifest") != old.get("manifest"):
            changed.append("%s (new game manifest)" % proj["id"])

    if not args.quiet:
        if changed:
            for line in changed:
                print("post-worthy: %s" % line)
        else:
            print("no signature/offset result change - nothing to announce")
    return 10 if changed else 0


if __name__ == "__main__":
    sys.exit(main())
