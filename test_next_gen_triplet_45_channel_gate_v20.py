#!/usr/bin/env python3
from __future__ import annotations

import unittest

import next_gen_triplet_45_channel_gate_v20 as gate
import next_gen_triplet_diagonal_baseline_gate_v20 as diagonal


class NextGenTriplet45ChannelGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = gate.build_report()

    def test_gate_executes(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "PARTIAL")
        self.assertTrue(self.report["flag"]["authoritative_exact_45_subgate"])

    def test_exact_builder_sign_pattern(self) -> None:
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
        blocks = gate.build_with_exact_45(
            norm_parameters=norm_parameters,
            anisotropic_residual_m2=residuals,
            p=0.9,
            a=0.4,
            omega=0.7,
            s_expectation=0.2,
            lambda4=0.05,
            mu_eta=0.3,
            kappa10=0.2,
            lambda10_hol=0.17,
            h_background_bilinear=0.11 + 0.03j,
            lambda_phi_h_54=0.07,
            lambda_phi_h_45=0.03,
            lambda_phi_sigma_45=0.02,
        )
        exact = blocks["exact_45_channel"]
        self.assertAlmostEqual(
            exact["Delta_A_T10_GeV2"] + exact["Delta_A_T10bar_GeV2"],
            0.0,
            places=14,
        )
        self.assertAlmostEqual(
            exact["Delta_A_t2_GeV2"] + exact["Delta_A_t2bar_GeV2"],
            0.0,
            places=14,
        )
        self.assertAlmostEqual(
            exact["Delta_A_t2bar_GeV2"], exact["Delta_A_t4bar_GeV2"], places=14
        )

    def test_phi_h_family_complete(self) -> None:
        contract = self.report["authoritative_input_contract"]
        self.assertEqual(contract["PhiH_Hermitian_channels"], ["1", "45", "54"])
        self.assertTrue(contract["PhiH_Hermitian_family_complete"])
        self.assertTrue(self.report["flag"]["PhiH_Hermitian_channel_family_complete"])

    def test_benchmark_positive(self) -> None:
        benchmark = self.report["benchmark"]
        self.assertGreater(benchmark["minimum_eigenvalue_m2"], 0.0)
        self.assertGreater(min(benchmark["schur_eigenvalues_m2"]), 0.0)

    def test_scope_remains_fail_closed(self) -> None:
        flags = self.report["flag"]
        self.assertTrue(flags["exact_PhiH_45_triplet_shifts_inserted"])
        self.assertTrue(flags["exact_PhiSigma_45_triplet_shifts_inserted"])
        self.assertFalse(flags["all_PhiSigma_anisotropic_channels_complete"])
        self.assertFalse(flags["complete_component_potential"])
        self.assertFalse(flags["physical_triplet_spectrum_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])
        self.assertFalse(flags["empirical_discovery"])


if __name__ == "__main__":
    unittest.main()
