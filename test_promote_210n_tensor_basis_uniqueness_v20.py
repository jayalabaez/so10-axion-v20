#!/usr/bin/env python3
"""Tests for promoting uniqueness to the full pure-210ⁿ tensor basis."""

from __future__ import annotations

import unittest

import promote_210n_tensor_basis_uniqueness_v20 as mod


class Promote210nTensorBasisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "UNIQUE_FROM_FULL_PURE_210N_TENSOR_BASIS__MIXED_REP_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["unique_from_full_pure_210n_tensor_basis"])
        self.assertTrue(flags["unique_from_full_210n_tensor_basis"])
        self.assertTrue(flags["hilbert_restriction_kernel_used"])
        self.assertTrue(flags["schematic_quartic_projected_to_H4"])
        self.assertFalse(flags["mixed_rep_full_hilbert_series"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_projection_and_selection(self):
        proj = self.report["quartic_projection"]
        self.assertTrue(proj["spans_full_H4"])
        self.assertEqual(proj["lstsq_rank"], 4)
        self.assertLess(proj["relative_noninvariant_residual"], 1.0)
        fr = self.report["selected_hilbert"]["fractions"]
        self.assertAlmostEqual(
            fr["a_over_MGUT"] + fr["omega_over_MGUT"] + fr["p_over_MGUT"],
            1.0,
            places=8,
        )
        self.assertTrue(all(v > 0.0 for v in fr.values()))

    def test_helper_projection(self):
        eta = {
            "a4": 0.05,
            "w4": 0.05,
            "p4": 0.05,
            "a2w2": 0.04,
            "a2p2": 0.03,
            "w2p2": 0.04,
        }
        out = mod.project_schematic_quartic_onto_hilbert(eta=eta)
        self.assertEqual(len(out["coeffs_vector"]), 4)
        self.assertTrue(out["spans_full_H4"])
        self.assertEqual(
            list(out["hilbert_quartic_coeffs"]), ["J0", "J2", "J3", "J4"]
        )

    def test_schematic_cubic_projects_onto_the_unique_invariant(self):
        proj = self.report["cubic_projection"]
        self.assertEqual(proj["hilbert_H3"], 1)
        self.assertNotEqual(proj["I3_coefficient"], 0.0)
        # The withdrawn cubic pair is mostly not SO(10)-invariant.
        self.assertGreater(proj["relative_noninvariant_residual"], 0.5)
        self.assertTrue(self.report["flag"]["schematic_cubic_projected_to_unique_I3"])
        self.assertTrue(self.report["flag"]["legacy_two_cubic_basis_withdrawn"])
        pot = mod.hilbert_complete_potential(
            a=0.3, omega=1.2, p=-0.7, lam1=0.1, lam2=0.1,
            quartic_coeffs=[0.0, 0.0, 0.0, 0.0],
        )
        expected = proj["I3_coefficient"] * mod.hilbert.ps_forms_degree3(0.3, 1.2, -0.7)[0]
        self.assertAlmostEqual(pot["V3"], expected, places=12)


if __name__ == "__main__":
    unittest.main()
