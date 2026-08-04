#!/usr/bin/env python3
"""Tests for CG-normalized M_T, locking 54-channel, and dim-4 mix."""

from __future__ import annotations

import math
import unittest

import cg_normalized_mt_locking_mix_v20 as mod


class CGNormalizedMTTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "CG_NORMALIZED_DIAGONAL_MT__LOCKING_54_PROVED__DIM4_MIX_ALLOWED",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["cg_factors_transcribed"])
        self.assertTrue(flags["locking_so10_proved_via_54"])
        self.assertTrue(flags["dim4_210_10_126_S_mix_allowed"])
        self.assertTrue(flags["forbidden_10_126_S_cubic_still_forbidden"])
        self.assertFalse(flags["invented_unpublished_cg_values"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_locking_54(self):
        lock = self.report["locking_54_channel"]
        self.assertEqual(lock["so10_channel"], "54")
        self.assertTrue(lock["flag"]["locking_so10_proved"])

    def test_dim4_charges(self):
        d4 = self.report["dim4_mix_210_10_126_S"]
        self.assertEqual(d4["charge_totals"]["PQ"], 0)
        self.assertTrue(d4["charge_allowed"]["all"])
        self.assertTrue(d4["so10_allowed"])

    def test_cg_sqrt3(self):
        factors = {f["symbol"]: f["value"] for f in self.report["cg_factor_ledger"]}
        self.assertAlmostEqual(factors["sqrt3"], math.sqrt(3.0))

    def test_mix_scenarios_nonzero_m12(self):
        mixed = [
            r
            for r in self.report["scenarios"]
            if r["flag"]["dim4_mix_used"] and abs(r["filled"]["m12_GeV"]) > 0
        ]
        self.assertGreater(len(mixed), 0)


if __name__ == "__main__":
    unittest.main()
