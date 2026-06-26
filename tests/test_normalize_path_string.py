from __future__ import annotations

import sys
import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pypathdub import normalizePathString, normalize_path_string  # noqa: E402


class NormalizePathStringTests(unittest.TestCase):
    def test_package_guard_rejects_unsupported_python(self) -> None:
        spec = spec_from_file_location("pypathdub_py36_guard_probe", ROOT / "src" / "pypathdub" / "__init__.py")
        assert spec is not None
        assert spec.loader is not None
        module = module_from_spec(spec)
        with mock.patch.object(sys, "version_info", (3, 6, 0)):
            with self.assertRaisesRegex(RuntimeError, "requires Python 3.7\\+"):
                spec.loader.exec_module(module)

    def test_windows_drive_projects_to_wsl(self) -> None:
        self.assertEqual(
            "/mnt/c/work/project/data.local",
            normalizePathString(r"C:\work\project\data.local", "python-wsl"),
        )

    def test_windows_drive_projects_to_lowercase_mingw_drive(self) -> None:
        self.assertEqual(
            "/c/work/project/data.local",
            normalizePathString(r"C:\work\project\data.local", "python-mingw"),
        )

    def test_mingw_drive_projects_to_python_win(self) -> None:
        self.assertEqual(
            "c:/work/project/data.local",
            normalizePathString("/c/work/project/data.local", "python-win"),
        )

    def test_wsl_drive_projects_to_osnative_win(self) -> None:
        self.assertEqual(
            r"c:\work\project\data.local",
            normalizePathString("/mnt/c/work/project/data.local", "osnative-win"),
        )

    def test_wsl_drive_projects_to_python_winabsolute(self) -> None:
        self.assertEqual(
            "c:/work/project/data.local",
            normalizePathString("/mnt/c/work/project/data.local", "python-winabsolute"),
        )

    def test_unc_share_projects_to_python_nix_authority(self) -> None:
        self.assertEqual(
            "//192.168.1.2/digitalmedia",
            normalizePathString(r"\\192.168.1.2\digitalmedia", "python-nix"),
        )

    def test_unc_nested_path_projects_to_python_nix_authority(self) -> None:
        self.assertEqual(
            "//192.168.1.2/digitalmedia/movies",
            normalizePathString(r"\\192.168.1.2\digitalmedia\movies", "python-nix"),
        )

    def test_relative_path_cannot_project_to_winabsolute(self) -> None:
        with self.assertRaises(ValueError):
            normalizePathString(r"work\project\data.local", "python-winabsolute")

    def test_plain_posix_path_cannot_project_to_winabsolute(self) -> None:
        with self.assertRaises(ValueError):
            normalizePathString("/work/project/data.local", "python-winabsolute")

    def test_windows_drive_cannot_project_to_nix(self) -> None:
        with self.assertRaises(ValueError):
            normalizePathString(r"C:\work\project\data.local", "python-nix")

    def test_python_style_alias(self) -> None:
        self.assertEqual(
            "/c/work/project/data.local",
            normalize_path_string(r"C:\work\project\data.local", "python-mingw"),
        )


if __name__ == "__main__":
    unittest.main()
