#!/usr/bin/env python3
from __future__ import annotations

import unittest

import numpy as np

import exact_hsigma_45_closed_formula_v20 as formula


class ExactHSigma45ClosedFormulaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = formula.build_report()

    def test_formula_gate_executes(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "CLOSED_SUBPROBLEM")

    def test_analytic_blocks(self) -> None:
        blocks = formula.analytic_blocks(v_r=2.0, lambda_hsigma_45=0.25)
        np.testing.assert_allclose(
            blocks["A_u_GeV2"], np.diag([-1.0, 0.0]), atol=1e-14
        )
        np.testing.assert_allclose(
            blocks["A_v_GeV2"], np.diag([1.0, 0.0, 0.0]), atol=1e-14
        )
        np.testing.assert_allclose(
            blocks["B_holomorphic_GeV2"], np.zeros((2, 3)), atol=1e-14
        )

    def test_exact_tensor_match_and_h_independence(self) -> None:
        verification = self.report["verification"]
        self.assertLess(verification["maximum_formula_residual"], 1e-10)
        self.assertLess(
            verification["h_background_independence_residual"], 1e-10
        )
        self.assertTrue(
            self.report["checks"][
                "closed_formula_matches_exact_tensor_Hessian"
            ]
        )
        self.assertTrue(
            self.report["checks"]["independent_of_neutral_EW_background"]
        )

    def test_formula_and_scope(self) -> None:
        exact = self.report["exact_triplet_formula"]
        self.assertEqual(
            exact["Delta_A_u"], "diag(-lambda_HSigma45 v_R^2, 0)"
        )
        self.assertEqual(
            exact["Delta_A_v"], "diag(+lambda_HSigma45 v_R^2, 0, 0)"
        )
        self.assertEqual(exact["Delta_B"], "zero 2x3 matrix")
        self.assertEqual(exact["independent_of"], ["h_u", "h_d"])
        flags = self.report["flag"]
        self.assertTrue(flags["exact_HSigma45_closed_formula"])
        self.assertFalse(flags["all_HSigma_invariants_complete"])
        self.assertFalse(flags["complete_component_potential"])
        self.assertFalse(flags["physical_triplet_spectrum_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])
        self.assertFalse(flags["empirical_discovery"])


if __name__ == "__main__":
    unittest.main()
