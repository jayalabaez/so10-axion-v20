import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import sympy as sp

import v99_original_section_elimination_audit as audit


class OriginalSectionEliminationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()
        cls.equations, cls.solved = audit.source_algebra()
        cls.formulas = cls.report["quadratic_trace_construction"]["actual_original_member_formulas"]

    def rehash(self, report):
        report["core_sha256"] = audit.canonical_sha(report)
        return report

    def test_canonical_lineage_and_roundtrip(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        self.assertEqual(json.loads(json.dumps(self.report)), self.report)
        self.assertEqual(self.report["input_core_hashes"], {
            "v98_route": audit.V98_ROUTE_CORE, "v98_master": audit.V98_MASTER_CORE,
            "v98_geometry": audit.V98_GEOMETRY_CORE, "v95_generic_K3": audit.V95_GEOMETRY_CORE})
        audit.validate_certificate(self.report)

    def test_portable_source_hash_on_crlf(self):
        path = audit.ROOT / "v98_original_square_section_audit.py"
        data = path.read_bytes().replace(b"\r\n", b"\n")
        expected = audit.portable_sha(path)
        with patch.object(Path, "read_bytes", return_value=data.replace(b"\n", b"\r\n")):
            self.assertEqual(audit.portable_sha(path), expected)

    def test_source_pins_remain_fresh_after_pure_algebra_cache(self):
        with patch.object(audit, "portable_sha", return_value="0"*64):
            with self.assertRaisesRegex(RuntimeError, "source/test pin"):
                audit.build_certificate()

    def test_parent_master_core_tampering_is_rejected(self):
        old = Path.read_text
        def read(path, *args, **kwargs):
            value = old(path, *args, **kwargs)
            if path == audit.V98_MASTER_PATH:
                data = json.loads(value)
                data["core_sha256"] = "0"*64
                return json.dumps(data)
            return value
        with patch.object(Path, "read_text", read):
            with self.assertRaisesRegex(RuntimeError, "canonical V98"):
                audit.build_certificate()

    def test_original_equations_and_nonzero_pivots_are_preserved(self):
        data = self.report["exceptional_chart_exact_equations"]
        self.assertEqual(data["nonzero_ell_charts_from_V98_still_present"], [1, 2, 3])
        self.assertFalse(data["nonzero_ell_charts_solved_or_excluded_here"])
        self.assertEqual(data["required_nonzero_factors"], ["z", "2*H-alpha", "a=-24*z*(2*H-alpha)"])
        a = audit.parse(data["quadratic_coefficients"]["a"])
        self.assertEqual(sp.expand(a+24*audit.z*(2*audit.H-audit.alpha)), 0)
        original = audit.previous.previous.universal_algebra()["remaining"]["reduced_equations_T3_through_T0"]
        self.assertEqual(self.report["original_equation_list_sha256"], audit.canonical_sha(original))

    def test_six_normalized_equations_are_polynomials(self):
        data = self.report["exceptional_chart_exact_equations"]
        rows = data["equations"]
        self.assertEqual([(row["row"], row["kind"]) for row in rows],
                         [(1, "ell"), (1, "mu"), (2, "ell"), (2, "mu"), (3, "ell"), (3, "mu")])
        self.assertEqual([row["degrees_z_H"] for row in rows], [[8, 6], [10, 7], [9, 7], [11, 8], [12, 9], [14, 10]])
        variables = (audit.z, audit.H, audit.alpha, audit.beta, audit.gamma, audit.delta, audit.epsilon)
        for row in rows:
            self.assertTrue(audit.parse(row["polynomial"]).is_polynomial(*variables))
            self.assertEqual(row["divide_remainder_by"], "z^2")

    def test_six_equations_independently_match_pseudodivision(self):
        values = {audit.alpha: 2, audit.beta: 3, audit.gamma: 3, audit.delta: 2, audit.epsilon: 5,
                  audit.z: 4, audit.H: 3}
        equations = [sp.Poly(value.subs(values), audit.K, domain=sp.QQ) for value in self.equations]
        normalized = self.report["exceptional_chart_exact_equations"]["equations"]
        for i, row in enumerate(equations[1:]):
            ell = audit.parse(normalized[2*i]["polynomial"]).subs(values)*16
            mu = audit.parse(normalized[2*i+1]["polynomial"]).subs(values)*16
            remainder = sp.prem(row, equations[0]).as_expr()
            self.assertEqual(sp.expand(remainder-ell*audit.K-mu), 0)

    def test_source_reconstruction_K_degrees_and_coefficients(self):
        K, z = audit.K, audit.z
        self.assertEqual(sp.degree(self.solved["q"], K), 0)
        self.assertEqual([sp.degree(self.solved[key], K) for key in ("p", "L", "M")], [1, 1, 2])
        self.assertEqual(sp.expand(self.solved["p"].coeff(K, 1)-2*z), 0)
        self.assertEqual(sp.Poly(self.solved["M"], K).nth(2), -sp.Rational(1, 2))

    def test_actual_original_coordinates_reduce_modulo_quadratic(self):
        T, K, z, H, alpha = audit.T, audit.K, audit.z, audit.H, audit.alpha
        D0, S, V = [audit.parse(self.formulas[key]) for key in ("D0", "S", "V")]
        original_x = -24*T**3+9*((z-alpha)*T*T+self.solved["q"]*T+self.solved["p"])
        original_y_over_r = 108*(T**4+H*T**3+K*T*T+self.solved["L"]*T+self.solved["M"])
        Q = K*K-audit.sigma_K*K+audit.pi_K
        self.assertEqual(sp.expand(original_x-D0-18*z*K), 0)
        self.assertEqual(sp.expand(sp.rem(original_y_over_r-108*(S*K+V), Q, K)), 0)

    def test_universal_trace_residual_identity_independently(self):
        d, e, g, j, A, B, sigma, pi, k = sp.symbols("d e g j A B sigma pi k")
        curve = (g*k+j)**2-(d+e*k)**3-A*(d+e*k)-B
        Q = k*k-sigma*k+pi
        quotient, remainder = sp.div(curve, Q, k)
        xt = (g/e)**2-2*d-e*sigma
        yt = -(g/e)*xt-j+g*d/e
        kappa = (xt-d)/e
        self.assertEqual(sp.cancel(quotient.subs(k, kappa)), 0)
        self.assertEqual(sp.cancel(yt*yt-xt**3-A*xt-B-remainder.subs(k, kappa)), 0)
        self.assertEqual(self.report["quadratic_trace_construction"]["universal_group_law_identity"]["trace_identity_residual"], "0")

    def test_actual_Jacobian_residual_not_a_changed_curve(self):
        T, K = audit.T, audit.K
        # These values do not solve the chart; this checks the residual identity,
        # not an invented point. Sigma,pi can be arbitrary for this identity.
        values = {audit.alpha: 2, audit.beta: 3, audit.gamma: 3, audit.delta: 2, audit.epsilon: 5,
                  audit.z: 4, audit.H: 3, audit.sigma_K: 5, audit.pi_K: 7}
        solved = {key: value.subs(values) for key, value in self.solved.items()}
        x = -24*T**3+9*((4-2)*T*T+solved["q"]*T+solved["p"])
        y = 216*(T**4+3*T**3+K*T*T+solved["L"]*T+solved["M"])
        qa, qb, qc, qe = T**3+2*T*T+3, 3*T*T+2, -2*T**3, T**3+5
        I, J = 12*qa*qe+qc*qc, 72*qa*qc*qe-27*qb*qb*qe-2*qc**3
        A, B = -27*I, -27*J
        xt = audit.parse(self.formulas["x_trace"]).subs(values)
        yt = 2*audit.parse(self.formulas["y_trace_over_r"]).subs(values)
        Q = K*K-5*K+7
        remainder = sp.rem(sp.expand(y*y-x**3-A*x-B), Q, K)
        D0 = audit.parse(self.formulas["D0"]).subs(values)
        kappa = (xt-D0)/72
        self.assertEqual(sp.expand(yt*yt-xt**3-A*xt-B-remainder.subs(K, kappa)), 0)

    def test_distinct_conjugate_points_can_have_nonzero_rational_trace(self):
        # Universal-lemma example over C(X), not the frozen theory member.
        X = audit.X
        k1, k2 = sp.sqrt(X), -sp.sqrt(X)
        A, B = 2-X, 1+X
        for k in (k1, k2):
            self.assertEqual(sp.expand((1+k)**2-k**3-A*k-B), 0)
        slope = sp.simplify(((1+k2)-(1+k1))/(k2-k1))
        xt = sp.simplify(slope*slope-k1-k2)
        yt = sp.simplify(-slope*xt-1)
        self.assertEqual((xt, yt), (1, -2))
        self.assertEqual(sp.expand(yt*yt-xt**3-A*xt-B), 0)
        self.assertEqual(sp.Poly(4*X, X).terms()[0][0][0] % 2, 1)

    def test_repeated_root_gives_tangent_and_double_point(self):
        k = audit.K
        x, y = k, 1-k/2
        curve_residual = sp.expand(y*y-x**3+x-1)
        self.assertEqual(sp.rem(curve_residual, k*k, k), 0)
        xt, yt = sp.Rational(1, 4), -sp.Rational(7, 8)
        self.assertEqual(yt*yt-xt**3+xt-1, 0)
        tangent = sp.Rational(-1, 2)
        self.assertEqual(xt, tangent*tangent)
        self.assertEqual(yt, -tangent*xt-1)
        self.assertIn("2*P0", self.report["repeated_root_and_descent"]["repeated_root"])
        self.assertTrue(self.report["repeated_root_and_descent"]["repeated_root_excluded_on_actual_generic_K3"])

    def test_no_roots_at_K_infinity_or_discriminant_division(self):
        data = self.report["repeated_root_and_descent"]
        self.assertIn("a!=0", data["no_K_infinity_loss"])
        self.assertTrue(self.formulas["no_K_discriminant_denominator"])
        self.assertEqual(self.formulas["only_variable_denominators_for_trace"], ["z", "a", "r"])
        self.assertTrue(data["quadratic_K_discriminant_need_not_be_square_for_trace"])

    def test_original_trace_still_requires_z_square(self):
        data = self.report["exceptional_chart_exact_equations"]
        self.assertFalse(data["K_discriminant_square_required_for_the_trace_point"])
        self.assertTrue(data["K_discriminant_square_required_for_a_cubic_point"])
        self.assertTrue(self.report["repeated_root_and_descent"]["z_square_remains_required_for_original_trace"])
        yt = audit.r*audit.parse(self.formulas["y_trace_over_r"])
        self.assertEqual(sp.expand(yt.subs(audit.r, -audit.r)+yt), 0)
        self.assertNotEqual(yt, 0)

    def test_trace_leading_terms_are_nonzero_and_degree_four_six(self):
        x = sp.Poly(audit.parse(self.formulas["x_trace"]), audit.T)
        y_over_r = sp.Poly(audit.parse(self.formulas["y_trace_over_r"]), audit.T)
        self.assertEqual([x.degree(), y_over_r.degree()], [4, 6])
        self.assertEqual(sp.cancel(x.LC()-36/audit.z), 0)
        self.assertEqual(sp.cancel(y_over_r.LC()+216/audit.z**2), 0)
        self.assertTrue(self.formulas["identity_point_is_not_produced"])
        self.assertFalse(self.formulas["concrete_original_point_has_been_found"])

    def test_generic_K3_infinity_point_and_height_independently(self):
        r, z = audit.r, audit.z
        x_infinity, y_infinity = 36/z, -216*r/z**2
        self.assertEqual(sp.cancel((y_infinity*y_infinity-x_infinity**3).subs(r*r, z)), 0)
        self.assertNotEqual(x_infinity, 0)
        data = self.report["conditional_height_and_rank_compatibility"]
        self.assertEqual(data["chi_O"], 2)
        self.assertEqual(data["finite_I1_count"], 16)
        self.assertTrue(data["infinity_identity_component_met"])
        self.assertEqual(2*data["chi_O"]+2*data["trace_intersection_with_zero_section"]-data["total_Cartan_correction"], 4)
        self.assertEqual(data["conditional_geometric_height"], 4)
        self.assertFalse(data["original_section_existence_proved"])

    def test_height_assumptions_cannot_be_changed_silently(self):
        _, _, k3 = audit.load_bound_inputs()
        for key, value in (("holomorphic_Euler_characteristic", 1), ("infinity_orders_A_B_Delta", [2, 3, 6])):
            changed = copy.deepcopy(k3)
            changed[key] = value
            with self.assertRaises(RuntimeError):
                audit.conditional_height(changed, self.report["preserved_frontier"])

    def test_affine_D6_multiplicities_and_height_bound_independently(self):
        data = self.report["conditional_height_and_rank_compatibility"]["geometric_D6_minimum_height_certificate"]
        affine = sp.Matrix(data["affine_D6_Cartan_matrix"])
        multiplicities = sp.Matrix(data["fiber_multiplicities_including_identity_component"])
        self.assertEqual(affine*multiplicities, sp.zeros(7, 1))
        self.assertEqual(list(multiplicities), [1, 1, 2, 2, 2, 1, 1])
        finite = sp.Matrix(data["D6_Cartan_matrix"])
        inverse = finite.inv()
        allowed = [i for i in range(1, 7) if multiplicities[i] == 1]
        self.assertEqual(allowed, [1, 5, 6])
        corrections = [inverse[i-1, i-1] for i in allowed]
        self.assertEqual(corrections, [1, sp.Rational(3, 2), sp.Rational(3, 2)])
        self.assertEqual(4-max(corrections), sp.Rational(5, 2))
        self.assertIn("no ramified cover of the T base", data["extension_scope"])

    def test_repeated_root_excluded_and_conditional_trace_primitive(self):
        data = self.report["conditional_height_and_rank_compatibility"]
        self.assertEqual(sp.Rational(4, 4), 1)
        self.assertLess(sp.Rational(4, 4), sp.Rational(5, 2))
        self.assertTrue(data["repeated_root_subchart_exclusion"]["excluded_over_algebraic_closure_C_X"])
        self.assertTrue(data["conditional_geometric_primitivity"]["primitive_modulo_torsion"])
        self.assertTrue(data["conditional_geometric_primitivity"]["trace_not_divisible_by_any_integer_abs_at_least_two"])
        self.assertTrue(data["conditional_geometric_primitivity"]["this_does_not_supply_a_full_MW_basis"])

    def test_conditional_two_point_independence_keeps_field_scope(self):
        data = self.report["conditional_height_and_rank_compatibility"]["conditional_two_cubic_points_independent"]
        self.assertEqual(data["each_cubic_point_integral_degree_bounds"], [3, 4])
        self.assertEqual(data["each_nonzero_cubic_height_at_most"], 4)
        self.assertNotIn(1, {m+n for m in (-1, 1) for n in (-1, 1)})
        self.assertTrue(data["independent_over_Q_modulo_torsion_over_L_T"])
        self.assertTrue(data["original_rank_at_least_two_if_z_and_K_discriminant_both_squares_and_chart_solution_exists"])
        self.assertTrue(data["nonsquare_K_discriminant_only_forces_extension_rank_at_least_two"])
        self.assertFalse(data["unconditional_original_rank_lower_bound_raised"])

    def test_rank_one_height_ratio_obstruction_is_exact_and_conditional(self):
        data = self.report["conditional_height_and_rank_compatibility"]["rank_one_compatibility"]
        self.assertEqual(data["target_height_over_trace_height"], ["37/4", "37"])
        self.assertEqual(data["bound_conditional_target_height_divisors_S_F"], [
            self.report["preserved_frontier"]["doubled_charge_conditional_section_height_S_F"],
            self.report["preserved_frontier"]["unit_charge_conditional_section_height_S_F"]])
        self.assertIn("S.F=1 and F.F=0", data["restriction_to_generic_ruling"])
        self.assertEqual(data["ratios_are_rational_squares"], [False, False])
        for value in (sp.Rational(37, 4), sp.Rational(148, 4)):
            self.assertEqual(sp.factorint(value.p)[37], 1)
            self.assertFalse(audit.rational_square(value))
        for value in (0, 1, sp.Rational(9, 4), 4):
            self.assertTrue(audit.rational_square(value))
        self.assertFalse(audit.rational_square(-1))
        self.assertFalse(data["unconditional_original_rank_lower_bound_raised"])

    def test_no_nonzero_multiple_can_repair_sign_descent(self):
        data = self.report["repeated_root_and_descent"]
        self.assertIn("2*n*trace=0", data["no_nonzero_multiple_repairs_nonsquare_z_descent"])
        self.assertTrue(self.report["conditional_height_and_rank_compatibility"]["conditional_infinite_order"])
        self.assertFalse(data["change_of_curve_or_quadratic_twist_used"])

    def test_no_equation_solution_rank_increase_or_gate_closure_is_claimed(self):
        chart = self.report["exceptional_chart_exact_equations"]
        self.assertFalse(chart["six_equations_solved_over_C_X"])
        self.assertFalse(chart["candidate_z_H_found"])
        data = self.report["preserved_frontier"]
        self.assertEqual([data["original_free_rank_lower_bound"], data["original_free_rank_upper_bound"]], [0, 11])
        self.assertEqual(data["original_MW_torsion_order"], 1)
        self.assertFalse(data["nonzero_original_section_constructed"])
        self.assertEqual(data["closed_gates"], [])

    def test_rehashed_existence_overclaim_is_rejected(self):
        data = copy.deepcopy(self.report)
        data["exceptional_chart_exact_equations"]["candidate_z_H_found"] = True
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(self.rehash(data))

    def test_rehashed_height_or_descent_mutation_is_rejected(self):
        for section, key, value in (
                ("conditional_height_and_rank_compatibility", "conditional_geometric_height", 0),
                ("repeated_root_and_descent", "z_square_remains_required_for_original_trace", False)):
            data = copy.deepcopy(self.report)
            data[section][key] = value
            with self.assertRaises(RuntimeError):
                audit.validate_certificate(self.rehash(data))

    def test_cached_algebra_is_not_mutable_through_returned_reports(self):
        report = audit.build_certificate()
        report["exceptional_chart_exact_equations"]["equations"].clear()
        report["quadratic_trace_construction"]["actual_original_member_formulas"]["x_trace"] = "0"
        fresh = audit.build_certificate()
        self.assertEqual(len(fresh["exceptional_chart_exact_equations"]["equations"]), 6)
        self.assertNotEqual(fresh["quadratic_trace_construction"]["actual_original_member_formulas"]["x_trace"], "0")


if __name__ == "__main__":
    unittest.main()
