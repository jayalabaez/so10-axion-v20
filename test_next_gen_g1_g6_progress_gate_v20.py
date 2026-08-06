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
        self.assertEqual(self.report["n_closed_subproblems"], 17)
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
        self.assertFalse(
            structure["legacy_symmetric_dimension_one_4x4_authoritative"]
        )

    def test_remaining_blockers_and_claim_scope(self) -> None:
        self.assertGreaterEqual(self.report["n_remaining_blockers"], 10)
        flags = self.report["flag"]
        self.assertTrue(flags["authoritative_next_gen_G1_G6_progress_gate"])
        self.assertTrue(flags["all_recorded_exact_subproblems_closed"])
        self.assertFalse(flags["G1_closed"])
        self.assertFalse(flags["G6_closed"])
        self.assertFalse(flags["physical_triplet_spectrum_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])
        self.assertFalse(flags["empirical_discovery"])


if __name__ == "__main__":
    unittest.main()
