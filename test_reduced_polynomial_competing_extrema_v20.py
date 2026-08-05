#!/usr/bin/env python3
"""Tests for reduced polynomial competing-extrema census."""

from __future__ import annotations

import unittest

import reduced_polynomial_competing_extrema_v20 as mod


class ReducedPolynomialCompetingExtremaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flags"]["reduced_competing_extrema_censused"])
        self.assertTrue(self.report["flags"]["selected_survival_locally_stable"])
        self.assertTrue(self.report["flags"]["historical_lam4_excluded_as_tachyonic"])
        self.assertFalse(self.report["flags"]["full_invariant_ring_extrema"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])

    def test_census_contents(self):
        self.assertGreaterEqual(len(self.report["census"]), 8)
        self.assertIn("selected_hEW174_lam4_0", self.report["pd_lam4_0_points"])
        self.assertIn(
            "selected_hEW174_historical_lam4", self.report["tachyonic_points"]
        )
        self.assertIn("ranking_note", self.report)


if __name__ == "__main__":
    unittest.main()
