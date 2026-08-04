#!/usr/bin/env python3
"""Tests for unique (a,ω,p) from the PS-singlet 210 potential."""

from __future__ import annotations

import unittest

import numpy as np

import unique_a_omega_p_ps_singlet_v20 as mod


class UniqueAOmegaPPSSingletTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "UNIQUE_A_OMEGA_P_FROM_PS_SINGLET__FULL_210N_OPEN",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["unique_a_omega_p_under_ps_singlet_potential"])
        self.assertTrue(flags["replaced_stack_030_050_020_convention"])
        self.assertTrue(flags["uv_masses_recomputed_at_selected_ratios"])
        self.assertFalse(flags["unique_from_full_210n_tensor_basis"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_fractions_and_masses(self):
        fr = self.report["selected"]["fractions"]
        self.assertAlmostEqual(
            fr["a_over_MGUT"] + fr["omega_over_MGUT"] + fr["p_over_MGUT"],
            1.0,
            places=8,
        )
        self.assertTrue(all(v > 0.0 for v in fr.values()))
        self.assertLess(
            self.report["selected"]["soft_shift_norm_over_MGUT2"],
            self.report["selected"]["stack_convention"]["soft_shift_norm_over_MGUT2"]
            * (1.0 + 1e-6),
        )
        self.assertGreater(
            self.report["masses_selected"]["proton_decay_mediator_GeV"], 0.0
        )

    def test_helper(self):
        a, w, p = mod.fractions_to_vevs(np.array([0.3, 0.5, 0.2]), 1.0e16)
        self.assertAlmostEqual(a + w + p, 1.0e16, places=3)


if __name__ == "__main__":
    unittest.main()
