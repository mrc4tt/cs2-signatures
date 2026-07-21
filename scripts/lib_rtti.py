"""Headless RTTI + signature-locate engine for offset validation. Stdlib only.

cs2-sig-tracker validates *signatures* by byte-scanning exec sections. It cannot
validate *offsets* (vtable slot indices) because a slot number is not a byte
pattern. This module closes that gap WITHOUT IDA: it maps every ELF section to
its virtual address so it can follow pointers, then does the Itanium RTTI walk
(typeinfo name string -> typeinfo -> primary vtable -> slot N) purely in Python.

Anchored offset validation (no decompile needed):
  1. relocate the entry's cached TARGET signature (the target function's head) ->
     a unique VA = the function start on the new build.
  2. RTTI-walk the entry's vtable_class to its primary vtable.
  3. confirm slot N still points at that function VA.
  Mismatch -> STALE; then scan the vtable for the function -> report new index.

Only Linux/Itanium (libserver.so) is implemented here. Windows/MSVC RTTI
(_RTTICompleteObjectLocator, image-relative RVAs) is a separate walk to add when
the linux side is finished.
"""
import struct

from lib_sig import sig_to_regex

SHF_EXECINSTR = 0x4
SHT_NOBITS = 8


class Image:
    """An ELF64 image mapped for VA-based reads, pointer scans and sig locates."""

    def __init__(self, path):
        with open(path, "rb") as fh:
            self.data = fh.read()
        if self.data[:4] != b"\x7fELF":
            raise ValueError("not an ELF file: %s" % path)
        if self.data[4] != 2:
            raise ValueError("only ELF64 supported")
        self.is_pe = False
        self._parse_sections()

    def _parse_sections(self):
        data = self.data
        e_shoff = struct.unpack_from("<Q", data, 0x28)[0]
        e_shentsize = struct.unpack_from("<H", data, 0x3A)[0]
        e_shnum = struct.unpack_from("<H", data, 0x3C)[0]
        # each section: (va, file_off, size, flags) for sections that occupy the
        # address space and have file bytes (skip .bss / NOBITS and addr==0).
        self.sections = []
        for i in range(e_shnum):
            off = e_shoff + i * e_shentsize
            sh_type = struct.unpack_from("<I", data, off + 4)[0]
            sh_flags = struct.unpack_from("<Q", data, off + 8)[0]
            sh_addr = struct.unpack_from("<Q", data, off + 0x10)[0]
            sh_offset = struct.unpack_from("<Q", data, off + 0x18)[0]
            sh_size = struct.unpack_from("<Q", data, off + 0x20)[0]
            if sh_type == SHT_NOBITS or sh_size == 0 or sh_addr == 0:
                continue
            self.sections.append((sh_addr, sh_offset, sh_size, sh_flags))
        # cache exec-section byte slices + their base VA for sig locates.
        self._exec = [(a, self.data[o:o + s]) for (a, o, s, fl) in self.sections
                      if fl & SHF_EXECINSTR]
        # non-exec allocated sections for pointer/string scans.
        self._data = [(a, self.data[o:o + s]) for (a, o, s, fl) in self.sections
                      if not (fl & SHF_EXECINSTR)]

    # --- VA reads -----------------------------------------------------------
    def _sec_of(self, va):
        for (a, o, s, fl) in self.sections:
            if a <= va < a + s:
                return (a, o, s, fl)
        return None

    def read(self, va, n):
        sec = self._sec_of(va)
        if not sec:
            return None
        a, o, s, fl = sec
        rel = va - a
        if rel + n > s:
            return None
        return self.data[o + rel:o + rel + n]

    def qword(self, va):
        b = self.read(va, 8)
        return struct.unpack("<Q", b)[0] if b else None

    def read_uint(self, va, size):
        """Little-endian unsigned int of `size` bytes at va (or None)."""
        b = self.read(va, size)
        if not b or len(b) != size:
            return None
        return int.from_bytes(b, "little")

    def read_int32(self, va):
        b = self.read(va, 4)
        return int.from_bytes(b, "little", signed=True) if b and len(b) == 4 else None

    def in_data(self, va):
        sec = self._sec_of(va)
        return bool(sec and not (sec[3] & SHF_EXECINSTR))

    def in_exec(self, va):
        sec = self._sec_of(va)
        return bool(sec and (sec[3] & SHF_EXECINSTR))

    # --- scans --------------------------------------------------------------
    def _scan(self, segments, needle):
        """Yield every VA where `needle` bytes occur across (base_va, bytes)."""
        out = []
        for base, buf in segments:
            start = 0
            while True:
                p = buf.find(needle, start)
                if p < 0:
                    break
                out.append(base + p)
                start = p + 1
        return out

    def find_ptr_vas(self, target_va):
        """VAs (in data sections) that hold the 8-byte LE pointer target_va."""
        return self._scan(self._data, struct.pack("<Q", target_va))

    def find_str_vas(self, raw):
        """VAs (in data sections) where the raw bytes occur (rodata strings)."""
        return self._scan(self._data, raw)

    def find_sig_vas(self, sig, limit=8):
        """VAs where a CSS signature matches inside exec sections.

        The target sig is anchored at a function head, so each match VA is a
        function start. Returns up to `limit` VAs across all exec sections.
        """
        pat = sig_to_regex(sig)
        out = []
        for base, buf in self._exec:
            for m in pat.finditer(buf):
                out.append(base + m.start())
                if len(out) >= limit:
                    return out
        return out

    # --- Itanium RTTI -------------------------------------------------------
    def typeinfo_name_bytes(self, class_name):
        # Itanium type_info::name() for a plain class = "<len><name>" length-
        # prefixed; the stored string is NUL-terminated.
        return ("%d%s" % (len(class_name), class_name)).encode() + b"\x00"

    def primary_vtables(self, class_name):
        """All primary-vtable VAs for class_name (offset_to_top == 0)."""
        prim = []
        for na in self.find_str_vas(self.typeinfo_name_bytes(class_name)):
            for pn in self.find_ptr_vas(na):        # ptr sits at typeinfo+8
                ti = pn - 8
                for pv in self.find_ptr_vas(ti):    # ptr sits at vtable+8
                    base = pv - 8
                    if self.qword(base) == 0:
                        prim.append(base)
        return sorted(set(prim))

    def slot_func(self, vtable_va, n):
        # slot 0 at vtable+0x10 (after offset_to_top + typeinfo qwords).
        return self.qword(vtable_va + 0x10 + n * 8)

    def vtable_len(self, vtable_va, cap=1024):
        n = 0
        while n < cap and self.in_exec(self.slot_func(vtable_va, n) or 0):
            n += 1
        return n

    def find_func_slot(self, vtable_va, func_va, cap=1024):
        """Slot index whose entry == func_va, scanning the whole vtable."""
        for n in range(cap):
            f = self.slot_func(vtable_va, n)
            if f is None or not self.in_exec(f):
                break
            if f == func_va:
                return n
        return None


def open_image(path):
    """Return an Image for an ELF path, or None if it isn't a supported ELF."""
    if not path:
        return None
    try:
        return Image(path)
    except Exception:
        return None
