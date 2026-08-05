#!/usr/bin/env python3
"""Tests for technically natural hierarchy soft matching."""

from __future__ import annotations

import unittest

import technically_natural_hierarchy_soft_matching_v20 as mod


class TechnicallyNaturalHierarchyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(
            self.report["flags"][
                "technically_natural_hierarchy_soft_matching_partial"
            ]
        )
        self.assertFalse(self.report["flags"]["uv_kappa_uniquely_determined"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])

    def test_hierarchy_ratios(self):
        self.assertAlmostEqual(
            self.report["hierarchy_ratios"]["hEW_GeV"], 174.0, places=9
        )
        self.assertLess(self.report["hierarchy_ratios"]["hEW_over_MI"], 1.0)
        self.assertGreater(
            self.report["soft_naturalness"]["max_abs_delta_m2_over_MI2"], 0.0
        )


if __name__ == "__main__":
    unittest.main()
