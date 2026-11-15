#!/usr/bin/env bash
# Push main para github.com/mastercorisco/GET
# Requer GITHUB_TOKEN (fine-grained PAT com Contents: read/write) na VM ou no ambiente.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

TOKEN="${GITHUB_TOKEN:-${GH_TOKEN:-}}"
if [[ -z "$TOKEN" ]]; then
  echo "[ERRO] Defina GITHUB_TOKEN ou GH_TOKEN (PAT com write no repo GET)." >&2
  exit 1
fi

REMOTE="https://x-access-token:${TOKEN}@github.com/mastercorisco/GET.git"

echo "[sync] A enviar main para GitHub..."
GIT_TERMINAL_PROMPT=0 git push "$REMOTE" main:main

echo "[sync] Concluido. Verifique: https://github.com/mastercorisco/GET"