#!/usr/bin/env python3
"""Post CS2 signature reports to a Discord webhook.

Default layout is delta-first: one embed that answers "what changed" rather
than "what exists". A healthy run is a verdict line, a per-project health bar
and the changes since the previous report - not 60 identical green rows. The
full per-signature listing lives in docs/<project>.md, which the embed links,
and is still available here with --full.

    🟢 valid (1 match)   🔴 failed (0)   🟡 multi-match (>1)   ⚪ not validated

The embed grows on demand: broken and ambiguous entries are listed in full,
healthy ones are counted. The colour and an optional @mention escalate on any
breakage.

Inputs beyond the statuses, all optional decoration - a missing one only costs
that section:

    reports/delta.json      named per-entry delta vs the previous report,
                            written by post_gate.py --write-delta (run_all.sh
                            step 5.5, before the commit moves HEAD). Recomputed
                            live when absent or stale.
    reports/fragility.json  per-signature breakage counts from gen_stats.py
                            --json; marks habitual breakers with 🔥.
    reports/history/*.json  previous CS2 version, for the `old -> new` line on
                            a game update.

Auth: webhook URL via env DISCORD_WEBHOOK (or --webhook). Never hard-code it.
Several URLs may be given - comma- or whitespace-separated in the env var, or
by repeating --webhook - to mirror the same report into more than one server.
A numeric DISCORD_MENTION is a global user id, so one value pings correctly in
every server; a role id would not (role ids are per-guild).

Preview: --preview prints the JSON payload without sending. Add --example for
synthetic data - also usable as a live test post (send without --preview) to
see the layout in Discord before a real breakage happens.

stdlib only (urllib).
"""
import argparse
import datetime
import json
import os
import re
import sys
import subprocess
import urllib.error
import urllib.request
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import projects as P  # noqa: E402

# Embed colour (decimal). Green healthy, yellow ambiguous, red broken.
COLOR_OK = 0x2ECC71
COLOR_WARN = 0xF1C40F
COLOR_BAD = 0xE74C3C

STEAMDB = "https://steamdb.info/depot/%s/history/?changeid=M:%s"
REPO_URL = "https://git.miksen.me/mikkel/cs2-signatures"
DOCS_URL = REPO_URL + "/src/branch/main/docs/%s.md"
STATS_URL = REPO_URL + "/src/branch/main/docs/stats.md"

# A signature that has broken this many times before is worth a warning even
# while it is currently healthy.
FRAGILE_BREAKS = 2

# Per change kind: the marker shown in the "Changes" field.
CHANGE_ICON = {"broke": "\U0001F534", "fixed": "\U0001F7E2",
               "changed": "\U0001F7E1",
               "added": "\u2795", "removed": "\u2796",
               "resigned": "\U0001F501", "moved": "\U0001F4CF"}
# Kinds whose row reads better as a label than as an `old -> new` transition.
CHANGE_LABEL = {"added": "added", "removed": "removed",
                "resigned": "re-signed", "moved": "offset moved"}
# Kinds counted in the headline "N fixed / N broke" line.
HEADLINE = ("broke", "fixed")

CIRCLE = {"ok": "\U0001F7E2", "broken": "\U0001F534", "ambiguous": "\U0001F7E1"}
UNTRACKED = "⚪"
LEGEND = "\U0001F7E2 Valid | \U0001F534 Failed | \U0001F7E1 Multi-match | ⚪ Untracked"

# Discord hard limits we stay under.
DESC_MAX = 4000        # embed description (spec 4096)
EMBEDS_PER_MSG = 10    # embeds per webhook message


def circle(status):
    return CIRCLE.get(status, UNTRACKED)


def load_statuses(projects_path, status_override=None):
    """[(project_id, status_dict), ...] across all tracked projects."""
    if status_override:
        with open(status_override) as fh:
            s = json.load(fh)
        return [(s.get("project", "project"), s)]
    out = []
    for proj in P.load(projects_path):
        path = P.status_path(proj)
        if os.path.isfile(path):
            with open(path) as fh:
                out.append((proj["id"], json.load(fh)))
    return out


def sig_entries(status):
    return [r for r in status.get("results", []) if r.get("kind") == "signature"]


def is_problem(r):
    return any(r["platforms"].get(p, {}).get("status") in ("broken", "ambiguous")
               for p in ("windows", "linux"))


def issue_list(statuses):
    """(project, name, platform, status) for every broken/ambiguous entry -
    used only to decide whether to @mention."""
    out = []
    for pid, status in statuses:
        for r in status.get("results", []):
            for plat, info in r.get("platforms", {}).items():
                if info.get("status") in ("broken", "ambiguous"):
                    out.append((pid, r["name"], plat, info["status"]))
    return out


def platform_counts(entries):
    """{'windows': [ok, validated], 'linux': [ok, validated]}."""
    c = {"windows": [0, 0], "linux": [0, 0]}
    for r in entries:
        for plat in ("windows", "linux"):
            st = r["platforms"].get(plat, {}).get("status")
            if st in ("ok", "broken", "ambiguous"):
                c[plat][1] += 1
                if st == "ok":
                    c[plat][0] += 1
    return c


def manifest_links(manifest):
    if not manifest:
        return None
    return " ".join("[`%s`](%s)" % (mid, STEAMDB % (depot, mid))
                    for depot, mid in sorted(manifest.items()))


def read_version(steam_inf, override=None):
    if override:
        return override
    if steam_inf and os.path.isfile(steam_inf):
        with open(steam_inf, errors="ignore") as fh:
            m = re.search(r"PatchVersion=(\S+)", fh.read())
            if m:
                return m.group(1)
    return None


def name_width(statuses, minimum=16):
    """Widest signature name across all projects, so every row's name box is the
    same width and the rows read as full, aligned lines (not ragged)."""
    widest = minimum
    for _, status in statuses:
        for r in sig_entries(status):
            widest = max(widest, len(r["name"]))
    return widest


def sig_rows(entries, width):
    """Padded, status-sorted `name` W/L lines. Problems first, then A→Z."""
    entries = sorted(entries, key=lambda r: (not is_problem(r), r["name"]))
    rows = []
    for r in entries:
        w = circle(r["platforms"].get("windows", {}).get("status"))
        lin = circle(r["platforms"].get("linux", {}).get("status"))
        rows.append("`%s`  W %s | L %s" % (r["name"].ljust(width), w, lin))
    return rows


def clamp_desc(rows):
    """Join rows under the description limit, noting any dropped tail."""
    out, used = [], 0
    for i, row in enumerate(rows):
        if used + len(row) + 1 > DESC_MAX:
            out.append("…and %d more" % (len(rows) - i))
            break
        out.append(row)
        used += len(row) + 1
    return "\n".join(out) if out else "_no signature entries_"


def bar(ok, total, n=10):
    """Unicode progress bar, e.g. ████████░░."""
    if total <= 0:
        return "─" * n
    filled = round(ok / total * n)
    return "█" * filled + "░" * (n - filled)


def load_proposal_keys(projects_path):
    """{(project_id, name, platform), ...} of broken sigs that have a
    replacement candidate in proposals.json (written by propose_sigs.py)."""
    out = set()
    try:
        projects = P.load(projects_path)
    except Exception:  # noqa: BLE001 - proposals are optional decoration
        return out
    for proj in projects:
        path = P.proposals_path(proj)
        if not os.path.isfile(path):
            continue
        try:
            with open(path) as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            continue
        for pr in data.get("proposals", []):
            if pr.get("candidate"):
                out.add((proj["id"], pr["name"], pr["platform"]))
    return out


def sum_tallies(statuses):
    t = {}
    for _, s in statuses:
        for k, v in s.get("tally", {}).items():
            t[k] = t.get(k, 0) + v
    return t


def load_fragility(path):
    """{(project, name, platform)} of signatures that have broken repeatedly.

    From gen_stats.py --json. Purely advisory: a healthy signature with a bad
    track record still gets a 🔥 so a reader knows where to look first.
    """
    out = set()
    if not path or not os.path.isfile(path):
        return out
    try:
        with open(path) as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return out
    for pid, entries in data.items():
        for key, stat in entries.items():
            name, _, plat = key.rpartition("|")
            if stat.get("breaks", 0) >= FRAGILE_BREAKS:
                out.add((pid, name, plat))
    return out


def delta_is_fresh(path, projects_path):
    """True if the delta file is at least as new as every status.json.

    run_all.sh writes it moments before posting, so it is fresh on a pipeline
    run. A hand-run `--preview` days later would otherwise render a delta from
    some earlier run as if it were this one's news.
    """
    try:
        newest = max(os.path.getmtime(P.status_path(proj))
                     for proj in P.load(projects_path)
                     if os.path.isfile(P.status_path(proj)))
    except (OSError, ValueError):
        return True
    return os.path.getmtime(path) >= newest


def load_delta(path, projects_path):
    """[{project, name, platform, change, old, new}, ...] since the last report.

    Prefers the file written by post_gate.py: by the time this script runs,
    run_all.sh has already committed, so HEAD is the CURRENT state and the diff
    is no longer computable here. Falls back to computing it live, which is
    what a manual pre-commit `--preview` wants.

    Change kinds this script has no icon for are dropped rather than rendered
    as a bullet with an `ok -> ok` transition: a retired kind left over in a
    stale delta.json would otherwise show up as a change that says nothing.
    """
    changes = None
    if path and os.path.isfile(path) and delta_is_fresh(path, projects_path):
        try:
            with open(path) as fh:
                changes = json.load(fh).get("changes", [])
        except (OSError, ValueError):
            changes = None
    if changes is None:
        try:
            import post_gate  # same directory; stdlib + git only
            changes = post_gate.named_changes(projects_path)
        except Exception:  # noqa: BLE001 - the delta is decoration, never fatal
            return []
    return [c for c in changes if c.get("change") in CHANGE_ICON]


def prev_version(history_dir, current):
    """The CS2 version of the newest history snapshot that is not `current`.

    gen_report.py stamps each snapshot with the version it validated, so the
    most recent differing one is the build we were on before this run.
    """
    if not current or not history_dir or not os.path.isdir(history_dir):
        return None
    for name in sorted(os.listdir(history_dir), reverse=True):
        if not name.endswith(".json"):
            continue
        try:
            with open(os.path.join(history_dir, name)) as fh:
                ver = json.load(fh).get("version")
        except (OSError, ValueError):
            continue
        if ver and ver != current:
            return ver
    return None


def commit_link():
    """Link to the commit this report describes, or None outside a checkout.

    run_all.sh commits in step 6 and posts in step 8, so HEAD is exactly the
    run being reported - one click from the post to the changed status.json.
    """
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=P.ROOT,
                             capture_output=True, check=True,
                             text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    return "%s/commit/%s" % (REPO_URL, sha) if sha else None


def clamp_rows(rows, limit=1024):
    """Join rows under a field-value limit, noting any dropped tail."""
    out, used = [], 0
    for i, row in enumerate(rows):
        tail = "…and %d more" % (len(rows) - i)
        if used + len(row) + 1 > limit - len(tail) - 1:
            out.append(tail)
            break
        out.append(row)
        used += len(row) + 1
    return "\n".join(out)


def change_row(c, multi, frag):
    """One line in the Changes field."""
    bits = ["%s `%s`" % (CHANGE_ICON.get(c["change"], "•"), c["name"])]
    if (c["project"], c["name"], c["platform"]) in frag:
        bits[0] += " 🔥"
    if multi:
        bits.append(c["project"])
    bits.append(c["platform"])
    if c["change"] in CHANGE_LABEL:
        bits.append(CHANGE_LABEL[c["change"]])
    else:
        bits.append("%s → %s" % (c.get("old") or "?", c.get("new") or "?"))
    return " · ".join(bits)


def delta_headline(changes):
    """"2 fixed · 1 new break · 3 re-signed", or None when nothing moved."""
    counts = {}
    for c in changes:
        counts[c["change"]] = counts.get(c["change"], 0) + 1
    words = {"broke": "new break", "fixed": "fixed", "changed": "changed",
             "added": "added", "removed": "removed",
             "resigned": "re-signed", "moved": "offset moved"}
    parts = []
    for kind in CHANGE_ICON:
        n = counts.get(kind, 0)
        if not n:
            continue
        word = words[kind]
        parts.append("**%d** %s%s" % (n, word,
                                      "s" if n > 1 and word.endswith("break")
                                      else ""))
    return " · ".join(parts) or None


def project_lines(statuses, projects_path):
    """One health line per project: verdict dot, link, bar, per-platform count."""
    out = []
    for pid, status in statuses:
        c = platform_counts(sig_entries(status))
        pok = c["windows"][0] + c["linux"][0]
        ptot = c["windows"][1] + c["linux"][1]
        out.append("%s [**%s**](%s)\n`%s` %d/%d  ·  W %d/%d · L %d/%d"
                   % (verdict_dot(status.get("tally", {})),
                      display_name(pid, projects_path), DOCS_URL % pid,
                      bar(pok, ptot), pok, ptot,
                      c["windows"][0], c["windows"][1],
                      c["linux"][0], c["linux"][1]))
    return out


def problem_rows(statuses, projects_path, frag):
    """Every broken/ambiguous entry, worst first, with fix/fragility markers."""
    props = load_proposal_keys(projects_path)
    rows = []
    for pid, name, plat, st in sorted(issue_list(statuses),
                                      key=lambda x: (x[3] != "broken",
                                                     x[0], x[1])):
        row = "%s `%s`" % (circle(st), name)
        if (pid, name, plat) in frag:
            row += " 🔥"
        row += " · %s · %s" % (plat, st)
        if (pid, name, plat) in props:
            row += " · 🔧 fix proposed"
        rows.append(row)
    return rows


def build_report_embed(statuses, version, projects_path, delta, frag,
                       history_dir):
    """The default report: verdict, what changed, project health, problems.

    Healthy signatures are counted, not listed - the full per-signature table
    is one click away in docs/<project>.md, and repeating it every run is what
    made the old layout unreadable.
    """
    total = sum_tallies(statuses)
    ok, amb, brk = (total.get("ok", 0), total.get("ambiguous", 0),
                    total.get("broken", 0))
    novb = total.get("no_binary", 0)
    sigs = ok + amb + brk + novb

    if brk:
        color = COLOR_BAD
        verdict = ("%s **%d broken** of %d signature checks - regenerate"
                   % (CIRCLE["broken"], brk, sigs))
    elif amb:
        color = COLOR_WARN
        verdict = ("%s **%d ambiguous** of %d signature checks - weak patterns"
                   % (CIRCLE["ambiguous"], amb, sigs))
    else:
        color = COLOR_OK
        verdict = ("%s **All %d signature checks valid** across %d project(s)"
                   % (CIRCLE["ok"], sigs, len(statuses)))

    lines = [verdict,
             "`%d ok`  ·  `%d ambiguous`  ·  `%d broken`  ·  `%d not validated`"
             % (ok, amb, brk, novb)]

    off_ok = total.get("offset_ok", 0)
    off_bad = total.get("offset_stale", 0)
    off_none = total.get("offset_no_recipe", 0) + total.get("offset_review", 0)
    if off_ok or off_bad or off_none:
        lines.append("Offsets: `%d ok`  ·  `%d stale`  ·  `%d no reference`"
                     % (off_ok, off_bad, off_none))

    head = delta_headline(delta)
    lines.append("Since last report: %s" % head if head
                 else "_No signature or offset result changed since the last "
                      "report._")

    prev = prev_version(history_dir, version)
    if prev:
        lines.append("Game build: `%s` → `%s`" % (prev, version))

    nav = ["[Full report](%s)" % REPO_URL, "[Fragility](%s)" % STATS_URL]
    commit = commit_link()
    if commit:
        nav.append("[This run](%s)" % commit)
    lines.append("Updated <t:%d:R>  ·  %s"
                 % (int(datetime.datetime.now(datetime.timezone.utc)
                        .timestamp()), "  ·  ".join(nav)))

    fields = []
    if delta:
        multi = len({c["project"] for c in delta}) > 1
        fields.append({"name": "Changes (%d)" % len(delta),
                       "value": clamp_rows([change_row(c, multi, frag)
                                            for c in delta]),
                       "inline": False})

    issues = issue_list(statuses)
    if issues:
        fields.append({"name": "Broken / ambiguous (%d)" % len(issues),
                       "value": clamp_rows(problem_rows(statuses,
                                                        projects_path, frag)),
                       "inline": False})

    fields.append({"name": "Projects (%d)" % len(statuses),
                   "value": clamp_rows(project_lines(statuses, projects_path))
                   or "none", "inline": False})

    links = manifest_links(next((s.get("manifest") for _, s in statuses
                                 if s.get("manifest")), None))
    if links:
        fields.append({"name": "Manifests", "value": links, "inline": False})

    return {
        "title": "CS2 Signatures - %s" % (version or "unknown build"),
        "url": REPO_URL,
        "color": color,
        "description": "\n".join(lines),
        "fields": fields,
        "footer": {"text": "%s  ·  🔥 breaks often  ·  🔧 fix proposed"
                           % LEGEND},
    }


def verdict_dot(tally):
    if tally.get("broken"):
        return CIRCLE["broken"]
    if tally.get("ambiguous"):
        return CIRCLE["ambiguous"]
    return CIRCLE["ok"]


def overall_color(statuses):
    tallies = [s.get("tally", {}) for _, s in statuses]
    if any(t.get("broken") for t in tallies):
        return COLOR_BAD
    if any(t.get("ambiguous") for t in tallies):
        return COLOR_WARN
    return COLOR_OK


def combined_blocks(statuses, width, projects_path):
    """One text block per project: a name header, its signature rows, then a
    Total / Windows / Linux count line below the rows."""
    blocks = []
    for pid, status in statuses:
        entries = sig_entries(status)
        c = platform_counts(entries)
        name = display_name(pid, projects_path)
        header = "%s **%s**" % (verdict_dot(status.get("tally", {})), name)
        total = c["windows"][1] + c["linux"][1]
        summary = ("**Total** %d · **Windows** %d/%d · **Linux** %d/%d"
                   % (total, c["windows"][0], c["windows"][1],
                      c["linux"][0], c["linux"][1]))
        blocks.append("\n".join([header] + sig_rows(entries, width) + [summary]))
    return blocks


def combined_fits(statuses, width, projects_path):
    """True if every project's rows fit in one combined description (no project
    would be dropped). Used to pick combined vs per-project cards."""
    total = 0
    for block in combined_blocks(statuses, width, projects_path):
        total += len(block) + 2  # blank line between blocks
    return total <= DESC_MAX


def build_combined_embed(statuses, version, ts, width, projects_path):
    """All projects in ONE embed: a section per project (header + rows),
    with a shared legend + manifest at the bottom."""
    desc = clamp_desc_blocks(combined_blocks(statuses, width, projects_path))

    fields = [{"name": "Legend", "value": LEGEND, "inline": False}]
    links = manifest_links(next((s.get("manifest") for _, s in statuses
                                 if s.get("manifest")), None))
    if links:
        fields.append({"name": "Manifests", "value": links, "inline": False})

    embed = {
        "title": "Signature Tracking Report - %s" % (version or "unknown"),
        "color": overall_color(statuses),
        "description": desc,
        "fields": fields,
        "footer": {"text": "%d project(s) tracked" % len(statuses)},
    }
    if ts:
        embed["timestamp"] = ts
    return embed


def clamp_desc_blocks(blocks):
    """Join project blocks (blank line between) under the description limit."""
    out, used = [], 0
    for i, block in enumerate(blocks):
        cost = len(block) + 2
        if used + cost > DESC_MAX:
            out.append("…and %d more project(s)" % (len(blocks) - i))
            break
        out.append(block)
        used += cost
    return "\n\n".join(out) if out else "_no signature entries_"


def build_project_embed(pid, name, status, version, ts, width):
    entries = sig_entries(status)
    counts = platform_counts(entries)
    t = status.get("tally", {})

    if t.get("broken"):
        color = COLOR_BAD
    elif t.get("ambiguous"):
        color = COLOR_WARN
    else:
        color = COLOR_OK

    total = counts["windows"][1] + counts["linux"][1]
    fields = [
        {"name": "Total", "value": str(total), "inline": True},
        {"name": "Windows",
         "value": "%d/%d" % tuple(counts["windows"]), "inline": True},
        {"name": "Linux",
         "value": "%d/%d" % tuple(counts["linux"]), "inline": True},
        {"name": "Legend", "value": LEGEND, "inline": False},
    ]
    links = manifest_links(status.get("manifest"))
    if links:
        fields.append({"name": "Manifests", "value": links, "inline": False})

    embed = {
        "author": {"name": name},
        "title": "Signature Tracking Report - %s" % (version or "unknown"),
        "color": color,
        "description": clamp_desc(sig_rows(entries, width)),
        "fields": fields,
        "footer": {"text": status.get("gamedata_source", pid)},
    }
    if ts:
        embed["timestamp"] = ts
    return embed


def example_statuses():
    """Synthetic two-project data (mixed states) for --preview / test posts."""
    manifest = {"2347771": "8344780363095656278",
                "2347773": "8898904655046099225"}

    def sig(name, win, lin):
        return {"name": name, "kind": "signature",
                "platforms": {"windows": {"status": win},
                              "linux": {"status": lin}}}

    css = [
        sig("CCSNavArea_IsValidNavMesh", "broken", "ok"),
        sig("CBaseEntity_Teleport", "ambiguous", "ok"),
        sig("Host_Say", "ok", "no_binary"),
        sig("UTIL_Remove", "ok", "ok"),
        sig("GiveNamedItem", "ok", "ok"),
        sig("ClientPrint", "ok", "ok"),
    ]
    alloc = [
        sig("GiveNamedItem2", "ok", "broken"),
    ]
    return [
        ("CounterStrikeSharp", {
            "manifest": manifest,
            "gamedata_source": "mrc4tt/CounterStrikeSharp (example)",
            "tally": {"ok": 9, "ambiguous": 1, "broken": 1, "no_binary": 1},
            "results": css}),
        ("RetakesAllocator", {
            "manifest": manifest,
            "gamedata_source": "mrc4tt/cs2-retakes-allocator (example)",
            "tally": {"ok": 1, "ambiguous": 0, "broken": 1, "no_binary": 0},
            "results": alloc}),
    ]


def example_delta():
    """Synthetic changeset matching example_statuses(), for --preview."""
    def ch(project, name, plat, change, old, new):
        return {"project": project, "kind": "signature", "name": name,
                "platform": plat, "change": change, "old": old, "new": new}

    return [
        ch("CounterStrikeSharp", "CCSNavArea_IsValidNavMesh", "windows",
           "broke", "ok", "broken"),
        ch("CounterStrikeSharp", "CBaseEntity_Teleport", "windows",
           "broke", "ok", "ambiguous"),
        ch("RetakesAllocator", "GiveNamedItem2", "linux",
           "broke", "ok", "broken"),
        ch("CounterStrikeSharp", "UTIL_Remove", "linux", "fixed", "broken",
           "ok"),
        ch("CounterStrikeSharp", "ClientPrint", "windows", "resigned", "ok",
           "ok"),
    ]


def example_fragility():
    return {("CounterStrikeSharp", "CCSNavArea_IsValidNavMesh", "windows")}


def display_name(pid, projects_path):
    """Human project name from the registry, falling back to the id."""
    try:
        for proj in P.load(projects_path):
            if proj["id"] == pid:
                return P.name(proj)
    except (OSError, ValueError, KeyError):
        pass
    return pid


UA = ("cs2-signatures-tracker (urllib, "
      "+https://git.miksen.me/mikkel/cs2-signatures)")


def post(webhook, payload, files=None):
    """POST a webhook message. With `files` ([(filename, bytes), ...]) the
    payload is sent as multipart/form-data with attachments; otherwise plain
    JSON. Discord allows up to 10 files per message.

    Posts with ?wait=true so Discord returns the created message; prints its
    id, which `--delete-message <id>` accepts to remove a post again."""
    webhook = "%s%swait=true" % (webhook, "&" if "?" in webhook else "?")
    if files:
        boundary = "----cs2sigtracker%s" % uuid.uuid4().hex
        body = bytearray()

        def part(headers, content):
            body.extend(b"--%s\r\n" % boundary.encode())
            body.extend(("\r\n".join(headers) + "\r\n\r\n").encode())
            body.extend(content)
            body.extend(b"\r\n")

        part(['Content-Disposition: form-data; name="payload_json"',
              "Content-Type: application/json"],
             json.dumps(payload).encode())
        for i, (fname, data) in enumerate(files[:10]):
            part(['Content-Disposition: form-data; name="files[%d]"; '
                  'filename="%s"' % (i, fname),
                  "Content-Type: application/json"], data)
        body.extend(b"--%s--\r\n" % boundary.encode())
        req = urllib.request.Request(webhook, data=bytes(body), method="POST")
        req.add_header("Content-Type",
                       "multipart/form-data; boundary=%s" % boundary)
    else:
        req = urllib.request.Request(webhook, data=json.dumps(payload).encode(),
                                     method="POST")
        req.add_header("Content-Type", "application/json")
    # Discord's Cloudflare edge 403s the default urllib UA (error 1010).
    req.add_header("User-Agent", UA)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            msg = json.loads(raw) if raw else {}
            if msg.get("id"):
                print("message id: %s" % msg["id"])
            return r.status
    except urllib.error.HTTPError as e:
        print("webhook POST -> %s: %s" % (e.code, e.read()[:300]),
              file=sys.stderr)
        raise


def split_webhooks(values):
    """Flatten webhook URLs out of `values` (list of strings, each possibly
    holding several URLs separated by commas or whitespace). Order preserved,
    duplicates dropped so a repeated URL is not posted to twice."""
    out = []
    for value in values:
        for url in re.split(r"[,\s]+", value or ""):
            url = url.strip()
            if url and url not in out:
                out.append(url)
    return out


def delete_message(webhook, message_id):
    """DELETE a previously posted webhook message by its id."""
    url = "%s/messages/%s" % (webhook.split("?")[0].rstrip("/"), message_id)
    req = urllib.request.Request(url, method="DELETE")
    req.add_header("User-Agent", UA)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status
    except urllib.error.HTTPError as e:
        print("webhook DELETE -> %s: %s" % (e.code, e.read()[:300]),
              file=sys.stderr)
        raise


def proposed_files(projects_path):
    """[(attachment_name, bytes), ...] of patched gamedata files written by
    propose_sigs.py - drop-in gamedata with candidate sigs applied."""
    out = []
    try:
        projects = P.load(projects_path)
    except Exception:  # noqa: BLE001 - attachments are optional decoration
        return out
    for proj in projects:
        path = P.proposed_gamedata_path(proj)
        if os.path.isfile(path):
            with open(path, "rb") as fh:
                out.append(("%s-gamedata-proposed.json" % proj["id"],
                            fh.read()))
    return out


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects", default=P.REGISTRY)
    ap.add_argument("--status", default=None,
                    help="single status.json override (default: all projects)")
    ap.add_argument("--webhook", action="append", default=None,
                    help="webhook URL; repeat, or pass several separated by "
                         "commas/whitespace, to post to multiple servers "
                         "(default: DISCORD_WEBHOOK env, same syntax)")
    ap.add_argument("--username", default="cs2-sig-tracker")
    ap.add_argument("--steam-inf", default="bin_linux/game/csgo/steam.inf",
                    help="steam.inf to read the CS2 version (PatchVersion) from")
    ap.add_argument("--version", default=None, help="CS2 version override")
    ap.add_argument("--mention", default=os.environ.get("DISCORD_MENTION"),
                    help="user/role id to ping when broken/ambiguous "
                         "(numeric id, or 'here'/'everyone')")
    ap.add_argument("--preview", action="store_true",
                    help="render payload to stdout, do not send")
    ap.add_argument("--delete-message", default=None, metavar="ID",
                    help="delete a previously posted message by id, then exit")
    ap.add_argument("--example", action="store_true",
                    help="use synthetic data (for --preview, or a live test post)")
    ap.add_argument("--full", action="store_true",
                    help="list every signature (one combined card) instead of "
                         "the default delta-first report")
    ap.add_argument("--summary", action="store_true",
                    help=argparse.SUPPRESS)  # back-compat: now the default
    ap.add_argument("--separate", action="store_true",
                    help="one per-signature card per project")
    ap.add_argument("--delta", default=os.path.join("reports", "delta.json"),
                    help="named delta from post_gate.py --write-delta "
                         "(recomputed live when missing or stale)")
    ap.add_argument("--fragility", default=os.path.join("reports",
                                                        "fragility.json"),
                    help="breakage counts from gen_stats.py --json, for the "
                         "🔥 marker")
    ap.add_argument("--history-dir", default=os.path.join("reports", "history"),
                    help="history snapshots, read for the previous CS2 version")
    args = ap.parse_args()
    webhooks = split_webhooks(args.webhook
                              if args.webhook is not None
                              else [os.environ.get("DISCORD_WEBHOOK", "")])

    if args.delete_message:
        if not webhooks:
            print("missing --webhook (or DISCORD_WEBHOOK env)", file=sys.stderr)
            return 1
        # A message id belongs to the webhook that created it, so with several
        # configured only one owns it - the rest 404. Try each, succeed if any.
        deleted = 0
        for hook in webhooks:
            try:
                delete_message(hook, args.delete_message)
                deleted += 1
            except urllib.error.HTTPError:
                continue
        if not deleted:
            print("no webhook owns message %s" % args.delete_message,
                  file=sys.stderr)
            return 1
        print("deleted message %s" % args.delete_message)
        return 0

    if args.example:
        statuses = example_statuses()
        version = read_version(args.steam_inf, args.version or "1.41.6.8")
        delta, frag, history = example_delta(), example_fragility(), None
    else:
        statuses = load_statuses(args.projects, args.status)
        version = read_version(args.steam_inf, args.version)
        delta = load_delta(args.delta, args.projects)
        frag = load_fragility(args.fragility)
        history = args.history_dir

    ts = now_iso()
    width = name_width(statuses)
    if not statuses:
        print("no project statuses found - nothing to post", file=sys.stderr)
        return 1
    def per_project():
        return [build_project_embed(pid, display_name(pid, args.projects),
                                    status, version, ts, width)
                for pid, status in statuses]

    if args.separate:
        embeds = per_project()
    elif args.full:
        if combined_fits(statuses, width, args.projects):
            embeds = [build_combined_embed(statuses, version, ts, width,
                                           args.projects)]
        else:
            # Too many/large plugins for one card - fall back to per-project
            # cards (each gets its own budget) rather than dropping projects.
            print("combined post too large -> per-project cards",
                  file=sys.stderr)
            embeds = per_project()
    else:
        # Default (and --summary, kept as an alias): answer "what changed".
        embeds = [build_report_embed(statuses, version, args.projects, delta,
                                     frag, history)]

    # Ping only when something needs attention. Mention must live in top-level
    # `content` (embeds never trigger notifications), and allowed_mentions must
    # whitelist the target or Discord silently drops the ping.
    content, allowed = None, None
    if args.mention and issue_list(statuses):
        m = args.mention.strip().lstrip("@")
        if m in ("here", "everyone"):
            content, allowed = "@%s" % m, {"parse": [m]}
        else:
            content, allowed = "<@%s>" % m, {"users": [m]}

    # Patched gamedata files (candidate sigs applied) ride the first message.
    # Unique-match verified, NOT runtime-tested - say so in the message.
    files = [] if args.example else proposed_files(args.projects)
    if files:
        warn = ("⚠️ Auto-generated gamedata with proposed replacement "
                "signatures attached - unique-match verified, not "
                "runtime-tested. Review before use.")
        content = "%s\n%s" % (content, warn) if content else warn

    if args.preview:
        payload = {"username": args.username, "embeds": embeds}
        if content:
            payload["content"] = content
            if allowed:
                payload["allowed_mentions"] = allowed
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        for fname, data in files:
            print("attachment: %s (%d bytes)" % (fname, len(data)),
                  file=sys.stderr)
        return 0

    if not webhooks:
        print("missing --webhook (or DISCORD_WEBHOOK env)", file=sys.stderr)
        return 1

    # Discord caps embeds per message; batch into chunks. Ping + attachments
    # ride the first message. Each webhook is independent (own rate limit), and
    # one dead URL must not cost the other servers their report.
    failed = 0
    for n, hook in enumerate(webhooks, 1):
        try:
            for start in range(0, len(embeds), EMBEDS_PER_MSG):
                chunk = embeds[start:start + EMBEDS_PER_MSG]
                payload = {"username": args.username, "embeds": chunk}
                if start == 0 and content:
                    payload["content"] = content
                    if allowed:
                        payload["allowed_mentions"] = allowed
                post(hook, payload, files=files if start == 0 else None)
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            # The URL itself is a secret - identify the webhook by position.
            print("webhook %d/%d failed: %s" % (n, len(webhooks), e),
                  file=sys.stderr)
            failed += 1
            continue
    posted = len(webhooks) - failed
    print("posted %d embed(s), %d attachment(s) to %d/%d discord webhook(s)"
          % (len(embeds), len(files), posted, len(webhooks)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
