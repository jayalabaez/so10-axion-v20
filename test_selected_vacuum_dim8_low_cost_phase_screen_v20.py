#!/usr/bin/env python3
"""Tests for the dimension-eight low-cost selected-vacuum screen."""
from __future__ import annotations

import unittest

import selected_vacuum_dim8_low_cost_phase_screen_v20 as mod


class SelectedVacuumDim8LowCostPhaseScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_enumeration_and_workload(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        enum = self.report["enumeration"]
        self.assertEqual(enum["dimension8_charge_allowed_monomials"], 166)
        self.assertEqual(enum["dimension8_tensor_signatures"], 166)
        self.assertEqual(enum["lower_dimension_signature_union"], 156)
        self.assertEqual(enum["genuinely_new_dimension8_tensor_signatures"], 108)
        self.assertEqual(enum["new_odd_H_signatures"], 66)
        self.assertEqual(enum["new_even_H_signatures"], 42)
        self.assertEqual(enum["new_even_H_conjugacy_representatives"], 21)

    def test_low_cost_wave_exact(self):
        screen = self.report["screen"]
        self.assertEqual(len(screen["representatives_evaluated"]), 6)
        self.assertEqual(screen["total_metric_graphs"], 956)
        self.assertEqual(screen["total_graph_coefficient_evaluations"], 7388)
        self.assertEqual(len(screen["representatives_remaining"]), 15)
        self.assertGreaterEqual(screen["maximum_abs_coefficient"], 0.0)

    def test_any_hit_has_correct_phase_rank(self):
        for row in self.report["screen"]["nonzero_representatives"]:
            for record in row["phase_rank_records"]:
                self.assertEqual(record["rank_with_kappa"], 2)
                self.assertTrue(record["null_is_PQ_1_1_minus2"])

    def test_honest_boundary(self):
        flags = self.report["flags"]
        self.assertTrue(flags["dimension7_no_go_used_as_prerequisite"])
        self.assertTrue(flags["dimension8_low_cost_wave_complete"])
        self.assertFalse(flags["full_selected_vacuum_dimension8_phase_lifting_no_go_proven"])
        self.assertFalse(flags["stationarity_rebuilt"])
        self.assertFalse(flags["full_scalar_hessian_rebuilt"])
        self.assertFalse(flags["selected_vacuum_fully_stabilized"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
