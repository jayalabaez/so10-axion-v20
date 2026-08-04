#!/usr/bin/env python3
"""Tests for multi-operator phase Hessian."""

from __future__ import annotations

import unittest

import multi_operator_phase_hessian_v20 as mod


class MultiOperatorPhaseHessianTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()
        cls.by_name = {p["name"]: p for p in cls.report["points"]}

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "MULTI_OPERATOR_PHASE_HESSIAN_COMPLETE__REDUCED_SECTOR",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["multi_operator_phase_hessian"])
        self.assertTrue(flags["includes_kappa_lam4_locking_cross_terms"])
        self.assertTrue(flags["complete_multi_operator_phase_hessian_reduced_sector"])
        self.assertFalse(flags["full_component_phase_space"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_locking_only_rank1(self):
        h = self.by_name["locking_only"]["multi_operator_hessian"]
        self.assertEqual(h["n_positive"], 1)
        self.assertEqual(h["n_zero"], 2)
        self.assertEqual(h["operator_charge_rank"], 1)

    def test_kappa_lifts_second_mode(self):
        h = self.by_name["finite_kappa_benchmark"]["multi_operator_hessian"]
        self.assertEqual(h["n_positive"], 2)
        self.assertEqual(h["n_zero"], 1)
        self.assertEqual(h["flat_direction"], [1.0, 1.0, -2.0])

    def test_g_lock_parallel_lam4(self):
        self.assertEqual(
            self.report["charge_vectors"]["g_lock"],
            [2.0 * x for x in self.report["charge_vectors"]["g_lam4"]],
        )
        h = self.by_name["kappa_and_lam4_on"]["multi_operator_hessian"]
        self.assertTrue(h["g_lock_parallel_g_lam4"])
        self.assertEqual(h["n_positive"], 2)
        self.assertEqual(h["n_zero"], 1)

    def test_radial_phase_cross_zero(self):
        for p in self.report["points"]:
            rp = p["multi_operator_hessian"]["radial_phase_cross"]
            self.assertTrue(rp["flag"]["radial_phase_cross_zero_at_minimum"])
            self.assertEqual(p["multi_operator_hessian"]["n_negative"], 0)


if __name__ == "__main__":
    unittest.main()
