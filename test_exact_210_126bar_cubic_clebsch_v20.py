#!/usr/bin/env python3
from __future__ import annotations

import math
import unittest

import exact_210_126bar_cubic_clebsch_v20 as cubic


class Exact210126barCubicClebschTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = cubic.build_report()

    def test_gate_executes(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "PARTIAL")

    def test_so10_invariance_and_hermiticity(self) -> None:
        self.assertLess(self.report["so10_invariance_max_residual"], 1e-10)
        sector = self.report["sector_matrices_cartesian"]
        self.assertLess(sector["maximum_hermiticity_residual"], 1e-10)
        self.assertLess(sector["maximum_color_weight_spread"], 1e-10)

    def test_exact_cartesian_matrices(self) -> None:
        root3 = math.sqrt(3.0)
        matrices = self.report["sector_matrices_cartesian"]["antitriplet_sector"]
        self.assertAlmostEqual(matrices["p"]["matrix"][0][0], 0.0, places=10)
        self.assertAlmostEqual(matrices["p"]["matrix"][0][1], 0.0, places=10)
        self.assertAlmostEqual(matrices["p"]["matrix"][1][0], 0.0, places=10)
        self.assertAlmostEqual(matrices["p"]["matrix"][1][1], 2.0, places=10)
        self.assertAlmostEqual(matrices["a"]["matrix"][1][1], 2.0 / root3, places=10)
        self.assertAlmostEqual(
            matrices["omega"]["matrix"][0][1], 4.0 / root3, places=10
        )
        self.assertAlmostEqual(
            matrices["omega"]["matrix"][1][0], 4.0 / root3, places=10
        )

    def test_t2_triplet_zero_for_this_operator(self) -> None:
        self.assertLess(
            self.report["sector_matrices_cartesian"]["maximum_t2_triplet_entry"],
            1e-10,
        )

    def test_dimension_and_scope(self) -> None:
        operator = self.report["operator"]
        self.assertEqual(operator["coefficient_mass_dimension"], 1)
        flags = self.report["flag"]
        self.assertTrue(flags["exact_210_126bar_cubic_contraction_derived"])
        self.assertTrue(flags["t4bar_diagonal_clebsch_derived"])
        self.assertTrue(flags["t2bar_t4bar_mixing_clebsch_derived"])
        self.assertFalse(flags["uses_susy_mass_matrix_as_nonsusy_scalar_m2"])
        self.assertFalse(flags["full_component_CG_complete"])
        self.assertFalse(flags["physical_triplet_spectrum_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
