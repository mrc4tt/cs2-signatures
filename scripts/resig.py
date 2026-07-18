#!/usr/bin/env python3
"""EXPERIMENTAL: regenerate a broken signature by diffing two game builds.

Not wired into run_all.sh. Stdlib only, like the rest of the pipeline.

Idea: a sig that broke on a game update usually points at a function whose
bytes drifted slightly (new immediates, displacements, register allocation),
not one that vanished. We don't need a disassembler to re-find it:

  1. locate the sig's unique match in the OLD binary (where it still works),
  2. take a window of the function's bytes from that spot,
  3. find the same function in the NEW binary by seeding exact-substring
     anchors from the window and scoring each candidate alignment by byte
     equality,
  4. build a candidate sig at the new location: literal where old==new,
     wildcard where the bytes drifted, extended until unique.

The candidate is a proposal - a human (or the validate step) still confirms
`matches == 1` before it lands in gamedata.

Usage (single sig):
  python3 scripts/resig.py --old OLD.so --new NEW.so \
      --sig "55 48 89 E5 41 57 ..."

Usage (evaluate the whole approach against a real update, using sigs that
still match both builds as ground truth):
  python3 scripts/resig.py --eval --old-dir DIR --new-dir DIR
where each dir holds libserver.so / server.dll / libengine2.so / engine2.dll.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_sig import sig_to_regex, exec_sections  # noqa: E402
from lib_x86 import wildcard_mask  # noqa: E402

WINDOW = 256        # bytes of function context taken from the old binary
ANCHOR_LEN = 12     # length of exact-match seeds searched in the new binary
ANCHOR_STRIDE = 8   # window offset step between seeds
MIN_SCORE = 0.55    # candidate must agree with >=55% of the window's bytes
MAX_SIG = 96        # longest candidate sig we will propose (bytes)
MIN_SIG = 16        # shortest candidate sig we will try


def find_matches(rx, sections, limit=None):
    """[(section_idx, offset), ...] of rx across sections, stop at limit."""
    hits = []
    for i, seg in enumerate(sections):
        for m in rx.finditer(seg):
            hits.append((i, m.start()))
            if limit and len(hits) >= limit:
                return hits
    return hits


def count_upto(rx, sections, limit):
    return len(find_matches(rx, sections, limit=limit))


def window_at(sections, sec_idx, off, size=WINDOW):
    seg = sections[sec_idx]
    return seg[off:off + size]


def map_window(window, new_sections):
    """Find where `window` (bytes from the old build) lives in the new build.

    Seeds candidate alignments from exact ANCHOR_LEN-byte substrings, scores
    each alignment by whole-window byte equality, returns
    (sec_idx, offset, score) for the best one or None.
    """
    candidates = {}
    for woff in range(0, max(1, len(window) - ANCHOR_LEN), ANCHOR_STRIDE):
        anchor = window[woff:woff + ANCHOR_LEN]
        if len(anchor) < ANCHOR_LEN:
            break
        for i, seg in enumerate(new_sections):
            start = 0
            while True:
                pos = seg.find(anchor, start)
                if pos == -1:
                    break
                cand = (i, pos - woff)
                if cand[1] >= 0:
                    candidates.setdefault(cand, 0)
                start = pos + 1
                # a super-common anchor (padding, common prologue) would
                # explode the candidate set; cap per anchor per section
                if len(candidates) > 4096:
                    break
    best = None
    for (i, off) in candidates:
        cand_bytes = window_at(new_sections, i, off, len(window))
        if len(cand_bytes) < len(window) // 2:
            continue
        score = sum(a == b for a, b in zip(window, cand_bytes)) / len(window)
        if best is None or score > best[2]:
            best = (i, off, score)
    if best and best[2] >= MIN_SCORE:
        return best
    return None


def build_candidate(old_window, new_sections, sec_idx, off):
    """Candidate sig at the mapped location, grown until unique in the new
    build. Wildcards are instruction-aware (lib_x86): whole drifted operand
    fields plus always-volatile rel32/RIP-relative fields, so the candidate
    survives the next relink instead of breaking on the first moved address."""
    new_window = window_at(new_sections, sec_idx, off, MAX_SIG)
    mask = wildcard_mask(new_window, old_window)
    toks = ["?" if mask[i] else "%02X" % nb
            for i, nb in enumerate(new_window)]
    if not toks or toks[0] == "?":
        return None  # prologue itself changed; too weak to anchor a sig

    def unique_at(length):
        sig = " ".join(toks[:length])
        return count_upto(sig_to_regex(sig), new_sections, 2) == 1

    # uniqueness is monotonic in length -> binary search the shortest sig
    lo, hi = MIN_SIG, min(MAX_SIG, len(toks))
    if not unique_at(hi):
        return None
    while lo < hi:
        mid = (lo + hi) // 2
        if unique_at(mid):
            hi = mid
        else:
            lo = mid + 1
    # don't end on a wildcard
    length = lo
    while length > MIN_SIG and toks[length - 1] == "?":
        length -= 1
        if not unique_at(length):
            length += 1
            break
    return " ".join(toks[:length])


def regen(sig, old_sections, new_sections):
    """Old sig + both builds -> dict with mapping + candidate sig (or error)."""
    rx = sig_to_regex(sig)
    old_hits = find_matches(rx, old_sections, limit=2)
    if len(old_hits) != 1:
        return {"error": "sig not unique in old binary (%d hits)" % len(old_hits)}
    sec_idx, off = old_hits[0]
    old_window = window_at(old_sections, sec_idx, off)
    mapped = map_window(old_window, new_sections)
    if mapped is None:
        return {"error": "function not found in new binary (score < %.2f)"
                % MIN_SCORE}
    n_sec, n_off, score = mapped
    candidate = build_candidate(old_window, new_sections, n_sec, n_off)
    out = {"old_pos": [sec_idx, off], "new_pos": [n_sec, n_off],
           "score": round(score, 3)}
    if candidate is None:
        out["error"] = "could not build unique candidate at mapped position"
    else:
        out["candidate"] = candidate
    return out


# ---------------------------------------------------------------------------
# Evaluation harness: replay a real update where the sigs did NOT break, so
# each sig's own match in the new build is ground truth for the mapping.
# ---------------------------------------------------------------------------

BIN_FILES = {
    ("linux", "server"): "libserver.so",
    ("windows", "server"): "server.dll",
    ("linux", "engine2"): "libengine2.so",
    ("windows", "engine2"): "engine2.dll",
}


def load_dir(path):
    out = {}
    for key, fn in BIN_FILES.items():
        p = os.path.join(path, fn)
        if os.path.isfile(p):
            out[key] = exec_sections(p)
    return out


def eval_update(old_dir, new_dir, registry):
    import projects as P
    old_bins = load_dir(old_dir)
    new_bins = load_dir(new_dir)
    total = mapped_ok = regen_ok = 0
    failures = []
    for proj in P.load(registry):
        with open(P.gamedata_path(proj)) as fh:
            gamedata = json.load(fh)
        for name, entry in gamedata.items():
            sigs = entry.get("signatures")
            if not sigs:
                continue
            library = sigs.get("library", "server")
            for plat in ("linux", "windows"):
                sig = sigs.get(plat)
                key = (plat, library)
                if not sig or key not in old_bins or key not in new_bins:
                    continue
                total += 1
                label = "%s/%s (%s)" % (proj["id"], name, plat)
                res = regen(sig, old_bins[key], new_bins[key])
                if "error" in res:
                    failures.append((label, res["error"]))
                    continue
                # ground truth: where the (still working) sig sits in new build
                truth = find_matches(sig_to_regex(sig), new_bins[key], limit=2)
                if len(truth) == 1 and tuple(res["new_pos"]) == truth[0]:
                    mapped_ok += 1
                else:
                    failures.append((label, "mapped to %s, truth %s"
                                     % (res["new_pos"], truth)))
                    continue
                cand_hits = find_matches(sig_to_regex(res["candidate"]),
                                         new_bins[key], limit=2)
                if len(cand_hits) == 1 and cand_hits[0] == truth[0]:
                    regen_ok += 1
                else:
                    failures.append((label, "candidate not unique at truth: %s"
                                     % cand_hits))
    print("sigs evaluated : %d" % total)
    print("mapped to truth: %d" % mapped_ok)
    print("regen unique   : %d" % regen_ok)
    for label, why in failures:
        print("FAIL %s: %s" % (label, why))
    return 0 if regen_ok == total else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", help="old binary (sig still matches here)")
    ap.add_argument("--new", help="new binary (sig broke here)")
    ap.add_argument("--sig", help="the broken signature string")
    ap.add_argument("--eval", action="store_true",
                    help="evaluate mapping over every tracked sig")
    ap.add_argument("--old-dir", help="dir with old build binaries (--eval)")
    ap.add_argument("--new-dir", help="dir with new build binaries (--eval)")
    ap.add_argument("--projects", default=None)
    args = ap.parse_args()

    if args.eval:
        if not args.old_dir or not args.new_dir:
            ap.error("--eval needs --old-dir and --new-dir")
        import projects as P
        return eval_update(args.old_dir, args.new_dir,
                           args.projects or P.REGISTRY)

    if not (args.old and args.new and args.sig):
        ap.error("need --old, --new and --sig (or --eval)")
    res = regen(args.sig, exec_sections(args.old), exec_sections(args.new))
    print(json.dumps(res, indent=2))
    return 0 if "candidate" in res else 1


if __name__ == "__main__":
    sys.exit(main())
