#!/bin/bash
# This script updates the OCI check lists in the same directory as the script.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INTERMEDIATE_CHECKS_FILE="${SCRIPT_DIR}/oci_intermediate_checks.txt"
FULL_CHECKS_FILE="${SCRIPT_DIR}/oci_full_checks.txt"

prowler --version > "$INTERMEDIATE_CHECKS_FILE"
prowler --version > "$FULL_CHECKS_FILE"

# Get intermediate checks
prowler oraclecloud --no-banner --list-checks \
    --severity critical high \
    | sed 's/\x1b\[[0-9;]*m//g' \
    >> "$INTERMEDIATE_CHECKS_FILE"

# Get full checks
prowler oraclecloud --no-banner --list-checks \
    | sed 's/\x1b\[[0-9;]*m//g' \
    >> "$FULL_CHECKS_FILE"
