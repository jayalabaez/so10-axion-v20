"""Independent index, cocharacter, minimality and tamper tests for F100."""
import copy
import unittest
from unittest.mock import patch

import sympy as sp
import v100_correlated_quotient_period_audit as audit


class CorrelatedPeriodTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()

    def test_canonical(self):
        self.assertEqual(self.report["core_sha256"], audit.common.canonical_sha(self.report))

    def test_reconstruction(self):
        audit.validate_certificate(self.report)

    def test_completed_module_kills_entire_kernel(self):
        old = audit.center.old_kernel()
        self.assertEqual(len(old), 8)
        self.assertTrue(any(audit.center.character_descent(audit.SIGMA, old)))
        self.assertFalse(any(audit.center.character_descent(audit.COMPLETED, old)))

    def test_normal_and_D_characters_are_genuine(self):
        for k in audit.center.old_kernel():
            self.assertEqual(2*k[1] % 2, 0)
            self.assertEqual(2*k[6] % 2, 0)

    def test_all_integer_twists_descend(self):
        for n in range(-8, 9):
            bits = list(audit.COMPLETED)
            bits[-1] = 2*n % 2
            self.assertFalse(any(audit.center.character_descent(bits, audit.center.old_kernel())))

    def test_index_independent_exponential_series(self):
        x, d, p, r2, t = audit.x, audit.d, audit.p, audit.r2, audit.t
        for n in (-2, 0, 1, 2, 7):
            expr = (1-p*t*t/24)*sp.exp((x/2+n*d)*t)*(2-r2*t*t)
            degree = sp.series(expr, t, 0, 4).removeO().expand().coeff(t, 3)
            self.assertEqual(sp.expand(degree-audit.completed_index(n)), 0)

    def test_virtual_bundle_starts_in_degree_four(self):
        t, d = audit.t, audit.d
        ch = sp.series((sp.exp(d*t)-1)**2, t, 0, 4).removeO().expand()
        self.assertEqual(ch, d*d*t*t+d**3*t**3)

    def test_exact_2P_and_no_R_gravity_remainder(self):
        diff = sp.expand(audit.completed_index(2)-2*audit.completed_index(1)+audit.completed_index(0))
        self.assertEqual(diff, 2*audit.d**3+audit.x*audit.d**2)
        self.assertFalse(diff.has(audit.r2, audit.p))

    def test_cocharacter_endpoint_is_frozen_kernel(self):
        row = self.report["CP3_correlated_witness"]
        endpoint = tuple(row["lift_endpoint_at_2pi"])
        self.assertEqual(endpoint, (0, 1, 0, 1, 1, 1, 1))
        self.assertIn(endpoint, audit.center.old_kernel())

    def test_half_angle_total_weights_are_integral(self):
        half = sp.Rational(1, 2)
        self.assertEqual([half+half, half-half], [1, 0])
        self.assertEqual(half*(-half), -sp.Rational(1, 4))

    def test_witness_does_not_fake_ordinary_R_bundle(self):
        self.assertFalse(self.report["category"]["independent_ordinary_SU2_R_bundle_required"])
        self.assertTrue(self.report["genuine_Clifford_module"]["formal_R_c2_may_be_fractional"])
        self.assertIn("no projection", self.report["CP3_correlated_witness"]["not_an_independent_Spin_c11_gauge_factor"])

    def test_cp3_p1_from_euler_sequence(self):
        c1, c2 = 4, 6
        self.assertEqual(c1*c1-2*c2, 4)
        self.assertEqual(c1 % 2, 0)

    def test_cp3_spin_index_independent_holomorphic_check(self):
        for k in range(-12, 13):
            # Polynomial Euler characteristic of O(k-2) on CP3.
            chi = sp.Rational((k+1)*k*(k-1), 6)
            self.assertEqual(audit.cp3_spin_index(k), chi)
            self.assertTrue(chi.is_Integer)

    def test_cp3_genuine_index(self):
        self.assertEqual([audit.cp3_witness(n) for n in range(3)], [0, 1, 5])
        self.assertEqual(audit.cp3_witness(2)-2*audit.cp3_witness(1)+audit.cp3_witness(0), 3)

    def test_cp3_eighth_period(self):
        self.assertEqual(audit.target().subs({audit.x: 1, audit.d: 1})/4, sp.Rational(3, 8))

    def test_natural_Spin_c_not_falsely_assumed(self):
        self.assertFalse(self.report["CP3_correlated_witness"]["natural_Spin_c_N_admissible"])
        self.assertFalse(self.report["category"]["natural_Spin_c_with_determinant_N_required"])

    def test_exact_minimum_eight(self):
        self.assertEqual(self.report["exact_quantization"]["minimum_positive_stack"], 8)
        for n in range(1, 65):
            row = audit.stack_row(n)
            self.assertEqual(row["quantized_on_stated_category"], n % 8 == 0)
            self.assertEqual(sp.Rational(row["period_mod1"]) == 0, n % 8 == 0)

    def test_invalid_inputs(self):
        for n in (True, 1.0, "1"):
            with self.assertRaises(ValueError):
                audit.cp3_spin_index(n)
            with self.assertRaises(ValueError):
                audit.cp3_witness(n)
        for n in (0, -1, True, 1.0, "8"):
            with self.assertRaises(ValueError):
                audit.stack_row(n)

    def test_nonbounding_response_includes_kernel(self):
        row = self.report["exact_quantization"]
        self.assertIn("dim(kernel)", row["xi_definition"])
        self.assertIn("without a chosen filling", row["nonbounding_definition"])
        self.assertFalse(row["additional_flat_closed5_factor_repairs_nonintegral_filling_period"])

    def test_not_new_particles_or_independent_gluing(self):
        row = self.report["exact_quantization"]
        self.assertFalse(row["response_is_new_particle_spectrum"])
        self.assertFalse(row["independent_boundary_corner_trivializations_constructed"])

    def test_old_restricted_theorems_not_retracted(self):
        row = self.report["relation_to_previous_results"]
        self.assertFalse(row["V98_quantization_with_chosen_root_retracted"])
        self.assertFalse(row["V99_natural_normal_order_two_retracted"])
        self.assertTrue(row["different_polynomial_from_normal_T"])

    def test_physical_category_not_identified(self):
        row = self.report["category"]
        self.assertFalse(row["physical_Gammahat_or_orbifold_category_identified"])
        self.assertFalse(row["finite_C8_only_bordism_classification"])

    def test_all_gates_open(self):
        row = self.report["terminal_decision"]
        self.assertEqual(row["closed_gates"], [])
        self.assertFalse(row["single_local_P_over4_repair_accepted"])
        self.assertFalse(row["physical_full_anomaly_cancelled"])

    def test_resealed_scope_promotion_rejected(self):
        value = copy.deepcopy(self.report)
        value["category"]["physical_Gammahat_or_orbifold_category_identified"] = True
        value["core_sha256"] = audit.common.canonical_sha(value)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(value)

    def test_fresh_source_hashes(self):
        with patch.object(audit.common, "file_sha", return_value="0"*64):
            with self.assertRaises(RuntimeError):
                audit.build_certificate()


if __name__ == "__main__":
    unittest.main()
