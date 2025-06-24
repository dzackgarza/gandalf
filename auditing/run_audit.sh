#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- [AUDIT] Starting Gandalf Automated Audit ---"

# --- Check 1: Code Formatting and Linting ---
echo "[1/3] Running Linter and Formatter Check..."
# This assumes uv-installed tools are in the path of the activated venv
flake8 gandalf_workshop/ main.py
black --check gandalf_workshop/ main.py
echo "✅ Linter and Formatter Check Passed."

# --- Check 2: Structural Integrity Audit ---
echo "[2/3] Running Structural Integrity Audit..."
python3 auditing/audit_structure.py
echo "✅ Structural Integrity Audit Passed."

# --- Check 3: Basic Functionality & Entrypoint Test ---
echo "[3/3] Running Basic Functionality Test..."
python3 main.py --help > /dev/null
python3 main.py --prompt "Dry Run Test" > /dev/null
echo "✅ Basic Functionality Test Passed."

echo "--- [AUDIT] All automated checks passed successfully! ---"
