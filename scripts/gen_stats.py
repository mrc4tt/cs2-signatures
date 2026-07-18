#!/usr/bin/env python3
"""Generate docs/stats.md: signature fragility mined from git history.

Every meaningful change commits reports/<id>/status.json, so its git
history is a timeline of each signature's health. Walk it (oldest first),
count transitions into broken/ambiguous per signature, and write a
fragility report: which signatures break most, per project.

Run by run_all.sh step 6 alongside gen_report.py (only on a real change),
with the same --date stamp. stdlib only.
"""
import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import projects as P  # noqa: E402


def snapshots(path):
    """All committed versions of a status.json, oldest first."""
    shas = subprocess.run(
        ["git", "log", "--reverse", "--format=%H", "--", path],
        capture_output=True, text=True).stdout.split()
    out = []
    for sha in shas:
        r = subprocess.run(["git", "show", "%s:%s" % (sha, path)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            continue
        try:
            out.append(json.loads(r.stdout))
        except ValueError:
            continue
    return out


def sig_stats(snaps):
    """{(name, platform): {breaks, ambiguous, current, observations}}."""
    seq = {}
    for snap in snaps:
        for res in snap.get("results", []):
            for plat, info in res.get("platforms", {}).items():
                st = info.get("status")
                if st:
                    seq.setdefault((res["name"], plat), []).append(st)
    stats = {}
    for key, sts in seq.items():
        stats[key] = {
            "breaks": sum(1 for a, b in zip(sts, sts[1:])
                          if a != "broken" and b == "broken"),
            "ambiguous": sum(1 for a, b in zip(sts, sts[1:])
                             if a != "ambiguous" and b == "ambiguous"),
            "current": sts[-1],
            "observations": len(sts),
        }
    return stats


def render(all_stats, date):
    lines = ["# Signature fragility", ""]
    if date:
        lines += ["Last updated: %s" % date, ""]
    lines += ["How often each signature has gone broken or ambiguous across "
              "the tracked history (each counted transition is one episode, "
              "not one run). Signatures with no episodes are summarised, not "
              "listed.", ""]

    fragile = [(pid, name, plat, s)
               for pid, stats in all_stats.items()
               for (name, plat), s in stats.items()
               if s["breaks"] or s["ambiguous"]]
    fragile.sort(key=lambda x: (-(x[3]["breaks"] + x[3]["ambiguous"]),
                                x[0], x[1]))
    if fragile:
        lines += ["## Most fragile", "",
                  "| Project | Signature | Platform | Breaks | Ambiguous | Now |",
                  "|---|---|---|---|---|---|"]
        for pid, name, plat, s in fragile[:20]:
            lines.append("| %s | `%s` | %s | %d | %d | %s |"
                         % (pid, name, plat, s["breaks"], s["ambiguous"],
                            s["current"]))
        lines.append("")
    else:
        lines += ["No breakage episodes recorded so far.", ""]

    lines += ["## Per project", ""]
    for pid, stats in all_stats.items():
        total = len(stats)
        episodes = sum(s["breaks"] + s["ambiguous"] for s in stats.values())
        clean = sum(1 for s in stats.values()
                    if not (s["breaks"] or s["ambiguous"]))
        obs = max((s["observations"] for s in stats.values()), default=0)
        lines.append("- **%s** - %d tracked sig/platform pairs, %d breakage "
                     "episode(s), %d never broken, %d snapshot(s) of history."
                     % (pid, total, episodes, clean, obs))
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects", default=P.REGISTRY)
    ap.add_argument("--out", default=os.path.join("docs", "stats.md"))
    ap.add_argument("--date", default=None, help="display timestamp")
    args = ap.parse_args()

    all_stats = {}
    for proj in P.load(args.projects):
        snaps = snapshots(P.status_path(proj))
        if snaps:
            all_stats[proj["id"]] = sig_stats(snaps)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as fh:
        fh.write(render(all_stats, args.date))
    print("wrote %s (%d project(s))" % (args.out, len(all_stats)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
