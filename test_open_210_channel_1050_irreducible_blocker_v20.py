#!/usr/bin/env python3
"""Tests for OPEN_210_CHANNEL_1050 irreducible blocker."""

from __future__ import annotations

import unittest

import open_210_channel_1050_irreducible_blocker_v20 as mod


class Open210Channel1050BlockerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flags"]["open_210_channel_1050_blocker_ready"])
        self.assertFalse(self.report["flags"]["open_210_channel_1050_filled"])
        self.assertFalse(self.report["flags"]["cg_1050_invented"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])

    def test_residual_not_unique(self):
        slot = self.report["inventory_slot"]
        self.assertEqual(slot["id"], "OPEN_210_CHANNEL_1050")
        self.assertEqual(slot["status"], "OPEN_AWAITING_YOUNG_CG")
        self.assertGreater(
            self.report["representation_theory"]["residual_dim_sum"], 1050
        )


if __name__ == "__main__":
    unittest.main()
