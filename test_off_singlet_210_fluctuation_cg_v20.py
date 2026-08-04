#!/usr/bin/env python3
"""Tests for off-singlet 210 fluctuation CG thresholds."""

from __future__ import annotations

import unittest

import off_singlet_210_fluctuation_cg_v20 as mod


class OffSinglet210FluctuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "OFF_SINGLET_210_FLUCTUATION_CG_THRESHOLDS_BUILT__MIXED_126_10_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["off_singlet_fluctuation_cg_thresholds"])
        self.assertTrue(flags["aulakh_table1_unmixed_transcribed"])
        self.assertTrue(flags["mixed_R_octet_diagonalized"])
        self.assertFalse(flags["mixed_210_126_10_complete"])
        self.assertFalse(flags["full_oscillator_basis"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_unmixed_and_R(self):
        self.assertEqual(len(self.report["unmixed_210_thresholds"]), 8)
        self.assertEqual(len(self.report["mixed_R_octet"]["masses_GeV"]), 2)
        self.assertGreater(self.report["summary"]["lightest_GeV"], 0.0)

    def test_R_matrix_symmetric(self):
        mat = self.report["mixed_R_octet"]["matrix"]
        self.assertAlmostEqual(mat[0][1], mat[1][0], places=10)


if __name__ == "__main__":
    unittest.main()
