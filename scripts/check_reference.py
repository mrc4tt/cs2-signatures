#!/usr/bin/env python3
"""Compare every tracked gamedata entry against a CS2_VibeSignatures snapshot.

Read-only: prints a report and optionally writes JSON to a path you name. It does
not touch reports/, does not change any exit code the pipeline depends on, and
does not post anything. run_all.sh does not call it yet.

What it answers that byte-scanning cannot:

  signatures  scanning says "this pattern still resolves here". This says whether
              the upstream analysis still uses that same pattern. A sig can be
              `ok` and `outdated` at once - it works today, and the project it
              came from has already moved on.
  offsets     scanning cannot check an integer at all. The snapshot carries the
              vtable index and struct member offset for linux AND windows, so an
              offsets entry gets a real verdict on both platforms without a
              hand-written recipe.

Build binding matters for reading the result: a snapshot describes one exact set
of binaries. When the local binaries hash differently, an `outdated` verdict may
just mean the reference is for another build, so the header states which.

  python3 scripts/check_reference.py --gamever 14178b
  python3 scripts/check_reference.py --gamever 14180 --project WeaponPaints
"""
import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_symbols as S  # noqa: E402
import projects as P  # noqa: E402

PLATFORMS = ("linux", "windows")
SYMBOL_DIR = os.path.join("data", "symbols")


def sha256(path):
    if not path or not os.path.isfile(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def binding(snap, bins):
    """How the local binaries relate to the ones the snapshot was built from."""
    rows = []
    for (module, plat), path in sorted(bins.items()):
        want = snap.binary_sha(module, plat)
        got = sha256(path)
        if not got:
            state = "missing"
        elif not want:
            state = "not_in_snapshot"
        else:
            state = "exact" if got == want else "different_build"
        rows.append({"module": module, "platform": plat, "state": state,
                     "local": got, "reference": want})
    return rows


def check_entry(snap, name, entry):
    """Per-platform verdicts for one gamedata entry."""
    out = {"name": name, "platforms": {}}
    if "signatures" in entry:
        out["kind"] = "signature"
        sigs = entry["signatures"]
        for plat in PLATFORMS:
            ours = sigs.get(plat)
            if not ours:
                out["platforms"][plat] = {"status": "missing_sig"}
                continue
            ref = snap.signature(name, plat)
            kind = snap.kind(name, plat)
            if ref is None:
                # A record can exist and still carry no byte pattern: func_sig is
                # present on 1145/1160 function records but only 731/1354
                # virtualFunction ones. Separate that from "not analysed at all".
                out["platforms"][plat] = {
                    "status": "no_sig" if kind else "no_reference", "kind": kind}
                continue
            rel = S.sig_relation(ours, ref)
            if rel == "conflict":
                out["platforms"][plat] = {"status": "outdated",
                                          "ours": ours, "reference": ref}
            else:
                out["platforms"][plat] = {"status": "match", "relation": rel}
        return out

    out["kind"] = "offset"
    offsets = entry.get("offsets", {})
    for plat in PLATFORMS:
        ours = offsets.get(plat)
        if ours is None:
            out["platforms"][plat] = {"status": "missing_offset"}
            continue
        ref, method = snap.offset(name, plat)
        if ref is None:
            out["platforms"][plat] = {"status": "no_reference", "reason": method}
        elif int(ours) == ref:
            out["platforms"][plat] = {"status": "match", "method": method,
                                      "value": ref}
        else:
            out["platforms"][plat] = {"status": "mismatch", "method": method,
                                      "ours": ours, "reference": ref}
    return out


ORDER = ("match", "outdated", "mismatch", "no_sig", "no_reference",
         "missing_sig", "missing_offset")


def check_project(snap, proj):
    path = P.gamedata_path(proj)
    with open(path) as fh:
        gamedata = json.load(fh)
    entries = [check_entry(snap, n, e) for n, e in gamedata.items()
               if "signatures" in e or "offsets" in e]
    tally = {"signature": dict.fromkeys(ORDER, 0),
             "offset": dict.fromkeys(ORDER, 0)}
    for e in entries:
        for info in e["platforms"].values():
            tally[e["kind"]][info["status"]] += 1
    return {"project": proj["id"], "tally": tally, "entries": entries}


def flag(status):
    return {"match": "ok", "outdated": "OUTDATED", "mismatch": "MISMATCH",
            "no_reference": "no ref", "no_sig": "no sig"}.get(status, status)


def report(result, verbose):
    t = result["tally"]
    print("[%s] sigs %s" % (result["project"], compact(t["signature"])))
    print("[%s] offs %s" % (result["project"], compact(t["offset"])))
    for e in result["entries"]:
        interesting = {p: i for p, i in e["platforms"].items()
                       if i["status"] not in ("match",)}
        if not interesting or (not verbose and
                               all(i["status"].startswith(("no_", "missing"))
                                   for i in interesting.values())):
            continue
        for plat, info in sorted(interesting.items()):
            detail = ""
            if info["status"] == "mismatch":
                detail = "  ours=%s reference=%s (%s)" % (
                    info["ours"], info["reference"], info["method"])
            elif info["status"] == "outdated":
                detail = "\n        ours: %s\n        ref:  %s" % (
                    info["ours"], info["reference"])
            print("    %-9s %-8s %-46s%s"
                  % (flag(info["status"]), plat, e["name"][:46], detail))


def compact(d):
    return ", ".join("%s=%d" % (k, v) for k, v in d.items() if v)or "none"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gamever", default=None,
                    help="snapshot in data/symbols (default: newest cached)")
    ap.add_argument("--snapshot", default=None, help="explicit snapshot path")
    ap.add_argument("--project", default=None)
    ap.add_argument("--projects", default=P.REGISTRY)
    ap.add_argument("--linux", default="bin_linux/game/csgo/bin/linuxsteamrt64/libserver.so")
    ap.add_argument("--windows", default="bin_win/game/csgo/bin/win64/server.dll")
    ap.add_argument("--linux-engine2", default="bin_linux/game/bin/linuxsteamrt64/libengine2.so")
    ap.add_argument("--windows-engine2", default="bin_win/game/bin/win64/engine2.dll")
    ap.add_argument("--json", default=None, help="also write the result here")
    ap.add_argument("--verbose", action="store_true",
                    help="list entries with no reference too")
    args = ap.parse_args()

    path = args.snapshot
    if not path:
        cached = sorted(f for f in os.listdir(SYMBOL_DIR)
                        if f.endswith(".json")) if os.path.isdir(SYMBOL_DIR) else []
        if args.gamever:
            path = os.path.join(SYMBOL_DIR, "%s.json" % args.gamever)
        elif cached:
            path = os.path.join(SYMBOL_DIR, cached[-1])
    if not path or not os.path.isfile(path):
        print("no snapshot; run scripts/fetch_symbols.py first", file=sys.stderr)
        return 1

    snap = S.load(path, S.load_aliases())
    bins = {("server", "linux"): args.linux, ("server", "windows"): args.windows,
            ("engine", "linux"): args.linux_engine2,
            ("engine", "windows"): args.windows_engine2}

    src = snap.raw.get("source", {})
    origin = src.get("origin", "unknown origin")
    commit = src.get("commit")
    print("snapshot %s (%d records) from %s"
          % (snap.gamever, len(snap.raw.get("records", [])), path))
    print("  analysis %s%s" % (origin, " @ %s" % commit[:12] if commit else ""))
    rows = binding(snap, bins)
    for r in rows:
        print("  binary %-7s %-8s %s" % (r["module"], r["platform"], r["state"]))
    if any(r["state"] == "different_build" for r in rows):
        print("  note: local binaries are a different build than the snapshot,"
              " so an outdated verdict may be a version gap, not a stale sig")
    print()

    results = [check_project(snap, p)
               for p in P.load(args.projects, only=args.project)]
    for r in results:
        report(r, args.verbose)
        print()

    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"gamever": snap.gamever, "binding": rows,
                       "projects": results}, fh, indent=2)
        print("wrote %s" % args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
