#!/usr/bin/env python3
from __future__ import annotations

import math
import unittest

import exact_126bar_triplet_clebsch_v20 as physics


class Exact126barTripletClebschTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = physics.build_report()

    def test_gate_executes(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "PARTIAL")

    def test_exact_weight_multiplicities(self) -> None:
        counts = self.report["derived_multiplicities"]
        self.assertEqual(counts["t2_triplet_3_1_minus_third"], 3)
        self.assertEqual(counts["t2bar_antitriplet_3bar_1_plus_third"], 3)
        self.assertEqual(counts["t4bar_antitriplet_3bar_1_plus_third"], 3)
        self.assertEqual(counts["sm_singlet"], 1)

    def test_canonical_kinetic_normalization(self) -> None:
        kinetic = self.report["kinetic_normalization"]
        self.assertTrue(kinetic["derived"])
        self.assertLess(kinetic["gram_max_abs_residual"], 1.0e-10)

    def test_direct_portal_clebsches(self) -> None:
        root3 = math.sqrt(3.0)
        portal = self.report["portal_clebsches"]
        minus = portal["Hbar10_from_t2_triplet"]["coefficients_cartesian"]
        plus = portal["H10_from_t2bar_antitriplet"]["coefficients_cartesian"]
        t4 = portal["H10_from_t4bar_antitriplet"]["coefficients_cartesian"]
        self.assertAlmostEqual(minus["p"], 1.0, places=10)
        self.assertAlmostEqual(minus["a"], -1.0 / root3, places=10)
        self.assertAlmostEqual(minus["omega"], 0.0, places=10)
        self.assertAlmostEqual(plus["p"], 1.0, places=10)
        self.assertAlmostEqual(plus["a"], 1.0 / root3, places=10)
        self.assertAlmostEqual(plus["omega"], 0.0, places=10)
        self.assertAlmostEqual(t4["p"], 0.0, places=10)
        self.assertAlmostEqual(t4["a"], 0.0, places=10)
        self.assertAlmostEqual(t4["omega"], 2.0 / root3, places=10)

    def test_singular_values_reconstructed(self) -> None:
        reconstruction = self.report["singular_value_reconstruction"]
        self.assertAlmostEqual(
            reconstruction["color_minus_reconstructed"],
            reconstruction["color_minus_analytic"],
            places=10,
        )
        self.assertAlmostEqual(
            reconstruction["color_plus_reconstructed"],
            reconstruction["color_plus_analytic"],
            places=10,
        )

    def test_chirality_convention_is_fail_closed(self) -> None:
        audit = self.report["chirality_convention_audit"]
        self.assertEqual(audit["current_direct_basis_hodge_eigenvalue"], "-i")
        self.assertEqual(audit["branching_basis_hodge_eigenvalue"], "+i")
        self.assertTrue(audit["basis_independent_singular_spectrum_preserved"])
        self.assertTrue(
            audit["component_labels_require_one_consistent_chirality_convention"]
        )

    def test_legacy_four_state_matrix_rejected(self) -> None:
        sectors = self.report["corrected_nonsusy_charge_sectors"]
        self.assertFalse(sectors["historical_symmetric_4x4_single_sector_valid"])
        self.assertFalse(
            self.report["flag"]["legacy_symmetric_4x4_charge_sector_valid"]
        )

    def test_no_full_spectrum_or_model_claim(self) -> None:
        flags = self.report["flag"]
        self.assertFalse(flags["full_diagonal_component_CG_complete"])
        self.assertFalse(flags["physical_triplet_spectrum_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
