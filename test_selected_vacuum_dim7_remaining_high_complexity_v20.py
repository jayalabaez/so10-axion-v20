#!/usr/bin/env python3
"""Structural tests for the remaining dimension-seven high-complexity waves."""
from __future__ import annotations

import unittest

import selected_vacuum_dim7_high_complexity_wave1_v20 as wave1
import selected_vacuum_dim7_remaining_high_complexity_v20 as mod


class RemainingHighComplexityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = mod.planning_context()

    def test_wave_specs_are_exact(self):
        self.assertEqual(
            mod.WAVE_SPECS,
            {
                "2a": {
                    "signature": (0, 2, 4, 0, 0),
                    "n_metric_graphs": 12043,
                    "n_neutral_assignments": 1,
                    "evaluation_cost": 12043,
                },
                "2b": {
                    "signature": (3, 0, 2, 2, 0),
                    "n_metric_graphs": 3387,
                    "n_neutral_assignments": 4,
                    "evaluation_cost": 13548,
                },
                "2c": {
                    "signature": (1, 1, 3, 2, 0),
                    "n_metric_graphs": 4897,
                    "n_neutral_assignments": 4,
                    "evaluation_cost": 19588,
                },
            },
        )

    def test_full_high_complexity_partition(self):
        self.assertEqual(len(self.context["representatives"]), 13)
        self.assertEqual(len(self.context["ordered_high"]), 5)
        self.assertEqual(
            self.context["ordered_high"][:2], wave1.EXPECTED_SIGNATURES
        )
        self.assertEqual(
            self.context["remaining"],
            [spec["signature"] for spec in mod.WAVE_SPECS.values()],
        )

    def test_costs_match_graphs_times_neutral_assignments(self):
        for spec in mod.WAVE_SPECS.values():
            signature = spec["signature"]
            self.assertEqual(
                self.context["graph_counts"][signature],
                spec["n_metric_graphs"],
            )
            self.assertEqual(
                self.context["assignment_counts"][signature],
                spec["n_neutral_assignments"],
            )
            self.assertEqual(
                self.context["costs"][signature], spec["evaluation_cost"]
            )

    def test_every_candidate_adds_one_physical_phase_constraint(self):
        candidate_map = self.context["candidate_map"]
        for spec in mod.WAVE_SPECS.values():
            rows = candidate_map[spec["signature"]]
            self.assertGreaterEqual(len(rows), 1)
            for record in mod.phase_rank_records(rows):
                self.assertEqual(record["rank_with_kappa"], 2)
                self.assertTrue(record["null_is_PQ_1_1_minus2"])
                self.assertEqual(record["null_vector"], [1, 1, -2])


if __name__ == "__main__":
    unittest.main()
