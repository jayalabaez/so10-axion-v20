#!/usr/bin/env python3
"""Tests for multi-operator phase Hessian with gauge quotient."""

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
            "MULTI_OPERATOR_PHASE_HESSIAN_REVALIDATED__GAUGE_QUOTIENT_PHYSICAL_CLOSURE",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["multi_operator_phase_hessian"])
        self.assertTrue(flags["selected_vacuum_lock_and_lam4_null"])
        self.assertTrue(flags["selected_vacuum_phase_rank_one"])
        self.assertTrue(flags["prequotient_second_null_is_gauge_Goldstone"])
        self.assertTrue(flags["physical_phase_closed_after_gauge_quotient"])
        self.assertFalse(flags["extra_physical_nonaxion_flat_phase"])
        self.assertFalse(flags["full_component_phase_space"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_locking_only_null(self):
        h = self.by_name["locking_only"]["multi_operator_hessian"]
        amp = self.by_name["locking_only"]["amplitudes"]
        self.assertEqual(amp["A_lock"], 0.0)
        self.assertEqual(amp["A_lam4"], 0.0)
        self.assertEqual(h["n_positive"], 0)
        self.assertEqual(h["n_zero"], 3)

    def test_kappa_prequotient_and_physical(self):
        point = self.by_name["finite_kappa_benchmark"]
        h = point["multi_operator_hessian"]
        phys = point["physical_after_gauge_quotient"]
        self.assertEqual(h["n_positive"], 1)
        self.assertEqual(h["n_zero"], 2)
        self.assertEqual(
            point["prequotient_classification"]["second_null_if_kappa_active"],
            "eaten_Zprime_BL_R_gauge_Goldstone",
        )
        self.assertEqual(phys["rank"], 1)
        self.assertEqual(phys["nullity"], 1)
        self.assertEqual(phys["physical_null_vector_integer"], [1, -2])
        self.assertFalse(phys["extra_nonaxion_flat_phase"])

    def test_lam4_does_not_add_rank(self):
        self.assertEqual(
            self.report["charge_vectors"]["g_lock"],
            [2.0 * x for x in self.report["charge_vectors"]["g_lam4"]],
        )
        point = self.by_name["kappa_and_lam4_on"]
        self.assertEqual(point["amplitudes"]["A_lam4"], 0.0)
        self.assertEqual(point["physical_after_gauge_quotient"]["rank"], 1)
        self.assertEqual(point["physical_after_gauge_quotient"]["nullity"], 1)

    def test_radial_phase_cross_zero(self):
        for p in self.report["points"]:
            rp = p["multi_operator_hessian"]["radial_phase_cross"]
            self.assertTrue(rp["flag"]["radial_phase_cross_zero_at_minimum"])
            self.assertEqual(p["multi_operator_hessian"]["n_negative"], 0)


if __name__ == "__main__":
    unittest.main()
