#!/usr/bin/env python3
from __future__ import annotations

import unittest

import exact_mixed_45_triplet_channel_v20 as exact
import exact_10h_squared_s_bterm_v20 as h10


class ExactMixed45TripletChannelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = exact.build_report()

    def test_gate_closes_45_subproblem(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "CLOSED_SUBPROBLEM")
        self.assertTrue(self.report["flag"]["exact_shared_Hermitian_45_channel_closed"])

    def test_analytic_phi_45(self) -> None:
        p, a, omega = 0.9, 0.4, 0.7
        numeric = exact.phi_45(exact.mixed54.phi_singlet(p, a, omega))
        analytic = exact.analytic_phi_45_form(p, a, omega)
        residual = exact.direct.tensor_norm(
            exact.direct.add_forms(numeric, exact.direct.scale_form(analytic, -1.0))
        )
        self.assertLess(residual, 1e-12)

    def test_plus_minus_10H_coefficients(self) -> None:
        p, a, omega = 0.9, 0.4, 0.7
        coefficients = exact.analytic_phi_45_coefficients(p, a, omega)
        basis = h10.complex_pair_basis()
        for state in basis["plus"][:3]:
            self.assertAlmostEqual(
                exact.h_component_coefficient(p, a, omega, state),
                coefficients["k_color_GeV2"],
                places=12,
            )
        for state in basis["minus"][:3]:
            self.assertAlmostEqual(
                exact.h_component_coefficient(p, a, omega, state),
                -coefficients["k_color_GeV2"],
                places=12,
            )

    def test_126_currents_are_rational_and_weight_degenerate(self) -> None:
        multiplets = self.report["126bar_component_currents"]
        self.assertEqual(
            set(multiplets),
            {"t2_triplet", "t2bar_antitriplet", "t4bar_antitriplet"},
        )
        for row in multiplets.values():
            self.assertLess(row["rationalization_max_abs_error"], 1e-10)
            self.assertLess(row["weight_spread"], 1e-10)
            self.assertLess(row["off_plane_leakage"], 1e-10)

    def test_vector_family_is_complete_but_full_model_is_not(self) -> None:
        h_result = self.report["H10_component_result"]
        self.assertTrue(h_result["210dag210_10dag10_Hermitian_family_complete"])
        flags = self.report["flag"]
        self.assertTrue(flags["PhiH_Hermitian_channel_family_complete"])
        self.assertTrue(flags["PhiSigma_45_triplet_coefficients_derived"])
        self.assertFalse(flags["all_PhiSigma_anisotropic_channels_complete"])
        self.assertFalse(flags["physical_triplet_spectrum_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
