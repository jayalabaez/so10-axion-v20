"""Independent polynomial, characteristic-number and scope tests for F99."""
import copy
import unittest
from unittest.mock import patch

import sympy as sp
import v99_normal_half_period_pairing_audit as audit


class NormalHalfPeriodPairingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()

    def test_core_canonical(self):
        self.assertEqual(self.report["core_sha256"], audit.common.canonical_sha(self.report))

    def test_reconstruction(self):
        audit.validate_certificate(self.report)

    def test_independent_index_series(self):
        t, x, p, z = sp.symbols("t x p z")
        value = sp.series((1-p*t*t/24)*sp.exp((z+x/2)*t), t, 0, 4).removeO().coeff(t, 3)
        self.assertEqual(sp.expand(value-audit.spin_c_index(z)), 0)

    def test_doubled_normal_identity(self):
        x, p, e2 = audit.x, audit.p, audit.e2
        base = x**3/48-x*p/48
        twisted = 9*x**3/16-x*p/16
        target = -x*e2/2+x**3/8+x*p/8
        self.assertEqual(sp.expand(twisted-15*base-x*e2-2*target), 0)

    def test_even_cubic_period_index_proof(self):
        self.assertEqual(sp.expand(audit.spin_c_index(audit.x)-3*audit.spin_c_index(0)), audit.x**3/2)
        self.assertFalse(self.report["closed6_order_two_obstruction"]["x_cubed_half_is_claimed_integral_universal_cohomology_class"])

    def test_parity_formula_differs_by_even_index(self):
        row = self.report["closed6_order_two_obstruction"]
        self.assertEqual(sp.expand(sp.sympify(row["difference_of_parity_formulas"])+12*audit.spin_c_index(0)), 0)

    def test_CP2_CP1_primitive_half_witness(self):
        self.assertEqual(audit.cp2_cp1_period(audit.normal_target()), sp.Rational(3, 2))
        self.assertEqual(audit.cp2_cp1_period(audit.spin_c_index(0)), 0)
        self.assertEqual(audit.cp2_cp1_period(audit.spin_c_index(audit.x)), 3)

    def test_many_independent_holomorphic_checks(self):
        for r in range(-3, 4):
            for s in range(-3, 4):
                nh, nj = 2*r+1, 2*s
                # Twist canonical determinant(3,2) by O(r-1,s-1).
                chi = lambda k, l: sp.Rational((k+1)*(k+2)*(l+1), 2)
                self.assertEqual(audit.cp2_cp1_period(audit.spin_c_index(0), nh, nj), chi(r-1, s-1))
                self.assertEqual(audit.cp2_cp1_period(audit.spin_c_index(audit.x), nh, nj), chi(3*r, 3*s-1))

    def test_invalid_normal_determinants_rejected(self):
        for args in ((0, 2), (2, 0), (1, 1), (True, 2), (1, 2.0)):
            with self.assertRaises(ValueError):
                audit.cp2_cp1_period(audit.normal_target(), *args)

    def test_exact_order_and_stack_classification(self):
        self.assertEqual(self.report["closed6_order_two_obstruction"]["exact_order"], 2)
        for n in range(1, 25):
            row = audit.multiplicity_row(n)
            self.assertEqual(row["all_natural_Spin_c_periods_integral"], n % 2 == 0)
            self.assertEqual(row["witness_phase"], "+1" if n % 2 == 0 else "-1")

    def test_invalid_stacks_rejected(self):
        for n in (0, -1, 1.5, "2", True):
            with self.assertRaises(ValueError):
                audit.multiplicity_row(n)

    def test_split_E_is_genuine_and_changes_parity(self):
        roots = [audit.h, audit.j, 0, 0, 0]
        second = sum(roots[i]*roots[j] for i in range(5) for j in range(i+1, 5))
        self.assertEqual(second, audit.h*audit.j)
        self.assertEqual(audit.cp2_cp1_period(audit.normal_target(), second=second), 1)

    def test_reflected_chern_classes_from_five_roots(self):
        r = sp.symbols("r0:5")
        second = lambda roots: sum(roots[i]*roots[j] for i in range(5) for j in range(i+1, 5))
        reflected = list(r[:2])+[-v for v in r[2:]]
        lhs = second(r)+second(reflected)
        rhs = 2*(r[0]*r[1]+r[2]*r[3]+r[2]*r[4]+r[3]*r[4])
        self.assertEqual(sp.expand(lhs-rhs), 0)

    def test_common_pair_polynomial(self):
        row = self.report["shared_reflected_U5_pair"]
        actual = sp.sympify(row["target_T0_plus_T1"])
        expected = audit.x**3/4+audit.x*audit.p/4-audit.x*(audit.A2+audit.B2)
        self.assertEqual(sp.expand(actual-expected), 0)

    def test_pair_indices_and_cup_are_integral(self):
        row = self.report["shared_reflected_U5_pair"]
        self.assertEqual(row["integer_eta_levels"], {"N": 1, "1": -15})
        self.assertEqual(row["integral_cup"], "-x*(c2(A)+c2(B))")
        self.assertTrue(row["quantized_on_all_stated_common_closed5_backgrounds"])

    def test_pair_is_not_independent_wall_factorization(self):
        row = self.report["shared_reflected_U5_pair"]
        self.assertEqual(row["obstruction_character_product_on_shared_closed6"], "+1")
        self.assertEqual(row["independent_endpoint_obstruction_phase"], "-1")
        self.assertFalse(row["factors_into_two_absolute_natural_Spin_c_T_responses"])

    def test_nonbounding_response_and_eta_kernel_retained(self):
        row = self.report["exact_normal_period_lattice"]
        self.assertIn("dim(kernel)", row["xi_definition"])
        self.assertIn("no chosen filling", row["nonbounding_closed5_definition"])
        self.assertFalse(row["T_has_absolute_closed5_response_on_all_these_backgrounds"])

    def test_no_normal_root_or_full_Gammahat_assumed(self):
        row = self.report["restricted_category"]
        self.assertFalse(row["normal_root_M_assumed"])
        self.assertFalse(row["full_frozen_Gammahat_category_identified"])
        self.assertFalse(self.report["shared_reflected_U5_pair"]["bare_Spin_c_eta_operators_descend_through_full_internal_kernel"])

    def test_individual_eta_kernel_obstruction(self):
        row = self.report["shared_reflected_U5_pair"]
        self.assertEqual(row["bare_eta_center_bits"], [1, 1, 0, 0, 0, 0, 0])
        self.assertEqual(row["bare_eta_known_kernel_exponents"], {"D_geom": 0, "krot_N": 1, "krot_T": 1, "kspin": 0})
        self.assertIn("alone is not", row["operator_scope"])

    def test_flat_factor_does_not_fix_period(self):
        self.assertFalse(self.report["closed6_order_two_obstruction"]["a_flat_closed5_factor_can_repair_this_filling_period"])
        self.assertFalse(self.report["closed6_order_two_obstruction"]["relative_bulk_boundary_theory_constructed"])

    def test_gauge_quarter_does_not_cancel_normal(self):
        row = self.report["separate_obstructions_retained"]
        self.assertEqual(row["gauge_quarter_at_C_trivial"], "0")
        self.assertFalse(row["gauge_quarter_removes_normal_half_period"])

    def test_SU2_shared_vs_independent_sign(self):
        row = self.report["separate_obstructions_retained"]
        self.assertEqual(row["ordinary_spin_product_SU2_normal_doublet_phase"], "-1")
        self.assertEqual(row["two_normal_doublets_on_shared_R_have_product_phase"], "+1")
        self.assertEqual(row["independent_R_endpoint_test_product_phase"], "-1")
        self.assertFalse(row["bare_parent_R_phase_computed"])

    def test_no_particle_or_gate_promotion(self):
        row = self.report["terminal_decision"]
        self.assertEqual(row["closed_gates"], [])
        self.assertFalse(row["full_quantum_Gammahat_parent_accepted"])
        self.assertFalse(self.report["shared_reflected_U5_pair"]["common_response_is_new_particles_or_SUSY_multiplets"])

    def test_resealed_false_claim_rejected(self):
        value = copy.deepcopy(self.report)
        value["terminal_decision"]["full_quantum_Gammahat_parent_accepted"] = True
        value["core_sha256"] = audit.common.canonical_sha(value)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(value)

    def test_fresh_source_hash_rechecked(self):
        with patch.object(audit.common, "file_sha", return_value="0"*64):
            with self.assertRaises(RuntimeError):
                audit.build_certificate()


if __name__ == "__main__":
    unittest.main()
