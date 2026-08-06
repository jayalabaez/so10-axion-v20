#!/usr/bin/env python3
"""Tests for promote-(p,a,ω) free extrema stationarity."""

from __future__ import annotations

import unittest

import promote_paw_free_extrema_stationarity_v20 as mod


class PromotePawFreeExtremaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_soft_anchors_selected(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flags"]["paw_free_extrema_ready"])
        self.assertTrue(self.report["flags"]["soft_anchors_selected_vacuum"])
        self.assertTrue(self.report["flags"]["isotropic_residual_S_Phi17_only"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])
        self.assertAlmostEqual(self.report["fixed"]["H10_EW"], 174.0)


if __name__ == "__main__":
    unittest.main()
