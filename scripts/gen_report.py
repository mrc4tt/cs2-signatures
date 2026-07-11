#!/usr/bin/env python3
"""Per-project status.json -> README dashboard + docs/<id>.md + aggregate badge.

Reads data/projects.json and each project's reports/<id>/status.json, then:
  * README: one summary-table row per project (Linux | Windows | Project |
    View signatures ->), a collapsible broken/ambiguous list per project, and
    the shared SteamDB manifest links.
  * docs/<id>.md: per-entry detail table (Status / Platform / Library /
    CODE-Style / IDA-Style) for that project.
  * reports/badge.json: aggregate verdict across all projects.
  * reports/history/<iso>.json: aggregate tally + per-project breakdown.

The README dashboard is injected between the STATUS:START / STATUS:END markers
so the static header/badge/instructions are preserved.
"""
import argparse
import json
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from depots import DEPOTS, steamdb_link  # noqa: E402
import projects as P  # noqa: E402

DOCS_URL_TMPL = ("https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/"
                 "docs/%s.md")
# Raw badge.json served by Forgejo -> wrapped by shields.io's endpoint badge.
BADGE_RAW_TMPL = ("https://git.miksen.me/mikkel/cs2-signatures/raw/branch/main/"
                  "reports/%s/badge.json")


def badge_md(project_id, alt):
    """shields.io endpoint badge <img> for a project's badge.json. HTML (not
    markdown ![]) so it renders reliably inside the HTML status table."""
    raw = BADGE_RAW_TMPL % project_id
    return ('<img src="https://img.shields.io/endpoint?url=%s" alt="%s">'
            % (urllib.parse.quote(raw, safe=""), alt))

OK, WARN, BAD, GREY = "✅", "⚠️", "❌", "❔"
START, END = "<!-- STATUS:START -->", "<!-- STATUS:END -->"


def docs_url(proj):
    return DOCS_URL_TMPL % proj["id"]


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


def issue_rows(results):
    """Entries where either platform is broken or ambiguous."""
    bad = ("broken", "ambiguous")
    rows = []
    for r in results:
        if r["kind"] != "signature":
            continue
        p = r["platforms"]
        lin = p.get("linux", {}).get("status")
        win = p.get("windows", {}).get("status")
        if lin in bad or win in bad:
            rows.append((emoji(lin), emoji(win), r["name"]))
    return rows


def sum_tallies(statuses):
    total = {}
    for s in statuses:
        for k, v in s.get("tally", {}).items():
            total[k] = total.get(k, 0) + v
    return total


def render_readme_block(projects, statuses, updated):
    """projects/statuses are parallel lists (same order)."""
    manifest = next((s.get("manifest") for s in statuses if s.get("manifest")),
                    None)
    t = sum_tallies(statuses)
    L = []
    L.append("## Signatures")
    L.append("")
    L.append("* **Last updated:** %s" % updated)
    L.append("* **Manifests:** %s" % manifest_links(manifest))
    L.append("* **Tracked projects:** %d" % len(projects))
    L.append("* **Validated:** %d ok, %d ambiguous, %d broken (%d not-yet-"
             "validated)" % (t.get("ok", 0), t.get("ambiguous", 0),
             t.get("broken", 0), t.get("no_binary", 0)))
    L.append("")
    L.append("<table>")
    L.append("<tr><th>Status</th><th>Linux</th><th>Windows</th><th>Project</th>"
             "<th></th></tr>")
    for proj, status in zip(projects, statuses):
        results = status["results"]
        lin = platform_agg(results, "linux")
        win = platform_agg(results, "windows")
        L.append('<tr><td>%s</td><td>%s</td><td>%s</td>'
                 '<td><a href="%s">%s</a></td>'
                 '<td><a href="%s">View signatures &rarr;</a></td></tr>'
                 % (badge_md(proj["id"], P.name(proj)), lin, win,
                    P.repo_url(proj), P.name(proj), docs_url(proj)))
    L.append("</table>")
    L.append("")

    for proj, status in zip(projects, statuses):
        rows = issue_rows(status["results"])
        if not rows:
            continue
        L.append("<details open><summary>&#9660; %s broken / ambiguous "
                 "signatures (%d)</summary>" % (P.name(proj), len(rows)))
        L.append("")
        L.append("<table>")
        L.append("<tr><th>Linux</th><th>Windows</th><th>Subroutine</th></tr>")
        for le, we, name in rows:
            L.append("<tr><td>%s</td><td>%s</td><td>%s</td></tr>"
                     % (le, we, name))
        L.append("</table>")
        L.append("</details>")
        L.append("")
    return "\n".join(L)


def render_docs(proj, status, updated):
    L = []
    L.append("# %s" % P.name(proj))
    L.append("")
    L.append("Last updated: %s" % updated)
    L.append("")
    L.append("* Manifests: %s" % manifest_links(status.get("manifest")))
    L.append("* Repository: %s" % P.repo_url(proj))
    L.append("* Gamedata: %s" % P.blob_url(proj))
    L.append("")
    L.append("Cell status: %s unique (1 match) &middot; %s ambiguous (>1) "
             "&middot; %s broken (0) &middot; %s binary not downloaded."
             % (OK, WARN, BAD, GREY))
    L.append("")
    L.append("## Signatures")
    L.append("")
    for r in status["results"]:
        # Offsets are not tracked here — signatures only.
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
    ap.add_argument("--projects", default=P.REGISTRY)
    ap.add_argument("--readme", default="README.md")
    ap.add_argument("--docs-dir", default="docs")
    ap.add_argument("--badge", default="reports/badge.json")
    ap.add_argument("--history-dir", default="reports/history")
    ap.add_argument("--date", required=True, help="display date e.g. 'July 2, 2026'")
    ap.add_argument("--iso", required=True, help="YYYY-MM-DD for history filename")
    args = ap.parse_args()

    projects = P.load(args.projects)
    statuses = []
    for proj in projects:
        with open(P.status_path(proj)) as fh:
            statuses.append(json.load(fh))

    inject_readme(args.readme, render_readme_block(projects, statuses, args.date))

    os.makedirs(args.docs_dir, exist_ok=True)
    for proj, status in zip(projects, statuses):
        with open(os.path.join(args.docs_dir, "%s.md" % proj["id"]), "w") as fh:
            fh.write(render_docs(proj, status, args.date))

    total = sum_tallies(statuses)
    os.makedirs(os.path.dirname(args.badge) or ".", exist_ok=True)
    with open(args.badge, "w") as fh:
        json.dump(make_badge(total), fh, indent=2)

    # Per-project badge (reports/<id>/badge.json) for the README table.
    for proj, status in zip(projects, statuses):
        b = make_badge(status["tally"])
        b["label"] = P.name(proj)
        path = os.path.join("reports", proj["id"], "badge.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            json.dump(b, fh, indent=2)

    manifest = next((s.get("manifest") for s in statuses if s.get("manifest")),
                    None)
    os.makedirs(args.history_dir, exist_ok=True)
    snap = os.path.join(args.history_dir, "%s.json" % args.iso)
    with open(snap, "w") as fh:
        json.dump({"date": args.date, "tally": total, "manifest": manifest,
                   "projects": {p["id"]: s["tally"]
                                for p, s in zip(projects, statuses)}}, fh, indent=2)

    print("updated %s, %s/*.md, %s" % (args.readme, args.docs_dir, args.badge))


if __name__ == "__main__":
    main()
