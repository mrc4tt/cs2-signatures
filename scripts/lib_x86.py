"""Minimal x86-64 instruction-length decoder for smarter sig wildcards.

Not a disassembler: we only need instruction *boundaries* and the byte
ranges of operand fields that drift between game builds (displacements,
immediates, call/jump targets). resig uses this to wildcard whole fields
instead of individual differing bytes, so a proposed signature keeps
matching after the next recompile shifts an address by a few bytes.

Deliberately incomplete: covers the encodings compilers actually emit in
function bodies. decode_insn returns None on anything unknown and the
caller falls back to plain byte-diff wildcarding from that point — a
wrong guess can only cost signature robustness, never correctness,
because every candidate is still uniqueness-checked afterwards.

stdlib only.
"""

LEGACY_PREFIXES = frozenset(
    (0x66, 0x67, 0xF0, 0xF2, 0xF3, 0x2E, 0x36, 0x3E, 0x26, 0x64, 0x65))

# 0F-map opcodes with NO ModRM byte.
_0F_NO_MODRM = frozenset((0x05, 0x0B, 0x31, 0x77, 0xA2,
                          0xC8, 0xC9, 0xCA, 0xCB, 0xCC, 0xCD, 0xCE, 0xCF))
# 0F-map opcodes with ModRM + imm8.
_0F_MODRM_IMM8 = frozenset((0x70, 0x71, 0x72, 0x73, 0xA4, 0xAC, 0xBA,
                            0xC2, 0xC4, 0xC5, 0xC6))


class _Trunc(Exception):
    """Window ended mid-instruction."""


def decode_insn(b, start):
    """Decode one instruction at b[start].

    Returns (length, fields) or None on unknown opcode / truncation.
    fields = [(offset_from_start, size, kind), ...] with kind one of
    'disp8' 'disp32' 'rip32' 'imm8' 'imm16' 'imm32' 'imm64' 'rel8' 'rel32'.
    """
    try:
        return _decode(b, start)
    except (_Trunc, IndexError):
        return None


def _decode(b, start):
    n = len(b)
    i = start
    opsize16 = False
    while i < n and b[i] in LEGACY_PREFIXES:
        if b[i] == 0x66:
            opsize16 = True
        i += 1
    rex = 0
    if i < n and 0x40 <= b[i] <= 0x4F:
        rex = b[i]
        i += 1
    if i >= n:
        raise _Trunc
    op = b[i]
    i += 1

    fields = []

    def field(kind, size):
        nonlocal i
        if i + size > n:
            raise _Trunc
        fields.append((i - start, size, kind))
        i += size

    def imm8():
        field("imm8", 1)

    def immz():
        field("imm16", 2) if opsize16 else field("imm32", 4)

    def modrm():
        nonlocal i
        if i >= n:
            raise _Trunc
        m = b[i]
        i += 1
        mod, rm = m >> 6, m & 7
        if mod == 3:
            return m
        if rm == 4:                      # SIB follows
            if i >= n:
                raise _Trunc
            sib = b[i]
            i += 1
            if mod == 0 and (sib & 7) == 5:
                field("disp32", 4)
                return m
        elif mod == 0 and rm == 5:       # RIP-relative
            field("rip32", 4)
            return m
        if mod == 1:
            field("disp8", 1)
        elif mod == 2:
            field("disp32", 4)
        return m

    if op == 0x0F:                       # two-byte map — must be checked
        if i >= n:                       # before the generic <0x40 block
            raise _Trunc
        op2 = b[i]
        i += 1
        if 0x80 <= op2 <= 0x8F:          # jcc rel32
            field("rel32", 4)
        elif op2 in _0F_NO_MODRM:
            pass
        elif op2 in _0F_MODRM_IMM8:
            modrm()
            imm8()
        elif op2 == 0x38:                # three-byte map: ModRM, no imm
            if i >= n:
                raise _Trunc
            i += 1
            modrm()
        elif op2 == 0x3A:                # three-byte map: ModRM + imm8
            if i >= n:
                raise _Trunc
            i += 1
            modrm()
            imm8()
        else:                            # bulk of 0F map: ModRM, no imm
            modrm()
    elif op < 0x40:
        low = op & 7
        if low in (0, 1, 2, 3):
            modrm()
        elif low == 4:
            imm8()
        elif low == 5:
            immz()
        else:                            # 0x*6/0x*7: invalid in 64-bit mode
            return None
    elif 0x50 <= op <= 0x5F:             # push/pop reg
        pass
    elif op == 0x63:                     # movsxd
        modrm()
    elif op == 0x68:
        immz()
    elif op == 0x69:
        modrm()
        immz()
    elif op == 0x6A:
        imm8()
    elif op == 0x6B:
        modrm()
        imm8()
    elif 0x70 <= op <= 0x7F:             # jcc rel8
        field("rel8", 1)
    elif op == 0x80:
        modrm()
        imm8()
    elif op == 0x81:
        modrm()
        immz()
    elif op == 0x83:
        modrm()
        imm8()
    elif 0x84 <= op <= 0x8F:             # test/xchg/mov/lea/pop r/m
        modrm()
    elif 0x90 <= op <= 0x99:             # nop/xchg/cwde/cdq
        pass
    elif op in (0x9C, 0x9D):             # pushf/popf
        pass
    elif op == 0xA8:
        imm8()
    elif op == 0xA9:
        immz()
    elif 0xB0 <= op <= 0xB7:             # mov r8, imm8
        imm8()
    elif 0xB8 <= op <= 0xBF:             # mov r, imm32/imm64
        field("imm64", 8) if rex & 8 else immz()
    elif op in (0xC0, 0xC1):             # shift r/m, imm8
        modrm()
        imm8()
    elif op == 0xC2:
        field("imm16", 2)
    elif op == 0xC3:
        pass
    elif op == 0xC6:
        modrm()
        imm8()
    elif op == 0xC7:
        modrm()
        immz()
    elif op == 0xC9:                     # leave
        pass
    elif op == 0xCC:                     # int3 (padding)
        pass
    elif 0xD0 <= op <= 0xD3:             # shift r/m, 1/cl
        modrm()
    elif op in (0xE8, 0xE9):             # call/jmp rel32
        field("rel32", 4)
    elif op == 0xEB:
        field("rel8", 1)
    elif op == 0xF6:
        m = modrm()
        if (m >> 3) & 7 in (0, 1):       # TEST r/m8, imm8
            imm8()
    elif op == 0xF7:
        m = modrm()
        if (m >> 3) & 7 in (0, 1):       # TEST r/m, immz
            immz()
    elif 0xF8 <= op <= 0xFD:             # clc..std
        pass
    elif op in (0xFE, 0xFF):             # inc/dec/call/jmp/push r/m
        modrm()
    else:
        return None

    return i - start, fields


def wildcard_mask(new, old):
    """bytearray mask over `new` (1 = wildcard) for candidate building.

    Walks instruction boundaries in `new`. Operand fields (disp/imm/rel)
    are wildcarded as a WHOLE when any of their bytes differ from `old`;
    rel32 and RIP-relative disp32 are always wildcarded (they encode
    distances/addresses that move on every relink). Other bytes are
    wildcarded only where old/new differ. Falls back to plain byte-diff
    from the first undecodable instruction.
    """
    mask = bytearray(len(new))

    def differs(j):
        return j >= len(old) or old[j] != new[j]

    i = 0
    while i < len(new):
        d = decode_insn(new, i)
        if d is None:
            for j in range(i, len(new)):
                if differs(j):
                    mask[j] = 1
            break
        length, fields = d
        end = min(i + length, len(new))
        in_field = set()
        for foff, fsize, kind in fields:
            rng = range(i + foff, min(i + foff + fsize, len(new)))
            in_field.update(rng)
            if kind in ("rel32", "rip32") or any(differs(j) for j in rng):
                for j in rng:
                    mask[j] = 1
        for j in range(i, end):
            if j not in in_field and differs(j):
                mask[j] = 1
        i += length
    return mask
