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

# Discord embed color (decimal). Green ok, yellow ambiguous, red broken.
COLOR_OK = 0x2ECC71
COLOR_WARN = 0xF1C40F
COLOR_BAD = 0xE74C3C

# SteamDB depot link, same shape gen_report uses for the README.
STEAMDB = "https://steamdb.info/depot/%s/history/?changeid=M:%s"


def issue_list(status):
    """(name, platform, status) for every broken/ambiguous platform entry."""
    out = []
    for r in status.get("results", []):
        for plat, info in r.get("platforms", {}).items():
            st = info.get("status")
            if st in ("broken", "ambiguous"):
                out.append((r["name"], plat, st))
    return out


def manifest_links(manifest):
    if not manifest:
        return "unknown"
    return " ".join("[`%s`](%s)" % (mid, STEAMDB % (depot, mid))
                    for depot, mid in sorted(manifest.items()))


def build_embed(status):
    t = status.get("tally", {})
    ok = t.get("ok", 0)
    amb = t.get("ambiguous", 0)
    brk = t.get("broken", 0)
    novb = t.get("no_binary", 0)
    issues = issue_list(status)

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
        {"name": "Manifests",
         "value": manifest_links(status.get("manifest")),
         "inline": False},
    ]
    if issues:
        lines = ["• `%s` (%s, %s)" % (n, p, s) for n, p, s in issues[:20]]
        if len(issues) > 20:
            lines.append("…and %d more" % (len(issues) - 20))
        fields.append({"name": "Broken / ambiguous (%d)" % len(issues),
                       "value": "\n".join(lines), "inline": False})

    return {
        "title": "CS2 signatures — %s" % verdict,
        "color": color,
        "fields": fields,
        "footer": {"text": "source: %s" % status.get("gamedata_source", "?")},
    }


def example_status():
    """Synthetic status with a broken + ambiguous entry, for --preview demos."""
    return {
        "manifest": {"2347771": "8344780363095656278",
                     "2347773": "8898904655046099225"},
        "gamedata_source": "mrc4tt/CounterStrikeSharp (example)",
        "tally": {"ok": 57, "ambiguous": 1, "broken": 2, "no_binary": 0},
        "results": [
            {"name": "CCSNavArea_IsValidNavMesh",
             "platforms": {"windows": {"status": "broken"}}},
            {"name": "UTIL_ClientPrintAll",
             "platforms": {"linux": {"status": "broken"}}},
            {"name": "CBaseEntity_Teleport",
             "platforms": {"windows": {"status": "ambiguous"}}},
        ],
    }


def post(webhook, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(webhook, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status
    except urllib.error.HTTPError as e:
        print("webhook POST -> %s: %s" % (e.code, e.read()[:300]),
              file=sys.stderr)
        raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", default="reports/status.json")
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
        status = example_status()
    else:
        with open(args.status) as fh:
            status = json.load(fh)

    payload = {"username": args.username, "embeds": [build_embed(status)]}

    # Ping only when something needs attention. Mention must live in top-level
    # `content` (embeds never trigger notifications), and allowed_mentions must
    # whitelist the target or Discord silently drops the ping.
    if args.mention and issue_list(status):
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
