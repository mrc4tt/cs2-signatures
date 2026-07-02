#!/usr/bin/env python3
"""status.json -> README dashboard block + docs/CounterStrikeSharp.md + badge.

Presentation matches ianlucas/cs2-signatures:
  * README: summary table (Linux | Windows | Project | View signatures ->) plus
    a collapsible "broken signatures" list and SteamDB manifest links.
  * docs/CounterStrikeSharp.md: per-entry detail table with Status / Platform /
    Library / CODE-Style / IDA-Style.

The README dashboard is injected between the STATUS:START / STATUS:END markers
so the static header/badge/instructions are preserved.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from depots import DEPOTS, steamdb_link  # noqa: E402

FORK = "https://github.com/mrc4tt/CounterStrikeSharp"
GAMEDATA_URL = (FORK + "/blob/main/configs/addons/counterstrikesharp/"
                "gamedata/gamedata.json")
DOCS_REL = "docs/CounterStrikeSharp.md"

OK, WARN, BAD, GREY = "✅", "⚠️", "❌", "❔"
START, END = "<!-- STATUS:START -->", "<!-- STATUS:END -->"


def code_style(ida_sig):
    parts = []
    for tok in ida_sig.split():
        parts.append("\\x2A" if tok in ("?", "??", "2A") else "\\x%s" % tok.upper())
    return "".join(parts)


def emoji(status):
    return {"ok": OK, "ambiguous": WARN, "broken": BAD,
            "no_binary": GREY, "missing_sig": "➖"}.get(status, "?")


def platform_agg(results, plat):
    """Aggregate one platform's status across all signature entries."""
    seen = set()
    for r in results:
        if r["kind"] != "signature":
            continue
        info = r["platforms"].get(plat)
        if info:
            seen.add(info["status"])
    if "broken" in seen:
        return BAD
    if "ambiguous" in seen:
        return WARN
    if seen and seen <= {"ok"}:
        return OK
    if seen == {"missing_sig"} or not seen:
        return GREY
    # mix of ok + no_binary/missing -> not fully validated
    if "no_binary" in seen:
        return GREY
    return OK


def manifest_links(manifest):
    if not manifest:
        return "unknown"
    depots = set(str(d) for d in DEPOTS.values())
    parts = []
    for depot, mid in manifest.items():
        if str(depot) in depots:
            parts.append("[%s](%s)" % (mid, steamdb_link(depot, mid)))
    return ", ".join(parts) if parts else "unknown"


def broken_rows(results):
    rows = []
    for r in results:
        if r["kind"] != "signature":
            continue
        p = r["platforms"]
        lin = p.get("linux", {}).get("status")
        win = p.get("windows", {}).get("status")
        if lin == "broken" or win == "broken":
            rows.append((emoji(lin), emoji(win), r["name"]))
    return rows


def render_readme_block(status, updated):
    results = status["results"]
    lin = platform_agg(results, "linux")
    win = platform_agg(results, "windows")
    t = status["tally"]
    L = []
    L.append("## Signatures")
    L.append("")
    L.append("* **Last updated:** %s" % updated)
    L.append("* **Manifests:** %s" % manifest_links(status.get("manifest")))
    L.append("* **Validated:** %d ok, %d ambiguous, %d broken (%d offset-only, "
             "%d not-yet-validated)" % (t.get("ok", 0), t.get("ambiguous", 0),
             t.get("broken", 0), t.get("offset_only", 0), t.get("no_binary", 0)))
    L.append("")
    L.append("<table>")
    L.append("<tr><th>Linux</th><th>Windows</th><th>Project</th><th></th></tr>")
    L.append('<tr><td>%s</td><td>%s</td>'
             '<td><a href="%s">CounterStrikeSharp</a></td>'
             '<td><a href="%s">View signatures &rarr;</a></td></tr>'
             % (lin, win, FORK, DOCS_REL))
    L.append("</table>")
    L.append("")

    brk = broken_rows(results)
    if brk:
        L.append("<details open><summary>&#9660; CounterStrikeSharp broken "
                 "signatures (%d)</summary>" % len(brk))
        L.append("")
        L.append("<table>")
        L.append("<tr><th>Linux</th><th>Windows</th><th>Subroutine</th></tr>")
        for le, we, name in brk:
            L.append("<tr><td>%s</td><td>%s</td><td>%s</td></tr>"
                     % (le, we, name))
        L.append("</table>")
        L.append("</details>")
        L.append("")
    return "\n".join(L)


def render_docs(status, updated):
    L = []
    L.append("# CounterStrikeSharp")
    L.append("")
    L.append("Last updated: %s" % updated)
    L.append("")
    L.append("* Manifests: %s" % manifest_links(status.get("manifest")))
    L.append("* Repository: %s" % FORK)
    L.append("* Gamedata: %s" % GAMEDATA_URL)
    L.append("")
    L.append("Cell status: %s unique (1 match) &middot; %s ambiguous (>1) "
             "&middot; %s broken (0) &middot; %s binary not downloaded."
             % (OK, WARN, BAD, GREY))
    L.append("")
    L.append("## Signatures")
    L.append("")
    for r in status["results"]:
        if r["kind"] == "offset_only":
            L.append("### %s" % r["name"])
            L.append("")
            L.append("_Offset-only entry (vtable slot) — not byte-validated._")
            L.append("")
            continue
        if r["kind"] != "signature":
            continue
        L.append("### %s" % r["name"])
        L.append("")
        L.append("<table>")
        L.append("<tr><th>Status</th><th>Platform</th><th>Library</th>"
                 "<th>Matches</th><th>CODE-Style</th><th>IDA-Style</th></tr>")
        for plat, disp in (("windows", "Windows"), ("linux", "Linux")):
            info = r["platforms"].get(plat, {})
            sig = info.get("sig")
            if not sig:
                continue
            m = info.get("matches")
            L.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td>"
                     "<td>\n<pre>\n%s\n</pre>\n</td><td>\n<pre>\n%s\n</pre>\n</td></tr>"
                     % (emoji(info.get("status")), disp,
                        info.get("library", "server"),
                        "-" if m is None else str(m),
                        code_style(sig), sig))
        L.append("</table>")
        L.append("")
    return "\n".join(L)


def inject_readme(readme_path, block):
    with open(readme_path) as fh:
        text = fh.read()
    if START in text and END in text:
        pre = text.split(START)[0]
        post = text.split(END, 1)[1]
        text = pre + START + "\n" + block + "\n" + END + post
    else:
        text = text.rstrip() + "\n\n" + START + "\n" + block + "\n" + END + "\n"
    with open(readme_path, "w") as fh:
        fh.write(text)


def make_badge(t):
    ok, brk, amb = t.get("ok", 0), t.get("broken", 0), t.get("ambiguous", 0)
    if ok + brk + amb == 0:
        msg, color = "not validated", "lightgrey"
    elif brk:
        msg, color = "%d broken / %d ok" % (brk, ok), "red"
    elif amb:
        msg, color = "%d ambiguous / %d ok" % (amb, ok), "yellow"
    else:
        msg, color = "%d ok" % ok, "brightgreen"
    return {"schemaVersion": 1, "label": "cs2 sigs", "message": msg,
            "color": color}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", default="reports/status.json")
    ap.add_argument("--readme", default="README.md")
    ap.add_argument("--docs", default="docs/CounterStrikeSharp.md")
    ap.add_argument("--badge", default="reports/badge.json")
    ap.add_argument("--history-dir", default="reports/history")
    ap.add_argument("--date", required=True, help="display date e.g. 'July 2, 2026'")
    ap.add_argument("--iso", required=True, help="YYYY-MM-DD for history filename")
    args = ap.parse_args()

    with open(args.status) as fh:
        status = json.load(fh)

    inject_readme(args.readme, render_readme_block(status, args.date))

    os.makedirs(os.path.dirname(args.docs) or ".", exist_ok=True)
    with open(args.docs, "w") as fh:
        fh.write(render_docs(status, args.date))

    os.makedirs(os.path.dirname(args.badge) or ".", exist_ok=True)
    with open(args.badge, "w") as fh:
        json.dump(make_badge(status["tally"]), fh, indent=2)

    os.makedirs(args.history_dir, exist_ok=True)
    snap = os.path.join(args.history_dir, "%s.json" % args.iso)
    with open(snap, "w") as fh:
        json.dump({"date": args.date, "tally": status["tally"],
                   "manifest": status.get("manifest")}, fh, indent=2)

    print("updated %s, %s, %s" % (args.readme, args.docs, args.badge))


if __name__ == "__main__":
    main()
