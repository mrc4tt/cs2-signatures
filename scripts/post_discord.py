#!/usr/bin/env python3
"""Post per-project CS2 signature reports to a Discord webhook.

One embed per tracked project. The title carries the CS2 version; the body
lists every signature with its Windows/Linux match state, and summary fields
give the healthy/validated count per platform:

    🟢 valid (1 match)   🔴 failed (0)   🟡 multi-match (>1)   ⚪ not validated

The embed colour and an optional @mention escalate on any breakage.

Auth: webhook URL via env DISCORD_WEBHOOK (or --webhook). Never hard-code it.

Preview: --preview prints the JSON payload without sending. Add --example for
synthetic data — also usable as a live test post (send without --preview) to
see the layout in Discord before a real breakage happens.

stdlib only (urllib).
"""
import argparse
import datetime
import json
import os
import re
import sys
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
DOCS_URL = ("https://git.miksen.me/mikkel/cs2-signatures/src/branch/main/"
            "docs/%s.md")

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
    """(project, name, platform, status) for every broken/ambiguous entry —
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
    except Exception:  # noqa: BLE001 — proposals are optional decoration
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


def build_summary_embed(statuses, version, ts, projects_path):
    """Polished at-a-glance summary: verdict, per-project health bars, manifest,
    and a grouped broken/ambiguous list. One embed."""
    total = sum_tallies(statuses)
    ok, amb, brk = total.get("ok", 0), total.get("ambiguous", 0), total.get("broken", 0)
    novb = total.get("no_binary", 0)

    if brk:
        color = COLOR_BAD
        verdict = "%s **%d broken** — signatures need regenerating" % (CIRCLE["broken"], brk)
    elif amb:
        color = COLOR_WARN
        verdict = "%s **%d ambiguous** — weak signatures" % (CIRCLE["ambiguous"], amb)
    else:
        color = COLOR_OK
        verdict = "%s **All signatures valid**" % CIRCLE["ok"]

    lines = [verdict,
             "`%d ok`  ·  `%d ambiguous`  ·  `%d broken`  ·  `%d not validated`"
             % (ok, amb, brk, novb)]

    proj_lines = []
    for pid, status in statuses:
        c = platform_counts(sig_entries(status))
        pok = c["windows"][0] + c["linux"][0]
        ptot = c["windows"][1] + c["linux"][1]
        proj_lines.append(
            "%s [**%s**](%s)\n`%s` %d/%d  ·  Win %d/%d · Lin %d/%d"
            % (verdict_dot(status.get("tally", {})),
               display_name(pid, projects_path), DOCS_URL % pid,
               bar(pok, ptot), pok, ptot,
               c["windows"][0], c["windows"][1], c["linux"][0], c["linux"][1]))

    fields = [{"name": "Projects (%d)" % len(statuses),
               "value": "\n".join(proj_lines) or "none", "inline": False}]

    links = manifest_links(next((s.get("manifest") for _, s in statuses
                                 if s.get("manifest")), None))
    if links:
        fields.append({"name": "Manifests", "value": links, "inline": False})

    issues = issue_list(statuses)
    if issues:
        props = load_proposal_keys(projects_path)
        rows = ["%s `%s` · %s (%s)%s"
                % (circle(st), n, plat,
                   "broken" if st == "broken" else "ambiguous",
                   " · 🔧 fix proposed" if (pid, n, plat) in props else "")
                for pid, n, plat, st in
                sorted(issues, key=lambda x: (x[3] != "broken", x[0], x[1]))]
        shown = rows[:15]
        if len(rows) > 15:
            shown.append("…and %d more" % (len(rows) - 15))
        fields.append({"name": "Broken / ambiguous (%d)" % len(issues),
                       "value": "\n".join(shown), "inline": False})

    embed = {
        "title": "CS2 Signatures — %s" % (version or "unknown"),
        "color": color,
        "description": "\n".join(lines),
        "fields": fields,
        "footer": {"text": "%d project(s) · %s" % (len(statuses), LEGEND)},
    }
    if ts:
        embed["timestamp"] = ts
    return embed


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
    JSON. Discord allows up to 10 files per message."""
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
            return r.status
    except urllib.error.HTTPError as e:
        print("webhook POST -> %s: %s" % (e.code, e.read()[:300]),
              file=sys.stderr)
        raise


def proposed_files(projects_path):
    """[(attachment_name, bytes), ...] of patched gamedata files written by
    propose_sigs.py — drop-in gamedata with candidate sigs applied."""
    out = []
    try:
        projects = P.load(projects_path)
    except Exception:  # noqa: BLE001 — attachments are optional decoration
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
    ap.add_argument("--webhook", default=os.environ.get("DISCORD_WEBHOOK"))
    ap.add_argument("--username", default="cs2-sig-tracker")
    ap.add_argument("--steam-inf", default="bin_linux/game/csgo/steam.inf",
                    help="steam.inf to read the CS2 version (PatchVersion) from")
    ap.add_argument("--version", default=None, help="CS2 version override")
    ap.add_argument("--mention", default=os.environ.get("DISCORD_MENTION"),
                    help="user/role id to ping when broken/ambiguous "
                         "(numeric id, or 'here'/'everyone')")
    ap.add_argument("--preview", action="store_true",
                    help="render payload to stdout, do not send")
    ap.add_argument("--example", action="store_true",
                    help="use synthetic data (for --preview, or a live test post)")
    ap.add_argument("--summary", action="store_true",
                    help="compact summary card instead of the per-signature report")
    ap.add_argument("--separate", action="store_true",
                    help="one per-signature card per project")
    args = ap.parse_args()

    if args.example:
        statuses = example_statuses()
        version = read_version(args.steam_inf, args.version or "1.41.6.8")
    else:
        statuses = load_statuses(args.projects, args.status)
        version = read_version(args.steam_inf, args.version)

    ts = now_iso()
    width = name_width(statuses)
    if not statuses:
        print("no project statuses found — nothing to post", file=sys.stderr)
        return 1
    def per_project():
        return [build_project_embed(pid, display_name(pid, args.projects),
                                    status, version, ts, width)
                for pid, status in statuses]

    if args.summary:
        embeds = [build_summary_embed(statuses, version, ts, args.projects)]
    elif args.separate:
        embeds = per_project()
    elif combined_fits(statuses, width, args.projects):
        # Default: one combined card while every project's rows fit.
        embeds = [build_combined_embed(statuses, version, ts, width,
                                       args.projects)]
    else:
        # Too many/large plugins for one card — fall back to per-project cards
        # (each gets its own budget) rather than silently dropping projects.
        print("combined post too large -> per-project cards", file=sys.stderr)
        embeds = per_project()

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
    # Unique-match verified, NOT runtime-tested — say so in the message.
    files = [] if args.example else proposed_files(args.projects)
    if files:
        warn = ("⚠️ Auto-generated gamedata with proposed replacement "
                "signatures attached — unique-match verified, not "
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

    if not args.webhook:
        print("missing --webhook (or DISCORD_WEBHOOK env)", file=sys.stderr)
        return 1

    # Discord caps embeds per message; batch into chunks. Ping + attachments
    # ride the first message.
    for start in range(0, len(embeds), EMBEDS_PER_MSG):
        chunk = embeds[start:start + EMBEDS_PER_MSG]
        payload = {"username": args.username, "embeds": chunk}
        if start == 0 and content:
            payload["content"] = content
            if allowed:
                payload["allowed_mentions"] = allowed
        post(args.webhook, payload, files=files if start == 0 else None)
    print("posted %d embed(s), %d attachment(s) to discord"
          % (len(embeds), len(files)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
