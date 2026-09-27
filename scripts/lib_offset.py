"""Offset validation on top of lib_rtti. Stdlib only.

IMPORTANT: gamedata has two distinct entry types and this module only concerns
the *offset* type.
  - `signatures` = a byte pattern that locates a FUNCTION -> validated by scanning
    (lib_sig, in validate_sigs.py). Not handled here.
  - `offsets`    = an INTEGER (vtable slot index, or a struct-member byte offset)
    -> validated here by re-deriving the integer and comparing.

The per-entry `offset_sig` in a recipe is NOT a gamedata signature: it is an
internal validation anchor (a byte pattern that pins the member-access
instruction) used only to read back the displacement so we can compare it to the
stored gamedata *offset* integer. Keep the two ideas separate.

Tiers for `offsets` entries:
  vtable / anchored   (kind=vtable + target_sig): relocate the target function's
             head sig -> unique VA, RTTI-walk the class vtable, confirm slot N ==
             that VA. Reports the new index on mismatch.
  vtable / structural (kind=vtable, no sig): slot N in range and points to .text.
  structoffset        (kind=structoffset + offset_sig + disp_tok_pos): relocate
             the offset_sig, read the displacement bytes, compare to N.

Kinds with no usable anchor (member offsets into non-RTTI managers, abstract
interfaces) get no_recipe -> resolve with GDT (cross-build relocate) in the GUI.

Address/global entries (plugify-style signature + step chain) are a separate
concern -> validate_address_chain(); they are not `offsets`.
"""


def validate_offset_entry(image, rec):
    """Return a per-platform (linux) status dict for one offsets entry."""
    N = rec.get("linux")
    kind = rec.get("kind")
    if image is None:
        return {"status": "no_binary", "linux": N}
    if N is None:
        return {"status": "review", "reason": "no-linux-offset"}
    cls = rec.get("resolve_vtable_class") or rec.get("vtable_class")
    sig = rec.get("target_sig")

    if kind == "structoffset":
        return _validate_structoffset(image, rec, N)

    if kind != "vtable" or not cls:
        # member offsets into non-RTTI managers / abstract interfaces: no usable
        # byte anchor -> resolve with GDT (cross-build relocate) in the GUI. The
        # recipe's `resolve` hint says what to do; surface it in the result.
        return {"status": "no_recipe", "linux": N, "kind": kind,
                "resolve": rec.get("resolve", "gdt"),
                "note": rec.get("note")}

    vts = image.primary_vtables(cls)
    if not vts:
        return {"status": "review", "reason": "no-vtable", "linux": N,
                "vtable_class": cls}
    vt = vts[0]
    slot_fn = image.slot_func(vt, N)

    if sig:
        vas = image.find_sig_vas(sig, limit=3)
        if len(vas) != 1:
            return {"status": "review", "linux": N, "method": "anchored",
                    "reason": "target-sig-%s" % ("none" if not vas else "multi")}
        func = vas[0]
        if slot_fn == func:
            return {"status": "ok", "linux": N, "method": "anchored",
                    "func_va": hex(func)}
        new = image.find_func_slot(vt, func)
        return {"status": "stale", "linux": N, "method": "anchored",
                "found_linux": new, "func_va": hex(func)}

    # structural fallback (no cached sig, e.g. trivial accessors)
    vlen = image.vtable_len(vt)
    if slot_fn is not None and image.in_exec(slot_fn) and N < vlen:
        return {"status": "ok", "linux": N, "method": "structural",
                "vtable_len": vlen}
    return {"status": "review", "linux": N, "method": "structural",
            "reason": "slot-out-of-range-or-not-text", "vtable_len": vlen}


def _validate_structoffset(image, rec, N):
    """Re-derive a struct-member offset from a cached `offset_sig`.

    offset_sig pins the member-access instruction with the displacement bytes
    wildcarded; disp_tok_pos is the byte position of the displacement inside the
    match. Read those bytes and compare to the stored gamedata offset N. The sig
    is a validation anchor only -- the thing being validated is the OFFSET int.
    """
    osig = rec.get("offset_sig")
    pos = rec.get("disp_tok_pos")
    size = rec.get("disp_size", 4)
    if not osig or pos is None:
        return {"status": "no_recipe", "linux": N, "kind": "structoffset",
                "resolve": rec.get("resolve", "gdt"),
                "reason": "offset_sig-missing"}
    vas = image.find_sig_vas(osig, limit=3)
    if len(vas) != 1:
        return {"status": "review", "linux": N, "method": "structoffset",
                "reason": "offset-sig-%s" % ("none" if not vas else "multi")}
    disp = image.read_uint(vas[0] + pos, size)
    if disp is None:
        return {"status": "review", "linux": N, "method": "structoffset",
                "reason": "disp-read-failed"}
    if disp == N:
        return {"status": "ok", "linux": N, "method": "structoffset"}
    return {"status": "stale", "linux": N, "method": "structoffset",
            "found_linux": disp}


def validate_address_chain(image, rec):
    """Validate a plugify-style address/global entry: a signature anchor plus a
    step chain (offset / read_offs32 / read) that resolves to a global address.

    This is for ADDRESS/global entries, NOT `offsets`. There is no stored integer
    to compare, so validation = "the chain resolves to a sane (non-null, mapped)
    address". Steps:
      {"offset": n}       va += n
      {"read_offs32": n}  disp = int32 at va+n; va = va + n + 4 + disp  (RIP-rel)
      {"read": n}         va = *(va + n)   (dereference qword)
    """
    if image is None:
        return {"status": "no_binary"}
    sig = rec.get("signature")
    steps = rec.get("steps") or rec.get("linux")
    if not sig or not isinstance(steps, list):
        return {"status": "no_recipe", "reason": "missing-signature-or-steps"}
    vas = image.find_sig_vas(sig, limit=3)
    if len(vas) != 1:
        return {"status": "review",
                "reason": "anchor-sig-%s" % ("none" if not vas else "multi")}
    va = vas[0]
    for step in steps:
        if "offset" in step:
            va += int(step["offset"])
        elif "read_offs32" in step:
            n = int(step["read_offs32"])
            disp = image.read_int32(va + n)
            if disp is None:
                return {"status": "review", "reason": "read_offs32-failed"}
            va = va + n + 4 + disp
        elif "read" in step:
            va = image.qword(va + int(step["read"]))
            if va is None:
                return {"status": "review", "reason": "read-failed"}
        else:
            return {"status": "review", "reason": "unknown-step"}
    if image._sec_of(va) is None:
        return {"status": "stale", "reason": "resolved-address-unmapped",
                "address": hex(va)}
    return {"status": "ok", "address": hex(va)}


def validate_offsets(gamedata, recipe_symbols, image_linux):
    """Yield result dicts (kind='offset') for every gamedata `offsets` entry.

    recipe_symbols: {symbol_name: recipe}. Entries with an `offsets` block but no
    recipe get status 'no_recipe'. Windows is not validated yet (linux first).
    """
    results = []
    for name, entry in gamedata.items():
        if "offsets" not in entry:
            continue
        rec = dict(recipe_symbols.get(name) or {})
        # The value under test is the one the gamedata ships, never the recipe's.
        # A recipe records HOW to check an entry (kind, class, anchor sig); the
        # integer it was written with is a snapshot of one build. Letting it win
        # froze every check at that build: on 14185 Respawn/Teleport/CommitSuicide/
        # FindPickerEntity were reported broken against their 14171 slots while
        # the gamedata already shipped the correct ones.
        shipped = entry["offsets"].get("linux")
        if isinstance(shipped, int) and not isinstance(shipped, bool):
            rec["linux"] = shipped
        elif "linux" not in rec:
            rec["linux"] = shipped
        if not rec.get("kind"):
            rec["kind"] = None
        lin = validate_offset_entry(image_linux, rec)
        results.append({
            "name": name,
            "kind": "offset",
            "offsets": entry["offsets"],
            "platforms": {"linux": lin},
        })
    return results
