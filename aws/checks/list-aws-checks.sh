#!/bin/bash
# This script updates the check lists in the same directory as the script.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASIC_CHECKS_FILE="${SCRIPT_DIR}/aws_basic_checks.txt"
INTERMEDIATE_CHECKS_FILE="${SCRIPT_DIR}/aws_intermediate_checks.txt"
FULL_CHECKS_FILE="${SCRIPT_DIR}/aws_full_checks.txt"

prowler --version > "$BASIC_CHECKS_FILE"
prowler --version > "$INTERMEDIATE_CHECKS_FILE"
prowler --version > "$FULL_CHECKS_FILE"

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
    >> "$BASIC_CHECKS_FILE"

# Get intermediate checks
prowler aws --no-banner --list-checks \
    --severity critical high \
    | sed 's/\x1b\[[0-9;]*m//g' \
    >> "$INTERMEDIATE_CHECKS_FILE"

# Get full checks
prowler aws --no-banner --list-checks \
    | sed 's/\x1b\[[0-9;]*m//g' \
    >> "$FULL_CHECKS_FILE"
