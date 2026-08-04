#!/usr/bin/env python3
"""Tests for the SO(10) triplet / invariant-basis next-step module."""

from __future__ import annotations

import unittest

import so10_triplet_invariant_basis_v20 as basis


class TripletInvariantBasisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = basis.build_report()

    def test_status_and_open_flags(self):
        self.assertEqual(
            self.report["status"],
            "SO10_TRIPLET_INVARIANT_BASIS_STRUCTURED__FULL_TENSORS_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["invariant_ledger_recorded"])
        self.assertFalse(flags["complete_so10_scalar_potential"])
        self.assertFalse(flags["hilbert_series_complete"])
        self.assertFalse(flags["numeric_triplet_spectrum_derived"])
        self.assertFalse(flags["exact_scalar_proton_decay"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_hilbert_not_overclaimed(self):
        inv = self.report["invariant_basis"]
        self.assertFalse(inv["flag"]["hilbert_series_certificate"])
        self.assertFalse(inv["flag"]["complete_independent_invariant_basis"])
        self.assertFalse(inv["flag"]["invented_unpublished_tensors"])
        self.assertGreaterEqual(inv["n_open_for_full_potential"], 1)

    def test_symbolic_matrix_empty_numerics(self):
        m = self.report["symbolic_triplet_mass_matrix"]
        self.assertEqual(m["basis"], ["T_10", "T_126"])
        self.assertIsNone(m["eigenvalues_GeV"])
        self.assertIsNone(m["lightest_triplet_GeV"])
        self.assertFalse(m["flag"]["numeric_mass_matrix_derived"])

    def test_conditional_bound_attached(self):
        b = self.report["conditional_bound_map"]
        self.assertTrue(b["conditional_exclusions"]["M_T_equals_M_I_and_y_eff_1e-4"])
        bounds = b["lower_bounds_on_lightest_eigenvalue_GeV"]
        self.assertIn("y_eff_1e-04", bounds)
        self.assertGreater(bounds["y_eff_1e-04"], 6.0e11)


if __name__ == "__main__":
    unittest.main()
