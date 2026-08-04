#!/usr/bin/env python3
"""Tests for fermion tower in Coleman–Weinberg."""

from __future__ import annotations

import unittest

import fermion_tower_cw_v20 as mod


class FermionTowerCWTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "FERMION_TOWER_IN_CW__G_SINGLET_AND_SARAH_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["fermion_tower_complete"])
        self.assertTrue(flags["matter_16_tower_in_cw"])
        self.assertTrue(flags["rhn_type_I_in_cw"])
        self.assertTrue(flags["heavy_decay_safe_16_in_cw"])
        self.assertTrue(flags["soft_gaugino_conditional"])
        self.assertTrue(flags["fermion_proxy_replaced"])
        self.assertTrue(flags["one_loop_stability_conditional"])
        self.assertFalse(flags["exact_soft_gaugino_masses_from_uv"])
        self.assertFalse(flags["g_singlet_6x6_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_ledger_counts_and_delta(self):
        led = self.report["ledger"]
        # 3 RHN + 3 heavy16 + 5 massive-gauge gaugino bundles
        self.assertEqual(led["n_entries"], 3 + 3 + 5)
        self.assertEqual(led["n_soft_gaugino_majoranas"], 33)
        self.assertGreater(led["heavy16_mass_GeV"], 0.0)
        self.assertTrue(
            abs(self.report["fermion_cw"]["V1_tower_GeV4"]) > 0.0
        )
        self.assertGreater(
            self.report["combined"]["abs_delta_over_abs_prev"], 0.0
        )


if __name__ == "__main__":
    unittest.main()
