#!/usr/bin/env python3
import unittest

import selected_vacuum_dim7_low_complexity_phase_screen_v20 as mod


class SelectedVacuumDim7LowComplexityScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertIn(
            self.report["status"],
            {
                "DIM7_LOW_COMPLEXITY_NONZERO_PHASE_CHANNEL_FOUND__STATIONARITY_OPEN",
                "DIM7_LOW_COMPLEXITY_SCREEN_ZERO__FIVE_HIGH_COMPLEXITY_REPS_OPEN",
            },
        )

    def test_enumeration_counts(self):
        enumeration = self.report["enumeration"]
        self.assertEqual(enumeration["dimension7_charge_allowed_monomials"], 98)
        self.assertEqual(enumeration["dimension7_tensor_signatures"], 98)
        self.assertEqual(enumeration["new_tensor_signatures_beyond_dim6"], 68)
        self.assertEqual(enumeration["new_odd_H_signatures"], 42)
        self.assertEqual(enumeration["new_even_H_signatures"], 26)
        self.assertEqual(enumeration["new_even_H_conjugacy_representatives"], 13)
        self.assertEqual(len(enumeration["low_complexity_representatives"]), 8)
        self.assertEqual(len(enumeration["high_complexity_representatives"]), 5)
        self.assertEqual(enumeration["graph_limit"], 300)

    def test_screen_counts_and_consistency(self):
        screen = self.report["screen"]
        self.assertEqual(len(screen["representatives_evaluated"]), 8)
        self.assertEqual(screen["total_metric_graphs"], 1128)
        self.assertEqual(screen["total_graph_coefficient_evaluations"], 5835)
        self.assertGreaterEqual(screen["maximum_abs_coefficient"], 0.0)
        self.assertEqual(
            screen["n_nonzero_representatives"],
            len(screen["nonzero_representatives"]),
        )
        self.assertEqual(
            self.report["flags"]["nonzero_dimension7_phase_channel_found"],
            bool(screen["nonzero_representatives"]),
        )

    def test_nonzero_channels_have_correct_phase_rank(self):
        for row in self.report["screen"]["nonzero_representatives"]:
            self.assertTrue(row["nonzero_selected_vacuum_channel"], row)
            self.assertGreater(row["maximum_abs_coefficient"], mod.TOL)
            for record in row["phase_rank_records"]:
                self.assertEqual(record["rank_with_kappa"], 2, record)
                self.assertTrue(record["null_is_PQ_1_1_minus2"], record)

    def test_scientific_boundary(self):
        flags = self.report["flags"]
        self.assertTrue(flags["dimension7_low_complexity_screen_complete"])
        self.assertFalse(flags["stationarity_rebuilt_with_dimension7_operator"])
        self.assertFalse(flags["selected_vacuum_fully_stabilized"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])
        if flags["nonzero_dimension7_phase_channel_found"]:
            self.assertTrue(
                flags["selected_vacuum_phase_lift_exists_in_screened_dim7_sector"]
            )
            self.assertFalse(
                flags["five_high_complexity_dimension7_representatives_open"]
            )
        else:
            self.assertFalse(
                flags["selected_vacuum_phase_lift_exists_in_screened_dim7_sector"]
            )
            self.assertTrue(
                flags["five_high_complexity_dimension7_representatives_open"]
            )


if __name__ == "__main__":
    unittest.main()
