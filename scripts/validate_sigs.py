#!/usr/bin/env python3
"""Validate every tracked project's gamedata signatures against CS2 binaries.

Projects come from data/projects.json (see scripts/projects.py). All projects
share the same downloaded game binaries, so the caller passes the four binary
paths once and we validate each project's data/<id>/gamedata.json against them,
writing reports/<id>/status.json per project.

For every entry with a `signatures` block, scan the matching platform+library
binary's executable sections and classify:

    matches == 1  -> ok        (unique, healthy)
    matches == 0  -> broken    (sig no longer present -> needs regen)
    matches  > 1  -> ambiguous (present but not unique -> weak sig)

The CSS `library` field ("server" / "engine2") picks which binary to scan.
Entries with only `offsets` (vtable slots) can't be byte-validated -> skipped.

An optional reference snapshot (--symbols, see fetch_symbols.py) adds a second
tier the scanner cannot reach on its own:

  signatures  the scan says the pattern still resolves here; the reference says
              whether it is still the pattern upstream uses. Both can be true at
              once - a sig that is `ok` and `outdated` works today and has been
              replaced upstream. Advisory, so it never fails the run.
  offsets     the reference carries the vtable index and struct-member offset for
              linux AND windows, so an offsets entry gets a real verdict on both
              platforms with no recipe. Windows offsets have no other source: the
              RTTI walk in lib_offset is linux-only.
  anchors     stronger still: `vfunc_sig` and `offset_sig` pin the instruction
              that carries the offset, so lib_anchor reads the value back out of
              the binary we actually downloaded. That verdict describes THIS
              build whichever version the snapshot came from, which is what makes
              it trustworthy while the analysis lags the game.
  bounds      an index at or past `vtable_numvfunc` is wrong no matter what else
              is known, and the vtable dumps cover every class on both platforms.

Exit non-zero if any signature broke, or an offset is provably stale, in any
project.

Edge over ianlucas/cs2-signatures: they scan the whole file and stop at the
first hit (boolean ok/broken). We scan per executable section and COUNT hits,
so we also flag `ambiguous` sigs (matches >1) that aren't actually unique.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_sig import sig_to_regex, count_matches, exec_sections  # noqa: E402
from lib_rtti import open_image  # noqa: E402
from lib_offset import validate_offsets  # noqa: E402
import lib_anchor as ANCHOR  # noqa: E402
import lib_symbols as SYM  # noqa: E402
import projects as P  # noqa: E402


def classify(n):
    if n == 1:
        return "ok"
    if n == 0:
        return "broken"
    return "ambiguous"


def load_sections(path):
    if path and os.path.isfile(path):
        return exec_sections(path)
    return None


def _load_offset_recipe(proj):
    """Per-project offset-validation recipe: data/<id>/offsets.json -> symbols."""
    path = os.path.join("data", proj["id"], "offsets.json")
    if os.path.isfile(path):
        with open(path) as fh:
            return json.load(fh).get("symbols", {})
    return {}


def validate(gamedata, bins, offset_recipe=None, image_linux=None):
    """bins = {(platform, library): sections_or_None}.

    Signature entries are byte-scanned as before. `offsets` entries are validated
    via lib_offset (Itanium RTTI walk + cached target sig) when image_linux is
    given; otherwise they surface as no_binary. Windows offsets: not yet.
    """
    results = []
    for name, entry in gamedata.items():
        sigs = entry.get("signatures")
        if not sigs:
            if "offsets" in entry:
                continue  # handled by validate_offsets() below
            results.append({
                "name": name,
                "kind": "unknown",
                "platforms": {},
            })
            continue

        library = sigs.get("library", "server")
        plats = {}
        for plat in ("linux", "windows"):
            sig = sigs.get(plat)
            if not sig:
                plats[plat] = {"status": "missing_sig", "matches": None,
                               "library": library, "sig": None}
                continue
            secs = bins.get((plat, library))
            if secs is None:
                plats[plat] = {"status": "no_binary", "matches": None,
                               "library": library, "sig": sig}
                continue
            n = count_matches(sig_to_regex(sig), secs)
            plats[plat] = {"status": classify(n), "matches": n,
                           "library": library, "sig": sig}
        results.append({"name": name, "kind": "signature",
                        "library": library, "platforms": plats})

    # Offset entries: RTTI-walk validation (linux/Itanium). Always emitted so
    # every `offsets` entry appears with a real status instead of offset_only.
    results.extend(validate_offsets(gamedata, offset_recipe or {}, image_linux))
    return results


# Snapshot module names against the gamedata `library` vocabulary the binaries
# are keyed by. client/ is not downloaded, so symbols living there get no_binary.
MODULE_LIBRARY = {"server": "server", "engine": "engine2"}


def apply_reference(results, gamedata, snap, bins=None):
    """Annotate scan results with what the reference analysis says.

    Signature blocks gain a `reference` sub-block and are otherwise untouched -
    the scan owns the ok/broken/ambiguous verdict. Offset blocks are different:
    where the recipe path had nothing to say (no_recipe/review) the reference
    supplies a real verdict, and windows offset blocks are created here because
    nothing else produces them.
    """
    if snap is None:
        return
    for r in results:
        if r["kind"] == "signature":
            for plat, info in r["platforms"].items():
                info["reference"] = _sig_reference(snap, r["name"], plat,
                                                   info.get("sig"))
        elif r["kind"] == "offset":
            entry = gamedata.get(r["name"], {})
            for plat in ("linux", "windows"):
                ours = (entry.get("offsets") or {}).get(plat)
                block = _offset_reference(snap, r["name"], plat, ours)
                if plat in r["platforms"]:
                    _merge_offset(r["platforms"][plat], block, plat)
                elif ours is not None or block["reference"].get("value"):
                    # An offset the gamedata declares gets a verdict even when
                    # that verdict is "nothing to compare against". Dropping the
                    # block instead is what made windows offsets invisible.
                    r["platforms"][plat] = block
                if plat in r["platforms"]:
                    _apply_anchor(r["platforms"][plat], snap, r["name"], plat,
                                  ours, bins)
                    _apply_bounds(r["platforms"][plat], snap, r["name"], plat,
                                  ours)


def _sig_reference(snap, name, plat, ours):
    ref = snap.signature(name, plat)
    if ref is None:
        # A record can exist and still carry no byte pattern, which is a
        # different thing from the symbol never having been analysed.
        return {"status": "no_sig" if snap.kind(name, plat) else "no_reference"}
    relation = SYM.sig_relation(ours, ref)
    if relation == "conflict":
        return {"status": "outdated", "sig": ref, "relation": relation}
    return {"status": "match", "relation": relation}


def _offset_reference(snap, name, plat, ours):
    """A platform block carrying only the reference verdict.

    Used verbatim for windows, where nothing else produces an offset block, and
    merged into the recipe result for linux.
    """
    value, method = snap.offset(name, plat)
    if value is None:
        return {"status": "no_recipe", plat: ours, "method": "reference",
                "reference": {"status": "no_reference", "reason": method}}
    ref = {"value": value, "source": method}
    if ours is None:
        ref["status"] = "no_gamedata_value"
        status = "review"
    elif int(ours) == value:
        ref["status"] = "match"
        status = "ok"
    else:
        ref["status"] = "mismatch"
        status = "stale"
    block = {"status": status, plat: ours, "method": "reference",
             "reference": ref}
    if status == "stale":
        block["found_%s" % plat] = value
    return block


def _sections_for(snap, name, plat, bins):
    library = MODULE_LIBRARY.get(snap.module(name, plat))
    return bins.get((plat, library)) if bins and library else None


def _apply_anchor(info, snap, name, plat, ours, bins):
    """Read the offset back out of our own binary, if the reference pins it.

    This outranks both the recipe and the reference: those describe how the value
    was derived somewhere else, this one is measured here. A disagreement is
    therefore a real `stale`, not a version gap.
    """
    anchor = snap.anchor(name, plat, expected=ours)
    if not anchor:
        return
    sections = _sections_for(snap, name, plat, bins)
    if sections is None:
        info["anchor"] = {"status": "no_binary"}
        return
    derive = (ANCHOR.derive_index if anchor["kind"] == "vfunc"
              else ANCHOR.derive_member)
    value, status = derive(sections, anchor["sig"], anchor["expected"],
                           anchor["disp_index"])
    if value is None:
        info["anchor"] = {"status": status}
        return
    info["anchor"] = {"status": status, "value": value, "kind": anchor["kind"],
                      "via": anchor["via"]}
    if ours is None:
        return
    if int(ours) == value:
        info["status"] = "ok"
        info["method"] = "anchor"
    else:
        info["status"] = "stale"
        info["method"] = "anchor"
        info["found_%s" % plat] = value


def _apply_bounds(info, snap, name, plat, ours):
    """An index at or past the end of the vtable is wrong on its own terms."""
    if ours is None:
        return
    length = snap.vtable_len(name, plat)
    if length is None:
        return
    info["bounds"] = {"vtable_len": length, "in_range": int(ours) < length}
    if not info["bounds"]["in_range"]:
        info["status"] = "stale"
        info.setdefault("method", "bounds")


def _merge_offset(existing, block, plat):
    """Fold a reference verdict into a recipe-derived block.

    The recipe and the reference derive the same integer by different routes, so
    a disagreement is kept visible rather than silently resolved. The reference
    only takes over the verdict where the recipe had no answer.
    """
    ref = block["reference"]
    existing["reference"] = ref
    if ref["status"] == "mismatch":
        existing["status"] = "stale"
        existing.setdefault("found_%s" % plat, ref["value"])
    elif ref["status"] == "match" and existing.get("status") in ("no_recipe",
                                                                "review"):
        existing["status"] = "ok"
        existing["method"] = "reference"


_OFFSET_STATUS_KEY = {
    "ok": "offset_ok", "stale": "offset_stale", "review": "offset_review",
    "no_recipe": "offset_no_recipe", "no_binary": "no_binary",
}


def tally_and_broken(results):
    tally = {"ok": 0, "broken": 0, "ambiguous": 0, "no_binary": 0,
             "missing_sig": 0,
             "offset_ok": 0, "offset_stale": 0, "offset_review": 0,
             "offset_no_recipe": 0,
             # Advisory: the sig still resolves, the reference has moved on.
             "sig_outdated": 0}
    broken = []
    for r in results:
        if r["kind"] == "unknown":
            continue
        for plat, info in r["platforms"].items():
            st = info["status"]
            if r["kind"] == "offset":
                tally[_OFFSET_STATUS_KEY.get(st, "offset_review")] += 1
                if st == "stale":
                    broken.append("%s (%s offset stale)" % (r["name"], plat))
            else:
                tally[st] = tally.get(st, 0) + 1
                if st == "broken":
                    broken.append("%s (%s)" % (r["name"], plat))
                if (info.get("reference") or {}).get("status") == "outdated":
                    tally["sig_outdated"] += 1
    return tally, broken


def validate_project(proj, bins, manifest, images=None, snap=None):
    """Validate one project; write reports/<id>/status.json. Return broken list."""
    gd_path = P.gamedata_path(proj)
    with open(gd_path) as fh:
        gamedata = json.load(fh)

    offset_recipe = _load_offset_recipe(proj)
    image_linux = (images or {}).get("linux")
    results = validate(gamedata, bins, offset_recipe=offset_recipe,
                       image_linux=image_linux)
    apply_reference(results, gamedata, snap, bins)
    tally, broken = tally_and_broken(results)

    out = {
        "project": proj["id"],
        "manifest": manifest,
        # Version only, never the snapshot commit: a commit sha would move on
        # every upstream push and churn a commit + post out of every run.
        "reference": snap.gamever if snap else None,
        "gamedata_source": "%s %s" % (proj["repo"], proj["path"]),
        "tally": tally,
        "results": results,
    }
    out_path = P.status_path(proj)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=2)

    print("[%s] validated %d entries -> %s" % (proj["id"], len(results), out_path))
    print("[%s] tally: %s" % (proj["id"], json.dumps(tally)))
    if tally.get("sig_outdated"):
        print("[%s] %d signature(s) outdated vs reference %s"
              % (proj["id"], tally["sig_outdated"], snap.gamever))
    if broken:
        print("[%s] BROKEN: %s" % (proj["id"], ", ".join(broken)))
    return broken


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects", default=P.REGISTRY)
    ap.add_argument("--project", default=None, help="validate only this id")
    ap.add_argument("--linux", default=None, help="libserver.so")
    ap.add_argument("--windows", default=None, help="server.dll")
    ap.add_argument("--linux-engine2", default=None, help="libengine2.so")
    ap.add_argument("--windows-engine2", default=None, help="engine2.dll")
    ap.add_argument("--manifest", default="data/manifest.json")
    ap.add_argument("--symbols", default=None,
                    help="reference snapshot from fetch_symbols.py; omit to "
                         "validate by byte-scanning alone")
    args = ap.parse_args()

    manifest = None
    if os.path.isfile(args.manifest):
        with open(args.manifest) as fh:
            manifest = json.load(fh)

    bins = {
        ("linux", "server"): load_sections(args.linux),
        ("windows", "server"): load_sections(args.windows),
        ("linux", "engine2"): load_sections(args.linux_engine2),
        ("windows", "engine2"): load_sections(args.windows_engine2),
    }
    # Full VA-mapped image for RTTI offset validation (linux/server only for
    # now; windows/MSVC RTTI is the follow-up).
    images = {"linux": open_image(args.linux)}

    snap = None
    if args.symbols and os.path.isfile(args.symbols):
        snap = SYM.load(args.symbols, SYM.load_aliases())
        print("reference %s (%d records)"
              % (snap.gamever, len(snap.raw.get("records", []))))
    elif args.symbols:
        print("no reference snapshot at %s - scanning only" % args.symbols,
              file=sys.stderr)

    projects = P.load(args.projects, only=args.project)
    any_broken = False
    for proj in projects:
        broken = validate_project(proj, bins, manifest, images, snap)
        any_broken = any_broken or bool(broken)

    return 1 if any_broken else 0


if __name__ == "__main__":
    sys.exit(main())
