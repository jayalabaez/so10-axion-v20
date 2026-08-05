#!/usr/bin/env python3
"""Tests for extended form-basis Hessian with Im H and S/Φ₁₇."""

from __future__ import annotations

import unittest

import extended_form_basis_hessian_imh_spectators_v20 as mod


class ExtendedFormBasisImhSpectatorsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["status"],
            "EXTENDED_FORM_BASIS_IMH_SPECTATORS_READY__PQ_AXION_OPEN",
        )
        flags = self.report["flags"]
        self.assertTrue(flags["extended_form_basis_imh_spectators_ready"])
        self.assertTrue(flags["im_H_in_embedding"])
        self.assertTrue(flags["full_holomorphic_portal_lifted"])
        self.assertTrue(flags["S_Phi17_dynamical_blocks"])
        self.assertFalse(flags["pq_axion_null_removed"])
        self.assertFalse(flags["full_component_hessian_complete"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_embedding_and_spectrum(self):
        self.assertEqual(self.report["embedding"]["total"], 738)
        gp = self.report["goldstone_projection"]
        self.assertEqual(gp["rank"], 36)
        self.assertAlmostEqual(gp["trace_P_G"], 36.0, places=6)
        self.assertAlmostEqual(gp["trace_P_phys"], 702.0, places=6)
        unit = gp["unit_skeleton_spectrum"]
        self.assertEqual(unit["n_zero"], 36)
        self.assertEqual(unit["n_positive"], 702)
        self.assertEqual(unit["n_negative"], 0)
        dyn = gp["dynamical_scaled_spectrum"]
        self.assertEqual(dyn["n_zero"], 36)
        self.assertEqual(dyn["n_positive"], 702)
        self.assertEqual(dyn["n_negative"], 0)
        sk = self.report["form_basis_skeleton"]
        self.assertTrue(sk["im_H_included"])
        self.assertTrue(sk["S_Phi17_included"])


if __name__ == "__main__":
    unittest.main()
