#!/usr/bin/env python3
"""Tests for SO(10) Goldstone SM root catalog."""

from __future__ import annotations

import unittest

import so10_goldstone_sm_root_catalog_v20 as mod


class GoldstoneSmRootCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flags"]["goldstone_sm_root_catalog_ready"])
        self.assertFalse(self.report["flags"]["root_by_root_dynamical_hessian_masses"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])

    def test_orbit_and_stabilizer_sectors(self):
        self.assertEqual(self.report["orbit"]["svd_rank_goldstones"], 36)
        self.assertEqual(self.report["orbit"]["stabilizer_dim"], 9)
        self.assertEqual(self.report["orbit"]["ew_extra_goldstones"], 3)
        stab = self.report["subspace_sector_l2_weights"]["stabilizer_9"]
        self.assertAlmostEqual(stab["so6_color"], 8.0, places=6)
        self.assertAlmostEqual(stab["so4_weak"], 1.0, places=6)
        self.assertAlmostEqual(stab["so6_so4_cross"], 0.0, places=6)
        self.assertEqual(len(self.report["planes"]), 45)
        self.assertEqual(len(self.report["stabilizer_mode_summaries"]), 9)


if __name__ == "__main__":
    unittest.main()
