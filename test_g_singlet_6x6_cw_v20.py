#!/usr/bin/env python3
"""Tests for G[1,1,0] 6×6 singlet mixing in Coleman–Weinberg."""

from __future__ import annotations

import unittest

import g_singlet_6x6_cw_v20 as mod


class GSinglet6x6CWTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "G_SINGLET_6x6_IN_CW__SARAH_AND_UV_CP_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["g_singlet_6x6_complete"])
        self.assertTrue(flags["cal_G_eq102_transcribed"])
        self.assertTrue(flags["chiral_5x5_null_verified"])
        self.assertTrue(flags["goldstone_compatible_M_slice"])
        self.assertTrue(flags["g6_gaugino_admixture_included"])
        self.assertTrue(flags["one_loop_stability_conditional"])
        self.assertFalse(flags["soft_gaugino_overlap_subtracted"])
        self.assertFalse(flags["sarah_validated_210_betas"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_spectrum_and_cw(self):
        sp = self.report["spectrum"]
        self.assertEqual(sp["n_modes"], 6)
        self.assertGreaterEqual(sp["n_modes_in_cw"], 5)
        self.assertGreater(sp["mass_min_GeV"], 0.0)
        self.assertGreater(min(sp["masses_in_cw_GeV"]), 1.0)
        self.assertGreater(sp["mass_max_GeV"], sp["mass_min_GeV"])
        self.assertGreater(sp["det_abs"], 0.0)
        self.assertTrue(self.report["chiral_5x5_null"]["ok"])
        self.assertTrue(abs(self.report["g_singlet_cw"]["V1_GeV4"]) > 0.0)
        self.assertGreater(
            self.report["combined"]["abs_g_over_abs_prev"], 0.0
        )


if __name__ == "__main__":
    unittest.main()
