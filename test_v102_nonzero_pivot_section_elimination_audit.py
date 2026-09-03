import copy
from fractions import Fraction
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import sympy as sp

import v102_nonzero_pivot_section_elimination_audit as audit


class NonzeroPivotSectionEliminationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()
        _, cls.saved, cls.legacy = audit.load_bound_inputs()
        cls.strings = tuple(cls.report["shared_resultant_necessity"]["original_four_equations_R0_through_R3"])
        cls.newton = cls.report["shared_resultant_newton_certificate"]
        cls.sparse = audit.universal_sparse_resultants(cls.strings)

    def rehash(self, data):
        data["core_sha256"] = audit.canonical_sha(data)
        return data

    def test_canonical_lineage_and_serialization(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        self.assertEqual(json.loads(json.dumps(self.report)), self.report)
        self.assertEqual(self.report["input_core_hashes"]["v101_route"], audit.V101_ROUTE_CORE)
        self.assertEqual(self.report["input_core_hashes"]["v101_master"], audit.V101_MASTER_CORE)
        audit.validate_certificate(self.report)

    def test_parent_source_hashes_are_crlf_portable(self):
        path = audit.ROOT / "v101_original_section_solvability_audit.py"
        data = path.read_bytes().replace(b"\r\n", b"\n")
        expected = audit.portable_sha(path)
        with patch.object(Path, "read_bytes", return_value=data.replace(b"\n", b"\r\n")):
            self.assertEqual(audit.portable_sha(path), expected)

    def test_source_pins_are_fresh_after_pure_cache(self):
        with patch.object(audit, "portable_sha", return_value="0"*64):
            with self.assertRaisesRegex(RuntimeError, "source/test pin"):
                audit.build_certificate()

    def test_parent_master_tampering_is_rejected(self):
        old = Path.read_text
        def read(path, *args, **kwargs):
            text = old(path, *args, **kwargs)
            if path == audit.V101_MASTER_PATH:
                data = json.loads(text)
                data["core_sha256"] = "0"*64
                return json.dumps(data)
            return text
        with patch.object(Path, "read_text", read):
            with self.assertRaisesRegex(RuntimeError, "canonical V101"):
                audit.build_certificate()

    def test_original_payload_and_equations_are_bound_unchanged(self):
        self.assertEqual(self.report["coefficient_payload"], self.saved["coefficient_payload"])
        self.assertEqual(self.report["coefficient_payload_sha256"], self.saved["coefficient_payload_sha256"])
        self.assertEqual(audit.canonical_sha(list(self.strings)), self.saved["original_equation_list_sha256"])
        self.assertEqual(self.report["coefficient_dictionary"], self.saved["coefficient_dictionary"])
        self.assertEqual(self.report["input_core_hashes"]["v96_geometry"], self.legacy["v96"]["core_sha256"])
        self.assertEqual(self.report["input_core_hashes"]["v97_geometry"], self.legacy["v97"]["core_sha256"])

    def test_generic_resultant_formula_matches_numeric_Sylvester_determinant(self):
        for degree in (3, 4):
            variables, polynomial = audit.generic_resultant_formula(degree)
            values = [2, 3, 5, *[7, 11, 13, 17, 19][:degree+1]]
            first = values[:3]
            second = list(reversed(values[3:]))
            size = degree+2
            rows = []
            for i in range(degree):
                rows.append([0]*i+first+[0]*(size-3-i))
            for i in range(2):
                rows.append([0]*i+second+[0]*(size-(degree+1)-i))
            determinant = sp.Matrix(rows).det()
            actual = polynomial.as_expr().subs(dict(zip(variables, values)))
            self.assertEqual(actual, determinant)
            self.assertEqual(len(polynomial.terms()), 13 if degree == 3 else 22)

    def test_common_finite_root_forces_resultant_even_when_pivot_drops(self):
        K = audit.K
        # Fixed degree2/degree3 Sylvester matrix with a=0 retains the
        # finite rootK=2. No leading-pivot division is valid or needed.
        first, second = [0, 1, -2], [1, 0, 0, -8]
        rows = [[0]*i+first+[0]*(2-i) for i in range(3)]
        rows += [[0]*i+second+[0]*(1-i) for i in range(2)]
        matrix = sp.Matrix(rows)
        self.assertEqual(matrix*sp.Matrix([16, 8, 4, 2, 1]), sp.zeros(5, 1))
        self.assertEqual(matrix.det(), 0)
        self.assertEqual(sp.resultant(K-2, K**3-8, K), 0)
        self.assertTrue(self.report["shared_resultant_necessity"]["quadratic_pivot_may_vanish_without_invalidating_necessity"])

    def test_pairwise_resultants_are_not_mistaken_for_sufficiency(self):
        K = audit.K
        first, second, third = K*K-1, K-1, K+1
        self.assertEqual(sp.resultant(first, second, K), 0)
        self.assertEqual(sp.resultant(first, third, K), 0)
        self.assertEqual(sp.gcd(second, third), 1)
        self.assertFalse(self.report["shared_resultant_necessity"]["pairwise_resultants_claimed_sufficient_for_common_K_root"])

    def test_universal_sparse_term_counts_and_exact_common_z_power(self):
        self.assertEqual([len(row[3]) for row in self.sparse], [5560, 9500, 21128])
        for data, row in zip(self.sparse, self.newton["rows"]):
            formula, term_count, factor, terms = data
            self.assertEqual(factor, 2)
            self.assertEqual(min(powers[0] for powers, numerator, denominator in terms), 0)
            self.assertTrue(all(min(powers) >= 0 for powers, numerator, denominator in terms))
            self.assertEqual(audit.canonical_sha(terms), row["universal_normalized_sparse_terms_sha256"])
            self.assertEqual(term_count, row["abstract_formula_term_count"])
            self.assertEqual(formula, row["generic_abstract_resultant"])

    def test_immutable_sparse_cache_has_no_mutable_polynomial_report(self):
        self.assertIsInstance(self.sparse, tuple)
        self.assertIsInstance(self.sparse[0][3], tuple)
        self.assertIsInstance(self.sparse[0][3][0][0], tuple)
        with self.assertRaises(TypeError):
            self.sparse[0][3][0] = ((), 0, 1)

    def test_sparse_expansion_specialization_matches_direct_resultants(self):
        inverse = (audit.w-audit.z+3)/4
        source = [sp.Poly(audit.parse(value).subs(audit.SPECIAL_VALUES).subs(audit.H, inverse).expand(), audit.K)
                  for value in self.strings]
        for index, data in enumerate(self.sparse, 1):
            sparse = audit.specialize_sparse(data[3])
            direct = sp.Poly(sp.resultant(source[0], source[index], audit.K)/audit.z**2, audit.z, audit.w, domain=sp.QQ)
            self.assertEqual(sparse, direct)
            denominator, integer = direct.clear_denoms()
            self.assertEqual(str(integer.as_expr()), self.newton["rows"][index-1]["X_one_integer_polynomial"])

    def test_sparse_resultant_at_independent_parameter_point_matches_direct_value(self):
        values = {audit.z: 3, audit.w: 5, audit.alpha: 7, audit.beta: 11,
                  audit.gamma: 13, audit.delta: 17, audit.epsilon: 19}
        source = [sp.Poly(audit.parse(value).subs(audit.H, (audit.w-audit.z+sp.Rational(3, 2)*audit.alpha)/4).subs(values), audit.K)
                  for value in self.strings]
        coordinate_values = [values[v] for v in audit.SPARSE_VARIABLES]
        for index, data in enumerate(self.sparse, 1):
            value = Fraction(0)
            for powers, numerator, denominator in data[3]:
                term = Fraction(numerator, denominator)
                for coordinate, power in zip(coordinate_values, powers):
                    term *= coordinate**power
                value += term
            exact = sp.resultant(source[0], source[index], audit.K)/9
            self.assertEqual(sp.Rational(value.numerator, value.denominator), exact)

    def test_universal_and_both_residue_hulls_match_with_unit_vertices(self):
        for data, row in zip(self.sparse, self.newton["rows"]):
            hull = audit.previous.convex_hull([powers[:2] for powers, numerator, denominator in data[3]])
            rational = audit.specialize_sparse(data[3])
            denominator, integer = rational.clear_denoms()
            modular = integer.set_modulus(101)
            self.assertEqual(hull, audit.previous.convex_hull(rational.monoms()))
            self.assertEqual(hull, audit.previous.convex_hull(modular.monoms()))
            self.assertEqual([list(point) for point in hull], row["newton_hull_CCW"])
            self.assertNotEqual(int(denominator) % 101, 0)
            for point in hull:
                self.assertNotEqual(rational.coeff_monomial(point), 0)
                self.assertNotEqual(modular.coeff_monomial(point), 0)

    def test_all_common_pole_rays_are_exhausted(self):
        raysets = [set(audit.previous.outward_rays(tuple(tuple(point) for point in row["newton_hull_CCW"])))
                   for row in self.newton["rows"]]
        common = sorted(set.intersection(*raysets))
        self.assertEqual(common, [(-2, 1), (0, -1), (1, 1)])
        self.assertEqual([ray for ray in common if max(ray) > 0], [(-2, 1), (1, 1)])
        self.assertEqual(self.newton["common_possible_pole_rays"], [[-2, 1], [1, 1]])

    def test_QQ_and_mod101_face_gcds_have_no_nonzero_root(self):
        for face in self.newton["pole_faces"]:
            expected = audit.w**2 if face["primitive_outward_ray"] == [-2, 1] else audit.w**8
            for field in ("QQ", "GF101"):
                options = {"domain": sp.QQ} if field == "QQ" else {"modulus": 101}
                polynomials = [sp.Poly(audit.parse(value), audit.w, **options) for value in face[field]["polynomials"]]
                common = polynomials[0]
                for polynomial in polynomials[1:]:
                    common = sp.gcd(common, polynomial)
                self.assertEqual(common.monic().as_expr(), expected)
                self.assertTrue(face[field]["torus_parameter_required_nonzero"])

    def test_pole_face_normalization_uses_square_not_previous_cube_root(self):
        A, lam = sp.symbols("A lam", nonzero=True)
        self.assertEqual((A/lam**2).subs(A, lam**2), 1)
        self.assertIn("lambda^2=A", self.newton["torus_normalization"])
        self.assertNotIn("lambda^3=A", self.newton["torus_normalization"])
        self.assertIn("must remain nonzero", self.newton["torus_normalization"])

    def test_universal_coordinate_axes_are_explicit_and_unit_controlled(self):
        first = self.sparse[0][3]
        self.assertTrue(all(powers[1] == 0 for powers, numerator, denominator in first if powers[0] == 0))
        self.assertEqual(max(powers[0] for powers, numerator, denominator in first if powers[1] == 0), 16)
        data = self.newton["zero_coordinate_cases"]
        for powers, key in (((0, 0), "universal_first_resultant_at_z_zero"),
                            ((16, 0), "universal_first_resultant_at_w_zero_leading_coefficient")):
            expression = audit.parameter_coefficient(first, *powers)
            self.assertEqual(sp.expand(expression-audit.parse(data[key])), 0)
            value = sp.Rational(expression.subs(audit.SPECIAL_VALUES))
            self.assertNotEqual(int(value.p) % 101, 0)
            self.assertNotEqual(int(value.q) % 101, 0)
        self.assertEqual(data["X_one_z_zero_constant"], "5514047299623807/134217728")
        self.assertEqual(data["X_one_w_zero_leading_coefficient"], "675/16384")

    def test_modular_inputs_are_the_same_exact_normalized_resultants(self):
        finite = self.report["finite_field_unit_ideal"]
        self.assertEqual(finite["input_polynomials"], [row["polynomial_mod101"] for row in self.newton["rows"]])
        for row in self.newton["rows"]:
            poly = sp.Poly(audit.parse(row["X_one_integer_polynomial"]), audit.z, audit.w, modulus=101)
            self.assertEqual(str(poly.as_expr()), row["polynomial_mod101"])
        self.assertEqual(finite["prime"], 101)

    def test_unit_ideal_independently_recomputed(self):
        finite = self.report["finite_field_unit_ideal"]
        basis = sp.groebner([audit.parse(value) for value in finite["input_polynomials"]],
                           audit.z, audit.w, modulus=101, order="grevlex")
        self.assertEqual([poly.as_expr() for poly in basis.polys], [1])
        self.assertTrue(finite["affine_modular_unit_ideal_alone_is_not_the_generic_proof"])

    def test_two_valuations_include_zero_coordinates_and_do_not_need_K_bound(self):
        data = self.report["two_valuation_generic_exclusion"]
        proof = " ".join(data["proof_steps"])
        for phrase in ("finite extension L/Q(X)", "X-1 valuation", "finite extension of Q", "place of that number field above101"):
            self.assertIn(phrase, proof)
        self.assertIn("Nothing is asserted about K at this stage", proof)
        self.assertTrue(data["both_valuations_and_coordinate_axes_controlled"])
        self.assertFalse(data["specialized_pivot_or_infinity_root_silently_removed"])
        self.assertFalse(data["generic_exclusion_from_modular_unit_ideal_alone_claimed"])

    def test_only_z_squared_is_divided_and_all_linear_pivots_retained(self):
        necessity = self.report["shared_resultant_necessity"]
        self.assertIn("z^2", necessity["only_divided_variable_factor"])
        self.assertTrue(necessity["no_a_ell_mu_or_K_discriminant_division"])
        self.assertTrue(necessity["all_three_nonzero_ell_charts_and_zero_ell_boundary_retained"])
        self.assertTrue(self.report["two_valuation_generic_exclusion"]["all_nonzero_b4_leading_minus24_cubic_charts_excluded_over_algebraic_closure_C_X"])

    def test_historical_degree_splits_are_bound_and_exhaustive(self):
        data = self.report["combined_original_polynomial_ansatz_conclusion"]
        self.assertEqual(data["bound_degree_three_leading_classification"]["only_possible_leading_coefficients"], [12, -24])
        self.assertFalse(data["bound_degree_at_most_two_exclusion"]["nonzero_section_with_this_ansatz_exists"])
        self.assertTrue(data["bound_minus24_b4_zero_excluded_over_algebraic_closure_C_X"])
        self.assertTrue(data["new_minus24_b4_nonzero_excluded_over_algebraic_closure_C_X"])
        self.assertFalse(data["nonzero_original_section_with_polynomial_x_degree_at_most_three_exists"])
        self.assertIn("integrally closed", data["y_integrality_argument"])

    def test_plus12_exclusion_remains_original_field_only(self):
        data = self.report["combined_original_polynomial_ansatz_conclusion"]
        plus = data["bound_plus12_original_field_squareclass_exclusion"]
        self.assertTrue(plus["squareclass_is_nontrivial_in_C_X"])
        self.assertFalse(plus["exclusion_claimed_after_adjoining_the_monodromy_square_root"])
        self.assertTrue(data["all_cubic_polynomial_x_sections_excluded_over_original_field"])
        self.assertFalse(data["entire_low_degree_exclusion_over_algebraic_closure_C_X_claimed"])

    def test_frontier_changes_only_proved_cubic_flag(self):
        self.assertEqual(self.report["prior_frontier"], self.saved["preserved_frontier"])
        before, after = self.report["prior_frontier"], self.report["preserved_frontier"]
        self.assertEqual([key for key in before if before[key] != after[key]], ["all_cubic_polynomial_x_sections_excluded"])
        self.assertFalse(before["all_cubic_polynomial_x_sections_excluded"])
        self.assertTrue(after["all_cubic_polynomial_x_sections_excluded"])

    def test_higher_degree_denominators_rank_and_gates_remain_open(self):
        data = self.report["combined_original_polynomial_ansatz_conclusion"]
        for key in ("polynomial_x_degree_at_least_four_excluded", "sections_with_T_denominators_excluded",
                    "all_rational_sections_excluded", "original_exact_MW_rank_computed"):
            self.assertFalse(data[key])
        frontier = self.report["remaining_section_frontier"]
        self.assertEqual(frontier["nonzero_linear_pivot_charts_still_open"], [])
        self.assertTrue(frontier["higher_polynomial_degree_or_T_denominator_search_open"])
        self.assertEqual([frontier["original_free_rank_lower_bound"], frontier["original_free_rank_upper_bound"]], [0, 11])
        self.assertEqual(frontier["original_MW_torsion_order"], 1)
        self.assertEqual(self.report["preserved_frontier"]["closed_gates"], [])

    def test_rehashed_rank_or_full_no_section_overclaim_is_rejected(self):
        for key, value in (("original_free_rank_upper_bound", 0), ("higher_polynomial_degree_or_T_denominator_search_open", False)):
            changed = copy.deepcopy(self.report)
            changed["remaining_section_frontier"][key] = value
            with self.assertRaises(RuntimeError):
                audit.validate_certificate(self.rehash(changed))

    def test_rehashed_constant_field_scope_overclaim_is_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["combined_original_polynomial_ansatz_conclusion"]["entire_low_degree_exclusion_over_algebraic_closure_C_X_claimed"] = True
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(self.rehash(changed))

    def test_cached_derived_reports_are_immutable_through_returned_values(self):
        changed = audit.build_certificate()
        changed["shared_resultant_newton_certificate"]["rows"].clear()
        changed["finite_field_unit_ideal"]["Groebner_basis"] = ["z"]
        fresh = audit.build_certificate()
        self.assertEqual(len(fresh["shared_resultant_newton_certificate"]["rows"]), 3)
        self.assertEqual(fresh["finite_field_unit_ideal"]["Groebner_basis"], ["1"])


if __name__ == "__main__":
    unittest.main()
