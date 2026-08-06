#!/bin/bash
# NexDoc Data Pipeline
# Run from project root: ./scripts/pipeline/run.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo "=== NexDoc Data Pipeline ==="
echo ""

echo "[1/5] Generating MCC alias registry..."
python3 "$SCRIPT_DIR/generate_mcc_aliases.py"
echo ""

echo "[2/5] Building master college details..."
python3 "$SCRIPT_DIR/build_college_details.py"
echo ""

echo "[3/5] Building normalized cutoffs & AIQ mapping..."
python3 "$SCRIPT_DIR/6_build_normalized_cutoffs.py"
echo ""

echo "[4/5] Generating readable copies..."
python3 "$SCRIPT_DIR/6_readable_copy.py"
echo ""

echo "[5/5] Updating college offered course levels (UG, PG, SS)..."
python3 "$SCRIPT_DIR/7_update_college_course_levels.py"
echo ""

echo "=== Pipeline complete ==="

