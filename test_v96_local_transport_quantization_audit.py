import copy
from itertools import product
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import sympy as sp

import v96_local_transport_quantization_audit as audit


class TestV96LocalTransportQuantization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()

    def test_pinned_canonical_parents_and_roundtrip(self):
        self.assertEqual(self.report["input_core_hashes"], {k: v[1] for k, v in audit.PARENTS.items()})
        self.assertEqual(self.report["embedded_v95_local_profile_core"], audit.LOCAL_CORE)
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        self.assertEqual(json.loads(json.dumps(self.report)), self.report)
        audit.validate_certificate(self.report)

    def test_rehashed_parent_tampering_rejected(self):
        original = Path.read_text
        def changed(path, *args, **kwargs):
            text = original(path, *args, **kwargs)
            if path.name == audit.PARENTS["v95_master"][0]:
                value = json.loads(text)
                value["next_required_action"]["id"] = "CLOSE_G1"
                value["core_sha256"] = audit.canonical_sha(value)
                return json.dumps(value)
            return text
        with patch.object(Path, "read_text", changed):
            with self.assertRaises(RuntimeError):
                audit.load_parents()

    def test_charge_two_is_integral_determinant_line_index(self):
        row = self.report["ordinary_eta_CS_quantization"]
        f, c, p = audit.f, audit.c, audit.p
        self.assertEqual(sp.expand(sp.sympify(row["J2"])-4*f**3/3+f*p/12), 0)
        self.assertEqual(sp.expand(sp.sympify(row["J2_in_integral_determinant_class"])-c**3/6+c*p/24), 0)
        self.assertEqual(sp.expand(sp.sympify(row["J2"]).subs(f, c/2)-sp.sympify(row["J2_in_integral_determinant_class"])), 0)
        self.assertTrue(row["charge_two_singlet_is_a_genuine_gauge_representation"])
        self.assertFalse(row["charge_one_gauge_singlet_is_a_genuine_representation"])

    def test_CP3_primitive_period_and_independent_filling_ambiguities(self):
        self.assertEqual(audit.cp3_period(audit.weyl_index(2)), 1)
        for q in range(-20, 21):
            self.assertEqual(audit.cp3_period(audit.weyl_index(q)), sp.Rational(q**3-q, 6))
        row = self.report["ordinary_eta_CS_quantization"]
        self.assertEqual([r["ambiguity_phase"] for r in row["requested_levels"]], ["+i", "+i", "-1"])
        self.assertTrue(all(not r["ordinary_independent_edge_quantized"] for r in row["requested_levels"]))
        self.assertEqual(row["sum_of_three_ambiguities"], "0")
        self.assertFalse(row["zero_sum_makes_independent_fillings_unambiguous"])

    def test_fractional_level_rejection_is_scoped(self):
        row = self.report["ordinary_eta_CS_quantization"]
        self.assertTrue(row["ordinary_integer_level_refinement_exists"])
        self.assertTrue(row["nonbounding_definition_uses_eta_not_an_assumption_of_bounding"])
        self.assertFalse(row["all_equivariant_or_relative_fractional_inflow_excluded"])
        self.assertFalse(row["same_test_is_the_F95_defect_lens_phase"])
        self.assertFalse(row["full_Gammahat_spin_refinement_constructed"])

    def test_cover_source_is_integral_but_weighted_quotient_is_fractional(self):
        row = self.report["free_edge_transport_obstruction"]
        push = sp.Matrix(row["quotient_push_matrix"])
        self.assertEqual(push*sp.Matrix(row["cover_integer_source_divisor"]), sp.Matrix([sp.Rational(1, 4), sp.Rational(1, 4), -sp.Rational(1, 2)]))
        self.assertEqual(row["effective_stabilizer_orders_on_cover"], [4, 4, 2, 2])
        self.assertEqual(row["cover_integer_source_divisor"], [1, 1, -1, -1])

    def test_free_edge_cover_multiplicities_and_incidence(self):
        row = self.report["free_edge_transport_obstruction"]
        cover = sp.Matrix(row["free_edge_orbit_boundary_on_cover"])
        quotient = sp.Matrix(row["ordinary_quotient_edge_incidence"])
        push = sp.Matrix(row["quotient_push_matrix"])
        self.assertEqual(cover, sp.Matrix([[4, 0], [0, 4], [-2, -2], [-2, -2]]))
        self.assertEqual(push*cover, quotient)
        for a, b in product(range(-5, 6), repeat=2):
            value = quotient*sp.Matrix([a, b])
            self.assertEqual(sum(value), 0)
            self.assertTrue(all(v.is_Integer for v in value))

    def test_minimum_multiple_in_integer_edge_lattice(self):
        B = sp.Matrix([[1, 0], [0, 1], [-1, -1]])
        target = sp.Matrix([sp.Rational(1, 4), sp.Rational(1, 4), -sp.Rational(1, 2)])
        for n in range(1, 25):
            solution = B.gauss_jordan_solve(n*target)[0]
            self.assertEqual(all(v.is_Integer for v in solution), n % 4 == 0)
        self.assertEqual(B*sp.Matrix([1, 1]), 4*target)
        self.assertFalse(self.report["free_edge_transport_obstruction"]["equivariant_fractional_transport_in_general_excluded"])

    def test_quarter_turn_curve_automorphism_has_order_four(self):
        X, Y = audit.X, audit.Y
        A = {X: -X, Y: sp.I*Y}
        F = Y**2-X**3+X
        self.assertEqual(sp.expand(F.subs(A, simultaneous=True)), -F)
        first = (X, Y)
        for _ in range(4):
            first = tuple(sp.expand(v.subs(A, simultaneous=True)) for v in first)
        self.assertEqual(first, (X, Y))
        self.assertNotEqual((X, -Y), (X, Y))

    def test_divisor_valuations_and_no_other_zero_or_pole(self):
        rows = self.report["equivariant_torus_phase"]["divisor_rows"]
        self.assertEqual([r["ord_g"] for r in rows], [1, 1, -1, -1])
        self.assertEqual([r["ord_X"]-r["ord_Y"] for r in rows], [1, 1, -1, -1])
        self.assertEqual(sum(r["ord_g"] for r in rows), 0)
        # Y vanishes exactly at the three simple roots of X^3-X;
        # only X=Y=0 needs the order2/order1 cancellation recorded above.
        self.assertEqual(sp.factor(audit.X**3-audit.X), audit.X*(audit.X-1)*(audit.X+1))
        self.assertNotEqual(sp.diff(audit.X**3-audit.X, audit.X).subs(audit.X, 0), 0)

    def test_g_character_and_minimum_invariant_power(self):
        X, Y = audit.X, audit.Y
        g = X/Y
        Ag = g.subs({X: -X, Y: sp.I*Y}, simultaneous=True)
        self.assertEqual(sp.cancel(Ag-sp.I*g), 0)
        for n in range(1, 9):
            self.assertEqual(sp.cancel(Ag**n-g**n) == 0, n % 4 == 0)
        self.assertFalse(self.report["equivariant_torus_phase"]["g_is_an_ordinary_function_on_the_quotient"])

    def test_quotient_fourth_power_and_residues(self):
        X, t = audit.X, audit.t
        reduced = sp.cancel(X**4/(X**3-X)**2)
        h = t/(t-1)**2
        self.assertEqual(sp.cancel(reduced-h.subs(t, X**2)), 0)
        logarithmic_derivative = sp.diff(h, t)/h/4
        self.assertEqual(sp.residue(logarithmic_derivative, t, 0), sp.Rational(1, 4))
        self.assertEqual(sp.residue(logarithmic_derivative, t, 1), -sp.Rational(1, 2))
        u = sp.Symbol("u")
        at_infinity = -logarithmic_derivative.subs(t, 1/u)/u**2
        self.assertEqual(sp.residue(at_infinity, u, 0), sp.Rational(1, 4))

    def test_exact_V71_phase_series(self):
        self.assertEqual(audit.phase_series(4, 1), [sp.Rational(1, 8), -sp.Rational(1, 8), -sp.Rational(5, 64), sp.Rational(11, 192)])
        self.assertEqual(audit.phase_series(4, 2), [-sp.Rational(1, 8), -sp.Rational(1, 8), sp.Rational(5, 64), sp.Rational(11, 192)])
        self.assertEqual(audit.phase_series(2, 1), [-sp.Rational(1, 8), 0, sp.Rational(1, 64), 0])
        self.assertEqual(audit.phase_series(2, 0), [sp.Rational(1, 8), 0, -sp.Rational(1, 64), 0])

    def test_full_matrices_SMW_reality_and_charge_normalization(self):
        blocks = self.report["virtual_shifted_determinant_profile"]["matrix_blocks"]
        for row in blocks:
            H, Q = sp.Matrix(row["H_C4"]), sp.Matrix(row["Q"])
            self.assertEqual(audit.clean(H**4), -sp.eye(2))
            self.assertEqual(audit.clean(H.T*audit.J*H), audit.J)
            self.assertEqual(audit.clean(audit.J*sp.conjugate(H)-H*audit.J), sp.zeros(2))
            self.assertEqual(Q, sp.diag(2, -2))
            self.assertEqual(sp.expand(audit.full_SMW_polynomial(H, Q, 4)-sp.sympify(row["C4_I6"])), 0)
            self.assertTrue(all(row["checks"].values()))

    def test_zero_mode_projectors_not_counts(self):
        for row in self.report["virtual_shifted_determinant_profile"]["matrix_blocks"]:
            phases = [sp.sympify(row["plus_phase"]), sp.sympify(row["minus_phase"])]
            for z in phases:
                self.assertEqual(sp.simplify(sum(z**j for j in range(4))/4), 0)
            self.assertEqual(row["constant_N1_projector_ranks"], [0, 0])
        self.assertFalse(self.report["virtual_shifted_determinant_profile"]["bulk_gap_survives_a_nonconstant_mass_profile_without_defect_modes"])

    def test_full_C4_normal_difference_not_only_pure_gauge(self):
        f, p, x = audit.f, audit.p, audit.x
        delta = sp.expand(audit.phase_polynomial(4, 1)-audit.phase_polynomial(4, 2))
        self.assertEqual(sp.expand(delta-audit.weyl_index(2)/4+5*f*x**2/16), 0)
        self.assertEqual(delta.coeff(x, 1), 0)
        self.assertEqual(delta.coeff(x, 3), 0)
        self.assertNotEqual(delta.subs(p, 0).coeff(x, 2), 0)

    def test_C2_cover_and_physical_orbit_difference(self):
        f, x = audit.f, audit.x
        delta = sp.expand(audit.phase_polynomial(2, 1)-audit.phase_polynomial(2, 0))
        self.assertEqual(sp.expand(delta+audit.weyl_index(2)/4-f*x**2/16), 0)
        row = self.report["virtual_shifted_determinant_profile"]
        self.assertEqual(sp.expand(2*delta-sp.sympify(row["per_physical_stratum_delta_I6"]["physical_C2_orbit"])), 0)

    def test_virtual_normal_residual_is_not_discarded(self):
        row = self.report["virtual_shifted_determinant_profile"]
        total = sp.expand(sum(sp.sympify(v) for v in row["per_physical_stratum_delta_I6"].values()))
        self.assertEqual(total, -audit.f*audit.x**2/2)
        self.assertEqual(row["integrated_pure_U1_delta_I6"], "0")
        self.assertEqual(total, sp.sympify(row["integrated_delta_I6"]))
        self.assertFalse(row["new_normal_anomaly_canceled"])
        self.assertFalse(row["full_R_and_flavor_curvature_polynomial_constructed"])

    def test_smooth_intertwiner_and_quaternionic_reality(self):
        row = self.report["smooth_equivariant_mass_intertwiner"]
        self.assertTrue(all(row["checks"].values()))
        M = sp.Matrix(row["mass_matrix"])
        m, mbar = sp.symbols("m mbar")
        self.assertEqual(M.det(), m*mbar)
        self.assertEqual(audit.J*M.subs({m: mbar, mbar: m}, simultaneous=True), M*audit.J)
        self.assertEqual(row["only_constant_charge_preserving_mass"], [["0", "0"], ["0", "0"]])

    def test_regularized_mass_is_smooth_at_poles_and_transforms(self):
        z, zb = sp.symbols("z zb")
        g = z
        gbar = zb
        self.assertEqual(sp.cancel((sp.I*g)/(1+(sp.I*g)*(-sp.I*gbar))-sp.I*g/(1+g*gbar)), 0)
        pole_regularized = (1/z)/(1+1/(z*zb))
        self.assertEqual(sp.cancel(pole_regularized-zb/(1+z*zb)), 0)
        row = self.report["smooth_equivariant_mass_intertwiner"]
        self.assertEqual(row["cover_mass_zero_windings"], {"z00": 1, "z11": 1, "z10": -1, "z01": -1})
        self.assertFalse(row["nowhere_nonzero_profile"])
        self.assertFalse(row["holomorphic_superpotential_mass_profile"])

    def test_fixed_point_equivariance_forces_zero(self):
        m = sp.Symbol("m")
        self.assertEqual(sp.solve(m-sp.I*m, m), [0])
        self.assertEqual(sp.solve(m-(-m), m), [0])
        row = self.report["smooth_equivariant_mass_intertwiner"]
        self.assertFalse(row["projected_defect_zero_modes_and_their_Gammahat_representations_computed"])
        self.assertFalse(row["cover_winding_divided_by_four_is_automatically_a_physical_Weyl_count"])

    def test_equivariant_identity_sector_fraction_is_not_full_index(self):
        rows = self.report["equivariant_scope_and_missing_data"]["elementary_equivariant_index_example"]
        self.assertEqual([row["invariant_index"] for row in rows], [1, 0, 0, 0])
        for row in rows:
            self.assertEqual(sp.simplify(sum(sp.sympify(v) for v in row["character"])/4), row["invariant_index"])
            self.assertEqual(sp.Rational(row["identity_sector_contribution"])+sp.sympify(row["nonidentity_contribution"]), row["invariant_index"])
        self.assertFalse(self.report["equivariant_scope_and_missing_data"]["ordinary_CP3_obstruction_is_full_equivariant_no_go"])

    def test_no_action_or_gate_promotion(self):
        row = self.report["terminal_decision"]
        self.assertEqual(row["closed_gates"], [])
        self.assertEqual(row["accepted_extensions"], 0)
        self.assertTrue(row["ordinary_integer_eta_CS_family_quantized_on_product_spin_backgrounds"])
        self.assertTrue(row["explicit_order4_torus_phase_and_smooth_mass_intertwiner_found"])
        for key in ("requested_fractional_free_edge_transport_quantized_as_standalone_ordinary_CS", "introduced_normal_anomaly_canceled", "equivariant_quantized_relative_transport_action_constructed", "all_equivariant_or_topological_repairs_excluded", "same_action_parent_accepted"):
            self.assertFalse(row[key])

    def test_rehashed_mixed_term_removal_is_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["virtual_shifted_determinant_profile"]["integrated_delta_I6"] = "0"
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(changed)

    def test_rehashed_quantum_action_promotion_is_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["terminal_decision"]["equivariant_quantized_relative_transport_action_constructed"] = True
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(changed)

    def test_kernel_input_validation(self):
        for order, power in ((3, 1), (4, 0), (4, 4), (2, 2)):
            with self.assertRaises(ValueError):
                audit.normal_kernel_series(order, power)
        with self.assertRaises(ValueError):
            audit.phase_series(4, 4)


if __name__ == "__main__":
    unittest.main()
