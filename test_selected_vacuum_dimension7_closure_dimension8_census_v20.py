#!/usr/bin/env python3
"""Tests for the consolidated dimension-seven no-go and dimension-eight census."""
from __future__ import annotations

import unittest

import selected_vacuum_dimension7_complete_no_go_v20 as dim7
import selected_vacuum_dimension8_phase_census_v20 as dim8


class Dimension7ClosureDimension8CensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d7 = dim7.build_report()
        cls.d8 = dim8.build_report()

    def test_dimension7_complete_no_go(self):
        report = self.d7
        self.assertEqual(report["n_failed"], 0, report)
        self.assertEqual(
            report["status"],
            "SELECTED_VACUUM_PHASE_LIFTING_NO_GO_THROUGH_DIMENSION7",
        )
        self.assertEqual(
            report["counts"]["dimension7_even_H_conjugacy_representatives"],
            13,
        )
        self.assertEqual(report["counts"]["dimension7_total_metric_graphs"], 33389)
        self.assertEqual(
            report["counts"]["dimension7_total_graph_coefficient_evaluations"],
            62948,
        )
        self.assertEqual(
            report["counts"]["dimension7_maximum_abs_coefficient"], 0.0
        )
        self.assertTrue(
            report["flags"][
                "full_selected_vacuum_phase_lifting_no_go_through_dimension7"
            ]
        )
        self.assertFalse(report["flags"]["dimension8_and_above_excluded"])
        self.assertFalse(report["flags"]["whole_model_excluded"])

    def test_dimension8_census_is_structural_only(self):
        report = self.d8
        self.assertEqual(report["n_failed"], 0, report)
        self.assertEqual(
            report["status"],
            "DIMENSION8_PHASE_CENSUS_COMPLETE__COEFFICIENT_SCREEN_OPEN",
        )
        self.assertTrue(
            report["flags"]["dimension8_charge_tensor_census_complete"]
        )
        self.assertFalse(report["flags"]["dimension8_coefficients_evaluated"])
        self.assertFalse(report["flags"]["dimension8_phase_lifting_no_go_proven"])
        self.assertFalse(report["flags"]["whole_model_excluded"])
        self.assertGreater(
            report["counts"]["dimension8_charge_allowed_phase_sensitive_monomials"],
            0,
        )
        self.assertGreater(
            report["counts"]["dimension8_even_H_conjugacy_representatives"],
            0,
        )

    def test_count_only_recurrence_matches_hosted_dimension7_counts(self):
        self.assertEqual(
            self.d8["calibration"]["dim7_signature_4_0_2_0_0"], 4691
        )
        self.assertEqual(
            self.d8["calibration"]["dim7_signature_0_2_4_0_0"], 12043
        )
        self.assertEqual(
            self.d8["calibration"]["dim7_signature_3_0_2_2_0"], 3387
        )

    def test_ranked_costs_are_monotone(self):
        rows = self.d8["ranked_even_H_representatives"]
        costs = [row["planned_graph_coefficient_evaluations"] for row in rows]
        self.assertEqual(costs, sorted(costs))
        self.assertTrue(all(cost > 0 for cost in costs))


if __name__ == "__main__":
    unittest.main()
