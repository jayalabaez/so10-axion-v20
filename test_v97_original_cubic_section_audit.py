import copy
import json
import unittest
from unittest.mock import patch

import sympy as sp

import v97_original_cubic_section_audit as audit


def determinant_mod(matrix, prime):
    """Independent Gaussian determinant, without Sympy's resultant routine."""
    values = [[int(v) % prime for v in row] for row in matrix]
    result = 1
    for col in range(len(values)):
        pivot = next((r for r in range(col, len(values)) if values[r][col]), None)
        if pivot is None:
            return 0
        if pivot != col:
            values[col], values[pivot] = values[pivot], values[col]
            result = -result
        diagonal = values[col][col]
        result = result*diagonal % prime
        inverse = pow(diagonal, -1, prime)
        for row in range(col+1, len(values)):
            factor = values[row][col]*inverse % prime
            values[row] = [(a-factor*b) % prime for a, b in zip(values[row], values[col])]
    return result % prime


class OriginalCubicSectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()
        cls.universal = audit.universal_algebra()
        cls.values = {key: value.subs(audit.X, 1) for key, value in audit.compressed_coefficients().items()}

    def test_canonical_lineage_and_roundtrip(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        self.assertEqual(self.report, json.loads(json.dumps(self.report)))
        self.assertEqual(self.report["input_core_hashes"], {
            "v96_route": audit.V96_ROUTE_CORE, "v96_master": audit.V96_MASTER_CORE,
            "v96_geometry": audit.V96_GEOMETRY_CORE})
        audit.validate_certificate(self.report)

    def test_original_model_is_exactly_the_frozen_Jacobian(self):
        model = audit.previous.previous.generic_ruling_model(self.report["coefficient_payload"])
        T, X = audit.T, audit.X
        a = T**3+(X**3+X)*T**2+X**11+2*X
        b = (X**4+2)*T**2+X**12+1
        c = -2*T**3
        e = T**3+2*X**11+3*X
        self.assertEqual(sp.expand(model["affine"]["A"]+27*(12*a*e+c*c)), 0)
        self.assertEqual(sp.expand(model["affine"]["B"]+27*(72*a*c*e-27*b*b*e-2*c**3)), 0)

    def test_coordinate_change_is_an_identity_not_a_twist(self):
        a, b, c, e, s, w = sp.symbols("a b c e s w")
        I, J = 12*a*e+c*c, 72*a*c*e-27*b*b*e-2*c**3
        x, y = 9*s-6*c, 27*w
        short = y*y-x**3+27*I*x+27*J
        resolvent = w*w-s*(s-c)**2+4*a*e*s-b*b*e
        self.assertEqual(sp.expand(short-729*resolvent), 0)
        data = self.report["original_model_and_coordinate_change"]["coordinate_identity"]
        self.assertEqual(data["short_Weierstrass_residual_over_resolvent_residual"], 729)
        self.assertFalse(data["birational_twist_or_field_extension_used"])

    def test_symbol_parser_does_not_confuse_beta_gamma_with_special_functions(self):
        self.assertEqual(audit.parse("beta**2+gamma"), audit.beta**2+audit.gamma)

    def test_linear_solver_rejects_nonlinear_or_changed_pivot(self):
        q = audit.q
        self.assertEqual(audit.solve_linear(3*q-6, q, 3), 2)
        for expression, pivot in ((q*q+3*q, 3), (q**3+3*q, 3), (3*q-6, 4)):
            with self.assertRaises(RuntimeError):
                audit.solve_linear(expression, q, pivot)

    def test_square_variable_reduction_rejects_odd_powers(self):
        h, z = audit.h, audit.z
        self.assertEqual(audit.even_polynomial(h**4+3*h*h+2, h, z).as_expr(), z*z+3*z+2)
        with self.assertRaises(RuntimeError):
            audit.even_polynomial(h**3+1, h, z)

    def test_h_zero_and_nonzero_split_is_explicit(self):
        lower = self.report["b4_zero_subbranch_exclusion"]
        self.assertIn("h=0 or h!=0", lower["split_is_exhaustive"])
        self.assertIn("Only the leading-minus-24", lower["branch_and_field_scope"])
        self.assertIn("leading-plus-12 exclusion is over C(X), not its algebraic closure", lower["branch_and_field_scope"])
        self.assertFalse(lower["h_zero"]["section_exists"])
        self.assertFalse(lower["h_nonzero"]["section_exists_over_algebraic_closure_C_X"])
        self.assertTrue(lower["entire_b4_zero_branch_excluded_over_algebraic_closure_C_X"])

    def test_lower_y_q_p_and_h_zero_obstruction_independently(self):
        A, B, C, D, E = audit.PARAMETERS
        h = audit.h
        lower = self.universal["lower"]
        solved = lower["solved_coefficients"]
        self.assertEqual(sp.expand(audit.parse(solved["q"])-(A*A/4-B*B/16)), 0)
        self.assertEqual(sp.expand(audit.parse(solved["p"])-(h*h-A**3/8+3*A*B*B/64-C-E)), 0)
        expected = (40*A**4-20*A*A*B*B+256*A*C-256*A*E+B**4-64*B*D)/32
        self.assertEqual(sp.expand(audit.parse(lower["h_zero_equation"])-expected), 0)
        self.assertEqual(expected.subs(self.values), -sp.Rational(1407, 32))

    def test_lower_univariate_numerators_reconstruct_original_short_equation(self):
        # Derive independently from the original Weierstrass model at X=1.
        T, h, q, p, K, L, M = audit.T, audit.h, audit.q, audit.p, audit.K, audit.L, audit.M
        model = audit.previous.previous.generic_ruling_model(self.report["coefficient_payload"])
        A, B = [model["affine"][key].subs(audit.X, 1) for key in ("A", "B")]
        x = -24*T**3-18*T*T+9*q*T+9*p
        y = 108*(h*T**3+K*T*T+L*T+M)
        F = sp.Poly(sp.expand((y*y-x**3-A*x-B)/729), T)
        solutions = {sp.Symbol(key): audit.parse(value).subs(self.values)
                     for key, value in self.universal["lower"]["solved_coefficients"].items()}
        for degree in range(7, 2, -1):
            self.assertEqual(sp.expand(F.nth(degree).subs(solutions)), 0)
        saved = self.report["b4_zero_subbranch_exclusion"]["h_nonzero"]
        for degree, power, coefficients in zip((2, 1, 0), (6, 8, 10), saved["primitive_integer_polynomials_at_X_one_coefficients_descending"]):
            expr = sp.expand(F.nth(degree).subs(solutions)*h**power)
            polynomial = sp.Poly(expr, h, domain=sp.QQ)
            self.assertTrue(all(index[0] % 2 == 0 for index, _ in polynomial.terms()))
            in_z = sp.Poly(sum(coef*audit.z**(index[0]//2) for index, coef in polynomial.terms()), audit.z, domain=sp.QQ)
            integer = in_z.clear_denoms()[1].primitive()[1]
            self.assertEqual([int(v) for v in integer.all_coeffs()], coefficients)

    def test_degrees_survive_both_specializations(self):
        data = self.report["b4_zero_subbranch_exclusion"]["h_nonzero"]
        self.assertEqual(data["generic_degrees_z"], [4, 6, 7])
        self.assertEqual(data["specialized_degrees_z"], [4, 6, 7])
        self.assertEqual(data["modular_degrees_z"], [4, 6, 7])
        for expression, degree in zip(data["numerators_in_z_h_squared"], (4, 6, 7)):
            poly = sp.Poly(audit.parse(expression), audit.z)
            self.assertEqual(poly.degree(), degree)
            self.assertNotEqual(poly.LC().subs(self.values), 0)
            self.assertTrue(all(coef.is_polynomial(*audit.PARAMETERS) for coef in poly.all_coeffs()))

    def test_modular_resultant_has_independent_sylvester_determinant_witness(self):
        data = self.report["b4_zero_subbranch_exclusion"]["h_nonzero"]
        first, second = data["modular_polynomials_coefficients_descending"][:2]
        n, m = len(first)-1, len(second)-1
        matrix = [[0]*shift+first+[0]*(m-1-shift) for shift in range(m)]
        matrix += [[0]*shift+second+[0]*(n-1-shift) for shift in range(n)]
        self.assertEqual(len(matrix), 10)
        self.assertTrue(all(len(row) == 10 for row in matrix))
        self.assertEqual(determinant_mod(matrix, 101), 37)
        self.assertEqual(data["first_two_resultant_mod_prime"], 37)

    def test_exact_specialized_gcd_and_generic_scope(self):
        data = self.report["b4_zero_subbranch_exclusion"]["h_nonzero"]
        first, second = [sp.Poly.from_list(v, gens=audit.z, domain=sp.QQ)
                         for v in data["primitive_integer_polynomials_at_X_one_coefficients_descending"][:2]]
        self.assertEqual(sp.gcd(first, second).monic().as_expr(), 1)
        self.assertTrue(data["generic_resultant_nonzero"])
        proof = " ".join(data["generic_resultant_proof"])
        self.assertIn("does not specialize a point", proof)
        self.assertIn("Sylvester determinant", proof)
        self.assertFalse(data["section_exists_over_algebraic_closure_C_X"])

    def test_remaining_system_has_three_unknowns_and_four_equations(self):
        data = self.report["remaining_nonzero_b4_system"]
        self.assertEqual(data["unknowns_over_C_X"], ["z", "H", "K"])
        self.assertEqual(data["equation_count"], 4)
        self.assertEqual(data["clearing_z_powers"], [0, 1, 1, 1])
        self.assertEqual(data["degrees_in_z_H_K"], [[6, 4, 2], [8, 4, 3], [9, 5, 3], [10, 6, 4]])
        self.assertEqual(data["reduced_equation_list_sha256"], audit.canonical_sha(data["reduced_equations_T3_through_T0"]))

    def test_remaining_elimination_and_reconstruction_are_exact(self):
        data = self.universal["remaining"]
        solutions = {sp.Symbol(key): audit.parse(value) for key, value in data["solved_coefficients"].items()}
        equations = [audit.parse(v) for v in data["equations_T7_through_T0"]]
        for equation in equations[:4]:
            self.assertEqual(sp.expand(equation.subs(solutions)), 0)
        for equation, power, reduced in zip(equations[4:], data["clearing_z_powers"], data["reduced_equations_T3_through_T0"]):
            self.assertEqual(sp.expand(equation.subs(solutions)*audit.z**power-audit.parse(reduced)), 0)
        for key in ("q", "p"):
            self.assertTrue(audit.parse(data["solved_coefficients"][key]).is_polynomial(audit.z, audit.H, audit.K, *audit.PARAMETERS))
        for key in ("L", "M"):
            self.assertTrue(sp.expand(audit.z*audit.parse(data["solved_coefficients"][key])).is_polynomial(audit.z, audit.H, audit.K, *audit.PARAMETERS))

    def test_remaining_normalization_against_original_short_model(self):
        T, z, H, K, L, M, q, p = audit.T, audit.z, audit.H, audit.K, audit.L, audit.M, audit.q, audit.p
        r = sp.Symbol("r")
        model = audit.previous.previous.generic_ruling_model(self.report["coefficient_payload"])
        A, B = [model["affine"][key].subs(audit.X, 1) for key in ("A", "B")]
        x = -24*T**3+9*((z-2)*T*T+q*T+p)
        y = 108*r*(T**4+H*T**3+K*T*T+L*T+M)
        original = sp.Poly(sp.expand((y*y-x**3-A*x-B)/729).subs(r*r, z), T)
        equations = self.universal["remaining"]["equations_T7_through_T0"]
        self.assertEqual(original.degree(), 7)
        for degree, expression in zip(range(7, -1, -1), equations):
            self.assertEqual(sp.expand(original.nth(degree)-audit.parse(expression).subs(self.values)), 0)

    def test_original_field_square_descent_is_not_dropped(self):
        data = self.report["remaining_nonzero_b4_system"]
        self.assertTrue(data["z_must_be_nonzero_square_in_C_X"])
        self.assertFalse(data["equations_without_square_condition_are_sufficient_over_original_field"])
        self.assertIn("nonzero y changes sign", data["Galois_descent"])
        self.assertFalse(data["system_solved_over_C_X"])
        self.assertFalse(data["rational_functions_H_K_or_r_assumed_polynomial_in_X"])

    def test_zero_leading_branch_is_not_lost_by_localization(self):
        data = self.report["remaining_nonzero_b4_system"]
        self.assertTrue(data["clearing_z_powers_creates_no_extra_points_when_z_nonzero"])
        self.assertIn("separately certified b4=0 exclusion", data["z_zero_is_not_silently_discarded"])

    def test_rank_torsion_heights_and_unresolved_general_sections_preserved(self):
        data = self.report["preserved_frontier"]
        self.assertEqual([data["original_MW_torsion_order"], data["original_free_rank_lower_bound"], data["original_free_rank_upper_bound"]], [1, 0, 11])
        self.assertEqual(data["unit_charge_conditional_section_height_S_F"], [148, 768])
        self.assertEqual(data["doubled_charge_conditional_section_height_S_F"], [37, 192])
        self.assertTrue(data["every_remaining_cubic_candidate_has_y_degree_exactly_four"])
        for key in ("exact_original_rank_computed", "all_cubic_polynomial_x_sections_excluded",
                    "all_rational_sections_excluded", "higher_degree_or_T_denominator_sections_excluded",
                    "target_height_or_primitive_generator_constructed", "original_coefficient_member_changed",
                    "same_action_parent_accepted"):
            self.assertFalse(data[key])
        self.assertEqual(data["closed_gates"], [])

    def test_cached_reports_are_independent_mutable_copies(self):
        first = audit.derive_member_certificate(self.report["coefficient_payload"])
        first["remaining_nonzero_b4_system"]["system_solved_over_C_X"] = True
        second = audit.derive_member_certificate(self.report["coefficient_payload"])
        self.assertFalse(second["remaining_nonzero_b4_system"]["system_solved_over_C_X"])
        algebra = audit.universal_algebra()
        algebra["remaining"]["clearing_z_powers"][0] = 100
        self.assertEqual(audit.universal_algebra()["remaining"]["clearing_z_powers"], [0, 1, 1, 1])

    def test_portable_source_hash_survives_CRLF_checkout(self):
        original = audit.Path.read_bytes
        names = {"v96_original_section_search_audit.py", "test_v96_original_section_search_audit.py"}
        def windows_bytes(path):
            value = original(path)
            return value.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n") if path.name in names else value
        with patch.object(audit.Path, "read_bytes", windows_bytes):
            payload, _ = audit.load_bound_inputs()
        self.assertEqual(payload, self.report["coefficient_payload"])

    def test_fresh_source_pin_checks_not_hidden_by_algebra_cache(self):
        with patch.object(audit, "portable_sha", return_value="0"*64):
            with self.assertRaises(RuntimeError):
                audit.build_certificate()

    def test_rehashed_resultant_mutation_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["b4_zero_subbranch_exclusion"]["h_nonzero"]["first_two_resultant_mod_prime"] = 0
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(changed)

    def test_rehashed_square_condition_erasure_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["remaining_nonzero_b4_system"]["z_must_be_nonzero_square_in_C_X"] = False
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(changed)

    def test_rehashed_general_nonexistence_promotion_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["preserved_frontier"]["all_rational_sections_excluded"] = True
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(changed)


if __name__ == "__main__":
    unittest.main()
