# Hyprland Integration (Optional)

Code Hatchery works without Hyprland-specific bindings. If you use Hyprland, add optional keybinds like these:

```ini
bind = $mainMod, N, exec, ~/.local/bin/code-hatchery
```

Then reload Hyprland:

```bash
hyprctl reload
```

## Optional close helper

If you want a `SUPER+C` helper that avoids killing Code Hatchery when it is focused, create this script:

```bash
mkdir -p ~/.local/bin
cat > ~/.local/bin/code-hatchery-close-or-killactive <<'EOF2'
#!/usr/bin/env bash
set -euo pipefail

active="$(hyprctl activewindow 2>/dev/null || true)"
if printf '%s\n' "$active" | grep -Eq 'title:[[:space:]]*(Code Hatchery)'; then
  exit 0
fi

hyprctl dispatch killactive
EOF2
chmod +x ~/.local/bin/code-hatchery-close-or-killactive
```

Then bind it:

```ini
bind = $mainMod, C, exec, ~/.local/bin/code-hatchery-close-or-killactive
```
