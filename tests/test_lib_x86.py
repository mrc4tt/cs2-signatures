"""Unit tests for the minimal x86-64 length decoder."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "scripts"))
from lib_x86 import decode_insn, wildcard_mask  # noqa: E402


def fields_of(data):
    got = decode_insn(data, 0)
    assert got is not None, "failed to decode %s" % data.hex()
    return got


class TestDecode(unittest.TestCase):
    def test_push_r15(self):
        length, fields = fields_of(bytes.fromhex("4157"))
        self.assertEqual(length, 2)
        self.assertEqual(fields, [])

    def test_sub_rsp_imm8(self):
        length, fields = fields_of(bytes.fromhex("4883EC28"))
        self.assertEqual(length, 4)
        self.assertEqual(fields, [(3, 1, "imm8")])

    def test_call_rel32(self):
        length, fields = fields_of(bytes.fromhex("E878563412"))
        self.assertEqual(length, 5)
        self.assertEqual(fields, [(1, 4, "rel32")])

    def test_mov_rax_rip_relative(self):
        length, fields = fields_of(bytes.fromhex("488B05DDCCBBAA"))
        self.assertEqual(length, 7)
        self.assertEqual(fields, [(3, 4, "rip32")])

    def test_mov_mem_imm32_sib_disp8(self):
        # mov dword [rsp+0x20], 1
        length, fields = fields_of(bytes.fromhex("C744242001000000"))
        self.assertEqual(length, 8)
        self.assertEqual(fields, [(3, 1, "disp8"), (4, 4, "imm32")])

    def test_jcc_rel32(self):
        length, fields = fields_of(bytes.fromhex("0F8478563412"))
        self.assertEqual(length, 6)
        self.assertEqual(fields, [(2, 4, "rel32")])

    def test_movaps_modrm(self):
        length, fields = fields_of(bytes.fromhex("0F28C1"))
        self.assertEqual(length, 3)
        self.assertEqual(fields, [])

    def test_test_rm_imm32(self):
        # test eax, 0x12345678 (F7 /0)
        length, fields = fields_of(bytes.fromhex("F7C078563412"))
        self.assertEqual(length, 6)
        self.assertEqual(fields, [(2, 4, "imm32")])

    def test_mov_r64_imm64(self):
        length, fields = fields_of(bytes.fromhex("48B8" + "11" * 8))
        self.assertEqual(length, 10)
        self.assertEqual(fields, [(2, 8, "imm64")])

    def test_unknown_returns_none(self):
        # 0x06 is invalid in 64-bit mode
        self.assertIsNone(decode_insn(b"\x06", 0))


class TestWildcardMask(unittest.TestCase):
    def test_rel32_always_wildcarded(self):
        code = bytes.fromhex("E878563412C3")  # call rel32; ret
        mask = wildcard_mask(code, code)
        self.assertEqual(list(mask), [0, 1, 1, 1, 1, 0])

    def test_whole_field_wildcarded_on_partial_drift(self):
        old = bytes.fromhex("C744242001000000C3")  # mov [rsp+0x20], 1; ret
        new = bytes.fromhex("C744242002000000C3")  # imm changed 1 -> 2
        mask = wildcard_mask(new, old)
        # entire imm32 (offsets 4-7) wildcarded, not just the changed byte
        self.assertEqual(list(mask[4:8]), [1, 1, 1, 1])
        self.assertEqual(mask[3], 0)   # disp8 unchanged -> literal
        self.assertEqual(mask[8], 0)   # ret unchanged

    def test_opcode_drift_stays_bytewise(self):
        old = bytes.fromhex("4157C3")
        new = bytes.fromhex("4156C3")  # push r15 -> push r14
        mask = wildcard_mask(new, old)
        self.assertEqual(list(mask), [0, 1, 0])

    def test_undecodable_falls_back_to_byte_diff(self):
        old = b"\x06\xaa\xbb"
        new = b"\x06\xaa\xcc"
        mask = wildcard_mask(new, old)
        self.assertEqual(list(mask), [0, 0, 1])


if __name__ == "__main__":
    unittest.main()
