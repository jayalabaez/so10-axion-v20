#!/usr/bin/env python3
"""Tests for X/Y flavour rotations in gauge proton-decay amplitudes."""

from __future__ import annotations

import unittest

import xy_flavour_rotations_gauge_v20 as mod


class XYFlavourRotationsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "XY_FLAVOUR_ROTATIONS_FROM_CKM_PMNS__UV_UNIQUENESS_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["xy_flavour_rotations_from_ckm_pmns"])
        self.assertTrue(flags["legacy_vud_limit_reproduced"])
        self.assertTrue(flags["multi_channel_flavour_factors"])
        self.assertFalse(flags["unique_flavour_rotations_for_XY"])
        self.assertFalse(flags["uv_yukawa_textures_unique"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_e_channel_matches_legacy(self):
        life = self.report["lifetimes"]
        self.assertAlmostEqual(life["ratio_e_to_legacy"], 1.0, places=2)
        self.assertTrue(life["passes_SK_e_pi0"])

    def test_mu_differs_from_e(self):
        ch = self.report["pdg_flavour"]["channels"]
        self.assertNotAlmostEqual(
            ch["p_to_e_pi0"]["flavour_factor"],
            ch["p_to_mu_pi0"]["flavour_factor"],
            places=4,
        )

    def test_flavour_factor_builder(self):
        factors = mod.flavour_factors_xy(ckm=mod.PDG_CKM, pmns=mod.NUFIT_PMNS)
        f_e = factors["channels"]["p_to_e_pi0"]["flavour_factor"]
        legacy = 1.0 + (1.0 + 0.9737**2) ** 2
        self.assertAlmostEqual(f_e / legacy, 1.0, places=3)


if __name__ == "__main__":
    unittest.main()
