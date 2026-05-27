#!/usr/bin/env bash
# Verifica que el working tree completo del repositorio no contenga
# firmas externas en archivos versionados.
#
# Uso:
#   ./scripts/verify-clean-worktree.sh
#
# Salida: imprime matches encontrados (cero esperado). Si hay matches,
# sale con código 1.

set -euo pipefail

PATTERN='claude|anthropic|co-authored.*claude|🤖|generated with claude|made with claude|cursor|copilot|codeium|AI[- ]?(generated|assist)'

MATCHES=$(grep -rniE "$PATTERN" \
  --include="*.md" --include="*.py" --include="*.sql" --include="*.toml" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=.venv \
  --exclude-dir=scripts \
  . 2>/dev/null || true)

if [ -n "$MATCHES" ]; then
  echo "VIOLACIÓN: firmas externas detectadas en working tree"
  echo "$MATCHES"
  exit 1
else
  echo "OK: cero firmas externas detectadas en working tree"
  exit 0
fi
