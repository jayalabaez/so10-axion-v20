#!/usr/bin/env python3
import unittest

import selected_vacuum_phase_invariant_dim6_epsilon_reduction_v20 as mod


class SelectedVacuumDim6EpsilonReductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["status"],
            "DIM6_EPSILON_SECTOR_REDUCES_TO_ZERO_METRIC_SECTOR__HEW_DICTIONARY_OPEN",
        )

    def test_hodge_eigenforms(self):
        hodge = self.report["hodge"]
        self.assertLess(hodge["DeltaR_residual"], mod.TOL)
        self.assertLess(hodge["DeltaR_conjugate_residual"], mod.TOL)
        delta = complex(*hodge["DeltaR_eigenvalue"])
        delta_bar = complex(*hodge["DeltaR_conjugate_eigenvalue"])
        self.assertAlmostEqual(delta.real, 0.0, places=12)
        self.assertAlmostEqual(delta_bar.real, 0.0, places=12)
        self.assertAlmostEqual(abs(delta.imag), 1.0, places=12)
        self.assertAlmostEqual(abs(delta_bar.imag), 1.0, places=12)
        self.assertAlmostEqual(abs(delta + delta_bar), 0.0, places=12)

    def test_epsilon_pair_identity(self):
        identity = self.report["epsilon_pair_identity"]
        self.assertTrue(identity["all_match"])
        self.assertTrue(identity["repeated_index_case"]["matches"])
        for case in identity["permutation_cases"]:
            self.assertTrue(case["matches"], case)

    def test_topology_ledger(self):
        ledger = self.report["topology_ledger"]
        self.assertEqual(len(ledger["representatives"]), 15)
        self.assertEqual(ledger["total_one_epsilon_metric_topologies"], 18577)
        self.assertGreater(ledger["total_epsilon_allocations"], 0)
        for row in ledger["representatives"]:
            self.assertTrue(row["contains_five_form"], row)
            self.assertGreater(row["epsilon_metric_topologies"], 0, row)

    def test_scope_is_not_overclaimed(self):
        flags = self.report["flags"]
        self.assertTrue(flags["one_epsilon_topology_ledger_complete"])
        self.assertFalse(flags["epsilon_channels_independent_of_metric_sector"])
        self.assertTrue(flags["epsilon_sector_reduced_to_metric_sector"])
        self.assertFalse(flags["nonzero_selected_epsilon_phase_channel_found"])
        self.assertTrue(
            flags["delta_epsilon_tensor_sector_closed_for_tested_embeddings"]
        )
        self.assertFalse(
            flags["exact_published_hEW_component_dictionary_complete"]
        )
        self.assertFalse(flags["full_selected_vacuum_dimension6_no_go_proven"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
