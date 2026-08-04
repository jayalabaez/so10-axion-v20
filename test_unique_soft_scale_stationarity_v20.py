#!/usr/bin/env python3
"""Tests for unique soft scale from stationarity matching."""

from __future__ import annotations

import math
import unittest

import unique_soft_scale_stationarity_v20 as mod


class UniqueSoftScaleStationarityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "UNIQUE_SOFT_SCALE_FROM_STATIONARITY__TAU_P_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["unique_soft_scale_under_stationarity_matching"])
        self.assertTrue(flags["m12_equals_sqrt_mean_abs_delta_m2"])
        self.assertTrue(flags["replaced_abs_kappa_MI_ansatz"])
        self.assertTrue(flags["universal_soft_matching_at_MI"])
        self.assertFalse(flags["unique_soft_scale_model_independent"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_matched_vs_prior(self):
        matched = self.report["matched_soft_scale"]
        prior = self.report["prior_ansatz"]
        self.assertGreater(matched["M_1_2_GeV"], 0.0)
        self.assertGreater(prior["M_1_2_GeV"], 0.0)
        self.assertNotAlmostEqual(
            matched["M_1_2_GeV"], prior["M_1_2_GeV"], places=3
        )
        sp = self.report["spectra"]["xi0_stationarity_matched"]
        self.assertEqual(sp["n_majoranas"], 32)
        self.assertAlmostEqual(sp["mass_GeV"], matched["M_1_2_GeV"], places=6)
        self.assertTrue(math.isfinite(self.report["cw"]["delta_rel_matched_vs_prior"]))

    def test_helper(self):
        out = mod.soft_scale_from_shifts([4.0, 4.0, 4.0])
        self.assertAlmostEqual(out["M_1_2_GeV"], 2.0, places=12)


if __name__ == "__main__":
    unittest.main()
