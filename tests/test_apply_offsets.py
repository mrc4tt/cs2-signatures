"""apply_offsets: turn stale->found offset results into gamedata edits."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from apply_offsets import collect_updates, apply_updates  # noqa: E402


def _status(results):
    return {"results": results}


def _offset(name, status, **kw):
    info = {"status": status}
    info.update(kw)
    return {"name": name, "kind": "offset", "platforms": {"linux": info}}


class TestCollectUpdates(unittest.TestCase):
    def test_stale_with_found_is_update(self):
        st = _status([_offset("A", "stale", found_linux=24)])
        upd, unresolved, attention = collect_updates(st, "linux")
        self.assertEqual(upd, {"A": 24})
        self.assertEqual(unresolved, [])

    def test_stale_without_found_is_unresolved(self):
        st = _status([_offset("A", "stale", found_linux=None)])
        upd, unresolved, _ = collect_updates(st, "linux")
        self.assertEqual(upd, {})
        self.assertEqual(unresolved, ["A"])

    def test_ok_is_ignored(self):
        st = _status([_offset("A", "ok")])
        upd, unresolved, attention = collect_updates(st, "linux")
        self.assertEqual((upd, unresolved, attention), ({}, [], []))

    def test_review_and_no_recipe_go_to_attention(self):
        st = _status([
            _offset("A", "review", reason="no-vtable"),
            _offset("B", "no_recipe", resolve="gdt", reason="offset_sig-missing"),
        ])
        _, _, attention = collect_updates(st, "linux")
        names = {a[0]: a[1] for a in attention}
        self.assertEqual(names, {"A": "review", "B": "gdt"})

    def test_signature_entries_ignored(self):
        st = _status([{"name": "S", "kind": "signature",
                       "platforms": {"linux": {"status": "broken"}}}])
        upd, unresolved, attention = collect_updates(st, "linux")
        self.assertEqual((upd, unresolved, attention), ({}, [], []))


class TestApplyUpdates(unittest.TestCase):
    def test_apply_changes_only_differing(self):
        gd = {"A": {"offsets": {"linux": 27, "windows": 26}},
              "B": {"offsets": {"linux": 5, "windows": 5}}}
        changed = apply_updates(gd, {"A": 24, "B": 5}, "linux")
        self.assertEqual(changed, [("A", 27, 24)])
        self.assertEqual(gd["A"]["offsets"]["linux"], 24)
        self.assertEqual(gd["A"]["offsets"]["windows"], 26)  # preserved

    def test_apply_skips_unknown_or_non_offset(self):
        gd = {"A": {"signatures": {"linux": "x"}}}
        changed = apply_updates(gd, {"A": 9, "Z": 1}, "linux")
        self.assertEqual(changed, [])


if __name__ == "__main__":
    unittest.main()
