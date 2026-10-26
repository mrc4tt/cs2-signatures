#!/usr/bin/env python3
"""Pull CS2_VibeSignatures symbol snapshots into data/symbols/<gamever>.json.

Two backends, same output shape, so lib_symbols does not care which was used:

  site (default)  https://sig.miksen.me publishes one content-addressed JSON per
                  game version. index.json lists {gameVersion, url, sha256, size};
                  the payload is verified against both before it is written. One
                  request per version, no auth, no rate limit.

  git             sparse clone of the analysis repo, reading
                  bin_artifacts/<gamever>/<module>/<artifact>.<platform>.yaml plus
                  binary_locks/<gamever>.json. Slower, but it reaches a game
                  version the moment it is committed, which is how a build gets
                  covered before it reaches the site.

The GitHub contents API is deliberately not used: it caps anonymous callers at 60
requests an hour, and one game version is over 3500 files.

The artifact YAML is a flat `key: value` mapping (plus one nested block for
vtable_entries) with folded long scalars, so it is parsed here directly rather
than pulling in a YAML dependency.

  python3 scripts/fetch_symbols.py --list
  python3 scripts/fetch_symbols.py --gamever 14178b
  python3 scripts/fetch_symbols.py --backend git --gamever 14180
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

import depots

SITE = "https://sig.miksen.me"
REPO = "https://github.com/mrc4tt/CS2_VibeSignatures.git"
UPSTREAM = "https://github.com/HLND2T/CS2_VibeSignatures.git"
OUT_DIR = os.path.join("data", "symbols")
CLONE_DIR = os.path.join(OUT_DIR, ".repo")
UA = "cs2-sig-tracker (+https://github.com/mrc4tt/cs2-signatures)"


def get(url):
    req = urllib.request.Request(url)
    # Cloudflare 403s the default urllib UA, so identify ourselves.
    req.add_header("User-Agent", UA)
    return urllib.request.urlopen(req, timeout=120).read()


# -- site backend --------------------------------------------------------
def site_index():
    return json.loads(get("%s/gamesymbols/index.json" % SITE))


def site_fetch(entry):
    """Download one snapshot and verify it against the index before returning."""
    raw = get("%s/gamesymbols/%s" % (SITE, entry["url"]))
    digest = hashlib.sha256(raw).hexdigest()
    if digest != entry["sha256"]:
        raise ValueError("%s: sha256 mismatch (index %s, payload %s)"
                         % (entry["gameVersion"], entry["sha256"], digest))
    if len(raw) != entry["size"]:
        raise ValueError("%s: size mismatch (index %d, payload %d)"
                         % (entry["gameVersion"], entry["size"], len(raw)))
    return json.loads(raw)


# -- git backend ---------------------------------------------------------
def parse_yaml(text):
    """Parse the flat artifact YAML subset: scalars, one nested block, folding."""
    out, lines, i = {}, text.splitlines(), 0
    while i < len(lines):
        line = lines[i]
        i += 1
        if not line.strip() or line.lstrip().startswith("#") or line[0].isspace():
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if not value:
            # Nested mapping (vtable_entries), one "k: v" per indented line.
            block = {}
            while i < len(lines) and lines[i][:1].isspace():
                k, _, v = lines[i].strip().partition(":")
                block[unquote(k)] = unquote(v.strip())
                i += 1
            out[key] = block
            continue
        # A long scalar folds onto following indented lines; join with a space.
        while i < len(lines) and lines[i][:1].isspace() and ":" not in lines[i]:
            value += " " + lines[i].strip()
            i += 1
        out[key] = scalar(unquote(value))
    return out


def unquote(s):
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"":
        return s[1:-1]
    return s


def scalar(s):
    if s in ("true", "false"):
        return s == "true"
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    return s


def kind_of(payload):
    if "vtable_entries" in payload:
        return "vtable"
    if "vfunc_index" in payload:
        return "virtualFunction"
    if "member_name" in payload:
        return "structMember"
    if "gv_name" in payload:
        return "global"
    if "patch_name" in payload:
        return "patch"
    return "function"


def sparse_clone(repo, paths):
    """Blob-filtered sparse checkout, refreshed in place on later runs."""
    if not os.path.isdir(os.path.join(CLONE_DIR, ".git")):
        os.makedirs(os.path.dirname(CLONE_DIR) or ".", exist_ok=True)
        run(["git", "clone", "--filter=blob:none", "--no-checkout", "--depth", "1",
             repo, CLONE_DIR])
    else:
        run(["git", "-C", CLONE_DIR, "remote", "set-url", "origin", repo])
        run(["git", "-C", CLONE_DIR, "fetch", "--depth", "1", "origin", "HEAD"])
        run(["git", "-C", CLONE_DIR, "reset", "--hard", "-q", "FETCH_HEAD"])
    run(["git", "-C", CLONE_DIR, "sparse-checkout", "set", "--no-cone"] + paths)
    run(["git", "-C", CLONE_DIR, "checkout", "-q"])


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.STDOUT)


def local_binaries(roots):
    """{(module, platform): sha256} of the server modules on disk, or None.

    The hash fallback in resolve_gamever() needs this. Valve re-pushes a depot
    with new manifest ids while the server binaries stay byte-identical, and a
    manifest-only match then misses the analysis that describes those exact
    bytes. Both platforms or nothing: a lock must not match on half a build.
    """
    out = {}
    for plat, root in roots.items():
        path = os.path.join(root, depots.FILES[plat]["server"])
        if not os.path.isfile(path):
            return None
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        out[("server", plat)] = h.hexdigest()
    return out


def resolve_gamever(repo, manifest_path="data/manifest.json", binaries=None):
    """Which game version describes the build sitting on disk?

    binary_locks/<ver>.json binds each version to the exact depot manifests and
    to a SHA-256 per module and platform. Matching on the manifest ids is enough
    and costs nothing extra, since check_update.py already tracks them. The hash
    path runs last, only when no manifest id matched: Valve re-pushes depots
    under new manifest ids with byte-identical server binaries, and the analysis
    of those bytes still applies. `binaries` may be a callable so the hashing is
    paid only on that path.

    Returns the version string, or None when no lock describes this build - which
    is the normal state right after a game update, before the analysis catches up.
    """
    sparse_clone(repo, ["binary_locks", "download.yaml"])
    lock_dir = os.path.join(CLONE_DIR, "binary_locks")
    manifest = None
    if os.path.isfile(manifest_path):
        with open(manifest_path) as fh:
            manifest = {str(k): str(v) for k, v in json.load(fh).items()}

    locks = []
    for fname in sorted(os.listdir(lock_dir), reverse=True):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(lock_dir, fname)) as fh:
            lock = json.load(fh)
        locks.append((lock.get("game_version", fname[:-5]), lock))
    for version, lock in locks:
        if manifest:
            have = {str(k): str(v) for k, v in
                    lock.get("download", {}).get("manifests", {}).items()}
            if have == manifest:
                return version

    # Fallback: download.yaml. The analysis repo stopped writing a lock per build
    # after 14181, while every build still gets a download.yaml entry (its
    # add_gamever.sh pins the manifests there), so without this the reference was
    # silently skipped from 14182 on. Manifest ids only - no hashes to compare.
    if manifest:
        path = os.path.join(CLONE_DIR, "download.yaml")
        if os.path.isfile(path):
            with open(path) as fh:
                for tag, have in reversed(download_manifests(fh.read())):
                    if have == manifest:
                        return tag

    if callable(binaries):
        binaries = binaries()
    if binaries:
        for version, lock in locks:
            locked = lock.get("binaries", {})
            if all(locked.get(m, {}).get(p, {}).get("sha256") == digest
                   for (m, p), digest in binaries.items()):
                return version
    return None


def download_manifests(text):
    """[(tag, {depot: manifest})] from download.yaml, in file order. Stdlib only.

    Reads just the shape that file has: `- tag: "<ver>"` opens an entry and the
    quoted `"<depot>": "<manifest>"` lines under `manifests:` belong to it.
    """
    out, tag, mans = [], None, None
    for line in text.splitlines():
        m = re.match(r'\s*-\s*tag:\s*"?([^"\s#]+)"?', line)
        if m:
            if tag is not None:
                out.append((tag, mans))
            tag, mans = m.group(1), {}
            continue
        m = re.match(r'\s+"(\d+)":\s*"(\d+)"', line)
        if m and tag is not None:
            mans[m.group(1)] = m.group(2)
    if tag is not None:
        out.append((tag, mans))
    return out


def git_versions(repo):
    sparse_clone(repo, ["binary_locks"])
    d = os.path.join(CLONE_DIR, "binary_locks")
    return sorted(f[:-5] for f in os.listdir(d) if f.endswith(".json"))


def git_fetch(repo, gamever):
    """Assemble a snapshot from bin_artifacts/<gamever> + binary_locks.

    A version the repo does not carry is an error, never a silent fall back to
    another repo: which analysis a verdict came from has to stay unambiguous.
    """
    sparse_clone(repo, ["binary_locks", "bin_artifacts/%s" % gamever])
    root = os.path.join(CLONE_DIR, "bin_artifacts", gamever)
    if not os.path.isdir(root):
        # The tree lists the versions that exist without checking out any blob.
        have = [os.path.basename(p.rstrip("/")) for p in subprocess.run(
            ["git", "-C", CLONE_DIR, "ls-tree", "--name-only", "HEAD",
             "bin_artifacts/"], capture_output=True, text=True).stdout.split()]
        raise SystemExit(
            "no bin_artifacts/%s in %s\n  that repo has: %s\n  pass --upstream to"
            " read %s instead (the report then labels the origin)"
            % (gamever, repo, " ".join(have) or "nothing", UPSTREAM))

    records = []
    for module in sorted(os.listdir(root)):
        mod_dir = os.path.join(root, module)
        if not os.path.isdir(mod_dir):
            continue
        for fname in sorted(os.listdir(mod_dir)):
            if not fname.endswith(".yaml"):
                continue
            artifact, _, rest = fname[:-5].rpartition(".")
            if rest not in ("linux", "windows") or not artifact:
                continue
            with open(os.path.join(mod_dir, fname)) as fh:
                payload = parse_yaml(fh.read())
            records.append({
                "id": "%s/%s" % (module, fname),
                "module": module,
                "artifact": artifact,
                "symbolName": payload.get("func_name") or payload.get("gv_name")
                or payload.get("patch_name") or artifact,
                "platform": rest,
                "kind": kind_of(payload),
                "payload": payload,
            })

    lock_path = os.path.join(CLONE_DIR, "binary_locks", "%s.json" % gamever)
    binaries, download = {}, {}
    if os.path.isfile(lock_path):
        with open(lock_path) as fh:
            lock = json.load(fh)
        binaries, download = lock.get("binaries", {}), lock.get("download", {})

    head = subprocess.run(["git", "-C", CLONE_DIR, "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    return {
        "schemaVersion": 3,
        "source": {"gameVersion": gamever, "origin": repo, "commit": head,
                   "fileCount": len(records)},
        "binaries": binaries,
        "download": download,
        "records": records,
    }


# -- entry point ---------------------------------------------------------
def write(snapshot, gamever):
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "%s.json" % gamever)
    with open(out, "w") as fh:
        json.dump(snapshot, fh, indent=1, sort_keys=True)
    print("[%s] %d records -> %s" % (gamever, len(snapshot["records"]), out))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=("site", "git"), default="site")
    ap.add_argument("--gamever", default=None,
                    help="version to fetch (default: newest available)")
    ap.add_argument("--all", action="store_true", help="fetch every version")
    ap.add_argument("--list", action="store_true", help="list versions and exit")
    ap.add_argument("--repo", default=REPO, help="git backend source repo")
    ap.add_argument("--upstream", action="store_true",
                    help="git backend: read %s instead" % UPSTREAM)
    ap.add_argument("--resolve", action="store_true",
                    help="print the game version matching data/manifest.json "
                         "and exit; empty output means no analysis covers this "
                         "build yet")
    ap.add_argument("--manifest", default="data/manifest.json")
    ap.add_argument("--linux-root", default="bin_linux",
                    help="download dir hashed when no lock matches the "
                         "manifest ids (--resolve)")
    ap.add_argument("--windows-root", default="bin_win")
    args = ap.parse_args()
    repo = UPSTREAM if args.upstream else args.repo

    if args.resolve:
        found = resolve_gamever(repo, args.manifest, lambda: local_binaries(
            {"linux": args.linux_root, "windows": args.windows_root}))
        if found:
            print(found)
            return 0
        print("no binary_lock in %s matches %s" % (repo, args.manifest),
              file=sys.stderr)
        return 1

    if args.backend == "site":
        versions = site_index()["versions"]
        if args.list:
            for v in versions:
                print("%-8s %6d symbols  %s"
                      % (v["gameVersion"], v["fileCount"], v["lastPublishTime"]))
            return 0
        wanted = versions if args.all else [
            v for v in versions
            if args.gamever in (None, v["gameVersion"])][:1]
        if not wanted:
            print("no such version on %s" % SITE, file=sys.stderr)
            return 1
        for entry in wanted:
            snapshot = site_fetch(entry)
            snapshot.setdefault("source", {})["origin"] = SITE
            write(snapshot, entry["gameVersion"])
        return 0

    versions = git_versions(repo)
    if args.list:
        print(" ".join(versions))
        return 0
    wanted = versions if args.all else [args.gamever or versions[-1]]
    for gamever in wanted:
        write(git_fetch(repo, gamever), gamever)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except urllib.error.HTTPError as e:
        print("HTTP %d: %s" % (e.code, e.reason), file=sys.stderr)
        sys.exit(1)
