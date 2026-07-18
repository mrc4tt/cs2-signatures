"""Unit tests for lib_sig: sig parsing, matching, section extraction."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "scripts"))
from lib_sig import (sig_to_regex, sig_tokens, count_matches,  # noqa: E402
                     exec_sections, _elf_exec_sections, _pe_exec_sections)


class TestSigTokens(unittest.TestCase):
    def test_space_style(self):
        self.assertEqual(sig_tokens("48 89 ? E8"), ["48", "89", "?", "E8"])

    def test_escape_style(self):
        self.assertEqual(sig_tokens(r"\x48\x89\x2A\xE8"),
                         ["48", "89", "2A", "E8"])

    def test_escape_style_with_spaces(self):
        self.assertEqual(sig_tokens(r"\x48 \x89\xE8"), ["48", "89", "E8"])


class TestSigToRegex(unittest.TestCase):
    def test_literal(self):
        rx = sig_to_regex("55 48 89")
        self.assertIsNotNone(rx.search(b"\x00\x55\x48\x89\x00"))
        self.assertIsNone(rx.search(b"\x55\x48\x00"))

    def test_wildcards_match_anything(self):
        rx = sig_to_regex("55 ? 89")
        self.assertIsNotNone(rx.search(b"\x55\xff\x89"))
        self.assertIsNotNone(rx.search(b"\x55\x00\x89"))

    def test_2a_is_wildcard(self):
        rx = sig_to_regex("55 2A 89")
        self.assertIsNotNone(rx.search(b"\x55\xab\x89"))

    def test_escape_equals_space_style(self):
        a = sig_to_regex("55 48 89 E5 ? ? E8")
        b = sig_to_regex(r"\x55\x48\x89\xE5\x2A\x2A\xE8")
        self.assertEqual(a.pattern, b.pattern)

    def test_literal_zero_is_not_wildcard(self):
        # 00 in a sig must match ONLY a real 0x00 byte (upstream trackers
        # that treat 00 as a wildcard report false "found").
        rx = sig_to_regex("55 00 89")
        self.assertIsNotNone(rx.search(b"\x55\x00\x89"))
        self.assertIsNone(rx.search(b"\x55\x42\x89"))

    def test_wildcard_matches_newline(self):
        # re.DOTALL: '.' must match 0x0A too.
        rx = sig_to_regex("55 ? 89")
        self.assertIsNotNone(rx.search(b"\x55\x0a\x89"))


class TestCountMatches(unittest.TestCase):
    def test_counts_across_segments(self):
        rx = sig_to_regex("AA BB")
        segs = [b"\xaa\xbb\x00\xaa\xbb", b"\xaa\xbb"]
        self.assertEqual(count_matches(rx, segs), 3)

    def test_no_cross_segment_match(self):
        rx = sig_to_regex("AA BB")
        segs = [b"\x00\xaa", b"\xbb\x00"]
        self.assertEqual(count_matches(rx, segs), 0)


def make_elf(sections):
    """Minimal ELF64 with the given [(flags, bytes)] sections."""
    ehsize, shentsize = 64, 64
    payload_off = ehsize
    payloads, offsets = b"", []
    for _, data in sections:
        offsets.append(payload_off + len(payloads))
        payloads += data
    e_shoff = payload_off + len(payloads)
    hdr = bytearray(64)
    hdr[:4] = b"\x7fELF"
    hdr[4] = 2  # ELF64
    struct.pack_into("<Q", hdr, 0x28, e_shoff)
    struct.pack_into("<H", hdr, 0x3A, shentsize)
    struct.pack_into("<H", hdr, 0x3C, len(sections))
    out = bytes(hdr) + payloads
    for (flags, data), off in zip(sections, offsets):
        sh = bytearray(shentsize)
        struct.pack_into("<I", sh, 4, 1)          # SHT_PROGBITS
        struct.pack_into("<Q", sh, 8, flags)
        struct.pack_into("<Q", sh, 0x18, off)
        struct.pack_into("<Q", sh, 0x20, len(data))
        out += bytes(sh)
    return out


def make_pe(sections):
    """Minimal PE with the given [(characteristics, bytes)] sections."""
    e_lfanew = 0x40
    coff = e_lfanew + 4
    size_opt = 0
    sec_table = coff + 20 + size_opt
    hdr_end = sec_table + 40 * len(sections)
    out = bytearray(hdr_end)
    out[:2] = b"MZ"
    struct.pack_into("<I", out, 0x3C, e_lfanew)
    out[e_lfanew:e_lfanew + 4] = b"PE\x00\x00"
    struct.pack_into("<H", out, coff + 2, len(sections))
    struct.pack_into("<H", out, coff + 16, size_opt)
    payloads = b""
    for i, (chars, data) in enumerate(sections):
        off = sec_table + i * 40
        struct.pack_into("<I", out, off + 16, len(data))
        struct.pack_into("<I", out, off + 20, hdr_end + len(payloads))
        struct.pack_into("<I", out, off + 36, chars)
        payloads += data
    return bytes(out) + payloads


class TestExecSections(unittest.TestCase):
    def test_elf_exec_only(self):
        SHF_EXECINSTR, SHF_ALLOC = 0x4, 0x2
        data = make_elf([(SHF_EXECINSTR | SHF_ALLOC, b"CODE"),
                         (SHF_ALLOC, b"DATA")])
        self.assertEqual(_elf_exec_sections(data), [b"CODE"])

    def test_pe_exec_only(self):
        CODE, EXEC, READ = 0x20, 0x20000000, 0x40000000
        data = make_pe([(CODE | EXEC | READ, b"TEXT"), (READ, b"RDATA")])
        self.assertEqual(_pe_exec_sections(data), [b"TEXT"])

    def test_unknown_magic_falls_back_to_whole_file(self):
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as fh:
            fh.write(b"RAWBYTES")
            path = fh.name
        try:
            self.assertEqual(exec_sections(path), [b"RAWBYTES"])
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
