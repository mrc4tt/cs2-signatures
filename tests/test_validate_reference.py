"""Unit tests for the reference tier in validate_sigs."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "scripts"))
from lib_symbols import Snapshot  # noqa: E402
from validate_sigs import apply_reference, tally_and_broken  # noqa: E402


def rec(artifact, platform, kind, payload):
    return {"id": "server/%s.%s.yaml" % (artifact, platform), "module": "server",
            "artifact": artifact, "symbolName": artifact, "platform": platform,
            "kind": kind, "payload": payload}


SNAP = Snapshot({
    "source": {"gameVersion": "14180"},
    "records": [
        rec("ClientPrint", "linux", "function", {"func_sig": "55 48 89 4D"}),
        rec("Healthy", "linux", "function", {"func_sig": "48 89 ? E8"}),
        rec("Slot", "linux", "virtualFunction",
            {"vfunc_index": 102, "vtable_name": "C"}),
        rec("Slot", "windows", "virtualFunction",
            {"vfunc_index": 103, "vtable_name": "C"}),
    ],
})

GAMEDATA = {
    "ClientPrint": {"signatures": {"linux": "55 48 89 45"}},
    "Healthy": {"signatures": {"linux": "48 89 AA E8"}},
    "Slot": {"offsets": {"linux": 102, "windows": 103}},
    "Drifted": {"offsets": {"linux": 5, "windows": 6}},
}


def results():
    return [
        {"name": "ClientPrint", "kind": "signature", "platforms": {
            "linux": {"status": "ok", "matches": 1, "sig": "55 48 89 45"}}},
        {"name": "Healthy", "kind": "signature", "platforms": {
            "linux": {"status": "ok", "matches": 1, "sig": "48 89 AA E8"}}},
        {"name": "Slot", "kind": "offset", "offsets": {"linux": 102},
         "platforms": {"linux": {"status": "no_recipe", "linux": 102}}},
        {"name": "Drifted", "kind": "offset", "offsets": {"linux": 5},
         "platforms": {"linux": {"status": "no_recipe", "linux": 5}}},
    ]


class TestApplyReference(unittest.TestCase):
    def setUp(self):
        self.r = results()
        apply_reference(self.r, GAMEDATA, SNAP)
        self.by_name = {r["name"]: r for r in self.r}

    def test_conflicting_bytes_are_outdated(self):
        ref = self.by_name["ClientPrint"]["platforms"]["linux"]["reference"]
        self.assertEqual(ref["status"], "outdated")
        self.assertEqual(ref["sig"], "55 48 89 4D")

    def test_scan_verdict_is_not_overwritten(self):
        # Outdated is advisory: the sig still resolves, so it stays ok.
        self.assertEqual(
            self.by_name["ClientPrint"]["platforms"]["linux"]["status"], "ok")

    def test_wildcard_difference_is_a_match(self):
        ref = self.by_name["Healthy"]["platforms"]["linux"]["reference"]
        self.assertEqual(ref["status"], "match")

    def test_reference_resolves_a_no_recipe_offset(self):
        info = self.by_name["Slot"]["platforms"]["linux"]
        self.assertEqual(info["status"], "ok")
        self.assertEqual(info["method"], "reference")

    def test_windows_offset_block_is_created(self):
        info = self.by_name["Slot"]["platforms"]["windows"]
        self.assertEqual(info["status"], "ok")
        self.assertEqual(info["reference"]["value"], 103)

    def test_declared_offset_without_reference_still_gets_a_block(self):
        # Invisible before: a windows offset nothing could check produced no
        # block at all, so the gap never showed up in the tally.
        info = self.by_name["Drifted"]["platforms"]["windows"]
        self.assertEqual(info["status"], "no_recipe")
        self.assertEqual(info["reference"]["status"], "no_reference")

    def test_tally_counts_outdated_without_marking_broken(self):
        tally, broken = tally_and_broken(self.r)
        self.assertEqual(tally["sig_outdated"], 1)
        self.assertEqual(broken, [])

    def test_no_snapshot_is_a_noop(self):
        plain = results()
        apply_reference(plain, GAMEDATA, None)
        self.assertNotIn("reference", plain[0]["platforms"]["linux"])


class TestMismatch(unittest.TestCase):
    def test_disagreement_marks_the_offset_stale(self):
        snap = Snapshot({"source": {"gameVersion": "x"}, "records": [
            rec("Slot", "linux", "virtualFunction",
                {"vfunc_index": 999, "vtable_name": "C"})]})
        r = [{"name": "Slot", "kind": "offset", "offsets": {"linux": 102},
              "platforms": {"linux": {"status": "ok", "linux": 102}}}]
        apply_reference(r, GAMEDATA, snap)
        info = r[0]["platforms"]["linux"]
        self.assertEqual(info["status"], "stale")
        self.assertEqual(info["found_linux"], 999)
        _, broken = tally_and_broken(r)
        self.assertTrue(broken)


if __name__ == "__main__":
    unittest.main()
