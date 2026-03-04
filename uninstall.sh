#!/usr/bin/env bash
set -euo pipefail

# Core uninstall is compositor-agnostic; removes only Code Hatchery user-local files.
PREFIX="${PREFIX:-$HOME/.local}"
APP_SHARE="$PREFIX/share/code-hatchery"
BIN_DIR="$PREFIX/bin"
APPS_DIR="$PREFIX/share/applications"
ICON_BASE="$PREFIX/share/icons/hicolor"

rm -rf "$APP_SHARE"
rm -f "$BIN_DIR/code-hatchery"
rm -f "$APPS_DIR/code-hatchery.desktop"

for s in 1024 512 256 128 64 48 32; do
  rm -f "$ICON_BASE/${s}x${s}/apps/code-hatchery.png"
done

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -f -t "$ICON_BASE" >/dev/null 2>&1 || true
fi

echo "Uninstalled Code Hatchery from PREFIX=$PREFIX"
