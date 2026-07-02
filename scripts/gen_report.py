#!/usr/bin/env python3
"""status.json -> STATUS.md dashboard + dated history snapshot.

Traffic-light table per ianlucas/cs2-signatures:
    ok        -> :white_check_mark:
    ambiguous -> :warning:
    broken    -> :x:
    no_binary -> :grey_question:
    offset    -> :arrows_counterclockwise:  (vtable slot, not byte-validated)
"""
import argparse
import json
import os

EMOJI = {
    "ok": ":white_check_mark:",
    "ambiguous": ":warning:",
    "broken": ":x:",
    "no_binary": ":grey_question:",
    "missing_sig": ":heavy_minus_sign:",
}


def cell(info):
    if info is None:
        return ""
    st = info["status"]
    e = EMOJI.get(st, "?")
    m = info.get("matches")
    if st in ("ok", "ambiguous", "broken") and m is not None:
        return "%s %d" % (e, m)
    return e


def render_md(status, updated):
    t = status["tally"]
    lines = []
    lines.append("# CS2 Signature Tracker")
    lines.append("")
    lines.append("Auto-validated signatures from "
                 "[mrc4tt/CounterStrikeSharp](https://github.com/mrc4tt/"
                 "CounterStrikeSharp/blob/main/configs/addons/"
                 "counterstrikesharp/gamedata/gamedata.json).")
    lines.append("")
    lines.append("- **Updated:** %s" % updated)
    lines.append("- **Manifest:** `%s`" % (status.get("manifest") or "unknown"))
    lines.append("")
    lines.append("| status | count |")
    lines.append("|---|---|")
    lines.append("| :white_check_mark: ok | %d |" % t.get("ok", 0))
    lines.append("| :warning: ambiguous | %d |" % t.get("ambiguous", 0))
    lines.append("| :x: broken | %d |" % t.get("broken", 0))
    lines.append("| :grey_question: no binary | %d |" % t.get("no_binary", 0))
    lines.append("| :arrows_counterclockwise: offset-only | %d |"
                 % t.get("offset_only", 0))
    lines.append("")
    lines.append("Cell value = match count. `1` = unique+healthy, "
                 "`0` = :x: gone, `>1` = :warning: not unique.")
    lines.append("")
    lines.append("| entry | linux | windows |")
    lines.append("|---|---|---|")
    for r in status["results"]:
        if r["kind"] == "offset_only":
            lines.append("| `%s` | :arrows_counterclockwise: offset | "
                         ":arrows_counterclockwise: offset |" % r["name"])
            continue
        p = r.get("platforms", {})
        lines.append("| `%s` | %s | %s |" % (
            r["name"], cell(p.get("linux")), cell(p.get("windows"))))
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", default="reports/status.json")
    ap.add_argument("--out", default="reports/STATUS.md")
    ap.add_argument("--history-dir", default="reports/history")
    # Date is passed in (CI provides it) so the script stays deterministic.
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    args = ap.parse_args()

    with open(args.status) as fh:
        status = json.load(fh)

    md = render_md(status, args.date)
    with open(args.out, "w") as fh:
        fh.write(md)

    os.makedirs(args.history_dir, exist_ok=True)
    snap = os.path.join(args.history_dir, "%s.json" % args.date)
    with open(snap, "w") as fh:
        json.dump({"date": args.date, "tally": status["tally"],
                   "manifest": status.get("manifest")}, fh, indent=2)

    # shields.io endpoint badge (https://shields.io/endpoint).
    badge_path = os.path.join(os.path.dirname(args.out) or ".", "badge.json")
    with open(badge_path, "w") as fh:
        json.dump(make_badge(status["tally"]), fh, indent=2)

    print("wrote %s, %s, %s" % (args.out, snap, badge_path))


def make_badge(t):
    ok, brk, amb = t.get("ok", 0), t.get("broken", 0), t.get("ambiguous", 0)
    validated = ok + brk + amb
    if validated == 0:
        msg, color = "not validated", "lightgrey"
    elif brk:
        msg, color = "%d broken / %d ok" % (brk, ok), "red"
    elif amb:
        msg, color = "%d ambiguous / %d ok" % (amb, ok), "yellow"
    else:
        msg, color = "%d ok" % ok, "brightgreen"
    return {"schemaVersion": 1, "label": "cs2 sigs", "message": msg,
            "color": color}


if __name__ == "__main__":
    main()
