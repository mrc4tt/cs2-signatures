#!/usr/bin/env python3
"""Propose replacement signatures for broken/ambiguous entries by diffing
builds.

Runs after validate_sigs.py. For every project whose status.json lists a
`broken` platform entry (sig vanished) or an `ambiguous` one (sig matches
more than once — proposal = the same function's sig extended until unique
again), re-locate the function in the previous build
(bin_prev/, snapshotted by run_all.sh before a game update overwrites the
binaries) and emit a candidate signature for the new build via resig.

Writes reports/<id>/proposals.json per affected project (no timestamps —
see the status.json rule in the docs) and deletes it again once nothing is
broken, so stale proposals never linger. The candidates are ADVISORY: they
are surfaced in the tracker issue and Discord post for a human to verify
and PR upstream — nothing edits gamedata automatically.

Exit 0 always; failing to propose is never a pipeline error. stdlib only.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_sig import exec_sections  # noqa: E402
from resig import regen, BIN_FILES  # noqa: E402
import projects as P  # noqa: E402


class BinCache:
    """Lazy-load executable sections per (platform, library), old and new."""

    def __init__(self, old_dir, new_paths):
        self.old_dir = old_dir
        self.new_paths = new_paths
        self._cache = {}

    def _load(self, key, path):
        if key not in self._cache:
            self._cache[key] = (exec_sections(path)
                                if path and os.path.isfile(path) else None)
        return self._cache[key]

    def old(self, plat, library):
        fn = BIN_FILES.get((plat, library))
        path = os.path.join(self.old_dir, fn) if fn else None
        return self._load(("old", plat, library), path)

    def new(self, plat, library):
        return self._load(("new", plat, library),
                          self.new_paths.get((plat, library)))


def problem_entries(status):
    """[(name, platform, library, sig, reason), ...] for entries needing a
    proposal: broken (sig gone) and ambiguous (sig matches more than once —
    still resolvable via the old build, where the intended function matched
    uniquely, so we can extend the sig until it is unique again)."""
    out = []
    for r in status.get("results", []):
        for plat, info in r.get("platforms", {}).items():
            if info.get("status") in ("broken", "ambiguous") and info.get("sig"):
                out.append((r["name"], plat, info.get("library", "server"),
                            info["sig"], info["status"]))
    return out


def write_patched_gamedata(proj, proposals):
    """Drop-in gamedata.json with candidate sigs applied, for projects with at
    least one candidate. Attached to the Discord post as an UNVERIFIED file —
    candidates are unique-match checked but not runtime-tested."""
    gpath = P.proposed_gamedata_path(proj)
    candidates = [pr for pr in proposals if pr.get("candidate")]
    if not candidates:
        if os.path.isfile(gpath):
            os.remove(gpath)
        return
    with open(P.gamedata_path(proj)) as fh:
        gamedata = json.load(fh)
    for pr in candidates:
        entry = gamedata.get(pr["name"], {}).get("signatures")
        if entry is not None:
            entry[pr["platform"]] = pr["candidate"]
    with open(gpath, "w") as fh:
        json.dump(gamedata, fh, indent=2)
        fh.write("\n")
    print("[%s] patched gamedata (%d candidate sig(s)) -> %s"
          % (proj["id"], len(candidates), gpath))


def propose_project(proj, bins):
    """Write/refresh or remove reports/<id>/proposals.json (+ patched
    gamedata). Return count of candidates."""
    spath = P.status_path(proj)
    ppath = P.proposals_path(proj)
    if not os.path.isfile(spath):
        return 0
    with open(spath) as fh:
        status = json.load(fh)

    problems = problem_entries(status)
    if not problems:
        removed = False
        for stale in (ppath, P.proposed_gamedata_path(proj)):
            if os.path.isfile(stale):
                os.remove(stale)
                removed = True
        if removed:
            print("[%s] nothing broken/ambiguous — removed stale proposals"
                  % proj["id"])
        return 0

    proposals = []
    for name, plat, library, sig, reason in problems:
        entry = {"name": name, "platform": plat, "library": library,
                 "reason": reason, "old_sig": sig}
        old_secs = bins.old(plat, library)
        new_secs = bins.new(plat, library)
        if old_secs is None:
            entry["error"] = "no previous build snapshot (bin_prev)"
        elif new_secs is None:
            entry["error"] = "no current binary"
        else:
            entry.update(regen(sig, old_secs, new_secs))
        proposals.append(entry)

    out = {"project": proj["id"], "manifest": status.get("manifest"),
           "proposals": proposals}
    os.makedirs(os.path.dirname(ppath) or ".", exist_ok=True)
    with open(ppath, "w") as fh:
        json.dump(out, fh, indent=2)

    write_patched_gamedata(proj, proposals)

    got = sum(1 for pr in proposals if pr.get("candidate"))
    print("[%s] proposed %d/%d replacement sig(s) -> %s"
          % (proj["id"], got, len(proposals), ppath))
    for pr in proposals:
        if pr.get("candidate"):
            print("[%s]   %s (%s): %s"
                  % (proj["id"], pr["name"], pr["platform"], pr["candidate"]))
        else:
            print("[%s]   %s (%s): %s"
                  % (proj["id"], pr["name"], pr["platform"],
                     pr.get("error", "no candidate")))
    return got


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects", default=P.REGISTRY)
    ap.add_argument("--project", default=None, help="only this project id")
    ap.add_argument("--old-dir", default="bin_prev",
                    help="previous build snapshot dir")
    ap.add_argument("--linux", default=None, help="libserver.so (new build)")
    ap.add_argument("--windows", default=None, help="server.dll (new build)")
    ap.add_argument("--linux-engine2", default=None)
    ap.add_argument("--windows-engine2", default=None)
    args = ap.parse_args()

    bins = BinCache(args.old_dir, {
        ("linux", "server"): args.linux,
        ("windows", "server"): args.windows,
        ("linux", "engine2"): args.linux_engine2,
        ("windows", "engine2"): args.windows_engine2,
    })

    for proj in P.load(args.projects, only=args.project):
        try:
            propose_project(proj, bins)
        except Exception as e:  # noqa: BLE001 — advisory step, never fatal
            print("[%s] proposal failed: %s" % (proj["id"], e),
                  file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
