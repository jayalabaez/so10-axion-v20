#!/usr/bin/env python3
"""Tests for the direct portal mass-squared Schur gate."""
from __future__ import annotations

import unittest

import numpy as np

import direct_portal_mass2_schur_gate_v20 as mod


class DirectPortalMass2SchurGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()
        cls.unit_tensor = mod.portal_tensor_aulakh(
            p=0.20, a=0.30, omega=0.50
        )

    def test_report_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["status"],
            "DIRECT_PORTAL_MASS2_SCHUR_GATE_EXECUTED__FULL_DIAGONAL_HESSIAN_OPEN",
        )

    def test_real_hessian_shape_and_symmetry(self):
        hessian = mod.real_hessian_from_holomorphic_portal(
            4.0, 9.0, self.unit_tensor
        )
        self.assertEqual(hessian.shape, (272, 272))
        self.assertLess(
            float(np.max(np.abs(hessian - hessian.T))), 1e-12
        )

    def test_schur_gate_matches_direct_eigenvalues(self):
        positive = mod.real_hessian_from_holomorphic_portal(
            4.0, 9.0, self.unit_tensor
        )
        positive_gate = mod.schur_positivity_report(
            4.0, 9.0, self.unit_tensor
        )
        self.assertTrue(positive_gate["positive_definite"])
        self.assertGreater(float(np.linalg.eigvalsh(positive)[0]), 0.0)

        negative = mod.real_hessian_from_holomorphic_portal(
            1.0, 1.0, self.unit_tensor
        )
        negative_gate = mod.schur_positivity_report(
            1.0, 1.0, self.unit_tensor
        )
        self.assertFalse(negative_gate["positive_definite"])
        self.assertLess(float(np.linalg.eigvalsh(negative)[0]), 0.0)

    def test_isotropic_analytic_spectrum(self):
        singular = np.linalg.svd(self.unit_tensor, compute_uv=False)
        analytic = mod.analytic_isotropic_real_spectrum(
            h_mass2=4.0,
            sigma_mass2=9.0,
            mixing_singular_values=singular,
        )
        numerical = np.linalg.eigvalsh(
            mod.real_hessian_from_holomorphic_portal(
                4.0, 9.0, self.unit_tensor
            )
        )
        self.assertEqual(len(analytic), 272)
        self.assertLess(
            float(
                np.max(
                    np.abs(
                        numerical - np.asarray(analytic, dtype=float)
                    )
                )
            ),
            1e-10,
        )

    def test_exact_rank_loss_surfaces(self):
        triplet = mod.aulakh_branch_singular_values(
            p=1.0, a=1.0, omega=0.2
        )
        self.assertEqual(
            triplet["triplet_minus"]["singular_value_GeV"], 0.0
        )
        doublet_minus = mod.aulakh_branch_singular_values(
            p=0.2, a=1.0, omega=1.0
        )
        self.assertEqual(
            doublet_minus["doublet_minus"]["singular_value_GeV"], 0.0
        )
        doublet_plus = mod.aulakh_branch_singular_values(
            p=0.2, a=1.0, omega=-1.0
        )
        self.assertEqual(
            doublet_plus["doublet_plus"]["singular_value_GeV"], 0.0
        )

    def test_physical_scope_is_not_overclaimed(self):
        flags = self.report["flags"]
        self.assertTrue(flags["direct_portal_mass2_block_constructed"])
        self.assertTrue(flags["exact_schur_positivity_gate_derived"])
        self.assertFalse(
            flags["full_nonsusy_diagonal_component_hessian_supplied"]
        )
        self.assertFalse(flags["full_component_hessian_complete"])
        self.assertFalse(flags["historical_lambda4_full_model_excluded"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
