"""V102 source binding, exact history retention and no false gate promotion."""
import copy
import json
import unittest
from unittest.mock import patch

import sympy as sp

import susy_v102_multipath_g1_frontier_master_audit as audit


class TestV102Master(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()
        cls.card = cls.report["consolidated_theory_card"]
        cls.previous = audit.load_bound(audit.V101_PATH, audit.EXPECTED_CORES["v101_master"])
        cls.route = audit.load_bound(audit.V102_PATH, audit.EXPECTED_CORES["v102_route"])

    def test_canonical_report(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))

    def test_fresh_reconstruction(self):
        audit.validate_report(self.report)

    def test_all29_historical_routes_exactly_preserved(self):
        self.assertEqual(self.report["route_matrix"][:-1], self.previous["route_matrix"])
        self.assertEqual(self.report["lineage"]["parent_route_matrix_sha256"], audit.canonical_sha(self.previous["route_matrix"]))
        self.assertEqual(self.card["historical_V101_card_sha256"], audit.canonical_sha(self.previous["consolidated_theory_card"]))

    def test_B102_is_unaccepted_route30(self):
        self.assertEqual(len(self.report["route_matrix"]), 30)
        row = self.report["route_matrix"][-1]
        self.assertEqual((row["route_id"], row["ordinal"]), ("B102", 30))
        self.assertFalse(row["accepted"])
        self.assertFalse(row["same_action_microscopic_completion"])

    def test_zero_accepted_extensions(self):
        self.assertEqual(self.card["accepted_extension_count"], 0)
        self.assertFalse(any(row["accepted"] for row in self.report["route_matrix"]))

    def test_all_four_frozen_helpers_embedded_exactly(self):
        self.assertEqual(len(audit.HELPER_KEYS), 4)
        for key in audit.HELPER_KEYS:
            self.assertEqual(self.card[key], self.route[key])
            self.assertEqual(self.card["bound_helper_core_hashes"][key], self.route[key]["core_sha256"])
            self.assertEqual(self.route[key]["core_sha256"], audit.canonical_sha(self.route[key]))

    def test_all_cubic_pivots_closed_with_exact_field_scope(self):
        self.assertTrue(self.card["exceptional_all_zero_linear_pivot_chart_excluded"])
        self.assertTrue(self.card["all_original_cubic_sections_excluded"])
        self.assertEqual(self.card["nonzero_linear_pivot_charts_still_open"], [])
        self.assertEqual(self.card["cubic_exclusion_original_field"], "C(X)(T)")
        self.assertEqual(self.card["cubic_exclusion_coefficient_field"], "C(X)")
        self.assertFalse(self.card["combined_cubic_exclusion_after_algebraic_constant_extension_claimed"])

    def test_higher_degree_denominators_and_actual_points_still_open(self):
        self.assertTrue(self.card["higher_polynomial_degree_or_T_denominator_search_open"])
        self.assertFalse(self.card["all_original_rational_sections_excluded"])
        self.assertFalse(self.card["actual_original_nonzero_section_constructed"])
        self.assertFalse(self.card["actual_target_sections_constructed"])
        self.assertFalse(self.card["historical_conditional_exceptional_pair_has_instance_on_original_member"])

    def test_rank_torsion_and_both_height_divisors_unchanged(self):
        for key in ("actual_original_MW_torsion_order", "actual_original_MW_free_rank_bounds", "conditional_unit_charge_section_height_S_F", "conditional_doubled_charge_section_height_S_F"):
            self.assertEqual(self.card[key], self.previous["consolidated_theory_card"][key])
        self.assertIsNone(self.card["actual_original_MW_free_rank"])

    def test_only_quartic_global_integral_chart_remains_without_point_or_rank_claim(self):
        q = self.card["surviving_global_integral_chart"]
        self.assertEqual(q["only_surviving_exact_degrees_x_y"], [4, 6])
        self.assertTrue(q["integral_means_P_dot_O_zero_globally_not_only_affine_T"])
        self.assertEqual(q["height_if_exists"], 4)
        self.assertEqual(q["target_to_quartic_height_ratios"], ["37/4", "37"])
        self.assertEqual(q["target_to_quartic_ratios_are_rational_squares"], [False, False])
        self.assertTrue(q["rank_at_least_two_if_quartic_and_either_target_both_exist_on_same_curve"])
        for key in ("quartic_point_constructed", "quartic_chart_excluded", "actual_rank_lower_bound_raised", "all_rational_sections_excluded"):
            self.assertFalse(q[key])
        T, x4, x3, y6, y5, a6, b9 = sp.symbols("T x4 x3 y6 y5 a6 b9")
        x, y = x4*T**4+x3*T**3, y6*T**6+y5*T**5
        residual = sp.Poly(y*y-x**3-a6*T**6*x-b9*T**9, T)
        self.assertEqual(residual.coeff_monomial(T**12), y6**2-x4**3)
        self.assertEqual([sp.degree(x**3, T), sp.degree(a6*T**6*x, T), sp.degree(b9*T**9, T)], q["degrees_x_cubed_Ax_B"])
        for target in (37, 148):
            ratio = sp.Rational(target, q["height_if_exists"])
            self.assertFalse(sp.sqrt(ratio).is_Rational)

    def test_natural_normal_pair_preserved(self):
        self.assertEqual(self.card["preserved_natural_Spin_c_normal_pair"], self.previous["consolidated_theory_card"]["preserved_natural_Spin_c_normal_pair"])

    def test_finite_locked_parity_is_actual_nine_singlets_not_V65(self):
        self.assertEqual(self.card["locked_odd_full_hypers"], 265)
        self.assertEqual(self.card["locked_odd_singlet_N1_zero_modes"], 9)
        self.assertFalse(self.card["odd_sector_is_V65_orphan_quark_pair"])
        f = self.card["finite_VEV_stabilizer"]
        self.assertEqual(f["known_finite_subgroup"]["exact_quotient_identity"], "P265=Rtilde^2 * k^4 * f")
        self.assertFalse(f["known_finite_subgroup"]["P265_is_old_universal_fermion_parity"])

    def test_named_stabilizer_not_full_quantum_stability(self):
        self.assertEqual((self.card["specified_finite_subgroup_order"], self.card["specified_finite_VEV_stabilizer_order"]), (64, 16))
        self.assertFalse(self.card["odd_state_stability_of_an_accepted_theory_proved"])
        f = self.card["finite_VEV_stabilizer"]
        self.assertFalse(f["full_stabilizer_boundary"]["full_unbroken_continuous_and_finite_group_classified"])
        self.assertFalse(f["component_characters_and_selection_rule"]["full_P265_quantum_anomaly_freedom_proved"])

    def test_complete_written_tensor_rank_and_GM_constraint(self):
        m = self.card["driver_mass_background"]["common_component_line_system"]
        self.assertEqual((m["number_of_equations"], m["number_of_fields"], m["matrix_rank"], m["rank_without_GM"]), (26, 22, 20, 19))
        self.assertEqual(m["all_equation_residuals"], ["0"]*26)

    def test_CP3_tensor_witness_not_full_normal_or_QK_action(self):
        row = self.card["driver_mass_background"]["CP3_common_tensor_witness_k0"]
        self.assertTrue(row["all_five_selected_VEV_lines_trivial"])
        self.assertEqual(row["P_over4_period"], "3/8")
        self.assertFalse(row["full_same_action_physical_background_proved"])
        self.assertFalse(self.card["full_normal_covariant_localized_representations_constructed"])
        self.assertFalse(self.card["nonlinear_QK_supersymmetric_vacuum_constructed"])

    def test_target_pole_budgets_and_divisibility_not_point_existence(self):
        self.assertEqual(self.card["target_O_intersections_by_height"], {"37": 17, "148": 72})
        a = self.card["target_height_pole_atlas"]
        targets = {r["height"]: r for r in a["target_sections"]}
        self.assertTrue(targets[37]["primitive_modulo_torsion_if_exists"])
        self.assertEqual(targets[148]["possible_nontrivial_integer_divisions"], [2])
        self.assertFalse(targets[148]["divisible_by_two_proved"])
        self.assertFalse(a["rank_one_target_boundary"]["original_rank_lower_bound_raised"])

    def test_global_pole_atlas_not_affine_denominator_assumption(self):
        a = self.card["target_height_pole_atlas"]
        targets = {r["height"]: r for r in a["target_sections"]}
        self.assertEqual(targets[37]["global_degrees_Z_U_V"], [17, 38, 57])
        self.assertEqual(targets[148]["global_degrees_Z_U_V"], [72, 148, 222])
        self.assertEqual(targets[37]["affine_U_degree_exact"], 37)
        self.assertFalse(targets[148]["all_O_intersections_forced_finite_in_T"])
        self.assertFalse(a["global_section_atlas"]["affine_denominator_degree_always_equals_global_n"])

    def test_generic_exclusion_not_uncontrolled_modular_scan(self):
        g = self.card["nonzero_pivot_section_elimination"]
        self.assertTrue(g["two_valuation_generic_exclusion"]["both_valuations_and_coordinate_axes_controlled"])
        self.assertFalse(g["two_valuation_generic_exclusion"]["generic_exclusion_from_modular_unit_ideal_alone_claimed"])
        self.assertFalse(g["shared_resultant_necessity"]["pairwise_resultants_claimed_sufficient_for_common_K_root"])

    def test_route_decisions_scopes_sources_and_next_copied_exactly(self):
        for key, source in (("strict_master_decision", "terminal_decision"), ("supersession_ledger", "supersession_boundary"),
                            ("cross_sector_scope_checks", "cross_sector_scope_checks"), ("gate_ledger", "gate_ledger"),
                            ("next_required_action", "next_required_action"), ("primary_sources", "primary_sources")):
            self.assertEqual(self.report[key], self.route[source])

    def test_all_eight_branch_gates_open_and_V21_preserved(self):
        self.assertEqual(set(self.report["gate_ledger"]), {"G"+str(i) for i in range(1, 9)})
        self.assertTrue(all(v.startswith("OPEN:") for v in self.report["gate_ledger"].values()))
        self.assertEqual(self.report["strict_master_decision"]["closed_gates"], [])
        self.assertTrue(self.report["lineage"]["canonical_V21_gate_scope_unchanged"])

    def test_no_complete_theory_or_empirical_claim(self):
        self.assertFalse(self.report["strict_master_decision"]["theory_complete"])
        self.assertFalse(self.report["strict_master_decision"]["same_action_microscopic_parent_accepted"])
        for key in ("experimental_confirmation", "full_quantum_anomaly_cancelled", "physical_background_category_identified", "same_action_spectrum_and_geometry_realized", "soft_spectrum_unification_cosmology_complete"):
            self.assertFalse(self.card[key])

    def test_next_obligation_is_F103(self):
        self.assertEqual(self.report["next_required_action"]["id"], audit.NEXT_ID)
        self.assertEqual(audit.NEXT_ID, "F103_HIGHER_SECTION_HEIGHT_ATLAS_AND_GLOBAL_QUANTUM_VACUUM_COMPLETION")

    def test_current_source_and_test_pins(self):
        self.assertEqual(self.report["artifact_hashes"]["generator_sha256"], audit.file_sha(audit.ROOT/(audit.__name__+".py")))
        self.assertEqual(self.report["artifact_hashes"]["test_sha256"], audit.file_sha(audit.TEST_PATH))

    def test_fresh_parent_route_and_helper_source_changes_rejected(self):
        original = audit.file_sha
        for name in ("susy_v101_multipath_g1_frontier_master_audit.py", "test_susy_v102_cubic_exclusion_common_tensor_target_audit.py",
                     "v102_driver_mass_background_audit.py", "test_v102_full_vev_finite_stabilizer_audit.py",
                     "v102_nonzero_pivot_section_elimination_audit.py", "test_v102_target_height_pole_atlas_audit.py"):
            with patch.object(audit, "file_sha", side_effect=lambda p: "0"*64 if p.name == name else original(p)):
                with self.assertRaises(RuntimeError):
                    audit.build_report()

    def test_resealed_history_scope_and_completion_mutations_rejected(self):
        for which in ("history", "closure", "rank", "all_rational", "field_scope", "tensor_completion", "quartic_point"):
            bad = copy.deepcopy(self.report)
            if which == "history":
                bad["route_matrix"][0]["accepted"] = True
            elif which == "closure":
                bad["strict_master_decision"]["theory_complete"] = True
            elif which == "quartic_point":
                bad["consolidated_theory_card"]["surviving_global_integral_chart"]["quartic_point_constructed"] = True
            else:
                key, value = {"rank": ("actual_original_MW_free_rank", 0),
                              "all_rational": ("all_original_rational_sections_excluded", True),
                              "field_scope": ("combined_cubic_exclusion_after_algebraic_constant_extension_claimed", True),
                              "tensor_completion": ("full_normal_covariant_localized_representations_constructed", True)}[which]
                bad["consolidated_theory_card"][key] = value
            bad["core_sha256"] = audit.canonical_sha(bad)
            with self.assertRaises(RuntimeError):
                audit.validate_report(bad)

    def test_generated_artifacts_and_readable_scope_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")), self.report)
        text = audit.render_markdown(self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"), text)
        for phrase in ("not its algebraic closure", "Higher polynomial degrees and T denominators remain OPEN", "not the V65 orphan quark pair", "not experimental confirmation"):
            self.assertIn(phrase, text)
        self.assertNotIn("| ---", text)


if __name__ == "__main__":
    unittest.main()
