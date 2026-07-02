#!/usr/bin/env bash
# Download ONLY server.so (linux) + server.dll (windows) for CS2 (app 730)
# using DepotDownloader + a filelist regex, so it pulls a few MB, not the whole
# ~40 GB install.
#
# Requires: DepotDownloader on PATH (dotnet tool) and .NET runtime.
#   dotnet tool install -g DepotDownloader   # or use the release binary
#
# Steam login: CS2 dedicated-server depots generally need a real account (not
# anonymous). Provide creds via env:
#   STEAM_USER=youracct STEAM_PASS=yourpass ./download_bins.sh
# On first interactive run, complete SteamGuard once; DepotDownloader caches the
# session so later CI runs reuse it. Never commit creds — pass via CI secrets.
set -euo pipefail

DD="${DEPOTDOWNLOADER:-DepotDownloader}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
APP=730

: "${STEAM_USER:?set STEAM_USER}"
: "${STEAM_PASS:?set STEAM_PASS}"

auth=(-username "$STEAM_USER" -password "$STEAM_PASS" -remember-password)

echo ">> linux server.so"
"$DD" -app "$APP" -os linux -osarch 64 \
  -filelist "$HERE/filelist_linux.txt" \
  -dir "$ROOT/bin_linux" "${auth[@]}"

echo ">> windows server.dll"
"$DD" -app "$APP" -os windows -osarch 64 \
  -filelist "$HERE/filelist_windows.txt" \
  -dir "$ROOT/bin_win" "${auth[@]}"

# Resolve the actual downloaded paths for the caller.
LINUX_SO="$(find "$ROOT/bin_linux" -name 'libserver.so' -o -name 'server.so' | head -1 || true)"
WIN_DLL="$(find "$ROOT/bin_win" -name 'server.dll' | head -1 || true)"
echo "LINUX_SO=$LINUX_SO"
echo "WIN_DLL=$WIN_DLL"
