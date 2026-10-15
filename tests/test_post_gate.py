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
from post_gate import CHANGE_ORDER, classify, diff_status, entry_map  # noqa: E402


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


class ReferenceFlip(unittest.TestCase):
    """A lagging reference snapshot drops windows offset blocks; not news."""

    @staticmethod
    def status(reference, windows=True, linux_value=164):
        plats = {"linux": {"status": "ok", "linux": linux_value}}
        if windows:
            plats["windows"] = {"status": "ok", "windows": 165}
        return {"reference": reference, "results": [
            {"name": "CBaseEntity_Teleport", "kind": "offset",
             "offsets": {"linux": linux_value, "windows": 165},
             "platforms": plats},
            sig("Foo", windows={"status": "ok", "sig": "48 89"}),
        ]}

    def test_reference_lost_hides_vanished_windows_offsets(self):
        old = self.status("14190")
        new = self.status(None, windows=False)
        self.assertEqual(diff_status("P", old, new), [])

    def test_reference_back_hides_returning_windows_offsets(self):
        old = self.status(None, windows=False)
        new = self.status("14200")
        self.assertEqual(diff_status("P", old, new), [])

    def test_real_changes_still_report_across_a_flip(self):
        old = self.status("14190", linux_value=164)
        new = self.status(None, windows=False, linux_value=165)
        got = [(c["name"], c["platform"], c["change"])
               for c in diff_status("P", old, new)]
        self.assertEqual(got, [("CBaseEntity_Teleport", "linux", "moved")])

    def test_lost_verification_is_quiet_but_a_break_is_not(self):
        old = self.status("14190")
        new = self.status(None)
        new["results"][0]["platforms"]["linux"]["status"] = "review"
        self.assertEqual(diff_status("P", old, new), [])
        new["results"][0]["platforms"]["linux"]["status"] = "stale"
        got = [c["change"] for c in diff_status("P", old, new)]
        self.assertEqual(got, ["broke"])

    def test_removal_without_a_flip_still_reports(self):
        old = self.status("14190")
        new = self.status("14190", windows=False)
        got = [c["change"] for c in diff_status("P", old, new)]
        self.assertEqual(got, ["removed"])

    def test_removed_signature_reports_across_a_flip(self):
        old = self.status("14190")
        new = self.status(None)
        new["results"] = new["results"][:1]
        got = [(c["kind"], c["change"]) for c in diff_status("P", old, new)]
        self.assertEqual(got, [("signature", "removed")])


if __name__ == "__main__":
    unittest.main()
