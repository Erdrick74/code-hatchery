# Code Hatchery

Code Hatchery is a Linux project scaffolder with a focused GUI and starter templates.

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

## Hyprland keybind example

```ini
bind = $mainMod, N, exec, ~/.local/bin/code-hatchery
bind = $mainMod, C, exec, ~/.local/bin/code-hatchery-close-or-killactive
```

Then run:

```bash
hyprctl reload
```
