#!/usr/bin/env bash
set -euo pipefail
dotnet restore
dotnet build
echo "csharp bootstrap complete"
