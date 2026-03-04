#!/usr/bin/env bash
set -euo pipefail
rustup component add clippy rustfmt >/dev/null 2>&1 || true
cargo check
echo "rust bootstrap complete"
