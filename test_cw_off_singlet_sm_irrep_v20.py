#!/usr/bin/env python3
"""Tests for CW with off-singlet 210 SM-irrep spectrum."""

from __future__ import annotations

import unittest

import cw_off_singlet_sm_irrep_v20 as mod


class CWOffSingletSmIrrepTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "CW_OFF_SINGLET_SM_IRREP_SPECTRUM_INCLUDED__FERMION_TOWER_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["cw_off_singlet_spectrum_included"])
        self.assertTrue(flags["sm_irrep_dof_counted"])
        self.assertTrue(flags["one_loop_stability_conditional"])
        self.assertFalse(flags["fermion_tower_complete"])
        self.assertFalse(flags["mixed_210_126_10_in_cw"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_off_entries_and_shift(self):
        off = self.report["off_singlet_cw"]
        self.assertEqual(off["n_entries"], 10)
        self.assertGreater(off["n_dof_total"], 0.0)
        self.assertTrue(abs(off["V1_GeV4"]) > 0.0)
        self.assertGreater(
            self.report["combined"]["abs_off_over_abs_baseline_gut"], 0.0
        )


if __name__ == "__main__":
    unittest.main()
