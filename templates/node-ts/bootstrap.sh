#!/usr/bin/env bash
set -euo pipefail

# Force non-interactive install to avoid hanging the GUI on package-manager prompts.
if command -v pnpm >/dev/null 2>&1; then
  CI=1 pnpm install --reporter=append-only
else
  CI=1 npm install --no-audit --no-fund --progress=false
fi

echo "node-ts bootstrap complete"
