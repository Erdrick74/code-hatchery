#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 <template> <destination> [--oss-meta]"
  echo "Templates: python python-github-ready node-ts go rust java cpp csharp php lua"
}

write_if_missing() {
  local path="$1"
  local content="$2"
  if [ ! -f "$path" ]; then
    printf "%s" "$content" >"$path"
  fi
}

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  usage
  exit 1
fi

BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$1"
DEST="$2"
OSS_META=0

if [ "${3:-}" = "--oss-meta" ]; then
  OSS_META=1
elif [ -n "${3:-}" ]; then
  usage
  exit 1
fi

if [ -d "$BASE/templates/$TEMPLATE" ]; then
  TEMPLATE_DIR="$BASE/templates/$TEMPLATE"
elif [ -d "$BASE/$TEMPLATE" ]; then
  TEMPLATE_DIR="$BASE/$TEMPLATE"
else
  echo "Unknown template: $TEMPLATE"
  exit 1
fi

if [ -e "$DEST" ]; then
  echo "Destination exists: $DEST"
  exit 1
fi

cp -r "$TEMPLATE_DIR" "$DEST"

if [ "$OSS_META" -eq 1 ]; then
  year="$(date +%Y)"
  holder="${USER:-Project Author}"

  license_text="MIT License

Copyright (c) ${year} ${holder}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the \"Software\"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"

  contributing_text="# Contributing

Thanks for contributing.

## Pull request checklist

- Keep changes focused and well-scoped.
- Add or update tests when behavior changes.
- Update docs for user-facing changes.
"

  conduct_text="# Code of Conduct

- Be respectful and constructive.
- Focus feedback on ideas and code, not people.
- No harassment, insults, or discriminatory language.
"

  security_text="# Security Policy

If you discover a security issue, report it privately to the maintainer before
opening a public issue.
"

  gitignore_text=".venv/
__pycache__/
*.py[cod]
*.egg-info/
.pytest_cache/
.ruff_cache/
.mypy_cache/
.coverage
htmlcov/
.DS_Store
"

  write_if_missing "$DEST/LICENSE" "$license_text"
  write_if_missing "$DEST/CONTRIBUTING.md" "$contributing_text"
  write_if_missing "$DEST/CODE_OF_CONDUCT.md" "$conduct_text"
  write_if_missing "$DEST/SECURITY.md" "$security_text"
  write_if_missing "$DEST/.gitignore" "$gitignore_text"
fi

echo "Created $DEST from $TEMPLATE"
