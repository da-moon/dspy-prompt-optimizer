#!/bin/bash

# DSPy Prompt Optimizer - Comprehensive Linting Script
# Runs all linters in the order specified in CLAUDE.md

set -e  # Exit on any error

echo "🔧 DSPy Prompt Optimizer - Running Linters"
echo "=========================================="

# Check if we have internet connectivity for sourcery
echo "🌐 Checking internet connectivity..."
INTERNET_AVAILABLE=false
if command -v curl >/dev/null 2>&1; then
    if curl -s --connect-timeout 5 https://api.sourcery.ai >/dev/null 2>&1; then
        INTERNET_AVAILABLE=true
        echo "✅ Internet connectivity detected (using curl)"
    else
        echo "❌ No internet connectivity (curl test failed)"
    fi
elif command -v wget >/dev/null 2>&1; then
    if wget -q --spider --timeout=5 https://api.sourcery.ai >/dev/null 2>&1; then
        INTERNET_AVAILABLE=true
        echo "✅ Internet connectivity detected (using wget)"
    else
        echo "❌ No internet connectivity (wget test failed)"
    fi
else
    echo "⚠️  Neither curl nor wget available - skipping internet check"
fi

echo ""

# 1. pyright (strict mode) - MUST fix all type errors
echo "🔍 Running pyright (strict mode)..."
poetry run pyright --project pyrightconfig.strict.json .
echo "✅ pyright passed"
echo ""

# 2. mypy - MUST fix all type checking issues
echo "🔍 Running mypy..."
poetry run mypy .
echo "✅ mypy passed"
echo ""

# 3. pylint - Fix unless conflicts with type checkers
echo "🔍 Running pylint..."
poetry run pylint -j`nproc` prompt_optimizer
echo "✅ pylint passed"
echo ""

# 4. sourcery - Apply improvements where feasible (only if internet available)
if [ "$INTERNET_AVAILABLE" = true ]; then
    echo "🔍 Running sourcery..."
    poetry run sourcery review --verbose --no-summary . | cat
    echo "✅ sourcery completed"
else
    echo "⚠️  Skipping sourcery (no internet connectivity)"
fi
echo ""

# 5. e2e tests - Run e2e tests for commands
echo "🧪 Running e2e tests..."
scripts/e2e_test.sh
echo "✅ e2e tests passed"
echo ""

echo "🎉 All linting and tests completed successfully!"