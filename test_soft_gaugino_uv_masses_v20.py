#!/usr/bin/env python3
"""Tests for soft-gaugino UV mass promotion beyond M_V."""

from __future__ import annotations

import unittest

import soft_gaugino_uv_masses_v20 as mod


class SoftGauginoUVMassesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "SOFT_GAUGINO_UV_MASSES_PROMOTED__QUARTIC_BETAS_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["exact_soft_gaugino_masses_from_uv"])
        self.assertTrue(flags["soft_law_m12_plus_xi_mv"])
        self.assertTrue(flags["m_V_proxy_replaced_by_pure_soft_xi0"])
        self.assertTrue(flags["g6_soft_overlap_resolved"])
        self.assertFalse(flags["unique_soft_scale"])
        self.assertFalse(flags["two_loop_quartic_betas_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_spectra_and_delta(self):
        soft = self.report["soft_scale"]
        self.assertGreater(soft["M_1_2_GeV"], 0.0)
        sp = self.report["spectra"]["xi0_pure_soft"]
        self.assertEqual(sp["n_majoranas"], 32)
        self.assertEqual(sp["n_excluded_g6"], 1)
        self.assertAlmostEqual(sp["mass_GeV"], soft["M_1_2_GeV"], places=6)
        self.assertTrue(
            abs(self.report["cw"]["delta_rel_xi0_vs_proxy"]) > 0.0
        )


if __name__ == "__main__":
    unittest.main()
