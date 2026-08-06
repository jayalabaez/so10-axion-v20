#!/usr/bin/env python3
from __future__ import annotations

import math
import unittest

import numpy as np

import next_gen_triplet_nambu_hessian_v20 as nambu


class NextGenTripletNambuHessianTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = nambu.build_report()

    def test_gate_executes(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "PARTIAL")

    def test_nambu_architecture_and_hermiticity(self) -> None:
        self.assertEqual(len(self.report["basis"]["nambu_Y_minus_1_over_3"]), 5)
        self.assertLess(
            self.report["numerical_invariants"]["hermiticity_max_abs"], 1e-12
        )
        self.assertTrue(
            self.report["flag"]["correct_nambu_doubled_triplet_M2_architecture"]
        )

    def test_exact_clebsch_slots(self) -> None:
        root3 = math.sqrt(3.0)
        cg = nambu.exact_clebsch_values(p=0.9, a=0.4, omega=0.7)
        self.assertAlmostEqual(
            cg["portal_H10_t2bar_GeV"], 0.9 + 0.4 / root3, places=12
        )
        self.assertAlmostEqual(
            cg["portal_H10_t4bar_GeV"], 1.4 / root3, places=12
        )
        self.assertAlmostEqual(
            cg["portal_t2_H10bar_GeV"], 0.9 - 0.4 / root3, places=12
        )
        self.assertAlmostEqual(
            cg["cubic_t4bar_diagonal_GeV"], 1.8 + 0.8 / root3, places=12
        )
        self.assertAlmostEqual(
            cg["cubic_t2bar_t4bar_GeV"], 2.8 / root3, places=12
        )

    def test_forbidden_holomorphic_entries_are_zero(self) -> None:
        diagonal = {name: 1.0 for name in nambu.U_BASIS + nambu.V_BASIS}
        blocks = nambu.build_blocks(
            p=0.9,
            a=0.4,
            omega=0.7,
            v_s=0.2,
            lambda4=0.05,
            mu_eta=0.3,
            b_hh_m2=0.04,
            diagonal_m2=diagonal,
        )
        b = blocks["B_holomorphic_GeV2"]
        self.assertEqual(b.shape, (2, 3))
        self.assertAlmostEqual(abs(b[1, 1]), 0.0, places=15)
        self.assertAlmostEqual(abs(b[1, 2]), 0.0, places=15)
        self.assertIn("SO10_FORBIDDEN", blocks["operator_provenance"]["B_11"])
        self.assertIn("SO10_FORBIDDEN", blocks["operator_provenance"]["B_12"])

    def test_rephasing_decoupling_and_schur(self) -> None:
        invariants = self.report["numerical_invariants"]
        self.assertLess(invariants["rephasing_eigenvalue_residual"], 1e-12)
        self.assertLess(invariants["decoupling_eigenvalue_residual"], 1e-12)
        benchmark = self.report["algebra_benchmark"]
        self.assertGreater(benchmark["minimum_eigenvalue_m2"], 0.0)
        self.assertGreater(min(benchmark["schur_eigenvalues_m2"]), 0.0)

    def test_input_contracts_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            nambu.build_blocks(
                p=1.0,
                a=0.0,
                omega=0.0,
                v_s=1.0,
                lambda4=0.0,
                mu_eta=0.0,
                b_hh_m2=0.0,
                diagonal_m2={"T10_Ym13": 1.0},
            )
        diagonal = {name: 1.0 for name in nambu.U_BASIS + nambu.V_BASIS}
        with self.assertRaises(ValueError):
            nambu.build_blocks(
                p=1.0,
                a=0.0,
                omega=0.0,
                v_s=1.0,
                lambda4=0.0,
                mu_eta=1j,
                b_hh_m2=0.0,
                diagonal_m2=diagonal,
            )
        with self.assertRaises(ValueError):
            nambu.nambu_matrix_from_blocks(
                np.eye(3), np.eye(3), np.zeros((2, 3))
            )

    def test_dimensional_and_claim_scope(self) -> None:
        dimensional = self.report["dimensional_contract"]
        self.assertEqual(dimensional["lambda4"], "dimensionless")
        self.assertEqual(dimensional["mu_eta"], "GeV")
        self.assertEqual(dimensional["mu_eta_times_210_VEV"], "GeV^2")
        flags = self.report["flag"]
        self.assertFalse(flags["legacy_dimension_one_4x4_used"])
        self.assertFalse(flags["complete_component_potential"])
        self.assertFalse(flags["physical_triplet_spectrum_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
