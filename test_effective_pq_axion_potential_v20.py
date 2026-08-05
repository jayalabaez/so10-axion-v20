#!/usr/bin/env python3
"""Tests for tree-level effective PQ-axion potential."""

from __future__ import annotations

import unittest

import effective_pq_axion_potential_v20 as mod


class EffectivePqAxionPotentialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flags"]["tree_level_axion_potential_flat"])
        self.assertFalse(self.report["flags"]["uv_kappa_determined"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])

    def test_heavy_mass_and_flat_eff(self):
        a_k = self.report["A_kappa_scale"]["A_kappa_GeV2"]
        self.assertAlmostEqual(
            self.report["phase_sector"]["m2_heavy_GeV2"], 5.0 * a_k, places=6
        )
        self.assertEqual(self.report["phase_sector"]["tree_level_V_eff_a"], 0.0)
        self.assertGreater(self.report["decay_constant"]["f_a_GeV"], 0.0)
        self.assertFalse(
            self.report["radial_heavy_integration"]["generates_axion_potential"]
        )


if __name__ == "__main__":
    unittest.main()
