#!/usr/bin/env python3
"""Tests for off-singlet SM-irrep Hessian extension."""

from __future__ import annotations

import unittest

import off_singlet_hessian_extension_v20 as mod


class OffSingletHessianExtensionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "OFF_SINGLET_HESSIAN_EXTENDED__MIXED_126_10_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["off_singlet_hessian_extension"])
        self.assertTrue(flags["off_singlet_evaluated_at_hilbert_vevs"])
        self.assertTrue(flags["extended_hessian_positive_definite"])
        self.assertTrue(flags["aulakh_unmixed_and_R_included"])
        self.assertFalse(flags["full_sm_irrep_mass_matrices"])
        self.assertFalse(flags["mixed_210_126_10_complete"])
        self.assertFalse(flags["live_sarah_or_pyrate_executable_run"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_spectrum(self):
        off = self.report["off_singlet_selected"]
        self.assertEqual(off["n_modes"], 10)
        self.assertTrue(off["all_positive"])
        self.assertGreater(off["lightest_GeV"], 0.0)
        self.assertTrue(
            self.report["extended_hessian"]["extended_positive_definite"]
        )

    def test_helper(self):
        out = mod.off_singlet_masses_at_vevs(
            a=1e15, omega=1e15, p=1e16, lam=0.1, m_gut=1e16
        )
        self.assertEqual(out["n_modes"], 10)
        self.assertTrue(out["all_positive"])


if __name__ == "__main__":
    unittest.main()
