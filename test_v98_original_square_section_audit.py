import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import sympy as sp

import v98_original_square_section_audit as audit


def determinant_mod(matrix, prime):
    values = [[int(v) % prime for v in row] for row in matrix]
    determinant = 1
    for col in range(len(values)):
        pivot = next((row for row in range(col, len(values)) if values[row][col]), None)
        if pivot is None:
            return 0
        if pivot != col:
            values[col], values[pivot] = values[pivot], values[col]
            determinant = -determinant
        diagonal = values[col][col]
        determinant = determinant*diagonal % prime
        for row in range(col+1, len(values)):
            factor = values[row][col]*pow(diagonal, -1, prime) % prime
            values[row] = [(left-factor*right) % prime for left, right in zip(values[row], values[col])]
    return determinant % prime


class OriginalSquareSectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()
        cls.equations = audit.input_equations()
        cls.values = {key: value.subs(audit.X, 1)
                      for key, value in audit.previous.compressed_coefficients().items()}

    def rehash(self, report):
        report["core_sha256"] = audit.canonical_sha(report)
        return report

    def test_canonical_lineage_roundtrip_and_validation(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        self.assertEqual(self.report, json.loads(json.dumps(self.report)))
        self.assertEqual(self.report["input_core_hashes"], {
            "v97_route": audit.V97_ROUTE_CORE, "v97_master": audit.V97_MASTER_CORE,
            "v97_geometry": audit.V97_GEOMETRY_CORE})
        audit.validate_certificate(self.report)

    def test_original_equations_and_coefficient_dictionary_are_bound(self):
        data = audit.previous.universal_algebra()["remaining"]
        self.assertEqual(self.report["original_equation_list_sha256"],
                         audit.canonical_sha(data["reduced_equations_T3_through_T0"]))
        expected = {"alpha": "X**3 + X", "beta": "X**4 + 2", "gamma": "X**11 + 2*X",
                    "delta": "X**12 + 1", "epsilon": "2*X**11 + 3*X"}
        self.assertEqual(self.report["square_aware_two_variable_reduction"]["coefficient_dictionary"], expected)

    def test_source_hash_portability_under_simulated_crlf_checkout(self):
        path = audit.ROOT / "v97_original_cubic_section_audit.py"
        raw = path.read_bytes().replace(b"\r\n", b"\n")
        expected = audit.portable_sha(path)
        with patch.object(Path, "read_bytes", return_value=raw.replace(b"\n", b"\r\n")):
            self.assertEqual(audit.portable_sha(path), expected)

    def test_source_tampering_is_rejected_fresh_even_after_cache_warmup(self):
        with patch.object(audit, "portable_sha", return_value="0"*64):
            with self.assertRaisesRegex(RuntimeError, "source/test pin"):
                audit.build_certificate()

    def test_parent_core_tampering_is_rejected(self):
        read_text = Path.read_text
        target = audit.V97_ROUTE_PATH
        def changed(path, *args, **kwargs):
            text = read_text(path, *args, **kwargs)
            if path == target:
                report = json.loads(text)
                report["core_sha256"] = "0"*64
                return json.dumps(report)
            return text
        with patch.object(Path, "read_text", changed):
            with self.assertRaisesRegex(RuntimeError, "canonical V97"):
                audit.build_certificate()

    def test_quadratic_pivot_and_exceptional_linear_degree_independently(self):
        z, H, K, alpha = audit.z, audit.H, audit.K, audit.alpha
        self.assertEqual(sp.factor(self.equations[0].coeff(K, 2)), -24*z*(2*H-alpha))
        linear = sp.Poly(self.equations[0].subs(H, alpha/2), K)
        self.assertEqual(linear.degree(), 1)
        self.assertEqual([sp.degree(linear.nth(j), z) for j in (1, 0)], [4, 6])
        data = self.report["half_alpha_generic_exclusion"]
        self.assertEqual(sp.expand(linear.nth(1)-audit.parse(data["A"])), 0)
        self.assertEqual(sp.expand(linear.nth(0)-audit.parse(data["B"])), 0)

    def test_high_coefficient_algorithm_against_full_products(self):
        z, alpha, beta = audit.z, audit.alpha, audit.beta
        factors = [2*z**4+alpha*z**2+1, z**3+beta*z+3, -z*z+4]
        exact = sp.Poly(sp.expand(sp.prod(factors)), z)
        for degree in range(10):
            self.assertEqual(audit.product_coefficient_at_degree(factors, degree), exact.nth(degree))
        self.assertEqual(audit.product_coefficient_at_degree(factors, 12), 0)

    def test_universal_top_degrees_are_cancelled_before_specialization(self):
        data = self.report["half_alpha_generic_exclusion"]["universal_degree_certificates"]
        self.assertEqual([row["termwise_degree_bound"] for row in data], [20, 21])
        self.assertEqual([row["certified_degree_upper_bound"] for row in data], [18, 19])
        self.assertEqual([[item["degree_z"] for item in row["universal_leading_cancellations"]]
                          for row in data], [[20, 19], [21, 20]])
        self.assertTrue(all(item["coefficient"] == "0" for row in data
                            for item in row["universal_leading_cancellations"]))

    def test_specialized_eliminants_reconstructed_by_independent_resultants(self):
        K, H, alpha, z = audit.K, audit.H, audit.alpha, audit.z
        restricted = [sp.expand(v.subs(H, alpha/2).subs(self.values)) for v in self.equations]
        expected = self.report["half_alpha_generic_exclusion"]["primitive_integer_polynomials_coefficients_descending"]
        for row, coefficients in zip(restricted[1:3], expected):
            resultant = sp.Poly(sp.resultant(restricted[0], row, K), z, domain=sp.QQ)
            # Compare monic polynomials: some subresultant implementations swap
            # the inputs by degree with an irrelevant overall sign convention.
            expected_polynomial = sp.Poly.from_list(coefficients, gens=z)
            self.assertEqual(resultant.monic(), expected_polynomial.monic())

    def test_resultant_necessary_condition_does_not_divide_by_A(self):
        A, B, k, c0, c1, c2, c3 = sp.symbols("A B k c0 c1 c2 c3")
        poly = c0+c1*k+c2*k*k+c3*k**3
        D = sum(coefficient*(-B)**j*A**(3-j) for j, coefficient in enumerate((c0,c1,c2,c3)))
        residual = sp.expand(A**3*poly-D)
        self.assertEqual(sp.rem(residual, A*k+B, k), 0)
        self.assertEqual(D.subs({A: 0, B: 0}), 0)
        self.assertTrue(self.report["half_alpha_generic_exclusion"]["no_division_by_A_and_no_A_zero_branch_omitted"])

    def test_degree_preservation_and_independent_37_by_37_sylvester_determinant(self):
        data = self.report["half_alpha_generic_exclusion"]
        f, g = data["modular_coefficients_descending"]
        m, n = len(f)-1, len(g)-1
        self.assertEqual([m, n], [18, 19])
        self.assertNotEqual(f[0], 0)
        self.assertNotEqual(g[0], 0)
        rows = [[0]*i+f+[0]*(n-1-i) for i in range(n)]
        rows += [[0]*i+g+[0]*(m-1-i) for i in range(m)]
        self.assertEqual(len(rows), 37)
        self.assertEqual(determinant_mod(rows, 101), 84)
        self.assertEqual(data["resultant_mod_prime"], 84)
        self.assertEqual(data["specialized_degrees"], data["modular_degrees"])

    def test_generic_exclusion_scope_remains_only_the_half_alpha_locus(self):
        data = self.report["half_alpha_generic_exclusion"]
        self.assertTrue(data["excluded_over_algebraic_closure_C_X"])
        self.assertIn("leading-minus-24", data["scope"])
        self.assertEqual(data["locus"], "H=alpha/2")
        self.assertFalse(self.report["preserved_frontier"]["all_cubic_polynomial_x_sections_excluded"])

    def test_saved_coefficient_rows_reconstruct_all_four_equations(self):
        rows = self.report["square_aware_two_variable_reduction"]["coefficient_rows_R0_R1_R2_R3_ascending_in_K"]
        self.assertEqual([len(v)-1 for v in rows], [2, 3, 3, 4])
        for row, equation in zip(rows, self.equations):
            self.assertEqual(sp.expand(sum(audit.parse(c)*audit.K**i for i, c in enumerate(row))-equation), 0)

    def test_quadratic_pseudoremainder_formulas_by_direct_division(self):
        a, b, c, k = sp.symbols("a b c k")
        for degree in (3, 4):
            coefficients = sp.symbols("u0:"+str(degree+1))
            ell, mu, power = audit.quadratic_remainder(list(coefficients), a, b, c)
            polynomial = sum(value*k**j for j, value in enumerate(coefficients))
            expected = sp.rem(a**power*polynomial, a*k*k+b*k+c, k)
            self.assertEqual(sp.expand(expected-ell*k-mu), 0)
            self.assertEqual(power, degree-1)
        with self.assertRaises(ValueError):
            audit.quadratic_remainder([1, 2], a, b, c)

    def test_nonzero_linear_pivot_reconstruction_and_cross_relations(self):
        a, b, c, ell, mu, ell2, mu2 = sp.symbols("a b c ell mu ell2 mu2")
        k = -mu/ell
        self.assertEqual(sp.cancel((a*k*k+b*k+c)*ell**2-(a*mu*mu-b*mu*ell+c*ell*ell)), 0)
        self.assertEqual(sp.cancel((ell2*k+mu2)*ell+(ell2*mu-mu2*ell)), 0)
        data = self.report["square_aware_two_variable_reduction"]["nonzero_ell_branches"]
        self.assertEqual(data["pivot_cases"], [1, 2, 3])
        self.assertEqual(data["K_reconstruction"], "K=-mu_j/ell_j")
        self.assertTrue(data["equivalent_to_original_branch_on_this_chart"])

    def test_all_linear_pivots_zero_is_not_discarded(self):
        k, X = audit.K, audit.X
        R0 = k*k-X
        polynomials = [R0*(k+3), R0*(k+4), R0*(k*k+1)]
        for polynomial in polynomials:
            row = sp.Poly(polynomial, k)
            ell, mu, _ = audit.quadratic_remainder([row.nth(i) for i in range(row.degree()+1)], 1, 0, -X)
            self.assertEqual(sp.expand(ell), 0)
            self.assertEqual(sp.expand(mu), 0)
        # A nonempty algebraic-closure branch may still have no original-field
        # K: the quadratic discriminant 4*X has an odd valuation at X=0.
        self.assertEqual(sp.Poly(4*X, X).terms()[-1][0][0], 1)
        data = self.report["square_aware_two_variable_reduction"]["all_ell_zero_branch"]
        self.assertFalse(data["branch_excluded"])
        self.assertTrue(data["over_algebraic_closure_quadratic_root_always_exists"])
        self.assertIn("b^2-4*a*c is a square in C(X), including zero", data["remaining_original_field_conditions"])

    def test_two_distinct_original_field_square_conditions_are_retained(self):
        data = self.report["square_aware_two_variable_reduction"]
        self.assertTrue(data["nonzero_ell_branches"]["z_nonzero_square_in_C_X_required"])
        self.assertIn("z!=0 is a square in C(X)", data["all_ell_zero_branch"]["remaining_original_field_conditions"])
        self.assertIn("anti-invariant", data["square_descent"])
        self.assertFalse(data["H_or_z_assumed_polynomial_in_X"])
        self.assertFalse(data["system_solved_over_C_X"])

    def test_full_modular_system_recomputed_exactly_not_sampled(self):
        data = self.report["full_system_finite_specialization"]
        polynomials = []
        for equation in self.equations:
            polynomial = sp.Poly(equation.subs(self.values), audit.K, audit.H, audit.z, domain=sp.QQ)
            polynomials.append(polynomial.clear_denoms()[1].set_modulus(101).as_expr())
        self.assertEqual([str(v) for v in polynomials], data["input_polynomials_mod_prime"])
        basis = sp.groebner(polynomials, audit.K, audit.H, audit.z, modulus=101, order="grevlex")
        self.assertEqual([v.as_expr() for v in basis.polys], [1])
        self.assertTrue(data["all_specialized_solutions_over_algebraic_closure_F101_excluded"])
        self.assertFalse(data["generic_C_X_exclusion_follows_from_this_unit_ideal"])

    def test_specialization_counterexample_prevents_false_generic_upgrade(self):
        X, z = audit.X, audit.z
        equation = (X-1)*z-1
        self.assertEqual(sp.cancel(equation.subs(z, 1/(X-1))), 0)
        self.assertEqual(equation.subs(X, 1), -1)
        data = self.report["full_system_finite_specialization"]
        self.assertFalse(data["geometric_upgrade_proved"])
        self.assertTrue(data["non_inference_counterexample"]["specialized_ideal_is_unit"])

    def test_no_rank_height_or_completion_claim_is_added(self):
        data = self.report["preserved_frontier"]
        self.assertEqual([data["original_free_rank_lower_bound"], data["original_free_rank_upper_bound"]], [0, 11])
        self.assertEqual(data["original_MW_torsion_order"], 1)
        self.assertEqual(data["unit_charge_conditional_section_height_S_F"], [148, 768])
        self.assertEqual(data["doubled_charge_conditional_section_height_S_F"], [37, 192])
        self.assertFalse(data["target_height_or_primitive_generator_constructed"])
        self.assertFalse(data["same_action_parent_accepted"])
        self.assertEqual(data["closed_gates"], [])

    def test_rehashed_false_resultant_is_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["half_alpha_generic_exclusion"]["resultant_mod_prime"] = 0
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(self.rehash(changed))

    def test_rehashed_dropped_square_or_exceptional_case_is_rejected(self):
        for mutate in (lambda d: d["nonzero_ell_branches"].update(z_nonzero_square_in_C_X_required=False),
                       lambda d: d["all_ell_zero_branch"].update(branch_excluded=True)):
            changed = copy.deepcopy(self.report)
            mutate(changed["square_aware_two_variable_reduction"])
            with self.assertRaises(RuntimeError):
                audit.validate_certificate(self.rehash(changed))

    def test_rehashed_modular_generic_overclaim_is_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["full_system_finite_specialization"]["generic_C_X_exclusion_follows_from_this_unit_ideal"] = True
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(self.rehash(changed))

    def test_cached_data_cannot_be_mutated_through_a_returned_report(self):
        changed = audit.build_certificate()
        changed["half_alpha_generic_exclusion"]["universal_degree_certificates"].clear()
        self.assertEqual(len(audit.build_certificate()["half_alpha_generic_exclusion"]["universal_degree_certificates"]), 2)
        changed["full_system_finite_specialization"]["basis"] = ["0"]
        self.assertEqual(audit.build_certificate()["full_system_finite_specialization"]["basis"], ["1"])


if __name__ == "__main__":
    unittest.main()
