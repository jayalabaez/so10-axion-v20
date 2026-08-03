#!/usr/bin/env python3
"""Tests for flavour fit, two-loop thresholds, and 37 GHz haloscope forecast."""

from __future__ import annotations

import unittest

import numpy as np

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

    def test_corrected_single_scale_fit_is_finite_but_not_viable(self):
        ss = self.report["v20_single_scale_point"]
        self.assertTrue(ss["chi2"] < float("inf"))
        self.assertGreater(ss["chi2"], 30.0)
        self.assertFalse(ss["single_scale_viable"])
        self.assertGreater(ss["observables"]["sum_mnu_eV"], 0.0)
        self.assertTrue(ss["perturbative_4pi"])
        self.assertTrue(ss["observables"]["takagi_reconstruction"])
        self.assertTrue(ss["observables"]["charged_lepton_basis_included"])

    def test_natural_scale_can_beat_or_match_v20(self):
        bo = self.report["best_overall"]
        ss = self.report["v20_single_scale_point"]
        self.assertLess(bo["chi2"], 50.0)
        # Natural scale should not be dramatically worse than v20.
        self.assertLess(bo["chi2"], ss["chi2"] + 5.0)

    def test_tan_beta_is_not_promoted_to_unique_prediction(self):
        ss = self.report["v20_single_scale_point"]
        self.assertFalse(ss["tan_beta_unique"])
        self.assertFalse(ss["fermion_coupling_numeric_point_unique"])
        self.assertFalse(self.report["tan_beta_status"]["unique_prediction"])
        self.assertFalse(self.report["fit_validity"]["precision_global_fit"])

    def test_takagi_reconstructs_complex_symmetric_matrix(self):
        matrix = np.array(
            [
                [1.0 + 0.2j, 0.3 - 0.1j, -0.2j],
                [0.3 - 0.1j, 2.0 - 0.4j, 0.5 + 0.1j],
                [-0.2j, 0.5 + 0.1j, 0.7 + 0.3j],
            ],
            dtype=complex,
        )
        singular, unitary = flavour.takagi(matrix)
        rebuilt = unitary @ np.diag(singular) @ unitary.T
        self.assertTrue(np.allclose(matrix, rebuilt, rtol=1e-9, atol=1e-12))

    def test_pmns_cp_quadrant_is_recovered_with_atan2(self):
        target_delta = 212.0
        unitary = flavour._rotation(
            np.sqrt(0.308),
            np.sqrt(0.470),
            np.sqrt(0.02215),
            np.radians(target_delta),
        )
        mnu = unitary @ np.diag([0.001e-9, 0.0087e-9, 0.05e-9]) @ unitary.T
        me = np.diag([0.000511, 0.10566, 1.777]).astype(complex)
        obs = flavour._pmns_from_matrices(mnu, me)
        self.assertAlmostEqual(obs["delta_cp_deg"], target_delta, places=8)

    def test_old_high_beta_witness_is_invalidated(self):
        old = np.array(
            [
                1.5204965809107627,
                -3.110498657825023,
                -3.8399334743851044,
                -3.2993019870703604,
                6.023852953107562,
                3.608822982208453,
                4.194843000843401,
                4.00662441306889,
                -15.585375802580941,
                -9.087776517267574,
                -13.209366204805681,
                -0.00019493846115192884,
                -8.762536280151762,
            ]
        )
        corrected_chi2, _ = flavour.chi2_from_params(old, flavour.VS)
        self.assertGreater(corrected_chi2, 1e6)


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
