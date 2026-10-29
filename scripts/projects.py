"""Registry of tracked plugin projects - one CSS-format gamedata.json each.

`data/projects.json` is the single source of truth. Each entry:

    id       stable slug -> data/<id>/, reports/<id>/, docs/<id>.md
    name     display name (defaults to id)
    repo     "owner/name" on `host`
    upstream optional "owner/name" (github.com) the tracked repo is forked from
    host     forge hostname (default "github.com"; e.g. "git.miksen.me")
    branch   branch to pull the gamedata from
    path     path to the gamedata.json inside that repo
    private  true -> fetch needs a token; false -> anonymous fetch works

All the tracked gamedata files share the CS2 game binaries, so the download +
manifest-diff steps stay game-global; only fetch / validate / report loop over
projects. Path + URL layout lives here so every script agrees on it.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(ROOT, "data", "projects.json")


def load(path=REGISTRY, only=None):
    """Return the project list, optionally filtered to a single id (`only`)."""
    with open(path) as fh:
        projects = json.load(fh)
    if only:
        projects = [p for p in projects if p["id"] == only]
        if not projects:
            raise KeyError("no project with id %r in %s" % (only, path))
    return projects


def name(p):
    return p.get("name", p["id"])


def host(p):
    return p.get("host", "github.com")


def is_github(p):
    return host(p) == "github.com"


def gamedata_path(p):
    return os.path.join("data", p["id"], "gamedata.json")


def status_path(p):
    return os.path.join("reports", p["id"], "status.json")


def docs_path(p):
    return os.path.join("docs", "%s.md" % p["id"])


def repo_url(p):
    return "https://%s/%s" % (host(p), p["repo"])


def blob_url(p):
    if is_github(p):
        return "https://github.com/%s/blob/%s/%s" % (
            p["repo"], p["branch"], p["path"])
    # Forgejo/Gitea web file view.
    return "https://%s/%s/src/branch/%s/%s" % (
        host(p), p["repo"], p["branch"], p["path"])
