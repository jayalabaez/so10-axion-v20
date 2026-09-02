import copy
import json
import unittest

import susy_v89_c8_localized_bv_compact_globalization_audit as audit


class TestV89C8LocalizedBVCompactGlobalizationAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()

    def test_report_validates_and_core_is_canonical(self):
        audit.validate_report(self.report)
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))

    def test_parent_cores_are_pinned(self):
        self.assertEqual(self.report["input_core_hashes"], {
            "V69_route": audit.EXPECTED_CORES["v69"],
            "V70_route": audit.EXPECTED_CORES["v70"],
            "V87_route": audit.EXPECTED_CORES["v87"],
            "V88_route": audit.EXPECTED_CORES["v88"],
            "V88_master": audit.EXPECTED_CORES["v88_master"],
        })

    def test_c8_translation_solutions_are_exhaustive(self):
        row = self.report["C8_space_group_enumeration"]
        self.assertEqual(row["raw_translation_pairs_u_v"], [
            [0, 0], [0, 4], [2, 2], [2, 6], [4, 0], [4, 4], [6, 2], [6, 6],
        ])
        self.assertEqual(row["raw_translation_pair_count"], 8)

    def test_projector_preserving_c8_triples_are_all_even(self):
        row = self.report["C8_space_group_enumeration"]
        self.assertEqual(row["projector_preserving_translation_pairs"], [[2, 2], [2, 6], [6, 2], [6, 6]])
        self.assertEqual(row["projector_preserving_triple_count"], 8)
        self.assertTrue(row["all_projector_preserving_exponents_even"])
        self.assertFalse(row["every_exponent_triple_is_a_fully_correlated_Gammahat_cocycle"])

    def test_selected_space_group_image_is_c4_not_c8(self):
        row = self.report["C8_space_group_enumeration"]
        self.assertEqual(row["selected_representative_alpha_u_v"], [0, 2, 2])
        self.assertEqual(row["selected_generated_C8_subgroup_exponents"], [0, 2, 4, 6])
        self.assertFalse(row["primitive_k_in_selected_C8_factor_projection"])
        self.assertFalse(row["any_necessary_triple_projects_to_primitive_k"])

    def test_c8_selected_defects_reproduce_v88(self):
        row = self.report["C8_space_group_enumeration"]
        self.assertEqual(row["selected_relation_C8_exponents"], {
            "A4": 0, "UVUinvVinv": 0, "AUAinvVinv": 0, "AVAinvU": 4,
        })
        self.assertFalse(row["contains_pure_Spin11_center"])

    def test_external_c8_kernel_parity_and_bulk_descent(self):
        row = self.report["independent_external_C8_extension"]
        self.assertTrue(row["all_assigned_central_characters_annihilate_z_times_k4"])
        self.assertTrue(row["bulk_G8_representations_descend"])
        self.assertFalse(row["localized_induced_wall_quotient_representations_constructed"])
        self.assertEqual(row["bulk_SMW_reality_pairs_q8"]["A_11"], [6, 2])
        self.assertEqual(row["bulk_SMW_reality_pairs_q8"]["B_11"], [4, 4])
        self.assertEqual(row["bulk_SMW_reality_pairs_q8"]["C_11"], [6, 2])
        self.assertTrue(all(item["assigned_central_character_annihilates_z_times_k4"] for item in row["field_rows"]))
        self.assertTrue(all(item["c_plus_q8_mod2"] == 0 for item in row["field_rows"]))

    def test_external_c8_is_not_quantum_or_geometric_completion(self):
        row = self.report["independent_external_C8_extension"]["scope_boundary"]
        self.assertTrue(row["primitive_external_C8_kernel_parity_assignment_defined"])
        self.assertTrue(row["bulk_G8_representation_descent_constructed"])
        self.assertFalse(row["localized_wall_quotient_representation_descent_constructed"])
        self.assertFalse(row["primitive_k_generated_in_frozen_V88_geometric_C8_factor"])
        self.assertFalse(row["continuous_U1_8_parent_action_constructed"])
        self.assertFalse(row["symmetry_preserving_regulator_proved"])
        self.assertFalse(row["external_C8_quantum_gauging_accepted"])

    def test_z00_phase_rows_are_exact(self):
        row = self.report["localized_z00_candidate"]
        self.assertEqual(len(row["phase_rows"]), 7)
        self.assertTrue(all(item["gauge_exponent_equals_minus_X_mod8"] for item in row["phase_rows"]))
        self.assertTrue(all(item["invariant_component"] for item in row["phase_rows"]))
        self.assertTrue(all(item["fourth_power_matches_center"] for item in row["phase_rows"]))
        self.assertTrue(all(item["z_times_k4_exponent_mod2"] == 0 for item in row["phase_rows"]))

    def test_z00_placement_is_explicitly_new_action_data(self):
        row = self.report["localized_z00_candidate"]["new_action_datum"]
        self.assertTrue(row["changes_the_action_data"])
        self.assertFalse(row["was_fixed_by_V70_or_V88"])
        self.assertFalse(row["one_scalar_intrinsic_character_on_irreducible_Spin11_16"])
        self.assertTrue(row["split_component_characters_are_additional_action_data"])

    def test_localized_character_counts_are_exact(self):
        row = self.report["localized_z00_candidate"]["central_character_completion"]
        self.assertEqual(row["spinor_solution_count"], 8)
        self.assertEqual(row["center_even_solution_count"], 8)

    def test_smooth_connected_spin11_polynomial_is_bound(self):
        row = self.report["continuous_Cartan_and_charged_wall_anomaly_audit"]["smooth_connected_parent"]
        self.assertEqual(row["factorized_I8"], "-1/16 (trR2-trF2)(trR2+2trF2)")
        self.assertTrue(row["irreducible_trR4_zero"])
        self.assertTrue(row["irreducible_trF4_zero"])
        self.assertFalse(row["is_orbifold_fixed_wall_polynomial"])

    def test_cartan_anomaly_moments_are_exact(self):
        row = self.report["continuous_Cartan_and_charged_wall_anomaly_audit"]["Sp3_Cartan_hyper_contribution"]
        self.assertEqual(row["T_weights_on_6"], [2, 0, 2, -2, 0, -2])
        self.assertEqual(row["raw_moments_Tr6_T_power"], {"1": 0, "2": 16, "3": 0, "4": 64})
        self.assertEqual(row["SMW_effective_moments"], {"1": 0, "2": 8, "3": 0, "4": 32})
        self.assertEqual((row["dimension_weighted_q2"], row["dimension_weighted_q4"]), (88, 352))

    def test_continuous_u1t_gs_equations_have_exact_no_go(self):
        row = self.report["continuous_Cartan_and_charged_wall_anomaly_audit"]["continuous_U1_T_GS_equations"]
        self.assertEqual(row["unique_rational_solution_first_two"], ["-92/9", "26/9"])
        self.assertEqual(row["rational_solution_c_squared"], "-4784/81")
        self.assertEqual(row["required_c_squared"], "352/3")
        self.assertTrue(row["integral_lattice_first_equation_impossible"])
        self.assertTrue(row["third_equation_fails_even_over_Q"])
        self.assertFalse(row["gauged_continuous_U1_T_parent_with_current_spectrum_and_lattice"])
        self.assertFalse(row["finite_C4_subgroup_rejected_by_this_continuous_no_go"])

    def test_new_u1_vector_has_independent_gravitational_obstruction(self):
        row = self.report["continuous_Cartan_and_charged_wall_anomaly_audit"]["new_U1_vector_gravitational_obstruction"]
        self.assertEqual(row["baseline_H_V_T"], [299, 55, 1])
        self.assertEqual(row["after_gauging_H_V_T"], [299, 56, 1])
        self.assertEqual(row["H_minus_V_plus_29T_minus_273"], -1)
        self.assertTrue(row["irreducible_trR4_obstruction"])
        self.assertTrue(row["three_Abelian_GS_equations_still_fail_after_that_repair"])

    def test_c8_residues_do_not_fix_six_dimensional_polynomial(self):
        row = self.report["continuous_Cartan_and_charged_wall_anomaly_audit"]["C8_integer_lift_ambiguity"]
        self.assertEqual(row["examples"][0]["same_residue_mod8"], [5, -3])
        self.assertEqual(row["examples"][1]["same_residue_mod8"], [2, -6])
        self.assertFalse(row["mod8_residues_determine_six_dimensional_I8"])

    def test_charged_wall_log_twist_sum_is_zero_but_not_full_gysin(self):
        row = self.report["continuous_Cartan_and_charged_wall_anomaly_audit"]["charged_fermion_gauge_log_twist_component"]
        self.assertEqual(row["z00_U5_coefficient_sum_in_B_units"]["sum"], "0")
        self.assertEqual(row["z10_SU2_doublets"], 20)
        self.assertEqual(row["z01_SU2_doublets"], 20)
        self.assertTrue(row["component_sum_zero"])
        self.assertFalse(row["full_gravity_tensor_neutral_normal_bundle_Gysin_term_computed"])

    def test_fixed_wall_inputs_and_placement_are_not_frozen(self):
        row = self.report["fixed_wall_quantum_determinacy"]["same_4D_spectrum_different_field_support_example"]
        self.assertEqual(row["localized_family_support_A_z00_z11_z2orbit"], [3, 0, 0])
        self.assertEqual(row["localized_family_support_B_z00_z11_z2orbit"], [0, 3, 0])
        self.assertTrue(row["same_integrated_4D_family_spectrum"])
        self.assertTrue(row["different_delta_function_support"])
        self.assertTrue(row["demonstrates_localized_placement_not_frozen"])
        self.assertFalse(row["computes_a_nonzero_difference_of_anomaly_characters"])
        self.assertFalse(row["is_by_itself_a_proof_that_the_eta_characters_differ"])

    def test_common_bv_regulator_remains_open(self):
        row = self.report["fixed_wall_quantum_determinacy"]["BV_regulator_decision"]
        self.assertTrue(row["formal_charge_conjugate_pairs_can_be_written"])
        self.assertFalse(row["one_common_elliptic_gauge_fixed_complex_specified"])
        self.assertFalse(row["regulator_preserves_gauge_C8_and_supersymmetry_proved"])
        self.assertFalse(row["signed_fixed_wall_anomaly_character_computed"])

    def test_f4_section_counts_are_computed(self):
        self.assertEqual(audit.h0_f4(1, 12), 22)
        self.assertEqual(audit.h0_f4(2, 12), 27)
        self.assertEqual(audit.h0_f4(3, 12), 28)
        row = self.report["compact_globalization"]["generic_compact_smoothness"]
        self.assertEqual(row["section_counts"], {
            "h0_S_plus_12F": 22, "h0_2S_plus_12F": 27, "h0_3S_plus_12F": 28,
        })

    def test_global_blowups_are_projective_crepant(self):
        row = self.report["compact_globalization"]["global_blowup_sequence"]
        self.assertTrue(row["C_plus_C_minus_smooth_copies_of_S"])
        self.assertTrue(row["C_plus_C_minus_disjoint"])
        self.assertEqual(row["discrepancies"], [0, 0, 0])
        self.assertEqual(row["strict_transform_class"], "4H+2Kbar-2E_plus-2E_minus-E0=-K_Atilde")
        self.assertTrue(row["global_projective_crepant_sequence"])

    def test_generic_compact_smooth_member_exists_but_is_not_frozen(self):
        row = self.report["compact_globalization"]["generic_compact_smoothness"]
        self.assertTrue(row["moving_directions_basepoint_free_where_U_V_not_both_zero"])
        self.assertTrue(row["full_span_including_fixed_F0_basepoint_free_on_s_nonzero"])
        self.assertTrue(row["Bertini_nonempty_Zariski_open_smooth_away_from_S"])
        self.assertTrue(row["V88_resolved_charts_smooth_over_S"])
        self.assertTrue(row["generic_compact_smooth_resolved_member_exists"])
        self.assertTrue(row["rational_member_exists_over_infinite_field_Q"])
        self.assertFalse(row["specific_rational_coefficients_frozen"])

    def test_wrong_v87_cox_fan_is_not_reused(self):
        row = self.report["compact_globalization"]["Cox_and_Rees_boundary"]
        self.assertEqual(row["V87_32_cone_fan_applies_to"], "resolved Tate/Jacobian ambient")
        self.assertFalse(row["applies_to_P112_torsor_binomial_blowups"])
        self.assertFalse(row["resolved_Rees_algebra_presentation_constructed"])
        self.assertFalse(row["explicit_resolved_Jacobian_saturation_computed"])

    def test_natural_order_four_root_is_rejected_without_overgeneralization(self):
        row = self.report["compact_globalization"]["order_four_action_audit"]
        self.assertEqual(row["W_squared_factor"], -1)
        self.assertEqual(row["U2_minus_V2_squared_factor"], 1)
        self.assertFalse(row["single_hypersurface_eigenvalue_exists"])
        self.assertFalse(row["boundary_quartic_is_plus_or_minus_original"])
        self.assertTrue(row["natural_order4_root_rejected"])
        self.assertFalse(row["all_possible_order4_automorphisms_classified"])
        self.assertFalse(row["literal_global_order4_action_constructed"])

    def test_diagonal_orbibundle_remains_open(self):
        row = self.report["compact_globalization"]["diagonal_bundle_boundary"]
        self.assertEqual(row["bisection_deck_data"], "branched C2 cover")
        self.assertTrue(row["center_coset_j2_equals_z_is_necessary_not_sufficient"])
        self.assertFalse(row["ordinary_principal_C4_bundle_constructed"])
        self.assertFalse(row["diagonal_resolved_Gammahat_orbibundle_constructed"])

    def test_terminal_decision_is_fail_closed(self):
        row = self.report["terminal_decision"]
        self.assertTrue(row["independent_external_C8_kernel_parity_assignment_constructed"])
        self.assertTrue(row["audited_bulk_G8_representation_descent_constructed"])
        self.assertFalse(row["localized_wall_quotient_representation_descent_constructed"])
        self.assertTrue(row["C8_exponent_projections_enumerated_for_frozen_V88_lifts"])
        self.assertTrue(row["new_z00_split_U5_local_phase_candidate_constructed"])
        self.assertTrue(row["split_U5_component_characters_are_new_action_data"])
        self.assertFalse(row["rank_VEVs_preserve_primitive_C8"])
        self.assertTrue(row["smooth_connected_Spin11_I8_computed"])
        self.assertTrue(row["charged_fermion_gauge_log_twist_component_zero"])
        self.assertTrue(row["global_projective_crepant_torsor_blowups_constructed"])
        self.assertTrue(row["generic_compact_smooth_resolved_member_exists"])
        self.assertFalse(row["primitive_k_in_C8_factor_projection_for_frozen_V88_lifts"])
        self.assertFalse(row["gauged_continuous_U1_T_parent_current_spectrum"])
        self.assertFalse(row["accepted_full_parent_action_exists"])
        self.assertEqual(row["closed_gates"], [])
        self.assertFalse(row["theory_complete"])

    def test_all_gates_remain_open(self):
        self.assertEqual(set(self.report["gate_ledger"]), {f"G{index}" for index in range(1, 9)})
        self.assertTrue(all(value.startswith("OPEN:") for value in self.report["gate_ledger"].values()))

    def test_source_manifest_is_primary_and_canonical(self):
        row = self.report["source_manifest"]
        self.assertEqual(row["kind"], "primary_sources_only")
        self.assertEqual(row["count"], 7)
        self.assertEqual(row["catalog_sha256"], audit.canonical_sha(self.report["primary_sources"]))

    def test_validator_rejects_false_promotions_and_mutations(self):
        mutations = [
            lambda value: value["C8_space_group_enumeration"].__setitem__("primitive_k_in_selected_C8_factor_projection", True),
            lambda value: value["C8_space_group_enumeration"].__setitem__("projector_preserving_triple_count", 7),
            lambda value: value["C8_space_group_enumeration"].__setitem__("every_exponent_triple_is_a_fully_correlated_Gammahat_cocycle", True),
            lambda value: value["independent_external_C8_extension"]["field_rows"][0].__setitem__("c_plus_q8_mod2", 1),
            lambda value: value["independent_external_C8_extension"].__setitem__("localized_induced_wall_quotient_representations_constructed", True),
            lambda value: value["independent_external_C8_extension"]["scope_boundary"].__setitem__("external_C8_quantum_gauging_accepted", True),
            lambda value: value["localized_z00_candidate"]["new_action_datum"].__setitem__("was_fixed_by_V70_or_V88", True),
            lambda value: value["localized_z00_candidate"]["new_action_datum"].__setitem__("one_scalar_intrinsic_character_on_irreducible_Spin11_16", True),
            lambda value: value["localized_z00_candidate"]["scope_boundary"].__setitem__("localized_rank_VEVs_invariant_under_primitive_k", True),
            lambda value: value["localized_z00_candidate"]["phase_rows"][0].__setitem__("invariant_component", False),
            lambda value: value["continuous_Cartan_and_charged_wall_anomaly_audit"]["continuous_U1_T_GS_equations"].__setitem__("third_equation_fails_even_over_Q", False),
            lambda value: value["continuous_Cartan_and_charged_wall_anomaly_audit"]["continuous_U1_T_GS_equations"].__setitem__("gauged_continuous_U1_T_parent_with_current_spectrum_and_lattice", True),
            lambda value: value["continuous_Cartan_and_charged_wall_anomaly_audit"]["new_U1_vector_gravitational_obstruction"].__setitem__("irreducible_trR4_obstruction", False),
            lambda value: value["continuous_Cartan_and_charged_wall_anomaly_audit"]["charged_fermion_gauge_log_twist_component"].__setitem__("full_gravity_tensor_neutral_normal_bundle_Gysin_term_computed", True),
            lambda value: value["fixed_wall_quantum_determinacy"]["same_4D_spectrum_different_field_support_example"].__setitem__("different_delta_function_support", False),
            lambda value: value["fixed_wall_quantum_determinacy"]["same_4D_spectrum_different_field_support_example"].__setitem__("is_by_itself_a_proof_that_the_eta_characters_differ", True),
            lambda value: value["fixed_wall_quantum_determinacy"]["BV_regulator_decision"].__setitem__("signed_fixed_wall_anomaly_character_computed", True),
            lambda value: value["compact_globalization"]["global_blowup_sequence"].__setitem__("discrepancies", [0, 0, 1]),
            lambda value: value["compact_globalization"]["generic_compact_smoothness"].__setitem__("specific_rational_coefficients_frozen", True),
            lambda value: value["compact_globalization"]["Cox_and_Rees_boundary"].__setitem__("applies_to_P112_torsor_binomial_blowups", True),
            lambda value: value["compact_globalization"]["order_four_action_audit"].__setitem__("all_possible_order4_automorphisms_classified", True),
            lambda value: value["compact_globalization"]["diagonal_bundle_boundary"].__setitem__("diagonal_resolved_Gammahat_orbibundle_constructed", True),
            lambda value: value["terminal_decision"].__setitem__("accepted_full_parent_action_exists", True),
            lambda value: value["terminal_decision"].__setitem__("theory_complete", True),
            lambda value: value["gate_ledger"].__setitem__("G1", "CLOSED"),
        ]
        for mutate in mutations:
            value = copy.deepcopy(self.report)
            mutate(value)
            value["core_sha256"] = audit.canonical_sha(value)
            with self.assertRaises(RuntimeError):
                audit.validate_report(value)

    def test_generated_artifacts_are_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"), audit.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
