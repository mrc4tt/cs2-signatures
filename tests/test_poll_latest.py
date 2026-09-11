"""Unit tests for the sig.miksen.me latest.json poller.

The poller decides whether a cron tick forces a full pipeline run, so the two
directions both matter: a missed change leaves the tracker comparing against a
superseded reference, and a false change re-downloads ~80 MB of binaries every
tick. No network here - state_of() is fed the documents directly.
"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "scripts"))
import poll_latest as P  # noqa: E402


def doc(gamever="14181", config="sha256:aaa", schema=1, **extra):
    latest = {"gameVersion": gamever, "configSha256": config,
              "lastPublishTime": "2026-09-11T07:57:31Z",
              "symbolRecords": 3763}
    latest.update(extra)
    return {"schemaVersion": schema, "latest": latest,
            "builds": [gamever], "generatedAt": "2026-09-11T20:32:47Z"}


class StateOf(unittest.TestCase):
    def test_reads_the_pair(self):
        self.assertEqual(P.state_of(doc()),
                         {"gameVersion": "14181", "configSha256": "sha256:aaa"})

    def test_ignores_everything_else(self):
        """A rebuild that only moves the clock must not look like a change."""
        a = P.state_of(doc())
        b = P.state_of(doc(lastPublishTime="2026-09-12T09:00:00Z",
                           symbolRecords=9999))
        self.assertEqual(a, b)

    def test_same_build_new_config_is_a_change(self):
        self.assertNotEqual(P.state_of(doc(config="sha256:aaa")),
                            P.state_of(doc(config="sha256:bbb")))

    def test_new_build_is_a_change(self):
        self.assertNotEqual(P.state_of(doc("14181")), P.state_of(doc("14182")))

    def test_numeric_gameversion_compares_as_text(self):
        """The document may hand back a bare int; state is stored as JSON text."""
        self.assertEqual(P.state_of(doc(gamever=14181))["gameVersion"], "14181")

    def test_unknown_schema_still_polls(self):
        """A schema bump that only adds fields must not stall the tracker."""
        self.assertEqual(P.state_of(doc(schema=2))["gameVersion"], "14181")

    def test_missing_fields_are_errors(self):
        for bad in ({"schemaVersion": 1},
                    {"schemaVersion": 1, "latest": {}},
                    {"schemaVersion": 1, "latest": {"gameVersion": "14181"}},
                    {"schemaVersion": 1, "latest": []},
                    []):
            with self.assertRaises(ValueError):
                P.state_of(bad)


class StateFile(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "sub", ".last_seen.json")

    def test_round_trip(self):
        state = P.state_of(doc())
        P.save_state(self.path, state)
        self.assertEqual(P.load_state(self.path), state)

    def test_no_file_is_unknown(self):
        self.assertEqual(P.load_state(self.path), {})

    def test_corrupt_file_is_unknown_not_a_crash(self):
        """Unknown means "run anyway" - a redundant run beats a skipped one."""
        os.makedirs(os.path.dirname(self.path))
        with open(self.path, "w") as fh:
            fh.write("{not json")
        self.assertEqual(P.load_state(self.path), {})

    def test_partial_file_is_unknown(self):
        os.makedirs(os.path.dirname(self.path))
        with open(self.path, "w") as fh:
            json.dump({"gameVersion": "14181"}, fh)
        self.assertNotEqual(P.load_state(self.path), P.state_of(doc()))


class ExitCodes(unittest.TestCase):
    """The contract cron.sh reads: 10 = changed, 0 = unchanged, 1 = error."""

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, ".last_seen.json")
        self.doc = doc()
        self.real_fetch = P.fetch
        P.fetch = lambda url, timeout: self.doc
        self.addCleanup(setattr, P, "fetch", self.real_fetch)

    def run_poll(self, *extra):
        argv = sys.argv
        sys.argv = ["poll_latest.py", "--state", self.path] + list(extra)
        try:
            return P.main()
        finally:
            sys.argv = argv

    def test_first_run_is_a_change(self):
        self.assertEqual(self.run_poll(), 10)

    def test_second_run_is_quiet(self):
        self.assertEqual(self.run_poll(), 10)
        self.assertEqual(self.run_poll(), 0)

    def test_republished_config_fires_again(self):
        self.assertEqual(self.run_poll(), 10)
        self.doc = doc(config="sha256:bbb")
        self.assertEqual(self.run_poll(), 10)
        self.assertEqual(self.run_poll(), 0)

    def test_no_write_does_not_persist(self):
        self.assertEqual(self.run_poll("--no-write"), 10)
        self.assertEqual(self.run_poll("--no-write"), 10)

    def test_network_error_is_not_a_change(self):
        def boom(url, timeout):
            raise OSError("connection refused")
        P.fetch = boom
        self.assertEqual(self.run_poll(), 1)
        self.assertFalse(os.path.exists(self.path))

    def test_bad_document_is_not_a_change(self):
        self.doc = {"schemaVersion": 1}
        self.assertEqual(self.run_poll(), 1)
        self.assertFalse(os.path.exists(self.path))


if __name__ == "__main__":
    unittest.main()
