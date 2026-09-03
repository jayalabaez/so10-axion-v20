import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import sympy as sp

import v100_original_section_existence_audit as audit


class OriginalSectionExistenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()
        _, cls.saved = audit.load_bound_inputs()
        cls.component = cls.report["cubic_vector_component_certificate"]
        cls.lattice = cls.report["conditional_rank_two_lattice"]
        cls.formulas = cls.report["difference_point_and_square_descent"]["actual_original_member_formulas"]

    def rehash(self, report):
        report["core_sha256"] = audit.canonical_sha(report)
        return report

    def test_canonical_lineage_roundtrip_and_validation(self):
        self.assertEqual(audit.canonical_sha(self.report), self.report["core_sha256"])
        self.assertEqual(json.loads(json.dumps(self.report)), self.report)
        self.assertEqual(self.report["input_core_hashes"], {
            "v99_route": audit.V99_ROUTE_CORE, "v99_master": audit.V99_MASTER_CORE,
            "v99_geometry": audit.V99_GEOMETRY_CORE})
        audit.validate_certificate(self.report)

    def test_portable_parent_source_hash_accepts_crlf(self):
        path = audit.ROOT / "v99_original_section_elimination_audit.py"
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
            if path == audit.V99_MASTER_PATH:
                data = json.loads(text)
                data["core_sha256"] = "0"*64
                return json.dumps(data)
            return text
        with patch.object(Path, "read_text", read):
            with self.assertRaisesRegex(RuntimeError, "canonical V99"):
                audit.build_certificate()

    def test_original_payload_equations_and_frontier_are_unchanged(self):
        self.assertEqual(self.report["coefficient_payload"], self.saved["coefficient_payload"])
        self.assertEqual(self.report["coefficient_payload_sha256"], self.saved["coefficient_payload_sha256"])
        self.assertEqual(self.report["original_equation_list_sha256"], self.saved["original_equation_list_sha256"])
        self.assertEqual(self.report["preserved_frontier"], self.saved["preserved_frontier"])
        self.assertEqual(self.report["existence_search_boundary"]["same_six_exceptional_equations_sha256"],
                         audit.canonical_sha(self.saved["exceptional_chart_exact_equations"]["equations"]))

    def test_original_jacobian_and_infinity_scaling_independently(self):
        T, u = audit.T, audit.u
        qa = T**3+audit.alpha*T*T+audit.gamma
        qb, qc, qe = audit.beta*T*T+audit.delta, -2*T**3, T**3+audit.epsilon
        expected = [-27*(12*qa*qe+qc*qc), -27*(72*qa*qc*qe-27*qb*qb*qe-2*qc**3)]
        actual = [audit.parse(value) for value in self.component["original_short_Weierstrass_A_B"]]
        infinity = [audit.parse(value) for value in self.component["infinity_A_B"]]
        for target, value, local, weight in zip(expected, actual, infinity, (8, 12)):
            self.assertEqual(sp.expand(value-target), 0)
            self.assertEqual(sp.expand(local-u**weight*value.subs(T, 1/u)), 0)

    def test_first_u_blowup_and_simple_root_derivative(self):
        u, X1, Y1 = audit.u, audit.X1, audit.Y1
        Ai, Bi = [audit.parse(value) for value in self.component["infinity_A_B"]]
        G = audit.parse(self.component["G"])
        original = (u*Y1)**2-(u*X1)**3-Ai*(u*X1)-Bi
        self.assertEqual(sp.expand(original/u**2-(Y1*Y1-u*G)), 0)
        self.assertEqual(sp.factor(G.subs(u, 0)), (X1+24)*(X1-12)**2)
        self.assertEqual(sp.diff(G, X1).subs({u: 0, X1: -24}), 1296)

    def test_second_u_blowup_smooth_chart_and_section_initial_point(self):
        u, X1, Z, W, z, r = audit.u, audit.X1, audit.Z, audit.W, audit.z, audit.r
        G = audit.parse(self.component["G"])
        second = audit.parse(self.component["second_u_chart_equation"])
        self.assertEqual(sp.expand(second-W*W+G.subs(X1, -24+u*Z)/u), 0)
        boundary = sp.expand(second.subs(u, 0))
        self.assertEqual(boundary, W*W-1296*Z-11664*audit.alpha)
        self.assertEqual(sp.diff(boundary, Z), -1296)
        at_point = sp.expand(boundary.subs({Z: 9*(z-audit.alpha), W: 108*r}))
        self.assertEqual(at_point, 11664*(r*r-z))

    def test_A1_resolution_second_chart_and_complete_exceptional_cover(self):
        u, v, Y1, V2 = audit.u, audit.v, audit.Y1, audit.V2
        U2 = sp.Symbol("U2")
        local = Y1*Y1-u*v
        transformed = sp.expand(local.subs({u: v*U2, Y1: v*V2})/v**2)
        self.assertEqual(transformed, V2*V2-U2)
        self.assertEqual(sp.diff(transformed, U2), -1)
        total_fiber = v*V2**2
        self.assertEqual(sp.degree(total_fiber, v), 1)
        self.assertEqual(sp.degree(total_fiber, V2), 2)
        # No exceptional projective point can have u=v=0: the conic then
        # forces Y1=0. Thus the u/v charts cover the conic; no chart is omitted.
        self.assertEqual(local.subs({u: 0, v: 0}), Y1*Y1)
        self.assertIn("entire exceptional conic", self.component["A1_chart_cover_complete"])

    def test_identity_component_first_x_chart_unit_and_attachment(self):
        rho, U, Yx, u = audit.rho, audit.U, audit.Yx, audit.u
        Ai, Bi = [audit.parse(value) for value in self.component["infinity_A_B"]]
        unit = audit.parse(self.component["first_x_chart_Hunit"])
        original = (rho*Yx)**2-rho**3-Ai.subs(u, rho*U)*rho-Bi.subs(u, rho*U)
        self.assertEqual(sp.expand(original/rho**2-Yx*Yx+rho*unit), 0)
        self.assertEqual(unit.subs({rho: 0, U: 0}), 1)
        self.assertEqual(unit.subs(U, 0), 1)
        self.assertIn("same first multiplicity2", self.component["identity_attachment"])

    def test_near_component_inverse_D6_correction_is_one(self):
        d6 = self.saved["conditional_height_and_rank_compatibility"]["geometric_D6_minimum_height_certificate"]
        affine, finite = sp.Matrix(d6["affine_D6_Cartan_matrix"]), sp.Matrix(d6["D6_Cartan_matrix"])
        self.assertEqual(affine[0, 2], -1)
        self.assertEqual(affine[1, 2], -1)
        self.assertEqual(finite.inv()[0, 0], 1)
        self.assertEqual(self.component["pinned_D6_component_index"], 1)
        self.assertEqual(self.component["inverse_Cartan_self_and_mutual_correction"], "1")

    def test_exact_finite_nonintersection_and_infinity_intersection_two(self):
        difference = audit.parse(self.lattice["finite_x_difference"])
        self.assertEqual(sp.expand(difference-18*audit.z*(audit.K1-audit.K2)), 0)
        jet = sp.Poly(audit.parse(self.lattice["second_chart_W_difference"]), audit.u)
        self.assertEqual(jet.nth(0), 0)
        self.assertEqual(jet.nth(1), 0)
        self.assertEqual(sp.expand(jet.nth(2)-108*audit.r*(audit.K1-audit.K2)), 0)
        self.assertEqual(self.lattice["finite_intersections"], 0)
        self.assertEqual(self.lattice["P1_dot_P2"], 2)

    def test_pairing_gram_and_diagonal_basis_independently(self):
        height = 2*2+2*0-1
        pairing = 2+0+0-2-1
        gram = sp.Matrix([[height, pairing], [pairing, height]])
        change = sp.Matrix([[1, 1], [1, -1]])
        self.assertEqual(gram, sp.Matrix(self.lattice["Gram_P1_P2"]))
        self.assertEqual(gram, sp.Matrix([[3, -1], [-1, 3]]))
        self.assertEqual(gram.det(), 8)
        self.assertEqual(change.T*gram*change, sp.diag(4, 8))
        self.assertEqual(abs(change.det()), 2)
        self.assertEqual(self.lattice["index_of_ZS_plus_ZA_in_ZP1_plus_ZP2"], 2)

    def test_saturation_fundamental_parallelogram_bound_and_scope(self):
        values = [3*a*a-2*a*b+3*b*b for a in (-sp.Rational(1, 2), sp.Rational(1, 2))
                  for b in (-sp.Rational(1, 2), sp.Rational(1, 2))]
        self.assertEqual(max(values), 2)
        # This also follows without vertex reasoning from the three absolute
        # term bounds, valid for every real |a|,|b|<=1/2.
        self.assertEqual(sp.Rational(3, 4)+sp.Rational(1, 2)+sp.Rational(3, 4), 2)
        data = self.lattice["conditional_saturation_in_full_geometric_MW"]
        self.assertLess(2, sp.Rational(data["saved_minimum_nonzero_height"]))
        self.assertTrue(data["rank_two_span_is_saturated"])
        self.assertFalse(data["full_geometric_MW_rank_is_two_claimed"])
        self.assertTrue(self.lattice["no_T_base_cover_or_height_rescaling"])

    def test_universal_opposite_sign_square_identity_independently(self):
        g, h, k, sigma, pi = sp.symbols("g h k sigma pi")
        D, Q = sigma*sigma-4*pi, k*k-sigma*k+pi
        N = (g*sigma+2*h)*k-(2*g*pi+h*sigma)
        self.assertEqual(sp.expand(N*N-D*(g*k+h)**2-4*(g*g*pi+g*h*sigma+h*h)*Q), 0)
        data = self.report["difference_point_and_square_descent"]["universal_sign_change_identity"]
        self.assertEqual(data["exact_identity_residual"], "0")
        self.assertFalse(data["curve_twist_or_coefficient_change_used"])

    def test_universal_interpolation_has_opposite_signs_at_both_roots(self):
        g, h, k1, k2 = sp.symbols("g h k1 k2")
        sigma, pi = k1+k2, k1*k2
        numerator = lambda k: (g*sigma+2*h)*k-(2*g*pi+h*sigma)
        self.assertEqual(sp.cancel(numerator(k1)/(k1-k2)-(g*k1+h)), 0)
        self.assertEqual(sp.cancel(numerator(k2)/(k1-k2)+(g*k2+h)), 0)

    def test_original_reconstruction_matches_difference_chord_formula(self):
        # Arbitrary parameter values test algebraic identities only; these do
        # not solve the six equations and are not asserted to be curve points.
        T, K = audit.T, audit.K
        values = {audit.alpha: 2, audit.beta: 3, audit.gamma: 3, audit.delta: 2, audit.epsilon: 5,
                  audit.z: 4, audit.H: 3, audit.sigma_K: 5, audit.pi_K: 6}
        source = self.saved["quadratic_trace_construction"]["actual_original_member_formulas"]["original_coefficient_reconstruction"]
        solved = {key: audit.parse(value).subs(values) for key, value in source.items()}
        x = -24*T**3+9*(2*T*T+solved["q"]*T+solved["p"])
        y = 216*(T**4+3*T**3+K*T*T+solved["L"]*T+solved["M"])
        x1, x2, y1, y2 = x.subs(K, 3), x.subs(K, 2), y.subs(K, 3), y.subs(K, 2)
        slope = sp.cancel((-y2-y1)/(x2-x1))
        expected_x = sp.expand(slope*slope-x1-x2)
        expected_y = sp.expand(slope*(x1-expected_x)-y1)
        actual_x = audit.parse(self.formulas["x_difference"]).subs(values)
        actual_y = audit.parse(self.formulas["y_difference_times_j"]).subs(values)/2
        self.assertEqual(sp.expand(expected_x-actual_x), 0)
        self.assertEqual(sp.expand(expected_y-actual_y), 0)

    def test_difference_non_cancellation_degrees_and_leading_terms(self):
        values = {audit.alpha: 2, audit.beta: 3, audit.gamma: 3, audit.delta: 2, audit.epsilon: 5,
                  audit.z: 4, audit.H: 3, audit.sigma_K: 5, audit.pi_K: 6}
        xp = sp.Poly(audit.parse(self.formulas["x_difference"]).subs(values), audit.T)
        yp = sp.Poly(audit.parse(self.formulas["y_difference_times_j"]).subs(values), audit.T)
        self.assertEqual([xp.degree(), yp.degree()], [8, 12])
        self.assertEqual([xp.LC(), yp.LC()], [36, -432])
        D = audit.sigma_K**2-4*audit.pi_K
        self.assertEqual(sp.cancel(audit.parse(self.formulas["leading_x"])-144/(audit.z*D)), 0)
        self.assertEqual(sp.cancel(audit.parse(self.formulas["leading_y_times_j"])+1728/(audit.z*D)), 0)
        self.assertEqual(self.formulas["input_degrees_T_D0_S_V_W"], [3, 2, 4, 4])

    def test_difference_poles_height_and_primitivity(self):
        self.assertEqual(8-4, 4)
        self.assertEqual(12-6, 6)
        pole_intersection = sp.Rational(4, 2)
        self.assertEqual(4+2*pole_intersection, 8)
        self.assertEqual(self.formulas["height"], 8)
        self.assertLess(sp.Rational(8, 4), sp.Rational(5, 2))
        self.assertIn("primitive", self.formulas["conditional_primitive_difference"])

    def test_equal_nonsquare_classes_give_square_product_without_toy_existence_claim(self):
        X = audit.X
        z_toy, D_toy, j_toy = X, X, X
        self.assertEqual(j_toy*j_toy-z_toy*D_toy, 0)
        self.assertEqual(sp.Poly(z_toy, X).degree() % 2, 1)
        self.assertTrue(self.formulas["z_itself_may_be_nonsquare_for_this_difference_point"])
        self.assertTrue(self.formulas["does_not_make_individual_cubic_points_original_when_z_nonsquare"])
        self.assertFalse(self.formulas["actual_z_H_solution_or_original_point_constructed"])

    def test_galois_matrices_and_fixed_dimensions_are_independent(self):
        rows = self.report["galois_squareclass_cases"]["rows"]
        self.assertEqual([row["constructed_Q_span_fixed_dimension"] for row in rows], [2, 1, 1, 0, 0])
        S, A, eye = sp.Matrix([1, 1]), sp.Matrix([1, -1]), sp.eye(2)
        for row in rows:
            matrices = [sp.Matrix(value) for value in row["two_generator_matrices_on_P1_P2"]]
            self.assertEqual(all(m*S == S for m in matrices), row["trace_S_fixed"])
            self.assertEqual(all(m*A == A for m in matrices), row["difference_A_fixed"])
            constraints = (matrices[0]-eye).col_join(matrices[1]-eye)
            self.assertEqual(len(constraints.nullspace()), row["constructed_Q_span_fixed_dimension"])

    def test_integral_fixed_sublattices_and_no_multiple_descent_repair(self):
        data = self.report["galois_squareclass_cases"]
        self.assertEqual([row["integral_fixed_sublattice_in_saturated_span"] for row in data["rows"]],
                         ["Z*P1+Z*P2", "Z*S", "Z*A", "0", "0"])
        self.assertIn("2n times it is zero", data["noninvariant_eigenpoint_multiple_cannot_repair_descent"])
        self.assertTrue(data["zero_fixed_dimension_is_not_a_full_original_rank_zero_claim"])
        self.assertFalse(data["actual_squareclasses_of_a_solved_z_H_candidate_computed"])

    def test_target_divisors_restrict_to_ruling_and_ratio_obstruction(self):
        data = self.formulas["conditional_rank_one_target_obstruction"]
        frontier = self.report["preserved_frontier"]
        divisors = [frontier["doubled_charge_conditional_section_height_S_F"],
                    frontier["unit_charge_conditional_section_height_S_F"]]
        self.assertEqual(data["bound_target_divisors_S_F"], divisors)
        self.assertEqual([str(sp.Rational(value[0], 8)) for value in divisors], ["37/8", "37/2"])
        self.assertEqual(data["target_height_over_difference_height"], ["37/8", "37/2"])
        self.assertEqual(data["ratios_are_rational_squares"], [False, False])
        self.assertIn("S.F=1,F.F=0", data["ruling_restriction"])
        self.assertFalse(data["actual_section_existence_or_rank_lower_bound_changed"])

    def test_no_actual_solution_generic_elimination_rank_or_gate_claim(self):
        boundary = self.report["existence_search_boundary"]
        for key in ("actual_rational_z_H_solution_found", "generic_exceptional_chart_exclusion_proved",
                    "generic_Q_X_Groebner_certificate_obtained", "specialized_QQ_Groebner_certificate_obtained",
                    "bounded_exploratory_runs_used_as_proof", "new_difference_route_changes_the_original_cubic_point_test"):
            self.assertFalse(boundary[key])
        self.assertIn("All nonzero-linear-pivot charts also remain open", boundary["next_exact_search"])
        frontier = self.report["preserved_frontier"]
        self.assertEqual([frontier["original_free_rank_lower_bound"], frontier["original_free_rank_upper_bound"]], [0, 11])
        self.assertEqual(frontier["original_MW_torsion_order"], 1)
        self.assertFalse(frontier["nonzero_original_section_constructed"])
        self.assertEqual(frontier["closed_gates"], [])

    def test_rehashed_existence_overclaim_is_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["existence_search_boundary"]["actual_rational_z_H_solution_found"] = True
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(self.rehash(changed))

    def test_rehashed_height_or_descent_overclaim_is_rejected(self):
        for section, key, value in (
                ("conditional_rank_two_lattice", "each_cubic_height", 4),
                ("galois_squareclass_cases", "zero_fixed_dimension_is_not_a_full_original_rank_zero_claim", False)):
            changed = copy.deepcopy(self.report)
            changed[section][key] = value
            with self.assertRaises(RuntimeError):
                audit.validate_certificate(self.rehash(changed))

    def test_returned_reports_cannot_mutate_pure_derived_cache(self):
        changed = audit.build_certificate()
        changed["conditional_rank_two_lattice"]["Gram_P1_P2"][0][0] = 0
        changed["galois_squareclass_cases"]["rows"].clear()
        fresh = audit.build_certificate()
        self.assertEqual(fresh["conditional_rank_two_lattice"]["Gram_P1_P2"], [[3, -1], [-1, 3]])
        self.assertEqual(len(fresh["galois_squareclass_cases"]["rows"]), 5)


if __name__ == "__main__":
    unittest.main()
