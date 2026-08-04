#!/usr/bin/env python3
"""Tests for cal G soft-mode classification."""

from __future__ import annotations

import unittest

import cal_g_soft_mode_classification_v20 as mod


class CalGSoftModeClassificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "CAL_G_SOFT_MODE_CLASSIFIED__TAU_P_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["cal_G_soft_mode_classified"])
        self.assertTrue(flags["cal_G_gamma_independent"])
        self.assertTrue(flags["goldstone_compatible_slice_null5"])
        self.assertEqual(flags["primary_label"], "residual_flat_or_light_singlet")
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_slices(self):
        gflat = self.report["slices"]["hilbert_goldstone_compatible_M"]
        hilb = self.report["slices"]["hilbert_generic_M"]
        self.assertTrue(gflat["chiral_5x5_null"]["ok"])
        self.assertGreater(gflat["spectrum_6x6"]["lightest_GeV"], 0.0)
        self.assertGreater(hilb["spectrum_6x6"]["lightest_GeV"], 0.0)
        self.assertTrue(gflat["classification"]["gamma_independent"])

    def test_primary(self):
        prim = self.report["primary_classification"]
        self.assertEqual(prim["label"], "residual_flat_or_light_singlet")
        self.assertTrue(prim["soft_vs_null_tol"])
        self.assertTrue(prim["residual_flat_candidate"])
        self.assertFalse(prim["goldstone_like"])


if __name__ == "__main__":
    unittest.main()
