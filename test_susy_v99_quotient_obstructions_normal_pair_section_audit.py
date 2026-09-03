import copy
import json
import unittest
from unittest.mock import patch

import sympy as sp
import susy_v99_quotient_obstructions_normal_pair_section_audit as audit


class TestV99Route(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()

    def test_canonical_lineage(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        self.assertEqual(self.report["input_core_hashes"], {k: v[1] for k, v in audit.PARENTS.items()})

    def test_all_helpers_reconstruct(self):
        for key, module in zip(audit.KEYS, audit.MODULES):
            self.assertEqual(self.report[key], module.build_certificate())

    def test_all_helpers_bind_same_frozen_V98(self):
        for key in audit.KEYS:
            for parent, (_, core) in audit.PARENTS.items():
                self.assertEqual(self.report[key]["input_core_hashes"][parent], core)

    def test_source_and_test_pins(self):
        hashes = self.report["artifact_hashes"]
        self.assertEqual(hashes["generator_sha256"], audit.file_sha(audit.ROOT/(audit.__name__+".py")))
        self.assertEqual(hashes["test_sha256"], audit.file_sha(audit.TEST_PATH))
        for name, value in hashes.items():
            if name.endswith(".py"):
                self.assertEqual(value, audit.file_sha(audit.ROOT/name))

    def test_frozen_translation_character_root_obstruction(self):
        row = self.report["determinant_root_descent"]["frozen_square_space_group_root_obstruction"]
        self.assertEqual(row["D_holonomies_A_U_V"], ["1", "-1", "-1"])
        self.assertEqual(row["smith_diagonal"], [1, 2, 4])
        self.assertFalse(row["equivariant_square_root_on_unchanged_space_group_exists"])
        self.assertFalse(any(r["is_a_character_of_the_original_space_group"] for r in row["all_eight_root_lift_attempts"]))

    def test_central_extension_is_a_change_not_a_frozen_root(self):
        row = self.report["determinant_root_descent"]["frozen_square_space_group_root_obstruction"]["explicit_changed_central_extension"]
        self.assertFalse(row["central_extension_splits"])
        self.assertEqual(row["minimum_central_kernel_order_for_this_root_lift"], 2)
        self.assertEqual([r["new_stabilizer_order"] for r in row["fixed_strata"]], [4, 4, 4, 4])
        self.assertFalse(row["extension_installed_in_frozen_theory"])

    def test_root_choice_sign_includes_both_eta_and_cup(self):
        row = self.report["determinant_root_descent"]["chosen_root_response_ambiguity"]
        self.assertEqual(len(row["both_circle_spin_structure_tests"]), 2)
        for test in row["both_circle_spin_structure_tests"]:
            self.assertEqual(test["eta_relative_phase"], "+1")
            self.assertEqual(test["cup_change"], "3/2")
            self.assertEqual(test["combined_relative_phase"], "-1")
        self.assertFalse(row["specific_V98_response_descends_after_forgetting_root"])
        self.assertFalse(row["two_copies_have_full_root_independence_or_relative_gluing"])

    def test_chosen_cover_quantization_is_not_retracted(self):
        row = self.report["determinant_root_descent"]["bound_V98_quantized_chosen_root_response"]
        self.assertFalse(row["quantization_on_its_chosen_root_category_retracted"])
        c, x = sp.symbols("c x")
        self.assertEqual(sp.expand(sp.sympify(row["polynomial"])-2*c**3-c*c*x/2), 0)

    def test_bare_eta_kernel_checks_agree_independently(self):
        finite = self.report["determinant_root_descent"]["inherited_center_and_operator_descent"]
        normal = self.report["normal_half_period_pairing"]["shared_reflected_U5_pair"]
        self.assertEqual(finite["bare_natural_Spin_c_spinor_character"], normal["bare_eta_center_bits"])
        self.assertFalse(normal["bare_Spin_c_eta_operators_descend_through_full_internal_kernel"])
        self.assertFalse(finite["individual_operator_failure_alone_proves_combined_response_failure"])

    def test_normal_obstruction_exact_order_two(self):
        row = self.report["normal_half_period_pairing"]
        self.assertEqual(row["closed6_order_two_obstruction"]["exact_order"], 2)
        self.assertEqual(row["exact_normal_period_lattice"]["minimum_positive_stack_for_quantization_on_this_category"], 2)
        self.assertFalse(row["exact_normal_period_lattice"]["T_has_absolute_closed5_response_on_all_these_backgrounds"])

    def test_actual_slots_and_no_minimal_replacement(self):
        matter = self.report["spectator_replacement_anomaly"]
        self.assertEqual(matter["actual_old_slots"]["selected_six_dimensional_hypers"], 16)
        self.assertEqual(matter["actual_old_slots"]["removed_constant_N1_chiral_modes"], 0)
        row = matter["minimal_sixteen_replacement_obstruction"]
        self.assertEqual(row["enumerated_actual_removal_count"], 2956)
        self.assertEqual(row["rationally_factorizing_removals"], [])
        self.assertEqual(row["A_zero_forced_removal_counts"], [4, 8, 4, 0, 0])

    def test_larger_bounded_scan_not_accepted_at_rational_stage(self):
        row = self.report["spectator_replacement_anomaly"]["bounded_regular_character_extensions"]
        self.assertEqual((row["twenty_hyper_rational_candidates"], row["twenty_four_hyper_rational_candidates"]), (0, 1))
        candidate = [g for r in row["records"] for g in r["rational_candidates"]][0]
        self.assertEqual(candidate["c_prime"], ["-464", "-144"])
        self.assertEqual(candidate["ordinary_quotient_half_source"], ["-57", "-37/2"])
        self.assertFalse(candidate["q0_removal_count_even"])
        self.assertEqual(row["surviving_frozen_category_candidates"], 0)

    def test_new_modes_and_flavor_anomalies_not_discarded(self):
        row = self.report["spectator_replacement_anomaly"]["full_independent_flavor_replacement"]
        self.assertEqual((row["old_constant_modes_removed"], row["new_constant_modes_added"]), (0, 8))
        self.assertTrue(row["index_crosscheck_exact"])
        self.assertFalse(row["independent_flavor_anomaly_delta_vanishes"])
        self.assertFalse(row["masses_or_interactions_constructed"])

    def test_global_flavor_anomaly_not_mislabelled_as_automatic_inconsistency(self):
        row = self.report["spectator_replacement_anomaly"]["flavor_GS_and_full_representation_scope"]
        self.assertIn("not by itself a quantum inconsistency", row["global_flavor_vs_gauge_scope"])
        self.assertEqual(row["independent_new_SU4_test"]["primitive_c4_coefficient"], "-1/6")
        self.assertFalse(row["independent_new_SU4_test"]["ordinary_tensor_GS_products_can_cancel_c4_or_z_c3"])

    def test_common_normal_pair_does_not_factor_into_independent_repairs(self):
        row = self.report["normal_half_period_pairing"]["shared_reflected_U5_pair"]
        self.assertTrue(row["quantized_on_all_stated_common_closed5_backgrounds"])
        self.assertEqual(row["exact_identity_residual"], "0")
        self.assertEqual(row["independent_endpoint_obstruction_phase"], "-1")
        self.assertFalse(row["actual_orbifold_relative_gluing_constructed"])

    def test_gauge_and_normal_obstructions_not_confused(self):
        row = self.report["normal_half_period_pairing"]["separate_obstructions_retained"]
        self.assertFalse(row["gauge_quarter_removes_normal_half_period"])
        self.assertEqual(row["ordinary_spin_product_SU2_normal_doublet_phase"], "-1")
        self.assertFalse(row["normal_pair_quantization_determines_full_parent_SU2_or_defect_phase"])

    def test_particle_response_and_spectrum_scopes(self):
        checks = self.report["cross_sector_scope_checks"]
        self.assertTrue(checks["spectator_particle_and_determinant_root_response_are_distinct_options"])
        self.assertFalse(checks["response_eta_levels_are_new_particle_multiplicities"])
        self.assertFalse(checks["old_V97_Dirac_gap_applied_to_new_particles"])

    def test_no_full_theory_no_go_or_gate_promotion(self):
        self.assertFalse(self.report["supersession_boundary"]["full_theory_no_go_over_all_possible_redesigns_claimed"])
        decision = self.report["terminal_decision"]
        self.assertEqual(decision["closed_gates"], [])
        self.assertFalse(decision["theory_complete"])
        self.assertFalse(decision["same_action_microscopic_parent_accepted"])
        self.assertFalse(decision["original_section_system_solved"])

    def test_geometry_conditional_trace_does_not_assert_existence(self):
        row = self.report["original_section_elimination"]
        chart = row["exceptional_chart_exact_equations"]
        self.assertEqual(chart["equation_count"], 6)
        self.assertFalse(chart["candidate_z_H_found"])
        self.assertFalse(chart["K_discriminant_square_required_for_the_trace_point"])
        self.assertTrue(row["repeated_root_and_descent"]["z_square_remains_required_for_original_trace"])

    def test_geometry_height_bound_excludes_repeated_root(self):
        row = self.report["original_section_elimination"]["conditional_height_and_rank_compatibility"]
        self.assertEqual(row["geometric_D6_minimum_height_certificate"]["minimum_nonzero_geometric_height"], "5/2")
        self.assertEqual(row["conditional_geometric_height"], 4)
        self.assertTrue(row["repeated_root_subchart_exclusion"]["excluded_over_algebraic_closure_C_X"])
        self.assertTrue(row["conditional_geometric_primitivity"]["primitive_modulo_torsion"])
        self.assertFalse(row["original_section_existence_proved"])

    def test_geometry_rank_two_requires_actual_points_and_field_descent(self):
        row = self.report["original_section_elimination"]["conditional_height_and_rank_compatibility"]
        pair = row["conditional_two_cubic_points_independent"]
        self.assertTrue(pair["original_rank_at_least_two_if_z_and_K_discriminant_both_squares_and_chart_solution_exists"])
        self.assertTrue(pair["nonsquare_K_discriminant_only_forces_extension_rank_at_least_two"])
        self.assertFalse(pair["unconditional_original_rank_lower_bound_raised"])

    def test_all_eight_gates_open(self):
        self.assertEqual(set(self.report["gate_ledger"]), {"G"+str(i) for i in range(1, 9)})
        self.assertTrue(all(value.startswith("OPEN:") for value in self.report["gate_ledger"].values()))

    def test_F100_requires_a_real_changed_action(self):
        row = self.report["next_required_action"]
        self.assertEqual(row["id"], audit.NEXT_ID)
        self.assertFalse(row["accepted"])
        self.assertIn("explicit modified", row["primary"])
        self.assertIn("existence", row["parallel"])

    def test_sources_present_and_deduplicated(self):
        sources = self.report["primary_sources"]
        self.assertGreaterEqual(len(sources), 5)
        self.assertEqual(len(sources), len({row["url"] for row in sources}))
        self.assertTrue(all(row["url"].startswith("https://") and row["use"] for row in sources))

    def test_resealed_scope_tamper_rejected(self):
        report = copy.deepcopy(self.report)
        report["terminal_decision"]["theory_complete"] = True
        report["core_sha256"] = audit.canonical_sha(report)
        with self.assertRaises(RuntimeError):
            audit.validate_report(report)

    def test_parent_hash_tamper_rejected(self):
        with patch.object(audit.common, "load_bound", side_effect=RuntimeError("tampered")):
            with self.assertRaises(RuntimeError):
                audit.build_report()

    def test_generated_json_and_markdown_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"), audit.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
