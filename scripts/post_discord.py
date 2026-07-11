#!/usr/bin/env python3
"""Post a signature-status summary to a Discord webhook.

Reads reports/status.json and sends a single embed: overall verdict (color
green/yellow/red), the ok/ambiguous/broken tally, SteamDB manifest links, and a
list of any broken/ambiguous subroutines.

Auth: webhook URL via env DISCORD_WEBHOOK (or --webhook). Never hard-code it.

Preview: pass --preview to render the exact JSON payload to stdout WITHOUT
sending — use it to see what a post looks like (optionally with --example to
fill in synthetic broken data so the formatting is visible even when all sigs
currently pass).

stdlib only (urllib). Mirrors scripts/open_issue.py conventions.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import projects as P  # noqa: E402

# Discord embed color (decimal). Green ok, yellow ambiguous, red broken.
COLOR_OK = 0x2ECC71
COLOR_WARN = 0xF1C40F
COLOR_BAD = 0xE74C3C

# SteamDB depot link, same shape gen_report uses for the README.
STEAMDB = "https://steamdb.info/depot/%s/history/?changeid=M:%s"


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


def issue_list(statuses):
    """(project, name, platform, status) for every broken/ambiguous entry."""
    out = []
    for pid, status in statuses:
        for r in status.get("results", []):
            for plat, info in r.get("platforms", {}).items():
                st = info.get("status")
                if st in ("broken", "ambiguous"):
                    out.append((pid, r["name"], plat, st))
    return out


def sum_tallies(statuses):
    t = {}
    for _, status in statuses:
        for k, v in status.get("tally", {}).items():
            t[k] = t.get(k, 0) + v
    return t


def manifest_links(manifest):
    if not manifest:
        return "unknown"
    return " ".join("[`%s`](%s)" % (mid, STEAMDB % (depot, mid))
                    for depot, mid in sorted(manifest.items()))


def build_embed(statuses):
    t = sum_tallies(statuses)
    ok = t.get("ok", 0)
    amb = t.get("ambiguous", 0)
    brk = t.get("broken", 0)
    novb = t.get("no_binary", 0)
    issues = issue_list(statuses)
    manifest = next((s.get("manifest") for _, s in statuses if s.get("manifest")),
                    None)

    if brk:
        color, verdict = COLOR_BAD, "\U0001F534 %d broken" % brk
    elif amb:
        color, verdict = COLOR_WARN, "\U0001F7E1 %d ambiguous" % amb
    else:
        color, verdict = COLOR_OK, "\U0001F7E2 all signatures pass"

    fields = [
        {"name": "Validated",
         "value": "%d ok · %d ambiguous · %d broken · %d "
                  "not-yet-validated" % (ok, amb, brk, novb),
         "inline": False},
        {"name": "Projects (%d)" % len(statuses),
         "value": "\n".join(
             "• `%s` — %d ok · %d amb · %d broken"
             % (pid, s.get("tally", {}).get("ok", 0),
                s.get("tally", {}).get("ambiguous", 0),
                s.get("tally", {}).get("broken", 0))
             for pid, s in statuses) or "none",
         "inline": False},
        {"name": "Manifests",
         "value": manifest_links(manifest),
         "inline": False},
    ]
    if issues:
        lines = ["• `[%s] %s` (%s, %s)" % (pid, n, p, s)
                 for pid, n, p, s in issues[:20]]
        if len(issues) > 20:
            lines.append("…and %d more" % (len(issues) - 20))
        fields.append({"name": "Broken / ambiguous (%d)" % len(issues),
                       "value": "\n".join(lines), "inline": False})

    return {
        "title": "CS2 signatures — %s" % verdict,
        "color": color,
        "fields": fields,
        "footer": {"text": "%d project(s) tracked" % len(statuses)},
    }


def example_statuses():
    """Synthetic multi-project data (broken + ambiguous) for --preview demos."""
    manifest = {"2347771": "8344780363095656278",
                "2347773": "8898904655046099225"}
    return [
        ("CounterStrikeSharp", {
            "manifest": manifest,
            "tally": {"ok": 57, "ambiguous": 1, "broken": 1, "no_binary": 0},
            "results": [
                {"name": "CCSNavArea_IsValidNavMesh",
                 "platforms": {"windows": {"status": "broken"}}},
                {"name": "CBaseEntity_Teleport",
                 "platforms": {"windows": {"status": "ambiguous"}}},
            ],
        }),
        ("RetakesAllocator", {
            "manifest": manifest,
            "tally": {"ok": 0, "ambiguous": 0, "broken": 1, "no_binary": 0},
            "results": [
                {"name": "GiveNamedItem2",
                 "platforms": {"linux": {"status": "broken"}}},
            ],
        }),
    ]


def post(webhook, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(webhook, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    # Discord's Cloudflare edge 403s the default urllib UA (error 1010).
    req.add_header("User-Agent", "cs2-signatures-tracker (urllib, +https://git.miksen.me/mikkel/cs2-signatures)")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status
    except urllib.error.HTTPError as e:
        print("webhook POST -> %s: %s" % (e.code, e.read()[:300]),
              file=sys.stderr)
        raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects", default=P.REGISTRY)
    ap.add_argument("--status", default=None,
                    help="single status.json override (default: all projects)")
    ap.add_argument("--webhook", default=os.environ.get("DISCORD_WEBHOOK"))
    ap.add_argument("--username", default="cs2-sig-tracker")
    ap.add_argument("--mention", default=os.environ.get("DISCORD_MENTION"),
                    help="user/role id to ping when broken/ambiguous "
                         "(numeric id, or 'here'/'everyone')")
    ap.add_argument("--preview", action="store_true",
                    help="render payload to stdout, do not send")
    ap.add_argument("--example", action="store_true",
                    help="with --preview: use synthetic broken data")
    args = ap.parse_args()

    if args.example and not args.preview:
        print("--example only makes sense with --preview", file=sys.stderr)
        return 1

    if args.example:
        statuses = example_statuses()
    else:
        statuses = load_statuses(args.projects, args.status)

    payload = {"username": args.username, "embeds": [build_embed(statuses)]}

    # Ping only when something needs attention. Mention must live in top-level
    # `content` (embeds never trigger notifications), and allowed_mentions must
    # whitelist the target or Discord silently drops the ping.
    if args.mention and issue_list(statuses):
        m = args.mention.strip().lstrip("@")
        if m in ("here", "everyone"):
            payload["content"] = "@%s" % m
            payload["allowed_mentions"] = {"parse": [m]}
        else:
            payload["content"] = "<@%s>" % m
            payload["allowed_mentions"] = {"users": [m]}

    if args.preview:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if not args.webhook:
        print("missing --webhook (or DISCORD_WEBHOOK env)", file=sys.stderr)
        return 1

    post(args.webhook, payload)
    print("posted to discord")
    return 0


if __name__ == "__main__":
    sys.exit(main())
