#!/usr/bin/env python3
"""Tests for CKM/PMNS RG in gauge X/Y widths."""

from __future__ import annotations

import unittest

import ckm_pmns_rg_gauge_width_v20 as mod


class CKMPMNSRGGaugeWidthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "CKM_PMNS_RG_TO_GUT_IN_GAUGE_WIDTH__CP_TENSORS_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["ckm_pmns_rg_to_gut"])
        self.assertTrue(flags["gauge_width_uses_GUT_mixings"])
        self.assertTrue(flags["vud_stable_under_rg"])
        self.assertFalse(flags["full_cp_xy_tensors"])
        self.assertFalse(flags["two_loop_matrix_flavour_rge"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_lifetime_shift_recorded(self):
        life = self.report["lifetimes"]
        self.assertTrue(life["passes_SK_e_pi0_GUT_flavour"])
        self.assertTrue(abs(life["delta_rel_tau_e"]) < 0.05)

    def test_wolfenstein_roundtrip_stable(self):
        w = mod.wolfenstein_from_ckm_abs(
            {
                "V_ud": 0.974,
                "V_us": 0.225,
                "V_ub": 0.0036,
                "V_cd": 0.225,
                "V_cs": 0.973,
                "V_cb": 0.041,
                "V_td": 0.008,
                "V_ts": 0.040,
                "V_tb": 1.0,
            }
        )
        ckm = mod.ckm_abs_from_wolfenstein(w)
        self.assertAlmostEqual(ckm["V_us"], w["lambda"], places=3)
        self.assertGreater(ckm["V_cb"], 0.0)


if __name__ == "__main__":
    unittest.main()
