#!/usr/bin/env python3
"""Tests for component Hessian / competing extrema map."""

from __future__ import annotations

import unittest

import component_hessian_competing_extrema_v20 as mod


class ComponentHessianCompetingExtremaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "COMPONENT_HESSIAN_COMPETING_EXTREMA_MAPPED__OFF_SINGLET_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(
            flags["full_component_hessian_and_competing_extrema_mapped"]
        )
        self.assertTrue(flags["lifted_8_hessian_at_hilbert_vevs"])
        self.assertTrue(flags["competing_extrema_scanned"])
        self.assertTrue(flags["selected_hilbert_slice_locally_stable"])
        self.assertTrue(flags["selected_unique_among_catalogue_soft_mpd"])
        self.assertFalse(flags["full_sm_irrep_mass_matrices"])
        self.assertFalse(flags["live_sarah_or_pyrate_executable_run"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_selected_and_ranking(self):
        sel = self.report["selected"]
        self.assertTrue(sel["hilbert_3x3"]["positive_definite"])
        self.assertGreaterEqual(len(self.report["candidates"]), 5)
        self.assertEqual(self.report["ranking"]["n_competing_lower_cost"], 0)
        self.assertTrue(
            self.report["ranking"]["selected_wins_band_mpd"]
            or self.report["ranking"]["selected_is_best"]
        )
        # Schematic lifted-well PD is a documented conditional residual
        self.assertIn("lifted_well_note", self.report)

    def test_helper_hessian(self):
        coup = mod.hilbert_coeffs_and_couplings()
        h = mod.numerical_hilbert_hessian(
            a=1.0e15,
            omega=1.0e15,
            p=1.0e16,
            lam1=coup["lam1"],
            lam2=coup["lam2"],
            coeffs=coup["coeffs"],
        )
        self.assertEqual(len(h["dimensionless_eigenvalues"]), 3)


if __name__ == "__main__":
    unittest.main()
