#!/usr/bin/env python3
"""Minimal Valve VPK (v1/v2) reader — stdlib only, no third-party vpk lib.

CS2 packs game scripts (e.g. scripts/items/items_game.txt) inside pak01 VPKs:
`pak01_dir.vpk` is the index, the bytes live in numbered `pak01_<NNN>.vpk`
archives. This resolves an internal path to its (archive, offset, length,
preload) and can slice the file out, so the pipeline can publish items_game.txt
without downloading the whole ~60 GB content depot — only the one ~100 MB
archive that holds it.

Two subcommands:
  locate  <dir.vpk> <internal/path>   -> prints the archive index (or -1 if the
                                         bytes are inline in the dir vpk)
  extract <dir.vpk> <internal/path> -o OUT
                                      -> writes the file's bytes to OUT, reading
                                         the numbered archive next to the dir vpk

VPK format: https://developer.valvesoftware.com/wiki/VPK_(file_format)
"""
import argparse
import os
import struct
import sys

VPK_SIGNATURE = 0x55AA1234
INLINE = 0x7FFF  # archive index meaning "data is in the dir vpk after the tree"


def _read_cstr(buf, pos):
    end = buf.index(b"\x00", pos)
    return buf[pos:end].decode("latin1"), end + 1


def parse_dir(dir_path):
    """Parse a *_dir.vpk header + tree.

    Returns (entries, tree_end) where entries maps 'path/name.ext' ->
    dict(archive, offset, length, preload_offset, preload_len) and tree_end is
    the byte offset of the inline data section in the dir vpk."""
    with open(dir_path, "rb") as fh:
        buf = fh.read()
    sig, version, tree_size = struct.unpack_from("<III", buf, 0)
    if sig != VPK_SIGNATURE:
        raise ValueError("not a VPK (signature %#x)" % sig)
    header = 12 if version == 1 else 28  # v2 adds four uint32 section sizes
    pos = header
    entries = {}
    while True:
        ext, pos = _read_cstr(buf, pos)
        if ext == "":
            break
        while True:
            path, pos = _read_cstr(buf, pos)
            if path == "":
                break
            while True:
                name, pos = _read_cstr(buf, pos)
                if name == "":
                    break
                crc, preload, archive, offset, length = struct.unpack_from(
                    "<IHHII", buf, pos)
                pos += 16
                pos += 2  # terminator (0xffff)
                preload_offset = pos
                pos += preload  # preload bytes stored inline in the tree
                full = "%s/%s.%s" % (path, name, ext) if path != " " \
                    else "%s.%s" % (name, ext)
                entries[full] = {
                    "archive": archive, "offset": offset, "length": length,
                    "preload_offset": preload_offset, "preload_len": preload,
                }
                del crc
    return entries, header + tree_size


def _entry(dir_path, internal):
    entries, tree_end = parse_dir(dir_path)
    e = entries.get(internal)
    if e is None:
        raise KeyError("%r not found in %s (%d entries)"
                       % (internal, dir_path, len(entries)))
    return e, tree_end


def archive_path(dir_path, index):
    """pak01_dir.vpk + index 475 -> pak01_475.vpk (same directory)."""
    base = os.path.basename(dir_path)
    if not base.endswith("_dir.vpk"):
        raise ValueError("expected a *_dir.vpk, got %s" % base)
    stem = base[:-len("_dir.vpk")]
    return os.path.join(os.path.dirname(dir_path), "%s_%03d.vpk" % (stem, index))


def extract(dir_path, internal, out_path):
    e, tree_end = _entry(dir_path, internal)
    with open(dir_path, "rb") as fh:
        dirbuf = fh.read()
    preload = dirbuf[e["preload_offset"]:e["preload_offset"] + e["preload_len"]]
    body = b""
    if e["length"]:
        if e["archive"] == INLINE:
            start = tree_end + e["offset"]
            body = dirbuf[start:start + e["length"]]
        else:
            src = archive_path(dir_path, e["archive"])
            with open(src, "rb") as fh:
                fh.seek(e["offset"])
                body = fh.read(e["length"])
    data = preload + body
    with open(out_path, "wb") as fh:
        fh.write(data)
    return len(data)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    lo = sub.add_parser("locate")
    lo.add_argument("dir_vpk")
    lo.add_argument("internal")
    ex = sub.add_parser("extract")
    ex.add_argument("dir_vpk")
    ex.add_argument("internal")
    ex.add_argument("-o", "--out", required=True)
    args = ap.parse_args()

    if args.cmd == "locate":
        e, _ = _entry(args.dir_vpk, args.internal)
        idx = e["archive"]
        print(-1 if idx == INLINE else idx)
        return 0
    n = extract(args.dir_vpk, args.internal, args.out)
    print("wrote %d bytes -> %s" % (n, args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
