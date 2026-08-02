#!/usr/bin/env python3
"""Tests for the v20 physics-push module."""

from __future__ import annotations

import math
import unittest

import physics_push_v20 as push


class PhysicsPushTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = push.build_report()

    def test_extra_portals_exist(self):
        extras = self.report["extra_portals"]
        self.assertGreater(extras["n_extra_charge_allowed"], 0)
        self.assertIn("P R H", extras["extra_examples"])

    def test_decay_inequality_direction(self):
        heavy = push.VPHI / math.sqrt(2.0)
        massless = push.corrected_decay_width(1e-8, heavy, 0.0)
        suppressed = push.corrected_decay_width(1e-8, heavy, 0.5 * heavy)
        self.assertLess(suppressed["width_GeV"], massless["width_GeV"])
        self.assertEqual(
            massless["inequality"],
            "Gamma <= |lambda|^2 M/(32 pi) for m_final < M",
        )

    def test_continuous_rg_not_weakly_coupled(self):
        rg = self.report["continuous_spin10_rg"]
        self.assertTrue(rg["conservative_complex_210"]["landau_pole_below_MPl"])
        self.assertFalse(rg["physical_real_210"]["weakly_coupled_at_MPl_alpha_lt_0.25"])

    def test_light_family_count_stable(self):
        self.assertEqual(self.report["heavy_light_rank"]["light_chiral_families"], 3)

    def test_seesaw_toy_stays_perturbative(self):
        toy = self.report["seesaw_benchmark_at_v20_scale"]
        self.assertTrue(toy["perturbative_4pi"])
        self.assertLess(toy["y_dirac_max"], 4.0 * math.pi)

    def test_does_not_claim_discovery(self):
        self.assertIn("experimental dark-matter detection", self.report["not_claimed"])
        self.assertIn("candidate model", self.report["bottom_line"])


if __name__ == "__main__":
    unittest.main()
