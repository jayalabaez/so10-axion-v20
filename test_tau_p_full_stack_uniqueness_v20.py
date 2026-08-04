#!/usr/bin/env python3
"""Tests for τ_p uniqueness under the full UV stack."""

from __future__ import annotations

import unittest

import tau_p_full_stack_uniqueness_v20 as mod


class TauPFullStackUniquenessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "TAU_P_UNIQUE_UNDER_FULL_UV_STACK__EXACT_UNIQUE_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["tau_p_unique_under_full_uv_stack"])
        self.assertTrue(flags["exact_XY_masses_used"])
        self.assertTrue(flags["residual_spectrum_used"])
        self.assertTrue(flags["mixed_rep_hilbert_used"])
        self.assertFalse(flags["live_sarah_or_pyrate_executable_run"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_certificate_residuals(self):
        cert = self.report["certificate"]
        self.assertGreater(cert["selected_tau_e_years"], 0.0)
        for name in mod.RESIDUAL_NOW_CLOSED:
            self.assertTrue(cert["residual_now_closed"][name])
        self.assertTrue(
            cert["residual_still_open"]["live_sarah_or_pyrate_executable_run"]
        )
        self.assertTrue(
            cert["closed_under_full_uv_stack"]["exact_XY_masses_at_selected_vevs"]
        )

    def test_masses_and_scalar(self):
        self.assertGreater(
            self.report["gauge_lifetime"]["M_PD_mediator_GeV"], 0.0
        )
        self.assertIsNotNone(self.report["scalar_lifetime"]["weakest"])


if __name__ == "__main__":
    unittest.main()
