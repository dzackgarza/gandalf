#!/bin/bash

# Script to run live tests and generate an audit report framework.

AUDIT_DIR="audits"
AUDIT_REPORT_FILE="$AUDIT_DIR/V1-0-1.md"
OUTPUT_DIR="outputs"

# Ensure audit directory exists
mkdir -p $AUDIT_DIR

# Header for the audit report
echo "# Audit Report: V1.0.1 Live Tests" > "$AUDIT_REPORT_FILE"
echo "" >> "$AUDIT_REPORT_FILE"
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')" >> "$AUDIT_REPORT_FILE"
echo "" >> "$AUDIT_REPORT_FILE"
echo "This report details the results of the \`make test-live\` command, assessing the generated artifacts for each prompt." >> "$AUDIT_REPORT_FILE"
echo "The 'Assessment' sections for Completeness, Correctness, and Runnable are to be filled in after manual review of the generated artifacts." >> "$AUDIT_REPORT_FILE"
echo "" >> "$AUDIT_REPORT_FILE"

# --- Run make test-live ---
echo ">>> Running make test-live... This may take some time and requires API keys in .env <<<"
if ! make test-live; then
    echo "Error: 'make test-live' failed. Audit report will be incomplete." >> "$AUDIT_REPORT_FILE"
    echo "Error: 'make test-live' failed. Please check the output above."
    # Decide if script should exit or continue to document what was generated before failure
    # For now, let's continue to document, as some outputs might exist.
fi
echo "" >> "$AUDIT_REPORT_FILE"
echo "--- 'make test-live' execution complete ---" >> "$AUDIT_REPORT_FILE"
echo "" >> "$AUDIT_REPORT_FILE"


# Helper function to add test case sections to the report
add_test_case_to_report() {
    local prompt_desc="$1"
    local unique_id="$2"
    local test_prompt_text="$3"
    local output_path="$OUTPUT_DIR/$unique_id"

    echo "---" >> "$AUDIT_REPORT_FILE"
    echo "" >> "$AUDIT_REPORT_FILE"
    echo "## Test Case: $prompt_desc" >> "$AUDIT_REPORT_FILE"
    echo "" >> "$AUDIT_REPORT_FILE"
    echo "**Prompt:** \"$test_prompt_text\"" >> "$AUDIT_REPORT_FILE"
    echo "**Unique ID:** \`$unique_id\`" >> "$AUDIT_REPORT_FILE"
    echo "**Output Path:** \`$output_path/\`" >> "$AUDIT_REPORT_FILE"
    echo "" >> "$AUDIT_REPORT_FILE"
    echo "**Artifacts Found:**" >> "$AUDIT_REPORT_FILE"
    if [ -d "$output_path" ]; then
        if [ -z "$(ls -A $output_path)" ]; then
            echo "- Directory is empty." >> "$AUDIT_REPORT_FILE"
        else
            for item in $(ls $output_path); do
                echo "- \`$item\`" >> "$AUDIT_REPORT_FILE"
            done
        fi
    else
        echo "- Output directory not found." >> "$AUDIT_REPORT_FILE"
    fi
    echo "" >> "$AUDIT_REPORT_FILE"
    echo "**Assessment:**" >> "$AUDIT_REPORT_FILE"
    echo "- **Completeness:** [TODO: Assess completeness]" >> "$AUDIT_REPORT_FILE"
    echo "- **Correctness:** [TODO: Assess correctness]" >> "$AUDIT_REPORT_FILE"
    echo "- **Runnable:** [TODO: Assess runnability - Yes/No]" >> "$AUDIT_REPORT_FILE"
    echo "    - *Test Command (if applicable):* \`[TODO: Add command]\`" >> "$AUDIT_REPORT_FILE"
    echo "    - *Observations:* \`[TODO: Add observations]\`" >> "$AUDIT_REPORT_FILE"
    echo "" >> "$AUDIT_REPORT_FILE"
}

# Add sections for each test case
add_test_case_to_report "CLI Calculator" "cli-calculator" "Write a CLI calculator app"
add_test_case_to_report "Weather API Script" "weather-api-script" "Write a Python script to fetch and display the current weather for a given city using an online API."
add_test_case_to_report "Static Web Server" "static-web-server" "Write a simple web server in Python that serves static files from a 'public' directory."
add_test_case_to_report "GUI Calculator (Streamlit)" "gui-calculator-streamlit" "Write a GUI calculator app with a Streamlit interface"
add_test_case_to_report "Sagemath Automorphism Group" "sagemath-automorphism-group" "Write a Sagemath script that computes the automorphism group Aut(G) of an arbitrary group G, as a permutation group."

echo "---" >> "$AUDIT_REPORT_FILE"
echo "" >> "$AUDIT_REPORT_FILE"
echo "## Overall Summary" >> "$AUDIT_REPORT_FILE"
echo "" >> "$AUDIT_REPORT_FILE"
echo "[TODO: Add overall summary of the quality and areas for improvement after reviewing all test cases.]" >> "$AUDIT_REPORT_FILE"
echo "" >> "$AUDIT_REPORT_FILE"

echo ">>> Audit report framework generated at $AUDIT_REPORT_FILE <<<"
echo ">>> Please manually fill in the TODO sections after reviewing artifacts. <<<"

# Make the script executable
chmod +x run_live_audit.sh
