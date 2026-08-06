#!/usr/bin/env python3
"""Tests for source pure-210 → reduced potential insertion."""

from __future__ import annotations

import unittest

import source_pure210_reduced_potential_insertion_v20 as mod


class SourcePure210ReducedInsertionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertFalse(self.report["flags"]["whole_model_validated"])
        self.assertFalse(self.report["flags"]["g1_closed"])
        self.assertTrue(self.report["flags"]["diagnostic_couplings_not_uv_fixed"])
        self.assertTrue(self.report["flags"]["radial_proxy_identification_only"])

    def test_insertion_patches_and_revalidates(self):
        self.assertTrue(self.report["flags"]["source_pure210_inserted_into_reduced_P210"])
        self.assertFalse(self.report["flags"]["reduced_potential_insertion_pending"])
        self.assertGreater(self.report["radial_proxy"]["lambda_eff"], 0.0)
        self.assertGreater(
            self.report["selected_vacuum_densities"]["||(ΦΦ)_45||^2 / ||Φ||^4"], 0.0
        )
        self.assertTrue(self.report["reduced_quartic"]["spectral_source_patched"]["positive_definite"])
        self.assertTrue(self.report["reduced_quartic"]["copositive_source_patched"])
        self.assertTrue(self.report["singlet_span"]["bfb"]["nonnegative"])
        self.assertTrue(self.report["reduced_hessian_lam4_0"]["positive_definite"])
        self.assertGreater(self.report["reduced_hessian_lam4_0"]["min_eig_mpmath"], 0.0)
        self.assertTrue(
            self.report["reduced_hessian_lam4_0"]["float64_false_tachyon_documented"]
        )
        self.assertFalse(self.report["flags"]["reduced_hessian_soft_rematch_open"])
        self.assertFalse(
            self.report["remaining_blockers"].get(
                "rematch_soft_masses_to_source_lambda_P", False
            )
        )
        self.assertTrue(
            self.report["remaining_blockers"][
                "replace_isotropic_P_cross_proxy_with_published_linear_cg"
            ]
        )

if __name__ == "__main__":
    unittest.main()
