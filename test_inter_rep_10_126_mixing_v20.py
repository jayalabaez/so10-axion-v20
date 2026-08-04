#!/usr/bin/env python3
"""Tests for inter-representation 10–126 colour-triplet mixing."""

from __future__ import annotations

import math
import unittest

import inter_rep_10_126_mixing_v20 as mod
import numpy as np


class InterRep10126MixingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "INTER_REP_10_126_MIXING_DERIVED__UNIQUE_SPECTRUM_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["inter_rep_mixing_angles_derived"])
        self.assertTrue(flags["uv_selected_kappa_lam4_used"])
        self.assertTrue(flags["soft_diagonals_from_stationarity_M12"])
        self.assertFalse(flags["unique_full_triplet_spectrum"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_mixing_content(self):
        mix = self.report["mt_and_mixing"]["mixing"]
        self.assertTrue(math.isfinite(mix["theta_10_126_rad"]))
        self.assertAlmostEqual(
            mix["frac_10_parent"] + mix["frac_126_parent"], 1.0, places=9
        )
        self.assertGreater(mix["lightest_abs_GeV"], 0.0)
        self.assertIn(mix["dominance"], {"10_H", "126bar_H", "mixed"})

    def test_extract_helper(self):
        m = np.diag([1.0, 2.0, 3.0, 4.0])
        out = mod.extract_mixing(m)
        self.assertAlmostEqual(out["lightest_abs_GeV"], 1.0, places=12)
        self.assertAlmostEqual(out["frac_10_parent"], 1.0, places=12)


if __name__ == "__main__":
    unittest.main()
