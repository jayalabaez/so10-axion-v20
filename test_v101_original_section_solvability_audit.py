import copy
import json
from math import gcd
from pathlib import Path
import unittest
from unittest.mock import patch

import sympy as sp

import v101_original_section_solvability_audit as audit


class OriginalSectionSolvabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()
        _, cls.saved, cls.saved99 = audit.load_bound_inputs()
        cls.newton = cls.report["transformed_newton_boundary_certificate"]
        cls.saturation = cls.report["universal_saturation_identity"]
        cls.finite = cls.report["specialized_finite_field_certificate"]

    def rehash(self, report):
        report["core_sha256"] = audit.canonical_sha(report)
        return report

    def test_canonical_lineage_serialization_and_validation(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        self.assertEqual(json.loads(json.dumps(self.report)), self.report)
        self.assertEqual(self.report["input_core_hashes"]["v100_route"], audit.V100_ROUTE_CORE)
        self.assertEqual(self.report["input_core_hashes"]["v100_master"], audit.V100_MASTER_CORE)
        self.assertEqual(self.report["input_core_hashes"]["v100_geometry"], audit.V100_GEOMETRY_CORE)
        audit.validate_certificate(self.report)

    def test_portable_hash_accepts_crlf_checkout(self):
        path = audit.ROOT / "v100_original_section_existence_audit.py"
        data = path.read_bytes().replace(b"\r\n", b"\n")
        expected = audit.portable_sha(path)
        with patch.object(Path, "read_bytes", return_value=data.replace(b"\n", b"\r\n")):
            self.assertEqual(audit.portable_sha(path), expected)

    def test_source_pins_are_checked_after_pure_cache(self):
        with patch.object(audit, "portable_sha", return_value="0"*64):
            with self.assertRaisesRegex(RuntimeError, "source/test pin"):
                audit.build_certificate()

    def test_changed_master_core_is_rejected(self):
        old = Path.read_text
        def read(path, *args, **kwargs):
            text = old(path, *args, **kwargs)
            if path == audit.V100_MASTER_PATH:
                data = json.loads(text)
                data["core_sha256"] = "0"*64
                return json.dumps(data)
            return text
        with patch.object(Path, "read_text", read):
            with self.assertRaisesRegex(RuntimeError, "canonical V100"):
                audit.build_certificate()

    def test_original_coefficients_equations_and_preserved_frontier_bound(self):
        self.assertEqual(self.report["coefficient_payload"], self.saved["coefficient_payload"])
        self.assertEqual(self.report["original_equation_list_sha256"], self.saved["original_equation_list_sha256"])
        self.assertEqual(self.report["six_exceptional_equation_list_sha256"],
                         self.saved["existence_search_boundary"]["same_six_exceptional_equations_sha256"])
        self.assertEqual(self.report["preserved_frontier"], self.saved["preserved_frontier"])
        self.assertEqual([int(audit.SPECIAL_VALUES[p]) for p in audit.PARAMETERS], [2, 3, 3, 2, 5])

    def test_coordinate_change_has_exact_inverse_and_unit_denominator(self):
        z, H, w, alpha = audit.z, audit.H, audit.w, audit.alpha
        forward = z+4*H-sp.Rational(3, 2)*alpha
        inverse = (w-z+sp.Rational(3, 2)*alpha)/4
        self.assertEqual(sp.expand(forward.subs(H, inverse)-w), 0)
        self.assertEqual(sp.expand(inverse.subs(w, forward)-H), 0)
        self.assertNotEqual(4 % 101, 0)
        self.assertTrue(self.newton["is_invertible_over_Q_X_and_over_Z_localized_at_101"])

    def test_universal_transformation_matches_frozen_six_rows(self):
        inverse = (audit.w-audit.z+sp.Rational(3, 2)*audit.alpha)/4
        source = self.saved99["exceptional_chart_exact_equations"]["equations"]
        for row, original in zip(self.newton["rows"], source):
            actual = audit.parse(row["universal_polynomial_z_w"])
            expected = audit.parse(original["polynomial"]).subs(audit.H, inverse)
            self.assertEqual(sp.expand(actual-expected), 0)

    def test_integer_convex_hull_known_polygon_and_collinear_points(self):
        points = [(0, 0), (1, 0), (2, 0), (2, 2), (1, 1), (0, 2), (0, 1)]
        self.assertEqual(audit.convex_hull(points), ((0, 0), (2, 0), (2, 2), (0, 2)))
        self.assertEqual(audit.outward_rays(audit.convex_hull(points)),
                         ((-1, 0), (0, -1), (0, 1), (1, 0)))
        with self.assertRaises(RuntimeError):
            audit.convex_hull([(0, 0), (1, 0), (2, 0)])

    def test_hulls_and_vertex_units_at_both_specializations(self):
        z, w = audit.z, audit.w
        for row in self.newton["rows"]:
            universal = sp.Poly(audit.parse(row["universal_polynomial_z_w"]), z, w)
            special = sp.Poly(universal.as_expr().subs(audit.SPECIAL_VALUES), z, w, domain=sp.QQ)
            denominator, integer = special.clear_denoms()
            mod = integer.set_modulus(101)
            expected = tuple(tuple(point) for point in row["newton_hull_CCW"])
            self.assertEqual(audit.convex_hull(universal.monoms()), expected)
            self.assertEqual(audit.convex_hull(special.monoms()), expected)
            self.assertEqual(audit.convex_hull(mod.monoms()), expected)
            self.assertEqual(int(denominator), row["cleared_constant_denominator"])
            self.assertNotEqual(int(denominator) % 101, 0)
            for point, value in zip(expected, row["vertex_coefficients_mod101"]):
                self.assertNotEqual(special.coeff_monomial(point), 0)
                self.assertEqual(int(mod.coeff_monomial(point)) % 101, value)
                self.assertNotEqual(value, 0)

    def test_edge_rays_independently_from_support_pairs(self):
        # Independent O(n^3) support-pair enumeration for the first polygon.
        # It does not use the monotone-chain implementation being tested.
        row = self.newton["rows"][0]
        points = sp.Poly(audit.parse(row["universal_polynomial_z_w"]), audit.z, audit.w).monoms()
        rays = set()
        for p in points:
            for q in points:
                dx, dy = q[0]-p[0], q[1]-p[1]
                divisor = gcd(abs(dx), abs(dy))
                if not divisor:
                    continue
                ray = (dy//divisor, -dx//divisor)
                bound = p[0]*ray[0]+p[1]*ray[1]
                if all(m[0]*ray[0]+m[1]*ray[1] <= bound for m in points):
                    rays.add(ray)
        self.assertEqual(rays, {tuple(ray) for ray in row["primitive_outward_rays"]})

    def test_common_rays_exhaustive_and_only_two_are_poles(self):
        sets = [{tuple(ray) for ray in row["primitive_outward_rays"]} for row in self.newton["rows"]]
        common = sorted(set.intersection(*sets))
        self.assertEqual(common, [(-3, 1), (0, -1), (1, 1)])
        self.assertEqual([ray for ray in common if max(ray) > 0], [(-3, 1), (1, 1)])
        self.assertEqual(self.newton["common_possible_pole_rays"], [[-3, 1], [1, 1]])

    def test_QQ_and_GF_initial_face_gcds_are_monomials_not_zero_roots(self):
        for row in self.newton["pole_faces"]:
            expected = 1 if row["primitive_outward_ray"] == [-3, 1] else audit.w**5
            for field in ("QQ", "GF101"):
                options = {"domain": sp.QQ} if field == "QQ" else {"modulus": 101}
                polynomials = [sp.Poly(audit.parse(value), audit.w, **options) for value in row[field]["polynomials"]]
                common = polynomials[0]
                for polynomial in polynomials[1:]:
                    common = sp.gcd(common, polynomial)
                self.assertEqual(common.monic().as_expr(), expected)
                self.assertEqual(len(common.terms()), 1)
                self.assertTrue(row[field]["torus_parameter_required_nonzero"])
                self.assertTrue(row[field]["all_nonzero_common_roots_excluded"])

    def test_initial_faces_independently_match_maximal_weights(self):
        for face in self.newton["pole_faces"]:
            ray = face["primitive_outward_ray"]
            for row, expression in zip(self.newton["rows"], face["QQ"]["polynomials"]):
                poly = sp.Poly(audit.parse(row["universal_polynomial_z_w"]).subs(audit.SPECIAL_VALUES), audit.z, audit.w)
                degree = max(sum(a*b for a, b in zip(exponent, ray)) for exponent, coefficient in poly.terms())
                expected = sum(coefficient*audit.w**exponent[1] for exponent, coefficient in poly.terms()
                               if sum(a*b for a, b in zip(exponent, ray)) == degree)
                self.assertEqual(sp.expand(audit.parse(expression)-expected), 0)

    def test_weighted_torus_normalization_covers_nonunit_initial_z(self):
        A, B, lam = sp.symbols("A B lam", nonzero=True)
        # For ray(-3,1), lambda^3=A makes lambda^-3*A=1. The
        # normalized w is lambda*B, never zero; requiring z-leading1
        # does not restrict the original torus point.
        self.assertEqual((A/lam**3).subs(A, lam**3), 1)
        self.assertIn("lambda^3=A", self.newton["torus_normalization"])
        self.assertIn("nonzero cube root", self.newton["torus_normalization"])

    def test_both_zero_coordinate_axes_have_unit_bounds(self):
        first = sp.Poly(audit.parse(self.newton["rows"][0]["universal_polynomial_z_w"]), audit.z, audit.w)
        self.assertFalse(first.as_expr().subs(audit.z, 0).has(audit.w))
        universal_axis = sp.Poly(first.as_expr().subs(audit.w, 0), audit.z)
        self.assertEqual(universal_axis.degree(), 6)
        self.assertEqual(sp.expand(first.as_expr().subs(audit.z, 0)-audit.parse(
            self.newton["zero_coordinate_cases"]["universal_first_equation_at_z_zero"])), 0)
        self.assertEqual(sp.expand(universal_axis.LC()-audit.parse(
            self.newton["zero_coordinate_cases"]["universal_first_equation_at_w_zero_leading_coefficient"])), 0)
        special = first.as_expr().subs(audit.SPECIAL_VALUES)
        zzero = sp.Poly(special.subs(audit.z, 0), audit.w, domain=sp.QQ)
        wzero = sp.Poly(special.subs(audit.w, 0), audit.z, domain=sp.QQ)
        self.assertEqual(zzero.degree(), 0)
        self.assertNotEqual(zzero.LC(), 0)
        self.assertEqual(wzero.degree(), 6)
        for value in (zzero.LC(), wzero.LC()):
            numerator, denominator = value.as_numer_denom()
            self.assertNotEqual(int(numerator) % 101, 0)
            self.assertNotEqual(int(denominator) % 101, 0)
        self.assertTrue(self.newton["zero_coordinate_cases"]["w_identically_zero_cannot_allow_z_pole"])

    def test_universal_saturation_identity_independently(self):
        a, b, c, u0, u1, u2, u3 = sp.symbols("a b c u0 u1 u2 u3")
        ell = u3*(b*b-a*c)-u2*a*b+u1*a*a
        mu = u3*b*c-u2*a*c+u0*a*a
        E = -u3*c*c+a*(u1*c-u0*b)
        self.assertEqual(sp.expand(c*ell-b*mu-a*E), 0)
        self.assertEqual(self.saturation["exact_universal_identity_residual"], "0")
        self.assertTrue(self.saturation["generic_nonzero_a_makes_E_necessary"])
        self.assertTrue(self.saturation["specialized_pivot_is_not_divided_out"])

    def test_original_saturation_coefficients_and_z_squared_normalization(self):
        a, b, c = [audit.parse(self.saturation["quadratic_coefficients"][key]) for key in ("a", "b", "c")]
        u0, u1, u2, u3 = [audit.parse(self.saturation["cubic_coefficients"][key]) for key in ("u0", "u1", "u2", "u3")]
        self.assertEqual(sp.expand(a+24*audit.z*(2*audit.H-audit.alpha)), 0)
        self.assertEqual(sp.expand(u3+16*audit.z*audit.z), 0)
        ell, mu = u3*(b*b-a*c)-u2*a*b+u1*a*a, u3*b*c-u2*a*c+u0*a*a
        rows = self.saved99["exceptional_chart_exact_equations"]["equations"]
        self.assertEqual(sp.expand(ell-audit.z**2*audit.parse(rows[0]["polynomial"])), 0)
        self.assertEqual(sp.expand(mu-audit.z**2*audit.parse(rows[1]["polynomial"])), 0)

    def test_E_is_polynomial_and_survives_vanishing_a(self):
        a, b, c = [audit.parse(self.saturation["quadratic_coefficients"][key]) for key in ("a", "b", "c")]
        u0, u1, u3 = [audit.parse(self.saturation["cubic_coefficients"][key]) for key in ("u0", "u1", "u3")]
        E = -u3*c*c+a*(u1*c-u0*b)
        self.assertTrue(E.is_polynomial(audit.z, audit.H, *audit.PARAMETERS))
        values = {**audit.SPECIAL_VALUES, audit.H: 1}
        self.assertEqual(sp.expand(a.subs(values)), 0)
        self.assertEqual(sp.expand((E+u3*c*c).subs(values)), 0)
        self.assertNotEqual(sp.expand(E.subs(values)), 0)
        self.assertNotEqual(self.saturation["specialized_E_cleared_denominator"] % 101, 0)

    def test_finite_six_equation_basis_recomputed_and_not_unit(self):
        polys = [audit.parse(value) for value in self.finite["six_input_integer_polynomials_mod101"]]
        basis = sp.groebner(polys, audit.z, audit.w, modulus=101, order="grevlex")
        self.assertEqual([str(p.as_expr()) for p in basis.polys], self.finite["six_equation_Groebner_basis"])
        self.assertEqual(len(basis.polys), 2)
        self.assertNotEqual([p.as_expr() for p in basis.polys], [1])
        H_residue = (audit.w-(audit.w-1)+3)/4
        self.assertEqual(H_residue, 1)
        self.assertEqual(H_residue, audit.SPECIAL_VALUES[audit.alpha]/2)

    def test_E_modular_remainder_recomputed_from_saved_integer_polynomial(self):
        E = sp.Poly(audit.parse(self.saturation["specialized_E_integer_z_w"]), audit.z, audit.w, modulus=101)
        self.assertEqual(E.as_expr(), audit.parse(self.saturation["specialized_E_mod101"]))
        basis = sp.groebner([audit.parse(value) for value in self.finite["six_equation_Groebner_basis"]],
                           audit.z, audit.w, modulus=101, order="grevlex")
        remainder = basis.reduce(E.as_expr())[1]
        self.assertEqual(remainder, -41*audit.w**3+7*audit.w**2-45*audit.w+40)
        self.assertEqual(str(remainder), self.finite["extra_E_remainder_mod_six_equation_basis"])

    def test_univariate_Bezout_certificate_independently(self):
        data = self.finite["univariate_Bezout"]
        values = {key: sp.Poly(audit.parse(value), audit.w, modulus=101)
                  for key, value in data.items() if key != "exact_residue"}
        identity = values["multiplier_quartic"]*values["quartic"]+values["multiplier_remainder"]*values["remainder"]
        self.assertEqual(identity.as_expr(), 1)
        self.assertEqual(sp.gcd(values["quartic"], values["remainder"]).as_expr(), 1)

    def test_augmented_seven_equation_unit_ideal_independently(self):
        polynomials = [audit.parse(value) for value in self.finite["six_input_integer_polynomials_mod101"]]
        polynomials.append(audit.parse(self.saturation["specialized_E_mod101"]))
        basis = sp.groebner(polynomials, audit.z, audit.w, modulus=101, order="grevlex")
        self.assertEqual([p.as_expr() for p in basis.polys], [1])
        self.assertTrue(self.finite["all_augmented_points_over_algebraic_closure_F101_excluded"])
        self.assertFalse(self.finite["unit_ideal_alone_claimed_to_imply_generic_exclusion"])

    def test_two_valuations_and_finite_constant_descent_are_explicit(self):
        data = self.report["exceptional_chart_valuative_exclusion"]
        proof = " ".join(data["proof_steps"])
        for phrase in ("finite extension L/Q(X)", "X-1 discrete valuation", "finite extension of Q", "place of that number field above101"):
            self.assertIn(phrase, proof)
        self.assertTrue(data["X_minus_one_and_101_poles_both_controlled"])
        self.assertFalse(data["projective_boundary_or_vanishing_pivot_silently_removed"])
        self.assertFalse(self.newton["global_family_properness_or_smoothness_asserted"])

    def test_modular_unit_ideal_without_boundary_control_is_not_enough(self):
        # Exact counterexamples show why both actual unit-vertex hypotheses
        # matter. These toy equations are not part of the frozen theory.
        X, z = audit.X, audit.z
        self.assertEqual(sp.cancel(((X-1)*z-1).subs(z, 1/(X-1))), 0)
        self.assertEqual(((X-1)*z-1).subs(X, 1), -1)
        self.assertEqual((101*z-1).subs(z, sp.Rational(1, 101)), 0)
        self.assertEqual(sp.Poly(101*z-1, z, modulus=101).as_expr(), -1)

    def test_exclusion_only_exceptional_chart_and_not_other_sections(self):
        data = self.report["exceptional_chart_valuative_exclusion"]
        self.assertTrue(data["all_zero_linear_pivot_chart_excluded_over_algebraic_closure_C_X"])
        self.assertFalse(data["rational_square_condition_needed_for_this_exclusion"])
        self.assertFalse(data["nonzero_K_discriminant_needed_for_this_exclusion"])
        frontier = self.report["remaining_section_frontier"]
        self.assertFalse(frontier["all_zero_linear_pivot_chart_open"])
        self.assertEqual(frontier["nonzero_linear_pivot_charts_still_open"], [1, 2, 3])
        self.assertFalse(frontier["all_cubic_polynomial_x_sections_excluded"])
        self.assertFalse(frontier["all_rational_sections_excluded"])
        self.assertEqual([frontier["original_free_rank_lower_bound"], frontier["original_free_rank_upper_bound"]], [0, 11])
        self.assertEqual(frontier["original_MW_torsion_order"], 1)
        self.assertEqual(self.report["preserved_frontier"]["closed_gates"], [])

    def test_conditional_historical_formulas_remain_valid_but_have_empty_antecedent(self):
        data = self.report["exceptional_chart_valuative_exclusion"]
        self.assertTrue(data["old_conditional_exceptional_pair_trace_difference_has_no_instance_on_this_member"])
        self.assertFalse(data["V100_conditional_group_law_and_lattice_identities_retracted"])
        self.assertTrue(data["z_times_discriminant_square_route_is_not_confused_with_z_square"])
        self.assertEqual(self.saved["conditional_rank_two_lattice"]["Gram_P1_P2"], [[3, -1], [-1, 3]])

    def test_rehashed_broad_no_section_overclaim_is_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["remaining_section_frontier"]["all_rational_sections_excluded"] = True
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(self.rehash(changed))

    def test_rehashed_lost_boundary_or_unit_witness_is_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["transformed_newton_boundary_certificate"]["pole_faces"].clear()
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(self.rehash(changed))
        changed = copy.deepcopy(self.report)
        changed["specialized_finite_field_certificate"]["augmented_seven_equation_Groebner_basis"] = ["z"]
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(self.rehash(changed))

    def test_returned_report_mutation_does_not_poison_derived_cache(self):
        changed = audit.build_certificate()
        changed["transformed_newton_boundary_certificate"]["rows"].clear()
        changed["universal_saturation_identity"]["exact_universal_identity_residual"] = "1"
        fresh = audit.build_certificate()
        self.assertEqual(len(fresh["transformed_newton_boundary_certificate"]["rows"]), 6)
        self.assertEqual(fresh["universal_saturation_identity"]["exact_universal_identity_residual"], "0")


if __name__ == "__main__":
    unittest.main()
