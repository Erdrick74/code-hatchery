# Code Hatchery

Code Hatchery is a Linux project scaffolder with a focused GUI and starter templates.

## Runtime dependencies

- `bash`
- `python3`
- `python-gobject` / `PyGObject` (`gi`)
- `gtk3`
- `gtk-layer-shell` (for overlay behavior)

Optional:

- `code` (VS Code launcher) for auto-open
- one terminal emulator (`kitty`, `footclient`, `alacritty`, `wezterm`, or `xterm`) for CLI fallback mode

## Install

```bash
git clone https://github.com/Erdrick74/code-hatchery.git
cd code-hatchery
./install.sh
```

By default it installs under `~/.local`.

To install somewhere else:

```bash
PREFIX=/your/prefix ./install.sh
```

## Uninstall

```bash
./uninstall.sh
```

## Run

```bash
code-hatchery
```

Default project creation path is the current user's home directory (`$HOME`), and can be changed in the UI/CLI.
