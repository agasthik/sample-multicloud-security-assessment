#!/bin/bash
# This script updates the check lists in the same directory as the script.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASIC_CHECKS_FILE="${SCRIPT_DIR}/aws_basic_checks.txt"
INTERMEDIATE_CHECKS_FILE="${SCRIPT_DIR}/aws_intermediate_checks.txt"
FULL_CHECKS_FILE="${SCRIPT_DIR}/aws_full_checks.txt"

# Fail early with a clear message if prowler is missing.
if ! command -v prowler >/dev/null 2>&1; then
    echo "ERROR: prowler is not installed or not on PATH; install it before running this script." >&2
    exit 1
fi

# Generate into temp files and only replace the committed lists once every
# prowler command has succeeded. This prevents a missing prowler (or any
# mid-run failure) from truncating the committed check lists to empty.
basic_tmp="$(mktemp "${BASIC_CHECKS_FILE}.XXXXXX")"
intermediate_tmp="$(mktemp "${INTERMEDIATE_CHECKS_FILE}.XXXXXX")"
full_tmp="$(mktemp "${FULL_CHECKS_FILE}.XXXXXX")"
trap 'rm -f "$basic_tmp" "$intermediate_tmp" "$full_tmp"' EXIT

prowler --version > "$basic_tmp"
prowler --version > "$intermediate_tmp"
prowler --version > "$full_tmp"

# Get basic checks
prowler aws --list-checks --no-banner -c \
    account_maintain_current_contact_details \
    awslambda_function_using_supported_runtimes \
    cloudtrail_multi_region_enabled \
    config_recorder_all_regions_enabled \
    ec2_securitygroup_allow_ingress_from_internet_to_any_port \
    guardduty_is_enabled \
    iam_password_policy_lowercase \
    iam_password_policy_number \
    iam_password_policy_symbol \
    iam_password_policy_uppercase \
    iam_root_mfa_enabled \
    iam_rotate_access_key_90_days \
    s3_bucket_public_access \
    | sed 's/\x1b\[[0-9;]*m//g' \
    >> "$basic_tmp"

# Get intermediate checks
prowler aws --no-banner --list-checks \
    --severity critical high \
    | sed 's/\x1b\[[0-9;]*m//g' \
    >> "$intermediate_tmp"

# Get full checks
prowler aws --no-banner --list-checks \
    | sed 's/\x1b\[[0-9;]*m//g' \
    >> "$full_tmp"

# All commands succeeded — publish the results.
chmod 644 "$basic_tmp" "$intermediate_tmp" "$full_tmp"
mv "$basic_tmp" "$BASIC_CHECKS_FILE"
mv "$intermediate_tmp" "$INTERMEDIATE_CHECKS_FILE"
mv "$full_tmp" "$FULL_CHECKS_FILE"
