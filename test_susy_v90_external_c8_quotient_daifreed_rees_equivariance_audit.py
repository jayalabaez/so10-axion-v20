import copy
import json
import unittest

import susy_v90_external_c8_quotient_daifreed_rees_equivariance_audit as audit


class TestV90ExternalC8QuotientDaiFreedReesEquivarianceAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()

    def test_report_validates_and_core_is_canonical(self):
        audit.validate_report(self.report)
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))

    def test_parent_cores_are_hash_pinned(self):
        self.assertEqual(self.report["input_core_hashes"], {
            "V70_route": audit.EXPECTED_CORES["v70"],
            "V87_route": audit.EXPECTED_CORES["v87"],
            "V88_route": audit.EXPECTED_CORES["v88"],
            "V89_route": audit.EXPECTED_CORES["v89"],
            "V89_master": audit.EXPECTED_CORES["v89_master"],
        })

    def test_component_extension_factor_set_is_exact(self):
        row = self.report["G8_component_extension"]
        self.assertEqual(row["component_group"], "C4")
        self.assertFalse(row["component_group_is_C8"])
        self.assertEqual(row["factor_set_rows"], [
            [0, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 1],
            [0, 1, 1, 1],
        ])
        self.assertTrue(row["factor_set_is_normalized_2_cocycle"])

    def test_component_extension_restricts_to_v87(self):
        row = self.report["G8_component_extension"]["restriction_to_j_equals_k2"]
        self.assertEqual(row["factor_set_rows"], [[0, 0], [0, 1]])
        self.assertEqual(row["extension_class"], "e|BC2=a^2")
        self.assertEqual(row["recovers_V87_condition"], "w2(V)=a^2")

    def test_quotient_has_secondary_character_obligation(self):
        row = self.report["G8_component_extension"]["H1_restriction_obstruction"]
        self.assertEqual(row["image_of_degree_one_generator"], 0)
        self.assertFalse(row["product_alpha_w4_can_restrict_to_a_w4"])

    def test_localized_component_characters_are_exact(self):
        row = self.report["localized_isotropy_characters"]
        self.assertEqual(len(row["phase_rows"]), 7)
        self.assertTrue(all(item["locally_invariant"] for item in row["phase_rows"]))
        self.assertTrue(all(item["fourth_power_matches_center"] for item in row["phase_rows"]))
        self.assertTrue(all(item["external_descent_parity"] == 0 for item in row["phase_rows"]))
        self.assertEqual(row["phase_rows_scope"], "corrected V90 D plus Dbar conditional local candidate")
        self.assertEqual(len(row["superseded_V89_comparison_phase_rows"]), 7)
        self.assertFalse(row["old_and_corrected_compensators_are_same_action_data"])
        repair = self.report["charged_neutral_and_compensator_repair"]
        self.assertEqual(
            row["corrected_rows_derived_from_action_charge_table_sha256"],
            repair["continuous_charge_table_sha256"],
        )
        action = {item["field"]: item for item in repair["continuous_charge_table"]}
        self.assertEqual(row["phase_rows"][-2]["external_q8"], action["D"]["finite_q8"])
        self.assertEqual(row["phase_rows"][-1]["external_q8"], action["Dbar"]["finite_q8"])
        self.assertFalse(row["single_intrinsic_character_preserves_full_localized_16"])

    def test_kernel_bit_completions_are_counted_not_selected(self):
        row = self.report["localized_isotropy_characters"]["kernel_bit_completion"]
        self.assertEqual(row["by_center_bit"]["0"]["count"], 8)
        self.assertEqual(row["by_center_bit"]["1"]["count"], 8)
        self.assertFalse(row["physical_completion_selected"])

    def test_all_four_normal_characters_are_frozen(self):
        row = self.report["localized_isotropy_characters"]["normal_characters"]
        self.assertEqual(row, {
            "z00": {"isotropy": "C4", "complex_normal_weight": 1},
            "z11": {"isotropy": "C4", "complex_normal_weight": 1},
            "z10": {"isotropy": "C2", "complex_normal_weight": 1},
            "z01": {"isotropy": "C2", "complex_normal_weight": 1},
        })

    def test_every_computed_hsieh_shadow_passes(self):
        rows = self.report["discrete_quantum_shadows"]["shadows"]
        self.assertEqual(set(rows), {
            "V88_compensated_full",
            "V88_uncompensated_full",
            "V89_superseded_z00_local_comparison",
            "V90_corrected_compensator_z00_visible_candidate",
            "V90_bulk_zero_mode_remainder",
        })
        self.assertTrue(all(row["linear_remainder"] == 0 for row in rows.values()))
        self.assertTrue(all(row["cubic_remainder"] == 0 for row in rows.values()))
        self.assertTrue(all(row["untwisted_Spin_x_C8_shadow_passes"] for row in rows.values()))

    def test_local_and_bulk_mixed_tensors_are_divisible_by_eight(self):
        row = self.report["discrete_quantum_shadows"]
        indices = [0, 1, 2, 3, 6, 7, 8]
        for name in (
            "V89_superseded_z00_local_comparison",
            "V90_corrected_compensator_z00_visible_candidate",
            "V90_bulk_zero_mode_remainder",
        ):
            self.assertTrue(all(row["tensors"][name][index] % 8 == 0 for index in indices))
        replacement = row["z00_compensator_replacement_derivation"]
        self.assertTrue(replacement["corrected_visible_local_tensor_is_derived"])
        self.assertFalse(replacement["charged_singlet_and_full_wall_projectors_included"])

    def test_neutral_choice_proves_quantum_underdetermination(self):
        row = self.report["discrete_quantum_shadows"]["neutral_underdetermination_witness"]
        self.assertEqual(row["two_center_compatible_choices"], [0, 2])
        self.assertEqual(row["change_in_linear_expression_mod8"], 4)
        self.assertEqual(row["change_in_cubic_expression_mod48"], 0)
        self.assertTrue(row["zero_mode_shadow_can_change_if_both_choices_are_realized"])
        self.assertFalse(row["two_complete_SMW_Gammahat_realizations_constructed"])
        self.assertFalse(row["full_quotient_character_change_constructed"])

    def test_bv_and_full_quotient_character_remain_open(self):
        row = self.report["discrete_quantum_shadows"]["BV_regulator_boundary"]
        self.assertFalse(row["antifields_are_opposite_physical_chiral_determinants"])
        self.assertFalse(row["elliptic_gauge_fixed_complex_constructed"])
        self.assertFalse(row["Pfaffian_orientation_computed"])
        self.assertFalse(row["relative_differential_WCS_cocycle_constructed"])
        self.assertFalse(row["full_G8_Dai_Freed_character_computed"])

    def test_unmodified_continuous_parent_has_universal_sign_no_go(self):
        row = self.report["unmodified_continuous_parent"]
        self.assertEqual(row["P_lower_bound"], 24)
        self.assertEqual(row["n_Phi_values"], [1, 2])
        self.assertTrue(row["contradiction_even_over_R"])
        self.assertTrue(all(item["c_squared_negative"] for item in row["minimal_examples"]))
        self.assertFalse(row["unmodified_parent_accepted"])

    def test_repair_moments_and_gravity_count_are_exact(self):
        row = self.report["charged_neutral_and_compensator_repair"]
        self.assertEqual(row["new_action_data"]["bulk_charge_magnitudes"], [6, 4, 6])
        self.assertEqual(row["new_action_data"]["singlet_hyper_counts_by_charge_magnitude"], {
            "0": 150, "2": 2, "4": 11, "6": 8, "8": 96,
        })
        self.assertEqual(row["new_action_data"]["H_V_T"], [300, 56, 1])
        self.assertEqual(row["new_action_data"]["total_singlet_hypers"], 267)
        self.assertEqual(row["new_action_data"]["charged_singlet_hypers"], 117)
        self.assertEqual(row["new_action_data"]["uncharged_singlet_hypers"], 150)
        self.assertTrue(row["new_action_data"]["smooth_bulk_GS_equations_solved"])
        self.assertFalse(row["new_action_data"]["localized_continuous_I6_and_inflow_constructed"])
        self.assertTrue(row["new_action_data"]["two_distinct_charge8_hypers_proposed_for_Phi_plus_and_Phi_minus_zero_modes"])
        self.assertFalse(row["new_action_data"]["explicit_SMW_Gammahat_projectors_for_Phi_zero_modes_constructed"])
        self.assertEqual(row["moments"]["D2"], 7584)
        self.assertEqual(row["moments"]["D4"], 437760)

    def test_repair_GS_equations_are_exact(self):
        row = self.report["charged_neutral_and_compensator_repair"]["GS_solution"]
        self.assertEqual(row["c"], [-480, -152])
        self.assertEqual(row["a_dot_c"], "-1264")
        self.assertEqual(row["minus_D2_over_6"], "-1264")
        self.assertEqual(row["b_over_2_dot_c"], "88")
        self.assertEqual(row["bulk_P"], 88)
        self.assertEqual(row["three_c_squared"], "437760")
        self.assertEqual(row["D4"], 437760)

    def test_repair_has_no_certified_physical_tensor_sheet(self):
        row = self.report["charged_neutral_and_compensator_repair"]["tensor_sheets"]
        self.assertEqual(row["frozen_j_plus"]["j_dot_c"], "-556")
        self.assertFalse(row["frozen_j_plus"]["U1_kinetic_positive"])
        self.assertEqual(row["opposite_j_minus_scout"]["j_dot_c"], "424")
        self.assertEqual(row["opposite_j_minus_scout"]["j_dot_a"], "-9/2")
        self.assertFalse(row["opposite_j_minus_scout"]["physical_cone_and_string_tensions_certified"])
        self.assertFalse(row["repair_accepted_on_physical_tensor_sheet"])

    def test_old_compensator_portals_are_retracted(self):
        row = self.report[
            "charged_neutral_and_compensator_repair"
        ]["old_V88_compensator_retraction"]
        self.assertEqual(row["representatives_as_signed_totals"], [-4, 4])
        self.assertFalse(row["X_plus_or_minus10_insertions_can_neutralize"])
        self.assertFalse(row["decay_portals_certified"])

    def test_corrected_compensator_continuous_residues_and_local_phases(self):
        section = self.report["charged_neutral_and_compensator_repair"]
        fields = {row["field"]: row for row in section["continuous_charge_table"]}
        self.assertEqual(section["continuous_charge_table_sha256"], audit.EXPECTED_ACTION_CHARGE_TABLE_SHA)
        self.assertEqual(
            section["continuous_charge_table_sha256"],
            audit.canonical_sha(section["continuous_charge_table"]),
        )
        self.assertEqual(
            section["operator_charge_registry_sha256"],
            audit.canonical_sha(section["operator_charge_registry"]),
        )
        self.assertEqual(
            (fields["D"]["continuous_U1_8_charge"], fields["D"]["finite_q8"], fields["D"]["Z4R"]),
            (6, 6, 0),
        )
        self.assertEqual(
            (fields["Dbar"]["continuous_U1_8_charge"], fields["Dbar"]["finite_q8"], fields["Dbar"]["Z4R"]),
            (-2, 6, 2),
        )
        phases = section["corrected_compensator"]["local_phase_rows"]
        self.assertEqual([(row["gauge_exponent"], row["intrinsic_exponent"]) for row in phases], [(6, 2), (2, 6)])
        self.assertTrue(all(row["sum_mod8"] == 0 and row["center_bit"] == 0 for row in phases))

    def test_operator_ledger_allows_and_forbids_intended_terms(self):
        rows = {
            row["operator"]: row
            for row in self.report[
                "charged_neutral_and_compensator_repair"
            ]["corrected_compensator"]["operator_ledger"]
        }
        self.assertTrue(rows["Phi- B0 D Dbar/M*"]["superpotential_allowed"])
        self.assertTrue(rows["Phi- B0 H_uA Dbar/M*"]["superpotential_allowed"])
        self.assertTrue(rows["D 10 10"]["superpotential_allowed"])
        self.assertTrue(rows["D 5bar 1"]["superpotential_allowed"])
        self.assertFalse(rows["Phi+ Dbar 10 5bar"]["superpotential_allowed"])
        self.assertFalse(rows["Phi+ B0 F^4"]["superpotential_allowed"])
        self.assertTrue(rows["K: Phi- B0^dag H_uA H_dC/M*^2"]["Kahler_allowed"])
        registry = self.report["charged_neutral_and_compensator_repair"]["operator_charge_registry"]
        action = {
            row["field"]: row
            for row in self.report["charged_neutral_and_compensator_repair"]["continuous_charge_table"]
        }
        for name, x_charge in action["F_i"]["U1_X_charge_by_component"].items():
            self.assertEqual(registry[name]["U1_X"], x_charge)
            self.assertEqual(registry[name]["U1_8"], action["F_i"]["continuous_U1_8_charge"])
        self.assertEqual(registry["B0_dag"]["U1_8"], -registry["B0"]["U1_8"])
        self.assertEqual(registry["B0_dag"]["U1_X"], -registry["B0"]["U1_X"])
        for row in rows.values():
            self.assertEqual(row["U1_8_sum"], sum(registry[name]["U1_8"] for name in row["factors"]))
            self.assertEqual(row["U1_X_sum"], sum(registry[name]["U1_X"] for name in row["factors"]))
            self.assertEqual(row["Z4R_sum_mod4"], sum(registry[name]["Z4R"] for name in row["factors"]) % 4)
        gm = self.report[
            "charged_neutral_and_compensator_repair"
        ]["corrected_compensator"]["GM_operator"]
        gm_row = rows[gm["bound_operator_ledger_name"]]
        self.assertEqual(gm["continuous_charge_sum"], gm_row["U1_8_sum"])
        self.assertEqual(gm["U1_X_sum"], gm_row["U1_X_sum"])
        self.assertEqual(gm["allowed"], gm_row["Kahler_allowed"])

    def test_rank_two_mass_matrix_and_tree_elimination_are_exact(self):
        row = self.report[
            "charged_neutral_and_compensator_repair"
        ]["corrected_compensator"]
        matrix = row["doublet_mass_matrix"]
        self.assertEqual(matrix["rank"], 2)
        self.assertEqual(matrix["nonzero_2x2_minor"], "M*a")
        self.assertEqual(matrix["left_null_light_Hu"], ["M", "0", "-mu"])
        self.assertEqual(matrix["right_null_light_Hd"], ["0", "1", "0"])
        self.assertTrue(matrix["left_null_verified_symbolically"])
        self.assertTrue(matrix["right_null_verified_symbolically"])
        elimination = row["tree_level_elimination"]
        self.assertEqual(elimination["effective_superpotential"], "-A_matter*H_uA*mu/M")
        self.assertFalse(elimination["A_matter_squared_term_generated_by_this_exchange"])
        self.assertFalse(elimination["holomorphic_dimension5_four_matter_generated_by_this_exchange"])

    def test_corrected_visible_tensor_is_derived_but_full_finite_anomaly_is_open(self):
        row = self.report["charged_neutral_and_compensator_repair"]["visible_zero_mode_conditional_shadow"]
        self.assertEqual(row["corrected_visible_tensor"], [72, 88, 2448, 2368, 352, 9664, 96, 384, 192])
        self.assertEqual(
            audit.anomaly_tensor(row["component_rows"]),
            dict(zip(row["tensor_order"], row["corrected_visible_tensor"])),
        )
        self.assertEqual(
            audit.anomaly_tensor(row["signed_component_rows"]),
            dict(zip(row["tensor_order"], row["signed_4d_shadow"])),
        )
        self.assertTrue(row["all_visible_entries_zero_mod8"])
        self.assertEqual(row["linear_shadow_mod8"], 0)
        self.assertEqual(row["cubic_shadow_mod48"], 0)
        self.assertFalse(row["signed_shadow_is_full_six_dimensional_or_fixed_wall_I8"])
        self.assertFalse(row["charged_singlet_zero_mode_projectors_frozen"])
        self.assertFalse(row["full_repaired_action_finite_anomaly_cancelled"])

    def test_vacuum_is_D_flat_but_breaks_C8_to_C2(self):
        row = self.report["charged_neutral_and_compensator_repair"]["vacuum"]
        self.assertEqual(row["VEV_charge_gcd"], 2)
        self.assertFalse(row["primitive_C8_preserved"])
        self.assertEqual(row["unbroken_external_subgroup"], "C2")
        self.assertTrue(row["Z4R_preserved"])
        self.assertTrue(row["zero_mode_realization_conditional_on_unbuilt_projectors"])
        self.assertEqual(row["F_driver_residuals_after_symbolic_witness"], ["0", "0", "0"])
        self.assertEqual(row["D8_after_symbolic_witness"], "0")
        self.assertTrue(row["F_and_D_witness_verified_symbolically"])

    def test_explicit_member_degrees_and_boundary_are_exact(self):
        row = self.report["explicit_compact_member_and_Rees_certificate"]
        self.assertEqual(row["ambient_Cox_degrees"]["L"], [3, 12])
        self.assertEqual(row["ambient_Cox_degrees"]["each_p_i"], [2, 12])
        self.assertEqual(row["coefficient_payload_sha256"], audit.canonical_sha(row["coefficient_payload"]))
        self.assertEqual(row["coefficient_payload_sha256"], audit.EXPECTED_MEMBER_COEFFICIENT_SHA)
        self.assertEqual(row["coefficient_payload_sha256"], row["expected_coefficient_payload_sha256"])
        self.assertTrue(row["V87_coefficient_construction_relations_checked"])
        self.assertEqual(row["mechanically_derived_nonzero_coefficient_bidegrees"], {
            "L": [3, 12], "p0": [2, 12], "p1": [2, 12],
            "p4": [2, 12], "R0": [1, 12], "R4": [1, 12],
        })
        self.assertTrue(row["boundary"]["P_plus_derived_from_payload"])
        self.assertTrue(row["boundary"]["P_minus_derived_from_payload"])
        self.assertEqual(row["boundary"]["discriminant_P_plus_dehomogenized"], -256)
        self.assertEqual(row["boundary"]["discriminant_P_minus_dehomogenized"], -2048)
        self.assertEqual(row["boundary"]["resultant_dehomogenized"], 1)
        self.assertTrue(row["boundary"]["eight_simple_pairwise_disjoint_branch_points"])

    def test_all_four_away_S_Groebner_bases_are_unit(self):
        row = self.report["explicit_compact_member_and_Rees_certificate"]["away_from_S"]
        self.assertEqual(len(row["rows"]), 4)
        self.assertTrue(row["all_four_unit_ideals"])
        self.assertTrue(all(
            item["Q_derived_directly_from_frozen_payload"]
            and item["case_X_zero_reduced_lex_basis"] == ["1"]
            and item["case_X_nonzero_reduced_grevlex_basis"] == ["1"]
            and item["unit_ideal_by_exhaustive_case_split"]
            for item in row["rows"]
        ))
        self.assertTrue(all(item["term_count"] == 10 for item in row["rows"]))
        self.assertEqual(row["aggregate_row_sha256"], audit.canonical_sha(row["rows"]))

    def test_Rees_presentation_and_finite_cover_are_exact(self):
        row = self.report["explicit_compact_member_and_Rees_certificate"]
        rees = row["Rees_presentation"]
        self.assertEqual(rees["first_centers"], ["I+=(s,W,a)", "I-=(s,W,b)"])
        self.assertEqual(rees["total_pullback_factor"], "e0*e_plus^2*e_minus^2")
        self.assertTrue(rees["symbolic_pullback_factorization_checked"])
        self.assertEqual(len(rees["final_local_chart_rows_bound_from_V88"]), 4)
        self.assertTrue(rees["all_final_local_chart_bases_are_unit"])
        self.assertTrue(rees["V88_nonbranch_unit_locus_smooth_after_second_blowup"])
        cover = row["cover_argument"]
        self.assertTrue(cover["finite_standard_open_localization_certificate"])
        self.assertTrue(cover["resolved_space_smooth_by_finite_localization_cover"])
        self.assertFalse(cover["literal_named_B_Rees_colon_computed"])
        self.assertFalse(cover["single_printed_homogeneous_colon_Groebner_basis_claimed"])
        self.assertTrue(row["resolved_compact_member_smooth"])

    def test_stabilizer_is_mu4_times_mu2_and_has_no_deck_root(self):
        row = self.report["global_equivariance_classification"]
        self.assertEqual(row["stabilizer_mod_Cox_tori"], "mu4 x mu2")
        self.assertEqual(len(row["group_elements"]), 8)
        self.assertEqual(
            [item["order"] for item in row["group_elements"]],
            [1, 2, 4, 4, 2, 2, 4, 4],
        )
        self.assertTrue(row["literal_order4_map_lifts_to_resolved_space"])
        self.assertFalse(row["literal_order4_square_is_deck"])
        self.assertFalse(row["any_classified_order4_element_squares_to_deck"])
        self.assertFalse(row["required_diagonal_Gammahat_action_constructed"])
        self.assertFalse(row["exotic_non_projection_descending_automorphisms_classified"])

    def test_terminal_decision_preserves_fail_closed_boundaries(self):
        row = self.report["terminal_decision"]
        self.assertTrue(row["specific_rational_compact_member_frozen"])
        self.assertTrue(row["resolved_compact_member_smooth"])
        self.assertTrue(row["literal_global_C4_action_constructed"])
        self.assertTrue(row["unmodified_continuous_U1_8_parent_rejected"])
        self.assertFalse(row["full_G8_quotient_Dai_Freed_character_computed"])
        self.assertFalse(row["Phi_zero_mode_Gammahat_projectors_constructed"])
        self.assertFalse(row["localized_continuous_inflow_constructed"])
        self.assertFalse(row["repaired_action_full_finite_anomaly_cancelled"])
        self.assertFalse(row["repair_physical_tensor_cone_certified"])
        self.assertFalse(row["primitive_C8_preserved_by_repair_vacuum"])
        self.assertFalse(row["classified_order4_deck_root_exists"])
        self.assertFalse(row["accepted_full_parent_action_exists"])
        self.assertFalse(row["theory_complete"])

    def test_every_SUSY_C8_branch_gate_remains_open(self):
        self.assertEqual(set(self.report["gate_ledger"]), {f"G{index}" for index in range(1, 9)})
        self.assertTrue(all(value.startswith("OPEN:") for value in self.report["gate_ledger"].values()))
        self.assertEqual(self.report["terminal_decision"]["closed_gates"], [])

    def test_next_obligation_is_F91(self):
        row = self.report["next_required_action"]
        self.assertEqual(row["id"], "F91_FINITE_G8_BORDISM_WCS_OR_PHYSICAL_TENSOR_CONE_DECISION")
        self.assertFalse(row["accepted"])

    def test_source_manifest_is_canonical(self):
        row = self.report["source_manifest"]
        self.assertEqual(row["kind"], "primary_sources_only")
        self.assertEqual(row["count"], 6)
        self.assertEqual(row["catalog_sha256"], audit.canonical_sha(self.report["primary_sources"]))

    def test_validator_rejects_false_promotions(self):
        def mutate_b0_dagger_with_rehash(value):
            repair = value["charged_neutral_and_compensator_repair"]
            repair["operator_charge_registry"]["B0_dag"]["U1_8"] = -12
            repair["operator_charge_registry_sha256"] = audit.canonical_sha(
                repair["operator_charge_registry"]
            )

        mutations = [
            lambda value: value["terminal_decision"].__setitem__("full_G8_quotient_Dai_Freed_character_computed", True),
            lambda value: value["terminal_decision"].__setitem__("common_BV_regulator_constructed", True),
            lambda value: value["terminal_decision"].__setitem__("Phi_zero_mode_Gammahat_projectors_constructed", True),
            lambda value: value["terminal_decision"].__setitem__("repaired_action_full_finite_anomaly_cancelled", True),
            lambda value: value["terminal_decision"].__setitem__("repair_physical_tensor_cone_certified", True),
            lambda value: value["terminal_decision"].__setitem__("primitive_C8_preserved_by_repair_vacuum", True),
            lambda value: value["terminal_decision"].__setitem__("classified_order4_deck_root_exists", True),
            lambda value: value["terminal_decision"].__setitem__("diagonal_resolved_Gammahat_orbibundle_constructed", True),
            lambda value: value["terminal_decision"].__setitem__("accepted_full_parent_action_exists", True),
            lambda value: value["terminal_decision"].__setitem__("theory_complete", True),
            lambda value: value["charged_neutral_and_compensator_repair"].__setitem__("accepted_same_action_parent", True),
            lambda value: value["charged_neutral_and_compensator_repair"]["continuous_charge_table"][-2].__setitem__(
                "continuous_U1_8_charge", 14
            ),
            lambda value: value["charged_neutral_and_compensator_repair"]["corrected_compensator"]["operator_ledger"][8].__setitem__(
                "U1_X_sum", 4
            ),
            lambda value: value["charged_neutral_and_compensator_repair"]["corrected_compensator"]["doublet_mass_matrix"].__setitem__(
                "rank", 3
            ),
            mutate_b0_dagger_with_rehash,
            lambda value: value["localized_isotropy_characters"]["phase_rows"][-2].__setitem__(
                "external_q8", 2
            ),
            lambda value: value["charged_neutral_and_compensator_repair"]["corrected_compensator"]["GM_operator"].__setitem__(
                "continuous_charge_sum", 8
            ),
            lambda value: value["charged_neutral_and_compensator_repair"]["corrected_compensator"]["GM_operator"].__setitem__(
                "nonzero_hidden_sector_numerator_constructed", True
            ),
            lambda value: value["charged_neutral_and_compensator_repair"]["corrected_compensator"].__setitem__(
                "local_wall_quotient_constructed", True
            ),
            lambda value: value["explicit_compact_member_and_Rees_certificate"]["cover_argument"].__setitem__(
                "single_printed_homogeneous_colon_Groebner_basis_claimed", True
            ),
            lambda value: value["gate_ledger"].__setitem__("G1", "CLOSED"),
        ]
        for mutate in mutations:
            candidate = copy.deepcopy(self.report)
            mutate(candidate)
            candidate["core_sha256"] = audit.canonical_sha(candidate)
            with self.assertRaises(RuntimeError):
                audit.validate_report(candidate)

    def test_generated_artifacts_are_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"), audit.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
