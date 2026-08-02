#!/usr/bin/env python3
"""Tests for flavour fit, two-loop thresholds, and 37 GHz haloscope forecast."""

from __future__ import annotations

import unittest

import flavour_clebsch_fit_v20 as flavour
import two_loop_thresholds_v20 as thresholds
import haloscope_scan_37ghz_v20 as halo


class FlavourFitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = flavour.run_fit(seed=20)

    def test_v20_point_exists(self):
        ss = self.report["v20_single_scale_point"]
        self.assertEqual(ss["v_r_GeV"], flavour.VS)
        self.assertIn("chi2", ss)
        self.assertIn("y126_max", ss)

    def test_clebsch_relations_documented(self):
        self.assertIn("H", self.report["clebsch_relations"])
        self.assertIn("F", self.report["clebsch_relations"])

    def test_fit_is_finite_and_improved(self):
        ss = self.report["v20_single_scale_point"]
        self.assertLess(ss["chi2"], 100.0)
        self.assertGreater(ss["observables"]["sum_mnu_eV"], 0.0)
        self.assertLess(ss["observables"]["sum_mnu_eV"], 0.2)
        self.assertTrue(ss["perturbative_4pi"])

    def test_natural_scale_can_beat_or_match_v20(self):
        bo = self.report["best_overall"]
        ss = self.report["v20_single_scale_point"]
        self.assertLess(bo["chi2"], 50.0)
        # Natural scale should not be dramatically worse than v20.
        self.assertLess(bo["chi2"], ss["chi2"] + 5.0)


class ThresholdTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = thresholds.build_report()

    def test_one_loop_regression_anchors(self):
        reg = self.report["regression_anchors"]
        self.assertTrue(reg["MI_one_ok"])
        self.assertTrue(reg["MGUT_one_ok"])
        self.assertTrue(reg["IU_one_ok"])

    def test_continuous_alpha_not_reset_to_40(self):
        inv = self.report["comparison"]["alpha_inv_vPhi_phys_two"]
        self.assertLess(abs(inv - 40.0), 40.0)  # exists
        self.assertGreater(abs(inv - 40.0), 10.0)  # far from the fake reset


class HaloscopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = halo.build_report(seed=20)

    def test_window_covers_benchmark(self):
        lo, hi = self.report["benchmark"]["recommended_scan_GHz"]
        nu = self.report["benchmark"]["nu_central_GHz"]
        self.assertLessEqual(lo, nu)
        self.assertLessEqual(nu, hi)
        self.assertAlmostEqual(nu, 37.116, places=2)

    def test_mock_is_not_claimed_as_discovery_of_nature(self):
        self.assertIn("MOCK DATA ONLY", self.report["mock_scan_with_injected_signal"]["disclaimer"])
        self.assertIn("not a discovery", self.report["verdict"].lower())
        self.assertFalse(self.report.get("physical_detection", False))

    def test_templates_written(self):
        self.assertGreaterEqual(len(self.report["templates"]), 2)


if __name__ == "__main__":
    unittest.main()
