"""Unit tests for post_gate's named delta: the "what changed" projection.

fingerprint() (the announce/stay-silent gate) is deliberately name-blind;
named_changes() is the opposite view over the same data. These tests pin the
classification rules, since the Discord report renders them verbatim.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "scripts"))
from post_gate import CHANGE_ORDER, classify, entry_map  # noqa: E402


def sig(name, **plats):
    return {"name": name, "kind": "signature",
            "platforms": {p: dict(v) for p, v in plats.items()}}


class EntryMap(unittest.TestCase):
    def test_flattens_to_kind_name_platform(self):
        status = {"results": [sig("A", linux={"status": "ok", "sig": "48 89"},
                                  windows={"status": "broken"})]}
        m = entry_map(status)
        self.assertEqual(sorted(m), [("signature", "A", "linux"),
                                     ("signature", "A", "windows")])
        self.assertEqual(m[("signature", "A", "linux")]["sig"], "48 89")

    def test_offset_value_comes_from_the_offsets_block(self):
        status = {"results": [{"name": "O", "kind": "offset",
                               "offsets": {"linux": 102},
                               "platforms": {"linux": {"status": "ok"}}}]}
        self.assertEqual(entry_map(status)[("offset", "O", "linux")]["offset"],
                         102)

    def test_reference_verdict_is_not_part_of_an_entry(self):
        """The reference compares our bytes against a third-party analysis of a
        possibly different build, so its verdict is a disagreement between two
        sources rather than a change here. It must not reach the report."""
        status = {"results": [sig("A", linux={"status": "ok", "sig": "48 89",
                                              "reference": {"status":
                                                            "outdated"}})]}
        entry = entry_map(status)[("signature", "A", "linux")]
        self.assertNotIn("outdated", entry)
        self.assertEqual(entry["status"], "ok")


class Classify(unittest.TestCase):
    def entry(self, status="ok", **kw):
        base = {"status": status, "sig": None, "offset": None}
        base.update(kw)
        return base

    def test_no_change(self):
        self.assertIsNone(classify(self.entry(), self.entry()))

    def test_break_and_fix(self):
        self.assertEqual(classify(self.entry("ok"), self.entry("broken")),
                         "broke")
        self.assertEqual(classify(self.entry("ok"), self.entry("ambiguous")),
                         "broke")
        self.assertEqual(classify(self.entry("broken"), self.entry("ok")),
                         "fixed")

    def test_stale_offset_counts_as_a_break(self):
        self.assertEqual(classify(self.entry("ok"), self.entry("stale")),
                         "broke")

    def test_added_and_removed(self):
        self.assertEqual(classify(None, self.entry()), "added")
        self.assertEqual(classify(self.entry(), None), "removed")

    def test_resigned_keeps_the_verdict_but_changes_the_bytes(self):
        self.assertEqual(classify(self.entry(sig="48 89"),
                                  self.entry(sig="48 8B")), "resigned")

    def test_moved_offset(self):
        self.assertEqual(classify(self.entry(offset=102),
                                  self.entry(offset=103)), "moved")

    def test_every_kind_has_a_sort_position(self):
        kinds = {"broke", "fixed", "changed", "added", "removed",
                 "resigned", "moved"}
        self.assertEqual(kinds - set(CHANGE_ORDER), set())


if __name__ == "__main__":
    unittest.main()
