from __future__ import annotations

import json

import susy_v71_spin11_normal_bundle_equivariant_gs_audit as audit


def report():
    return audit.build_report()


def test_v71_integrity_and_v70_lineage():
    value = report()
    audit.validate(value)
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["lineage"]["bound_V70_core"] == audit.EXPECTED_V70_CORE


def test_spin_half_equivariant_polynomials_are_exact():
    index = report()["spin_half_equivariant_index"]
    assert index["phase_signs_m0123"] == [-1, 1, 1, -1]
    assert index["all_compact_forms_exact"]
    assert [row["I6_x3"] for row in index["rows"]] == ["-11/192", "11/192", "11/192", "-11/192"]
    assert [row["I6_x_p1T4"] for row in index["rows"]] == ["-1/192", "1/192", "1/192", "-1/192"]


def test_gravity_tensor_virtual_bundle_and_standard_form_cancellation():
    value = report()["gravity_tensor_equivariant_index"]
    assert value["fermionic_virtual_bundle"] == "-(T_C M6-1)+1 = -(T_C M6-2)"
    assert value["I6_gravity_plus_tensor_fermions"]["common_denominator_192"] == ["42", "-18"]
    assert "cancel pointwise" in value["self_dual_forms"]["standard_lift"]
    assert "NOT_ASSUMED" in value["self_dual_forms"]["extra_tensor_lattice_twist"]


def test_both_charged_branches_give_plus_four_hyper_units():
    value = report()["charged_bulk_normal_gravity_ledger"]
    assert value["adjoint"]["gaugino_opposite_chirality_units"] == 5
    assert value["full_11_identity"]["values_m0123"] == [-1, 1, 1, -1]
    assert value["integer_m301_branch"]["three_11_sum"] == -1
    assert value["integer_m301_branch"]["with_gaugino"] == 4
    assert value["flavor_Wilson_branch"]["with_gaugino"] == 4
    assert value["z00_equals_z11"]


def test_neutral_polynomial_cannot_vanish_but_factorizes_only_at_delta_minus10():
    value = report()["neutral_266_phase_classification"]
    assert value["cannot_vanish"]["x3_requires_Delta"] == "-86/11"
    assert value["cannot_vanish"]["xp_requires_Delta"] == "14"
    assert value["cannot_vanish"]["requirements_incompatible"]
    factor = value["bulk_gravitational_trace_factorization"]
    assert factor["unique_Delta"] == -10
    assert factor["coefficient_pair_over_192"] == [-24, -24]
    assert factor["factored_polynomial"].startswith("-(1/8)")
    assert factor["necessary_not_sufficient"]
    assert value["general_localized_extension"]["full_directional_factorization_equation"] == "100+10 Delta_f+32 Q3_f+8 Q1_f=0"


def test_ten_neutral_zero_mode_lower_bound_and_sharp_witness():
    value = report()["neutral_266_phase_classification"]
    theorem = value["two_corner_zero_mode_theorem"]
    witness = value["explicit_266_dimensional_witness"]
    assert theorem["minimum_neutral_chiral_zero_modes"] == 10
    assert witness["dimension"] == 266
    assert witness["phase_counts_at_each_corner"] == {"m0": 74, "m1": 64, "m2": 64, "m3": 64}
    assert witness["Delta_at_each_corner"] == -10
    assert witness["neutral_chiral_zero_modes"] == 10
    assert witness["target_isometry_constructed"]
    assert not witness["global_H_bundle_constructed"]
    target = value["symmetric_quaternionic_Kahler_realization"]
    assert target["target"] == "Sp(266,1)/(Sp(266)xSp(1))"
    assert target["real_dimension"] == 1064
    assert "A_F^4=-I" in target["underlying_half_angle_flavor_lift"]
    assert target["local_space_group_and_bundle_lift"].startswith("PASS_EXACT")
    no_go = value["conventional_local_fermion_only_no_go_for_factored_residue"]
    assert no_go["required_charge_moments"] == ["sum q=-3", "sum q^3=+3/4"]
    assert not no_go["solution_exists"]
    assert "GS inflow" in no_go["conclusion"]


def test_explicit_four_orbit_matrices_obey_the_space_group():
    value = report()["neutral_four_orbit_matrix_witness"]
    assert value["all_checks_pass"]
    assert all(value["checks"].values())


def test_mixed_normal_gauge_vector_and_bulk_direction_mismatch_exactly():
    value = report()["mixed_normal_gauge_obstruction"]
    assert value["von_Gersdorff_factor"]["kappa_eta_1_i_minus1_minusi"] == ["1/4", "-1/4", "-1/4", "1/4"]
    assert value["von_Gersdorff_factor"]["fixed_density_c1_eta_1_i_minus1_minusi"] == ["1/8", "-1/8", "-1/8", "1/8"]
    assert value["weighted_adjoint_trace_before_chirality"] == ["1/4", "-40"]
    assert value["gaugino_opposite_chirality"] == ["-1/4", "40"]
    assert value["three_full_11_hypers"]["all_zero"]
    assert value["standard_bulk_GS"]["restriction_to_U5"] == ["1", "40"]
    assert value["standard_bulk_GS"]["determinant_with_F70_vector"] == "-50"
    assert not value["standard_bulk_GS"]["ordinary_bulk_GS_can_cancel_F70_vector"]


def test_complete_16_cannot_fix_orthogonal_component():
    value = report()["mixed_normal_gauge_obstruction"]["complete_16_check"]
    assert value["trace_direction"] == ["2", "80"]
    assert value["equals_two_times_bulk_direction"]


def test_former_minimal_pair_repair_is_retracted_by_common_normalization():
    value = report()["mixed_normal_gauge_obstruction"]["minimal_singlet_pair_repair"]
    assert value["required_fermion_normal_charge_sum"] == "-1"
    assert value["mixed_shift"] == ["0", "-100"]
    assert value["repaired_vector"] == ["-1/4", "-60"]
    assert value["aligned_target_vector"] == ["-1/4", "-10"]
    assert value["required_net_local_shift_without_the_pair"] == ["0", "-50"]
    assert not value["aligns_with_bulk_direction"]
    assert value["symmetric_pair_additional_local_I6"] == {
        "x3": "-1/24",
        "x_p1T4": "1/24",
        "formula": "-x^3/24+x p1(T4)/24",
    }
    assert "overshoots" in value["scope"]


def test_U1L_squared_X_and_minimal_four_fermion_module_are_exact():
    mixed = report()["mixed_normal_gauge_obstruction"]
    x2 = mixed["U1L_squared_X_ledger"]
    assert x2["spin_half_x2_coefficients_m0123"] == ["-7/64", "-5/64", "5/64", "7/64"]
    assert x2["gaugino"] == "15/8"
    assert x2["one_11_m0123"] == ["-15/8", "15/8", "15/8", "-15/8"]
    assert x2["integer_m301_total_with_gaugino"] == "0"
    assert x2["flavor_Wilson_total_with_gaugino"] == "0"
    assert x2["both_V70_branches_zero"]
    module = mixed["minimal_R_compatible_four_fermion_module"]
    assert module["Q1"] == "0"
    assert module["Q3"] == "0"
    assert module["U1L_squared_X"] == "0"
    assert module["U1L_X_squared"] == "-100"
    assert module["standalone_mixed_repair"].startswith("FAIL")
    assert module["restores_bulk_Delta_condition"] == "Delta_f=-10 because Q1=Q3=0"
    theorem = module["supersymmetric_mass_and_VEV_theorem"]
    assert "qpsi sum 0" in theorem["bare_mass"]
    assert "W=S(X Xbar-v^2)" in theorem["allowed_driver"]
    assert "hypercharge +/-2" in theorem["z11_boundary"]
    assert "qL(psi_16)=0" in module["localized_family_contract"]
    corrected = mixed["corrected_spinorial_U5_preimage_modules"]
    assert corrected["both_mixed_vectors_align"]
    assert corrected["required_local_shift_each_Z4"] == ["0", "-50"]
    z00 = corrected["z00_complete_ledger"]
    z11 = corrected["z11_complete_ledger"]
    assert z00["field_count"] == 10
    assert z11["field_count"] == 8
    assert z00["U1L_X_squared"] == z11["U1L_X_squared"] == "-50"
    assert z00["all_spectator_anomalies_zero"]
    assert z11["all_spectator_anomalies_zero"]
    assert "Y=+/-1" in corrected["z11_hypercharge"]
    assert "vector-form U(5)" in corrected["global_form_boundary"]
    assert "Giudice-Masiero" in corrected["mass_boundary"]
    assert "z00 each charged scalar has continuous normal charge +1" in corrected["mass_boundary"]
    assert corrected["V70_z00_R_charge_binding"]["X_Xbar"] == 0
    assert corrected["V70_z00_R_charge_binding"]["S0"] == 2


def test_repair_is_required_independently_at_both_corners():
    locality = report()["mixed_normal_gauge_obstruction"]["locality"]
    assert locality["one_corner_cannot_cancel_the_other"]
    assert "existing X/Xbar" in locality["z00"]
    assert "eight new" in locality["z11"]


def test_smooth_wucs_does_not_supply_orbifold_equivariant_completion():
    value = report()["equivariant_GS_WuCS_boundary"]
    assert value["smooth_parent_imported_from_V70"]["a_characteristic"]
    assert value["smooth_parent_imported_from_V70"]["global_form"] == "Spin(11)"
    assert value["smooth_parent_imported_from_V70"]["reduced_Omega7_spin_BSpin11"] == "0"
    assert value["SO11_fallback_fails"]["verdict"] == "FAIL"
    assert not value["SO11_fallback_fails"]["b_is_even"]
    assert value["ordinary_spin_orbifold_obstruction"]["L_theta_fourth"] == "-1"
    assert "diagonal Z2" in value["preserved_supersymmetry_structure"]["combined_fourth"]
    assert not value["equivariant_GS_descent_constructed"]
    assert not value["Dai_Freed_phases_computed"]
    torsion = value["naive_orbifold_torsion_divisibility"]
    assert torsion["all_loci_fail_ordinary_divisibility"]
    rows = {row["locus"]: row for row in torsion["rows"]}
    assert rows["z00"]["two_Y_mod_order"] == [3, 2]
    assert rows["z11"]["two_Y_mod_order"] == [3, 2]
    assert rows["z10_z01"]["two_Y_mod_order"] == [1, 1]
    assert rows["z00"]["doubling_image_each_coordinate"] == [0, 2]
    assert rows["z10_z01"]["doubling_image_each_coordinate"] == [0]
    assert all(not row["Y_exists_in_ordinary_integral_cohomology"] for row in rows.values())
    corrections = torsion["minimal_restriction_level_corrections_to_twice_Y"]
    assert "delta=(1,0)" in corrections["Z4"]
    assert "delta=(1,1)" in corrections["Z2"]
    assert "cannot" in corrections["SU2R_alone"]
    assert "do not define one global class" in torsion["local_relative_halves_and_gluing_obstruction"]["conclusion"]
    stueckelberg = value["continuous_Stueckelberg"]
    assert stueckelberg["bulk_GS_reduction"]["value"] == "0"
    assert not stueckelberg["four_dimensional_crosscheck"]["forced_mass_for_hypercharge"]
    assert not stueckelberg["four_dimensional_crosscheck"]["forced_mass_for_X"]
    assert "normal U1L" in stueckelberg["repair_design_rule"]


def test_F71_is_an_exact_local_witness_not_an_accepted_action():
    candidate = report()["F71_repair_candidate"]
    assert candidate["selected_for_next_frontier"]
    assert not candidate["accepted"]
    assert not candidate["same_action_complete"]
    assert candidate["supersedes"] == ["F70", "F70_ALT"]
    assert candidate["exact_required_variation_ledger"]["neutral_zero_mode_count"] == 10
    assert not candidate["exact_required_variation_ledger"]["continuous_hypercharge_or_X_Stueckelberg_from_flat_bulk_holonomy_forced"]
    selected = candidate["repair_options"]["selected_hybrid"]
    assert "eight-new-chiral" in selected["z11"]
    assert selected["z11_primed_hypercharge"] == "+/-1 for the charged singlets"
    assert not selected["mass_decay_cosmology_complete"]
    assert candidate["not_yet_passes"]


def test_fail_closed_decision_and_all_gates_open():
    value = report()
    assert value["acceptance"]["F70_unmodified"].startswith("REJECTED")
    assert value["acceptance"]["F71_microscopic_supergravity_action"] == "OPEN_NOT_CONSTRUCTED"
    assert value["acceptance"]["continuous_hypercharge_or_X_Stueckelberg_from_flat_holonomy"] == "PASS_NOT_FORCED"
    assert "NAIVE_FIXED_STRATUM_MMP_COCYCLE_FAIL_EXACT" in value["frontier_status_ledger"]
    assert "NEUTRAL_QK_SPACE_GROUP_LIFT_PASS_EXACT" in value["frontier_status_ledger"]
    assert not value["terminal_decision"]["F71_accepted"]
    assert not value["terminal_decision"]["theory_complete"]
    assert all(state == "OPEN" for state in value["gate_ledger"].values())


def test_generated_artifacts_are_required_and_match():
    value = report()
    assert audit.JSON_PATH.is_file()
    assert audit.MD_PATH.is_file()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
