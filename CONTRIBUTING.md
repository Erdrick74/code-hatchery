# Contributing

Thanks for contributing to Code Hatchery.

## Development notes

- Keep changes focused and easy to review.
- Update docs when behavior changes.
- Validate both GUI and CLI fallback flows when touching launcher code.

## Local checks

You can run quick syntax checks with:

```bash
python3 -m py_compile src/code_hatchery/gui_gtk.py scripts/code-hatchery-gui-gtk.py
bash -n scripts/code-hatchery scripts/code-hatchery.cli scripts/create-project.sh install.sh uninstall.sh
```
