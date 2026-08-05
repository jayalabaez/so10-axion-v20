#!/usr/bin/env python3
"""Tests for UV CP phases from the SO(10)×Z₁₇ phase potential."""

from __future__ import annotations

import unittest

import uv_cp_phases_from_potential_v20 as mod


class UVCPPhasesFromPotentialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "UV_CP_PHASES_FROM_POTENTIAL__UNIQUE_VACUUM_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["uv_cp_phases_from_potential"])
        self.assertTrue(flags["real_couplings_cp_conserving_vacuum"])
        self.assertTrue(flags["complex_coupling_phases_conditional"])
        self.assertTrue(flags["axion_flat_direction_quotiented"])
        self.assertTrue(flags["zprime_gauge_goldstone_fixed"])
        self.assertTrue(flags["fed_into_xy_gauge_width"])
        self.assertFalse(flags["unique_uv_cp_phases"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_real_and_conditional(self):
        real = self.report["real_coupling_vacuum"]
        self.assertTrue(real["cp_conserving"])
        self.assertLess(abs(real["invariants"]["psi_physical_uv_phase"]), 1e-6)
        self.assertLess(abs(real["invariants"]["theta_kappa"]), 1e-6)
        self.assertTrue(real["selected_vacuum_kappa_only"])
        self.assertTrue(real["gauge_fixed_DeltaR"])
        cond = self.report["conditional_uv_point"]
        self.assertTrue(abs(cond["psi_physical_uv_phase"]) > 1e-3)
        gw = self.report["gauge_width"]
        self.assertGreater(gw["conditional_uv_cp"]["tau_e_years"], 0.0)
        self.assertTrue(gw["conditional_uv_cp"]["passes_SK"])
        self.assertTrue(abs(gw["delta_rel_tau_uv_vs_pdg"]) >= 0.0)


if __name__ == "__main__":
    unittest.main()
