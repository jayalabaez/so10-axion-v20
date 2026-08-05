#!/usr/bin/env python3
"""Tests for SO(10) (210⊗210)→210 four-form self-map."""

from __future__ import annotations

import unittest

import so10_210_to_210_self_map_v20 as mod


class So10210To210SelfMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flags"]["so10_210_to_210_self_map_ready"])
        self.assertFalse(self.report["flags"]["cg_120_320_1050_4125_invented"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])

    def test_algebra_and_vacuum(self):
        self.assertTrue(self.report["checks"]["swap_symmetric"])
        self.assertTrue(self.report["checks"]["selected_vacuum_self_nontrivial"])
        self.assertTrue(self.report["checks"]["ps_p_self_vanishes"])
        self.assertGreater(
            self.report["selected_vacuum"]["OPEN_210_CHANNEL_210_seed_GeV2"], 0.0
        )
        self.assertGreater(self.report["selected_vacuum"]["overlap_with_phi"], 0.9)


if __name__ == "__main__":
    unittest.main()
