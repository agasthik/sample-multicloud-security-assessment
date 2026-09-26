#!/usr/bin/env python3
"""Update the pinned Prowler version in every provider template."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


PYPI_JSON_URL = "https://pypi.org/pypi/prowler/json"
STABLE_VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
DEFAULT_LINE_PATTERN = re.compile(
    r'^(?P<indent>    )Default: "(?P<version>[^"]+)"(?P<newline>\r?\n)?$'
)
TEMPLATE_PATHS = (
    Path("aws/2-codebuild-prowler-aws.yaml"),
    Path("azure/codebuild-prowler-azure.yaml"),
    Path("gcp/codebuild-prowler-gcp.yaml"),
    Path("oci/codebuild-prowler-oci.yaml"),
)


class ProwlerVersionUpdateError(RuntimeError):
    """Raised when the release metadata or a template is not as expected."""


def validate_stable_version(version: object) -> str:
    """Return a supported stable version string or raise a useful error."""
    if not isinstance(version, str) or not STABLE_VERSION_PATTERN.fullmatch(version):
        raise ProwlerVersionUpdateError(
            f"PyPI returned unsupported Prowler version {version!r}; "
            "expected a stable X.Y.Z release"
        )
    return version


def fetch_latest_version(url: str = PYPI_JSON_URL) -> str:
    """Read the latest Prowler release from PyPI's JSON API."""
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "sample-multicloud-security-assessment-version-check/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as error:
        raise ProwlerVersionUpdateError(
            f"Unable to read Prowler release metadata from PyPI: {error}"
        ) from error

    try:
        version = payload["info"]["version"]
    except (KeyError, TypeError) as error:
        raise ProwlerVersionUpdateError(
            "PyPI response did not contain info.version"
        ) from error
    return validate_stable_version(version)


def update_template(path: Path, new_version: str) -> str:
    """Update one ProwlerVersion parameter and return its previous value."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    except OSError as error:
        raise ProwlerVersionUpdateError(f"Unable to read {path}: {error}") from error

    parameter_headers = [
        index for index, line in enumerate(lines) if line.rstrip() == "  ProwlerVersion:"
    ]
    if len(parameter_headers) != 1:
        raise ProwlerVersionUpdateError(
            f"Expected one ProwlerVersion parameter in {path}, "
            f"found {len(parameter_headers)}"
        )

    default_indexes: list[int] = []
    header_index = parameter_headers[0]
    for index in range(header_index + 1, len(lines)):
        line = lines[index]
        if line.startswith("  ") and not line.startswith("    "):
            break
        if DEFAULT_LINE_PATTERN.fullmatch(line):
            default_indexes.append(index)

    if len(default_indexes) != 1:
        raise ProwlerVersionUpdateError(
            f"Expected one quoted Default in {path}'s ProwlerVersion parameter, "
            f"found {len(default_indexes)}"
        )

    default_index = default_indexes[0]
    match = DEFAULT_LINE_PATTERN.fullmatch(lines[default_index])
    if match is None:  # Defensive: the index was selected with the same pattern.
        raise ProwlerVersionUpdateError(f"Unable to parse ProwlerVersion in {path}")

    old_version = match.group("version")
    newline = match.group("newline") or ""
    lines[default_index] = f'    Default: "{new_version}"{newline}'

    if old_version != new_version:
        try:
            path.write_text("".join(lines), encoding="utf-8")
        except OSError as error:
            raise ProwlerVersionUpdateError(f"Unable to write {path}: {error}") from error
    return old_version


def update_templates(repo_root: Path, new_version: str) -> list[tuple[Path, str]]:
    """Update all known provider templates."""
    validate_stable_version(new_version)
    updates: list[tuple[Path, str]] = []
    for relative_path in TEMPLATE_PATHS:
        old_version = update_template(repo_root / relative_path, new_version)
        updates.append((relative_path, old_version))
    return updates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--version",
        help="Use an explicit stable X.Y.Z version instead of querying PyPI",
    )
    mode.add_argument(
        "--print-latest",
        action="store_true",
        help="Print the latest stable PyPI version without changing files",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help=argparse.SUPPRESS,
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        version = (
            validate_stable_version(args.version)
            if args.version
            else fetch_latest_version()
        )
        if args.print_latest:
            print(version)
            return 0

        updates = update_templates(args.repo_root.resolve(), version)
    except ProwlerVersionUpdateError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    changed = False
    for path, old_version in updates:
        if old_version == version:
            print(f"{path}: already at {version}")
        else:
            changed = True
            print(f"{path}: {old_version} -> {version}")
    if not changed:
        source = "requested" if args.version else "latest"
        print(f"All provider templates already use the {source} Prowler release.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
