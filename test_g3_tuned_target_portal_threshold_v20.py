#!/usr/bin/env python3
"""Tests for the H-S portal threshold and its local-minimality limit."""
from __future__ import annotations

import json
import math
import unittest

import g3_candidate_physical_target_audit_v20 as target
import g3_tuned_target_portal_threshold_v20 as portal


class PortalThresholdTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = portal.build_report()

    def test_all_checks_pass_and_scope_is_fail_closed(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "CONSTRAINT")
        flags = self.report["flags"]
        self.assertFalse(flags["g3_closed"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])
        self.assertFalse(flags["certified_point_is_sm_vacuum"])
        self.assertFalse(
            self.report["scientific_outcomes"]["higgs_mass_tension_resolvable_by_tree_level_portal_at_a_local_minimum"]
        )

    def test_compiler_reproduces_singlet_threshold_formula(self) -> None:
        for point in self.report["scan"]:
            self.assertAlmostEqual(point["lambda_eff"], 1.0 - point["lambda_HS"] ** 2 / 4.0, places=9)
            self.assertAlmostEqual(point["retuned_O06"], -point["lambda_HS"] / 25.0, places=12)
            self.assertEqual(point["negative_hessian_eigenvalues"], 0)
            self.assertEqual(point["zero_modes"], 39)

    def test_local_minimality_bound(self) -> None:
        outcomes = self.report["scientific_outcomes"]
        self.assertAlmostEqual(outcomes["local_minimum_requires_lambda_HS_at_most"], 2.0, places=12)
        self.assertTrue(outcomes["stable_control_lambda_HS_1_has_no_lower_S_zero_branch"])
        control = self.report["stable_control"]
        self.assertTrue(control["tuned_point_is_tree_level_local_minimum"])
        self.assertGreater(control["S_zero_branch"]["delta_V"], 0.0)

    def test_sm_matched_portal_makes_the_tuned_point_a_saddle(self) -> None:
        matching = self.report["sm_matching"]
        self.assertLess(matching["lambda_gut_required_two_loop"], 0.0)
        required = matching["lambda_HS_required_at_benchmark_lambda_H_lambda_S"]
        self.assertAlmostEqual(required, 2.0 * math.sqrt(1.0 - matching["lambda_gut_required_two_loop"]), places=12)
        self.assertGreater(required, 2.0)
        valley = matching["valley"]
        self.assertFalse(valley["tuned_point_is_tree_level_local_minimum"])
        for row in valley["valley"]:
            self.assertLess(row["delta_V"], 0.0)
            self.assertAlmostEqual(row["delta_V"], row["lambda_eff_y2"], delta=1.0e-12)
        branch = valley["S_zero_branch"]
        self.assertTrue(branch["lower_than_tuned_point"])
        self.assertAlmostEqual(branch["delta_V"], branch["analytic"], delta=1.0e-12)
        self.assertTrue(self.report["scientific_outcomes"]["sm_matched_point_has_lower_EW_breaking_PQ_restoring_configuration"])

    def test_committed_artifact_matches_fresh_report(self) -> None:
        committed = json.loads(portal.OUT_JSON.read_text(encoding="utf-8"))
        fresh = json.loads(json.dumps(target._jsonable(self.report), sort_keys=True))
        for key in ("status", "checks", "flags", "formula", "couplings", "scientific_outcomes", "sm_matching"):
            self.assertEqual(target.report_mismatches(committed[key], fresh[key], key), [])


if __name__ == "__main__":
    unittest.main()
