#!/usr/bin/env python3
"""Structural tests for the second dimension-eight coefficient wave."""
from __future__ import annotations

import unittest

import selected_vacuum_dimension8_first_wave_v20 as first
import selected_vacuum_dimension8_second_wave_v20 as mod


class Dimension8SecondWaveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = mod.planning_context()

    def test_partition_after_first_wave(self):
        self.assertEqual(len(self.context["new_rows"]), 21)
        self.assertEqual(len(first.WAVE_SPECS), 12)
        self.assertEqual(len(self.context["remaining_after_first"]), 9)
        self.assertEqual(
            [row["signature"] for row in self.context["second_wave"]],
            [spec["signature"] for spec in mod.WAVE_SPECS.values()],
        )

    def test_specs_match_census(self):
        by_signature = {
            row["signature"]: row for row in self.context["second_wave"]
        }
        for spec in mod.WAVE_SPECS.values():
            row = by_signature[spec["signature"]]
            self.assertEqual(row["graphs"], spec["graphs"])
            self.assertEqual(row["assignments"], spec["assignments"])
            self.assertEqual(row["cost"], spec["cost"])
            self.assertGreater(row["cost"], 20000)


if __name__ == "__main__":
    unittest.main()
