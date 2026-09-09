"""Unit tests for lib_symbols: name folding, sig relations, snapshot lookup."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "scripts"))
from lib_symbols import (Snapshot, norm, sig_relation,  # noqa: E402
                         sig_tokens, same_sig)


def record(artifact, platform, kind, payload, module="server"):
    return {"id": "%s/%s.%s.yaml" % (module, artifact, platform),
            "module": module, "artifact": artifact, "symbolName": artifact,
            "platform": platform, "kind": kind, "payload": payload}


SNAPSHOT = {
    "source": {"gameVersion": "14178b"},
    "binaries": {"server": {"linux": {"sha256": "abc"}}},
    "records": [
        record("CBaseEntity_EmitSound", "linux", "function",
               {"func_name": "CBaseEntity_EmitSound", "func_va": "0x1a7a960",
                "func_sig": "55 48 89 E5 41 57"}),
        record("CCSPlayerController_ChangeTeam", "windows", "virtualFunction",
               {"func_name": "CCSPlayerController_ChangeTeam",
                "vfunc_index": 103, "vtable_name": "CCSPlayerController",
                "vfunc_offset": "0x338", "vfunc_sig": "FF 90 38 03 00 00",
                "func_va": "0x180aa0000"}),
        record("CBaseAnimGraph_m_skeletonInstance", "linux", "structMember",
               {"struct_name": "CBaseAnimGraph", "member_name": "m_skeleton",
                "offset": "0x528"}),
        record("CCSPlayerController_Teleport", "windows", "function",
               {"func_name": "CCSPlayerController_Teleport",
                "func_va": "0x180bb0000"}),
        record("CGCClientSharedObjectCache_m_Owner", "windows", "function",
               {"func_name": "m_Owner", "func_sig": "0F 10 41 28 48 8B C2"}),
        record("CCSPlayerController_vtable", "windows", "vtable",
               {"vtable_class": "CCSPlayerController",
                "vtable_entries": {"0": "0x1", "7": "0x180bb0000"}}),
    ],
}


class TestNorm(unittest.TestCase):
    def test_three_spellings_fold_together(self):
        self.assertEqual(norm("CEconItemView::operator"),
                         norm("CEconItemView.operator"))
        self.assertEqual(norm("A::b"), norm("A_b"))


class TestSigTokens(unittest.TestCase):
    def test_wildcard_spellings_fold(self):
        self.assertEqual(sig_tokens("48 ? 89"), sig_tokens("48 ?? 89"))

    def test_escape_style_accepted(self):
        self.assertEqual(sig_tokens(r"\x48\x89"), ["48", "89"])


class TestSigRelation(unittest.TestCase):
    def test_equal(self):
        self.assertEqual(sig_relation("48 89 ?", "48 89 ?"), "equal")

    def test_wildcard_spelling_is_equal(self):
        self.assertEqual(sig_relation("48 89 ?", "48 89 ??"), "equal")

    def test_compatible_when_one_side_pins_a_byte(self):
        self.assertEqual(sig_relation("0F 1F 80 ? ? ? ?",
                                      "0F 1F 80 00 00 00 00"), "compatible")

    def test_prefix_is_not_a_conflict(self):
        self.assertEqual(sig_relation("48 89 5C 24 08 57 48",
                                      "48 89 5C 24 ?? 57"), "prefix")

    def test_conflicting_byte(self):
        self.assertEqual(sig_relation("4C 89 45 ?", "4C 89 4D ??"), "conflict")

    def test_same_sig_accepts_compatible_only(self):
        self.assertTrue(same_sig("48 ? 89", "48 AA 89"))
        self.assertFalse(same_sig("48 AA 89", "48 BB 89"))

    def test_empty_side(self):
        self.assertIsNone(sig_relation("", "48 89"))


class TestSnapshot(unittest.TestCase):
    def setUp(self):
        self.snap = Snapshot(SNAPSHOT)

    def test_gamever_and_binaries(self):
        self.assertEqual(self.snap.gamever, "14178b")
        self.assertEqual(self.snap.library_sha("server", "linux"), "abc")

    def test_signature_lookup_folds_the_name(self):
        self.assertEqual(self.snap.signature("CBaseEntity::EmitSound", "linux"),
                         "55 48 89 E5 41 57")

    def test_signature_missing_platform(self):
        self.assertIsNone(self.snap.signature("CBaseEntity_EmitSound", "windows"))

    def test_offset_from_vfunc_index(self):
        self.assertEqual(
            self.snap.offset("CCSPlayerController_ChangeTeam", "windows"),
            (103, "vfunc_index"))

    def test_offset_from_struct_member_is_decimal(self):
        self.assertEqual(
            self.snap.offset("CBaseAnimGraph_m_skeletonInstance", "linux"),
            (0x528, "struct_member"))

    def test_offset_derived_from_vtable_dump(self):
        # No virtualFunction record, but the function VA sits in slot 7.
        self.assertEqual(
            self.snap.offset("CCSPlayerController_Teleport", "windows"),
            (7, "vtable_derived"))

    def test_offset_without_any_record(self):
        self.assertEqual(self.snap.offset("GameEntitySystem", "linux"),
                         (None, "no_reference"))

    def test_anchor_prefers_the_dedicated_kinds(self):
        a = self.snap.anchor("CCSPlayerController_ChangeTeam", "windows")
        self.assertEqual((a["via"], a["kind"], a["expected"]),
                         ("vfunc_sig", "vfunc", 0x338))
        # A structMember with no offset_sig has nothing to anchor on.
        self.assertIsNone(
            self.snap.anchor("CBaseAnimGraph_m_skeletonInstance", "linux"))

    def test_function_record_serves_as_an_anchor_when_told_what_to_expect(self):
        # The analysis files some members as a plain function whose pattern spans
        # the access instruction; 0x28 is the member offset.
        a = self.snap.anchor("CGCClientSharedObjectCache::m_Owner", "windows",
                             expected=40)
        self.assertEqual((a["via"], a["kind"], a["expected"]),
                         ("func_sig", "member", 40))

    def test_function_record_is_not_an_anchor_without_an_expected_value(self):
        self.assertIsNone(
            self.snap.anchor("CGCClientSharedObjectCache::m_Owner", "windows"))

    def test_alias_redirects_lookup(self):
        snap = Snapshot(SNAPSHOT,
                        {"ISource2GameEntities::EmitSound": "CBaseEntity_EmitSound"})
        self.assertEqual(
            snap.signature("ISource2GameEntities::EmitSound", "linux"),
            "55 48 89 E5 41 57")


if __name__ == "__main__":
    unittest.main()
