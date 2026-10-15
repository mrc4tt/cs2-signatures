"""Unit tests for the artifact-YAML subset parser and version resolve in
fetch_symbols."""
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "scripts"))
import fetch_symbols  # noqa: E402
from fetch_symbols import kind_of, parse_yaml  # noqa: E402

FUNCTION = """func_name: CBaseEntity_EmitSound
func_va: '0x1a7a960'
func_rva: '0x1a7a960'
func_size: '0x1ad'
func_sig: 55 48 89 E5 41 57 41 56 41 55 41 54 49 89 FC 53 48 83 EC ??
"""

FOLDED = """member_name: m_skeletonInstance
offset: '0x270'
size: 8
offset_sig: 48 8B 89 ?? ?? ?? ?? 48 8B 01 FF 50 ?? 48 85 C0 74 ?? 48 8B 80 ?? ?? ?? ??
  CC CC CC CC 48 89 5C 24 ??
offset_sig_disp: 0
offset_sig_allow_across_function_boundary: true
struct_name: CBaseAnimGraph
"""

VTABLE = """vtable_class: CEntityInstance
vtable_entries:
  '0': '0x2ded430'
  '1': '0xcb6ee0'
vtable_numvfunc: 2
"""


class TestParseYaml(unittest.TestCase):
    def test_scalars_and_quotes(self):
        got = parse_yaml(FUNCTION)
        self.assertEqual(got["func_name"], "CBaseEntity_EmitSound")
        self.assertEqual(got["func_va"], "0x1a7a960")
        self.assertTrue(got["func_sig"].startswith("55 48 89 E5"))

    def test_folded_scalar_is_joined(self):
        got = parse_yaml(FOLDED)
        self.assertTrue(got["offset_sig"].endswith("CC CC CC CC 48 89 5C 24 ??"))
        self.assertNotIn("\n", got["offset_sig"])

    def test_int_and_bool_conversion(self):
        got = parse_yaml(FOLDED)
        self.assertEqual(got["size"], 8)
        self.assertEqual(got["offset_sig_disp"], 0)
        self.assertIs(got["offset_sig_allow_across_function_boundary"], True)

    def test_nested_block(self):
        got = parse_yaml(VTABLE)
        self.assertEqual(got["vtable_entries"],
                         {"0": "0x2ded430", "1": "0xcb6ee0"})
        self.assertEqual(got["vtable_numvfunc"], 2)


class TestKindOf(unittest.TestCase):
    def test_kinds(self):
        self.assertEqual(kind_of(parse_yaml(FUNCTION)), "function")
        self.assertEqual(kind_of(parse_yaml(FOLDED)), "structMember")
        self.assertEqual(kind_of(parse_yaml(VTABLE)), "vtable")
        self.assertEqual(kind_of({"vfunc_index": 3}), "virtualFunction")
        self.assertEqual(kind_of({"gv_name": "x"}), "global")
        self.assertEqual(kind_of({"patch_name": "x"}), "patch")


class ResolveGamever(unittest.TestCase):
    """Manifest ids first; byte-identical server binaries as the fallback."""

    LOCK = {"game_version": "14191",
            "download": {"manifests": {"2347771": "111", "2347773": "222"}},
            "binaries": {"server": {"linux": {"sha256": "aa"},
                                    "windows": {"sha256": "bb"}}}}
    SAME = {("server", "linux"): "aa", ("server", "windows"): "bb"}

    def resolve(self, manifest, binaries):
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "binary_locks"))
            with open(os.path.join(tmp, "binary_locks", "14191.json"),
                      "w") as fh:
                json.dump(self.LOCK, fh)
            man = os.path.join(tmp, "manifest.json")
            with open(man, "w") as fh:
                json.dump(manifest, fh)
            with mock.patch.object(fetch_symbols, "CLONE_DIR", tmp), \
                    mock.patch.object(fetch_symbols, "sparse_clone"):
                return fetch_symbols.resolve_gamever("repo", man, binaries)

    def test_manifest_match_never_hashes(self):
        hashed = mock.Mock(return_value=None)
        got = self.resolve({"2347771": "111", "2347773": "222"}, hashed)
        self.assertEqual(got, "14191")
        hashed.assert_not_called()

    def test_repushed_depot_with_same_binaries_resolves(self):
        got = self.resolve({"2347771": "333", "2347773": "444"},
                           lambda: self.SAME)
        self.assertEqual(got, "14191")

    def test_changed_binaries_do_not_resolve(self):
        other = dict(self.SAME)
        other[("server", "windows")] = "cc"
        got = self.resolve({"2347771": "333", "2347773": "444"},
                           lambda: other)
        self.assertIsNone(got)

    def test_missing_binaries_do_not_resolve(self):
        got = self.resolve({"2347771": "333", "2347773": "444"},
                           lambda: None)
        self.assertIsNone(got)


if __name__ == "__main__":
    unittest.main()
