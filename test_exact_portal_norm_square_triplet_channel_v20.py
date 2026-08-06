#!/usr/bin/env python3
from __future__ import annotations

import unittest

import numpy as np

import exact_portal_norm_square_triplet_channel_v20 as exact


class ExactPortalNormSquareTripletChannelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = exact.build_report()

    def test_gate_closes_specific_contraction(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "CLOSED_SUBPROBLEM")
        self.assertTrue(self.report["flag"]["exact_portal_norm_square_channel_closed"])

    def test_analytic_blocks(self) -> None:
        p, a, omega = 0.9, 0.4, 0.7
        c = exact.analytic_coefficients(p, a, omega)
        blocks = exact.analytic_sigma_blocks(p, a, omega)
        xm, xp, y = c["x_minus_GeV"], c["x_plus_GeV"], c["y_GeV"]
        self.assertTrue(np.allclose(blocks["A_u_sigma_GeV2"], [[xm * xm]]))
        self.assertTrue(
            np.allclose(
                blocks["A_v_sigma_GeV2"],
                [[xp * xp, xp * y], [xp * y, y * y]],
            )
        )

    def test_positive_rank_one_structure(self) -> None:
        blocks = self.report["exact_sigma_blocks"]
        matrix = np.asarray(blocks["A_v_GeV2"], dtype=float)
        eigenvalues = np.linalg.eigvalsh(matrix)
        self.assertGreaterEqual(eigenvalues[0], -1e-12)
        self.assertGreater(eigenvalues[-1], 0.0)
        self.assertAlmostEqual(np.linalg.det(matrix), 0.0, places=12)
        self.assertEqual(blocks["positive_sector_rank"], 1)

    def test_tensor_and_spectrum_crosschecks(self) -> None:
        residuals = self.report["numerical_residuals"]
        self.assertLess(residuals["u_block"], 1e-12)
        self.assertLess(residuals["v_block"], 1e-12)
        self.assertLess(residuals["weight_spread"], 1e-12)
        cross = self.report["exact_H_crosscheck"]
        self.assertLess(cross["nonzero_spectrum_residual"], 1e-10)

    def test_scope_remains_fail_closed(self) -> None:
        closed = self.report["newly_closed_subproblem"]
        self.assertTrue(all(closed.values()))
        flags = self.report["flag"]
        self.assertTrue(flags["exact_quartic_t2bar_t4bar_mixing_derived"])
        self.assertFalse(flags["all_PhiSigma_anisotropic_channels_complete"])
        self.assertFalse(flags["physical_triplet_spectrum_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
