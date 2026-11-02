"""Retired or stale build files must not survive into a release wheel."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("release_checks", ROOT / "tools/check_release.py")
checks = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checks)


class ReleaseArtifactTests(unittest.TestCase):
    def wheel(self, files):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "labtune-fixture.whl"
        with zipfile.ZipFile(path, "w") as archive:
            for name, content in {"LICENSE": "fixture", "LICENSING.md": "fixture", **files}.items():
                archive.writestr(name, content)
        return path

    def test_retired_module_in_a_reused_build_directory_is_rejected(self):
        path = self.wheel({"labtune/_retired_adapter.py": "raise RuntimeError('retired')"})
        self.assertIn("labtune/_retired_adapter.py: not in current package source", checks.check_artifact(path))

    def test_unexpected_package_namespace_is_rejected_after_a_rename(self):
        path = self.wheel({"outdated_namespace/__init__.py": "# Stale package from an earlier build"})
        self.assertIn("outdated_namespace/__init__.py: not in current package source", checks.check_artifact(path))

    def test_stale_module_bytes_are_rejected_and_current_source_passes(self):
        name = "labtune/__init__.py"
        current = (ROOT / "src" / name).read_bytes()
        stale = self.wheel({name: current + b"\n# stale build content\n"})
        self.assertIn(name + ": differs from current package source", checks.check_artifact(stale))
        self.assertEqual(checks.check_artifact(self.wheel({name: current})), [])
