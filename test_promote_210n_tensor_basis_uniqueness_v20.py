#!/usr/bin/env python3
"""Tests for promoting uniqueness to the full pure-210ⁿ tensor basis."""

from __future__ import annotations

import unittest

import promote_210n_tensor_basis_uniqueness_v20 as mod


class Promote210nTensorBasisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "UNIQUE_FROM_FULL_PURE_210N_TENSOR_BASIS__MIXED_REP_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["unique_from_full_pure_210n_tensor_basis"])
        self.assertTrue(flags["unique_from_full_210n_tensor_basis"])
        self.assertTrue(flags["hilbert_restriction_kernel_used"])
        self.assertTrue(flags["schematic_quartic_projected_to_H4"])
        self.assertFalse(flags["mixed_rep_full_hilbert_series"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_projection_and_selection(self):
        proj = self.report["quartic_projection"]
        self.assertTrue(proj["spans_full_H4"])
        self.assertEqual(proj["lstsq_rank"], 4)
        self.assertLess(proj["relative_noninvariant_residual"], 1.0)
        fr = self.report["selected_hilbert"]["fractions"]
        self.assertAlmostEqual(
            fr["a_over_MGUT"] + fr["omega_over_MGUT"] + fr["p_over_MGUT"],
            1.0,
            places=8,
        )
        self.assertTrue(all(v > 0.0 for v in fr.values()))

    def test_helper_projection(self):
        eta = {
            "a4": 0.05,
            "w4": 0.05,
            "p4": 0.05,
            "a2w2": 0.04,
            "a2p2": 0.03,
            "w2p2": 0.04,
        }
        out = mod.project_schematic_quartic_onto_hilbert(eta=eta)
        self.assertEqual(len(out["coeffs_vector"]), 4)
        self.assertTrue(out["spans_full_H4"])


if __name__ == "__main__":
    unittest.main()
