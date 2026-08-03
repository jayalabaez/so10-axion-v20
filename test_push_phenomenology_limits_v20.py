#!/usr/bin/env python3
"""Fail-closed tests for the phenomenology-limits push."""

from __future__ import annotations

import unittest

import push_phenomenology_limits_v20 as push


class PhenomenologyLimitsPushTests(unittest.TestCase):
    def test_hierarchical_expansion_is_controlled(self) -> None:
        report = push.hierarchical_w_expansion()
        self.assertLess(report["epsilon"], 1e-3)
        self.assertFalse(report["claims_exact_vanishing"])
        self.assertLess(
            report["frobenius_error_resummed"],
            report["frobenius_error_leading"] + 1e-12,
        )

    def test_portal_envelope_refuses_uniqueness(self) -> None:
        report = push.portal_cf_envelope(n_samples=24, seed=7)
        self.assertTrue(report["flag"]["portal_envelope_constructed"])
        self.assertFalse(report["flag"]["unconditional_unique_Cf"])
        self.assertGreater(report["n_total_rows"], 0)

    def test_fcnc_bounds_applied_without_absence_claim(self) -> None:
        report = push.fcnc_experimental_bound_application()
        self.assertTrue(report["flag"]["experimental_FCNC_bound_applied"])
        self.assertFalse(
            report["flag"]["actual_finite_model_fcnc_absence_proved"]
        )
        self.assertTrue(report["mass_bases"]["uses_U_uL"])

    def test_one_loop_matrix_rge_solves(self) -> None:
        report = push.solve_one_loop_matrix_yukawa_rge()
        self.assertTrue(report["integration"]["success"])
        self.assertTrue(
            report["flag"]["actual_one_loop_matrix_beta_system_solved"]
        )
        self.assertFalse(report["flag"]["two_loop_so10_complete"])
        self.assertFalse(report["flag"]["full_RG_global_fit_minimal"])

    def test_aggregate_push_report(self) -> None:
        report = push.build_report()
        self.assertEqual(report["n_failed"], 0)
        self.assertTrue(report["advances"]["one_loop_matrix_Yukawa_RGE_solved"])
        self.assertFalse(report["advances"]["unconditional_unique_Cf"])
        self.assertFalse(report["advances"]["finite_model_fcnc_absence_proved"])
        self.assertFalse(report["advances"]["two_loop_so10_yukawa_complete"])


if __name__ == "__main__":
    unittest.main()
