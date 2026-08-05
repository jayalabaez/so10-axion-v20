#!/usr/bin/env python3
import math
import unittest

import numpy as np

import so10_210_source_quartic_basis_v20 as basis
import so10_210_symmetric_45_source_projector_v20 as source45


class SourceNormalizedPure210QuarticTests(unittest.TestCase):
    def test_corrected_45_anchor_and_factor(self):
        anchor = source45.simple_anchor_vector()
        output = source45.symmetric_210_to_45(anchor, anchor)
        self.assertAlmostEqual(source45.SOURCE_FACTOR, 1 / math.sqrt(70), places=14)
        self.assertAlmostEqual(output[8, 9], 2 / math.sqrt(70), places=12)

    def test_54_anchor(self):
        output = basis.source_210_to_54(
            basis.anchor_54_vector(), basis.anchor_54_vector()
        )
        self.assertAlmostEqual(output[0, 1], 2 / math.sqrt(112), places=12)
        self.assertLess(np.max(np.abs(output - output.T)), 1e-12)
        self.assertAlmostEqual(np.trace(output), 0.0, places=12)

    def test_210_anchor(self):
        output = basis.source_210_to_210_six(
            basis.anchor_210_vector(), basis.anchor_210_vector()
        )
        value = output[basis.INDEX6[(4, 5, 6, 7, 8, 9)]]
        self.assertAlmostEqual(value, 2 / math.sqrt(90), places=12)

    def test_54_and_210_equivariance(self):
        rng = np.random.default_rng(210)
        phi = rng.normal(size=len(basis.COMB4))
        psi = rng.normal(size=len(basis.COMB4))
        for generator in [(0, 1), (2, 7), (8, 9)]:
            self.assertLess(
                basis.equivariance_54_residual(phi, psi, *generator), 1e-10
            )
            self.assertLess(
                basis.equivariance_210_residual(phi, psi, *generator), 1e-10
            )

    def test_published_1050_identity_is_nonnegative_on_random_forms(self):
        rng = np.random.default_rng(1050)
        for _ in range(20):
            invariants = basis.pure_210_invariants(
                rng.normal(size=len(basis.COMB4))
            )
            self.assertGreaterEqual(
                invariants["channel_1050_norm_sq_from_identity"], -1e-9
            )

    def test_ps_p_direction_matches_source_nulls(self):
        p = source45.form_to_vector(basis.direct.singlet_basis()["p"])
        invariants = basis.pure_210_invariants(p)
        self.assertAlmostEqual(invariants["channel_45_norm_sq"], 0.0, places=12)
        self.assertAlmostEqual(invariants["channel_210_norm_sq"], 0.0, places=12)
        self.assertAlmostEqual(
            invariants["channel_1050_norm_sq_from_identity"], 0.0, places=12
        )
        self.assertAlmostEqual(invariants["channel_54_norm_sq"], 3 / 70, places=12)

    def test_quartic_homogeneity(self):
        rng = np.random.default_rng(4)
        phi = rng.normal(size=len(basis.COMB4))
        base = basis.pure_210_invariants(phi)
        scaled = basis.pure_210_invariants(3.0 * phi)
        for name in base:
            self.assertAlmostEqual(scaled[name] / base[name], 81.0, places=9)

    def test_report_closes_only_pure_210_subsector(self):
        report = basis.build_report()
        self.assertEqual(report["n_failed"], 0, report)
        self.assertEqual(report["overall_state"], "BLOCKED")
        self.assertTrue(report["closure"]["pure_210_quartic_basis_closed"])
        self.assertFalse(report["closure"]["full_mixed_representation_ring_G1_closed"])
        self.assertFalse(report["closure"]["full_component_potential_G2_closed"])
        self.assertFalse(report["flags"]["whole_model_validated"])


if __name__ == "__main__":
    unittest.main()
