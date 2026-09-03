"""Independent polynomial identities, pivot boundaries and fail-closed scope."""
import copy
from fractions import Fraction
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import sympy as sp

import v103_original_quartic_section_audit as audit


def sparse_expression(terms, variables):
    return sum(sp.Rational(n, d)*sp.prod(symbol**power for symbol, power in zip(variables, exponents))
               for exponents, n, d in terms)


def sparse_value(terms, values):
    return sum(sp.Rational(n, d)*sp.prod(value**power for value, power in zip(values, exponents))
               for exponents, n, d in terms)


def sylvester_rows(first, second):
    f, g = first.all_coeffs(), second.all_coeffs()
    m, n = first.degree(), second.degree()
    return [([0]*i+f+[0]*(n-1-i)) for i in range(n)]+[([0]*i+g+[0]*(m-1-i)) for i in range(m)]


def determinant_mod(matrix, prime):
    data = [[int(value) % prime for value in row] for row in matrix]
    determinant = 1
    for col in range(len(data)):
        pivot = next((i for i in range(col, len(data)) if data[i][col]), None)
        if pivot is None:
            return 0
        if pivot != col:
            data[pivot], data[col] = data[col], data[pivot]
            determinant = -determinant
        value = data[col][col]
        determinant = determinant*value % prime
        inverse = pow(value, -1, prime)
        for row in range(col+1, len(data)):
            factor = data[row][col]*inverse % prime
            for j in range(col, len(data)):
                data[row][j] = (data[row][j]-factor*data[col][j]) % prime
    return determinant % prime


class TestOriginalQuartic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()
        cls.reduced = cls.report["exact_quartic_reduction"]
        cls.boundary = cls.report["pivot_boundary_data"]
        cls.rows = cls.reduced["remaining_equations_T5_through_T0"]
        cls.N = [audit.parse(row["numerator"]) for row in cls.rows]
        cls.route = json.loads((audit.ROOT/audit.PARENTS["v102_route"][0]).read_text())

    def test_canonical_roundtrip_and_validation(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        audit.validate_certificate(json.loads(json.dumps(self.report)))

    def test_exact_immutable_parents(self):
        for key, (_, core) in audit.PARENTS.items():
            self.assertEqual(self.report["input_core_hashes"][key], core)
        with patch.object(audit.common, "load_bound", side_effect=RuntimeError("changed parent")):
            with self.assertRaises(RuntimeError):
                audit.build_certificate()

    def test_source_checks_are_fresh_and_portable(self):
        with patch.object(audit, "file_sha", return_value="0"*64):
            with self.assertRaises(RuntimeError):
                audit.build_certificate()
        with tempfile.TemporaryDirectory() as folder:
            first, second = Path(folder)/"lf.py", Path(folder)/"crlf.py"
            first.write_bytes(b"first\nsecond\n")
            second.write_bytes(b"first\r\nsecond\r\n")
            self.assertEqual(audit.file_sha(first), audit.file_sha(second))

    def test_original_payload_and_old_equations_are_preserved(self):
        old = self.route["nonzero_pivot_section_elimination"]
        for key in ("coefficient_payload", "coefficient_payload_sha256", "original_equation_list_sha256", "preserved_frontier"):
            self.assertEqual(self.report[key], old[key])
        self.assertEqual(self.report["quartic_reduced_equations_sha256"], audit.canonical_sha(self.rows))

    def test_globally_integral_frontier_not_affine_integrality(self):
        old = self.report["inherited_global_integral_frontier"]
        self.assertTrue(old["integral_means_P_dot_O_zero_globally_not_only_affine_T"])
        self.assertEqual(old["only_surviving_exact_degrees_x_y"], [4, 6])
        self.assertEqual(old["height_if_exists"], 4)
        self.assertEqual(old["target_to_quartic_height_ratios"], ["37/4", "37"])

    def test_rational_leading_parameter_needs_no_square_root(self):
        a, b = sp.symbols("a b")
        relation = b*b-a**3
        self.assertEqual(sp.rem(sp.together((b/a)**2-a).as_numer_denom()[0], relation, b), 0)
        self.assertEqual(sp.rem(sp.together((b/a)**3-b).as_numer_denom()[0], relation, b), 0)
        self.assertFalse(self.report["rational_leading_normalization"]["square_root_extension_or_rescaling_of_original_curve"])
        self.assertTrue(self.report["rational_leading_normalization"]["t_may_not_be_set_to_one"])

    def test_completed_square_inverse_covers_all_quartics(self):
        t, p, q, r, h = audit.VARIABLES
        c3, c2, c1, c0 = sp.symbols("c3 c2 c1 c0")
        pp = c3/(2*t)
        qq = (c2-pp*pp)/(2*t)
        substitutions = {p: pp, q: qq, r: c1-2*pp*qq, h: c0-qq*qq}
        rebuilt = audit.parse(self.reduced["x_section"]).subs(substitutions)
        self.assertEqual(sp.cancel(rebuilt-(t*t*audit.T**4+c3*audit.T**3+c2*audit.T**2+c1*audit.T+c0)), 0)

    def test_original_binary_quartic_invariants_reproduce_curve(self):
        T = audit.T
        qa = T**3+audit.alpha*T*T+audit.gamma
        qb = audit.beta*T*T+audit.delta
        qc, qe = -2*T**3, T**3+audit.epsilon
        A, B = map(audit.parse, self.reduced["unchanged_A_B"])
        self.assertEqual(sp.expand(A+27*(12*qa*qe+qc*qc)), 0)
        self.assertEqual(sp.expand(B+27*(72*qa*qc*qe-27*qb*qb*qe-2*qc**3)), 0)
        self.assertEqual([sp.degree(A, T), sp.degree(B, T)], [6, 9])

    def test_first_recursive_coefficients_are_independent(self):
        t, p, q, _, _ = audit.VARIABLES
        coeffs = {row["degree"]: audit.parse(row["coefficient"]) for row in self.reduced["recursive_y_coefficients"]}
        self.assertEqual(coeffs[5], 3*p*t*t)
        self.assertEqual(sp.cancel(coeffs[4]-3*(p*p*t*t+q*t**3-72)/t), 0)

    def test_independent_full_high_coefficient_cancellation(self):
        x, y = map(audit.parse, (self.reduced["x_section"], self.reduced["y_section"]))
        A, B = map(audit.parse, self.reduced["unchanged_A_B"])
        residual = sp.Poly(sp.expand(y*y-x**3-A*x-B), audit.T)
        for exponent in range(6, 13):
            self.assertEqual(sp.cancel(residual.nth(exponent)), 0)
        for row in self.rows:
            self.assertEqual(sp.cancel(residual.nth(row["T_degree"])-audit.parse(row["numerator"])/audit.parse(row["denominator"])), 0)

    def test_recurrence_rejects_wrong_leading_chart(self):
        A, B = audit.original_model()
        with self.assertRaises(ValueError):
            audit.square_root_coefficients(audit.t*audit.T**4, A, B)

    def test_only_nonzero_t_denominators_are_cleared(self):
        for row in self.rows:
            denominator = sp.Poly(audit.parse(row["denominator"]), audit.t)
            self.assertEqual(len(denominator.terms()), 1)
            self.assertEqual(denominator.as_expr().free_symbols, {audit.t})
        self.assertEqual([row["degree_in_h"] for row in self.rows], [1, 2, 2, 2, 2, 3])

    def test_sign_involution_preserves_x_and_negates_y(self):
        flip = {audit.t: -audit.t, audit.p: -audit.p, audit.q: -audit.q}
        x, y = map(audit.parse, (self.reduced["x_section"], self.reduced["y_section"]))
        self.assertEqual(sp.expand(x.subs(flip, simultaneous=True)-x), 0)
        self.assertEqual(sp.cancel(y.subs(flip, simultaneous=True)+y), 0)

    def test_linear_h_pivot_is_derived_not_guessed(self):
        L = audit.parse(self.reduced["first_linear_pivot_L"])
        self.assertEqual(sp.expand(sp.diff(self.N[0], audit.h)+6*audit.t**6*L), 0)
        self.assertEqual(sp.degree(self.N[0], audit.h), 1)

    def test_Q1_reconstruction_solves_first_equation_exactly(self):
        row = self.report["remaining_quartic_charts"]["live_charts"][0]
        self.assertEqual(row["conditions"], ["t!=0", "L!=0"])
        self.assertEqual(sp.cancel(self.N[0].subs(audit.h, audit.parse(row["h_reconstruction"]))), 0)
        self.assertEqual(row["remaining_equations"], 5)
        self.assertEqual(len(row["remaining_unknowns"]), 4)

    def test_L_zero_quadratic_and_M_boundary_are_exact(self):
        F = audit.parse(self.boundary["L_zero_first_equation_F"])
        r0 = audit.parse(self.boundary["L_zero_r_reconstruction"])
        self.assertEqual(sp.cancel(self.N[0].subs(audit.r, r0)-F), 0)
        M = audit.parse(self.boundary["second_pivot_M"])
        self.assertEqual(sp.expand(sp.Poly(F, audit.q).nth(2)+1296*audit.t**6*M), 0)
        self.assertNotIn(audit.h, F.free_symbols)

    def test_double_pivot_leading_identity(self):
        F = audit.parse(self.boundary["L_zero_first_equation_F"])
        p0 = audit.parse(self.boundary["L_M_zero_p_reconstruction"])
        D, E = audit.boundary_polynomials()
        target = -27*audit.t**3*D.subs(audit.v, audit.t**2)*audit.q+sp.Rational(27, 8)*E.subs(audit.v, audit.t**2)
        self.assertEqual(sp.cancel(F.subs(audit.p, p0)-target), 0)

    def test_deepest_D_zero_sylvester_is_independently_nonzero(self):
        row = self.boundary["deepest_zero_pivot_exclusion"]
        polynomials = [sp.Poly(audit.parse(text), audit.v) for text in row["X_one_polynomials"]]
        matrix = sylvester_rows(*polynomials)
        self.assertEqual(len(matrix), 8)
        self.assertEqual(str(sp.Matrix(matrix).det()), row["X_one_resultant"])
        self.assertEqual(determinant_mod(matrix, 101), 54)
        self.assertEqual(row["universal_degree_bounds_D_E"], [3, 5])

    def test_sparse_double_pivot_substitution_is_exact_at_second_parameters(self):
        tvalue, hvalue = sp.Rational(2), sp.Rational(3)
        parameters = {symbol: value for symbol, value in zip(audit.PARAMETERS, (1, 2, 4, 5, 7))}
        D, E = audit.boundary_polynomials()
        dvalue, evalue = [expr.subs(parameters).subs(audit.v, tvalue*tvalue) for expr in (D, E)]
        substitutions = {**parameters, audit.t: tvalue, audit.h: hvalue,
                         audit.p: (parameters[audit.alpha]*tvalue*tvalue-64)/(4*tvalue),
                         audit.r: -3456/tvalue**4, audit.q: evalue/(8*tvalue**3*dvalue)}
        for degree, tden, dden, removed, terms in audit.double_pivot_sparse():
            row = next(row for row in self.rows if row["T_degree"] == degree)
            direct = audit.parse(row["numerator"]).subs(substitutions)*tvalue**(tden-removed)*dvalue**dden
            actual = sparse_value(terms, (tvalue, hvalue, *(parameters[s] for s in audit.PARAMETERS)))
            self.assertEqual(direct, actual)

    def test_sparse_linear_remainders_and_resultants_at_independent_values(self):
        tv, hv = sp.Rational(3), sp.Rational(2)
        pars = (sp.Integer(1), sp.Integer(3), sp.Integer(2), sp.Integer(7), sp.Integer(4))
        sub = dict(zip(audit.PARAMETERS, pars))
        dv = audit.boundary_polynomials()[0].subs(sub).subs(audit.v, tv*tv)
        quadratic = []
        for degree, td, dd, mt, terms in audit.double_pivot_sparse():
            coefficients = [sparse_value(tuple((powers, n, d) for powers, n, d in terms if powers[1] == k), (tv, 1, *pars)) for k in range(3)]
            quadratic.append(coefficients)
        c, b, a = quadratic[0]
        for index, tp, dp, terms, ltp, ldp, ell, mu in audit.double_pivot_resultants_sparse():
            f, e, d = quadratic[index]
            le = sparse_value(ell, (tv, *pars))
            lm = sparse_value(mu, (tv, *pars))
            self.assertEqual(le*tv**ltp*dv**ldp, e-d*b/a)
            self.assertEqual(lm*tv**ltp*dv**ldp, f-d*c/a)
            result = sparse_value(terms, (tv, *pars))
            self.assertEqual(result*tv**tp*dv**dp, a*lm*lm-b*le*lm+c*le*le)

    def test_universal_degrees_evenness_and_only_approved_factors(self):
        rows = self.report["double_pivot_generic_exclusion"]["resultant_rows"]
        self.assertEqual([row["universal_normalized_term_count"] for row in rows], [6716, 10349])
        self.assertEqual([row["universal_exact_degree_t"] for row in rows], [56, 66])
        self.assertEqual([row["resultant_removed_t_D_powers"] for row in rows], [[16, 3], [16, 2]])
        for derived, row in zip(audit.double_pivot_resultants_sparse(), rows):
            terms = derived[3]
            self.assertFalse(any(powers[0] % 2 for powers, n, d in terms))
            self.assertEqual(audit.canonical_sha(terms), row["universal_normalized_sparse_sha256"])

    def test_fixed_61_by_61_resultant_independently_nonzero(self):
        proof = self.report["double_pivot_generic_exclusion"]
        polys = [sp.Poly(audit.parse(row["polynomial_mod101"]), audit.v, modulus=101) for row in proof["resultant_rows"]]
        matrix = sylvester_rows(*polys)
        self.assertEqual([poly.degree() for poly in polys], [28, 33])
        self.assertEqual(len(matrix), 61)
        self.assertEqual(determinant_mod(matrix, 101), 23)
        self.assertEqual(proof["specialized_fixed_Sylvester_determinant_mod101"], 23)
        self.assertEqual(sp.gcd(*polys).degree(), 0)

    def test_residue_degree_bounds_are_preserved(self):
        rows = self.report["double_pivot_generic_exclusion"]["resultant_rows"]
        for row in rows:
            degree = row["universal_degree_bound_v"]
            self.assertEqual(row["X_one_degree_v"], degree)
            self.assertEqual(row["degree_mod101"], degree)
            self.assertNotEqual(row["leading_coefficient_mod101"], 0)
            self.assertNotEqual(row["cleared_constant_denominator"] % 101, 0)

    def test_both_D_cases_and_zero_linear_pivots_are_retained(self):
        row = self.report["double_pivot_generic_exclusion"]
        self.assertTrue(self.boundary["deepest_zero_pivot_exclusion"]["generic_excluded_over_algebraic_closure_C_X"])
        self.assertTrue(row["generic_L_M_zero_boundary_excluded_over_algebraic_closure_C_X"])
        self.assertTrue(row["linear_h_pivots_may_vanish"])
        self.assertTrue(row["no_linear_h_pivot_or_quadratic_discriminant_divided"])
        self.assertIn("No coordinate valuation, properness, rank-specialization", row["proof"])

    def test_Q2_square_condition_includes_repeated_roots(self):
        row = self.report["remaining_quartic_charts"]["live_charts"][1]
        self.assertEqual(row["conditions"], ["t!=0", "L=0", "M!=0"])
        self.assertTrue(row["repeated_q_root_retained"])
        self.assertIn("including zero", row["original_field_necessary_and_sufficient_q_test_for_this_equation"])
        A, B, C, ss = sp.symbols("A B C ss")
        root = (-B+ss)/(2*A)
        numerator = sp.together(A*root*root+B*root+C).as_numer_denom()[0]
        self.assertEqual(sp.rem(numerator, ss*ss-B*B+4*A*C, ss), 0)
        self.assertFalse(row["square_test_alone_solves_all_remaining_equations"])

    def test_two_charts_remain_open_without_function_degree_bound(self):
        row = self.report["remaining_quartic_charts"]
        self.assertEqual([chart["id"] for chart in row["live_charts"]], ["Q1", "Q2"])
        self.assertTrue(row["no_degree_bound_on_rational_functions_of_X_imposed"])
        self.assertFalse(row["actual_rational_candidate_found"])
        self.assertFalse(row["entire_quartic_chart_excluded"])

    def test_rank_targets_and_gate_boundaries_preserved(self):
        old = self.report["preserved_frontier"]
        self.assertEqual((old["original_free_rank_lower_bound"], old["original_free_rank_upper_bound"], old["original_MW_torsion_order"]), (0, 11, 1))
        self.assertFalse(old["nonzero_original_section_constructed"])
        decision = self.report["terminal_decision"]
        for key in ("all_global_integral_sections_excluded", "original_exact_MW_rank_computed", "actual_target_section_or_height_constructed", "theory_complete"):
            self.assertFalse(decision[key])
        self.assertEqual(decision["closed_gates"], [])

    def test_resealed_overclaim_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["remaining_quartic_charts"]["entire_quartic_chart_excluded"] = True
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(changed)

    def test_resealed_equation_change_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["exact_quartic_reduction"]["remaining_equations_T5_through_T0"][0]["numerator"] = "0"
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(changed)

    def test_cached_algebra_is_immutable_and_reports_are_independent(self):
        self.assertIsInstance(audit.double_pivot_sparse(), tuple)
        self.assertIsInstance(audit.double_pivot_resultants_sparse()[0][3], tuple)
        changed = json.loads(audit.reduced_json())
        changed["high_equations_T12_through_T6"][0] = "1"
        self.assertEqual(json.loads(audit.reduced_json())["high_equations_T12_through_T6"], ["0"]*7)


if __name__ == "__main__":
    unittest.main()
