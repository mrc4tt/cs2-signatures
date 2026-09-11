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

What is deliberately NOT news is anything the reference snapshot says on its
own. A symbol appearing in a newer snapshot flips an offset from `no_recipe` to
a real verdict without anything about the game or the gamedata having changed,
so `no_recipe` blocks are left out of the fingerprint entirely. The signature
`outdated` verdict is excluded for the same reason plus a stronger one: it
compares our bytes against a third-party analysis of a possibly different build,
so a sig that resolves uniquely here can still be called `outdated`. That is a
disagreement between two sources, not a change in this repo, and it must not
drive a post.

Names are NOT part of it - entries are compared as an unordered multiset, so a
pure rename is invisible. Deliberately excluded too: `matches` counts, `library`,
`method`, and `func_va` (a resolved address moves on every game build). The
manifest is excluded unless --include-manifest is passed, so a CS2 update that
breaks nothing stays silent.

--write-delta additionally dumps the NAMED per-entry delta (which signature
went which way) for post_discord.py to render. That view needs names, so it is
built separately from the fingerprint above - see named_changes().

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
            elif st == "no_recipe":
                continue  # "no verdict available" is not a result
            else:
                # Offset value lives under the platform key in `offsets`, and is
                # echoed inside the platform block; prefer the former.
                items.append((kind, plat, st,
                              offsets.get(plat, info.get(plat))))
    items.sort(key=lambda t: tuple("" if v is None else str(v) for v in t))
    return {"entries": items}


# ---------------------------------------------------------------------------
# Named delta (for the Discord report)
#
# fingerprint() above deliberately drops names so a pure rename cannot trigger
# a post. The report needs the opposite: which entry changed, by name. Same
# source data, different projection - kept here so both views stay in sync.
# ---------------------------------------------------------------------------

# Ordered worst-first; the report renders them in this order.
CHANGE_ORDER = ("broke", "removed", "changed", "fixed", "added",
                "resigned", "moved")


def entry_map(status):
    """{(kind, name, platform): facts} for one status.json."""
    out = {}
    for r in status.get("results", []):
        kind = r.get("kind")
        offsets = r.get("offsets") or {}
        for plat, info in (r.get("platforms") or {}).items():
            out[(kind, r.get("name"), plat)] = {
                "status": info.get("status"),
                "sig": info.get("sig"),
                "offset": offsets.get(plat, info.get(plat)),
            }
    return out


def classify(old, new):
    """Change kind for one entry, or None when nothing worth reporting moved."""
    if old is None:
        return "added"
    if new is None:
        return "removed"
    if old["status"] != new["status"]:
        if new["status"] == "ok":
            return "fixed"
        if new["status"] in ("broken", "ambiguous", "stale"):
            return "broke"
        return "changed"
    if new.get("sig") != old.get("sig"):
        return "resigned"
    if new.get("offset") != old.get("offset"):
        return "moved"
    return None


def named_changes(projects_path=P.REGISTRY):
    """[{project, kind, name, platform, change, old, new}, ...] vs HEAD.

    A project with no committed status yet is skipped rather than reported as
    dozens of "added" rows - its first report is the baseline, not news.
    """
    changes = []
    try:
        projects = P.load(projects_path)
    except (OSError, ValueError):
        return changes
    for proj in projects:
        path = P.status_path(proj)
        full = os.path.join(P.ROOT, path)
        if not os.path.isfile(full):
            continue
        try:
            with open(full) as fh:
                current = json.load(fh)
        except (OSError, ValueError):
            continue
        old = committed(path)
        if old is None:
            continue
        cur_map, old_map = entry_map(current), entry_map(old)
        for key in sorted(set(cur_map) | set(old_map)):
            kind, name, plat = key
            change = classify(old_map.get(key), cur_map.get(key))
            if not change:
                continue
            changes.append({
                "project": proj["id"], "kind": kind, "name": name,
                "platform": plat, "change": change,
                "old": (old_map.get(key) or {}).get("status"),
                "new": (cur_map.get(key) or {}).get("status"),
            })
    changes.sort(key=lambda c: (CHANGE_ORDER.index(c["change"])
                                if c["change"] in CHANGE_ORDER else 99,
                                c["project"], c["name"], c["platform"]))
    return changes


def write_delta(path, changes):
    """Dump the named delta for post_discord.py to render.

    Written before the commit in step 6, read after it - by then HEAD has moved
    and the diff is no longer computable, so it has to be handed over on disk.
    Git-ignored: it is per-run scratch, not a tracked result.
    """
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    counts = {}
    for c in changes:
        counts[c["change"]] = counts.get(c["change"], 0) + 1
    with open(path, "w") as fh:
        json.dump({"changes": changes, "counts": counts}, fh, indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects", default=P.REGISTRY)
    ap.add_argument("--include-manifest", action="store_true",
                    help="treat a new game manifest as post-worthy even when "
                         "every signature still resolves the same way")
    ap.add_argument("--quiet", action="store_true",
                    help="exit code only, no explanation on stdout")
    ap.add_argument("--write-delta", default=None, metavar="PATH",
                    help="also dump the named per-entry delta vs HEAD to PATH "
                         "(read by post_discord.py, which runs after the "
                         "commit has moved HEAD)")
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

    if args.write_delta:
        try:
            write_delta(args.write_delta, named_changes(args.projects))
        except OSError as e:
            # Decoration for the report, never a reason to fail the gate.
            print("cannot write delta: %s" % e, file=sys.stderr)

    if not args.quiet:
        if changed:
            for line in changed:
                print("post-worthy: %s" % line)
        else:
            print("no signature/offset result change - nothing to announce")
    return 10 if changed else 0


if __name__ == "__main__":
    sys.exit(main())
