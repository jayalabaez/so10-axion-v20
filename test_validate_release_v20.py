#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest

import validate_release_v20 as release


class ValidateReleaseChecksumTests(unittest.TestCase):
    def test_final_theorem_core_paths_are_portable_unique_and_present(self):
        paths = release.FINAL_THEOREM_CORE_PATHS

        self.assertEqual(len(paths), len(set(paths)))
        self.assertNotIn(
            "exact_gauged_u1x_g3_su5_max_negative_sigma35_orbits_v20.py",
            paths,
        )
        self.assertNotIn(
            "exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20.py",
            paths,
        )
        for relative in paths:
            with self.subTest(relative=relative):
                path = Path(relative)
                self.assertFalse(path.is_absolute())
                self.assertEqual(relative, path.as_posix())
                self.assertTrue((release.ROOT / path).is_file())

    def test_checksums_use_sorted_repository_relative_posix_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            readme = root / "README.md"
            model = root / "models" / "SO10Z17AxionV20.m"
            model.parent.mkdir()
            readme.write_bytes(b"release\n")
            model.write_bytes(b"model\n")

            release.write_checksums([model, readme], root=root)

            expected = [
                f"{hashlib.sha256(readme.read_bytes()).hexdigest()}  README.md",
                (
                    f"{hashlib.sha256(model.read_bytes()).hexdigest()}  "
                    "models/SO10Z17AxionV20.m"
                ),
            ]
            lines = (root / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
            self.assertEqual(lines, expected)
            self.assertNotIn("\\", "\n".join(lines))

    def test_checksums_reject_files_outside_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "repository"
            root.mkdir()
            outside = base / "outside.txt"
            outside.write_text("outside\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "outside repository"):
                release.write_checksums([outside], root=root)


if __name__ == "__main__":
    unittest.main()
