# Contributing

Thanks for contributing.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Checks

```bash
ruff check .
black --check .
pytest
```

## Pull request checklist

- Keep changes focused and well-scoped.
- Add or update tests when behavior changes.
- Update docs for user-facing changes.
