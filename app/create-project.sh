#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <template> <destination>"
  echo "Templates: python node-ts go rust java cpp csharp php lua"
  exit 1
fi

BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$1"
DEST="$2"

if [ ! -d "$BASE/$TEMPLATE" ]; then
  echo "Unknown template: $TEMPLATE"
  exit 1
fi

if [ -e "$DEST" ]; then
  echo "Destination exists: $DEST"
  exit 1
fi

cp -r "$BASE/$TEMPLATE" "$DEST"
echo "Created $DEST from $TEMPLATE"
