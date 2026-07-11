#!/usr/bin/env bash
# Download ONLY the CS2 server/engine2 binaries via DepotDownloader, using the
# exact per-OS depots + a filelist so it pulls a few MB, not the ~40 GB install.
#
#   depot 2347771  windows  -> server.dll, engine2.dll
#   depot 2347773  linux    -> libserver.so, libengine2.so
#
# These depots are downloadable ANONYMOUSLY — no Steam login required. If your
# setup needs a login, export STEAM_USER/STEAM_PASS and they'll be used.
#
# Requires DepotDownloader on PATH (or set DEPOTDOWNLOADER=/path/to/it):
#   dotnet tool install -g DepotDownloader
set -euo pipefail

DD="${DEPOTDOWNLOADER:-DepotDownloader}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
APP=730
DEPOT_WIN=2347771
DEPOT_LINUX=2347773
DEPOT_CONTENT=2347770   # game content depot — holds game/csgo/steam.inf (version)

auth=()
if [ -n "${STEAM_USER:-}" ]; then
  auth=(-username "$STEAM_USER" -password "${STEAM_PASS:-}" -remember-password)
fi

echo ">> linux depot $DEPOT_LINUX"
"$DD" -app "$APP" -depot "$DEPOT_LINUX" \
  -filelist "$HERE/filelist_linux.txt" \
  -dir "$ROOT/bin_linux" "${auth[@]}"

echo ">> windows depot $DEPOT_WIN"
"$DD" -app "$APP" -depot "$DEPOT_WIN" \
  -filelist "$HERE/filelist_windows.txt" \
  -dir "$ROOT/bin_win" "${auth[@]}"

# steam.inf (a few KB) from the content depot -> ClientVersion for release tags.
# Non-fatal: if it fails, publish_bins falls back to the manifest id.
echo ">> content depot $DEPOT_CONTENT (steam.inf)"
"$DD" -app "$APP" -depot "$DEPOT_CONTENT" \
  -filelist "$HERE/filelist_steaminf.txt" \
  -dir "$ROOT/bin_linux" "${auth[@]}" || echo "WARN: steam.inf fetch failed"

# Emit resolved paths for the caller (server is what the sigs target).
echo "LINUX_SO=$(find "$ROOT/bin_linux" -name 'libserver.so' | head -1 || true)"
echo "LINUX_ENGINE2=$(find "$ROOT/bin_linux" -name 'libengine2.so' | head -1 || true)"
echo "WIN_DLL=$(find "$ROOT/bin_win" -name 'server.dll' | head -1 || true)"
echo "WIN_ENGINE2=$(find "$ROOT/bin_win" -name 'engine2.dll' | head -1 || true)"
