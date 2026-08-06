#!/usr/bin/env python3
from __future__ import annotations

import unittest

import numpy as np

import exact_mixed_54_triplet_channel_v20 as exact
import exact_10h_squared_s_bterm_v20 as h10


class ExactMixed54TripletChannelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = exact.build_report()

    def test_gate_closes_shared_54_subproblem(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "CLOSED_SUBPROBLEM")
        self.assertTrue(self.report["flag"]["exact_shared_Hermitian_54_channel_closed"])

    def test_analytic_phi_54(self) -> None:
        p, a, omega = 0.9, 0.4, 0.7
        numeric = exact.phi_54(exact.phi_singlet(p, a, omega))
        analytic = exact.analytic_phi_54_matrix(p, a, omega)
        self.assertLess(float(np.max(np.abs(numeric - analytic))), 1e-12)
        self.assertLess(abs(float(np.trace(numeric))), 1e-12)
        coefficients = exact.analytic_phi_54_coefficients(p, a, omega)
        self.assertAlmostEqual(
            6.0 * coefficients["q_color_GeV2"]
            + 4.0 * coefficients["q_weak_GeV2"],
            0.0,
            places=12,
        )

    def test_h_triplet_and_weak_coefficients(self) -> None:
        p, a, omega = 0.9, 0.4, 0.7
        coefficients = exact.analytic_phi_54_coefficients(p, a, omega)
        basis = h10.complex_pair_basis()
        for branch in ("plus", "minus"):
            for state in basis[branch][:3]:
                self.assertAlmostEqual(
                    exact.h_component_coefficient(p, a, omega, state),
                    coefficients["q_color_GeV2"],
                    places=12,
                )
            for state in basis[branch][3:]:
                self.assertAlmostEqual(
                    exact.h_component_coefficient(p, a, omega, state),
                    coefficients["q_weak_GeV2"],
                    places=12,
                )

    def test_chiral_126_hermitian_54_vanishes(self) -> None:
        identity = self.report["chiral_126_identity"]
        self.assertLess(identity["basis_max_abs_residual"], 1e-12)
        self.assertLess(identity["random_max_abs_residual"], 1e-12)
        self.assertLess(max(identity["classified_triplet_residuals"].values()), 1e-12)
        self.assertEqual(identity["consequence_PhiSigma_Hermitian_54"], "identically zero")
        self.assertEqual(identity["consequence_HSigma_Hermitian_54"], "identically zero")

    def test_scope_remains_fail_closed(self) -> None:
        closed = self.report["newly_closed_subproblem"]
        self.assertTrue(all(closed.values()))
        flags = self.report["flag"]
        self.assertTrue(flags["PhiH_54_triplet_shift_derived"])
        self.assertFalse(flags["PhiSigma_Hermitian_54_exists"])
        self.assertFalse(flags["HSigma_Hermitian_54_exists"])
        self.assertFalse(flags["all_anisotropic_channels_complete"])
        self.assertFalse(flags["physical_triplet_spectrum_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
