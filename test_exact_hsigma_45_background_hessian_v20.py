#!/usr/bin/env python3
from __future__ import annotations

import unittest

import numpy as np

import exact_hsigma_45_background_hessian_v20 as exact


class ExactHSigma45BackgroundHessianTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = exact.build_report()

    def test_gate_executes(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "CLOSED_SUBPROBLEM")

    def test_background_quantum_numbers(self) -> None:
        background = self.report["background"]
        self.assertAlmostEqual(background["H_u0_quantum_numbers"]["Q"], 0.0, places=12)
        self.assertAlmostEqual(background["H_d0_quantum_numbers"]["Q"], 0.0, places=12)
        self.assertAlmostEqual(background["DeltaR_quantum_numbers"]["Y"], 0.0, places=10)
        self.assertAlmostEqual(
            background["H_u0_quantum_numbers"]["T3R"],
            -background["H_d0_quantum_numbers"]["T3R"],
            places=12,
        )

    def test_phase_resolved_extraction(self) -> None:
        checks = self.report["checks"]
        self.assertTrue(checks["A_blocks_Hermitian"])
        self.assertTrue(checks["opposite_charge_Hermitian_terms_zero"])
        self.assertTrue(checks["same_charge_holomorphic_terms_zero"])
        self.assertTrue(checks["self_holomorphic_terms_zero"])
        self.assertTrue(checks["phase_resolved_reconstruction"])

    def test_color_degeneracy_and_scaling(self) -> None:
        self.assertTrue(self.report["checks"]["three_color_spectra_degenerate"])
        self.assertTrue(self.report["checks"]["vR_squared_scaling"])
        self.assertTrue(self.report["checks"]["quadratic_background_homogeneity"])
        benchmark = self.report["benchmark"]
        self.assertLess(benchmark["reconstruction_residual"], 1e-8)
        self.assertLess(benchmark["color_spectrum_residual"], 1e-8)

    def test_exact_builder_shapes(self) -> None:
        blocks = exact.extract_blocks(
            h_u=0.11,
            h_d=0.04,
            v_r=0.8,
            lambda_hsigma_45=0.2,
            color_index=1,
        )
        self.assertEqual(blocks["A_u_GeV2"].shape, (2, 2))
        self.assertEqual(blocks["A_v_GeV2"].shape, (3, 3))
        self.assertEqual(blocks["B_holomorphic_GeV2"].shape, (2, 3))
        self.assertLess(
            np.max(
                np.abs(
                    blocks["A_u_GeV2"]
                    - blocks["A_u_GeV2"].conj().T
                )
            ),
            1e-10,
        )
        self.assertLess(
            np.max(
                np.abs(
                    blocks["A_v_GeV2"]
                    - blocks["A_v_GeV2"].conj().T
                )
            ),
            1e-10,
        )

    def test_scope_is_fail_closed(self) -> None:
        closed = self.report["newly_closed_subproblem"]
        self.assertTrue(all(closed.values()))
        flags = self.report["flag"]
        self.assertTrue(flags["exact_HSigma_45_background_Hessian"])
        self.assertTrue(flags["exact_HSigma_45_Nambu_projection"])
        self.assertFalse(flags["all_HSigma_invariants_complete"])
        self.assertFalse(flags["complete_component_potential"])
        self.assertFalse(flags["physical_triplet_spectrum_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])
        self.assertFalse(flags["empirical_discovery"])


if __name__ == "__main__":
    unittest.main()
