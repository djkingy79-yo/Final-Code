#!/bin/bash
# Sync yarn.lock with package.json and stage for commit
# Run this after adding/removing frontend dependencies
cd "$(dirname "$0")/frontend" || exit 1
yarn install
echo "yarn.lock synced. Run: git add frontend/yarn.lock && git commit -m 'chore: sync yarn.lock'"
