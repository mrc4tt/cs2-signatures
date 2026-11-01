#!/usr/bin/env python3
"""Valve KeyValues gamedata (Metamod / SourceMod style) -> the JSON shape the
tracker reads.

    "Games" { "csgo" { "Signatures" { "Key" { "library" "server"
                                               "linux" "..." "windows" "..." } }
                       "Offsets"    { "Key" { "linux" "12" "windows" "11" } } } }

becomes {"Key": {"signatures": {"library", "linux", "windows"}}} /
{"Key": {"offsets": {"linux": 12, "windows": 11}}} - the CounterStrikeSharp
gamedata.json layout every other script here already takes. Signatures in the
escaped style ("\\x48\\x8B\\x2A") are turned into IDA style with \\x2A as the
wildcard; IDA style passes through with "??" normalised to "?".

stdlib only.
"""
import re

_TOKEN = re.compile(r'"((?:[^"\\]|\\.)*)"|([{}])|//[^\n]*')
_ESCAPED_BYTE = re.compile(r'\\[xX]([0-9A-Fa-f]{2})')


def parse(text):
    """Minimal KeyValues -> nested dicts. Quoted keys and values, braces, // comments."""
    root = {}
    stack = [root]
    pending = None
    for m in _TOKEN.finditer(text):
        quoted, brace = m.group(1), m.group(2)
        if quoted is None and brace is None:
            continue  # comment
        if brace == "{":
            child = {}
            stack[-1][pending if pending is not None else ""] = child
            stack.append(child)
            pending = None
        elif brace == "}":
            if len(stack) > 1:
                stack.pop()
            pending = None
        elif pending is None:
            pending = quoted
        else:
            stack[-1][pending] = quoted
            pending = None
    return root


def normalize_sig(sig):
    """Escaped or IDA-style signature -> IDA style, one '?' per wildcard byte."""
    if "\\x" in sig or "\\X" in sig:
        out = []
        for byte in _ESCAPED_BYTE.findall(sig):
            out.append("?" if byte.upper() == "2A" else byte.upper())
        return " ".join(out)
    return " ".join("?" if t.startswith("?") else t for t in sig.split())


def _int(value):
    try:
        return int(str(value), 0)
    except ValueError:
        return None


def to_gamedata(text, game="csgo"):
    """KeyValues gamedata text -> CounterStrikeSharp-shaped dict."""
    doc = parse(text)
    games = doc.get("Games", doc)
    block = games.get(game) or {}
    out = {}
    for name, entry in (block.get("Signatures") or {}).items():
        if not isinstance(entry, dict):
            continue
        sigs = {"library": entry.get("library", "server")}
        for plat in ("linux", "windows"):
            if isinstance(entry.get(plat), str) and entry[plat]:
                sigs[plat] = normalize_sig(entry[plat])
        out[name] = {"signatures": sigs}
    for name, entry in (block.get("Offsets") or {}).items():
        if not isinstance(entry, dict):
            continue
        offs = {}
        for plat in ("linux", "windows"):
            if plat in entry and _int(entry[plat]) is not None:
                offs[plat] = _int(entry[plat])
        out.setdefault(name, {})["offsets"] = offs
    return out
