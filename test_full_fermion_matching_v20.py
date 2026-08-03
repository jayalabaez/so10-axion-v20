#!/usr/bin/env python3
"""Tests for full_fermion_matching_v20."""

from __future__ import annotations

import math
import unittest

import fermion_couplings_150uev_v20 as ferm
import full_fermion_matching_v20 as full


class FullFermionMatchingTests(unittest.TestCase):
    def test_unmixed_limit_recovers_ert(self):
        out = full.match_under_ansatz(lambda_q=1e-12, y_q=1.0)
        base = ferm.ert_leading_extrapolation(
            full.TAN_BETA_V20, acknowledge_not_full_matching=True
        )
        self.assertAlmostEqual(out["matched"]["C_e"] / base["C_e"], 1.0, places=8)
        self.assertAlmostEqual(out["matched"]["C_p"] / base["C_p"], 1.0, places=6)
        self.assertAlmostEqual(out["matched"]["C_n"], base["C_n"], places=8)

    def test_three_light_families(self):
        q = full.q_sector_light_pq_charges(lambda_q=1.0, y_q=1.0)
        self.assertEqual(q["n_light"], 3)
        self.assertEqual(q["rank"], 1)

    def test_o1_portal_shift_tiny(self):
        out = full.match_under_ansatz(lambda_q=1.0, y_q=1.0)
        self.assertLess(out["q_sector"]["max_abs_PQ_shift_from_1"], 1e-8)
        self.assertLess(abs(out["delta"]["C_p"]), 1e-8)

    def test_report_unique_under_ansatz(self):
        report = full.build_report()
        self.assertTrue(report["unique_under_ansatz"])
        self.assertTrue(report["bound_checks"]["full_model_pass_under_stated_ansatz"])
        self.assertIsNone(report["bound_checks"]["full_model_pass_without_ansatz"])
        p = report["primary_v20_tanbeta_1p5"]
        self.assertTrue(math.isfinite(p["C_e"]))
        self.assertTrue(math.isfinite(p["C_p"]))
        self.assertTrue(math.isfinite(p["C_n"]))

    def test_scan_monotonic_ish(self):
        scan = full.portal_ratio_scan()
        shifts = [r["max_abs_PQ_shift"] for r in scan["scan"]]
        self.assertLess(shifts[0], shifts[-1])


if __name__ == "__main__":
    unittest.main()
