#!/usr/bin/env python3
"""Structural tests for the final dimension-eight high-cost wave."""
from __future__ import annotations

import unittest

import selected_vacuum_dimension8_third_wave_v20 as mod


class SelectedVacuumDimension8ThirdWaveTests(unittest.TestCase):
    def test_exact_partition(self):
        context = mod.planning_context()
        expected = [spec["signature"] for spec in mod.WAVE_SPECS.values()]
        self.assertEqual(len(context["new_rows"]), 21)
        self.assertEqual(len(context["remaining_after_second"]), 6)
        self.assertEqual([row["signature"] for row in context["third_wave"]], expected)

    def test_specs_match_planning_costs(self):
        context = mod.planning_context()
        rows = {row["signature"]: row for row in context["third_wave"]}
        for wave, spec in mod.WAVE_SPECS.items():
            with self.subTest(wave=wave):
                row = rows[spec["signature"]]
                self.assertEqual(row["graphs"], spec["graphs"])
                self.assertEqual(row["assignments"], spec["assignments"])
                self.assertEqual(row["cost"], spec["cost"])

    def test_total_final_workload(self):
        self.assertEqual(
            sum(spec["cost"] for spec in mod.WAVE_SPECS.values()),
            2916056,
        )


if __name__ == "__main__":
    unittest.main()
