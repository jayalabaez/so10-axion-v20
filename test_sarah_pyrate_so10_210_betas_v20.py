#!/usr/bin/env python3
"""Tests for SARAH/PyR@TE-formula SO(10)+210 two-loop β ingest."""

from __future__ import annotations

import unittest

import sarah_pyrate_so10_210_betas_v20 as mod


class SarahPyrateBetasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "SARAH_PYRATE_FORMULA_SO10_210_BETAS_INGESTED__QUARTIC_AND_UV_CP_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["sarah_validated_210_betas"])
        self.assertTrue(flags["pyrate_sarah_mv_formulas_ingested"])
        self.assertTrue(flags["published_so10_dynkin_ledger"])
        self.assertTrue(flags["ad_hoc_1p1_fudge_replaced"])
        self.assertTrue(flags["two_loop_so10_gauge_complete_for_content"])
        self.assertTrue(flags["two_loop_landau_or_breakdown_above_MGUT"])
        self.assertFalse(flags["live_sarah_or_pyrate_executable_run"])
        self.assertFalse(flags["two_loop_quartic_betas_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_dynkin_and_betas(self):
        self.assertEqual(mod.T_SO10["210"], 56.0)
        self.assertAlmostEqual(mod.c2_of("16"), 45.0, places=10)
        b = self.report["betas"]["below_vPhi"]
        self.assertTrue(abs(b["b1"]) > 0.0)
        self.assertTrue(abs(b["b2_gauge_only"]) > 0.0)
        self.assertTrue(
            abs(self.report["continuous_spin10"]["delta_inv_MPl_vs_fudge"]) > 0.0
            or self.report["continuous_spin10"]["landau_pole_below_MPl_ingested"]
        )
        self.assertGreater(
            self.report["yukawa_two_loop"]["rel_delta_H"], 0.0
        )


if __name__ == "__main__":
    unittest.main()
