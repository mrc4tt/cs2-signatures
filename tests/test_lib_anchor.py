"""Unit tests for lib_anchor: locating a displacement and reading it back."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "scripts"))
from lib_anchor import (derive, derive_index, derive_member,  # noqa: E402
                        locate, read_displacement, value_runs, wildcard_runs)

# call [rax+0xC0] -> vtable slot 24, displacement spelled out
VFUNC = "FF 90 C0 00 00 00 48 89 C6"
# mov edi,[r14+disp32] -> displacement already wildcarded, first run
MEMBER_WILD = "41 8B BE ?? ?? ?? ?? E8 ?? ?? ?? ??"
# mov rdi,[rdi+0x68] -> one byte displacement, spelled out
MEMBER_BYTE = "48 8B 7F 68 48 85 FF"


def sect(hexstr):
    return [bytes(int(t, 16) for t in hexstr.split())]


class TestRuns(unittest.TestCase):
    def test_wildcard_runs(self):
        self.assertEqual(wildcard_runs("41 8B ?? ?? E8 ??".split()),
                         [(2, 2), (5, 1)])

    def test_value_runs_finds_every_width_at_one_start(self):
        # C0 00 00 00 decodes to 0xC0 at width 1, 2 and 4. One displacement.
        hits = value_runs(VFUNC.split(), 0xC0)
        self.assertEqual({p for p, _ in hits}, {2})


class TestLocate(unittest.TestCase):
    def test_concrete_takes_the_widest_run(self):
        tokens, pos, width = locate(VFUNC, 0xC0)
        self.assertEqual((pos, width), (2, 4))

    def test_single_byte_displacement(self):
        _, pos, width = locate(MEMBER_BYTE, 0x68)
        self.assertEqual((pos, width), (3, 1))

    def test_inst_offset_takes_the_first_wildcard_run_after_it(self):
        _, pos, width = locate(MEMBER_WILD, 0x240, inst_offset=0)
        self.assertEqual((pos, width), (3, 4))

    def test_inst_offset_prefers_a_spelled_out_value(self):
        # CTakeDamageInfo::HitGroupInfo on 14185: mov [rbx+0x68], rdx, then an
        # unrelated wildcard. The displacement is the 68, not the trailing ??.
        _, pos, width = locate("48 89 53 68 41 83 C7 ??", 0x68, inst_offset=0)
        self.assertEqual((pos, width), (3, 1))

    def test_inst_offset_skips_bytes_before_the_instruction(self):
        # 0x68 also occurs before the instruction; only the one inside counts.
        _, pos, _ = locate("68 90 48 8B 7F 68", 0x68, inst_offset=2)
        self.assertEqual(pos, 5)

    def test_ambiguous_start_positions_are_refused(self):
        # 0x11 appears twice in unrelated places, so there is nothing to pick.
        self.assertIsNone(locate("11 90 11 00", 0x11))

    def test_inst_offset_past_the_pattern(self):
        self.assertIsNone(locate(MEMBER_WILD, 0x240, inst_offset=20))


class TestReadBack(unittest.TestCase):
    def test_reads_the_bytes_in_the_hole(self):
        tokens, pos, width = locate(VFUNC, 0xC0)
        value, status = read_displacement(sect("FF 90 D0 00 00 00 48 89 C6"),
                                          tokens, pos, width)
        self.assertEqual((value, status), (0xD0, "ok"))

    def test_absent_pattern(self):
        tokens, pos, width = locate(VFUNC, 0xC0)
        self.assertEqual(read_displacement(sect("90 90 90"), tokens, pos, width),
                         (None, "anchor_not_found"))

    def test_disagreeing_matches_are_refused(self):
        # Same call shape at two sites, different slots: nothing to conclude.
        tokens, pos, width = locate(VFUNC, 0xC0)
        two = sect("FF 90 C0 00 00 00 48 89 C6 90 FF 90 D0 00 00 00 48 89 C6")
        self.assertEqual(read_displacement(two, tokens, pos, width),
                         (None, "anchor_disagrees"))


class TestDerive(unittest.TestCase):
    def test_exact_pattern_still_present_confirms_without_widening(self):
        value, status = derive(sect("FF 90 C0 00 00 00 48 89 C6"), VFUNC, 0xC0)
        self.assertEqual((value, status), (0xC0, "confirmed"))

    def test_exact_pattern_gone_reads_the_new_value(self):
        value, status = derive(sect("FF 90 D0 00 00 00 48 89 C6"), VFUNC, 0xC0)
        self.assertEqual((value, status), (0xD0, "moved"))

    def test_wildcarded_anchor_goes_straight_to_read_back(self):
        value, status = derive(sect("41 8B BE 40 02 00 00 E8 00 00 00 00"),
                               MEMBER_WILD, 0x240, inst_offset=0)
        self.assertEqual((value, status), (0x240, "read"))

    def test_index_is_the_displacement_over_eight(self):
        value, status = derive_index(sect("FF 90 C0 00 00 00 48 89 C6"),
                                     VFUNC, 0xC0)
        self.assertEqual((value, status), (24, "confirmed"))

    def test_index_rejects_a_displacement_that_is_not_a_pointer_multiple(self):
        # 0xC5 is not divisible by 8, so the hole was read in the wrong place.
        value, status = derive_index(sect("FF 90 C5 00 00 00 48 89 C6"),
                                     VFUNC, 0xC0)
        self.assertEqual((value, status), (None, "anchor_implausible"))

    def test_member_keeps_the_raw_byte_offset(self):
        value, status = derive_member(sect("48 8B 7F 68 48 85 FF"),
                                      MEMBER_BYTE, 0x68)
        self.assertEqual((value, status), (104, "confirmed"))

    def test_unlocatable_anchor(self):
        self.assertEqual(derive(sect("90"), "11 90 11 00", 0x11),
                         (None, "anchor_unlocatable"))


if __name__ == "__main__":
    unittest.main()
