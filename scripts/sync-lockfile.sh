#!/bin/bash
# Sync yarn.lock with package.json and stage for commit
# Run this after adding/removing frontend dependencies
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../frontend" || exit 1
yarn install
echo "yarn.lock synced. Run: git add frontend/yarn.lock && git commit -m 'chore: sync yarn.lock'"
