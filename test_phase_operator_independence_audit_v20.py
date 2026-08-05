#!/usr/bin/env python3
"""Tests for phase-operator independence with gauge quotient."""

from __future__ import annotations

import unittest

import phase_operator_independence_audit_v20 as mod


class PhaseOperatorIndependenceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["status"],
            "SELECTED_PHASE_HESSIAN_CLOSED_AFTER_NEUTRAL_GAUGE_QUOTIENT",
        )

    def test_formal_rank_and_redundancy(self):
        formal = self.report["formal_operator_algebra"]
        self.assertEqual(formal["rank_kappa_lambda4"], 2)
        self.assertEqual(formal["rank_after_adding_lambda_lock"], 2)
        self.assertEqual(formal["rank_increment_from_lambda_lock"], 0)
        self.assertEqual(formal["common_PQ_null_vector"], [1, 1, -2])

    def test_prequotient_rank_one_two_nulls(self):
        selected = self.report["selected_vacuum_rank"]
        self.assertEqual(selected["active_operators"], ["kappa_H2_S"])
        self.assertEqual(selected["rank"], 1)
        self.assertEqual(selected["null_dimension"], 2)
        self.assertTrue(selected["additional_flat_phase_present_prequotient"])
        self.assertFalse(selected["additional_flat_phase_present"])
        self.assertEqual(
            selected["prequotient_second_null_classification"],
            "eaten_Zprime_BL_R_gauge_Goldstone",
        )

    def test_physical_after_gauge_quotient(self):
        physical = self.report["physical_after_gauge_quotient"]
        self.assertEqual(physical["rank"], 1)
        self.assertEqual(physical["null_dimension"], 1)
        self.assertEqual(physical["physical_null_vector_integer"], [1, -2])
        self.assertFalse(physical["extra_nonaxion_flat_phase"])

    def test_vacuum_claims(self):
        flags = self.report["flags"]
        self.assertTrue(flags["formal_phase_vector_problem_closed"])
        self.assertTrue(flags["selected_phase_rank_problem_closed"])
        self.assertTrue(flags["physical_phase_closed_after_gauge_quotient"])
        self.assertFalse(flags["legacy_lambda_lock_independent_lift_claim_valid"])
        self.assertFalse(flags["selected_vacuum_lambda4_active"])
        self.assertFalse(flags["selected_vacuum_dimension6_lock_valid"])
        self.assertFalse(flags["selected_vacuum_has_extra_nonaxion_flat_phase"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
