#!/usr/bin/env python3
"""Tests for direct portal mass-squared integration."""
from __future__ import annotations

import unittest

import direct_portal_mass2_integration_v20 as mod


class DirectPortalMass2IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_exact_partial_closure_integrates(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["status"],
            "DIRECT_PORTAL_MASS2_INTEGRATED__FULL_DIAGONAL_HESSIAN_OPEN",
        )
        closures = self.report["new_exact_closures"]
        self.assertTrue(closures["lambda4_vS_TPhi_offdiagonal_mass2_block"])
        self.assertTrue(closures["real_272_mode_H10_Sigmabar_hessian_embedding"])
        self.assertTrue(closures["schur_complement_positivity_criterion"])

    def test_conditional_result_is_not_model_exclusion(self):
        diagnostic = self.report["conditional_historical_diagnostic"]
        self.assertTrue(
            diagnostic[
                "generic_probe_both_doublet_branches_fail_on_assumption"
            ]
        )
        self.assertGreater(
            diagnostic["max_abs_a_plus_omega_over_MGUT"], 0.0
        )
        self.assertGreater(
            diagnostic["max_abs_a_minus_omega_over_MGUT"], 0.0
        )
        self.assertFalse(diagnostic["full_model_exclusion"])

    def test_missing_diagonal_hessian_remains_open(self):
        flags = self.report["flags"]
        self.assertTrue(
            flags["direct_portal_component_mass_squared_insertion_closed"]
        )
        self.assertFalse(
            flags["full_nonsusy_diagonal_component_hessian_supplied"]
        )
        self.assertFalse(flags["full_component_hessian_complete"])
        self.assertFalse(flags["global_vacuum_complete"])
        self.assertFalse(flags["historical_lambda4_full_model_excluded"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_next_physical_requirements_are_explicit(self):
        open_items = self.report["still_open"]
        self.assertTrue(open_items["complete_nonsusy_invariant_ring"])
        self.assertTrue(
            open_items["derive_H10_diagonal_component_mass_squared"]
        )
        self.assertTrue(
            open_items["derive_Sigmabar126_diagonal_component_mass_squared"]
        )
        self.assertTrue(
            open_items["remove_exactly_33_goldstones_from_complete_hessian"]
        )


if __name__ == "__main__":
    unittest.main()
