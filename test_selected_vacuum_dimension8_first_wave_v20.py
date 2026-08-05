#!/usr/bin/env python3
"""Structural tests for the dimension-eight first coefficient wave."""
from __future__ import annotations

import unittest

import selected_vacuum_dimension8_first_wave_v20 as mod


class Dimension8FirstWaveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = mod.planning_context()

    def test_census_partition(self):
        self.assertEqual(len(self.context["candidates"]), 166)
        self.assertEqual(len(self.context["new_rows"]), 21)
        self.assertEqual(len(self.context["first_wave"]), 12)
        self.assertEqual(
            [row["signature"] for row in self.context["first_wave"]],
            [spec["signature"] for spec in mod.WAVE_SPECS.values()],
        )

    def test_each_spec_matches_count_only_census(self):
        by_signature = {
            row["signature"]: row for row in self.context["first_wave"]
        }
        for spec in mod.WAVE_SPECS.values():
            row = by_signature[spec["signature"]]
            self.assertEqual(row["graphs"], spec["graphs"])
            self.assertEqual(row["assignments"], spec["assignments"])
            self.assertEqual(row["cost"], spec["cost"])
            self.assertLessEqual(row["cost"], 20000)

    def test_every_first_wave_candidate_has_rank_two_and_PQ_null(self):
        candidate_map = self.context["candidate_map"]
        import selected_vacuum_dim7_low_complexity_phase_screen_v20 as dim7

        for spec in mod.WAVE_SPECS.values():
            rows = candidate_map[spec["signature"]]
            self.assertGreaterEqual(len(rows), 1)
            for row in rows:
                record = dim7.phase_rank_record(row["phase_vector_D_H_S"])
                self.assertEqual(record["rank_with_kappa"], 2)
                self.assertTrue(record["null_is_PQ_1_1_minus2"])


if __name__ == "__main__":
    unittest.main()
