"""Standalone sig<->bytes toolbox. No Ghidra, no third-party deps (stdlib only).

Mirrors the sig->regex idea from CS2SigMaker.py but reads raw ELF/PE
executable sections off disk so it can run in CI. A CSS gamedata signature is
a space-separated list of hex bytes where '?' / '??' / '2A' style tokens mark
wildcards (CSS uses '?'; some tools use 0x2A). We turn that into a bytes regex
and count matches inside each executable section separately (a real function
body never straddles a section boundary, so per-section counting avoids bogus
cross-boundary hits).
"""
import re
import struct

WILDCARD_TOKENS = ("?", "??", "*", "2A", "2a")


def sig_to_regex(sig):
    """CSS sig string -> compiled bytes regex.

    '48 89 ? ? E8' -> re.compile(b'\\x48\\x89..\\xe8', re.S)
    Accepts '?' wildcards (CSS style) and raw 0x2A wildcards (IDA style).
    """
    out = []
    for tok in sig.split():
        tok = tok.strip()
        if not tok:
            continue
        if tok in WILDCARD_TOKENS or tok == "\\x2A":
            out.append(b".")
        else:
            out.append(re.escape(bytes([int(tok, 16)])))
    return re.compile(b"".join(out), re.DOTALL)


def count_matches(pattern, segments):
    """Total non-overlapping matches of a compiled bytes regex across segments."""
    n = 0
    for seg in segments:
        n += len(pattern.findall(seg))
    return n


# ---------------------------------------------------------------------------
# Executable-section extraction. Returns a list of `bytes`, one per exec
# section, so callers can scan each independently.
# ---------------------------------------------------------------------------

def _elf_exec_sections(data):
    # ELF64 little-endian only (CS2 server.so is x86-64).
    if data[:4] != b"\x7fELF" or data[4] != 1 and data[4] != 2:
        raise ValueError("not an ELF file")
    if data[4] != 2:
        raise ValueError("only ELF64 supported")
    e_shoff = struct.unpack_from("<Q", data, 0x28)[0]
    e_shentsize = struct.unpack_from("<H", data, 0x3A)[0]
    e_shnum = struct.unpack_from("<H", data, 0x3C)[0]
    SHF_EXECINSTR = 0x4
    segs = []
    for i in range(e_shnum):
        off = e_shoff + i * e_shentsize
        sh_type = struct.unpack_from("<I", data, off + 4)[0]
        sh_flags = struct.unpack_from("<Q", data, off + 8)[0]
        sh_offset = struct.unpack_from("<Q", data, off + 0x18)[0]
        sh_size = struct.unpack_from("<Q", data, off + 0x20)[0]
        # SHT_NOBITS (8) has no file bytes (e.g. .bss); skip.
        if (sh_flags & SHF_EXECINSTR) and sh_type != 8 and sh_size:
            segs.append(data[sh_offset:sh_offset + sh_size])
    return segs


def _pe_exec_sections(data):
    if data[:2] != b"MZ":
        raise ValueError("not a PE file")
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    if data[e_lfanew:e_lfanew + 4] != b"PE\x00\x00":
        raise ValueError("bad PE signature")
    coff = e_lfanew + 4
    num_sections = struct.unpack_from("<H", data, coff + 2)[0]
    size_opt = struct.unpack_from("<H", data, coff + 16)[0]
    sec_table = coff + 20 + size_opt
    IMAGE_SCN_CNT_CODE = 0x00000020
    IMAGE_SCN_MEM_EXECUTE = 0x20000000
    segs = []
    for i in range(num_sections):
        off = sec_table + i * 40
        size_raw = struct.unpack_from("<I", data, off + 16)[0]
        ptr_raw = struct.unpack_from("<I", data, off + 20)[0]
        chars = struct.unpack_from("<I", data, off + 36)[0]
        if (chars & (IMAGE_SCN_CNT_CODE | IMAGE_SCN_MEM_EXECUTE)) and size_raw:
            segs.append(data[ptr_raw:ptr_raw + size_raw])
    return segs


def exec_sections(path):
    """Read a binary and return its executable sections as [bytes, ...].

    Auto-detects ELF vs PE from the magic. Falls back to whole-file if the
    magic is unknown (keeps validation from crashing on odd inputs).
    """
    with open(path, "rb") as fh:
        data = fh.read()
    if data[:4] == b"\x7fELF":
        return _elf_exec_sections(data)
    if data[:2] == b"MZ":
        return _pe_exec_sections(data)
    return [data]
