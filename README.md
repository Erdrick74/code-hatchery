# Code Hatchery

Code Hatchery is a Linux project scaffolder with a focused GUI, starter templates for popular languages, and automatic terminal fallback when GUI mode is unavailable.

Repository layout is now conventional as well:

- `src/code_hatchery/` for Python runtime code
- `scripts/` for launch and creation scripts
- `templates/` for bundled project templates
- `assets/` for icons and static assets

## Open-source metadata

This repository now includes:

- `LICENSE` (MIT)
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Runtime behavior

- Primary mode: GTK GUI
- Fallback mode: terminal CLI (if GUI requirements are unavailable)

## Runtime dependencies

- `bash`
- `python3`
- `python-gobject` / `PyGObject` (`gi`) for GUI mode
- `gtk3` for GUI mode
- `gtk-layer-shell` for GUI overlay behavior

Optional:

- `code` (VS Code launcher) for auto-open
- one terminal emulator (`kitty`, `footclient`, `alacritty`, `wezterm`, or `xterm`) for fallback CLI mode

## Install dependencies

### Arch Linux

```bash
sudo pacman -S --needed bash python python-gobject gtk3 gtk-layer-shell
```

### Debian / Ubuntu

```bash
sudo apt update
sudo apt install -y bash python3 python3-gi gir1.2-gtk-3.0 libgtk-layer-shell0
```

### Fedora

```bash
sudo dnf install -y bash python3 python3-gobject gtk3 gtk-layer-shell
```

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

Default project creation path is `~/Chronos/projects`, and can be changed in the UI/CLI.

## Repository checks

```bash
ruff check .
pytest
```

## Open-source metadata bootstrap

Project creation now supports an optional metadata bootstrap that adds:

- `LICENSE` (MIT)
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `.gitignore` (if missing)

GUI:

- Toggle `Include open-source metadata files` during project creation.

CLI:

- Prompted during creation (`Include open-source metadata files? [Y/n]`)
- Optional flags: `--oss-meta` or `--no-oss-meta`

## Available templates

- `python`
- `python-github-ready`
- `node-ts`
- `go`
- `rust`
- `java`
- `cpp`
- `csharp`
- `php`
- `lua`
