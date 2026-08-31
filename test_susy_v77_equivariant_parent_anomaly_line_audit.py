import json

import pytest

import susy_v77_equivariant_parent_anomaly_line_audit as audit


def report():
    return audit.build_report()


def test_v70_v71_and_v76_lineage_is_canonical_and_bound():
    value = report()["lineage"]
    assert value["V70_route_core"] == audit.EXPECTED_CORES["v70_route"]
    assert value["V71_route_core"] == audit.EXPECTED_CORES["v71_route"]
    assert value["V76_route_core"] == audit.EXPECTED_CORES["v76_route"]
    assert value["V76_master_core"] == audit.EXPECTED_CORES["v76_master"]


def test_mutated_parent_with_old_core_is_rejected(tmp_path):
    parent = json.loads(audit.V76_ROUTE_PATH.read_text(encoding="utf-8"))
    parent["status"] += "__MUTATED"
    path = tmp_path / "mutated.json"
    path.write_text(json.dumps(parent), encoding="utf-8")
    with pytest.raises(RuntimeError, match="noncanonical parent core"):
        audit.load_bound(path, audit.EXPECTED_CORES["v76_route"])


def test_space_group_abelianization_is_z4_times_z2():
    value = report()["space_group_flat_character_audit"]
    assert value["abelianization"] == "Z4 x Z2"
    assert value["character_count"] == 8


def test_all_eight_character_rows_obey_the_abelianized_relations():
    rows = report()["space_group_flat_character_audit"]["characters"]
    assert len({row["id"] for row in rows}) == 8
    for row in rows:
        assert row["identity"] == "1"
        assert row["U"] == row["V"]
        assert row["translation_sign"] in (-1, 1)
        assert row["A"] in {"1", "i", "-1", "-i"}
        assert row["UA"] == row["z11_character"]
        assert row["A"] == row["z00_character"]
        assert row["UA2"] == row["z2_character"]


def test_translation_character_changes_only_relative_corner_sign_in_witness():
    rows = {
        row["id"]: row
        for row in report()["space_group_flat_character_audit"]["characters"]
    }
    same = rows["chi_m0_tp"]
    opposite = rows["chi_m0_tm"]
    assert same["identity"] == opposite["identity"] == "1"
    assert same["z00_character"] == opposite["z00_character"] == "1"
    assert same["z11_character"] == "1"
    assert opposite["z11_character"] == "-1"


def test_real_m2_twist_is_invisible_to_identity_and_order_two():
    rows = {
        row["id"]: row
        for row in report()["space_group_flat_character_audit"]["characters"]
    }
    positive = rows["chi_m0_tp"]
    negative = rows["chi_m2_tp"]
    assert positive["identity"] == negative["identity"] == "1"
    assert positive["z2_character"] == negative["z2_character"] == "1"
    assert positive["z00_character"] == "1"
    assert negative["z00_character"] == "-1"
    assert positive["real_character"] and negative["real_character"]


def test_relative_corner_profile_can_change_with_identity_and_actual_z2_fixed():
    rows = {
        row["id"]: row
        for row in report()["space_group_flat_character_audit"]["characters"]
    }
    same = rows["chi_m0_tp"]
    opposite = rows["chi_m1_tm"]
    assert same["identity"] == opposite["identity"] == "1"
    assert same["z2_character"] == opposite["z2_character"] == "1"
    assert (same["z00_character"], same["z11_character"]) == ("1", "1")
    assert (opposite["z00_character"], opposite["z11_character"]) == ("i", "-i")


def test_character_table_is_diagnostic_not_an_accepted_supergravity_completion():
    value = report()["space_group_flat_character_audit"]
    assert "not eight accepted" in value["scope"]


def test_v71_parent_component_blocks_are_imported_exactly():
    blocks = report()["V71_parent_index_inventory"]["blocks_over_192"]
    assert blocks["charged_gaugino_plus_three_11_hypers"] == [44, 4]
    assert blocks["gauge_fixed_gravitino_plus_tensorino"] == [42, -18]
    assert blocks["neutral_266_at_Delta_minus10"] == [-110, -10]


def test_standard_untwisted_parent_residue_is_reproduced():
    value = report()["V71_parent_index_inventory"]["standard_untwisted_lift"]
    assert value["sum_over_192"] == [-24, -24]
    assert value["reduced_coefficients"] == ["-1/8", "-1/8"]
    assert value["matches_V71_total_polynomial"]


def test_formal_character_probe_changes_the_residue_without_being_accepted():
    probes = report()["V71_parent_index_inventory"][
        "formal_character_sensitivity_probes"
    ]
    gravity = probes["gravity_tensor_order4_common_sign_flipped"]
    assert gravity["sum_over_192"] == [-108, 12]
    assert gravity["reduced_coefficients"] == ["-9/16", "1/16"]
    assert gravity["different_from_standard"]
    assert not probes["accepted_as_supersymmetric_lifts"]


def test_v76_equal_corner_theorem_is_not_retracted():
    scope = report()["V71_parent_index_inventory"]["V76_theorem_scope"]
    assert scope["odd_quarter_no_go_remains_exact_for_the_bound_equal_corner_parent_profile"]
    assert scope["a_future_different_profile_requires_complete_recomputation"]
    assert not scope["V76_retracted"]


def test_parent_action_scenarios_do_not_merge_unmodified_v70_with_f71():
    value = report()["parent_action_scenario_audit"]
    assert value["V70_selected_branch"] == "integer_m301_dynamical_reduction"
    assert not value["accepted_full_parent_action_exists"]
    assert value["all_later_routes_unaccepted"]
    f71 = value["V71_neutral_and_local_repair_status"]
    assert not f71["accepted"]
    assert not f71["same_action_complete"]


def test_inherited_v70_localized_fields_make_provisional_profile_unequal():
    value = report()["parent_action_scenario_audit"]
    shift = value["V71_provisional_lifts_on_inherited_V70_z00_fields_shift"]
    assert shift["fields"] == ["X_plus10", "Xbar_minus10", "S0"]
    assert shift["fermion_normal_charges"] == ["-1/2", "-1/2", "1/2"]
    assert shift["Q1"] == "-1/2"
    assert shift["Q3"] == "-1/8"
    assert shift["coefficients_over_192_nu3_nu_p1"] == [-4, 4]
    assert shift["U1L_X_squared"] == "-100"
    assert "V70 itself did not define" in shift["normal_lift_provenance"]
    hybrid = value["scenarios"][
        "V71_neutral_witness_without_F71_local_compensators"
    ]
    assert hybrid["z00_over_192"] == [-28, -20]
    assert hybrid["z11_over_192"] == [-24, -24]
    assert not hybrid["equal_corner_profile"]


def test_v70_and_complete_f71_mixed_normal_gauge_profiles_are_distinct():
    scenarios = report()["parent_action_scenario_audit"]["scenarios"]
    assert scenarios["unmodified_V70"]["provisional_mixed_normal_gauge_vectors"] == {
        "z00": ["-1/4", "-60"],
        "z11": ["-1/4", "40"],
    }
    complete = scenarios["complete_F71_local_perturbative_ledger"]
    assert complete["aligned_mixed_normal_gauge_vector_each_corner"] == ["-1/4", "-10"]
    assert complete["equal_corner_profile"]
    assert complete["V76_equal_corner_theorem_applies"]
    assert not complete["accepted_action"]


def test_fixed_point_profile_is_not_identifiable_from_smooth_data_alone():
    value = report()["fixed_point_identifiability_theorem"]
    assert value["identity_class_unchanged"]
    assert value["smooth_six_dimensional_I8_unchanged"]
    assert value["nonidentity_fixed_point_traces_can_change"]
    assert value["order4_equal_vs_opposite_profile_can_change"]


def test_v71_zero_mode_lower_bound_forces_unprimed_determinant_to_zero():
    value = report()["zero_mode_and_anomaly_line_audit"]
    assert value["minimum_neutral_chiral_zero_modes"] == 10
    assert "internal orbifold" in value["zero_mode_operator_scope"]
    assert value["ordinary_unprimed_internal_KK_determinant_at_zero_external_momentum"] == "0"
    assert not value["full_6D_determinant_identically_zero_on_every_external_background"]
    assert not value["ordinary_unprimed_determinant_is_nonzero_scalar"]


def test_scalar_determinant_target_is_refined_to_anomaly_line():
    value = report()["zero_mode_and_anomaly_line_audit"]
    assert "determinant/anomaly line" in value["correct_fermionic_object"]
    refinement = value["F76_target_refinement"]
    assert refinement["old_label"] == "F76_FULL_EQUIVARIANT_PARENT_DETERMINANT"
    assert refinement["new_label"] == "F77_EQUIVARIANT_ANOMALY_LINE_WUCS_TRIVIALIZATION"
    assert not refinement["same_action_completion_constructed"]


def test_self_dual_sector_is_not_misrepresented_as_an_ordinary_determinant():
    value = report()["zero_mode_and_anomaly_line_audit"]
    assert "quadratic-refinement" in value["self_dual_extension"]


def test_parent_quantum_input_contract_is_fail_closed():
    value = report()["BRST_and_global_input_contract"]
    assert value["present_ids"] == ["D1", "D2", "D3", "D4"]
    assert set(value["missing_ids"]) == {f"D{i}" for i in range(5, 16)}
    assert not value["all_required_inputs_present"]
    assert not value["full_parent_anomaly_line_computable"]


def test_index_level_virtual_bundle_is_not_promoted_to_spectral_determinant():
    value = report()["BRST_and_global_input_contract"]
    assert "not specify" in value["index_level_is_not_determinant_level"]


def test_tensor_lattice_is_rigid_when_a_and_b_are_held_fixed():
    value = report()["tensor_lattice_and_isotropy_cocycle_audit"]
    assert value["anomaly_coefficients"] == {"a": [2, 2], "b": [2, -1]}
    assert value["determinant_of_a_b_basis_over_Q"] == -6
    assert value["a_and_b_span_the_two_dimensional_lattice_over_Q"]
    assert not value["nontrivial_O_U_Z_twist_fixing_a_and_b_exists"]


def test_ordinary_smooth_GS_class_fails_every_isotropy_divisibility_test():
    value = report()["tensor_lattice_and_isotropy_cocycle_audit"]
    rows = {row["locus"]: row for row in value["isotropy_rows"]}
    assert rows["z00"]["two_Y_mod_order"] == [3, 2]
    assert rows["z11"]["two_Y_mod_order"] == [3, 2]
    assert rows["z10_z01"]["two_Y_mod_order"] == [1, 1]
    assert all(not row["ordinary_integral_Y_exists"] for row in rows.values())
    assert value["all_ordinary_integral_restrictions_fail"]
    assert not value["regulator_can_supply_missing_integral_Y_class"]
    assert not value["ordinary_GS_WuCS_state_defined_on_current_naive_isotropy_data"]
    for token in ("constant coefficient", "flat/torsion", "defect/cap/string"):
        assert token in value["scope"]


def test_completion_target_is_combined_anomaly_line_identity_not_a_number():
    value = report()["anomaly_line_trivialization_target"]
    assert "A_bare(U)" in value["closed_seven_manifold_target"]
    assert "WCS" in value["closed_seven_manifold_target"]
    assert "A_cap_defect(U)" in value["closed_seven_manifold_target"]
    assert "symmetric-monoidal isomorphism" in value["categorical_trivialization_target"]
    assert "cutting and gluing" in value["required_domain"]
    assert "to-be-defined" in value["required_domain"]
    assert not value["current_ordinary_characteristic_class"]["orbifold_restriction_exists"]
    smooth = value["smooth_parent_formula_only"]
    assert "H^4(W,boundary W;Lambda)" in smooth["when_U_bounds_W"]
    assert "log WCS^s" in smooth["smooth_WCS_counterphase"]
    assert not value["string_worldsheet_anomaly_sector_constructed"]
    assert not value["domain_explicitly_restricted_to_source_free_Y_zero_backgrounds"]
    assert not value["identity_proved_on_required_domain"]
    assert "not the degree-four Wu class" in value["notation_warning"]


def test_conditional_z2_su2r_polynomial_arithmetic_is_exact():
    value = report()["conditional_order2_SU2R_index_density"]
    branch = value["standard_induced_branch"]
    assert branch["single_Z2_orbit_normalization"] == "2 covering fixed points times 1/4 = 1/2"
    assert branch["Spin11_adjoint_trace"] == "27-28=-1"
    phases = branch["SU2R_phase_exponents_mod8"]
    assert phases["U_R_inverse"] == [1, 7]
    assert [2 * exponent % 8 for exponent in phases["U_R_inverse"]] == [2, 6]
    assert phases["U_R_inverse_squared"] == phases["U_R_minus2_expected"]
    assert phases["first_eigenline_root"] == "+rho"
    assert value["gravity_tensorino"][
        "coefficients_over_96_rho3_rho_nu2_rho_p1"
    ] == [0, 24, -24]
    assert value["opposite_chirality_gaugino"][
        "coefficients_over_96_rho3_rho_nu2_rho_p1"
    ] == [4, -3, -1]
    assert value["total"][
        "coefficients_over_96_rho3_rho_nu2_rho_p1"
    ] == [4, 21, -25]
    assert value["total"]["nonzero_as_formal_polynomial"]
    assert value["conventions"]["orientation"] == (
        "rho -> -rho reverses the displayed Z2 polynomial"
    )


def test_conditional_z4_restricted_bulk_crosscheck_contains_v71_rho_zero_limit():
    value = report()["conditional_order2_SU2R_index_density"][
        "Z4_restricted_bulk_crosscheck"
    ]
    gravity = value["gravity_tensorino_coefficients_over_192"]
    gaugino = value["gaugino_coefficients_over_192"]
    hypers = value["charged_plus_neutral_hyper_coefficients_over_192"]
    assert gravity == [42, -18, -16, -68, 108, -72]
    assert gaugino == [55, 5, -180, 45, 195, -60]
    assert hypers == [-121, -11, 0, 0, 0, 0]
    assert [sum(values) for values in zip(gravity, gaugino, hypers)] == [
        -24,
        -24,
        -196,
        -23,
        303,
        -132,
    ]
    assert value["coefficients_over_192"] == [-24, -24, -196, -23, 303, -132]
    assert value["inherited_bulk_nu_c2R"] == "11/16"
    assert value["rho_zero_reproduces_V71_standard_normal_polynomial"]
    assert value["rho2_nu_equals_11_over_16_nu_c2R"]
    assert "rho^2 nu is invariant" in value["orientation_rule"]
    assert "excludes inherited V70" in value["scope"]
    assert not value["accepted_as_global_result"]


def test_z2_su2r_result_corrects_scope_without_retracting_v71_normal_screen():
    value = report()["conditional_order2_SU2R_index_density"]
    relation = value["relation_to_V71"]
    assert relation["V71_normal_only_Z2_coefficients_nu3_and_nu_p1_remain_zero"]
    assert not relation["V71_full_parent_SU2R_dependent_Z2_polynomial_was_computed"]
    assert not value["accepted_as_regulator_complete_parent_result"]
    assert "gauge and flavor curvatures are set to zero" in value["projection_scope"]


def test_no_candidate_is_accepted_and_correct_candidate_is_selected_open():
    value = report()["candidate_matrix"]
    assert all(not row["accepted"] for row in value)
    selected = [row for row in value if row["result"] == "SELECTED_OPEN"]
    assert [row["id"] for row in selected] == [
        "F77E_EQUIVARIANT_ANOMALY_LINE_WUCS_TRIVIALIZATION"
    ]


def test_terminal_decision_keeps_current_action_rejected_and_candidate_open():
    value = report()["terminal_decision"]
    assert value["space_group_abelianization_computed"]
    assert value["standard_V71_residue_reproduced"]
    assert not value["equal_corner_profile_is_an_accepted_current_action"]
    assert value["V71_provisional_lifts_on_V70_fields_profile_is_unequal"]
    assert not value["accepted_full_parent_action_exists"]
    assert not value["V76_equal_corner_theorem_retracted"]
    assert not value["numeric_unprimed_parent_determinant_defined"]
    assert not value["full_equivariant_anomaly_line_computed"]
    assert not value["combined_anomaly_line_trivialized"]
    assert not value[
        "naive_smooth_GS_class_has_ordinary_integral_isotropy_restriction"
    ]
    assert not value["nontrivial_unchanged_tensor_lattice_twist_exists"]
    assert value["conditional_standard_branch_Z2_SU2R_polynomial_nonzero"]
    assert not value[
        "conditional_SU2R_index_densities_promoted_to_global_parent_result"
    ]
    assert not value["selected_candidate_accepted"]
    assert not value["theory_complete"]


def test_all_eight_gates_remain_open():
    value = report()
    assert value["gate_ledger"] == {f"G{i}": "OPEN" for i in range(1, 9)}
    assert value["terminal_decision"]["closed_gates"] == []


def test_open_obligations_include_brst_zero_modes_caps_and_wucs():
    text = " ".join(report()["open_obligations"]).lower()
    for token in (
        "brst",
        "zero-mode",
        "caps",
        "wucs",
        "regulator",
        "self-dual-string",
        "source-free",
        "same-action",
    ):
        assert token in text


def test_primary_source_manifest_is_bound_and_primary_only():
    value = report()
    assert len(value["primary_sources"]) == value["source_manifest"]["count"]
    assert value["source_manifest"]["kind"] == "primary_sources_only"
    assert value["source_manifest"]["count"] >= 8
    assert value["source_manifest"]["catalog_sha256"] == audit.canonical_sha(
        value["primary_sources"]
    )
    assert {
        "monnier_2013",
        "monnier_2016",
        "zhang_2026",
        "alvarez_gaume_witten_1984",
    }.issubset(
        set(value["source_manifest"]["ids"])
    )
    titles = {row["id"]: row["title"] for row in value["primary_sources"]}
    urls = {row["id"]: row["url"] for row in value["primary_sources"]}
    assert titles["monnier_2016"] == (
        "Topological field theories on manifolds with Wu structures"
    )
    assert urls["monnier_2016"] == "https://arxiv.org/abs/1607.01396"


def test_report_core_is_canonical():
    value = report()
    assert audit.canonical_sha(value) == value["core_sha256"]


def test_artifacts_are_fresh_when_present():
    value = report()
    if audit.OUT_JSON.is_file() and audit.OUT_MD.is_file():
        disk = json.loads(audit.OUT_JSON.read_text(encoding="utf-8"))
        assert disk == value
        assert audit.OUT_MD.read_text(encoding="utf-8") == audit.render_markdown(value)
