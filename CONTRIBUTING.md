# Contributing

Thanks for contributing to Code Hatchery.

## Development notes

- Keep changes focused and easy to review.
- Update docs when behavior changes.
- Validate both GUI and CLI fallback flows when touching launcher code.

## Local checks

You can run quick syntax checks with:

```bash
python3 -m py_compile app/code-hatchery-gui-gtk.py
bash -n app/code-hatchery app/code-hatchery.cli app/create-project.sh install.sh uninstall.sh
```
