"""Offset-validation decision logic (lib_offset). Mock Image -> no binary needed.

The real RTTI walk (lib_rtti) is exercised against downloaded binaries in the
validate step; here we pin the classification logic: anchored ok/stale,
structural ok/review, no-vtable, no-recipe, ambiguous target sig, no binary.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from lib_offset import (validate_offset_entry, validate_offsets,  # noqa: E402
                        validate_address_chain)


class FakeImage:
    """Minimal stand-in for lib_rtti.Image driven by explicit fixtures."""

    def __init__(self, vtables=None, slots=None, sig_hits=None, exec_vas=None,
                 vlen=300, mem=None, mapped=None):
        self._vtables = vtables or {}          # class -> [vtable_va]
        self._slots = slots or {}              # (vtable_va, n) -> func_va
        self._sig_hits = sig_hits or {}        # sig -> [va]
        self._exec = set(exec_vas or [])       # VAs that are "in .text"
        self._vlen = vlen
        self._mem = mem or {}                  # va -> (size -> int) via read_uint
        self._mapped = set(mapped or [])       # VAs considered mapped

    def read_uint(self, va, size):
        return self._mem.get((va, size))

    def read_int32(self, va):
        v = self._mem.get((va, 4))
        return v if v is None or v < 0x80000000 else v - 0x100000000

    def qword(self, va):
        return self._mem.get((va, 8))

    def _sec_of(self, va):
        return object() if va in self._mapped else None

    def primary_vtables(self, cls):
        return list(self._vtables.get(cls, []))

    def slot_func(self, vt, n):
        return self._slots.get((vt, n))

    def find_sig_vas(self, sig, limit=8):
        return list(self._sig_hits.get(sig, []))[:limit]

    def in_exec(self, va):
        return va in self._exec

    def vtable_len(self, vt, cap=1024):
        return self._vlen

    def find_func_slot(self, vt, func, cap=1024):
        for (v, n), f in self._slots.items():
            if v == vt and f == func:
                return n
        return None


class TestValidateOffsetEntry(unittest.TestCase):
    def test_anchored_ok(self):
        img = FakeImage(vtables={"C": [0x1000]}, slots={(0x1000, 5): 0xABC},
                        sig_hits={"AA BB": [0xABC]}, exec_vas={0xABC})
        r = validate_offset_entry(img, {"kind": "vtable", "vtable_class": "C",
                                        "linux": 5, "target_sig": "AA BB"})
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["method"], "anchored")

    def test_anchored_stale_reports_new_index(self):
        img = FakeImage(vtables={"C": [0x1000]},
                        slots={(0x1000, 5): 0xDEAD, (0x1000, 7): 0xABC},
                        sig_hits={"AA BB": [0xABC]}, exec_vas={0xABC, 0xDEAD})
        r = validate_offset_entry(img, {"kind": "vtable", "vtable_class": "C",
                                        "linux": 5, "target_sig": "AA BB"})
        self.assertEqual(r["status"], "stale")
        self.assertEqual(r["found_linux"], 7)

    def test_anchored_ambiguous_sig_is_review(self):
        img = FakeImage(vtables={"C": [0x1000]}, slots={(0x1000, 5): 0xABC},
                        sig_hits={"AA BB": [0xABC, 0x999]}, exec_vas={0xABC})
        r = validate_offset_entry(img, {"kind": "vtable", "vtable_class": "C",
                                        "linux": 5, "target_sig": "AA BB"})
        self.assertEqual(r["status"], "review")
        self.assertIn("multi", r["reason"])

    def test_structural_ok_without_sig(self):
        img = FakeImage(vtables={"C": [0x1000]}, slots={(0x1000, 5): 0xABC},
                        exec_vas={0xABC}, vlen=300)
        r = validate_offset_entry(img, {"kind": "vtable", "vtable_class": "C",
                                        "linux": 5})
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["method"], "structural")

    def test_structural_out_of_range_is_review(self):
        img = FakeImage(vtables={"C": [0x1000]}, slots={(0x1000, 5): 0xABC},
                        exec_vas={0xABC}, vlen=3)
        r = validate_offset_entry(img, {"kind": "vtable", "vtable_class": "C",
                                        "linux": 5})
        self.assertEqual(r["status"], "review")

    def test_no_vtable_is_review(self):
        img = FakeImage()
        r = validate_offset_entry(img, {"kind": "vtable", "vtable_class": "X",
                                        "linux": 5, "target_sig": "AA"})
        self.assertEqual(r["status"], "review")
        self.assertEqual(r["reason"], "no-vtable")

    def test_non_vtable_kind_is_no_recipe(self):
        img = FakeImage()
        r = validate_offset_entry(img, {"kind": "structoffset", "linux": 104})
        self.assertEqual(r["status"], "no_recipe")

    def test_no_binary(self):
        r = validate_offset_entry(None, {"kind": "vtable", "linux": 5})
        self.assertEqual(r["status"], "no_binary")


class TestStructOffset(unittest.TestCase):
    def test_structoffset_ok(self):
        # match at 0x500, disp32 at +7 reads 576 == stored offset
        img = FakeImage(sig_hits={"S": [0x500]}, mem={(0x507, 4): 576})
        r = validate_offset_entry(img, {"kind": "structoffset", "linux": 576,
                                        "offset_sig": "S", "disp_tok_pos": 7,
                                        "disp_size": 4})
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["method"], "structoffset")

    def test_structoffset_stale_reports_found(self):
        img = FakeImage(sig_hits={"S": [0x500]}, mem={(0x507, 4): 600})
        r = validate_offset_entry(img, {"kind": "structoffset", "linux": 576,
                                        "offset_sig": "S", "disp_tok_pos": 7,
                                        "disp_size": 4})
        self.assertEqual(r["status"], "stale")
        self.assertEqual(r["found_linux"], 600)

    def test_structoffset_missing_sig_is_no_recipe_with_resolve(self):
        r = validate_offset_entry(FakeImage(), {"kind": "structoffset",
                                                "linux": 104, "resolve": "gdt"})
        self.assertEqual(r["status"], "no_recipe")
        self.assertEqual(r["resolve"], "gdt")

    def test_structoffset_ambiguous_sig_is_review(self):
        img = FakeImage(sig_hits={"S": [0x500, 0x900]})
        r = validate_offset_entry(img, {"kind": "structoffset", "linux": 576,
                                        "offset_sig": "S", "disp_tok_pos": 7})
        self.assertEqual(r["status"], "review")

    def test_non_vtable_kind_carries_resolve_hint(self):
        r = validate_offset_entry(FakeImage(), {"kind": "member", "linux": 80,
                                                "resolve": "gdt"})
        self.assertEqual(r["status"], "no_recipe")
        self.assertEqual(r["resolve"], "gdt")


class TestAddressChain(unittest.TestCase):
    def test_read_offs32_then_read_resolves(self):
        # anchor sig at 0x1000; step read_offs32:6 -> disp at 0x1006 == 0x40,
        # va = 0x1006 + 4 + 0x40 = 0x104A; then read:0 -> qword -> 0x2000 (mapped)
        img = FakeImage(sig_hits={"CSource2Server::Init": [0x1000]},
                        mem={(0x1006, 4): 0x40, (0x104A, 8): 0x2000},
                        mapped={0x2000})
        r = validate_address_chain(img, {
            "signature": "CSource2Server::Init",
            "steps": [{"read_offs32": 6}, {"read": 0}]})
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["address"], hex(0x2000))

    def test_unmapped_resolution_is_stale(self):
        img = FakeImage(sig_hits={"S": [0x1000]}, mem={(0x1000, 8): 0xDEAD})
        r = validate_address_chain(img, {"signature": "S",
                                         "steps": [{"read": 0}]})
        self.assertEqual(r["status"], "stale")

    def test_missing_anchor_is_review(self):
        img = FakeImage(sig_hits={})
        r = validate_address_chain(img, {"signature": "S", "steps": [{"read": 0}]})
        self.assertEqual(r["status"], "review")


class TestValidateOffsets(unittest.TestCase):
    def test_only_offset_entries_emitted_linux_only(self):
        gd = {
            "A": {"signatures": {"linux": "x"}},          # skipped (sig)
            "B": {"offsets": {"linux": 5, "windows": 6}},  # validated
        }
        img = FakeImage(vtables={"C": [0x1000]}, slots={(0x1000, 5): 0xABC},
                        sig_hits={"S": [0xABC]}, exec_vas={0xABC})
        recipe = {"B": {"kind": "vtable", "vtable_class": "C", "linux": 5,
                        "target_sig": "S"}}
        out = validate_offsets(gd, recipe, img)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["name"], "B")
        self.assertEqual(out[0]["kind"], "offset")
        self.assertEqual(set(out[0]["platforms"]), {"linux"})
        self.assertEqual(out[0]["platforms"]["linux"]["status"], "ok")

    def test_shipped_value_outranks_stale_recipe_value(self):
        # Recipe written on an old build (slot 272); the gamedata already ships the
        # new slot 276 and the anchor sits there. Must be ok, not "272 -> 276".
        gd = {"R": {"offsets": {"linux": 276, "windows": 274}}}
        img = FakeImage(vtables={"C": [0x1000]},
                        slots={(0x1000, 272): 0xDEAD, (0x1000, 276): 0xABC},
                        sig_hits={"S": [0xABC]}, exec_vas={0xABC, 0xDEAD})
        recipe = {"R": {"kind": "vtable", "vtable_class": "C", "linux": 272,
                        "target_sig": "S"}}
        lin = validate_offsets(gd, recipe, img)[0]["platforms"]["linux"]
        self.assertEqual(lin["status"], "ok")
        self.assertEqual(lin["linux"], 276)

    def test_shipped_value_that_moved_is_still_reported_stale(self):
        # The fix must not hide a real break: gamedata ships 276, anchor is at 280.
        gd = {"R": {"offsets": {"linux": 276}}}
        img = FakeImage(vtables={"C": [0x1000]},
                        slots={(0x1000, 276): 0xDEAD, (0x1000, 280): 0xABC},
                        sig_hits={"S": [0xABC]}, exec_vas={0xABC, 0xDEAD})
        recipe = {"R": {"kind": "vtable", "vtable_class": "C", "linux": 272,
                        "target_sig": "S"}}
        lin = validate_offsets(gd, recipe, img)[0]["platforms"]["linux"]
        self.assertEqual(lin["status"], "stale")
        self.assertEqual(lin["linux"], 276)

    def test_offset_entry_without_recipe_is_no_recipe(self):
        gd = {"B": {"offsets": {"linux": 5}}}
        out = validate_offsets(gd, {}, FakeImage())
        self.assertEqual(out[0]["platforms"]["linux"]["status"], "no_recipe")


if __name__ == "__main__":
    unittest.main()
