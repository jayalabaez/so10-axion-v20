#!/usr/bin/env python3
from __future__ import annotations

import unittest

import next_gen_g1_g6_progress_gate_v20 as gate


class NextGenG1G6ProgressGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = gate.build_report()

    def test_gate_executes(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "PARTIAL")
        self.assertEqual(self.report["n_closed_subproblems"], 26)
        self.assertTrue(all(self.report["closed_subproblems"].values()))

    def test_top_level_gates_remain_honest(self) -> None:
        states = self.report["gate_states"]
        self.assertEqual(states["G1"], "OPEN")
        self.assertEqual(states["G2"], "PARTIAL")
        self.assertEqual(states["G6"], "PARTIAL")
        self.assertEqual(states["G7"], "OPEN")
        self.assertEqual(states["G8"], "PARTIAL")

    def test_authoritative_structure(self) -> None:
        structure = self.report["authoritative_triplet_structure"]
        self.assertEqual(
            structure["quadratic_object"],
            "5x5 Hermitian Nambu mass-squared matrix",
        )
        self.assertEqual(
            structure["B_T10_T10bar"],
            "kappa10 <S> + 2 lambda10_hol (H0·H0)^*",
        )
        channel54 = structure["exact_Hermitian_54"]
        self.assertEqual(
            channel54["T10_and_T10bar_shift"],
            "lambda_PhiH_54 q_color",
        )
        self.assertEqual(channel54["Q54_126bardag126bar"], 0.0)
        self.assertEqual(channel54["PhiSigma_Hermitian_54_parameter"], "absent")
        self.assertEqual(channel54["HSigma_Hermitian_54_parameter"], "absent")
        channel45 = structure["exact_Hermitian_45"]
        self.assertEqual(channel45["T10_shift"], "+lambda_PhiH_45 k_color")
        self.assertEqual(channel45["T10bar_shift"], "-lambda_PhiH_45 k_color")
        self.assertEqual(channel45["t2_shift"], "+lambda_PhiSigma_45 k_color")
        self.assertEqual(channel45["t2bar_shift"], "-lambda_PhiSigma_45 k_color")
        self.assertEqual(channel45["t4bar_shift"], "-lambda_PhiSigma_45 k_color")
        self.assertEqual(structure["PhiH_Hermitian_channels"], ["1", "45", "54"])
        self.assertTrue(structure["PhiH_Hermitian_family_complete"])
        self.assertFalse(
            structure["legacy_symmetric_dimension_one_4x4_authoritative"]
        )

    def test_remaining_blockers_and_claim_scope(self) -> None:
        self.assertGreaterEqual(self.report["n_remaining_blockers"], 10)
        flags = self.report["flag"]
        self.assertTrue(flags["authoritative_next_gen_G1_G6_progress_gate"])
        self.assertTrue(flags["all_recorded_exact_subproblems_closed"])
        self.assertTrue(flags["shared_Hermitian_54_channel_closed"])
        self.assertTrue(flags["shared_Hermitian_45_channel_closed"])
        self.assertTrue(flags["PhiH_Hermitian_channel_family_complete"])
        self.assertFalse(flags["G1_closed"])
        self.assertFalse(flags["G6_closed"])
        self.assertFalse(flags["physical_triplet_spectrum_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])
        self.assertFalse(flags["empirical_discovery"])


if __name__ == "__main__":
    unittest.main()
