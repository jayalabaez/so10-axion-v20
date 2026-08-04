#!/usr/bin/env python3
"""Tests for mixed 210–126–10 mass matrices in Coleman–Weinberg."""

from __future__ import annotations

import unittest

import mixed_210_126_10_cw_v20 as mod


class Mixed21012610CWTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "MIXED_210_126_10_MASSES_IN_CW__G_SINGLET_AND_FERMION_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["mixed_210_126_10_in_cw"])
        self.assertTrue(flags["cal_T_and_cal_D_included"])
        self.assertTrue(flags["E_F_J_X_included"])
        self.assertTrue(flags["one_loop_stability_conditional"])
        self.assertFalse(flags["g_singlet_6x6_complete"])
        self.assertFalse(flags["fermion_tower_complete"])
        self.assertFalse(flags["invented_unpublished_cg_values"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_spectra_and_cw_shift(self):
        sp = self.report["spectra"]
        self.assertEqual(sp["n_blocks"], 6)
        self.assertEqual(sp["n_modes_total"], 5 + 4 + 4 + 3 + 4 + 3)
        self.assertGreater(sp["lightest_GeV"], 0.0)
        self.assertGreater(sp["heaviest_GeV"], sp["lightest_GeV"])
        names = {b["name"] for b in sp["blocks"]}
        self.assertEqual(names, {"T", "D", "E", "F", "J", "X"})
        self.assertTrue(abs(self.report["mixed_cw"]["V1_GeV4"]) > 0.0)
        self.assertGreater(
            self.report["combined"]["abs_mixed_over_abs_prev"], 0.0
        )


if __name__ == "__main__":
    unittest.main()
