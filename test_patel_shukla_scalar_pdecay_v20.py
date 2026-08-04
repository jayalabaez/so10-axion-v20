#!/usr/bin/env python3
"""Tests for Patel–Shukla published scalar proton-decay channel calculator."""

from __future__ import annotations

import unittest

import patel_shukla_scalar_pdecay_v20 as ps


class PatelShuklaChannelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = ps.build_report()

    def test_status_and_open_flags(self):
        self.assertEqual(
            self.report["status"],
            "PATEL_SHUKLA_SCALAR_CHANNELS_COMPUTED__VACUUM_M_T_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["published_patel_shukla_templates_applied"])
        self.assertTrue(flags["pq_theta_T_zero_adopted"])
        self.assertFalse(flags["complete_so10_scalar_potential"])
        self.assertFalse(flags["numeric_triplet_spectrum_derived"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])
        self.assertTrue(flags["conditional_parameter_points_excluded"])

    def test_template_at_reference_point_equals_limit(self):
        tau = ps.predicted_lifetime_years(
            limit_yr=1.6e33, alpha=0.1, mass_GeV=1.4e11, M_ref_GeV=1.4e11
        )
        self.assertAlmostEqual(tau, 1.6e33, places=0)

    def test_required_mass_inverts_template(self):
        m = ps.required_mass_GeV(limit_yr=1.6e33, alpha=0.1, M_ref_GeV=1.4e11)
        self.assertAlmostEqual(m, 1.4e11, delta=1.0)

    def test_MI_alpha_grid_behavior(self):
        scan = self.report["channel_scan"]
        self.assertTrue(scan["flag"]["MI_alpha0p1_10_H_mu_K0_passes"])
        self.assertTrue(scan["flag"]["MI_alpha0p01_10_H_mu_K0_excluded"])
        danger = scan["danger_MI_alpha0p01_10_H_mu_K0"]
        self.assertLess(danger["predicted_lifetime_years"], 1.6e33)

    def test_matrix_still_unfilled(self):
        mapped = self.report["map_onto_triplet_ledger"]
        self.assertTrue(mapped["eigenvalues_still_null"])
        self.assertFalse(mapped["flag"]["numeric_mass_matrix_derived"])

    def test_branching_prefers_kaon_modes(self):
        br = self.report["branching_equal_mass_pct"]["10_H"]
        self.assertEqual(br["p_to_nubar_K_plus"], 83)
        self.assertEqual(br["p_to_e_pi0"], "<1")

    def test_theta_T_pq_structure(self):
        mix = self.report["pq_mixing_structure"]
        self.assertEqual(mix["within_10_H"]["theta_T"], 0.0)
        self.assertFalse(mix["flag"]["inter_rep_mixing_angles_derived"])


if __name__ == "__main__":
    unittest.main()
