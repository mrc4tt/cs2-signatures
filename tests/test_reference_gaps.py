"""Unit tests for the reference-gap report handed back to the analysis repo.

The classification decides what lands in someone else's issue tracker, so the
rules are pinned here: what counts as a gap, how platforms and projects merge
into one row, and what the fingerprint does and does not react to.
"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "scripts"))
import reference_gaps as G  # noqa: E402


def status(project, results, reference="14181"):
    return {"project": project, "reference": reference, "results": results}


def sig_entry(name, **plats):
    return {"name": name, "kind": "signature",
            "platforms": {p: dict(v) for p, v in plats.items()}}


def offset_entry(name, offsets, **plats):
    return {"name": name, "kind": "offset", "offsets": offsets,
            "platforms": {p: dict(v) for p, v in plats.items()}}


class Classify(unittest.TestCase):
    def test_covered_signature_is_not_a_gap(self):
        self.assertIsNone(G.classify("signature", "ok", "match"))
        self.assertIsNone(G.classify("signature", "broken", "match"))

    def test_outdated_is_a_verdict_not_a_gap(self):
        self.assertIsNone(G.classify("signature", "ok", "outdated"))

    def test_signature_gaps(self):
        self.assertEqual(G.classify("signature", "ok", "no_reference"),
                         "missing_symbol")
        self.assertEqual(G.classify("signature", "ok", "no_sig"),
                         "missing_pattern")

    def test_offset_answered_by_a_recipe_is_not_a_gap(self):
        # The recipe produced a verdict, so nobody needs to analyse anything.
        self.assertIsNone(G.classify("offset", "ok", "no_reference"))
        self.assertIsNone(G.classify("offset", "stale", "no_reference"))

    def test_offset_with_neither_route_is_the_blind_spot(self):
        self.assertEqual(G.classify("offset", "no_recipe", "no_reference"),
                         "no_verdict")
        self.assertEqual(G.classify("offset", "review", None), "no_verdict")

    def test_offset_rescued_by_the_reference_is_not_a_gap(self):
        self.assertIsNone(G.classify("offset", "no_recipe", "match"))


class Collect(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def write(self, projects, statuses, aliases=None):
        """Lay out a registry + reports tree and collect against it."""
        root = self.dir.name
        reg = os.path.join(root, "projects.json")
        with open(reg, "w") as fh:
            json.dump(projects, fh)
        for pid, st in statuses.items():
            d = os.path.join(root, "reports", pid)
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "status.json"), "w") as fh:
                json.dump(st, fh)
        alias_path = os.path.join(root, "aliases.json")
        with open(alias_path, "w") as fh:
            json.dump(aliases or {}, fh)
        # P.status_path is relative to the repo root, so run from ours.
        cwd = os.getcwd()
        os.chdir(root)
        try:
            return G.collect(reg, alias_path)
        finally:
            os.chdir(cwd)

    def test_one_row_per_symbol_merging_platforms_and_projects(self):
        entry = sig_entry("Shared",
                          linux={"status": "ok",
                                 "reference": {"status": "no_sig"}},
                          windows={"status": "ok",
                                   "reference": {"status": "no_sig"}})
        report = self.write(
            [{"id": "A", "name": "A"}, {"id": "B", "name": "B"}],
            {"A": status("A", [entry]), "B": status("B", [entry])})
        self.assertEqual(len(report["gaps"]), 1)
        gap = report["gaps"][0]
        self.assertEqual(sorted(gap["platforms"]), ["linux", "windows"])
        self.assertEqual(sorted(gap["projects"]), ["A", "B"])
        self.assertEqual(report["reference"], "14181")

    def test_worst_category_wins_across_platforms(self):
        entry = sig_entry("Mixed",
                          linux={"status": "ok",
                                 "reference": {"status": "no_sig"}},
                          windows={"status": "ok",
                                   "reference": {"status": "no_reference"}})
        report = self.write([{"id": "A", "name": "A"}],
                            {"A": status("A", [entry])})
        self.assertEqual(report["gaps"][0]["category"], "missing_symbol")

    def test_offset_value_and_reason_are_carried(self):
        entry = offset_entry("Off", {"linux": 93},
                             linux={"status": "no_recipe",
                                    "reference": {"status": "no_reference",
                                                  "reason": "kind_global"}})
        report = self.write([{"id": "A", "name": "A"}],
                            {"A": status("A", [entry])})
        gap = report["gaps"][0]
        self.assertEqual(gap["values"], {"linux": 93})
        self.assertEqual(gap["reasons"], {"linux": "kind_global"})

    def test_aliases_are_reported(self):
        entry = sig_entry("Ours", linux={"status": "ok",
                                         "reference": {"status":
                                                       "no_reference"}})
        report = self.write([{"id": "A", "name": "A"}],
                            {"A": status("A", [entry])},
                            aliases={"Ours": "Theirs"})
        self.assertEqual(report["gaps"][0]["alias"], "Theirs")

    def test_worst_category_sorts_first(self):
        entries = [
            sig_entry("Sig", linux={"status": "ok",
                                    "reference": {"status": "no_sig"}}),
            offset_entry("Off", {"linux": 1},
                         linux={"status": "no_recipe",
                                "reference": {"status": "no_reference"}}),
        ]
        report = self.write([{"id": "A", "name": "A"}],
                            {"A": status("A", entries)})
        self.assertEqual([g["category"] for g in report["gaps"]],
                         ["no_verdict", "missing_pattern"])

    def test_clean_project_reports_nothing(self):
        entry = sig_entry("Fine", linux={"status": "ok",
                                         "reference": {"status": "match"}})
        report = self.write([{"id": "A", "name": "A"}],
                            {"A": status("A", [entry])})
        self.assertEqual(report["gaps"], [])
        self.assertIn("Nothing outstanding", G.render_markdown(report))


class Fingerprint(unittest.TestCase):
    def report(self, reference="14181", **over):
        gap = {"symbol": "S", "kind": "signature", "category": "missing_symbol",
               "platforms": ["linux"], "projects": ["A"], "reasons": {},
               "values": {}, "alias": None}
        gap.update(over)
        return {"reference": reference, "gaps": [gap]}

    def test_snapshot_version_alone_does_not_move_it(self):
        # A new game build with the same holes must not re-post the issue.
        self.assertEqual(G.fingerprint(self.report("14181")),
                         G.fingerprint(self.report("14999")))

    def test_a_new_symbol_moves_it(self):
        self.assertNotEqual(G.fingerprint(self.report()),
                            G.fingerprint(self.report(symbol="T")))

    def test_another_project_hitting_the_same_gap_moves_it(self):
        self.assertNotEqual(G.fingerprint(self.report()),
                            G.fingerprint(self.report(projects=["A", "B"])))

    def test_empty_is_stable(self):
        empty = {"reference": "14181", "gaps": []}
        self.assertEqual(G.fingerprint(empty), G.fingerprint(dict(empty)))


if __name__ == "__main__":
    unittest.main()
