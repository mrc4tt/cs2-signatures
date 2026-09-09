"""Re-derive an offset from our own binary using a reference anchor. Stdlib only.

Why this exists. The reference tier compares our stored integer against the one
CS2_VibeSignatures recorded. That is a comparison of two opinions, and it is only
as current as the snapshot: when the analysis lags a game build, the reference
describes bytes we are not scanning.

An anchor closes that gap. Both anchor kinds pin the instruction that carries the
offset, with the offset itself sitting in the operand:

    virtualFunction  vfunc_sig   FF 90 E8 00 00 00     call [rax+0xE8]  -> slot 29
    structMember     offset_sig  48 8B 7F 68           mov rdi,[rdi+0x68]

So the offset can be read back out of the binary we actually downloaded:
wildcard the displacement, scan for the pattern, and decode the bytes that landed
in the hole. The answer describes THIS build, whichever version the snapshot was
built from, and it needs nothing but byte scanning - which is why it works on
Windows, where the RTTI walk in lib_offset cannot go.

Two conventions appear in the corpus, and both are handled:

  offset_sig_disp: N   the displacement is already wildcarded; it is the Nth
                       wildcard run in the pattern (135 of 215 structMembers)
  field absent         the displacement is spelled out; locate it by value
                       (316 of 344 vfunc_sigs, 74 more structMembers)

Locating by value can hit several widths at one position, because `C0 00 00 00`
decodes to 0xC0 at width 1, 2 and 4. That is one displacement, not three, so the
widest run at a single start position wins. Genuinely different start positions
are ambiguous and are refused rather than guessed.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_sig import WILDCARD_TOKENS, sig_tokens  # noqa: E402

# A vtable of more than this many slots, or a struct member further in than this,
# means we decoded something that is not the displacement.
MAX_SLOTS = 8192
MAX_MEMBER = 1 << 20


def is_wild(tok):
    return tok in WILDCARD_TOKENS


def wildcard_runs(tokens):
    """[(start, width)] for each maximal run of wildcard tokens."""
    runs, start = [], None
    for i, tok in enumerate(tokens):
        if is_wild(tok):
            if start is None:
                start = i
        elif start is not None:
            runs.append((start, i - start))
            start = None
    if start is not None:
        runs.append((start, len(tokens) - start))
    return runs


def value_runs(tokens, expected):
    """[(start, width)] for each concrete little-endian run equal to expected."""
    hits = []
    for width in (1, 2, 4, 8):
        for i in range(len(tokens) - width + 1):
            run = tokens[i:i + width]
            if any(is_wild(t) for t in run):
                continue
            try:
                raw = bytes(int(t, 16) for t in run)
            except ValueError:
                continue
            if int.from_bytes(raw, "little") == expected:
                hits.append((i, width))
    return hits


def locate(sig, expected, disp_index=None):
    """Where the displacement sits in `sig`. Returns (tokens, pos, width) or None.

    `tokens` comes back so the caller works on the same tokenisation the position
    refers to.
    """
    tokens = sig_tokens(sig)
    if not tokens:
        return None

    if disp_index is not None:
        runs = wildcard_runs(tokens)
        if disp_index >= len(runs):
            return None
        pos, width = runs[disp_index]
        return tokens, pos, width

    hits = value_runs(tokens, expected)
    if not hits:
        return None
    starts = set(p for p, _ in hits)
    if len(starts) != 1:
        return None  # two unrelated places encode the same value; do not guess
    pos = starts.pop()
    width = max(w for p, w in hits if p == pos)
    return tokens, pos, width


def pattern_with_hole(tokens, pos, width):
    """The token list with the displacement wildcarded, ready to scan for."""
    return ["?" if pos <= i < pos + width else t for i, t in enumerate(tokens)]


def tokens_to_regex(tokens):
    out = []
    for tok in tokens:
        out.append(b"." if is_wild(tok) else re.escape(bytes([int(tok, 16)])))
    return re.compile(b"".join(out), re.DOTALL)


# Wildcarding the displacement widens the pattern, so a virtual call reached from
# several places matches at each of them. That is not ambiguity: every call
# through the same slot carries the same displacement. Agreement is the test, not
# uniqueness. Stop after this many so a degenerate pattern cannot scan forever.
MAX_HITS = 256


def read_displacement(sections, tokens, pos, width):
    """Scan for the holed pattern and decode what sits in the hole.

    Returns (value, status). Every match must agree: one disagreement means the
    pattern is catching unrelated code and the answer would be a guess.
    """
    rx = tokens_to_regex(pattern_with_hole(tokens, pos, width))
    value = None
    hits = 0
    for seg in sections or ():
        for m in rx.finditer(seg):
            raw = int.from_bytes(seg[m.start() + pos:m.start() + pos + width],
                                 "little")
            if value is None:
                value = raw
            elif raw != value:
                return None, "anchor_disagrees"
            hits += 1
            if hits >= MAX_HITS:
                return value, "ok"
    if value is None:
        return None, "anchor_not_found"
    return value, "ok"


def _matches(sections, tokens):
    rx = tokens_to_regex(tokens)
    for seg in sections or ():
        if rx.search(seg):
            return True
    return False


def derive(sections, sig, expected, disp_index=None):
    """What this binary says the offset is. Returns (value, status).

    Order matters. When the anchor spells the displacement out, the cheapest and
    strongest test is whether that exact pattern still occurs: if it does, the
    instruction still carries that displacement and the offset is confirmed
    against these bytes, with no widening and so no ambiguity.

    Only when the exact pattern is gone do we punch the hole and read back what
    replaced it. That path is weaker, because wildcarding four bytes can let the
    pattern catch unrelated call sites, so every match has to agree.

    An anchor that already ships with the displacement wildcarded
    (offset_sig_disp) has nothing to match exactly, and goes straight to read
    back.
    """
    located = locate(sig, expected, disp_index)
    if not located:
        return None, "anchor_unlocatable"
    tokens, pos, width = located

    if disp_index is None:
        if _matches(sections, tokens):
            return expected, "confirmed"
        value, status = read_displacement(sections, tokens, pos, width)
        return (value, "moved") if status == "ok" else (None, status)

    value, status = read_displacement(sections, tokens, pos, width)
    return (value, "read") if status == "ok" else (None, status)


def derive_index(sections, sig, expected_offset, disp_index=None):
    """Vtable slot index for a vfunc anchor, as it stands in THIS binary."""
    value, status = derive(sections, sig, expected_offset, disp_index)
    if value is None:
        return None, status
    # A vtable displacement is always a whole number of pointers, so anything
    # else means the hole was in the wrong place.
    if value % 8 or value // 8 > MAX_SLOTS:
        return None, "anchor_implausible"
    return value // 8, status


def derive_member(sections, sig, expected_offset, disp_index=None):
    """Struct member byte offset, as it stands in THIS binary."""
    value, status = derive(sections, sig, expected_offset, disp_index)
    if value is None:
        return None, status
    if value > MAX_MEMBER:
        return None, "anchor_implausible"
    return value, status
