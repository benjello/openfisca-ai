#!/usr/bin/env bash
# Pre-push hook : rejoue les vérifications openfisca-ai en local avant de pousser.
# Généré par : openfisca-ai setup-hooks <package-path>

set -e

echo "╔══════════════════════════════════════════╗"
echo "║  openfisca-ai pre-push check             ║"
echo "╚══════════════════════════════════════════╝"

echo ""
echo "▶ Validation des paramètres..."
uv run openfisca-ai validate-parameters . || {
    echo "✗ Paramètres invalides. Corrigez avant de pousser."
    exit 1
}

echo ""
echo "▶ Validation du code..."
uv run openfisca-ai validate-code . || {
    echo "✗ Code invalide. Corrigez avant de pousser."
    exit 1
}

echo ""
echo "▶ Tests..."
uv run pytest tests/ -q --timeout=120 || {
    echo "✗ Tests échoués. Corrigez avant de pousser."
    exit 1
}

echo ""
echo "▶ Review du diff..."
REMOTE_REF=$(git rev-parse @{upstream} 2>/dev/null || git rev-parse origin/master 2>/dev/null || git rev-parse origin/main 2>/dev/null || echo "HEAD~5")
DIFF=$(git diff "${REMOTE_REF}"...HEAD)
if [ -n "$DIFF" ]; then
    echo "$DIFF" | uv run openfisca-ai review-diff . --markdown 2>/dev/null || true
fi

echo ""
echo "════════════════════════════════════════════"
echo "  ✓ Pre-push checks passed"
echo "════════════════════════════════════════════"
