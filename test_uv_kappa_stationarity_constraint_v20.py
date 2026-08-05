#!/usr/bin/env python3
"""Tests for UV κ stationarity constraint at hEW=174."""

from __future__ import annotations

import unittest

import uv_kappa_stationarity_constraint_v20 as mod


class UvKappaStationarityConstraintTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flags"]["uv_kappa_stationarity_constrained"])
        self.assertFalse(self.report["flags"]["uv_kappa_uniquely_determined"])
        self.assertTrue(self.report["flags"]["physical_A_kappa_ready"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])

    def test_physical_a_kappa(self):
        self.assertAlmostEqual(self.report["vevs_GeV"]["hEW"], 174.0, places=12)
        a = self.report["A_kappa"]["physical_GeV2"]
        self.assertGreater(a, 0.0)
        self.assertAlmostEqual(
            self.report["A_kappa"]["m2_heavy_cp_odd_GeV2"], 5.0 * a, places=6
        )
        self.assertNotAlmostEqual(
            a, self.report["A_kappa"]["mi_equal_proxy_GeV2"], delta=a * 0.5
        )


if __name__ == "__main__":
    unittest.main()
