#!/usr/bin/env python3
"""Tests for conditional M_T diagonalization + interference envelope."""

from __future__ import annotations

import unittest

import numpy as np

import conditional_mt_interference_v20 as mod


class ConditionalMTInterferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_open_flags(self):
        self.assertEqual(
            self.report["status"],
            "CONDITIONAL_MT_DIAGONALIZED__INTERFERENCE_ENVELOPE_COMPUTED__FULL_TENSORS_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["conditional_spectrum_diagonalized"])
        self.assertTrue(flags["mixing_angles_extracted"])
        self.assertTrue(flags["gauge_scalar_interference_envelope_computed"])
        self.assertFalse(flags["msgut_cal_T_used_as_v20_spectrum"])
        self.assertFalse(flags["complete_so10_scalar_potential"])
        self.assertFalse(flags["numeric_triplet_spectrum_from_full_potential"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])
        self.assertTrue(flags["conditional_parameter_points_excluded"])

    def test_diagonalize_equal_mix(self):
        m = np.array([[3.0, 1.0], [1.0, 3.0]])
        spec = mod.diagonalize_mt(m)
        self.assertAlmostEqual(spec["lightest_GeV"], 2.0, places=10)
        self.assertAlmostEqual(spec["heaviest_GeV"], 4.0, places=10)
        self.assertEqual(spec["dominance_class"], "mixed")

    def test_interference_incoherent_matches_parallel_sum(self):
        tau = mod.interference_lifetime_years(4.0, 4.0, 0.0)
        self.assertAlmostEqual(tau, 2.0, places=12)

    def test_constructive_shorter_than_incoherent(self):
        t_c = mod.interference_lifetime_years(1.0e35, 1.0e35, 1.0)
        t_i = mod.interference_lifetime_years(1.0e35, 1.0e35, 0.0)
        self.assertLess(t_c, t_i)

    def test_some_scenarios_excluded_some_survive(self):
        self.assertGreater(self.report["n_excluded_by_ps_mu_K0"], 0)
        self.assertLess(
            self.report["n_excluded_by_ps_mu_K0"], self.report["n_scenarios"]
        )

    def test_msgut_not_applied(self):
        self.assertFalse(
            self.report["msgut_reference"]["flag"]["msgut_cal_T_used_as_v20_spectrum"]
        )


if __name__ == "__main__":
    unittest.main()
