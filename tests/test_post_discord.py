"""Unit tests for the delta-first Discord report's rendering helpers."""
import json
import os
import re
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "scripts"))
from post_discord import (CHANGE_ICON, EMBEDS_PER_MSG, bar,  # noqa: E402
                          change_row, clamp_rows, delta_headline,
                          fits_standing, load_fragility, load_state,
                          prev_version, repost_reason, save_state, state_key)


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


class ChangeIcons(unittest.TestCase):
    """Every kind needs an icon, and a custom one needs a well-formed id."""

    CUSTOM = re.compile(r"^<a?:[A-Za-z0-9_]{2,32}:\d{17,20}>$")

    def test_every_icon_is_unicode_or_a_valid_custom_emoji(self):
        for kind, icon in CHANGE_ICON.items():
            if icon.startswith("<"):
                self.assertRegex(icon, self.CUSTOM,
                                 "%s has a malformed custom emoji" % kind)
            else:
                self.assertLessEqual(len(icon), 4,
                                     "%s is neither an emoji nor <:name:id>"
                                     % kind)

    def test_icons_are_distinct(self):
        # Two kinds sharing a marker makes the Changes list unreadable.
        icons = list(CHANGE_ICON.values())
        self.assertEqual(len(icons), len(set(icons)))


class RepostReason(unittest.TestCase):
    """When a run may edit the standing message, and when it may not."""

    def test_a_quiet_change_is_an_edit(self):
        delta = [change("A", "linux", "resigned")]
        self.assertIsNone(repost_reason(delta, [{}], False))

    def test_a_new_break_gets_its_own_message(self):
        # Discord fires no notification for an edit, so a mention buried in one
        # would never reach anyone.
        delta = [change("A", "linux", "broke", "ok", "broken")]
        self.assertIsNotNone(repost_reason(delta, [{}], False))

    def test_multi_message_report_is_never_edited(self):
        embeds = [{} for _ in range(EMBEDS_PER_MSG + 1)]
        self.assertIsNotNone(repost_reason([], embeds, False))

    def test_new_flag_overrides(self):
        self.assertIsNotNone(repost_reason([], [{}], True))


class FitsStanding(unittest.TestCase):
    def test_same_build_is_editable(self):
        self.assertTrue(fits_standing({"message_id": "1", "version": "1.2"},
                                      "1.2"))

    def test_new_build_starts_a_new_card(self):
        self.assertFalse(fits_standing({"message_id": "1", "version": "1.2"},
                                       "1.3"))

    def test_nothing_remembered(self):
        self.assertFalse(fits_standing({}, "1.2"))


class State(unittest.TestCase):
    HOOK = "https://discord.com/api/webhooks/123/s3cr3t-token"

    def test_key_is_a_digest_not_the_url(self):
        key = state_key(self.HOOK)
        self.assertEqual(len(key), 16)
        self.assertNotIn("s3cr3t-token", key)

    def test_key_ignores_query_and_trailing_slash(self):
        self.assertEqual(state_key(self.HOOK),
                         state_key(self.HOOK + "/?wait=true"))

    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "sub", "state.json")
            save_state(path, {"k": {"message_id": "9", "version": "1.2"}})
            self.assertEqual(load_state(path)["k"]["message_id"], "9")

    def test_missing_or_corrupt_file_costs_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(load_state(os.path.join(d, "nope.json")), {})
            bad = os.path.join(d, "bad.json")
            with open(bad, "w") as fh:
                fh.write("not json")
            self.assertEqual(load_state(bad), {})


if __name__ == "__main__":
    unittest.main()
