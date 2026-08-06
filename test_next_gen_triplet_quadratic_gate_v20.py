#!/usr/bin/env python3
from __future__ import annotations

import unittest

import numpy as np

import next_gen_triplet_nambu_hessian_v20 as nambu
import next_gen_triplet_quadratic_gate_v20 as gate


class NextGenTripletQuadraticGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = gate.build_report()

    def test_gate_executes(self) -> None:
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "PARTIAL")
        self.assertTrue(
            self.report["flag"]["authoritative_next_gen_quadratic_subgate"]
        )

    def test_exact_bterm_has_no_free_normalization(self) -> None:
        contract = self.report["authoritative_input_contract"]
        self.assertFalse(contract["free_b_hh_m2_parameter_exposed"])
        self.assertEqual(contract["B_T10_T10bar"], "kappa10 * <S> in GeV^2")
        benchmark = self.report["benchmark"]
        self.assertAlmostEqual(
            benchmark["exact_B_T10_T10bar_GeV2"]["re"], 0.04, places=14
        )
        self.assertAlmostEqual(
            benchmark["exact_B_T10_T10bar_GeV2"]["im"], 0.0, places=14
        )

    def test_authoritative_builder_inserts_exact_entry(self) -> None:
        diagonal = {name: 1.0 for name in nambu.U_BASIS + nambu.V_BASIS}
        blocks = gate.build_exact_blocks(
            p=0.9,
            a=0.4,
            omega=0.7,
            s_expectation=5.0,
            lambda4=0.05,
            mu_eta=0.3,
            kappa10=3.0,
            diagonal_m2=diagonal,
        )
        b = blocks["B_holomorphic_GeV2"]
        self.assertAlmostEqual(b[0, 0].real, 15.0, places=12)
        self.assertAlmostEqual(b[0, 0].imag, 0.0, places=12)
        self.assertAlmostEqual(abs(b[1, 1]), 0.0, places=15)
        self.assertAlmostEqual(abs(b[1, 2]), 0.0, places=15)

    def test_nambu_matrix_is_hermitian_and_conditionally_positive(self) -> None:
        benchmark = self.report["benchmark"]
        self.assertGreater(benchmark["minimum_eigenvalue_m2"], 0.0)
        self.assertGreater(min(benchmark["schur_eigenvalues_m2"]), 0.0)
        blocks = self.report["exact_blocks"]
        self.assertEqual(len(blocks["A_u_GeV2"]), 2)
        self.assertEqual(len(blocks["A_v_GeV2"]), 3)
        self.assertEqual(len(blocks["B_holomorphic_GeV2"]), 2)

    def test_closed_and_open_scope(self) -> None:
        closed = self.report["newly_closed_subproblem"]
        self.assertTrue(all(value for key, value in closed.items() if key != "kappa10_mass_dimension"))
        self.assertEqual(closed["kappa10_mass_dimension"], 1)
        flags = self.report["flag"]
        self.assertTrue(flags["exact_10h_B_term_inserted"])
        self.assertTrue(flags["exact_portal_and_cubic_blocks_inserted"])
        self.assertTrue(flags["correct_5x5_Nambu_M2_used"])
        self.assertFalse(flags["free_10h_B_normalization_remaining"])
        self.assertFalse(flags["complete_component_potential"])
        self.assertFalse(flags["physical_triplet_spectrum_complete"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])
        self.assertFalse(flags["empirical_discovery"])


if __name__ == "__main__":
    unittest.main()
