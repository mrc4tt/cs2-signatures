#!/usr/bin/env python3
"""Which tracked symbols the reference analysis cannot answer for.

`validate_sigs.py` already records, per entry per platform, what the
CS2_VibeSignatures snapshot had to say. This collects the places where it had
nothing to say about a symbol we actually track, so the gap can be handed back
to the analysis instead of sitting unread in a status.json.

Three categories, worst first:

  no_verdict       an offset with neither a working recipe nor a reference.
                   Nothing checks that value: it is copied from the gamedata
                   and trusted. The real blind spot.
  missing_symbol   a signature whose symbol is absent from the snapshot. The
                   scan still says ok/broken, but nothing can say whether the
                   pattern is still the one upstream uses.
  missing_pattern  the symbol was analysed, but the record carries no byte
                   pattern, so there is nothing to compare against.

Only symbols in data/projects.json are reported - a snapshot covers thousands
of symbols nobody here tracks, and a request list has to be short to be acted
on.

    python3 scripts/reference_gaps.py                 # summary to stdout
    python3 scripts/reference_gaps.py --markdown      # issue body
    python3 scripts/reference_gaps.py --out reports/reference_gaps.json

stdlib only.
"""
import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import projects as P  # noqa: E402

ALIASES = os.path.join("data", "symbol_aliases.json")

# Worst first: an unverifiable value outranks an unverifiable pattern, since
# the scan still covers the pattern and nothing covers the value.
CATEGORIES = ("no_verdict", "missing_symbol", "missing_pattern")
TITLES = {
    "no_verdict": "Offsets with no verdict from either route",
    "missing_symbol": "Signatures whose symbol is not in the snapshot",
    "missing_pattern": "Symbols analysed without a byte pattern",
}
BLURBS = {
    "no_verdict": ("Neither an anchor/recipe nor the reference can produce a "
                   "value for these, so the number in the gamedata is taken on "
                   "trust. A reference record - vtable index, struct member, or "
                   "an anchor pattern spanning the access - would close it."),
    "missing_symbol": ("These signatures resolve in the binaries, but the "
                       "snapshot has no record under this name, so nothing can "
                       "say whether the pattern is still the one the analysis "
                       "uses."),
    "missing_pattern": ("The symbol is in the snapshot but its record carries "
                        "no byte pattern, so there is nothing to compare the "
                        "tracked signature against."),
}


def load_aliases(path):
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def classify(kind, status, ref_status):
    """Gap category for one platform block, or None when it is covered."""
    if kind == "offset":
        # A recipe or anchor answered, or the reference did: not a gap.
        if status not in ("no_recipe", "review"):
            return None
        return "no_verdict" if ref_status in (None, "no_reference") else None
    if ref_status == "no_reference":
        return "missing_symbol"
    if ref_status == "no_sig":
        return "missing_pattern"
    return None


def collect(projects_path=P.REGISTRY, aliases_path=ALIASES):
    """[{symbol, kind, category, platforms, projects, reasons, values, alias}]

    One entry per symbol, merging the platforms and the projects that use it -
    the same symbol missing on both platforms in three plugins is one piece of
    analysis work, not six.
    """
    aliases = load_aliases(aliases_path)
    gaps, reference = {}, None
    for proj in P.load(projects_path):
        path = P.status_path(proj)
        if not os.path.isfile(path):
            continue
        try:
            with open(path) as fh:
                status = json.load(fh)
        except (OSError, ValueError):
            continue
        reference = reference or status.get("reference")
        for r in status.get("results", []):
            kind = r.get("kind")
            offsets = r.get("offsets") or {}
            for plat, info in sorted((r.get("platforms") or {}).items()):
                ref = info.get("reference") or {}
                cat = classify(kind, info.get("status"), ref.get("status"))
                if not cat:
                    continue
                g = gaps.setdefault((r["name"], kind), {
                    "symbol": r["name"], "kind": kind, "category": cat,
                    "platforms": [], "projects": [], "reasons": {},
                    "values": {}, "alias": aliases.get(r["name"])})
                # Worst category wins when the platforms disagree.
                if CATEGORIES.index(cat) < CATEGORIES.index(g["category"]):
                    g["category"] = cat
                if plat not in g["platforms"]:
                    g["platforms"].append(plat)
                if proj["id"] not in g["projects"]:
                    g["projects"].append(proj["id"])
                reason = ref.get("reason") or info.get("reason")
                if reason:
                    g["reasons"][plat] = reason
                value = offsets.get(plat, info.get(plat))
                if kind == "offset" and value is not None:
                    g["values"][plat] = value
    out = sorted(gaps.values(),
                 key=lambda g: (CATEGORIES.index(g["category"]), g["symbol"]))
    return {"reference": reference, "gaps": out}


def fingerprint(report):
    """Hash of the gap set alone.

    Excludes the snapshot version on purpose: a new game version with the same
    holes is not new information, and re-posting it would train everyone to
    ignore the issue.
    """
    items = [(g["symbol"], g["kind"], g["category"],
              tuple(sorted(g["platforms"])), tuple(sorted(g["projects"])))
             for g in report["gaps"]]
    raw = json.dumps(sorted(items), separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def render_markdown(report, repo_url=None):
    """Issue body: what is missing, for whom, and what would close it."""
    gaps = report["gaps"]
    L = ["Symbols tracked by the signature tracker that the analysis cannot "
         "currently answer for."]
    if report.get("reference"):
        L.append("")
        L.append("Snapshot: `%s`. Tracker: %s"
                 % (report["reference"], repo_url or "cs2-signatures"))
    if not gaps:
        L += ["", "Nothing outstanding - every tracked symbol has a reference "
                  "verdict."]
        return "\n".join(L) + "\n"

    for cat in CATEGORIES:
        rows = [g for g in gaps if g["category"] == cat]
        if not rows:
            continue
        L += ["", "## %s (%d)" % (TITLES[cat], len(rows)), "", BLURBS[cat], ""]
        value_col = cat == "no_verdict"
        header = "| Symbol | Platforms | Used by |"
        rule = "|---|---|---|"
        if value_col:
            header += " Value in gamedata | Reason |"
            rule += "---|---|"
        L += [header, rule]
        for g in rows:
            line = "| `%s` | %s | %s |" % (
                g["symbol"], ", ".join(g["platforms"]),
                ", ".join(g["projects"]))
            if value_col:
                vals = ", ".join("%s `%s`" % (p, v)
                                 for p, v in sorted(g["values"].items()))
                reasons = ", ".join(sorted(set(g["reasons"].values())))
                line += " %s | %s |" % (vals or "-", reasons or "-")
            L.append(line)

    aliased = [g for g in gaps if g["alias"]]
    if aliased:
        L += ["", "Looked up under an alias, in case the analysis files these "
                  "under a different name:", ""]
        for g in aliased:
            L.append("* `%s` -> `%s`" % (g["symbol"], g["alias"]))

    L += ["", "Generated from the tracker's own reports; it updates itself as "
              "symbols get covered."]
    return "\n".join(L) + "\n"


def write_page(report, path, date=None):
    """docs page with the same content as the issue body, rewritten every run.

    Replaces the GitHub issue as the place to look: a page in this repo is
    current after every run, while the issue flipped open and closed whenever
    the gap set moved - including every time the reference snapshot could not be
    resolved, which made every offset look like a gap.
    """
    L = ["# Reference coverage gaps", ""]
    if date:
        L += ["Last updated: %s" % date, ""]
    body = render_markdown(report, "https://github.com/mrc4tt/cs2-signatures")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as fh:
        fh.write("\n".join(L) + "\n" + body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects", default=P.REGISTRY)
    ap.add_argument("--aliases", default=ALIASES)
    ap.add_argument("--out", default=None,
                    help="write the machine-readable report to PATH")
    ap.add_argument("--markdown", action="store_true",
                    help="print the issue body instead of a summary")
    ap.add_argument("--page", default=None,
                    help="write the report as a docs page to PATH (run_all.sh "
                         "does this every run, so the page is always current)")
    ap.add_argument("--date", default=None, help="'Last updated' for --page")
    args = ap.parse_args()

    report = collect(args.projects, args.aliases)
    report["fingerprint"] = fingerprint(report)

    if args.out:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w") as fh:
            json.dump(report, fh, indent=2)

    if args.page:
        write_page(report, args.page, args.date)

    if args.markdown:
        print(render_markdown(report), end="")
        return 0

    if not report["gaps"]:
        print("no reference gaps across tracked symbols")
        return 0
    for cat in CATEGORIES:
        rows = [g for g in report["gaps"] if g["category"] == cat]
        if rows:
            print("%s (%d):" % (cat, len(rows)))
            for g in rows:
                print("  %-52s %s  [%s]" % (g["symbol"],
                                            ",".join(g["platforms"]),
                                            ",".join(g["projects"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
