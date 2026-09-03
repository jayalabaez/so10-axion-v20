"""Independent polynomial products and boundary tests for the target reductions."""
import copy
from fractions import Fraction
import unittest
from unittest.mock import patch

import sympy as sp
import v103_target_section_jet_reduction_audit as audit


class TargetSectionJetReductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()
        cls.parameters = cls.report["exact_modular_recursion_checks"]["parameters_at_X_one"]

    def polynomial(self, values, prime=None):
        args = {"modulus": prime} if prime else {"domain": sp.QQ}
        return sp.Poly.from_list([sp.Rational(v.numerator, v.denominator) if isinstance(v, Fraction) else v for v in reversed(values)], audit.u, **args)

    def independent_residual(self, row):
        p, n = row["prime"], row["n"]
        z = self.polynomial(row["input_Z"], p)
        a, b = (self.polynomial(v, p) for v in audit.coefficient_vectors(self.parameters))
        t = self.polynomial([0, 1], p)
        if row["chart"] == "near_height37":
            x, y = self.polynomial(row["solved_U"], p), self.polynomial(row["input_free_W"], p)
            result = x**3+a*x*z**4+b*z**6-t*y**2
            degree = 6*n+9
        else:
            x, y = self.polynomial(row["input_free_U"], p), self.polynomial(row["solved_V"], p)
            result = y**2-x**3-t**2*a*x*z**4-t**3*b*z**6
            degree = 6*n+12
        return [int(result.nth(k)) % p for k in range(degree+1)]

    def test_canonical(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))

    def test_fresh_reconstruction(self):
        audit.validate_certificate(self.report)

    def test_both_parent_edges_bound(self):
        route, master = audit.load_inputs()
        for key, (_, core) in audit.PARENTS.items():
            self.assertEqual(self.report["input_core_hashes"][key], core)
        self.assertEqual(master["input_core_hashes"]["v102_route"], route["core_sha256"])

    def test_original_member_and_current_cubic_frontier_preserved(self):
        route, _ = audit.load_inputs()
        self.assertEqual(self.report["coefficient_payload_sha256"], route["target_height_pole_atlas"]["coefficient_payload_sha256"])
        self.assertEqual(self.report["inherited_frontier"], route["nonzero_pivot_section_elimination"]["preserved_frontier"])
        self.assertTrue(self.report["inherited_frontier"]["all_cubic_polynomial_x_sections_excluded"])

    def test_coefficient_vectors_match_original_curve(self):
        route, _ = audit.load_inputs()
        old = route["target_height_pole_atlas"]["unchanged_curve"]
        A, B = audit.parse(old["A"]), audit.parse(old["B"])
        a, b = audit.coefficient_vectors((audit.alpha, audit.beta, audit.gamma, audit.delta, audit.epsilon))
        for source, values, degree in ((A, a, 6), (B, b, 9)):
            self.assertEqual(sp.expand(audit.u**degree*source.subs(audit.T, 1/audit.u)-sum(v*audit.u**i for i, v in enumerate(values))), 0)

    def test_near_constant_pivot(self):
        x = sp.Symbol("x")
        f = x**3-432*x+3456
        self.assertEqual(f.subs(x, -24), 0)
        self.assertEqual(sp.diff(f, x).subs(x, -24), 1296)
        self.assertEqual(self.report["near_height37_reduced_system"]["constant_pivot_for_every_solved_coefficient"], 1296)

    def test_near_first_coefficient_and_resolved_component(self):
        c = self.report["original_local_model"]
        Z1, W0 = sp.symbols("z1 w0")
        actual = sp.sympify(c["near_first_solved_coefficient"], locals={**audit.SYMBOLS, "z1": Z1, "w0": W0})
        self.assertEqual(sp.expand(actual+48*Z1+9*audit.alpha-W0**2/sp.Integer(1296)), 0)
        self.assertTrue(c["near_component_condition_holds_even_when_W0_zero"])

    def test_near_target_counts_and_exhaustive_indices(self):
        row = self.report["near_height37_reduced_system"]
        self.assertEqual(row["degrees_Zhat_Ubar_W"], [17, 37, 55])
        self.assertEqual(len(set(row["free_variable_names"])), 73)
        self.assertEqual(row["free_variable_count"], 73)
        self.assertEqual(row["solved_U_coefficients"], list(range(1, 38)))
        self.assertEqual(row["remaining_coefficient_indices"], list(range(38, 112)))
        self.assertEqual(row["remaining_equation_count"], 74)

    def test_near_rational_small_case_independent_product(self):
        n = 1
        result = audit.near_reduction(n, [1, Fraction(2, 3)], [Fraction(i+1, 2) for i in range(8)], self.parameters)
        z, x, y = (self.polynomial(result[name]) for name in ("Z", "U", "W"))
        a, b = (self.polynomial(v) for v in audit.coefficient_vectors(self.parameters))
        t = self.polynomial([0, 1])
        residual = x**3+a*x*z**4+b*z**6-t*y**2
        self.assertEqual([residual.nth(i) for i in range(16)], [sp.Rational(v.numerator, v.denominator) for v in result["residual"]])
        self.assertEqual(result["residual"][:6], [0]*6)

    def test_near_zero_leading_y_not_lost(self):
        for n in (0, 1, 17):
            result = audit.near_reduction(n, [1]+[0]*n, [0]+[i+1 for i in range(3*n+4)], self.parameters, 101)
            self.assertEqual(result["W"][0], 0)
            self.assertEqual(result["residual"][:2*n+4], [0]*(2*n+4))
            self.assertEqual(len(result["tail"]), 4*n+6)

    def test_actual_near_target_independent_modular_products(self):
        for row in self.report["exact_modular_recursion_checks"]["rows"]:
            if row["chart"] == "near_height37":
                residual = self.independent_residual(row)
                cut = row["vanishing_low_residual_count"]
                self.assertEqual(residual[:cut], [0]*cut)
                self.assertEqual(residual[cut:], row["remaining_residual"])

    def test_identity_normalization_uses_no_square_root(self):
        for a in (Fraction(2, 3), Fraction(-7, 5), Fraction(1)):
            U0, V0, Z0 = a*a, a*a*a, Fraction(3, 7)
            t = V0/U0
            self.assertEqual((U0/t**2, V0/t**3), (1, 1))
            self.assertEqual((U0/t**2)/(Z0/t)**2, U0/Z0**2)
            self.assertEqual((V0/t**3)/(Z0/t)**3, V0/Z0**3)

    def test_identity_first_two_coefficients(self):
        c1, c2, z0 = sp.symbols("c1 c2 z0")
        rows = self.report["original_local_model"]["identity_first_two_solved_coefficients"]
        parsed = [sp.sympify(v, locals={"c1": c1, "c2": c2, "z0": z0}) for v in rows]
        self.assertEqual(sp.expand(parsed[0]-3*c1/2), 0)
        self.assertEqual(sp.expand(parsed[1]-(3*c2/2+3*c1*c1/8-216*z0**4)), 0)

    def test_identity_target_counts_and_exhaustive_indices(self):
        row = self.report["identity_height148_reduced_system"]
        self.assertEqual(row["degrees_Zhat_Uhat_Vhat"], [72, 148, 222])
        self.assertEqual(len(set(row["free_variable_names"])), 221)
        self.assertEqual(row["free_variable_count"], 221)
        self.assertEqual(row["solved_V_coefficients"], list(range(1, 223)))
        self.assertEqual(row["remaining_coefficient_indices"], list(range(223, 445)))
        self.assertEqual(row["remaining_equation_count"], 222)

    def test_identity_rational_small_case_independent_product(self):
        result = audit.identity_reduction(0, [Fraction(2, 3)], [1, 2, -1, 3, 4], self.parameters)
        z, x, y = (self.polynomial(result[name]) for name in ("Z", "U", "V"))
        a, b = (self.polynomial(v) for v in audit.coefficient_vectors(self.parameters))
        t = self.polynomial([0, 1])
        residual = y**2-x**3-t**2*a*x*z**4-t**3*b*z**6
        self.assertEqual([residual.nth(i) for i in range(13)], [sp.Rational(v.numerator, v.denominator) for v in result["residual"]])
        self.assertEqual(result["residual"][:7], [0]*7)

    def test_actual_identity_target_independent_modular_products(self):
        for row in self.report["exact_modular_recursion_checks"]["rows"]:
            if row["chart"] == "identity_height148":
                residual = self.independent_residual(row)
                cut = row["vanishing_low_residual_count"]
                self.assertEqual(residual[:cut], [0]*cut)
                self.assertEqual(residual[cut:], row["remaining_residual"])

    def test_every_identity_infinity_order_retained(self):
        row = self.report["identity_height148_reduced_system"]
        self.assertEqual(row["all_infinity_pole_multiplicities_retained"], list(range(73)))
        self.assertFalse(row["Z0_divided_out"])
        for sample in self.report["exact_modular_recursion_checks"]["rows"]:
            if sample["chart"] == "identity_height148":
                self.assertEqual(next(i for i, z in enumerate(sample["input_Z"]) if z), sample["O_intersection_at_infinity"])
                self.assertEqual((sample["input_free_U"][0], sample["solved_V"][0]), (1, 1))

    def test_positive_pole_divisor_can_have_polynomial_coordinates(self):
        row = self.report["identity_target_infinity_partition"]
        self.assertEqual(row["m72_polynomial_degrees_x_y"], [148, 222])
        self.assertFalse(row["a_polynomial_x_coordinate_implies_global_integrality"])
        self.assertEqual(row["height37_requires_nontrivial_finite_denominator_degree"], 17)

    def test_generic_n_degree_balance(self):
        for n in (0, 1, 17, 72):
            self.assertEqual([3*(2*n+3), 6+(2*n+3)+4*n, 9+6*n, 1+2*(3*n+4)], [6*n+9]*4)
            self.assertEqual([2*(3*n+6), 3*(2*n+4), 8+(2*n+4)+4*n, 12+6*n], [6*n+12]*4)

    def test_modular_fraction_conversion_not_truncation(self):
        norm, _ = audit.arithmetic(101)
        self.assertEqual(norm(Fraction(1, 2)), 51)
        self.assertEqual(norm(Fraction(-2, 3)), 33)
        with self.assertRaises(ValueError):
            norm(Fraction(1, 101))

    def test_bad_domains_and_shapes_rejected(self):
        for prime in (2, 3, 9, True):
            with self.assertRaises(ValueError):
                audit.arithmetic(prime)
        for n in (-1, 1.5, True):
            with self.assertRaises(ValueError):
                audit.size_check(n)
        with self.assertRaises(ValueError):
            audit.near_reduction(0, [0], [1]*5, self.parameters)
        with self.assertRaises(ValueError):
            audit.identity_reduction(0, [0], [1]*5, self.parameters)
        with self.assertRaises(ValueError):
            audit.identity_reduction(0, [1], [2]*5, self.parameters)

    def test_local_jets_and_dimension_counts_are_not_global_proofs(self):
        boundary = self.report["equivalence_and_local_global_boundary"]
        for key in ("leading_jet_solution_is_a_global_section", "coefficient_count_is_a_no_solution_proof", "finite_modular_samples_prove_original_field_solvability"):
            self.assertFalse(boundary[key])
        self.assertTrue(self.report["exact_modular_recursion_checks"]["all_example_tails_are_nonzero"])

    def test_homogeneous_primitivity_not_dropped(self):
        row = self.report["equivalence_and_local_global_boundary"]
        self.assertTrue(row["sufficiency_requires_all_tail_equations_and_homogeneous_primitivity"])
        self.assertEqual(len(row["remaining_primitivity_conditions"]), 3)

    def test_no_target_or_gate_promotion(self):
        row = self.report["terminal_decision"]
        self.assertTrue(row["two_exact_reduced_target_systems_constructed"])
        for key in ("either_target_section_constructed_or_excluded", "quartic_chart_solved_here", "actual_original_MW_rank_computed", "compact_threefold_height_realized", "theory_complete"):
            self.assertFalse(row[key])
        self.assertEqual(row["closed_gates"], [])

    def test_resealed_mathematical_or_scope_mutation_rejected(self):
        for branch, key, value in (("near_height37_reduced_system", "constant_pivot_for_every_solved_coefficient", 1295),
                                   ("terminal_decision", "theory_complete", True)):
            bad = copy.deepcopy(self.report)
            bad[branch][key] = value
            bad["core_sha256"] = audit.canonical_sha(bad)
            with self.assertRaises(RuntimeError):
                audit.validate_certificate(bad)

    def test_parent_and_fresh_source_mutations_rejected(self):
        with patch.object(audit.common, "load_bound", side_effect=RuntimeError("changed parent")):
            with self.assertRaises(RuntimeError):
                audit.build_certificate()
        with patch.object(audit, "file_sha", return_value="0"*64):
            with self.assertRaises(RuntimeError):
                audit.build_certificate()


if __name__ == "__main__":
    unittest.main()
