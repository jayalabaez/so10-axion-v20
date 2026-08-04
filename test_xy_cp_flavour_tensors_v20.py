#!/usr/bin/env python3
"""Tests for CP-aware X/Y flavour tensors."""

from __future__ import annotations

import unittest

import numpy as np

import xy_cp_flavour_tensors_v20 as mod


class XYCPFlavourTensorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "XY_CP_FLAVOUR_TENSORS_COMPLETE__UV_CP_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["full_cp_xy_tensors"])
        self.assertTrue(flags["coherent_V2_interference"])
        self.assertTrue(flags["subleading_cp_portals_included"])
        self.assertTrue(flags["reduces_to_magnitude_for_real_V"])
        self.assertFalse(flags["uv_cp_phases_from_potential"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_coherent_reduces_for_real(self):
        v = 0.97367 + 0j
        self.assertAlmostEqual(
            mod.coherent_flavour_factor(v),
            mod.magnitude_flavour_factor(v),
            places=12,
        )

    def test_cp_interference_nonzero_for_phased_v(self):
        v = 0.22 * np.exp(1j * 0.7)
        self.assertNotAlmostEqual(
            mod.coherent_flavour_factor(v),
            mod.magnitude_flavour_factor(v),
            places=6,
        )

    def test_subleading_cp_portal_shifts_factor(self):
        ch = self.report["tensors_GUT"]["channels"]["p_to_e_pi0"]
        self.assertGreater(ch["interference"]["abs_V_cp"], 0.0)
        self.assertNotAlmostEqual(ch["F_CP"], ch["F_lead_only"], places=8)

    def test_lifetime_passes_sk(self):
        self.assertTrue(self.report["lifetimes"]["passes_SK_e_pi0_CP"])
        self.assertGreater(abs(self.report["lifetimes"]["delta_rel_tau_e"]), 0.0)


if __name__ == "__main__":
    unittest.main()
