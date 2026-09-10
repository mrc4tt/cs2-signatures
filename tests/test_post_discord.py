"""Unit tests for the delta-first Discord report's rendering helpers."""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "scripts"))
from post_discord import (CHANGE_ICON, bar, change_row, clamp_rows,  # noqa: E402
                          delta_headline, load_fragility, prev_version)


def change(name, plat, kind, old=None, new=None, project="P"):
    return {"project": project, "kind": "signature", "name": name,
            "platform": plat, "change": kind, "old": old, "new": new}


class Headline(unittest.TestCase):
    def test_empty(self):
        self.assertIsNone(delta_headline([]))

    def test_counts_and_pluralises_breaks(self):
        head = delta_headline([change("A", "linux", "broke", "ok", "broken"),
                               change("B", "linux", "broke", "ok", "broken"),
                               change("C", "linux", "fixed", "broken", "ok")])
        self.assertIn("**2** new breaks", head)
        self.assertIn("**1** fixed", head)

    def test_breaks_come_first(self):
        head = delta_headline([change("C", "linux", "fixed", "broken", "ok"),
                               change("A", "linux", "broke", "ok", "broken")])
        self.assertLess(head.index("new break"), head.index("fixed"))


class Rows(unittest.TestCase):
    def test_transition_row(self):
        row = change_row(change("A", "linux", "broke", "ok", "broken"),
                         multi=False, frag=set())
        self.assertIn("`A`", row)
        self.assertIn("ok → broken", row)
        self.assertIn(CHANGE_ICON["broke"], row)

    def test_labelled_row_has_no_arrow(self):
        row = change_row(change("A", "linux", "resigned", "ok", "ok"),
                         multi=False, frag=set())
        self.assertIn("re-signed", row)
        self.assertNotIn("→", row)

    def test_project_shown_only_when_several(self):
        c = change("A", "linux", "broke", "ok", "broken")
        self.assertNotIn("P", change_row(c, False, set()).split("`A`")[1])
        self.assertIn("P", change_row(c, True, set()))

    def test_fragility_marker(self):
        row = change_row(change("A", "linux", "broke", "ok", "broken"),
                         False, {("P", "A", "linux")})
        self.assertIn("🔥", row)


class Clamp(unittest.TestCase):
    def test_fits(self):
        self.assertEqual(clamp_rows(["a", "b"]), "a\nb")

    def test_drops_tail_and_says_so(self):
        out = clamp_rows(["x" * 100] * 40)
        self.assertLessEqual(len(out), 1024)
        self.assertIn("and", out.splitlines()[-1])


class Bar(unittest.TestCase):
    def test_full_and_empty(self):
        self.assertEqual(bar(10, 10), "█" * 10)
        self.assertEqual(bar(0, 10), "░" * 10)

    def test_no_total_is_not_a_division_error(self):
        self.assertEqual(len(bar(0, 0)), 10)


class Inputs(unittest.TestCase):
    def test_fragility_threshold(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "f.json")
            with open(path, "w") as fh:
                json.dump({"P": {"A|linux": {"breaks": 2},
                                 "B|linux": {"breaks": 1}}}, fh)
            self.assertEqual(load_fragility(path), {("P", "A", "linux")})

    def test_fragility_missing_file_is_empty(self):
        self.assertEqual(load_fragility("/nonexistent/f.json"), set())

    def test_previous_version_is_the_newest_differing_snapshot(self):
        with tempfile.TemporaryDirectory() as d:
            for name, ver in (("2026-01-01.json", "1.0"),
                              ("2026-01-02.json", "1.1"),
                              ("2026-01-03.json", "1.2")):
                with open(os.path.join(d, name), "w") as fh:
                    json.dump({"version": ver}, fh)
            self.assertEqual(prev_version(d, "1.2"), "1.1")
            self.assertIsNone(prev_version(d, None))
            self.assertIsNone(prev_version(None, "1.2"))


if __name__ == "__main__":
    unittest.main()
