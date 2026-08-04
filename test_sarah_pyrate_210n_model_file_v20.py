#!/usr/bin/env python3
"""Tests for SARAH/PyR@TE 210n model-file scaffold."""

from __future__ import annotations

import unittest

import sarah_pyrate_210n_model_file_v20 as mod


class SarahPyrateModelFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "SARAH_PYRATE_MODEL_FILE_AUTHORED__LIVE_RUN_BLOCKED",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["sarah_pyrate_model_file_authored"])
        self.assertTrue(flags["pyrate_yaml_dynkin_matches_upstream"])
        self.assertTrue(flags["charge_locks_encoded"])
        self.assertTrue(flags["live_run_blocked_without_tools_or_dump"])
        self.assertFalse(flags["live_sarah_or_pyrate_executable_run"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_validation_and_probe(self):
        self.assertTrue(self.report["validation"]["sarah"]["all_structure_ok"])
        self.assertTrue(self.report["validation"]["pyrate"]["dynkin_match_upstream"])
        self.assertTrue(self.report["validation"]["pyrate"]["charges_match_locks"])
        self.assertFalse(self.report["live_probe"]["live_run_executed"])
        self.assertGreater(self.report["files"]["sarah_bytes"], 500)
        self.assertGreater(self.report["files"]["pyrate_bytes"], 500)


if __name__ == "__main__":
    unittest.main()
