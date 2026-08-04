#!/usr/bin/env python3
"""Tests for Hilbert/mixed operator 8-component Hessian."""

from __future__ import annotations

import unittest

import hilbert_mixed_8comp_hessian_v20 as mod


class HilbertMixed8CompHessianTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "HILBERT_MIXED_8COMP_HESSIAN_PD__OFF_SINGLET_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["schematic_well_hessian_replaced_by_hilbert_mixed"])
        self.assertTrue(flags["operator_based_8comp_hessian_pd"])
        self.assertTrue(flags["schematic_lifted_well_instability_fixed"])
        self.assertTrue(flags["lam210_cross_terms_included"])
        self.assertFalse(flags["full_sm_irrep_mass_matrices"])
        self.assertFalse(flags["live_sarah_or_pyrate_executable_run"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_improvement(self):
        imp = self.report["improvement"]
        self.assertTrue(imp["operator_pd"])
        self.assertFalse(imp["schematic_pd"])
        self.assertTrue(imp["fixed_schematic_instability"])
        self.assertGreater(imp["min_eig_operator"], 0.0)
        self.assertLess(imp["min_eig_schematic"], 0.0)

    def test_eff_helper(self):
        ef = mod.eff_210_linear(a=1.0, omega=2.0, p=3.0)
        self.assertAlmostEqual(ef["eff_126"], 1.0 + 2.0 + 3.0)
        self.assertIn("eff_10", ef)


if __name__ == "__main__":
    unittest.main()
