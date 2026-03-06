# Python Starter (GitHub Ready)

A clean Python app starter designed for local projects and later open-source publishing.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Run

```bash
python -m app.main
```

## GitHub Readiness

- Includes `.gitignore` for Python tooling and local envs.
- Includes `LICENSE` (MIT) for open-source usage.
- Includes `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and `SECURITY.md`.

## Quality

```bash
ruff check .
black --check .
pytest
```
