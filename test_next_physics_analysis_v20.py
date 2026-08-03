#!/usr/bin/env python3
"""Smoke tests for next_physics_analysis_v20."""

from __future__ import annotations

import math
import unittest

import next_physics_analysis_v20 as nxt


class NextPhysicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.astro = nxt.astrophysics_ledger()
        cls.pq = nxt.pq_history_scenarios()
        cls.reach = nxt.experiment_reach_triage()
        cls.bbn = nxt.bbn_lifetime_grid()
        cls.qual = nxt.quality_boundary()

    def test_astro_not_excluded(self):
        self.assertFalse(self.astro["currently_excluded_by_listed_bounds"])
        self.assertLess(self.astro["v20"]["g_agamma_GeV_inv"] / 5.8e-11, 1e-2)

    def test_misalignment_theta(self):
        th = self.pq["scenarios"]["pre_inflationary_PQ"]["theta_i_for_all_DM"]
        self.assertAlmostEqual(th, 2.91, places=1)

    def test_gmu_below_pta_ballpark(self):
        gmu = self.pq["scenarios"]["post_inflationary_v20_13_m3"]["G_mu"]
        self.assertLess(gmu, 1e-10)

    def test_priority_experiments(self):
        self.assertEqual(self.reach["recommended_contact_list"][0], "MADMAX (full)")
        self.assertIn("ORGAN", self.reach["recommended_contact_list"])

    def test_bbn_floor_positive(self):
        self.assertIsNotNone(self.bbn["portal_floor_tau_lt_1s"])
        self.assertGreater(self.bbn["portal_floor_tau_lt_1s"], 0.0)

    def test_quality_o1_safe(self):
        self.assertTrue(self.qual["O1_mild_grow_safe"])
        self.assertGreater(self.qual["max_abs_Ceff_for_quality_1e-10"], 1e30)

    def test_omega_formula_monotonic(self):
        self.assertLess(nxt.omega_a(nxt.FA, 0.5), nxt.omega_a(nxt.FA, 2.0))
        self.assertTrue(math.isfinite(nxt.omega_a(nxt.FA, 1.0)))


if __name__ == "__main__":
    unittest.main()
