#!/bin/bash
# NexDoc Data Pipeline
# Run from project root: ./scripts/pipeline/run.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo "=== NexDoc Data Pipeline ==="
echo ""

echo "[1/4] Generating MCC alias registry..."
python3 "$SCRIPT_DIR/generate_mcc_aliases.py"
echo ""

echo "[2/4] Building master college details..."
python3 "$SCRIPT_DIR/build_college_details.py"
echo ""

echo "[3/4] Building normalized cutoffs & AIQ mapping..."
python3 "$SCRIPT_DIR/6_build_normalized_cutoffs.py"
echo ""

echo "[4/4] Generating readable copies..."
python3 "$SCRIPT_DIR/6_readable_copy.py"
echo ""

echo "=== Pipeline complete ==="

