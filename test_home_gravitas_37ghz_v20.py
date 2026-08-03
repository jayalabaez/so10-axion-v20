#!/usr/bin/env python3
"""Tests for home/public 37 GHz search and GRAVITAS v20 retarget."""

from __future__ import annotations

import math
import unittest

import gravitas_axion_v20_37ghz as grav
import home_public_37ghz_search_v20 as home


class HomePublicTests(unittest.TestCase):
    def test_cmb_dilution_huge(self):
        report = home.build_report()
        for row in report["cmb_mythbust"]["rows"]:
            self.assertGreater(row["dilution_factor"], 1e4)
            self.assertFalse(row["useful_for_v20_DM_line_search"])

    def test_linewidth_order(self):
        self.assertAlmostEqual(home.LINEWIDTH_HZ / 1e3, 37.11, places=0)


class GravitasV20Tests(unittest.TestCase):
    def test_line_centre_near_37(self):
        self.assertAlmostEqual(grav.NU0_HZ / 1e9, 37.11, places=1)

    def test_rv_shift_sign(self):
        nu_pos = grav.line_centre_ghz(100.0)
        nu_neg = grav.line_centre_ghz(-100.0)
        self.assertLess(nu_pos, grav.NU0_HZ / 1e9)
        self.assertGreater(nu_neg, grav.NU0_HZ / 1e9)

    def test_build_report_runs(self):
        report = grav.build_report()
        self.assertEqual(report["status"], "PASS")
        self.assertGreater(report["catalog"]["n_targets_built"], 0)
        self.assertTrue(math.isfinite(report["population_channel"]["single_object_reach_kpc_at_v20_g"]))


if __name__ == "__main__":
    unittest.main()
