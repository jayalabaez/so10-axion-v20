#!/usr/bin/env python3
"""Tests for the H-S portal threshold at the tuned G3 target."""
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
        flags = self.report["flags"]
        self.assertTrue(flags["higgs_mass_tension_resolvable_by_declared_hs_portal"])
        self.assertFalse(flags["g3_closed"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_compiler_reproduces_singlet_threshold_formula(self) -> None:
        for point in self.report["scan"]:
            expected = 1.0 - point["lambda_HS"] ** 2 / 4.0
            self.assertAlmostEqual(point["lambda_eff"], expected, places=9)
            self.assertAlmostEqual(point["retuned_O06"], -point["lambda_HS"] / 25.0, places=12)

    def test_required_portal_is_perturbative_and_matches_the_sm(self) -> None:
        matching = self.report["sm_matching"]
        required = matching["lambda_HS_required_at_certified_lambda_H"]
        self.assertAlmostEqual(required, 2.0 * math.sqrt(1.0 - matching["lambda_gut_required_one_loop"]), places=12)
        self.assertAlmostEqual(required, 2.0335, delta=2.0e-3)
        self.assertTrue(matching["portal_perturbative"])
        self.assertAlmostEqual(matching["solution"]["lambda_eff"], matching["lambda_gut_required_one_loop"], places=9)
        self.assertAlmostEqual(matching["solution_m_h_tree_GeV"], 123.62, delta=0.05)

    def test_portal_retune_keeps_a_psd_stationary_point(self) -> None:
        for point in self.report["scan"] + [self.report["sm_matching"]["solution"]]:
            self.assertLess(point["gradient_max_abs"], 1.0e-10)
            self.assertEqual(point["negative_eigenvalues_below_minus_1e_minus_9"], 0)
            self.assertEqual(point["zero_modes"], 39)

    def test_committed_artifact_matches_fresh_report(self) -> None:
        committed = json.loads(portal.OUT_JSON.read_text(encoding="utf-8"))
        fresh = json.loads(json.dumps(target._jsonable(self.report), sort_keys=True))
        for key in ("status", "checks", "flags", "formula", "couplings"):
            self.assertEqual(committed[key], fresh[key], key)
        self.assertAlmostEqual(
            committed["sm_matching"]["lambda_HS_required_at_certified_lambda_H"],
            fresh["sm_matching"]["lambda_HS_required_at_certified_lambda_H"],
            places=9,
        )


if __name__ == "__main__":
    unittest.main()
