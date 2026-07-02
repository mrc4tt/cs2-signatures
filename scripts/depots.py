"""Shared CS2 depot constants (verified against ianlucas/cs2-signatures).

CS2 app 730. The dedicated-server binaries live in two per-OS depots that are
downloadable **anonymously** (no Steam login needed):

    2347771  windows  -> game/csgo/bin/win64/server.dll        (+ engine2.dll)
    2347773  linux    -> game/csgo/bin/linuxsteamrt64/libserver.so (+ libengine2.so)

The CSS gamedata `library` field is "server" or "engine2"; we map it to the
right file per platform so a sig is scanned against the binary it belongs to.
"""
APP = 730

DEPOTS = {
    "windows": 2347771,
    "linux": 2347773,
}

# {platform: {library: relative_path_in_download}}
FILES = {
    "windows": {
        "server": "game/csgo/bin/win64/server.dll",
        "engine2": "game/bin/win64/engine2.dll",
    },
    "linux": {
        "server": "game/csgo/bin/linuxsteamrt64/libserver.so",
        "engine2": "game/bin/linuxsteamrt64/libengine2.so",
    },
}


def steamdb_link(depot, manifest):
    return ("https://steamdb.info/depot/%s/history/?changeid=M:%s"
            % (depot, manifest))
