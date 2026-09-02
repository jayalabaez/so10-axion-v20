"""Independent finite-linear-algebra and index checks for the F98 scout."""
import copy
from itertools import product
import unittest
from unittest.mock import patch

import sympy as sp
import v98_common_response_bordism_audit as audit


def binary_image(columns):
    vectors = {tuple(0 for _ in columns[0])}
    for column in columns:
        vectors |= {tuple(x ^ y for x, y in zip(v, column)) for v in list(vectors)}
    return vectors


class CommonResponseBordismTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_certificate()

    def test_certificate_is_canonical(self):
        self.assertEqual(self.report["core_sha256"], audit.common.canonical_sha(self.report))

    def test_four_exact_bordism_groups(self):
        rows = self.report["ordinary_spin_product_bordism"]
        self.assertEqual({key: row["Omega5"] for key, row in rows.items()},
                         {"local": "0", "common": "0", "local_with_R": "Z2", "common_with_R": "Z2"})

    def test_ahss_matrices_by_exhaustive_kernel_image(self):
        for row in self.report["ordinary_spin_product_bordism"].values():
            outgoing, incoming = row["d2_outgoing_H4_Z2_to_H2_Z2"], row["d2_incoming_H6_Z_to_H4_Z2"]
            kernel = {bits for bits in product((0, 1), repeat=len(row["degree4_basis"]))
                      if all(sum(x*y for x, y in zip(bits, line)) % 2 == 0 for line in outgoing)}
            image = binary_image(list(zip(*incoming)))
            self.assertTrue(image <= kernel)
            self.assertEqual(len(kernel)//len(image), row["group_order"])

    def test_common_ranks_and_dimensions(self):
        row = self.report["ordinary_spin_product_bordism"]["common"]
        self.assertEqual([len(row[k]) for k in ("degree2_basis", "degree4_basis", "degree6_basis")], [4, 12, 29])
        self.assertEqual((row["outgoing_rank"], row["incoming_rank"]), (4, 8))

    def test_local_ranks_and_dimensions(self):
        row = self.report["ordinary_spin_product_bordism"]["local"]
        self.assertEqual([len(row[k]) for k in ("degree2_basis", "degree4_basis", "degree6_basis")], [3, 7, 14])
        self.assertEqual((row["outgoing_rank"], row["incoming_rank"]), (3, 4))

    def test_SU2_class_not_a_U2_class(self):
        row = self.report["ordinary_spin_product_bordism"]["common_with_R"]
        rules = dict(zip(row["degree4_basis"], row["Sq2_degree4"]))
        self.assertEqual(sp.sympify(rules["A2"]), audit.a*audit.A2)
        self.assertEqual(sp.sympify(rules["B2"]), audit.b*audit.B2+audit.B3)
        self.assertEqual(rules["r2"], "0")
        self.assertEqual(row["surviving_dual_class"], "c2(R)")

    def test_common_cross_terms_are_killed(self):
        row = self.report["ordinary_spin_product_bordism"]["common"]
        rules = dict(zip(row["degree4_basis"], row["Sq2_degree4"]))
        self.assertEqual(sp.sympify(rules["a*b"]), audit.a**2*audit.b+audit.a*audit.b**2)
        self.assertEqual(rules["u**2"], "0")

    def test_no_higher_or_extension_ambiguity_hidden(self):
        for row in self.report["ordinary_spin_product_bordism"].values():
            self.assertIn("finite group", row["higher_differentials"])
            self.assertIn("one", row["extension_problem"])
            self.assertFalse(row["full_Gammahat_or_finite_symmetry_category_computed"])

    def test_bad_category_flags_rejected(self):
        for bad in (0, 1, "yes", None):
            with self.assertRaises(ValueError):
                audit.bordism_table(local=bad)

    def test_eta_levels_from_three_independent_local_pieces(self):
        self.assertEqual(self.report["common_integer_response"]["positive_eta_levels"],
                         {"D*M": 2*17+1, "D": 2*(-5), "M": 2*(-17)-1})

    def test_combined_polynomial_reconstructed_independently(self):
        a, b, ell, u, A2, B2, d, p = sp.symbols("a b ell u A2 B2 d p")
        cup = sp.sympify(self.report["common_integer_response"]["integral_cup_polynomial"])
        total = sp.sympify(self.report["common_integer_response"]["combined_I6_before_d_relation"])
        line_index = lambda z: z**3/sp.Integer(6)-z*p/sp.Integer(24)
        eta = 35*line_index(d+u)-10*line_index(d)-35*line_index(u)
        self.assertEqual(sp.expand((total-eta-cup).subs(d, a+b+2*ell)), 0)
        self.assertTrue(all(v.is_Integer for v in sp.Poly(cup, a, b, ell, u, A2, B2, d).coeffs()))

    def test_common_CP3_period_is_thirty_not_a_fraction(self):
        value = sp.sympify(self.report["common_integer_response"]["combined_I6_before_d_relation"])
        mapping = {audit.a: 1, audit.b: 0, audit.ell: 0, audit.u: 0,
                   audit.A2: 0, audit.B2: 0, audit.d: 1, audit.p: 4}
        self.assertEqual(value.subs(mapping), 30)

    def test_P_index_identity_independently(self):
        d, u, p = sp.symbols("d u p")
        index = lambda z: z**3/sp.Integer(6)-z*p/sp.Integer(24)
        self.assertEqual(sp.expand(index(2*d+u)-2*index(d+u)+index(u)), sp.expand(d*d*(d+u)))
        self.assertTrue(self.report["P_eta_cup_comparison"]["equal_on_all_closed_spin5_of_local_and_common_product_categories"])

    def test_equal_integer_responses_do_not_define_quarter_roots(self):
        self.assertFalse(self.report["P_eta_cup_comparison"]["equality_provides_canonical_quarter_roots"])
        self.assertEqual(self.report["quarter_class_and_changed_cover"]["old_category_CP3_period_P_over4"], "1/4")

    def test_closed5_uniqueness_not_full_theory_identification(self):
        row = self.report["common_integer_response"]
        self.assertTrue(row["closed5_phase_uniqueness_given_full_restricted_curvature"])
        self.assertFalse(row["actual_parent_anomaly_is_proved_to_factor_through_this_category"])
        self.assertFalse(row["all_boundary_trivializations_or_4D_counterterm_choices_unique"])
        self.assertFalse(row["independent_endpoint_gluing_or_full_equivariant_action_constructed"])

    def test_SU2_Witten_sign_retained(self):
        row = self.report["SU2_flat_refinement"]
        self.assertEqual(row["V97_added_normal_doublet_phase_on_generator"], "-1")
        self.assertEqual(row["P_eta_cup_ratio_on_generator"], "+1")
        self.assertFalse(row["V97_normal_doublet_nu_R_is_erased_by_continuous_gauge_factors"])
        self.assertFalse(row["original_parent_R_flat_phase_determined"])

    def test_determinant_double_cover_polynomial(self):
        self.assertEqual(sp.sympify(audit.determinant_cover(2)["P_over4_pullback"]), 2*audit.c**3+audit.c**2*audit.u)
        self.assertEqual(self.report["quarter_class_and_changed_cover"]["minimum_cover_degree"], 2)

    def test_cover_parity_samples_and_odd_CP3_witness(self):
        for degree in range(1, 33):
            row = audit.determinant_cover(degree)
            self.assertEqual(row["local_P_over4_quantized_on_this_cover"], degree % 2 == 0)
            if degree % 2:
                self.assertNotEqual(sp.Rational(row["CP3_period_mod1"]), 0)

    def test_cover_proof_symbolic_even_coefficients(self):
        k = sp.symbols("k", integer=True)
        expression = sp.expand((2*k*audit.c)**2*(2*k*audit.c+audit.u)/4)
        self.assertEqual(expression, 2*k**3*audit.c**3+k**2*audit.c**2*audit.u)

    def test_cover_invalid_input(self):
        for value in (0, -2, True, 1.5, "2"):
            with self.assertRaises(ValueError):
                audit.determinant_cover(value)

    def test_cover_not_silently_adopted(self):
        row = self.report["quarter_class_and_changed_cover"]
        self.assertTrue(row["global_gauge_group_and_allowed_bundles_changed"])
        for key in ("equivalent_reformulation_of_unchanged_theory", "new_cover_adopted_in_canonical_theory",
                    "original_D_odd_CP3_background_lifts_to_double_cover", "double_cover_repairs_geometric_Spin4_Spin2_identity_of_M_carrier",
                    "root_cover_bordism_or_discrete_equivariant_gluing_computed", "normal_root_or_independent_flavor_cover_alone_removes_quarter",
                    "adding_a_flat_closed5_character_repairs_nonintegral_curvature_periods"):
            self.assertFalse(row[key])

    def test_every_gate_remains_open(self):
        terminal = self.report["terminal_decision"]
        self.assertEqual(terminal["closed_gates"], [])
        self.assertFalse(terminal["full_quantum_Gammahat_parent_accepted"])

    def test_spin_c_quarter_identity_without_normal_root(self):
        row = self.report["natural_Spin_c_determinant_root_response"]
        c, x = sp.symbols("c x")
        self.assertEqual(sp.sympify(row["target_P_over4_with_D_C_squared"]), 2*c**3+c*c*x/2)
        self.assertEqual(sp.expand(sp.sympify(row["integer_virtual_index_J_C2_minus_2J_C_plus_J_1"])+c**3), 2*c**3+c*c*x/2)
        self.assertTrue(row["normal_square_root_not_needed_for_this_response"])

    def test_spin_c_eta_levels_are_integers(self):
        row = self.report["natural_Spin_c_determinant_root_response"]
        self.assertEqual(row["eta_integer_levels"], {"C^2": 1, "C": -2, "1": 1})
        self.assertIn("without choosing", row["definition_on_nonbounding_closed5"])

    def test_nonspin_example_by_holomorphic_Euler_characteristic(self):
        row = self.report["natural_Spin_c_determinant_root_response"]["CP2_times_CP1_example"]
        chi = lambda a, b: sp.Rational((a+1)*(a+2)*(b+1), 2)
        self.assertEqual([chi(1, 1), chi(0, 0), chi(-1, -1)], row["three_line_indices"])
        self.assertEqual(chi(1, 1)-2*chi(0, 0)+chi(-1, -1)+3, row["P_over4_period"])
        self.assertFalse(row["normal_square_root_exists"])

    def test_distinct_old_normal_half_period_not_removed(self):
        row = self.report["natural_Spin_c_determinant_root_response"]["distinct_V96_normal_repair_half_period"]
        self.assertEqual(row["old_target_period"], "3/2")
        self.assertEqual(row["new_quarter_response_period_on_this_test"], 0)
        self.assertFalse(row["old_normal_half_period_removed"])

    def test_spin_c_quantization_not_a_full_Gammahat_action(self):
        row = self.report["natural_Spin_c_determinant_root_response"]
        for key in ("all_full_Gammahat_tangential_backgrounds_identified_with_this_category",
                    "SU2_R_and_finite_defect_refinements_glued", "same_action_microscopic_inflow_or_boundary_state_constructed",
                    "changed_determinant_cover_adopted"):
            self.assertFalse(row[key])

    def test_resealed_false_conclusion_rejected(self):
        report = copy.deepcopy(self.report)
        report["terminal_decision"]["full_quantum_Gammahat_parent_accepted"] = True
        report["core_sha256"] = audit.common.canonical_sha(report)
        with self.assertRaises(RuntimeError):
            audit.validate_certificate(report)

    def test_source_lineage_tamper_rejected(self):
        with patch.object(audit.common, "file_sha", return_value="bad"):
            with self.assertRaises(RuntimeError):
                audit.build_certificate()


if __name__ == "__main__":
    unittest.main()
