#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$ROOT/.." && pwd)"
DEST_ROOT="$REPO_ROOT/.cursor/skills"
MANIFEST="$ROOT/MANIFEST.json"

skills=$(python -c "import json; print(' '.join(json.load(open('$MANIFEST'))['skills']))")
mkdir -p "$DEST_ROOT"
for skill in $skills; do
  src="$ROOT/$skill"
  dest="$DEST_ROOT/$skill"
  test -d "$src" || { echo "missing skill: $skill"; exit 1; }
  rm -rf "$dest"
  cp -R "$src" "$dest"
  echo "Synced $skill -> $dest"
done
echo "Done."