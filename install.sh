#!/usr/bin/env bash
set -euo pipefail

# Core installer is compositor-agnostic; no Hyprland-specific integration is required.
PREFIX="${PREFIX:-$HOME/.local}"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_SHARE="$PREFIX/share/code-hatchery"
BIN_DIR="$PREFIX/bin"
APPS_DIR="$PREFIX/share/applications"
ICON_BASE="$PREFIX/share/icons/hicolor"

mkdir -p "$APP_SHARE" "$BIN_DIR" "$APPS_DIR"

install -m 0755 "$REPO_DIR/app/code-hatchery" "$APP_SHARE/code-hatchery"
install -m 0755 "$REPO_DIR/app/code-hatchery-gui-gtk.py" "$APP_SHARE/code-hatchery-gui-gtk.py"
install -m 0755 "$REPO_DIR/app/code-hatchery.cli" "$APP_SHARE/code-hatchery.cli"
install -m 0755 "$REPO_DIR/app/create-project.sh" "$APP_SHARE/create-project.sh"

for t in python python-github-ready node-ts go rust java cpp csharp php lua; do
  rm -rf "$APP_SHARE/$t"
  cp -a "$REPO_DIR/app/templates/$t" "$APP_SHARE/$t"
done

cat > "$BIN_DIR/code-hatchery" <<LAUNCH
#!/usr/bin/env bash
set -euo pipefail
exec "$APP_SHARE/code-hatchery" "\$@"
LAUNCH

chmod +x "$BIN_DIR/code-hatchery"

# Install icon at common sizes.
ICON_SRC="$REPO_DIR/app/icons/code-hatchery.png"
mkdir -p "$ICON_BASE/1024x1024/apps"
cp -f "$ICON_SRC" "$ICON_BASE/1024x1024/apps/code-hatchery.png"

if python3 - <<'PY' >/dev/null 2>&1
import gi
from gi.repository import GdkPixbuf
PY
then
  python3 - <<PY
from pathlib import Path
import gi

gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf

src = Path('$ICON_SRC')
base = Path('$ICON_BASE')
pix = GdkPixbuf.Pixbuf.new_from_file(str(src))
for s in [512, 256, 128, 64, 48, 32]:
    outdir = base / f'{s}x{s}' / 'apps'
    outdir.mkdir(parents=True, exist_ok=True)
    scaled = pix.scale_simple(s, s, GdkPixbuf.InterpType.BILINEAR)
    scaled.savev(str(outdir / 'code-hatchery.png'), 'png', [], [])
print('icons written')
PY
else
  mkdir -p "$ICON_BASE/128x128/apps" "$ICON_BASE/48x48/apps"
  cp -f "$ICON_SRC" "$ICON_BASE/128x128/apps/code-hatchery.png"
  cp -f "$ICON_SRC" "$ICON_BASE/48x48/apps/code-hatchery.png"
fi

cat > "$APPS_DIR/code-hatchery.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=Code Hatchery
Comment=Create a new starter project in Code Hatchery
Exec=$BIN_DIR/code-hatchery
Icon=code-hatchery
Terminal=false
Categories=Development;
StartupNotify=false
DESKTOP

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -f -t "$ICON_BASE" >/dev/null 2>&1 || true
fi

echo "Installed Code Hatchery to: $APP_SHARE"
echo "Launch command: $BIN_DIR/code-hatchery"
echo "Desktop file:   $APPS_DIR/code-hatchery.desktop"
