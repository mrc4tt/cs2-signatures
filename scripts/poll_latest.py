#!/usr/bin/env python3
"""Notice that the analysis box published a new CS2_VibeSignatures snapshot.

The analysis box (9950X3D) polls Steam itself, analyses both platforms and
publishes to sig.miksen.me on its own timer. Nothing here drives it and nothing
here may reach into it; this side only has to notice the result.

latest.json is a few hundred bytes and carries the two values that decide
whether the published reference moved:

  gameVersion    which build the newest snapshot describes
  configSha256   the analysis config that produced it - a re-publish of the SAME
                 build with a changed config lands here and nowhere else, which
                 is why the version alone is not enough

Both are compared against reports/.last_seen.json and the pair is stored back on
a change. The 2 MB snapshot is never fetched to answer this question.

Exit 10 = the published reference changed (caller should force a full run).
Exit  0 = unchanged.
Exit  1 = error (network, bad document) - the caller should carry on with its
          normal schedule rather than treat it as a change.

  python3 scripts/poll_latest.py
  python3 scripts/poll_latest.py --no-write        # report, don't persist
"""
import argparse
import json
import os
import sys
import urllib.request

URL = "https://sig.miksen.me/latest.json"
STATE = os.path.join("reports", ".last_seen.json")
# Cloudflare 403s the default urllib UA (error 1010), so identify ourselves.
UA = "cs2-sig-tracker (+https://git.miksen.me/mikkel/cs2-signatures)"
SCHEMA = 1
# The fields that mean "re-compare". lastPublishTime is deliberately NOT one of
# them: a rebuild that changes nothing would otherwise force a full run.
KEYS = ("gameVersion", "configSha256")


def fetch(url, timeout):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", UA)
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())


def state_of(doc):
    """The comparable pair, or a ValueError naming what the document lacked."""
    if not isinstance(doc, dict):
        raise ValueError("latest.json is not an object")
    schema = doc.get("schemaVersion")
    if schema != SCHEMA:
        # Keep going if the fields we read are still there - a schema bump that
        # only adds fields must not stall the tracker - but say so.
        print("warning: latest.json schemaVersion %r, expected %d"
              % (schema, SCHEMA), file=sys.stderr)
    latest = doc.get("latest")
    if not isinstance(latest, dict):
        raise ValueError("latest.json has no 'latest' object")
    missing = [k for k in KEYS if not latest.get(k)]
    if missing:
        raise ValueError("latest.json is missing %s" % ", ".join(missing))
    return {k: str(latest[k]) for k in KEYS}


def load_state(path):
    if not os.path.isfile(path):
        return {}
    try:
        with open(path) as fh:
            old = json.load(fh)
    except (OSError, ValueError):
        # An unreadable state file means "unknown", which is a change. Better a
        # redundant run than a silently skipped one.
        return {}
    return {k: str(old[k]) for k in KEYS if old.get(k)}


def save_state(path, state):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as fh:
        json.dump(state, fh, indent=2)
        fh.write("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=os.environ.get("SIG_LATEST_URL", URL))
    ap.add_argument("--state", default=STATE)
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--no-write", action="store_true",
                    help="report the verdict without persisting the new state")
    args = ap.parse_args()

    try:
        new = state_of(fetch(args.url, args.timeout))
    except Exception as e:  # noqa: BLE001
        print("error polling %s: %s" % (args.url, e), file=sys.stderr)
        return 1

    old = load_state(args.state)
    print(json.dumps(new))
    if new == old:
        print("unchanged %s" % new, file=sys.stderr)
        return 0
    if not args.no_write:
        save_state(args.state, new)
    print("CHANGED %s -> %s" % (old or "(no previous state)", new),
          file=sys.stderr)
    return 10


if __name__ == "__main__":
    sys.exit(main())
