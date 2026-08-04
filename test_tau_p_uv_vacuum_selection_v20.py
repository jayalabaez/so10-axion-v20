#!/usr/bin/env python3
"""Tests for τ_p UV vacuum-selection certificate."""

from __future__ import annotations

import math
import unittest

import tau_p_uv_vacuum_selection_v20 as mod


class TauPUVVacuumSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "TAU_P_UNIQUE_UNDER_REDUCED_UV_SELECTION__EXACT_UNIQUE_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["tau_p_unique_under_reduced_uv_vacuum_selection"])
        self.assertTrue(flags["uv_selected_gauge_tau_computed"])
        self.assertTrue(flags["selected_gauge_passes_SK"])
        self.assertTrue(flags["scalar_ref_channels_evaluated_at_MI"])
        self.assertTrue(flags["residual_MX_envelope_documented"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_certificate(self):
        cert = self.report["certificate"]
        self.assertGreater(cert["selected_tau_e_years"], 0.0)
        self.assertTrue(cert["selected_passes_SK"])
        self.assertTrue(math.isfinite(cert["envelope_min_tau_e_years"]))
        self.assertTrue(cert["closed_under_reduced_uv_selection"]["psi_fixed_to_zero"])
        self.assertTrue(
            cert["residual_open"]["exact_XY_mass_from_full_scalar_vacuum"]
        )
        vac = self.report["uv_selected_vacuum"]
        self.assertEqual(vac["delta_i"]["delta_phys"], 0.0)
        self.assertGreater(vac["soft_scale"]["M_1_2_GeV"], 0.0)


if __name__ == "__main__":
    unittest.main()
