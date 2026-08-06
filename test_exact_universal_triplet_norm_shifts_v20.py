#!/usr/bin/env python3
from __future__ import annotations

import unittest

import numpy as np

import exact_universal_triplet_norm_shifts_v20 as exact


class ExactUniversalTripletNormShiftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = exact.build_report()

    def test_gate_closes_universal_subproblem(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "CLOSED_SUBPROBLEM")

    def test_phi_norm_is_sum_of_moduli(self) -> None:
        p = 0.9 + 0.1j
        a = -0.4 + 0.2j
        omega = 0.7 - 0.3j
        expected = abs(p) ** 2 + abs(a) ** 2 + abs(omega) ** 2
        self.assertAlmostEqual(exact.phi_norm_squared(p, a, omega), expected, places=12)

    def test_universal_shift_formulas(self) -> None:
        shifts = exact.universal_shifts(
            m10_sq=1.0,
            m126_sq=2.0,
            lambda10=0.5,
            lambda126=0.25,
            lambda10_126=0.1,
            lambda210_10=0.2,
            lambda210_126=0.3,
            lambdaS_10=0.4,
            lambdaS_126=0.5,
            lambdaX_10=0.6,
            lambdaX_126=0.7,
            h_norm_sq=0.8,
            sigma_norm_sq=0.9,
            p=1.0,
            a=2.0,
            omega=3.0,
            s_abs_sq=1.1,
            phi17_abs_sq=1.2,
        )
        n_phi = 14.0
        expected10 = 1.0 + 2 * 0.5 * 0.8 + 0.1 * 0.9 + 0.2 * n_phi + 0.4 * 1.1 + 0.6 * 1.2
        expected126 = 2.0 + 2 * 0.25 * 0.9 + 0.1 * 0.8 + 0.3 * n_phi + 0.5 * 1.1 + 0.7 * 1.2
        self.assertAlmostEqual(shifts["n_phi"], n_phi, places=12)
        self.assertAlmostEqual(shifts["d10_universal_m2"], expected10, places=12)
        self.assertAlmostEqual(shifts["d126_universal_m2"], expected126, places=12)

    def test_identity_blocks_share_two_baselines(self) -> None:
        blocks = exact.universal_identity_blocks(3.0, 5.0)
        self.assertTrue(np.allclose(blocks["A_u"], np.diag([3.0, 5.0])))
        self.assertTrue(np.allclose(blocks["A_v"], np.diag([3.0, 5.0, 5.0])))

    def test_derivative_and_normalization_checks(self) -> None:
        benchmark = self.report["benchmark"]
        self.assertLess(benchmark["finite_difference_H_residual"], 5e-8)
        self.assertLess(benchmark["finite_difference_Sigma_residual"], 5e-8)
        self.assertLess(benchmark["Sigma_rotation_residual"], 1e-12)
        norms = self.report["exact_norm_results"]["canonical_state_norm_residuals"]
        self.assertLess(norms["H"], 1e-12)
        self.assertLess(norms["Sigma"], 1e-12)

    def test_scope_remains_fail_closed(self) -> None:
        flags = self.report["flag"]
        self.assertTrue(flags["exact_universal_norm_shifts_derived"])
        self.assertTrue(
            flags["five_diagonal_placeholders_reducible_to_two_baselines_plus_residuals"]
        )
        self.assertFalse(flags["anisotropic_component_CG_complete"])
        self.assertFalse(flags["complete_component_potential"])
        self.assertFalse(flags["physical_triplet_spectrum_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
