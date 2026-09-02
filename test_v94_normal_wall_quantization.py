import copy
from itertools import combinations, product
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import sympy as sp

import v94_normal_wall_quantization as audit


class TestV94NormalWallQuantization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()

    def test_canonical_pinned_parent_chain(self):
        self.assertEqual(self.report["input_core_hashes"], {k: v[1] for k, v in audit.PARENTS.items()})
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))

    def test_rehashed_changed_parent_rejected(self):
        original = Path.read_text
        def changed(path, *args, **kwargs):
            text = original(path, *args, **kwargs)
            if path.name == audit.PARENTS["v93_master"][0]:
                value = json.loads(text)
                value["strict_master_decision"]["theory_complete"] = True
                value["core_sha256"] = audit.canonical_sha(value)
                return json.dumps(value)
            return text
        with patch.object(Path, "read_text", changed):
            with self.assertRaises(RuntimeError):
                audit.load_parents()

    def test_frozen_and_reallocated_polynomial_identity(self):
        row = self.report["normal_target_reallocation"]
        I, A, B, A0, B0 = (sp.sympify(row[k]) for k in ("C4_bare_I6", "A4_frozen", "B4_frozen", "A4_reallocated", "B4_reallocated"))
        f, x = audit.f, audit.x
        self.assertEqual(sp.expand(I-x*A-f*B), 0)
        self.assertEqual(sp.expand(I-x*A0-f*B0), 0)
        self.assertEqual(sp.expand(A-A0-f*sp.sympify(row["mixed_form_moved_into_gauge_descent"])), 0)
        self.assertTrue(all(row["identity_checks"].values()))
        self.assertFalse(row["reallocation_is_accepted_counterterm"])

    def test_Spin2_normal_form_with_exact_Chern_normalization(self):
        row = self.report["normal_target_reallocation"]
        cc2 = sum(a*b for a, b in combinations(audit.E, 2))
        Q = sp.sympify(row["Spin2_normal_four_form"])
        self.assertEqual(sp.expand(Q-cc2+audit.p/4+audit.u**2), 0)
        I, B0 = sp.sympify(row["C4_bare_I6"]), sp.sympify(row["B4_reallocated"])
        self.assertEqual(sp.expand(I.subs(audit.x, 2*audit.u)-audit.u*Q-audit.f*B0.subs(audit.x, 2*audit.u)), 0)

    def test_no_effective_C4_or_C2_square_root_character(self):
        for point, row in self.report["normal_root_isotropy"]["strata"].items():
            n = row["effective_order"]
            self.assertEqual(n, 4 if point in ("z00", "z11") else 2)
            self.assertEqual([r for r in range(n) if 2*r % n == 1], [])
            self.assertEqual(row["square_root_characters_on_effective_group"], [])
            self.assertEqual(row["minimal_cyclic_pullback_order"], 2*n)
            self.assertEqual(row["projection_kernel"], [0, n])

    def test_cyclic_pullback_maps_and_kernel_signs(self):
        for row in self.report["normal_root_isotropy"]["strata"].values():
            n = row["effective_order"]
            root = (1+sp.I)/sp.sqrt(2) if n == 4 else sp.I
            normal = sp.I if n == 4 else sp.Integer(-1)
            self.assertEqual(sp.simplify(root**n), -1)
            self.assertEqual(sp.simplify(root**(2*n)), 1)
            for j in range(2*n):
                self.assertEqual(sp.simplify(root**(2*j)-normal**(j % n)), 0)
            self.assertTrue(all(row["checks"].values()))

    def test_existing_half_angles_not_falsely_declared_absent(self):
        row = self.report["normal_root_isotropy"]
        self.assertTrue(row["existing_Gammahat_already_contains_correlated_half_angle_factors"])
        self.assertIsNone(row["independent_normal_root_descends_through_existing_Gammahat_kernel"])
        self.assertFalse(row["existing_Gammahat_is_proved_to_exclude_the_needed_root"])

    def test_original_half_c2_forces_even_cover(self):
        for n in range(1, 12):
            self.assertEqual(sp.Rational(n, 2).is_Integer, n % 2 == 0)
        row = self.report["fixed_allocation_period_screens"]["proof_and_counterexamples"][0]
        self.assertEqual(row["S4_unit_SU5_instanton"], "1/2")

    def test_frozen_integral_flux_screen_requires_multiple_four(self):
        for n in range(1, 25):
            witness = audit.fixed_period(n, (1, 0), (0, 0), (0, 1))
            self.assertEqual(witness, -sp.Rational(87*n*n, 16))
            self.assertEqual(witness.is_Integer, n % 4 == 0)
        self.assertEqual(audit.fixed_period(2, (1, 0), (0, 0), (0, 1)), -sp.Rational(87, 4))

    def test_actual_gauge_quotient_half_flux_requires_multiple_eight(self):
        for n in range(1, 25):
            witness = audit.fixed_period(n, (sp.Rational(1, 2), 0), (1, 0), (0, 1))
            self.assertEqual(witness, -sp.Rational(87*n*n, 32))
            self.assertEqual(witness.is_Integer, n % 8 == 0)
        self.assertEqual(audit.fixed_period(4, (sp.Rational(1, 2), 0), (1, 0), (0, 1)), -sp.Rational(87, 2))

    def test_degree_four_sufficiency_integral_spin_classes(self):
        f, t, c2, p, u = audit.f, audit.t, audit.c2, audit.p, audit.u
        expected = 2*c2-4*f*t+78*f*f-87*f*u-p/2-8*u*u
        self.assertEqual(audit.fixed_normal_form(4), sp.expand(expected))
        lam = sp.Symbol("lambda_spin")
        self.assertTrue(all(v.is_Integer for v in sp.Poly(expected.subs(p, 2*lam), f, t, c2, lam, u).coeffs()))

    def test_degree_eight_sufficiency_for_quotient_integral_classes(self):
        c, t, c2, p, u = audit.c, audit.t, audit.c2, audit.p, audit.u
        expected = 4*c2-4*c*t+39*c*c-174*c*u-p-64*u*u
        self.assertEqual(audit.fixed_normal_form(8, True), sp.expand(expected))
        self.assertTrue(all(v.is_Integer for v in sp.Poly(expected, c, t, c2, p, u).coeffs()))

    def test_mixed_flux_period_tests_do_not_assume_a_nonzero_root_phase(self):
        row = self.report["fixed_allocation_period_screens"]["phase_field_domain"]
        self.assertIn("integral class", row["nowhere_nonzero_charge_one_root_field_requires"])
        self.assertFalse(row["mixed_flux_counterexamples_admit_everywhere_nonzero_charge_one_root_field"])
        self.assertFalse(row["four_and_eight_bounds_are_no_go_for_restricted_phase_field_domains"])
        self.assertTrue(row["S4_half_c2_witness_has_u_zero_and_survives_this_restriction"])
        self.assertFalse(row["root_zeros_defects_and_patchwise_completion_constructed"])

    def test_closed_spin4_period_formula_and_examples(self):
        row = self.report["reallocated_Spin2_period_screen"]
        self.assertEqual(row["minimum_cover_for_half_c2"], 2)
        self.assertTrue(row["closed_spin4_pass"])
        self.assertTrue(row["same_screen_with_Spin_c11_gauge_bundles_passes"])
        expected = [sp.Integer(1), sp.Integer(12), sp.Integer(-2), sp.Integer(0)]
        self.assertEqual([sp.Rational(z["period"]) for z in row["examples"]], expected)
        for c2, k, aa, bb in product(range(-2, 3), repeat=4):
            period = c2-sp.Rational(48*k, 4)-audit.pairing((aa, bb), (aa, bb))
            self.assertTrue(period.is_Integer)

    def test_spin_periods_not_universal_nonspin_quantization(self):
        row = self.report["reallocated_Spin2_period_screen"]
        self.assertFalse(row["p1_over4_claimed_integral_in_universal_ordinary_H4_BSpin"])
        self.assertTrue(row["spin_dependent_gravitational_refinement_needed"])
        self.assertEqual(row["nonspin_warning"]["formal_period"], "-3/4")
        self.assertFalse(row["nonspin_warning"]["admissible_in_the_stated_Spin4_product_category"])
        self.assertFalse(row["nonspin_warning"]["obstruction_to_full_Gammahat_claimed"])

    def test_SU5_exterior_indices_derived_from_weights(self):
        rows = self.report["wall_fermion_parity_obstruction"]["indices_on_exterior_power_generators"]
        self.assertEqual([r["dimension"] for r in rows], [5, 10, 10, 5])
        self.assertEqual([r["quadratic_index_ell"] for r in rows], [1, 3, 3, 1])
        self.assertEqual([r["cubic_index_A"] for r in rows], [1, 1, -1, -1])
        for r in rows:
            self.assertEqual(sum(z*z for z in r["weight_values_on_H"]), 20*r["quadratic_index_ell"])
            self.assertEqual(sum(z**3 for z in r["weight_values_on_H"]), -60*r["cubic_index_A"])

    def test_index_parity_preserved_by_tensor_product(self):
        rows = audit.su5_exterior_indices()
        for a, b in product(rows, repeat=2):
            weights = [v+w for v in a["weight_values_on_H"] for w in b["weight_values_on_H"]]
            ell = sp.Rational(sum(z*z for z in weights), 20)
            cubic = -sp.Rational(sum(z**3 for z in weights), 60)
            self.assertEqual(ell, a["dimension"]*b["quadratic_index_ell"]+b["dimension"]*a["quadratic_index_ell"])
            self.assertEqual(cubic, a["dimension"]*b["cubic_index_A"]+b["dimension"]*a["cubic_index_A"])
            self.assertEqual(int(ell-cubic) % 2, 0)

    def test_fermion_only_parity_obstruction_is_restricted(self):
        row = self.report["wall_fermion_parity_obstruction"]
        self.assertFalse(row["fermions_only_cancel_required_half_in_this_structure"])
        self.assertFalse(row["integer_normal_charges_alone_cancel_required_half"])
        self.assertFalse(row["no_go_for_every_Gammahat_or_extended_wall_completion"])
        self.assertFalse(row["single_fundamental_check"]["cubic_anomaly_free"])

    def test_conditional_wall_count_and_actual_polynomial(self):
        row = self.report["conditional_product_lift_wall_module"]
        total = 0
        for field in row["field_blocks"]:
            weights = [sp.sympify(v) for v in field["weights"]]
            q = sp.Rational(field["normal_charge_qN"])
            self.assertEqual(audit.weyl_polynomial(weights, q), sp.sympify(field["one_copy_I6"]))
            total += field["copies"]*audit.weyl_polynomial(weights, q)
        self.assertEqual(sp.expand(total-sp.sympify(row["full_wall_polynomial"])), 0)
        self.assertEqual((row["complex_Weyl_components"], row["irreducible_multiplets_counted_with_copies"]), (28, 20))
        self.assertEqual((row["Tr_normal_Q"], row["Tr_normal_Q3"]), ("-3", "3/4"))

    def test_conditional_wall_cancels_complete_f_zero_C4_restriction(self):
        row = self.report["conditional_product_lift_wall_module"]
        self.assertEqual(sp.expand(sp.sympify(row["full_wall_polynomial"])+sp.sympify(row["bare_C4_f_zero_polynomial"])), 0)
        self.assertTrue(row["normal_gauge_gravity_restriction_f_zero_cancelled"])
        self.assertFalse(row["all_f_dependent_anomalies_are_cancelled"])
        self.assertFalse(row["minimality_claimed"])

    def test_wall_module_does_not_descend_through_natural_spin_kernel(self):
        row = self.report["conditional_product_lift_wall_module"]
        failures = sum(v["copies"]*v["dimension"]*((1+v["Spin2_integral_weight"]) % 2) for v in row["field_blocks"])
        self.assertEqual(failures, 8)
        self.assertEqual(row["components_failing_natural_diagonal_spin_kernel"], 8)
        self.assertFalse(row["descends_to_natural_Spin4_Spin2_diagonal_quotient"])
        self.assertIsNone(row["descends_to_frozen_Gammahat_with_full_wall_R_data"])

    def test_wall_spin6_periods_are_index_integral(self):
        row = self.report["conditional_product_lift_wall_module"]["index_integrality_on_closed_spin6"]
        cc2 = sum(a*b for a, b in combinations(audit.E, 2))
        idx = audit.u**3/6-audit.u*audit.p/24
        expected = -audit.u*cc2+2*audit.u**3-6*idx
        self.assertEqual(sp.expand(sp.sympify(row["x_equals_2u_polynomial"])-expected), 0)
        self.assertTrue(row["all_periods_integer_in_this_product_spin_category"])
        self.assertFalse(row["relative_or_global_anomaly_trivialization_follows"])

    def test_scope_and_gates_stay_open(self):
        row = self.report["terminal_decision"]
        for key in ("frozen_Gammahat_wall_orbibundle_constructed", "full_bare_I6_cancelled_on_all_backgrounds",
                    "normal_lift_or_new_fermions_accepted_as_same_action_physics", "quantized_relative_WCS_Dai_Freed_trivialization_constructed"):
            self.assertFalse(row[key])
        self.assertEqual(row["closed_gates"], [])
        self.assertEqual(row["accepted_extensions"], 0)

    def test_rehashed_numeric_or_scope_mutation_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["conditional_product_lift_wall_module"]["components_failing_natural_diagonal_spin_kernel"] = 0
        changed["terminal_decision"]["full_bare_I6_cancelled_on_all_backgrounds"] = True
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(changed)

    def test_output_serializable_and_invalid_cover_rejected(self):
        self.assertEqual(json.loads(json.dumps(self.report)), self.report)
        for n in (0, -1, sp.Rational(1, 2), True):
            with self.assertRaises(ValueError):
                audit.fixed_normal_form(n)


if __name__ == "__main__":
    unittest.main()
