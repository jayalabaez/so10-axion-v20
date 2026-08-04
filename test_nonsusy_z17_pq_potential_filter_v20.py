#!/usr/bin/env python3
"""Tests for the signed non-SUSY Z17/PQ operator filter."""
from __future__ import annotations

import unittest

import nonsusy_z17_pq_potential_filter_v20 as mod


class NonsusyZ17PQFilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()
        cls.ops = {row["name"]: row for row in cls.report["operators"]}

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "NONSUSY_Z17_PQ_OPERATOR_FILTER_COMPLETE__FULL_TENSORS_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        flags = self.report["flag"]
        self.assertTrue(flags["z17_pq_x_filter_applied"])
        self.assertTrue(flags["bare_10_squared_forbidden"])
        self.assertTrue(flags["ten2_S_allowed"])
        self.assertTrue(flags["locking_operator_charge_allowed"])
        self.assertTrue(flags["forbidden_210_10dag10_removed"])
        self.assertTrue(flags["quartic_2102_10dag10_retained"])
        self.assertFalse(flags["invented_unpublished_cg_tensors"])
        self.assertFalse(flags["complete_so10_scalar_potential"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_bare_10_forbidden_ten2_s_allowed(self):
        self.assertFalse(self.ops["bare_10_H^2"]["charge_allowed"]["all"])
        self.assertTrue(self.ops["10_H^2 S"]["charge_allowed"]["all"])
        self.assertEqual(self.ops["10_H^2 S"]["status"], "ALLOWED")

    def test_forbidden_linear_210_higgs_cubic(self):
        cubic = self.ops["210_H 10_H^dag 10_H"]
        quartic = self.ops["210_H^dag 210_H 10_H^dag 10_H"]
        self.assertTrue(cubic["charge_allowed"]["all"])
        self.assertFalse(cubic["so10_invariant_exists"])
        self.assertEqual(cubic["status"], "SO10_FORBIDDEN")
        self.assertNotIn(cubic["name"], self.report["allowed_feeding_M_T"])
        self.assertEqual(quartic["status"], "ALLOWED")

    def test_locking_charges(self):
        lock = self.ops["126bar_H^2 10_H^2 S^2"]
        modulus = self.ops["|126bar_H|^2 |10_H|^2 |S|^2"]
        self.assertTrue(lock["charge_allowed"]["all"])
        self.assertTrue(modulus["charge_allowed"]["all"])
        self.assertEqual(modulus["status"], "ALLOWED")

    def test_phi3_forbidden(self):
        self.assertFalse(self.ops["Phi17^3"]["charge_allowed"]["all"])
        self.assertEqual(self.ops["Phi17^3"]["status"], "CHARGE_FORBIDDEN")

    def test_charge_sum_helper(self):
        total = mod._total_charge({"10_H": 2, "S": 1})
        self.assertEqual(total, {"PQ": 0, "X": 0, "Z17": 0})


if __name__ == "__main__":
    unittest.main()
