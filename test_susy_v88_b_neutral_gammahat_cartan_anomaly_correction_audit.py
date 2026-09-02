import copy
import json
import unittest

import susy_v88_b_neutral_gammahat_cartan_anomaly_correction_audit as audit


class TestV88BNeutralGammahatCartanAnomalyCorrectionAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()

    def test_report_validates_and_core_is_canonical(self):
        audit.validate_report(self.report)
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))

    def test_parent_cores_are_exactly_pinned(self):
        self.assertEqual(self.report["input_core_hashes"], {
            "V70_route": audit.EXPECTED_CORES["v70"],
            "V84_route": audit.EXPECTED_CORES["v84"],
            "V85_route": audit.EXPECTED_CORES["v85"],
            "V86_route": audit.EXPECTED_CORES["v86"],
            "V87_route": audit.EXPECTED_CORES["v87"],
            "V87_master": audit.EXPECTED_CORES["v87_master"],
        })

    def test_discrete_flavor_centralizer_is_sp2_times_sp1(self):
        row = self.report["flavor_centralizer_audit"]["H_AC"]
        self.assertEqual(row["signs"], [-1, 1, -1, -1, 1, -1])
        self.assertEqual(row["quaternionic_minus_eigenspace_dimension"], 2)
        self.assertEqual(row["quaternionic_plus_eigenspace_dimension"], 1)
        self.assertEqual(row["centralizer_in_Sp3"], "Sp(2)_AC x Sp(1)_B")
        self.assertEqual(row["centralizer_dimension"], 13)
        self.assertFalse(row["full_Sp3_preserved"])

    def test_signed_continuous_cartan_is_exact(self):
        row = self.report["flavor_centralizer_audit"]["continuous_Cartan"]
        self.assertEqual(row["T_fundamental_charges"], [2, 0, 2, -2, 0, -2])
        self.assertTrue(row["exp_i_pi_T_over_2_equals_H_AC"])
        self.assertEqual(row["centralizer_in_Sp3"], "U(2)_AC x Sp(1)_B")
        self.assertEqual(row["centralizer_dimension"], 7)

    def test_signed_cartan_traces(self):
        traces = self.report["flavor_centralizer_audit"]["continuous_Cartan"]["traces"]
        self.assertEqual(traces, {"TrT": 0, "TrT2": 16, "TrT3": 0, "TrT4": 64})

    def test_unsigned_continuous_u1_is_rejected(self):
        row = self.report["flavor_centralizer_audit"]["literal_unsigned_external_U1"]
        self.assertEqual(row["symplectic_pair_charge_sums"], [4, 0, 4])
        self.assertFalse(row["lies_in_sp3_lie_algebra"])
        self.assertFalse(row["commutes_with_full_Sp3_fundamental"])
        self.assertFalse(row["valid_continuous_parent_of_the_discrete_assignment"])

    def test_kernel_is_krot_kspin_and_keeps_spin11_faithful(self):
        cover = self.report["B_neutral_Gammahat_lift"]["cover"]
        self.assertEqual(cover["K_F_generators"]["krot"], [1, 1, 1, 1, 1, 0])
        self.assertEqual(cover["K_F_generators"]["kspin"], [0, 1, 0, 0, 0, 1])
        self.assertFalse(cover["contains_pure_Spin11_center"])
        self.assertTrue(cover["Spin11_remains_faithful"])

    def test_selected_lift_class_is_zero_zero_zero_zero(self):
        space = self.report["B_neutral_Gammahat_lift"]["square_space_group"]
        self.assertEqual(space["selected_lift_class_u_v_r_s"], [0, 0, 0, 0])
        self.assertEqual(space["U"], {"Spin11": "what", "H3": "H_AC", "C4F": "j"})
        self.assertEqual(space["V"], space["U"])

    def test_every_space_group_defect_lies_in_kernel(self):
        space = self.report["B_neutral_Gammahat_lift"]["square_space_group"]
        self.assertEqual(space["relation_defects_mod_center_bits"], {
            "A4": [1, 1, 1, 1, 1, 0],
            "UVUinvVinv": [0, 0, 0, 0, 0, 0],
            "AUAinvVinv": [0, 0, 0, 0, 0, 0],
            "AVAinvU": [0, 1, 0, 0, 0, 1],
        })
        self.assertTrue(space["every_relation_defect_in_K_F"])
        self.assertTrue(space["full_algebraic_cocycle_for_selected_smooth_bulk_lift"])

    def test_all_four_fixed_stratum_cover_powers_are_bound(self):
        rows = self.report["B_neutral_Gammahat_lift"]["fixed_strata"]
        self.assertEqual([row["point"] for row in rows], [
            "z00=0", "z11=(1+i)/2", "z10=1/2", "z01=i/2",
        ])
        self.assertEqual([row["cover_power"] for row in rows], [
            "Atilde^4=krot",
            "(Utilde*Atilde)^4=krot",
            "(Utilde*Atilde^2)^2=krot*kspin",
            "(Vtilde*Atilde^2)^2=krot*kspin",
        ])
        self.assertTrue(all(row["combined_copy_factor"] == [1, 1, 1] for row in rows))

    def test_three_hyper_translation_compensations_are_identity(self):
        rows = self.report["B_neutral_Gammahat_lift"]["projector_reconstruction"]["rows"]
        self.assertEqual([row["hyper"] for row in rows], ["A", "B", "C"])
        self.assertEqual([row["qF"] for row in rows], [2, 0, 2])
        self.assertEqual([row["combined_translation_factor"] for row in rows], [1, 1, 1])

    def test_every_v70_projector_is_restored(self):
        projectors = self.report["B_neutral_Gammahat_lift"]["projector_reconstruction"]
        self.assertEqual(projectors["n_hypers"], 3)
        self.assertEqual(projectors["n_strata"], 4)
        self.assertTrue(projectors["all_V70_A_B_C_projectors_restored"])
        self.assertTrue(all(row["reconstructed"] == row["V70"] for row in projectors["rows"]))

    def test_b_projector_and_triplet_boundary(self):
        projectors = self.report["B_neutral_Gammahat_lift"]["projector_reconstruction"]
        self.assertTrue(projectors["B_m0_singlet_and_doublet_restored"])
        self.assertTrue(projectors["no_color_triplet_zero_modes_reintroduced"])

    def test_lift_is_scoped_to_smooth_charged_hypers(self):
        boundary = self.report["B_neutral_Gammahat_lift"]["scope_boundary"]
        self.assertTrue(boundary["smooth_charged_hyper_Gammahat_lift_constructed"])
        for key, value in boundary.items():
            if key != "smooth_charged_hyper_Gammahat_lift_constructed":
                self.assertFalse(value)

    def test_relative_crepant_resolution_centers_and_discrepancies(self):
        row = self.report["resolved_bisection_over_S"]["relative_model"]
        self.assertEqual(row["P_plus_on_S"], "2*t^2*(r0^4-r1^4)")
        self.assertEqual(row["P_minus_on_S"], "2*t^2*(r0^4-2*r1^4)")
        self.assertTrue(row["P_plus_P_minus_no_common_root"])
        self.assertTrue(row["product_has_eight_simple_roots"])
        self.assertEqual(row["singular_curves"], ["C_+=(s,W,U-V)", "C_-=(s,W,U+V)"])
        self.assertTrue(row["curves_disjoint_in_projective_UV_fiber"])
        self.assertEqual(row["hypersurface_multiplicity_along_each_curve"], 2)
        self.assertEqual(row["residual_multiplicity"], 1)
        self.assertTrue(row["all_blowups_projective"])
        self.assertEqual([entry["discrepancy"] for entry in row["discrepancy_ledger"]], [0, 0, 0])
        self.assertTrue(row["relative_resolution_crepant"])

    def test_resolution_jacobian_groebner_certificate(self):
        certificate = self.report["resolved_bisection_over_S"]["Jacobian_chart_certificate"]
        rows = {row["chart"]: row for row in certificate["rows"]}
        self.assertEqual(rows["B1_r"]["Jacobian_Groebner_basis"], ["w", "a", "r"])
        self.assertFalse(rows["B1_r"]["smooth"])
        for name in ("B1_s", "B1_w", "B2_a", "B2_w"):
            self.assertEqual(rows[name]["Jacobian_Groebner_basis"], ["1"])
            self.assertTrue(rows[name]["smooth"])
        self.assertTrue(certificate["second_blowup_charts_smooth"])
        self.assertTrue(certificate["all_eight_simple_root_neighborhoods_resolved"])
        self.assertTrue(certificate["nonbranch_unit_locus_check"]["smooth_after_second_blowup"])

    def test_bisection_degree_and_spin11_center_coset(self):
        geometry = self.report["resolved_bisection_over_S"]
        fiber = geometry["fiber_and_bisection_data"]
        self.assertEqual(fiber["V87_period"], 2)
        self.assertEqual(fiber["V87_index"], 2)
        self.assertTrue(fiber["V87_U_equals_zero_divisor_is_irreducible_bisection"])
        self.assertEqual(fiber["affine_D6_marks"], [1, 1, 2, 2, 2, 1, 1])
        self.assertEqual(fiber["affine_D6_edges_by_node_index"], [[0, 2], [1, 2], [2, 3], [3, 4], [4, 5], [4, 6]])
        self.assertEqual(fiber["bisection_intersection_vector"], [0, 0, 0, 1, 0, 0, 0])
        self.assertEqual(fiber["bisection_degree_from_marks"], 2)
        self.assertEqual(fiber["component_rows"], audit.affine_d6_component_rows())
        self.assertTrue(fiber["Q_avoids_C_plus_and_C_minus"])
        self.assertEqual(fiber["F_s_at_Q"], "-L, a unit")
        self.assertTrue(fiber["second_blowup_is_isomorphism_near_Q"])
        center = geometry["Spin11_center_coset"]
        self.assertEqual(center["B5_inverse_Cartan_column_node3_V88"], ["1", "2", "3", "3", "3/2"])
        self.assertEqual(center["node3_minus_node1"], ["0", "1", "2", "2", "1"])
        self.assertTrue(center["node3_column_nonintegral"])
        self.assertTrue(center["twice_node3_column_integral"])
        self.assertTrue(center["same_nontrivial_Spin11_center_coset"])
        self.assertEqual(center["center_extension_class"], "j^2=z")
        self.assertFalse(center["literal_global_order4_automorphism_inferred_from_center_class"])

    def test_relative_resolution_is_not_promoted_to_compact_global_geometry(self):
        row = self.report["resolved_bisection_over_S"]["scope_boundary"]
        self.assertTrue(row["relative_resolution_over_S_constructed"])
        self.assertTrue(row["ordinary_smoothness_in_all_simple_root_charts"])
        self.assertFalse(row["compact_total_space_smooth_away_from_S"])
        self.assertFalse(row["global_Cox_irrelevant_ideal_saturation_checked"])
        self.assertFalse(row["literal_global_order4_automorphism_constructed"])
        self.assertFalse(row["diagonal_Gammahat_bundle_on_resolved_compact_space"])
        self.assertFalse(row["compact_resolved_bisection_complete"])

    def test_discrete_v87_anomaly_screen_is_retained(self):
        shadow = self.report["anomaly_scope_correction"]["V87_discrete_zero_mode_shadow"]
        self.assertFalse(any(shadow["mod4_tensor"].values()))
        self.assertEqual(shadow["unit_SU2_instanton_phase"], "+1")
        self.assertTrue(shadow["retained_as_necessary_low_energy_screen"])
        self.assertFalse(shadow["is_full_fixed_wall_Dai_Freed_character"])

    def test_tensor_over_four_continuous_gs_claim_is_retracted(self):
        row = self.report["anomaly_scope_correction"]["V87_tensor_divided_by_four"]
        self.assertTrue(row["integer_divisibility_is_true"])
        self.assertFalse(row["defines_external_continuous_U1_anomaly_polynomial"])
        self.assertFalse(row["proves_I6_equals_FF_times_X4_factorization"])
        self.assertFalse(row["defines_quantized_GS_or_WCS_coefficients"])

    def test_one_minimal_integer_lift_is_corrected_but_not_canonical(self):
        row = self.report["anomaly_scope_correction"]["one_minimal_integer_lift_of_four_dimensional_discrete_table"]
        self.assertEqual(row["changed_continuous_charge"], {
            "field": "A0", "from_discrete_representative": 2, "to_signed_Cartan_charge": -2,
        })
        self.assertEqual(row["integer_tensor"], {
            "A3": 12, "A2": 16, "FY6_squared": 432, "FX_squared": 672,
            "TrF": 60, "TrF_cubed": 96, "F_squared_Y6": 0,
            "F_squared_X": 0, "FY6X": 48,
        })
        self.assertFalse(row["is_canonical_continuous_U1_anomaly_tensor"])
        self.assertTrue(row["family_and_external_diagonal_charges_are_not_generated_by_U1_T_subset_Sp3"])
        self.assertTrue(row["still_not_complete_6D_anomaly_polynomial"])

    def test_ordinary_degree5_character_reduces_to_aw4(self):
        row = self.report["anomaly_scope_correction"]["ordinary_degree5_characteristic_reduction"]
        self.assertEqual(row["candidate"], "omega5=a*w4(V)")
        self.assertTrue(row["unique_nonzero_candidate_within_stated_SW_polynomial_subring"])
        self.assertEqual(row["omega5_witness_phase"], -1)
        self.assertFalse(row["displayed_witness_requires_k_aw4"])
        self.assertFalse(row["basis_coefficient_of_full_bordism_character_determined"])
        self.assertFalse(row["full_Gammahat_characteristic_ring_computed"])
        self.assertFalse(row["full_spin_bordism_group_computed"])

    def test_pure_c4_shadow_passes_but_torsion_wcs_is_unfixed(self):
        anomaly = self.report["anomaly_scope_correction"]
        self.assertTrue(anomaly["pure_C4_Dai_Freed_shadow"]["both_conditions_pass"])
        row = anomaly["torsion_WCS_reduction"]
        self.assertEqual(row["candidate_label_space_for_t2_component"], "Lambda/2Lambda=(Z2)^2")
        self.assertEqual(row["number_of_candidate_labels_for_t2_component"], 4)
        self.assertFalse(row["fixed_by_de_Rham_I8"])
        self.assertFalse(row["fixed_by_pure_C4_tests"])
        self.assertFalse(row["full_degree4_torsion_cohomology_of_BGF_computed"])
        self.assertFalse(row["WCS_admissibility_conditions_checked"])
        self.assertFalse(row["number_of_admissible_WCS_choices_determined"])
        self.assertFalse(row["secondary_term_constructed"])

    def test_full_signed_6d_anomaly_and_wcs_remain_open(self):
        row = self.report["anomaly_scope_correction"]["correct_continuous_parent_data"]
        self.assertEqual(row["Cartan_charges_on_6_of_Sp3"], [2, 0, 2, -2, 0, -2])
        self.assertFalse(row["complete_6D_bulk_anomaly_polynomial_computed"])
        self.assertFalse(row["fixed_stratum_log_twist_terms_computed"])
        self.assertFalse(row["localized_fermion_and_normal_bundle_contributions_computed"])
        self.assertFalse(row["differential_GS_WCS_trivialization_constructed"])

    def test_quantum_parent_is_not_promoted(self):
        row = self.report["anomaly_scope_correction"]["quantum_decision"]
        self.assertFalse(row["V86_k2_required_by_displayed_B_neutral_zero_modes"])
        self.assertFalse(row["UV_k2_coefficient_determined"])
        self.assertFalse(row["ordinary_aw4_character_trivialized"])
        self.assertFalse(row["full_stratified_Dai_Freed_character_vanishes"])
        self.assertFalse(row["quantum_parent_accepted"])

    def test_v85_action_lineage_retraction_and_live_operator_boundary(self):
        row = self.report["operator_closure_boundary"]
        self.assertEqual(row["rank_one_light_Higgs_pair_retained"], ["H_uA", "H_dC"])
        self.assertEqual(row["V84_Cbar45C_row"], "RETRACTED_MIXED_ACTION_ROW")
        self.assertFalse(row["Cbar_Cbar_45_present_in_selected_V70_action"])
        self.assertFalse(row["Cbar45C_is_current_obligation"])
        self.assertEqual(row["odd_B0_driver_terms_allowed"], ["S_B*B0"])
        self.assertFalse(row["even_B0_potential_symmetry_enforced"])
        self.assertFalse(row["all_order_operator_closure_proved"])

    def test_c8_selector_scopes_b0_parity_to_neutral_coefficients(self):
        row = self.report["signed_C8_parent_selector_scout"]
        self.assertEqual(row["parent_group"]["finite_group"], "G8=(Spin(11) x C8)/<(z,k^4)>")
        self.assertEqual(row["parent_group"]["prequotient_C8_stabilizer_generator_after_B0_q4_VEV"], "j=k^2")
        self.assertEqual(row["parent_group"]["j_squared"], "k^4=z")
        self.assertEqual(row["parent_group"]["B0_VEV_nongauge_component_group"], "C2")
        self.assertFalse(row["parent_group"]["faithful_global_C4_selector_on_gauge_invariant_operators"])
        parity = row["neutral_coefficient_B0_driver_parity"]
        self.assertTrue(parity["all_odd_powers_forbidden_with_neutral_coefficients"])
        self.assertTrue(parity["all_even_powers_allowed_with_neutral_coefficients"])
        self.assertTrue(parity["charge4_spurion_can_compensate_an_odd_B0_power"])
        self.assertFalse(parity["unconditional_all_order_selector_after_charged_spurions"])

    def test_c8_vectorlike_pair_cancels_displayed_mod8_residues(self):
        row = self.report["signed_C8_parent_selector_scout"]["ordinary_anomaly_screen"]
        self.assertEqual(row["raw_nonzero_residues"], ["A3", "A2", "TrF"])
        self.assertEqual(row["compensator"], "one localized gauge-vectorlike SU5 5_0 + 5bar_4")
        self.assertEqual(row["compensated_tensor"], {
            "A3": 64, "A2": 80, "FY6_squared": 2208, "FX_squared": 2208,
            "TrF": 312, "TrF_cubed": 7824, "F_squared_Y6": 96,
            "F_squared_X": 544, "FY6X": 192,
        })
        self.assertFalse(any(row["compensated_mod8"].values()))
        self.assertTrue(row["all_displayed_mod8_residues_zero"])
        self.assertFalse(row["is_full_C8_Dai_Freed_character"])

    def test_c8_operator_rows_keep_yukawas_and_forbid_direct_mu(self):
        audit_rows = self.report["signed_C8_parent_selector_scout"]["operator_audit"]
        rows = {row["operator"]: row for row in audit_rows["rows"]}
        for operator in ("16 16 H_uA", "10 5bar H_dC", "N N X", "S_B B0^2", "g B0 H_uB H_dSigma"):
            self.assertTrue(rows[operator]["allowed"])
        for operator in ("S_B B0", "direct H_uA H_dC", "16 16 5_0", "16 16 5bar_4"):
            self.assertFalse(rows[operator]["allowed"])
        self.assertTrue(audit_rows["direct_light_mu_forbidden"])
        self.assertTrue(audit_rows["charge4_SUSY_breaking_spurion_GM_route_allowed"])
        self.assertTrue(rows["spurion4 S_B B0"]["allowed"])
        self.assertTrue(rows["X H_uA 5bar_4"]["allowed"])
        self.assertTrue(rows["Xbar 5_0 H_dC"]["allowed"])
        self.assertFalse(audit_rows["R_assignment_tradeoff"]["simultaneous_no_mixing_decay_and_proton_safety_constructed"])
        self.assertFalse(audit_rows["GM_spurion_sector_constructed"])

    def test_c8_parent_remains_a_scout_not_a_completed_action(self):
        row = self.report["signed_C8_parent_selector_scout"]
        self.assertFalse(row["parent_group"]["full_order8_generator_Gammahat_lift_constructed"])
        self.assertTrue(row["pure_C8_Dai_Freed_shadow"]["both_conditions_pass"])
        self.assertFalse(row["pure_C8_Dai_Freed_shadow"]["mixed_diagonal_and_fixed_wall_data_determined"])
        self.assertFalse(row["scope_boundary"]["GM_SUSY_breaking_spurion_sector"])
        self.assertTrue(row["scope_boundary"]["compensator_mass_operator_charge_and_R_allowed"])
        self.assertFalse(row["scope_boundary"]["localized_compensator_isotropy_and_nonzero_mass_coupling_constructed"])
        self.assertFalse(row["scope_boundary"]["simultaneous_compensator_decay_exact_Higgs_identity_and_proton_safety"])
        self.assertFalse(row["scope_boundary"]["accepted_same_action_parent"])

    def test_terminal_decision_records_gain_and_boundaries(self):
        decision = self.report["terminal_decision"]
        self.assertTrue(decision["reduced_flavor_group_exact"])
        self.assertTrue(decision["selected_smooth_bulk_Gammahat_cocycle_constructed"])
        self.assertTrue(decision["all_V70_A_B_C_projectors_restored"])
        self.assertTrue(decision["relative_projective_crepant_resolution_over_S"])
        self.assertTrue(decision["bisection_center_coset_realizes_j_squared_equals_z"])
        self.assertTrue(decision["ordinary_aw4_displayed_witness_requires_no_term"])
        self.assertTrue(decision["C8_neutral_coefficient_B0_parity_screen_passes"])
        self.assertTrue(decision["C8_compensated_displayed_mod8_screen_zero"])
        self.assertFalse(decision["pure_Spin11_center_in_kernel"])
        self.assertFalse(decision["C8_full_order8_Gammahat_lift_constructed"])
        self.assertFalse(decision["complete_signed_6D_anomaly_polynomial"])
        self.assertFalse(decision["accepted_full_parent_action_exists"])
        self.assertEqual(decision["closed_gates"], [])
        self.assertFalse(decision["theory_complete"])

    def test_all_susy_gates_remain_open(self):
        self.assertEqual(set(self.report["gate_ledger"]), {f"G{i}" for i in range(1, 9)})
        self.assertTrue(all(value.startswith("OPEN:") for value in self.report["gate_ledger"].values()))

    def test_source_manifest_is_primary_and_canonical(self):
        manifest = self.report["source_manifest"]
        self.assertEqual(manifest["kind"], "primary_sources_only")
        self.assertEqual(manifest["count"], 3)
        self.assertEqual(manifest["catalog_sha256"], audit.canonical_sha(self.report["primary_sources"]))

    def test_validator_rejects_false_promotions_and_mutations(self):
        mutations = [
            lambda x: x["flavor_centralizer_audit"]["literal_unsigned_external_U1"].__setitem__("valid_continuous_parent_of_the_discrete_assignment", True),
            lambda x: x["B_neutral_Gammahat_lift"]["cover"].__setitem__("contains_pure_Spin11_center", True),
            lambda x: x["B_neutral_Gammahat_lift"]["square_space_group"].__setitem__("selected_lift_class_u_v_r_s", [1, 0, 0, 0]),
            lambda x: x["B_neutral_Gammahat_lift"]["projector_reconstruction"].__setitem__("all_V70_A_B_C_projectors_restored", False),
            lambda x: x["B_neutral_Gammahat_lift"]["scope_boundary"].__setitem__("full_physical_HGamma_orbibundle_constructed", True),
            lambda x: x["resolved_bisection_over_S"]["Jacobian_chart_certificate"]["rows"][0].__setitem__("Jacobian_Groebner_basis", ["s"]),
            lambda x: x["resolved_bisection_over_S"]["relative_model"].__setitem__("branch_assumption", "P has a double root"),
            lambda x: x["resolved_bisection_over_S"]["relative_model"].__setitem__("globality", "formal only"),
            lambda x: x["resolved_bisection_over_S"]["relative_model"].__setitem__("relative_resolution_crepant", False),
            lambda x: x["resolved_bisection_over_S"]["relative_model"].__setitem__("discrepancy_first_blowup", "3-1-2=1"),
            lambda x: x["resolved_bisection_over_S"]["Jacobian_chart_certificate"].__setitem__("second_blowup_charts_smooth", False),
            lambda x: x["resolved_bisection_over_S"]["Jacobian_chart_certificate"].__setitem__("all_eight_simple_root_neighborhoods_resolved", False),
            lambda x: x["resolved_bisection_over_S"]["fiber_and_bisection_data"].__setitem__("bisection_intersection_vector", [0, 0, 1, 0, 0, 0, 0]),
            lambda x: x["resolved_bisection_over_S"]["fiber_and_bisection_data"]["component_rows"][0].__setitem__("local_equation", "reducible union"),
            lambda x: x["resolved_bisection_over_S"]["fiber_and_bisection_data"].__setitem__("scope", "all fibers"),
            lambda x: x["resolved_bisection_over_S"]["fiber_and_bisection_data"].__setitem__("bisection_point", "Q=[1:0:0]"),
            lambda x: x["resolved_bisection_over_S"]["fiber_and_bisection_data"].__setitem__("intersected_node", "alpha2"),
            lambda x: x["resolved_bisection_over_S"]["local_normal_form"].__setitem__("coordinate_scope", "global chart"),
            lambda x: x["resolved_bisection_over_S"]["Spin11_center_coset"].__setitem__("center_extension_class", "j^2=1"),
            lambda x: x["resolved_bisection_over_S"]["Spin11_center_coset"].__setitem__("difference_integral", False),
            lambda x: x["resolved_bisection_over_S"]["scope_boundary"].__setitem__("compact_resolved_bisection_complete", True),
            lambda x: x["anomaly_scope_correction"]["V87_discrete_zero_mode_shadow"]["mod4_tensor"].__setitem__("A2", 2),
            lambda x: x["anomaly_scope_correction"]["V87_tensor_divided_by_four"].__setitem__("proves_I6_equals_FF_times_X4_factorization", True),
            lambda x: x["anomaly_scope_correction"]["one_minimal_integer_lift_of_four_dimensional_discrete_table"]["integer_tensor"].__setitem__("TrF", 64),
            lambda x: x["anomaly_scope_correction"]["one_minimal_integer_lift_of_four_dimensional_discrete_table"].__setitem__("is_canonical_continuous_U1_anomaly_tensor", True),
            lambda x: x["anomaly_scope_correction"]["torsion_WCS_reduction"].__setitem__("fixed_by_pure_C4_tests", True),
            lambda x: x["anomaly_scope_correction"]["torsion_WCS_reduction"].__setitem__("WCS_admissibility_conditions_checked", True),
            lambda x: x["anomaly_scope_correction"]["correct_continuous_parent_data"].__setitem__("complete_6D_bulk_anomaly_polynomial_computed", True),
            lambda x: x["operator_closure_boundary"].__setitem__("Cbar45C_is_current_obligation", True),
            lambda x: x["operator_closure_boundary"].__setitem__("all_order_operator_closure_proved", True),
            lambda x: x["signed_C8_parent_selector_scout"]["ordinary_anomaly_screen"]["compensated_mod8"].__setitem__("A3", 4),
            lambda x: x["signed_C8_parent_selector_scout"]["neutral_coefficient_B0_driver_parity"].__setitem__("unconditional_all_order_selector_after_charged_spurions", True),
            lambda x: x["signed_C8_parent_selector_scout"]["operator_audit"]["R_assignment_tradeoff"].__setitem__("simultaneous_no_mixing_decay_and_proton_safety_constructed", True),
            lambda x: x["signed_C8_parent_selector_scout"]["scope_boundary"].__setitem__("localized_compensator_isotropy_and_nonzero_mass_coupling_constructed", True),
            lambda x: x["signed_C8_parent_selector_scout"]["parent_group"].__setitem__("full_order8_generator_Gammahat_lift_constructed", True),
            lambda x: x["terminal_decision"].__setitem__("accepted_full_parent_action_exists", True),
            lambda x: x["terminal_decision"].__setitem__("bisection_center_coset_realizes_j_squared_equals_z", False),
            lambda x: x["terminal_decision"].__setitem__("theory_complete", True),
            lambda x: x["gate_ledger"].__setitem__("G1", "CLOSED"),
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
