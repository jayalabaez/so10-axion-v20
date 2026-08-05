#!/usr/bin/env python3
"""Tests for the selected-vacuum neutral phase gauge quotient."""
from __future__ import annotations

import unittest

import numpy as np

import selected_vacuum_neutral_phase_gauge_quotient_v20 as mod


class SelectedVacuumNeutralPhaseGaugeQuotientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.quotient_report(1.0)

    def test_exact_gauge_quotient(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(
            self.report["status"],
            "SELECTED_VACUUM_NEUTRAL_PHASE_CLOSED_AFTER_GAUGE_QUOTIENT",
        )
        h = self.report["hessian"]
        self.assertEqual(h["rank_before_quotient"], 1)
        self.assertEqual(h["nullity_before_quotient"], 2)
        self.assertEqual(h["gauge_orbit_rank_removed"], 1)
        self.assertEqual(h["physical_phase_dimension"], 2)
        self.assertEqual(h["rank_after_quotient"], 1)
        self.assertEqual(h["nullity_after_quotient"], 1)
        self.assertEqual(h["physical_null_vector_integer"], [1, -2])

    def test_delta_phase_is_gauge_null(self):
        h = np.asarray(self.report["hessian"]["before_quotient"], dtype=float)
        q = np.asarray(
            self.report["basis"]["neutral_gauge_orbit_Zprime"], dtype=float
        )
        self.assertLess(np.linalg.norm(h @ q), 1e-12)
        self.assertEqual(q.tolist(), [1.0, 0.0, 0.0])

    def test_exactly_one_physical_pq_null(self):
        h = np.asarray(self.report["hessian"]["after_quotient"], dtype=float)
        pq = np.asarray(
            self.report["basis"]["PQ_vector_in_physical_basis"], dtype=float
        )
        self.assertLess(np.linalg.norm(h @ pq), 1e-12)
        self.assertEqual(pq.tolist(), [1.0, -2.0])
        flags = self.report["flags"]
        self.assertTrue(flags["DeltaR_phase_eaten_by_Zprime_BL_R"])
        self.assertFalse(flags["extra_nonaxion_flat_phase_present"])
        self.assertTrue(flags["exactly_one_physical_PQ_null"])

    def test_all_orders_selection_rule_is_not_obstruction(self):
        rule = self.report["all_orders_selection_rule"]
        self.assertEqual(rule["BL_neutrality_on_selected_VEVs"], "d=0")
        self.assertEqual(rule["combined_result"], "(d,h,s)=s*(0,2,1)")
        self.assertIn("eaten Z' gauge direction", rule["interpretation"])
        self.assertFalse(
            self.report["flags"]["finite_dimension_phase_search_required_for_closure"]
        )

    def test_honest_scope(self):
        flags = self.report["flags"]
        self.assertFalse(flags["full_component_scalar_hessian_complete"])
        self.assertFalse(flags["root_by_root_33_goldstone_projection_complete"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_positive_amplitude_required(self):
        with self.assertRaises(ValueError):
            mod.quotient_report(0.0)


if __name__ == "__main__":
    unittest.main()
