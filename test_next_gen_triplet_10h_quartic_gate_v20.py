#!/usr/bin/env python3
from __future__ import annotations

import unittest

import numpy as np

import next_gen_triplet_10h_quartic_gate_v20 as gate
import next_gen_triplet_diagonal_baseline_gate_v20 as diagonal


class NextGenTriplet10HQuarticGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = gate.build_report()

    def test_gate_executes(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "PARTIAL")
        self.assertTrue(self.report["flag"]["authoritative_10h_quartic_subgate"])

    def test_only_B00_changes(self) -> None:
        benchmark = self.report["benchmark"]
        self.assertLess(benchmark["A_u_change_max_abs"], 1e-14)
        self.assertLess(benchmark["A_v_change_max_abs"], 1e-14)
        base = complex(
            benchmark["base_B_GeV2"]["re"], benchmark["base_B_GeV2"]["im"]
        )
        delta = complex(
            benchmark["Delta_B_GeV2"]["re"], benchmark["Delta_B_GeV2"]["im"]
        )
        total = complex(
            benchmark["total_B_GeV2"]["re"], benchmark["total_B_GeV2"]["im"]
        )
        self.assertAlmostEqual(abs(total - base - delta), 0.0, places=13)

    def test_exact_builder_formula(self) -> None:
        norm_parameters = {
            "m10_sq": 4.0,
            "m126_sq": 5.0,
            "lambda10": 0.1,
            "lambda126": 0.12,
            "lambda10_126": 0.03,
            "lambda210_10": 0.04,
            "lambda210_126": 0.05,
            "lambdaS_10": 0.02,
            "lambdaS_126": 0.025,
            "lambdaX_10": 0.01,
            "lambdaX_126": 0.015,
            "h_norm_sq": 0.02,
            "sigma_norm_sq": 0.08,
            "s_abs_sq": 0.04,
            "phi17_abs_sq": 0.09,
        }
        residuals = {key: 0.0 for key in diagonal.RESIDUAL_KEYS}
        blocks = gate.build_with_10h_quartic(
            norm_parameters=norm_parameters,
            anisotropic_residual_m2=residuals,
            p=0.9,
            a=0.4,
            omega=0.7,
            s_expectation=5.0,
            lambda4=0.05,
            mu_eta=0.3,
            kappa10=3.0,
            lambda10_hol=0.25,
            h_background_bilinear=2.0 + 4.0j,
        )
        expected = 15.0 + 2.0 * 0.25 * np.conjugate(2.0 + 4.0j)
        self.assertAlmostEqual(
            abs(blocks["B_holomorphic_GeV2"][0, 0] - expected), 0.0, places=12
        )
        self.assertEqual(
            blocks["exact_10h_holomorphic_quartic"][
                "Hermitian_diagonal_shift_GeV2"
            ],
            0.0,
        )

    def test_positive_benchmark_and_scope(self) -> None:
        benchmark = self.report["benchmark"]
        self.assertGreater(benchmark["minimum_eigenvalue_m2"], 0.0)
        self.assertGreater(min(benchmark["schur_eigenvalues_m2"]), 0.0)
        flags = self.report["flag"]
        self.assertTrue(flags["exact_second_10h_quartic_B_inserted"])
        self.assertTrue(flags["second_10h_quartic_diagonal_shift_zero"])
        self.assertFalse(flags["physical_Q_H0_derived"])
        self.assertFalse(flags["complete_component_potential"])
        self.assertFalse(flags["physical_triplet_spectrum_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])
        self.assertFalse(flags["empirical_discovery"])


if __name__ == "__main__":
    unittest.main()
