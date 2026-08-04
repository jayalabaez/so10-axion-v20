#!/usr/bin/env python3
"""Tests for exact X/Y masses from the component vacuum."""

from __future__ import annotations

import math
import unittest

import exact_xy_masses_component_vacuum_v20 as mod


class ExactXYMassesComponentVacuumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "EXACT_XY_MASSES_FROM_COMPONENT_VACUUM__VEV_RATIOS_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["exact_XY_mass_from_component_vacuum"])
        self.assertTrue(flags["published_susyno_fonseca_formulas"])
        self.assertTrue(flags["proton_decay_uses_min_UV"])
        self.assertTrue(flags["replaced_g_MGUT_proxy"])
        self.assertFalse(flags["unique_vev_ratios_from_full_potential"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_masses_and_lifetime(self):
        m = self.report["masses"]
        self.assertGreater(m["M_U_GeV"], 0.0)
        self.assertGreater(m["M_V_GeV"], 0.0)
        self.assertTrue(self.report["literature_check_126_only"]["V_massless"])
        p = self.report["proxy_comparison"]
        self.assertGreater(abs(p["ratio_exact_over_proxy"] - 1.0), 1e-6)
        g = self.report["gauge_lifetime"]
        self.assertGreater(g["exact_mediator"]["tau_e_years"], 0.0)
        self.assertTrue(math.isfinite(g["delta_rel_tau_exact_vs_proxy"]))
        # Stack VEV split may fail SK; must not become whole-model exclusion
        self.assertFalse(self.report["flag"]["whole_model_excluded"])
        self.assertIn(
            "selected_point_passes_SK", self.report["flag"]
        )

    def test_helper_126_only_V_zero(self):
        out = mod.gauge_masses_from_vevs(
            a=0.0, omega=0.0, p=0.0, v126=1.0e12, g=0.7
        )
        self.assertAlmostEqual(out["M_V_GeV"], 0.0, places=6)
        self.assertGreater(out["M_U_GeV"], 0.0)


if __name__ == "__main__":
    unittest.main()
