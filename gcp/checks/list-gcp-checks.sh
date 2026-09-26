#!/bin/bash
# This script updates the GCP check lists in the same directory as the script.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INTERMEDIATE_CHECKS_FILE="${SCRIPT_DIR}/gcp_intermediate_checks.txt"
FULL_CHECKS_FILE="${SCRIPT_DIR}/gcp_full_checks.txt"

# Fail early with a clear message if prowler is missing.
if ! command -v prowler >/dev/null 2>&1; then
    echo "ERROR: prowler is not installed or not on PATH; install it before running this script." >&2
    exit 1
fi

# Generate into temp files and only replace the committed lists once every
# prowler command has succeeded. This prevents a missing prowler (or any
# mid-run failure) from truncating the committed check lists to empty.
intermediate_tmp="$(mktemp "${INTERMEDIATE_CHECKS_FILE}.XXXXXX")"
full_tmp="$(mktemp "${FULL_CHECKS_FILE}.XXXXXX")"
trap 'rm -f "$intermediate_tmp" "$full_tmp"' EXIT

prowler --version > "$intermediate_tmp"
prowler --version > "$full_tmp"

# Get intermediate checks
prowler gcp --no-banner --list-checks \
    --severity critical high \
    | sed 's/\x1b\[[0-9;]*m//g' \
    >> "$intermediate_tmp"

# Get full checks
prowler gcp --no-banner --list-checks \
    | sed 's/\x1b\[[0-9;]*m//g' \
    >> "$full_tmp"

# All commands succeeded — publish the results.
chmod 644 "$intermediate_tmp" "$full_tmp"
mv "$intermediate_tmp" "$INTERMEDIATE_CHECKS_FILE"
mv "$full_tmp" "$FULL_CHECKS_FILE"
