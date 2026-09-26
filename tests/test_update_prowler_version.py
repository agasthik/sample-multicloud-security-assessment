import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import update_prowler_version


class FakeResponse:
    def __init__(self, payload: object) -> None:
        self.payload = payload

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self, *_args: object, **_kwargs: object) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class UpdateProwlerVersionTests(unittest.TestCase):
    def test_fetch_latest_version_reads_pypi_metadata(self) -> None:
        response = FakeResponse({"info": {"version": "5.43.0"}})
        with mock.patch("urllib.request.urlopen", return_value=response):
            self.assertEqual(update_prowler_version.fetch_latest_version(), "5.43.0")

    def test_fetch_latest_version_rejects_prerelease(self) -> None:
        response = FakeResponse({"info": {"version": "6.0.0rc1"}})
        with mock.patch("urllib.request.urlopen", return_value=response):
            with self.assertRaises(
                update_prowler_version.ProwlerVersionUpdateError
            ):
                update_prowler_version.fetch_latest_version()

    def test_update_templates_changes_only_prowler_defaults(self) -> None:
        template = """AWSTemplateFormatVersion: 2010-09-09
Parameters:
  ProwlerVersion:
    Description: Prowler release
    Type: String
    Default: "5.39.1"
  AnotherParameter:
    Type: String
    Default: "5.39.1"
Resources: {}
"""
        with tempfile.TemporaryDirectory() as directory:
            repo_root = Path(directory)
            for relative_path in update_prowler_version.TEMPLATE_PATHS:
                path = repo_root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(template, encoding="utf-8")

            updates = update_prowler_version.update_templates(repo_root, "5.43.0")

            self.assertEqual(len(updates), 4)
            for relative_path, old_version in updates:
                self.assertEqual(old_version, "5.39.1")
                contents = (repo_root / relative_path).read_text(encoding="utf-8")
                self.assertIn('    Default: "5.43.0"', contents)
                self.assertEqual(contents.count('    Default: "5.39.1"'), 1)

    def test_update_template_fails_when_parameter_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "template.yaml"
            path.write_text("Parameters: {}\n", encoding="utf-8")
            with self.assertRaises(
                update_prowler_version.ProwlerVersionUpdateError
            ):
                update_prowler_version.update_template(path, "5.43.0")


if __name__ == "__main__":
    unittest.main()
