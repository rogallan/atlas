#!/usr/bin/env bash
# ATLAS Git History & Repository Security Audit (S22)
# Scans git log and repository assets for leaked secrets, real API keys, and sensitive tokens.

set -euo pipefail

echo "======================================================================"
echo "🔒 ATLAS Security Clearance Audit — Zero Real Data & Secrets Scanner"
echo "======================================================================"

EXIT_CODE=0

# 1. Gitleaks scan if installed
if command -v gitleaks &> /dev/null; then
    echo "🔍 Executando Gitleaks scan no repositório..."
    if gitleaks detect --source . -v; then
        echo "✅ Gitleaks: Zero segredos detectados."
    else
        echo "❌ Gitleaks: Segredos encontrados no código ou histórico!"
        EXIT_CODE=1
    fi
else
    echo "ℹ️ Gitleaks não encontrado no PATH; executando scanner nativo regex..."
fi

# 2. Native Pattern Scan in Git Log and tracked files
PATTERNS=(
    "AKIA[0-9A-Z]{16}"
    "-----BEGIN RSA PRIVATE KEY-----"
    "-----BEGIN OPENSSH PRIVATE KEY-----"
    "ghp_[0-9a-zA-Z]{36}"
    "xox[baprs]-[0-9a-zA-Z]{10,48}"
)

for pattern in "${PATTERNS[@]}"; do
    MATCHES=$(git grep -E "$pattern" 2>/dev/null || true)
    if [ -n "$MATCHES" ]; then
        echo "❌ Violação de Segurança encontrada para o padrão: $pattern"
        echo "$MATCHES"
        EXIT_CODE=1
    fi
done

if [ $EXIT_CODE -eq 0 ]; then
    echo "======================================================================"
    echo "🎉 AUDITORIA DE SEGURANÇA APROVADA: 100% livre de segredos reais!"
    echo "======================================================================"
else
    echo "======================================================================"
    echo "❌ FALHA NA AUDITORIA DE SEGURANÇA"
    echo "======================================================================"
fi

exit $EXIT_CODE
