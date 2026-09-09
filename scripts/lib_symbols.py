"""Reference-symbol lookup on top of a CS2_VibeSignatures snapshot. Stdlib only.

Why this exists. Byte-scanning (lib_sig) proves a signature still resolves in the
binary we downloaded, but it cannot tell us the upstream analysis has since moved
to a different pattern - a sig that matches exactly once is reported ok forever,
even when the project it came from has already replaced it. And an `offsets`
entry has no bytes to scan at all: lib_offset can only check it where somebody
hand-wrote a recipe in data/<id>/offsets.json, linux only.

A snapshot fixes both. It is one JSON file per game version holding every symbol
the upstream analysis resolved, for linux AND windows:

    function         func_sig / func_va / func_rva / func_size
    virtualFunction  vfunc_index / vfunc_offset / vtable_name (+ func_sig, 731/1354)
    structMember     offset (hex) / offset_sig / size
    vtable           vtable_class + full {slot: va} dump
    global           gv_va / gv_sig
    patch            patch_sig / patch_bytes

`offset()` reads the integer straight out of virtualFunction/structMember, so a
gamedata offset can be compared against the reference on both platforms with no
recipe and no RTTI walk. Where the virtualFunction record is missing but the
function and its class vtable are both present, `derive_slot()` recovers the
index by finding func_va in the vtable dump - verified to reproduce the known
windows indices exactly (CCSPlayerController_ChangeTeam 103, CBaseEntity_Teleport
163).

Names. Gamedata keys, snapshot `symbolName` and the artifact file name spell the
same symbol three ways (`A::b`, `A.b`, `A_b`), so every lookup goes through
`norm()`. Genuine renames are not a normalization problem - feed those in as an
alias map (see load_aliases).
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_sig import WILDCARD_TOKENS, sig_tokens as raw_tokens  # noqa: E402

# gamedata `library` -> snapshot module name.
LIBRARY_MODULE = {"server": "server", "engine2": "engine", "client": "client"}


def norm(name):
    """Fold the three spellings of one symbol onto a single key."""
    return re.sub(r"[^a-z0-9_]", "_", name.replace("::", "_").replace(".", "_").lower())


def sig_tokens(sig):
    """Tokenise a signature and fold every wildcard spelling onto one form.

    lib_sig already accepts both the spaced and the \\x-escaped style and knows
    the wildcard spellings (?, ??, *, 2A); reuse it so a comparison here can
    never disagree with what the scanner actually matched.
    """
    return ["?" if t in WILDCARD_TOKENS else t.upper()
            for t in raw_tokens(sig or "")]


def sig_relation(ours, ref):
    """How our gamedata pattern relates to the reference pattern.

    "equal"       identical token for token
    "compatible"  same length, and every difference is a wildcard on one side.
                  One pattern is simply broader than the other (upstream pinned
                  a byte we wildcard, or the reverse). Both still describe the
                  same function, so this is not a stale signature.
    "prefix"      one pattern is a compatible prefix of the other. The two were
                  cut at different lengths from the same function head, which is
                  a uniqueness question, not a staleness one.
    "conflict"    two concrete bytes disagree. The upstream analysis has moved to
                  a different pattern.
    """
    a, b = sig_tokens(ours), sig_tokens(ref)
    if not a or not b:
        return None
    for x, y in zip(a, b):
        if x != y and x != "?" and y != "?":
            return "conflict"
    if a == b:
        return "equal"
    return "compatible" if len(a) == len(b) else "prefix"


def same_sig(a, b):
    return sig_relation(a, b) in ("equal", "compatible")


def load_aliases(path=os.path.join("data", "symbol_aliases.json")):
    """{gamedata name: reference name}. Optional; missing file means no aliases."""
    if not os.path.isfile(path):
        return {}
    with open(path) as fh:
        return json.load(fh)


class Snapshot(object):
    """One gamesymbols snapshot, indexed for per-symbol per-platform lookup."""

    def __init__(self, data, aliases=None):
        self.raw = data
        self.gamever = data.get("source", {}).get("gameVersion")
        self.published = data.get("source", {}).get("lastPublishTime")
        self.binaries = data.get("binaries", {})
        self.aliases = {norm(k): norm(v) for k, v in (aliases or {}).items()}

        self._by_key = {}
        self._vtables = {}
        for rec in data.get("records", []):
            key = norm(rec.get("artifact") or rec.get("symbolName") or "")
            self._by_key.setdefault(key, {})[rec["platform"]] = rec
            if rec["kind"] == "vtable":
                cls = norm(rec["payload"]["vtable_class"])
                slots = {int(s): int(va, 16)
                         for s, va in rec["payload"]["vtable_entries"].items()}
                self._vtables.setdefault(cls, {})[rec["platform"]] = slots

    # -- lookup ----------------------------------------------------------
    def _key(self, name):
        key = norm(name)
        return self.aliases.get(key, key)

    def record(self, name, platform):
        return self._by_key.get(self._key(name), {}).get(platform)

    def platforms(self, name):
        return set(self._by_key.get(self._key(name), {}))

    def module(self, name, platform):
        """Which binary this symbol lives in (server / engine / client)."""
        rec = self.record(name, platform)
        return rec["module"] if rec else None

    def kind(self, name, platform):
        rec = self.record(name, platform)
        return rec["kind"] if rec else None

    def signature(self, name, platform):
        """Reference byte pattern for a function, or None.

        func_sig lives on `function` records and on most `virtualFunction` ones.
        vfunc_sig is deliberately not used here: it pins the call site, not the
        function body, so it is not comparable to a gamedata signature.
        """
        rec = self.record(name, platform)
        if not rec:
            return None
        return rec["payload"].get("func_sig")

    def offset(self, name, platform):
        """(value, method) for an offsets entry, or (None, reason)."""
        rec = self.record(name, platform)
        if not rec:
            return None, "no_reference"
        payload, kind = rec["payload"], rec["kind"]
        if kind == "virtualFunction" and "vfunc_index" in payload:
            return int(payload["vfunc_index"]), "vfunc_index"
        if kind == "structMember" and "offset" in payload:
            return int(str(payload["offset"]), 16), "struct_member"
        derived = self.derive_slot(name, platform)
        if derived is not None:
            return derived, "vtable_derived"
        return None, "kind_%s" % kind

    def derive_slot(self, name, platform, vtable_class=None):
        """Recover a vtable index by locating func_va in the class vtable dump.

        Used when the reference has the function but no virtualFunction record.
        Returns None when the class vtable is absent or the address appears zero
        or many times (a thunk, or a slot shared by several entries).
        """
        rec = self.record(name, platform)
        if not rec:
            return None
        va = rec["payload"].get("func_va")
        if not va:
            return None
        cls = vtable_class or rec["payload"].get("vtable_name")
        if not cls:
            # "CBaseEntity_Teleport" -> try the longest class prefix we know.
            stem = norm(name)
            cands = [c for c in self._vtables if stem.startswith(c + "_")]
            if not cands:
                return None
            cls = max(cands, key=len)
        slots = self._vtables.get(norm(cls), {}).get(platform)
        if not slots:
            return None
        hits = [s for s, addr in slots.items() if addr == int(va, 16)]
        return hits[0] if len(hits) == 1 else None

    def anchor(self, name, platform, expected=None):
        """The byte anchor that pins this entry's offset, or None.

        Returns {"sig", "expected", "disp_index", "kind", "via"} for lib_anchor
        to re-derive the value from the binary we actually downloaded, instead of
        trusting an integer recorded against some other build.

        The two dedicated anchor kinds carry their own expected value, so they
        derive the offset independently. `func_sig` is the fallback: the analysis
        sometimes files a member as a plain `function` whose pattern happens to
        span the access instruction, for example

            48 83 C1 70 E9 D7 EC 44 00      add rcx, 0x70

        where 0x70 is the member offset. There is no recorded integer to pair it
        with, so the caller supplies one (`expected`, in practice the gamedata's
        own value) and the check becomes "does our binary still encode that
        offset at the site the analysis found". Weaker, because it cannot produce
        a value from nothing, but it still catches a moved offset: once the exact
        pattern stops matching, the read back reports what replaced it.
        """
        rec = self.record(name, platform)
        if not rec:
            return None
        p = rec["payload"]
        if rec["kind"] == "virtualFunction" and p.get("vfunc_sig"):
            return {"sig": p["vfunc_sig"], "kind": "vfunc", "via": "vfunc_sig",
                    "expected": int(str(p["vfunc_offset"]), 16),
                    "disp_index": None}
        if rec["kind"] == "structMember" and p.get("offset_sig"):
            return {"sig": p["offset_sig"], "kind": "member", "via": "offset_sig",
                    "expected": int(str(p["offset"]), 16),
                    "disp_index": p.get("offset_sig_disp")}
        if expected is not None and p.get("func_sig"):
            return {"sig": p["func_sig"], "kind": "member", "via": "func_sig",
                    "expected": int(expected), "disp_index": None}
        return None

    def vtable_len(self, name, platform, vtable_class=None):
        """Slot count of the class this entry's index addresses, or None.

        Enough on its own to prove an index wrong: a slot past the end of the
        vtable cannot be right, whether or not the symbol itself is covered.
        """
        cls = vtable_class
        if cls is None:
            rec = self.record(name, platform)
            cls = (rec or {}).get("payload", {}).get("vtable_name")
        if not cls:
            return None
        payload = self._vtable_payload(norm(cls), platform)
        if payload is None:
            return None
        num = payload.get("vtable_numvfunc")
        return int(num) if num is not None else None

    def _vtable_payload(self, key, platform):
        for rec in self.raw.get("records", []):
            if (rec["kind"] == "vtable" and rec["platform"] == platform
                    and norm(rec["payload"]["vtable_class"]) == key):
                return rec["payload"]
        return None

    # -- binaries --------------------------------------------------------
    def binary_sha(self, module, platform):
        return self.binaries.get(module, {}).get(platform, {}).get("sha256")

    def library_sha(self, library, platform):
        return self.binary_sha(LIBRARY_MODULE.get(library, library), platform)


def load(path, aliases=None):
    with open(path) as fh:
        return Snapshot(json.load(fh), aliases)
