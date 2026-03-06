# Python Starter

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

## Quality

```bash
ruff check .
black --check .
pytest
```
