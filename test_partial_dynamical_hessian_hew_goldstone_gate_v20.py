#!/usr/bin/env python3
"""Tests for partial dynamical Hessian + hEW Goldstone gate."""

from __future__ import annotations

import unittest

import partial_dynamical_hessian_hew_goldstone_gate_v20 as mod


class PartialDynamicalHessianHewGoldstoneGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["status"],
            "PARTIAL_DYNAMICAL_HESSIAN_HODGE_C_PORTAL_LIFT_READY__IM_H_OPEN",
        )
        flags = self.report["flags"]
        self.assertTrue(flags["partial_dynamical_hessian_goldstone_gate"])
        self.assertTrue(flags["hodge_c_embedding_applied"])
        self.assertTrue(flags["portal_b_lifted_into_form_basis"])
        self.assertTrue(flags["hew_36_goldstones_applied"])
        self.assertTrue(flags["form_basis_skeleton_positive_after_projection"])
        self.assertFalse(flags["im_H_in_orbit_embedding"])
        self.assertFalse(flags["full_component_hessian_complete"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_projected_spectrum(self):
        gp = self.report["goldstone_projection"]
        self.assertEqual(gp["rank"], 36)
        unit = gp["unit_skeleton_spectrum"]
        self.assertEqual(unit["n_zero"], 36)
        self.assertEqual(unit["n_positive"], 688)
        self.assertEqual(unit["n_negative"], 0)
        dyn = gp["dynamical_scaled_spectrum"]
        self.assertEqual(dyn["n_zero"], 36)
        self.assertEqual(dyn["n_positive"], 688)
        self.assertEqual(dyn["n_negative"], 0)
        self.assertEqual(self.report["embedding"]["total"], 724)
        self.assertTrue(self.report["form_basis_skeleton"]["uses_portal_B"])


if __name__ == "__main__":
    unittest.main()
