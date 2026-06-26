from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pypathdub import normalizePathString, normalize_path_string  # noqa: E402


class NormalizePathStringTests(unittest.TestCase):
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

    def test_mingw_drive_projects_to_python_windows(self) -> None:
        self.assertEqual(
            "c:/work/project/data.local",
            normalizePathString("/c/work/project/data.local", "python-windows"),
        )

    def test_wsl_drive_projects_to_osnative_windows(self) -> None:
        self.assertEqual(
            r"c:\work\project\data.local",
            normalizePathString("/mnt/c/work/project/data.local", "osnative-windows"),
        )

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
