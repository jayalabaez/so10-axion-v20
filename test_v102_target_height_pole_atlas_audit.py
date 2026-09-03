"""Independent height arithmetic, global coordinate and duplication checks."""
import copy
import unittest
from unittest.mock import patch

import sympy as sp
import v102_target_height_pole_atlas_audit as audit


class TargetHeightPoleAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()
        cls.targets = {r["height"]: r for r in cls.report["target_sections"]}

    def test_canonical(self):
        self.assertEqual(self.report["core_sha256"], audit.common.canonical_sha(self.report))

    def test_reconstruction(self):
        audit.validate_certificate(self.report)

    def test_D6_inverse_corrections(self):
        C = sp.Matrix(self.report["D6_height_and_divisibility"]["Cartan"])
        self.assertEqual(C.det(), 4)
        self.assertEqual([C.inv()[i, i] for i in (0, 4, 5)], [1, sp.Rational(3, 2), sp.Rational(3, 2)])
        self.assertTrue(all(q.is_Integer for q in 2*C.inv()))

    def test_component_group_exponent_two(self):
        row = self.report["D6_height_and_divisibility"]
        self.assertEqual(row["Smith_invariants"], [1, 1, 1, 1, 2, 2])
        self.assertTrue(row["every_double_meets_identity_component"])

    def test_height_options_independent_enumeration(self):
        for h in (sp.Rational(5, 2), 3, 4, 37, 148):
            expected = [(name, n) for name, c in audit.COMPONENTS for n in range(100) if 4+2*n-c == h]
            self.assertEqual([(r["component"], r["P_dot_O"]) for r in audit.height_options(h)], expected)

    def test_target37_forces_near_and17(self):
        row = self.targets[37]
        self.assertEqual((row["component"], row["correction"], row["P_dot_O"]), ("near_vector", "1", 17))

    def test_target148_forces_identity_and72(self):
        row = self.targets[148]
        self.assertEqual((row["component"], row["correction"], row["P_dot_O"]), ("identity", "0", 72))

    def test_target_global_coordinate_degrees(self):
        self.assertEqual(self.targets[37]["global_degrees_Z_U_V"], [17, 38, 57])
        self.assertEqual(self.targets[148]["global_degrees_Z_U_V"], [72, 148, 222])

    def test_every_equation_term_has_same_line_degree(self):
        for n in (0, 1, 17, 72):
            du, dv, dz = 4+2*n, 6+3*n, n
            self.assertEqual([2*dv, 3*du, 8+du+4*dz, 12+6*dz], [12+6*n]*4)

    def test_target_affine_near_sharpening(self):
        row = self.targets[37]
        n = row["monic_affine_denominator_degree"]
        self.assertEqual(n, 17)
        self.assertEqual(row["affine_U_degree_exact"]-2*n, 3)
        self.assertEqual(row["affine_V_degree_upper_bound"]-3*n, 4)
        self.assertEqual(row["affine_U_leading_with_monic_Z"], -24)
        self.assertTrue(row["all_O_intersections_forced_finite_in_T"])

    def test_identity_allows_poles_at_infinity(self):
        row = self.targets[148]
        self.assertFalse(row["all_O_intersections_forced_finite_in_T"])
        for infinity_multiplicity in range(73):
            affine_z = 72-infinity_multiplicity
            self.assertEqual(row["affine_U_degree_exact"]-2*affine_z, 4+2*infinity_multiplicity)
            self.assertEqual(row["affine_V_degree_exact"]-3*affine_z, 6+3*infinity_multiplicity)
        self.assertFalse(self.report["global_section_atlas"]["affine_denominator_degree_always_equals_global_n"])

    def test_original_curve_homogenization(self):
        row = self.report["unchanged_curve"]
        for key, homogeneous, degree in (("A", "A8_homogeneous", 8), ("B", "B12_homogeneous", 12)):
            p = audit.previous.parse(row[homogeneous])
            self.assertEqual({sum(m) for m in sp.Poly(p, audit.s, audit.t).monoms()}, {degree})
            self.assertEqual(sp.expand(p.subs({audit.s: audit.T, audit.t: 1})-audit.previous.parse(row[key])), 0)

    def test_homogenization_rejects_low_degree(self):
        with self.assertRaises(ValueError):
            audit.homogenize(audit.T**9, 8)

    def test_weighted_rescaling_preserves_equation(self):
        U, V, Z, A, B, lam = sp.symbols("U V Z A B lam")
        F = V*V-U**3-A*U*Z**4-B*Z**6
        self.assertEqual(sp.expand(F.subs({U: lam**2*U, V: lam**3*V, Z: lam*Z})-lam**6*F), 0)

    def test_binary_counts_not_existence(self):
        for row in self.targets.values():
            n, u, v = row["global_degrees_Z_U_V"]
            self.assertEqual(n+u+v+3, row["unconstrained_binary_coefficient_count"])
            self.assertEqual(row["homogeneous_equation_degree"]+1, row["homogeneous_equation_coefficient_count"])
            self.assertFalse(row["coefficient_count_is_a_no_solution_proof"])

    def test_formal_identity_pole_orders(self):
        # Exact leading valuation balance for the identity parameter tau=-x/y.
        for m in range(1, 10):
            self.assertEqual((-2*m)-(-3*m), m)
            self.assertEqual(3*(-2*m), 2*(-3*m))
        self.assertTrue(self.report["global_section_atlas"]["coprimality_is_essential"])

    def test_duplication_curve_remainder_independent(self):
        row = self.report["exact_duplication"]
        U, V, Z, A, B = sp.symbols("U V Z A B")
        Ud, Vd, Zd = [sp.sympify(row[k]) for k in ("raw_doubled_U", "raw_doubled_V", "raw_doubled_Z")]
        residual = V*V-U**3-A*U*Z**4-B*Z**6
        self.assertEqual(sp.rem(sp.expand(Vd**2-Ud**3-A*Ud*Zd**4-B*Zd**6), residual, V), 0)

    def test_duplication_tangent_numeric_example(self):
        # Independent smooth curve y²=x³−x+1 at(0,1); 2P=(1/4,−7/8).
        row = self.report["exact_duplication"]
        values = dict(zip(sp.symbols("U V Z A B"), (0, 1, 1, -1, 1)))
        U, V, Z = [sp.sympify(row[k]).subs(values) for k in ("raw_doubled_U", "raw_doubled_V", "raw_doubled_Z")]
        self.assertEqual(U/Z**2, sp.Rational(1, 4))
        self.assertEqual(V/Z**3, -sp.Rational(7, 8))

    def test_near_duplication_leading_orders(self):
        u, a2, b3, x2, y2 = sp.symbols("u a2 b3 x2 y2")
        values = dict(zip(sp.symbols("U V Z A B"), (-24*u+x2*u*u, y2*u*u, 1, -432*u*u+a2*u**3, 3456*u**3+b3*u**4)))
        row = self.report["exact_duplication"]
        U = sp.Poly(sp.expand(sp.sympify(row["raw_doubled_U"]).subs(values)), u)
        V = sp.Poly(sp.expand(sp.sympify(row["raw_doubled_V"]).subs(values)), u)
        self.assertEqual(min(m[0] for m in U.monoms()), 4)
        self.assertEqual(min(m[0] for m in V.monoms()), 6)
        self.assertEqual(U.nth(4), 1296**2)
        self.assertEqual(V.nth(6), -1296**3)

    def test_doubling_intersections_match_height(self):
        for _, c in audit.COMPONENTS:
            for n in range(30):
                nd = int(4*n+6-2*c)
                self.assertEqual(audit.height(nd, 0), 4*audit.height(n, c))
        self.assertEqual(4*17+4, 72)

    def test_half_integrality_blocks_target37_division(self):
        self.assertEqual(sp.factorint(74), {2: 1, 37: 1})
        self.assertEqual(audit.possible_integer_divisors(37), [])
        self.assertTrue(self.targets[37]["primitive_modulo_torsion_if_exists"])

    def test_target148_only_possible_division_two(self):
        self.assertEqual(sp.factorint(296), {2: 3, 37: 1})
        self.assertEqual(audit.possible_integer_divisors(148), [2])
        self.assertFalse(self.targets[148]["divisible_by_two_proved"])

    def test_low_integral_heights_cannot_be_rank_one_targets(self):
        self.assertEqual({audit.height(0, c) for _, c in audit.COMPONENTS}, {4, 3, sp.Rational(5, 2)})
        for h in (37, 148):
            for n in [1]+audit.possible_integer_divisors(h):
                self.assertGreaterEqual(sp.Rational(h, n*n), 37)
        self.assertFalse(self.report["rank_one_target_boundary"]["original_rank_lower_bound_raised"])

    def test_invalid_height_inputs(self):
        for n in (-1, 1.0, True):
            with self.assertRaises(ValueError):
                audit.height(n, 0)
        with self.assertRaises(ValueError):
            audit.height(0, sp.Rational(1, 2))
        for value in (0, -1, sp.Rational(1, 3)):
            with self.assertRaises(ValueError):
                audit.possible_integer_divisors(value)

    def test_no_actual_section_or_gate_promotion(self):
        decision = self.report["terminal_decision"]
        self.assertFalse(decision["original_target_section_constructed"])
        self.assertFalse(decision["original_MW_rank_computed"])
        self.assertEqual(decision["closed_gates"], [])
        self.assertFalse(self.report["global_section_atlas"]["target_binary_form_system_solved"])

    def test_resealed_scope_tamper_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["terminal_decision"]["original_target_section_constructed"] = True
        changed["core_sha256"] = audit.common.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(changed)

    def test_fresh_source_hash_rechecked(self):
        with patch.object(audit.common, "file_sha", return_value="0"*64):
            with self.assertRaises(RuntimeError):
                audit.build_certificate()


if __name__ == "__main__":
    unittest.main()
