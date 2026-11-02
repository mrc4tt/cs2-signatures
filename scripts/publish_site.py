#!/usr/bin/env python3
"""Publish the CS2 binaries to a static download site (bins.miksen.me).

The self-hosted replacement for publish_bins.py's Forgejo releases: no git
forge involved, so the .so/.dll never land in any repository's Releases page.
Each CS2 update copies the validated binaries into

    <dest>/<version>/libserver.so libengine2.so libclient.so server.dll
                     engine2.dll SHA256SUMS meta.json

then rewrites <dest>/latest/ (symlinks to the newest files), <dest>/index.html (the page people open) and <dest>/versions.json
(the same list for scripts) and <dest>/releases.rss (feed for bots), prunes all but the newest --keep versions, and -
when DISCORD_BINS_WEBHOOK is set - posts one embed linking the new version.

nginx serves <dest> as-is (server-ops etc/nginx/bins.miksen.me.conf).

Version: --version wins; else PatchVersion from steam.inf (1.41.9.4); else
ClientVersion; else the --iso date. Re-publishing the same version replaces its
files in place and does not post to Discord again unless --announce is given.

    python3 scripts/publish_site.py --linux bin_linux/.../libserver.so ...
    python3 scripts/publish_site.py --rebuild-index     # page only, no copy
    python3 scripts/publish_site.py --preview           # print the embed

stdlib only.
"""
import argparse
import datetime
import hashlib
import html
import json
import os
import re
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from publish_bins import parse_steaminf  # noqa: E402

DEFAULT_DEST = "/srv/cs2-bins"
DEFAULT_URL = "https://bins.miksen.me"
REPO_URL = "https://github.com/mrc4tt/cs2-signatures"

# CLI flag -> (platform, description). Order is the order on the page.
ASSETS = (
    ("linux", "linux", "server"),
    ("linux_engine2", "linux", "engine2"),
    ("linux_client", "linux", "client"),
    ("windows", "windows", "server"),
    ("windows_engine2", "windows", "engine2"),
)

# Only these names are ever read from a version directory, so a stray file
# dropped there is not advertised on the page.
VERSION_RE = re.compile(r"^[0-9A-Za-z][0-9A-Za-z._-]*$")
INFO_KEYS = ("PatchVersion", "ClientVersion", "ServerVersion",
             "SourceRevision", "VersionDate", "VersionTime")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_version(version, info, iso):
    if version:
        return version
    for key in ("PatchVersion", "ClientVersion"):
        if info.get(key):
            return info[key]
    return iso or datetime.date.today().isoformat()


def human_size(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return ("%d %s" % (n, unit)) if unit == "B" else ("%.1f %s" % (n, unit))
        n /= 1024.0
    return "%d B" % n


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


def write_atomic(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        fh.write(text)
    os.chmod(tmp, 0o644)
    os.replace(tmp, path)


def stage_version(dest, version, info, files, sigs=None):
    """Copy `files` [(flag, path)] into <dest>/<version>/ atomically.

    Built in a hidden sibling dir, then swapped in, so a download never sees a
    half-copied file and a failed copy leaves the old version untouched."""
    final = os.path.join(dest, version)
    tmp = os.path.join(dest, ".staging-%s" % version)
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)
    os.chmod(tmp, 0o755)
    entries = []
    for flag, src in files:
        plat, desc = next((p, d) for f, p, d in ASSETS if f == flag)
        name = os.path.basename(src)
        dst = os.path.join(tmp, name)
        shutil.copyfile(src, dst)
        os.chmod(dst, 0o644)
        entries.append({"name": name, "platform": plat, "module": desc,
                        "size": os.path.getsize(dst), "sha256": sha256(dst)})
    zips = {}
    for plat in sorted({e["platform"] for e in entries}):
        name = ZIP_NAME % (version, plat)
        zpath = os.path.join(tmp, name)
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
            for e in entries:
                if e["platform"] == plat:
                    zf.write(os.path.join(tmp, e["name"]), e["name"])
        os.chmod(zpath, 0o644)
        zips[plat] = {"name": name, "size": os.path.getsize(zpath),
                      "sha256": sha256(zpath)}
    meta = {"version": version, "published": now_utc(),
            "info": {k: info[k] for k in INFO_KEYS if info.get(k)},
            "files": entries, "zips": zips}
    if sigs:
        meta["sigs"] = sigs
    write_atomic(os.path.join(tmp, "meta.json"),
                 json.dumps(meta, indent=2) + "\n")
    write_atomic(os.path.join(tmp, "SHA256SUMS"),
                 "".join("%s  %s\n" % (e["sha256"], e["name"])
                         for e in entries + list(zips.values())))
    old = os.path.join(dest, ".old-%s" % version)
    shutil.rmtree(old, ignore_errors=True)
    if os.path.isdir(final):
        os.rename(final, old)
    os.rename(tmp, final)
    shutil.rmtree(old, ignore_errors=True)
    return meta


def load_versions(dest):
    """Every published version's meta.json, newest published first."""
    out = []
    for name in os.listdir(dest) if os.path.isdir(dest) else ():
        if not VERSION_RE.match(name):
            continue
        path = os.path.join(dest, name, "meta.json")
        try:
            with open(path) as fh:
                meta = json.load(fh)
        except (OSError, ValueError):
            continue
        if meta.get("version") == name:
            out.append(meta)
    out.sort(key=lambda m: m.get("published", ""), reverse=True)
    return out


def prune(dest, keep, current):
    """Delete all but the newest `keep` versions (never `current`)."""
    removed = []
    for meta in load_versions(dest)[keep:]:
        if meta["version"] != current:
            shutil.rmtree(os.path.join(dest, meta["version"]))
            removed.append(meta["version"])
    return removed


def title(meta):
    info = meta.get("info", {})
    t = "CS2 %s" % meta["version"]
    build = info.get("ClientVersion")
    if build and build != meta["version"]:
        t += " · build %s" % build
    return t


def game_version(meta):
    """CS2_VibeSignatures / sig.miksen.me name a build by its gameVersion:
    PatchVersion without dots (1.41.9.4 -> 14194)."""
    patch = meta.get("info", {}).get("PatchVersion") or meta["version"]
    digits = patch.replace(".", "")
    return digits if digits.isdigit() else None


ZIP_NAME = "cs2-%s-%s.zip"  # (version, platform)

CSS = """
:root{--bg:#0b0d10;--panel:#14181d;--panel2:#191e24;--line:#262c34;--text:#e8e4d8;
--dim:#8a8f98;--t:#e0a33a;--ct:#5d9be0;--red:#e04a3a;--green:#6fd36f}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);min-height:100vh;
font:15px/1.55 ui-monospace,"SFMono-Regular",Menlo,Consolas,monospace}
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:9;
background:repeating-linear-gradient(0deg,rgba(255,255,255,.02) 0 1px,transparent 1px 3px)}
a{color:inherit;text-decoration:none}
.wrap{max-width:940px;margin:0 auto;padding:0 20px}
nav{border-bottom:1px solid var(--line);background:rgba(20,24,29,.7)}
nav .wrap{display:flex;align-items:center;justify-content:space-between;height:56px}
.logo{font:900 20px/1 Impact,"Arial Black",sans-serif;letter-spacing:.06em}
.logo b{color:var(--t)}.logo i{font-style:normal;color:var(--ct)}
nav .links a{color:var(--dim);margin-left:18px;font-size:13px;letter-spacing:.1em;text-transform:uppercase}
nav .links a:hover{color:var(--t)}
.hero{padding:44px 0 28px}
.eyebrow{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;
color:var(--dim);font-size:12px;letter-spacing:.25em;text-transform:uppercase}
.pill{letter-spacing:.05em;text-transform:none;border:1px solid var(--line);background:var(--panel);
padding:4px 12px;border-radius:999px;font-size:13px;color:var(--text)}
.pill .dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:8px;
background:var(--green);box-shadow:0 0 10px var(--green)}
.pill.bad .dot{background:var(--red);box-shadow:0 0 10px var(--red)}
h1{font:900 clamp(56px,13vw,112px)/.95 Impact,"Arial Black",sans-serif;letter-spacing:-.01em;
color:var(--t);text-shadow:0 0 40px rgba(224,163,58,.22);margin:14px 0 10px}
.sub{color:var(--dim);font-size:14px}.sub b{color:var(--text);font-weight:600}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px;margin-top:28px}
.card{background:var(--panel);border:1px solid var(--line);border-top:3px solid var(--c);padding:18px}
.card.linux{--c:var(--t)}.card.windows{--c:var(--ct)}
.card h2{font-size:12px;letter-spacing:.25em;color:var(--c);margin-bottom:12px}
.card h2 span{color:var(--dim);letter-spacing:.1em}
.file{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:9px 0;
border-top:1px solid var(--line)}
.file:first-of-type{border-top:0}
.file a.n{font-weight:600}.file a.n:hover{color:var(--c)}
.file .sz{color:var(--dim);font-size:13px;white-space:nowrap}
.hash{display:block;color:#5c626b;font-size:11px;cursor:pointer;max-width:100%;
overflow:hidden;text-overflow:ellipsis;white-space:nowrap;border:0;background:none;font-family:inherit;text-align:left}
.hash:hover{color:var(--c)}.hash.ok{color:var(--green)}
.btn{display:flex;justify-content:center;gap:8px;margin-top:14px;padding:11px;border:1px solid var(--c);
color:var(--c);letter-spacing:.12em;text-transform:uppercase;font-size:13px;transition:.15s}
.btn:hover{background:var(--c);color:var(--bg)}
.btn small{opacity:.7;letter-spacing:0}
.meta{margin-top:14px;font-size:12px;color:var(--dim)}.meta a{color:var(--dim);text-decoration:underline}
h3{font-size:12px;letter-spacing:.25em;color:var(--dim);margin:40px 0 12px}
details{background:var(--panel);border:1px solid var(--line);margin-bottom:8px}
summary{list-style:none;cursor:pointer;display:flex;gap:16px;align-items:center;padding:12px 16px}
summary::-webkit-details-marker{display:none}
summary::before{content:"\\25B8";color:var(--t);transition:.15s}
details[open] summary::before{transform:rotate(90deg)}
summary .v{font-weight:700;color:var(--text);min-width:90px}
summary .g{color:var(--t);min-width:60px}summary .d{color:var(--dim);flex:1}
summary .c{color:var(--dim);font-size:12px;text-align:right}
details .body{border-top:1px solid var(--line);padding:4px 16px 14px}
details .row{display:grid;grid-template-columns:80px 1fr auto;gap:12px;padding:7px 0;
border-top:1px solid var(--line);font-size:14px;align-items:center}
details .row:first-child{border-top:0}
details .row .p.linux{color:var(--t)}details .row .p.windows{color:var(--ct)}
details .row a:hover{color:var(--t)}
.empty{padding:80px 0;text-align:center;color:var(--dim)}
footer{border-top:1px solid var(--line);margin-top:48px;padding:20px 0 40px;color:#5c626b;font-size:12px}
footer a{text-decoration:underline}
footer .legal{margin-top:8px;color:#454a52}
.toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%) translateY(80px);
background:var(--panel2);border:1px solid var(--green);color:var(--green);padding:8px 16px;
font-size:13px;transition:.2s;z-index:10}.toast.on{transform:translateX(-50%)}
.chg{display:inline-block;margin-left:8px;font-size:11px;padding:0 6px;border:1px solid var(--line);
vertical-align:1px}
.chg.same{color:#5c626b}.chg.changed{color:var(--t);border-color:rgba(224,163,58,.4)}
.chg.new{color:var(--green);border-color:rgba(111,211,111,.4)}
.delta{margin-top:10px;font-size:13px;color:var(--dim)}
.projs{display:flex;flex-wrap:wrap;gap:6px 16px;margin-top:12px;font-size:12px;color:var(--dim)}
.projs b{color:var(--green);font-weight:600}.projs .bad b{color:var(--red)}
.perma{margin-top:8px;font-size:12px;color:#5c626b}.perma a{color:var(--dim);text-decoration:underline}
.perma code{color:var(--t)}
.sdot{width:8px;height:8px;border-radius:50%;background:var(--green);flex:none}
.sdot.bad{background:var(--red)}
details .pill{display:inline-block;margin:12px 0 0}
@media(max-width:560px){summary .d{display:none}nav .links a{margin-left:10px}}
"""

JS = """
document.querySelectorAll('.hash').forEach(function(b){b.addEventListener('click',function(){
var t=document.getElementById('toast');navigator.clipboard.writeText(b.dataset.h).then(function(){
b.classList.add('ok');t.classList.add('on');setTimeout(function(){t.classList.remove('on');
b.classList.remove('ok')},1400)})})});
"""

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#e0a33a">
<meta property="og:type" content="website">
<meta property="og:site_name" content="CS2 BINS">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<link rel="canonical" href="{url}">
<link rel="alternate" type="application/rss+xml" title="CS2 binaries" href="releases.rss">
<style>{css}</style>
</head>
<body>
<nav><div class="wrap"><a class="logo" href="./"><b>CS2</b> <i>BINS</i></a>
<div class="links"><a href="releases.rss">RSS</a><a href="versions.json">JSON</a>
<a href="{repo}">GitHub</a></div></div></nav>
<main class="wrap">
{body}
</main>
<footer><div class="wrap">The exact files the <a href="{repo}">cs2-signatures</a> tracker
validated, one set per CS2 update &middot; newest {keep} kept &middot; page updated {updated}
<div class="legal">&copy; {year} Miksen &middot; site and tooling MIT-licensed &middot;
Counter-Strike 2 binaries &copy; Valve Corporation, shared unmodified for plugin development
&middot; not affiliated with or endorsed by Valve</div>
</div></footer>
<div class="toast" id="toast">sha256 copied</div>
<script>{js}</script>
</body>
</html>
"""


def file_changes(versions):
    """{version: {file name: (kind, detail)}} comparing each version with the
    one before it (versions newest first, as load_versions returns them).

    kind: "same"    detail = oldest kept version with these exact bytes
          "changed" detail = size delta in bytes vs the previous version
          "new"     detail = None (no file of that name before)
    The oldest kept version gets no entry: nothing older to compare with."""
    out = {}
    origin = {}  # name -> (sha256, version those bytes first appeared in)
    prev = None
    for meta in reversed(versions):
        v = meta["version"]
        files = {f["name"]: f for f in meta.get("files", [])}
        if prev is not None:
            ch = {}
            for name, f in files.items():
                pf = prev.get(name)
                if pf is None:
                    ch[name] = ("new", None)
                elif pf["sha256"] == f["sha256"]:
                    ch[name] = ("same", origin.get(name, (None, prev_v))[1])
                else:
                    ch[name] = ("changed", f["size"] - pf["size"])
            out[v] = ch
        for name, f in files.items():
            if origin.get(name, (None,))[0] != f["sha256"]:
                origin[name] = (f["sha256"], v)
        prev, prev_v = files, v
    return out


def signed_size(n):
    if n == 0:
        return "same size"
    return ("+" if n > 0 else "-") + human_size(abs(n))


def change_tag(c):
    if not c:
        return ""
    kind, detail = c
    if kind == "same":
        return '<span class="chg same">unchanged since %s</span>' % html.escape(detail)
    if kind == "new":
        return '<span class="chg new">new</span>'
    return '<span class="chg changed">changed &middot; %s</span>' % signed_size(detail)


def change_summary(changes, prev_version):
    if not changes or not prev_version:
        return ""
    kinds = [k for k, _ in changes.values()]
    bits = []
    for kind, label in (("changed", "changed"), ("new", "new"), ("same", "unchanged")):
        if kinds.count(kind):
            bits.append("%d %s" % (kinds.count(kind), label))
    return "%s vs %s" % (", ".join(bits), html.escape(prev_version))


def sigs_pill(sigs, live):
    if not sigs:
        return ""
    when = html.escape((sigs.get("checked") or "")[:16].replace("T", " "))
    href = ("%s/commit/%s" % (REPO_URL, html.escape(sigs["commit"]))
            if sigs.get("commit") else REPO_URL)
    return ('<a class="pill%s" href="%s" title="%s checked %s UTC">'
            '<span class="dot"></span>signatures: %s</a>'
            % ("" if sigs.get("ok") else " bad", href,
               "signature check, last" if live else "signature result at publish,",
               when, html.escape(sigs.get("text", ""))))


def sigs_projects(sigs):
    if not sigs or not sigs.get("projects"):
        return ""
    return '<div class="projs">%s</div>' % "".join(
        '<span class="%s">%s <b>%d/%d</b></span>'
        % ("ok" if p["ok"] == p["total"] else "bad", html.escape(p["name"]),
           p["ok"], p["total"])
        for p in sigs["projects"])


def _file_line(v, f, change=None):
    n = html.escape(f["name"])
    h = html.escape(f["sha256"])
    return ('<div class="file"><div style="min-width:0"><a class="n" href="%s/%s" download>%s</a>%s'
            '<button class="hash" data-h="%s" title="click to copy">sha256 %s</button></div>'
            '<span class="sz">%s</span></div>'
            % (v, n, n, change_tag(change), h, h[:16] + "&hellip;", human_size(f["size"])))


def render_hero(meta, changes=None, prev_version=None):
    v = html.escape(meta["version"])
    info = meta.get("info", {})
    gv = game_version(meta)
    changes = changes or {}
    sub = []
    if gv:
        sub.append("gameVersion <b>%s</b>" % gv)
    if info.get("ClientVersion"):
        sub.append("build <b>%s</b>" % html.escape(info["ClientVersion"]))
    if info.get("SourceRevision"):
        sub.append("rev <b>%s</b>" % html.escape(info["SourceRevision"]))
    if info.get("VersionDate"):
        sub.append("<b>%s</b>" % html.escape(info["VersionDate"]))
    cards = []
    for plat, label in (("linux", "LINUX"), ("windows", "WINDOWS")):
        fs = [f for f in meta.get("files", []) if f["platform"] == plat]
        if not fs:
            continue
        z = meta.get("zips", {}).get(plat)
        btn = ('<a class="btn" href="%s/%s" download>&#11015; download all <small>%s</small></a>'
               % (v, html.escape(z["name"]), human_size(z["size"]))) if z else ""
        cards.append('<div class="card %s"><h2>%s <span>&middot; %d files</span></h2>%s%s</div>'
                     % (plat, label, len(fs),
                        "".join(_file_line(v, f, changes.get(f["name"])) for f in fs), btn))
    summary = change_summary(changes, prev_version)
    latest = ('<div class="perma">always-newest links: <a href="latest/libserver.so">/latest/libserver.so</a>'
              ' &middot; <a href="latest/cs2-linux.zip">/latest/cs2-linux.zip</a>'
              ' &middot; <a href="latest/cs2-windows.zip">/latest/cs2-windows.zip</a>'
              ' &middot; any file name works under <code>/latest/</code></div>')
    return ('<section class="hero" id="v%s"><div class="eyebrow"><span>Latest build</span>%s</div>'
            '<h1>%s</h1><div class="sub">%s</div>%s%s<div class="grid">%s</div>'
            '<div class="meta">published %s &middot; <a href="%s/SHA256SUMS">SHA256SUMS</a></div>%s'
            '</section>'
            % (v, sigs_pill(meta.get("sigs"), True), v, " &middot; ".join(sub),
               sigs_projects(meta.get("sigs")),
               '<div class="delta">%s</div>' % summary if summary else "",
               "".join(cards), html.escape(meta.get("published", "")[:10]), v, latest))


def render_older(meta, changes=None, prev_version=None):
    v = html.escape(meta["version"])
    info = meta.get("info", {})
    gv = game_version(meta) or ""
    changes = changes or {}
    rows = "".join(
        '<div class="row"><span class="p %s">%s</span><span><a href="%s/%s" download>%s</a>%s</span>'
        '<span class="sz">%s</span></div>'
        % (f["platform"], f["platform"], v, html.escape(f["name"]),
           html.escape(f["name"]), change_tag(changes.get(f["name"])), human_size(f["size"]))
        for f in meta.get("files", []))
    zips = " &middot; ".join('<a href="%s/%s" download>%s.zip</a>' % (v, html.escape(z["name"]), p)
                             for p, z in sorted(meta.get("zips", {}).items()))
    sigs = meta.get("sigs")
    dot = ('<span class="sdot %s" title="signatures at publish: %s"></span>'
           % ("ok" if sigs.get("ok") else "bad", html.escape(sigs.get("text", "")))) if sigs else ""
    summary = change_summary(changes, prev_version)
    return ('<details id="v%s"><summary>%s<span class="v">%s</span><span class="g">%s</span>'
            '<span class="d">%s</span><span class="c">%s</span></summary>'
            '<div class="body">%s%s%s<div class="meta">%s%s<a href="%s/SHA256SUMS">SHA256SUMS</a>'
            '</div></div></details>'
            % (v, dot, v, gv, html.escape(info.get("VersionDate") or meta.get("published", "")[:10]),
               summary or "%d files" % len(meta.get("files", [])),
               sigs_pill(sigs, False), sigs_projects(sigs), rows,
               zips, " &middot; " if zips else "", v))


def og_description(meta):
    bits = []
    gv = game_version(meta)
    if gv:
        bits.append("gameVersion %s" % gv)
    plats = sorted({f["platform"] for f in meta.get("files", [])})
    bits.append("%d files (%s)" % (len(meta.get("files", [])), " + ".join(plats)))
    if meta.get("sigs"):
        bits.append("signatures: %s" % meta["sigs"].get("text", ""))
    return " · ".join(bits)


def render_index(versions, keep, base_url=DEFAULT_URL):
    url = base_url.rstrip("/") + "/"
    if versions:
        changes = file_changes(versions)
        older = [m["version"] for m in versions[1:]] + [None]
        body = render_hero(versions[0], changes.get(versions[0]["version"]), older[0])
        if versions[1:]:
            body += "<h3>OLDER BUILDS</h3>" + "".join(
                render_older(m, changes.get(m["version"]), older[i + 1])
                for i, m in enumerate(versions[1:]))
        title = "CS2 %s binaries" % versions[0]["version"]
        desc = og_description(versions[0])
    else:
        body = '<div class="empty">Nothing published yet.</div>'
        title = "CS2 binaries"
        desc = "CS2 server binaries (.so/.dll) per game version."
    return PAGE.format(title=html.escape(title), desc=html.escape(desc), url=html.escape(url),
                       css=CSS, js=JS, repo=REPO_URL, keep=keep, body=body,
                       year=datetime.date.today().year,
                       updated=html.escape(now_utc().replace("T", " ")[:16] + " UTC"))


def rfc822(stamp):
    """meta 'published' (ISO, UTC) -> RSS pubDate."""
    try:
        d = datetime.datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ")
    except (TypeError, ValueError):
        d = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    return d.strftime("%a, %d %b %Y %H:%M:%S +0000")


def render_rss(versions, base_url):
    """RSS 2.0, one item per version, guid = version: the shape the old Forgejo
    releases.rss had, so a feed reader (ximik's Discord bot) needs only the URL
    changed."""
    url = base_url.rstrip("/")
    esc = html.escape
    items = []
    for m in versions:
        v = m["version"]
        links = "".join('<li><a href="%s/%s/%s">%s</a> (%s)</li>'
                        % (url, v, f["name"], f["name"], human_size(f["size"]))
                        for f in m.get("files", []))
        items.append(
            "<item><title>%s</title><link>%s/#v%s</link>"
            '<guid isPermaLink="false">bins-%s</guid><pubDate>%s</pubDate>'
            "<description>%s</description></item>"
            % (esc(title(m)), url, esc(v), esc(v), rfc822(m.get("published")),
               esc("<ul>%s</ul>" % links)))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0"><channel><title>CS2 server binaries</title>'
            "<link>%s/</link><description>CS2 .so/.dll per game version"
            "</description>%s</channel></rss>\n" % (url, "".join(items)))


def write_latest(dest, meta):
    """<dest>/latest/: relative symlinks to the newest version's files, with
    version-free zip names (cs2-linux.zip), so a script can always fetch
    https://bins.miksen.me/latest/libserver.so. Rebuilt and swapped whole."""
    final = os.path.join(dest, "latest")
    tmp = os.path.join(dest, ".latest-tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    if meta is None:
        shutil.rmtree(final, ignore_errors=True)
        return
    os.makedirs(tmp)
    os.chmod(tmp, 0o755)
    v = meta["version"]
    sums = []
    links = [(f["name"], f["name"], f["sha256"]) for f in meta.get("files", [])]
    links += [(z["name"], "cs2-%s.zip" % plat, z["sha256"])
              for plat, z in sorted(meta.get("zips", {}).items())]
    for src, alias, digest in links:
        os.symlink(os.path.join("..", v, src), os.path.join(tmp, alias))
        sums.append("%s  %s\n" % (digest, alias))
    os.symlink(os.path.join("..", v, "meta.json"), os.path.join(tmp, "meta.json"))
    write_atomic(os.path.join(tmp, "SHA256SUMS"), "".join(sums))
    old = os.path.join(dest, ".latest-old")
    shutil.rmtree(old, ignore_errors=True)
    if os.path.lexists(final):
        os.rename(final, old)
    os.rename(tmp, final)
    shutil.rmtree(old, ignore_errors=True)


def sig_snapshot(badge_path):
    """The tracker's current verdict (reports/badge.json + each project's
    reports/<id>/status.json tally) plus the repo commit holding that report."""
    try:
        with open(badge_path) as fh:
            badge = json.load(fh)
    except (OSError, ValueError, TypeError):
        return None
    reports = os.path.dirname(os.path.abspath(badge_path))
    names = {}
    try:
        import projects as P
        names = {p["id"]: P.name(p) for p in P.load()}
    except Exception:
        pass
    projs = []
    for pid in sorted(os.listdir(reports), key=str.lower):
        try:
            with open(os.path.join(reports, pid, "status.json")) as fh:
                tally = json.load(fh).get("tally", {})
        except (OSError, ValueError):
            continue
        bad = sum(tally.get(k, 0) for k in ("broken", "ambiguous", "no_binary", "missing_sig"))
        projs.append({"name": names.get(pid, pid), "ok": tally.get("ok", 0),
                      "total": tally.get("ok", 0) + bad})
    order = {n: i for i, n in enumerate(names.values())}
    projs.sort(key=lambda p: order.get(p["name"], len(order)))
    commit = None
    try:
        import subprocess
        commit = subprocess.run(["git", "-C", os.path.dirname(reports), "rev-parse", "HEAD"],
                                capture_output=True, text=True, timeout=10).stdout.strip() or None
    except Exception:
        pass
    return {"text": badge.get("message", ""),
            "ok": badge.get("color") in ("brightgreen", "green"),
            "projects": projs, "commit": commit, "checked": now_utc()}


def update_sigs(dest, version, sigs):
    """Refresh the signature snapshot stored in <dest>/<version>/meta.json."""
    path = os.path.join(dest, version, "meta.json")
    try:
        with open(path) as fh:
            meta = json.load(fh)
    except (OSError, ValueError):
        return False
    meta["sigs"] = sigs
    write_atomic(path, json.dumps(meta, indent=2) + "\n")
    return True


def write_index(dest, keep, base_url=DEFAULT_URL):
    versions = load_versions(dest)
    write_latest(dest, versions[0] if versions else None)
    write_atomic(os.path.join(dest, "releases.rss"),
                 render_rss(versions, base_url))
    write_atomic(os.path.join(dest, "index.html"), render_index(versions, keep, base_url))
    write_atomic(os.path.join(dest, "versions.json"), json.dumps(
        {"latest": versions[0]["version"] if versions else None,
         "versions": versions}, indent=2) + "\n")
    return versions


def build_embed(meta, base_url):
    url = base_url.rstrip("/")
    v = meta["version"]
    lines = []
    for f in meta.get("files", []):
        lines.append("`%-8s` [%s](%s/%s/%s) · %s"
                     % (f["platform"], f["name"], url, v, f["name"],
                        human_size(f["size"])))
    info = meta.get("info", {})
    fields = [{"name": k, "value": "`%s`" % info[k], "inline": True}
              for k in ("ClientVersion", "SourceRevision", "VersionDate")
              if info.get(k)]
    return {"title": "New CS2 binaries: %s" % title(meta),
            "url": "%s/#v%s" % (url, v),
            "description": "\n".join(lines) + "\n\n[All versions](%s/)" % url,
            "color": 0x2B7BE4, "fields": fields,
            "footer": {"text": "cs2-signatures"},
            "timestamp": meta.get("published")}


def announce(meta, base_url, webhooks):
    from post_discord import post, split_webhooks  # noqa: E402
    payload = {"embeds": [build_embed(meta, base_url)],
               "allowed_mentions": {"parse": []}}
    mention = os.environ.get("DISCORD_BINS_MENTION", "").strip()
    if mention.isdigit():
        payload["content"] = "<@%s>" % mention
        payload["allowed_mentions"] = {"users": [mention]}
    ok = True
    for hook in split_webhooks([webhooks]):
        try:
            post(hook, payload)
        except Exception as e:  # one dead webhook must not block the others
            print("discord bins post failed: %s" % e, file=sys.stderr)
            ok = False
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    for flag, _, _ in ASSETS:
        ap.add_argument("--" + flag.replace("_", "-"), dest=flag)
    ap.add_argument("--version")
    ap.add_argument("--steam-inf", default="bin_linux/game/csgo/steam.inf")
    ap.add_argument("--iso", help="date fallback for the version")
    ap.add_argument("--dest", default=os.environ.get("BINS_DIR") or DEFAULT_DEST)
    ap.add_argument("--url", default=os.environ.get("BINS_URL") or DEFAULT_URL)
    ap.add_argument("--keep", type=int,
                    default=int(os.environ.get("BINS_KEEP") or 5))
    ap.add_argument("--badge", default="reports/badge.json",
                    help="tracker verdict stored with the version (needs "
                         "reports/<id>/status.json beside it)")
    ap.add_argument("--announce", action="store_true",
                    help="post to Discord even if this version existed")
    ap.add_argument("--no-announce", action="store_true")
    ap.add_argument("--rebuild-index", action="store_true",
                    help="only rewrite index.html/versions.json")
    ap.add_argument("--preview", action="store_true",
                    help="print the Discord embed for the latest version")
    args = ap.parse_args()

    if args.preview:
        versions = load_versions(args.dest)
        if not versions:
            print("nothing published in %s" % args.dest, file=sys.stderr)
            return 1
        print(json.dumps(build_embed(versions[0], args.url), indent=2))
        return 0

    os.makedirs(args.dest, exist_ok=True)
    os.chmod(args.dest, 0o755)
    if args.rebuild_index:
        # The newest version's signature result follows the tracker: a later
        # run that fixes (or breaks) a signature against the same binaries
        # changes that version's verdict. Older versions keep theirs. Only
        # when the checked binaries ARE that version (steam.inf agrees).
        versions = load_versions(args.dest)
        current = resolve_version(None, parse_steaminf(args.steam_inf), None)
        if versions and versions[0]["version"] == current:
            sigs = sig_snapshot(args.badge)
            if sigs:
                update_sigs(args.dest, current, sigs)
        print("index: %d version(s)" % len(write_index(args.dest, args.keep, args.url)))
        return 0

    files = [(f, getattr(args, f)) for f, _, _ in ASSETS
             if getattr(args, f) and os.path.isfile(getattr(args, f))]
    if not files:
        print("no binary files found to publish", file=sys.stderr)
        return 1
    info = parse_steaminf(args.steam_inf)
    version = resolve_version(args.version, info, args.iso)
    if not VERSION_RE.match(version):
        print("refusing unsafe version %r" % version, file=sys.stderr)
        return 1
    existed = os.path.isfile(os.path.join(args.dest, version, "meta.json"))
    meta = stage_version(args.dest, version, info, files, sig_snapshot(args.badge))
    for v in prune(args.dest, args.keep, version):
        print("pruned %s" % v)
    write_index(args.dest, args.keep, args.url)
    print("published %d file(s) as %s -> %s/#v%s"
          % (len(files), version, args.url.rstrip("/"), version))

    hooks = os.environ.get("DISCORD_BINS_WEBHOOK", "")
    if hooks and not args.no_announce and (args.announce or not existed):
        return 0 if announce(meta, args.url, hooks) else 1
    if hooks and existed:
        print("version %s already published - no Discord post" % version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
