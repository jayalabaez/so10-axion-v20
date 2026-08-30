#!/usr/bin/env python3
from __future__ import annotations

import unittest

import next_gen_g1_g6_progress_30_gate_v20 as gate


class NextGenG1G6Progress30GateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = gate.build_report()

    def test_gate_executes(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "OPEN")
        self.assertTrue(self.report["contract_consistent"])
        self.assertEqual(self.report["n_closed_subproblems"], 30)
        self.assertTrue(all(self.report["closed_subproblems"].values()))
        self.assertTrue(
            self.report["flag"]["all_recorded_exact_subproblems_closed"]
        )

    def test_exact_portal_norm_square_structure(self) -> None:
        structure = self.report["authoritative_triplet_structure"]
        portal = structure["exact_portal_norm_square"]
        self.assertEqual(portal["positive_sector_rank"], 1)
        self.assertTrue(portal["positive_semidefinite_for_lambda_C_nonnegative"])
        self.assertIn("x_plus*y", portal["t2bar_t4bar_block"])

    def test_top_level_scope(self) -> None:
        states = self.report["gate_states"]
        self.assertEqual(states["G1"], "CLOSED")
        self.assertEqual(states["G2"], "CLOSED")
        self.assertEqual(states["G6"], "BLOCKED")
        self.assertEqual(states["G7"], "BLOCKED")
        self.assertEqual(states["G8"], "BLOCKED")
        flags = self.report["flag"]
        self.assertTrue(flags["authoritative_next_gen_G1_G6_progress_30_gate"])
        self.assertTrue(flags["exact_quartic_t2bar_t4bar_mixing_inserted"])
        self.assertTrue(flags["exact_X_G1_G2_scoped_subtheorems_complete"])
        self.assertFalse(flags["historical_option_C_authoritative"])
        self.assertTrue(flags["G6_diagnostics_are_scoped_not_gate_closure"])
        self.assertTrue(flags["G1_closed"])
        self.assertFalse(flags["G6_closed"])
        self.assertFalse(flags["physical_triplet_spectrum_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])
        self.assertFalse(flags["empirical_discovery"])


if __name__ == "__main__":
    unittest.main()
