#!/usr/bin/env python3
"""Tests for SO(10) (210⊗210)→54 four-form projector."""

from __future__ import annotations

import unittest

import so10_210_to_54_projector_v20 as mod


class So10210To54Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flags"]["so10_210_to_54_projector_ready"])
        self.assertFalse(self.report["flags"]["cg_120_320_1050_4125_invented"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])

    def test_algebra_and_vacuum_seed(self):
        self.assertTrue(self.report["checks"]["swap_identity"])
        self.assertTrue(self.report["checks"]["P54_image_traceless"])
        self.assertTrue(self.report["checks"]["selected_vacuum_Q54_nontrivial"])
        seed = self.report["selected_vacuum"]["OPEN_210_CHANNEL_54_seed_GeV2"]
        self.assertGreater(seed, 0.0)

    def test_inventory_partial(self):
        slot = self.report["inventory_slot"]
        self.assertEqual(slot["id"], "OPEN_210_CHANNEL_54")
        self.assertEqual(slot["status"], "PARTIAL_PS_SINGLET_TENSOR_MAP_READY")
        self.assertFalse(slot["off_singlet_fluctuation_cg"])


if __name__ == "__main__":
    unittest.main()
