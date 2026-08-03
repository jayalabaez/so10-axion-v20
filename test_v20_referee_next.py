#!/usr/bin/env python3
"""Tests for referee next-step packages."""

from __future__ import annotations

import unittest

import heavy_light_spectrum_v20 as spectrum
import p8_spin10_reconstruction_v20 as p8
import wilson_rg_evolution_v20 as wilson
import thermal_string_v20 as thermal


class SpectrumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = spectrum.build_report(seed=20)

    def test_three_light_families(self):
        self.assertEqual(
            self.report["x1_block_with_extra_portals"]["n_light_chiral_families"], 3
        )
        self.assertTrue(self.report["light_family_count_stable"])

    def test_all_components_decay(self):
        self.assertTrue(self.report["all_components_decay_before_1s_at_1e-8"])
        self.assertIsNotNone(self.report["max_portal_floor_for_1s"])
        self.assertLess(self.report["max_portal_floor_for_1s"], 1e-15)


class P8ReconstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = p8.build_report()

    def test_group_and_charge(self):
        self.assertTrue(self.report["spin10_group_factors"]["group_ok"])
        self.assertTrue(self.report["topology"]["charge_ok"])
        self.assertNotEqual(self.report["lorentz"]["one_loop_lorentz_factor"], 0)

    def test_matches_engine_kernel(self):
        self.assertLess(
            self.report["compared_to_engine_benchmark"]["relative_difference"], 1e-8
        )


class WilsonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = wilson.build_report()

    def test_mild_wilson_safe(self):
        mild = self.report["operator_running"]["NDA_O1_at_MPl_mild_shrink"]
        self.assertTrue(mild["quality"]["safe_below_1e-10"])

    def test_large_wilson_can_threaten(self):
        # Either unsafe or documented as a UV constraint; must remain finite.
        large = self.report["operator_running"]["large_Wilson_1e6_at_MPl"]
        self.assertIn("safe_below_1e-10", large["quality"])
        self.assertGreater(abs(large["C8_eff_schematic"]), 0.0)


class ThermalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = thermal.build_report()

    def test_gmu_small(self):
        self.assertLess(self.report["string_network"]["G_mu"], 1e-12)

    def test_benchmark_reheating_pattern(self):
        low = self.report["restoration_benchmarks"]["T_RH_1e10"]
        self.assertFalse(low["restores_U1X_Phi"])
        self.assertFalse(low["restores_S_vev"] and low["T_RH_GeV"] < 1e8)


if __name__ == "__main__":
    unittest.main()
