#!/usr/bin/env python3
"""Update the pinned Prowler version in each CloudFormation template."""

from __future__ import annotations

import re
import sys
from pathlib import Path


TEMPLATES = (
    "aws/2-codebuild-prowler-aws.yaml",
    "azure/codebuild-prowler-azure.yaml",
    "gcp/codebuild-prowler-gcp.yaml",
    "oci/codebuild-prowler-oci.yaml",
)
VERSION_PATTERN = re.compile(
    r'(?m)^(  ProwlerVersion:\n'
    r'    Description: [^\n]+\n'
    r'    Type: String\n'
    r'    Default: )"([0-9]+\.[0-9]+\.[0-9]+)"$'
)


def update_template(path: Path, version: str) -> bool:
    original = path.read_text(encoding="utf-8")
    matches = list(VERSION_PATTERN.finditer(original))
    if len(matches) != 1:
        raise ValueError(
            f"{path}: expected exactly one ProwlerVersion default, found {len(matches)}"
        )

    current_version = matches[0].group(2)
    if current_version == version:
        print(f"{path}: already {version}")
        return False

    updated = VERSION_PATTERN.sub(
        lambda match: f'{match.group(1)}"{version}"',
        original,
        count=1,
    )
    path.write_text(updated, encoding="utf-8")
    print(f"{path}: {current_version} -> {version}")
    return True


def main() -> int:
    if len(sys.argv) != 2 or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", sys.argv[1]):
        print("usage: update-prowler-version.py X.Y.Z", file=sys.stderr)
        return 2

    version = sys.argv[1]
    repository_root = Path(__file__).resolve().parents[2]
    changed_count = 0
    for template in TEMPLATES:
        if update_template(repository_root / template, version):
            changed_count += 1

    print(f"Updated {changed_count} templates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
