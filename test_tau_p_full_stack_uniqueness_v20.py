#!/usr/bin/env python3
"""Regression tests for the withdrawn full-stack proton-lifetime claim."""
from __future__ import annotations

import math
import unittest

import tau_p_full_stack_uniqueness_v20 as mod


class TauPSelectedStackConditionalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_is_conditional_not_unique(self):
        self.assertEqual(self.report["n_failed"], 0)
        self.assertEqual(
            self.report["status"],
            "TAU_P_SELECTED_STACK_CONDITIONAL__UNIQUE_LIFETIME_OPEN",
        )
        flags = self.report["flag"]
        self.assertFalse(flags["tau_p_unique_under_full_uv_stack"])
        self.assertFalse(flags["tau_p_unique_under_reduced_uv_vacuum_selection"])
        self.assertFalse(flags["exact_XY_masses_used"])
        self.assertFalse(flags["residual_spectrum_used"])
        self.assertFalse(flags["physical_triplet_spectrum_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_selected_point_is_retained_as_finite_benchmark(self):
        cert = self.report["certificate"]
        self.assertTrue(cert["conditional_only"])
        self.assertTrue(math.isfinite(cert["selected_tau_e_years"]))
        self.assertGreater(cert["selected_tau_e_years"], 0.0)
        self.assertTrue(
            cert["closed_under_full_uv_stack"]["selected_point_inputs_available"]
        )
        self.assertFalse(
            cert["closed_under_full_uv_stack"]["full_physical_stack_closed"]
        )

    def test_physics_blockers_remain_explicit(self):
        residuals = self.report["certificate"]["residual_still_open"]
        for name in mod.RESIDUAL_STILL_OPEN:
            self.assertTrue(residuals[name])
        self.assertIn("direct_component_mass_squared_matrix", residuals)
        self.assertIn("full_component_hessian_and_competing_extrema", residuals)
        self.assertIn("exact_unique_proton_lifetime", residuals)

    def test_historical_scalar_output_is_never_physical(self):
        scalar = self.report["scalar_lifetime"]
        self.assertTrue(scalar["conditional_only"])
        self.assertFalse(scalar["physical_spectrum"])

    def test_selected_failure_never_becomes_whole_model_failure(self):
        cert = self.report["certificate"]
        if not cert["selected_passes_SK"]:
            self.assertFalse(self.report["flag"]["whole_model_excluded"])
            self.assertFalse(
                self.report["flag"]["exact_unique_proton_lifetime"]
            )


if __name__ == "__main__":
    unittest.main()
