import copy
from itertools import combinations, product
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import sympy as sp

import v95_wall_symmetry_lift_audit as audit


class TestV95WallSymmetryLiftAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parents = audit.load_parents()
        cls.report = audit.build_certificate()
        cls.normal = cls.parents["v94_route"]["normal_wall_quantization"]
        cls.rows = audit.block_specs(cls.normal)

    def test_canonical_parent_and_embedded_helper_pins(self):
        self.assertEqual(self.report["input_core_hashes"], {k: v[1] for k, v in audit.PARENTS.items()})
        self.assertEqual(self.report["embedded_parent_core_hashes"], {"v94_normal": audit.NORMAL_CORE, "v93_R_lift": audit.R_CORE})
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        audit.validate_certificate(self.report)

    def test_rehashed_parent_tampering_fails(self):
        original = Path.read_text
        def changed(path, *args, **kwargs):
            text = original(path, *args, **kwargs)
            if path.name == audit.PARENTS["v94_master"][0]:
                value = json.loads(text)
                value["input_core_hashes"]["v94_route"] = "bad"
                value["core_sha256"] = audit.canonical_sha(value)
                return json.dumps(value)
            return text
        with patch.object(Path, "read_text", changed):
            with self.assertRaises(RuntimeError):
                audit.load_parents()

    def test_full_kernel_preimage_independently_enumerated(self):
        old = [[0]*6, [1, 1, 1, 1, 1, 0], [0, 1, 0, 0, 0, 1], [1, 0, 1, 1, 1, 1]]
        actual = [list(v) for v in product(range(2), repeat=7) if [(v[0]+v[1]) % 2]+list(v[2:]) in old]
        self.assertEqual(len(actual), 8)
        self.assertEqual(actual, self.report["geometric_kernel"]["full_inverse_image_kernel"])
        self.assertEqual(sum(1 for v in product(range(2), repeat=7) if audit.center_map(v) == [0]*6), 2)

    def test_kernel_map_is_group_homomorphism(self):
        all_bits = list(product(range(2), repeat=7))
        for left in all_bits:
            for right in all_bits:
                self.assertEqual(audit.center_map(audit.xor(left, right)), audit.xor(audit.center_map(left), audit.center_map(right)))

    def test_D_is_identity_before_quotient_and_two_preimages_differ_by_D(self):
        self.assertEqual(audit.center_map(audit.D), [0]*6)
        self.assertEqual(audit.xor(audit.KROT_T, audit.KROT_N), audit.D)
        self.assertEqual(audit.center_map(audit.KROT_T), audit.center_map(audit.KROT_N))
        for bits in product(range(2), repeat=5):
            # Every independent internal representation has zero tangent and
            # normal charge and therefore evaluates to +1 on D.
            self.assertEqual(audit.dot_mod2([0, 0]+list(bits), audit.D), 0)

    def test_Clifford_lift_matrices(self):
        gamma = audit.clifford_generators()
        self.assertEqual(len(gamma), 6)
        for i in range(6):
            self.assertEqual(gamma[i].conjugate().T, gamma[i])
            for j in range(6):
                self.assertEqual(gamma[i]*gamma[j]+gamma[j]*gamma[i], 2*sp.eye(8) if i == j else sp.zeros(8))
        tangent, normal = gamma[0]*gamma[1], gamma[4]*gamma[5]
        self.assertEqual(tangent*normal, normal*tangent)
        self.assertEqual(tangent**2, -sp.eye(8))
        self.assertEqual(normal**2, -sp.eye(8))
        self.assertEqual(tangent**2*normal**2, sp.eye(8))

    def test_kernel_checks_and_boundaries(self):
        row = self.report["geometric_kernel"]
        self.assertTrue(all(row["checks"].values()))
        self.assertFalse(row["independent_R_flavor_or_C8_character_can_change_D"])
        self.assertFalse(row["existing_half_angle_factors_denied"])
        self.assertIn("unchanged", row["restriction"])

    def test_all_integer_normal_weights_fail_even_with_mod4_choices(self):
        for k in range(-8, 9, 2):
            self.assertEqual(audit.central_solutions(k), [])
            self.assertEqual(audit.central_solutions(k, modulus=4), [])

    def test_half_odd_integer_normal_weights_have_four_center_assignments(self):
        for k in range(-7, 8, 2):
            values = audit.central_solutions(k)
            self.assertEqual(values, [[0, 0, 1], [0, 1, 0], [1, 0, 0], [1, 1, 1]])
            self.assertEqual(len(audit.central_solutions(k, modulus=4)), 32)
            for r, h3, h267 in values:
                self.assertEqual((1+r+h3+h267) % 2, 0)
                self.assertEqual((k+r+h3+h267) % 2, 0)

    def test_N1_scalar_transport_for_general_integer_weights(self):
        for k in range(-5, 6):
            fermions = audit.central_solutions(k)
            scalars = audit.central_solutions(k+1, tangent_bit=0)
            self.assertEqual(sorted([[(r+1) % 2, a, b] for r, a, b in fermions]), sorted(scalars))
            self.assertEqual((1+k) % 2, (k+1) % 2)
            # The auxiliary scalar, shifted oppositely to the physical scalar,
            # has precisely the same center-character obstruction.
            self.assertEqual((k-1) % 2, (1+k) % 2)

    def test_exact_failing_blocks_not_just_total(self):
        rows = self.report["wall_module_descent"]["rows"]
        self.assertEqual({r["representation"]: r["failing_complex_Weyl_components"] for r in rows},
                         {"E": 0, "E_dual": 5, "det_E": 1, "det_E_inverse": 0, "singlet_positive": 2, "singlet_negative": 0})
        self.assertEqual(sum(r["copies"]*r["dimension"] for r in rows), 28)
        self.assertEqual(sum(r["failing_complex_Weyl_components"] for r in rows), 8)
        self.assertTrue(all(not r["central_solution_is_full_representation"] for r in rows))

    def test_candidate_parent_field_tampering_rejected(self):
        value = copy.deepcopy(self.normal)
        value["conditional_product_lift_wall_module"]["field_blocks"][1]["normal_charge_qN"] = "1/2"
        with self.assertRaises(RuntimeError):
            audit.block_specs(value)
        value = copy.deepcopy(self.normal)
        value["conditional_product_lift_wall_module"]["field_blocks"][0]["continuous_U1_8_charge"] = 1
        with self.assertRaises(RuntimeError):
            audit.block_specs(value)

    def test_selected_theta_has_trivial_entire_kernel_character(self):
        theta = [1, 1, 0, 1, 0, 0, 0]
        for g in self.report["geometric_kernel"]["full_inverse_image_kernel"]:
            self.assertEqual(audit.dot_mod2(theta, g), 0)
        row = self.report["N1_charge_bookkeeping"]
        self.assertEqual(row["theta_normal_charge"], "1/2")
        self.assertEqual(row["theta_R_Cartan_weight"], 1)
        self.assertFalse(row["V93_R_squared_equals_fermion_parity_was_imposed"])

    def test_N1_effective_normal_character_and_both_C4_C2_phases(self):
        zeta = (1+sp.I)/sp.sqrt(2)
        for k, r in product(range(-2, 3), repeat=2):
            q = sp.Rational(k, 2)
            self.assertEqual((q+sp.Rational(1, 2))-(r+1)/sp.Integer(2), q-r/sp.Integer(2))
            for multiple in (1, 2):
                self.assertEqual(sp.simplify(zeta**(multiple*(k+1-r-1))-zeta**(multiple*(k-r))), 0)
        self.assertEqual(sp.simplify(zeta*zeta**-1), 1)

    def test_N1_scalar_charge_table(self):
        values = {r["representation"]: r["scalar_normal_charge"] for r in self.report["wall_module_descent"]["rows"]}
        self.assertEqual(values, {"E": "1", "E_dual": "1/2", "det_E": "1/2", "det_E_inverse": "0", "singlet_positive": "3/2", "singlet_negative": "0"})

    def test_original_index_density_reconstructed_from_all_28_weights(self):
        total = sp.Integer(0)
        for row in self.rows:
            q = sp.Rational(row["normal_charge_qN"])
            for w in row["weights"]:
                root = sp.sympify(w)+q*audit.x
                total += row["copies"]*(root**3/6-root*audit.p/24)
        cc2 = sum(a*b for a, b in combinations(audit.E, 2))
        self.assertEqual(sp.expand(total+audit.x*cc2/2-audit.x*audit.p/8-audit.x**3/8), 0)
        self.assertEqual(sp.expand(total-sp.sympify(self.report["retained_internal_anomaly_curvatures"]["original_wall_I6"])), 0)

    def test_phase_neutralizing_R_assignment_does_not_repair_D(self):
        count = 0
        for row in self.rows:
            k = row["Spin2_integral_weight"]
            character = [1, k % 2, 0, k % 2, 0, 0, 0]
            self.assertEqual(audit.dot_mod2(character, audit.KROT_N), 0)
            self.assertEqual(audit.dot_mod2(character, audit.KROT_T), (1+k) % 2)
            self.assertEqual(audit.dot_mod2(character, audit.D), (1+k) % 2)
            count += row["copies"]*row["dimension"]*audit.dot_mod2(character, audit.D)
        self.assertEqual(count, 8)

    def test_full_R_curvature_shift_is_retained(self):
        row = self.report["retained_internal_anomaly_curvatures"]
        plain = sp.sympify(row["original_wall_I6"])
        new = sp.sympify(row["R_diagnostic_full_I6"])
        self.assertEqual(sp.expand(new-plain.subs(audit.x, audit.x+2*audit.y)), 0)
        cc2 = sum(a*b for a, b in combinations(audit.E, 2))
        expected = -audit.y*cc2+audit.p*audit.y/4+3*audit.x**2*audit.y/4+3*audit.x*audit.y**2/2+audit.y**3
        self.assertEqual(sp.expand(new-plain-expected), 0)
        self.assertEqual(sp.expand(sp.sympify(row["R_diagnostic_added_I6"])-expected), 0)

    def test_diagonal_locking_does_not_silently_preserve_normal_cancellation(self):
        row = self.report["retained_internal_anomaly_curvatures"]
        self.assertEqual(sp.expand(sp.sympify(row["R_diagnostic_full_I6"]).subs(audit.y, -audit.x/2)), 0)
        self.assertEqual(row["diagonal_connection_y_minus_x_over2_restriction"], "0")
        self.assertFalse(row["diagonal_restriction_cancels_frozen_bare_normal_anomaly"])
        self.assertNotEqual(sp.sympify(row["original_wall_I6"]), 0)

    def test_general_internal_shift_formula_at_each_block(self):
        extra = self.report["retained_internal_anomaly_curvatures"]["rows"]
        total = sp.Integer(0)
        for index, (source, row) in enumerate(zip(self.rows, extra)):
            d = sp.Symbol("d"+str(index))
            q = sp.Rational(source["normal_charge_qN"])
            before = after = sp.Integer(0)
            for w in source["weights"]:
                root = sp.sympify(w)+q*audit.x
                before += root**3/6-root*audit.p/24
                after += (root+d)**3/6-(root+d)*audit.p/24
            self.assertEqual(sp.expand(after-before-sp.sympify(row["one_copy_general_added_anomaly"])), 0)
            total += source["copies"]*(after-before)
        actual = sp.sympify(self.report["retained_internal_anomaly_curvatures"]["all_internal_Cartan_shifts_added_I6"])
        self.assertEqual(sp.expand(total-actual), 0)

    def test_R4_residue_is_not_continuous_anomaly_data(self):
        root, r = sp.symbols("root r")
        first = (root+r*audit.y)**3/6-(root+r*audit.y)*audit.p/24
        second = (root+(r+4)*audit.y)**3/6-(root+(r+4)*audit.y)*audit.p/24
        self.assertNotEqual(sp.expand(second-first), 0)
        self.assertEqual(sp.expand((second-first).subs(audit.y, 0)), 0)
        row = self.report["retained_internal_anomaly_curvatures"]
        self.assertFalse(row["R4_mod4_charges_determine_unique_continuous_anomaly"])
        self.assertTrue(row["flat_discrete_R4_has_no_nonzero_deRham_y_but_torsion_still_requires_audit"])

    def test_no_full_representation_or_gate_promotion(self):
        row = self.report["terminal_decision"]
        self.assertEqual(row["closed_gates"], [])
        self.assertEqual(row["accepted_extensions"], 0)
        self.assertTrue(row["all_eight_gates_remain_open"])
        for key in ("V94_unchanged_module_embeds_in_natural_Gammahat_pullback", "independent_internal_centers_repair_it", "new_full_wall_action_constructed", "every_possible_wall_completion_excluded", "full_bare_I6_cancelled"):
            self.assertFalse(row[key])
        self.assertFalse(self.report["retained_internal_anomaly_curvatures"]["new_curvatures_may_be_dropped_from_a_full_anomaly_claim"])

    def test_rehashed_false_promotion_and_altered_arithmetic_rejected(self):
        value = copy.deepcopy(self.report)
        value["terminal_decision"]["new_full_wall_action_constructed"] = True
        value["core_sha256"] = audit.canonical_sha(value)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(value)
        value = copy.deepcopy(self.report)
        value["wall_module_descent"]["failing_complex_Weyl_components"] = 0
        value["core_sha256"] = audit.canonical_sha(value)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(value)

    def test_exact_determinism_and_no_float_leakage(self):
        self.assertEqual(self.report, audit.build_certificate())
        self.assertEqual(json.loads(json.dumps(self.report)), self.report)
        def check(value):
            self.assertNotIsInstance(value, float)
            if isinstance(value, dict):
                for child in value.values():
                    check(child)
            if isinstance(value, list):
                for child in value:
                    check(child)
        check(self.report)

    def test_bad_input_domains_rejected(self):
        for value in ([0]*6, [2]*7, [0]*8):
            with self.assertRaises(ValueError):
                audit.center_map(value)
        for args in ((sp.Rational(1, 2),), (1, 2), (1, 1, 8)):
            with self.assertRaises(ValueError):
                audit.central_solutions(*args)


if __name__ == "__main__":
    unittest.main()
