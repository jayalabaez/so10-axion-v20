#!/usr/bin/env python3
import unittest

import phase_operator_independence_audit_v20 as mod


class PhaseOperatorIndependenceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")

    def test_rank_and_null(self):
        linear = self.report["linear_algebra"]
        self.assertEqual(linear["rank_kappa_lambda4"], 2)
        self.assertEqual(linear["rank_after_adding_lambda_lock"], 2)
        self.assertEqual(linear["rank_increment_from_lambda_lock"], 0)
        self.assertEqual(linear["common_null_vector"], [1, 1, -2])

    def test_lock_is_redundant_and_zero(self):
        consequences = self.report["consequences"]
        self.assertFalse(
            consequences["dimension6_operator_adds_independent_phase_constraint"]
        )
        self.assertFalse(
            consequences["dimension6_operator_can_lift_lambda4_null_direction"]
        )
        self.assertTrue(
            self.report["selected_vacuum"]["DeltaR_squared_54_projection_zero"]
        )
        self.assertFalse(
            self.report["selected_vacuum"]["dimension6_locking_curvature_present"]
        )

    def test_whole_model_flags_false(self):
        flags = self.report["flags"]
        self.assertTrue(flags["phase_vector_independence_problem_closed"])
        self.assertFalse(flags["legacy_lambda_lock_independent_lift_claim_valid"])
        self.assertFalse(flags["selected_vacuum_dimension6_lock_valid"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
