#!/usr/bin/env bash
set -euo pipefail
mvn -q -DskipTests compile
echo "java bootstrap complete"
