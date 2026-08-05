#!/usr/bin/env python3
import math
import unittest

import numpy as np

import so10_210_symmetric_45_source_projector_v20 as mod


class SourceCorrectSymmetric45Tests(unittest.TestCase):
    def test_anchor_normalization_and_nonzero_self_channel(self):
        anchor = mod.simple_anchor_vector()
        q = mod.symmetric_210_to_45(anchor, anchor)
        self.assertAlmostEqual(q[8, 9], 2.0 * mod.SOURCE_FACTOR, places=10)
        self.assertGreater(mod.channel_norm_sq(q), 0.0)

    def test_swap_symmetry_and_output_antisymmetry(self):
        rng = np.random.default_rng(45)
        phi = rng.normal(size=mod.N_COMBOS)
        psi = rng.normal(size=mod.N_COMBOS)
        q = mod.symmetric_210_to_45(phi, psi)
        q_swap = mod.symmetric_210_to_45(psi, phi)
        self.assertLess(np.max(np.abs(q - q_swap)), 1e-10)
        self.assertLess(np.max(np.abs(q + q.T)), 1e-10)

    def test_infinitesimal_equivariance(self):
        rng = np.random.default_rng(451)
        phi = rng.normal(size=mod.N_COMBOS)
        psi = rng.normal(size=mod.N_COMBOS)
        for generator in [(0, 1), (2, 7), (8, 9)]:
            self.assertLess(mod.equivariance_residual(phi, psi, *generator), 1e-10)

    def test_report_is_fail_closed_and_source_correct(self):
        report = mod.build_report()
        self.assertEqual(report["n_failed"], 0, report)
        self.assertEqual(report["overall_state"], "BLOCKED")
        self.assertTrue(report["flags"]["symmetric_product_45_projector_ready"])
        self.assertTrue(report["flags"]["old_same_field_45_vanishing_cannot_close_quartic_channel"])
        self.assertFalse(report["flags"]["whole_model_validated"])


if __name__ == "__main__":
    unittest.main()
