"""Unit tests for resig: window mapping and candidate regeneration.

Uses raw byte blobs (unknown magic -> exec_sections falls back to
whole-file), so no real ELF/PE needed to exercise the diff logic.
"""
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "scripts"))
from lib_sig import sig_to_regex  # noqa: E402
from resig import regen, map_window, build_candidate, WINDOW  # noqa: E402


def rng_bytes(seed, n):
    r = random.Random(seed)
    return bytes(r.randrange(256) for _ in range(n))


# A synthetic "function": distinctive prologue + body.
FUNC = (b"\x55\x48\x89\xe5\x41\x57\x49\x89\xff\x41\x56\x41\x55\x41\x54\x53"
        + rng_bytes(1, WINDOW))
SIG = "55 48 89 E5 41 57 49 89 FF 41 56 41 55 41 54 53"


def build_binary(func, filler_seed, size=64 * 1024, at=1000):
    data = bytearray(rng_bytes(filler_seed, size))
    data[at:at + len(func)] = func
    return bytes(data)


class TestRegen(unittest.TestCase):
    def test_identical_builds(self):
        old = [build_binary(FUNC, 2)]
        new = [build_binary(FUNC, 3, at=5000)]  # moved, bytes identical
        res = regen(SIG, old, new)
        self.assertIn("candidate", res)
        self.assertEqual(res["new_pos"], [0, 5000])
        rx = sig_to_regex(res["candidate"])
        hits = [m.start() for m in rx.finditer(new[0])]
        self.assertEqual(hits, [5000])

    def test_drifted_bytes_get_wildcarded(self):
        # mutate a few body bytes like a recompile would
        drifted = bytearray(FUNC)
        for i in (20, 21, 22, 23, 40):
            drifted[i] ^= 0xFF
        old = [build_binary(FUNC, 4)]
        new = [build_binary(bytes(drifted), 5, at=7777)]
        res = regen(SIG, old, new)
        self.assertIn("candidate", res)
        self.assertEqual(res["new_pos"], [0, 7777])
        rx = sig_to_regex(res["candidate"])
        self.assertEqual([m.start() for m in rx.finditer(new[0])], [7777])

    def test_sig_not_unique_in_old_is_error(self):
        two = build_binary(FUNC, 6) + build_binary(FUNC, 7)
        res = regen(SIG, [two], [build_binary(FUNC, 8)])
        self.assertIn("error", res)
        self.assertIn("not unique", res["error"])

    def test_function_removed_is_error(self):
        old = [build_binary(FUNC, 9)]
        new = [rng_bytes(10, 64 * 1024)]  # function gone
        res = regen(SIG, old, new)
        self.assertIn("error", res)


class TestMapWindow(unittest.TestCase):
    def test_finds_exact_copy(self):
        window = FUNC[:WINDOW]
        hay = rng_bytes(11, 32 * 1024) + window + rng_bytes(12, 1024)
        got = map_window(window, [hay])
        self.assertIsNotNone(got)
        self.assertEqual((got[0], got[1]), (0, 32 * 1024))
        self.assertAlmostEqual(got[2], 1.0)

    def test_rejects_low_similarity(self):
        window = FUNC[:WINDOW]
        got = map_window(window, [rng_bytes(13, 32 * 1024)])
        self.assertIsNone(got)


class TestBuildCandidate(unittest.TestCase):
    def test_wildcard_prologue_rejected(self):
        old_window = b"\xaa" * WINDOW
        new = [b"\xbb" + rng_bytes(14, 4096)]
        self.assertIsNone(build_candidate(old_window, new, 0, 0))


if __name__ == "__main__":
    unittest.main()
