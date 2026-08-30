#!/usr/bin/env python3
"""Tests for the contract-aware G1-G8 execution roadmap."""
from __future__ import annotations

import copy

import g1_g8_execution_roadmap_v20 as mod


def bind_tool_native_root_evidence(report):
    scaffold = report["executable_scaffold_contract"]
    scaffold.update(
        model_syntax_class="sarah_native",
        tool_native_sarah_syntax=True,
        statically_executable_model_contract=True,
    )
    scaffold["lagrangian"][
        "registered_in_GaugeES_LagrangianInput"
    ] = True
    external = report["external_model_validation"]
    external["schema"] = mod.ledger.exact_x.EXTERNAL_VALIDATION_SCHEMA
    external["present"] = True
    external["valid"] = True
    external["fresh_for_exact_model_bytes"] = True
    for name in mod.ledger.EXPECTED_EXACT_X_V3_EXTERNAL_CHECKS:
        external["checks"][name] = True


def test_roadmap_audit_succeeds_and_tracks_contract_state():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["audit_failures"]
    assert report["overall_state"] == (
        mod.ledger.STATUS_OPEN
        if report["contract_consistent"]
        else mod.ledger.STATUS_BLOCKED
    )
    assert report["scientific_blockers"]
    assert (
        "G6_GLOBAL_EQUALITY_SCALE_FULL_MASS_MIXING_POLE_AND_THRESHOLD_INPUTS_REQUIRED"
        in report["scientific_blockers"]
    )
    assert (
        "G6_DIRECT_SOURCE_ALGEBRA_GLOBAL_EQUALITY_ORBIT_AND_POLE_SPECTRUM_REQUIRED"
        not in report["scientific_blockers"]
    )
    assert (
        "G6_FROZEN_STABILIZER_IS_SU3_X_U1_89_NOT_PHYSICAL_ELECTROMAGNETISM"
        not in report["scientific_blockers"]
    )


def test_exact_x_v3_resolution_binds_trusted_tree_and_execution_state():
    report = mod.build_report()
    scoped = report["exact_X_v3_fail_closed_resolution"]
    assert scoped["source_bound"] is True
    assert scoped["static_native_contract_closed"] is True
    assert scoped["trusted_SARAH_4_15_3_source_tree_manifest_closed"] is True
    assert scoped["trusted_SARAH_source_tree_file_count"] == 1056
    consistent = report["contract_consistent"]
    assert scoped["external_v3_execution_attestation_present"] is consistent
    assert scoped["resolved_Wolfram_runtime_bound"] is consistent
    assert scoped["contract_consistent"] is consistent
    assert scoped["authoritative_G1_closed"] is consistent
    assert report["gates"]["G1"]["status"] == (
        mod.ledger.STATUS_CLOSED if consistent else mod.ledger.STATUS_BLOCKED
    )
    assert report["checks"][
        "exact_X_v3_contract_state_is_fail_closed_and_consistent"
    ]

    forged = copy.deepcopy(mod.ledger.build_report())
    forged["exact_X_v3_fail_closed_contract"]["source_bound"] = False
    failed = mod._build_report_from_ledger(forged)
    assert failed["n_failed"] > 0
    assert failed["overall_state"] == "EXECUTION_FAIL"


def test_parallel_eft_g4_g5_g6_are_pinned_without_authoritative_promotion():
    report = mod.build_report()
    g4 = report["parallel_EFT_G4_resolution"]
    g5 = report["parallel_EFT_G5_resolution"]
    g6 = report["parallel_EFT_G6_resolution"]
    assert g4["source_bound"] is True
    assert g4["raw_sha256"] == mod.EFT_G4_RAW_SHA256
    assert g4["core_sha256"] == mod.EFT_G4_CORE_SHA256
    assert g4["mathematical_G4_closed"] is True
    assert g4["release_G4_verified"] is False
    assert g4["original_renormalizable_G4_closed"] is False
    assert g4["integration_completed"] is True
    assert "parallel_EFT_G4_integrated_into_release_orchestrators" not in g4[
        "release_blockers"
    ]
    assert g5["source_bound"] is True
    assert g5["raw_sha256"] == mod.EFT_G5_RAW_SHA256
    assert g5["core_sha256"] == mod.EFT_G5_CORE_SHA256
    assert g5["mathematical_G5_closed"] is True
    assert g5["release_G5_verified"] is False
    assert g5["original_renormalizable_G5_closed"] is False
    assert g5["new_SOS_claimed"] is False
    assert g5["integration_completed"] is True
    assert "downstream_parallel_G5_integration_completed" not in g5[
        "release_blockers"
    ]
    assert g6["source_bound"] is True
    assert g6["raw_sha256"] == mod.EFT_G6_RAW_SHA256
    assert g6["core_sha256"] == mod.EFT_G6_CORE_SHA256
    assert (
        g6["gate_source_raw_sha256"]
        == mod.ledger.FINAL_G6_EFT_GATE_SOURCE_RAW_SHA256
    )
    assert g6["formal_SU3_x_U1_89_tree_factorization_closed"] is True
    assert g6["mathematical_G6_closed"] is False
    assert g6["physical_mathematical_G6_closed"] is False
    assert g6["release_G6_verified"] is False
    assert g6["original_renormalizable_G6_closed"] is False
    assert g6["authoritative_G6_gate_mutated"] is False
    assert g6["spectrum_summary"]["ambient_real_fields"] == 486
    assert g6["spectrum_summary"]["gauge_quotient_dimension"] == 449
    assert g6["spectrum_summary"]["ungauged_PQ_zero_modes"] == 1
    assert g6["spectrum_summary"]["positive_massive_modes"] == 448
    assert g6["integration_completed"] == (
        "parallel_EFT_G6_integrated_into_release_orchestrators"
        not in g6["release_blockers"]
    )
    expected = {
        "G3": mod.ledger.STATUS_OPEN,
        "G4": mod.ledger.STATUS_BLOCKED,
        "G5": mod.ledger.STATUS_CLOSED,
        "G6": mod.ledger.STATUS_BLOCKED,
    }
    for name, status in expected.items():
        assert report["gates"][name]["status"] == status
    assert report["checks"]["parallel_EFT_G4_mathematical_raw_and_core_bound"]
    assert report["checks"]["parallel_EFT_G5_mathematical_raw_and_core_bound"]
    assert report["checks"][
        "parallel_EFT_G6_formal_spectrum_bound_but_physical_G6_open"
    ]

    for key in (
        "parallel_EFT_G4_mathematical",
        "parallel_EFT_G5_mathematical",
        "parallel_EFT_G6_spectrum",
    ):
        forged_ledger = copy.deepcopy(mod.ledger.build_report())
        forged_ledger[key]["core_sha256"] = "0" * 64
        forged_roadmap = mod._build_report_from_ledger(forged_ledger)
        assert forged_roadmap["n_failed"] > 0
        assert forged_roadmap["overall_state"] == "EXECUTION_FAIL"


def test_formal_u1_89_restriction_audit_is_pinned_and_keeps_g7_g8_blocked():
    report = mod.build_report()
    g7 = report["parallel_EFT_G7_nonidentifiability_resolution"]
    assert g7["source_bound"] is True
    assert g7["core_sha256"] == mod.EFT_G7_NONIDENTIFIABILITY_CORE_SHA256
    assert g7["raw_sha256"] == mod.EFT_G7_NONIDENTIFIABILITY_RAW_SHA256
    assert g7["source_raw_sha256"] == mod.EFT_G7_NONIDENTIFIABILITY_SOURCE_RAW_SHA256
    assert g7["formal_U1_89_abstract_restriction_noninjectivity_proved"] is True
    assert g7["exact_physical_EFT_G7_input_nonidentifiability_proved"] is False
    assert g7["historical_electroweak_lift_interpretation_valid"] is False
    assert g7["formal_U1_89_restriction_map_noninjective"] is True
    assert g7["absolute_scale_unidentified"] is True
    assert g7["mathematical_G7_closed"] is False
    assert g7["positive_G7_certified"] is False
    assert g7["negative_G7_no_go_certified"] is False
    assert g7["release_G7_verified"] is False
    assert g7["authoritative_renormalizable_G7_closed"] is False
    assert g7["integration_completed"] is True
    assert report["gates"]["G7"]["status"] == mod.ledger.STATUS_BLOCKED
    assert report["gates"]["G8"]["status"] == mod.ledger.STATUS_BLOCKED

    forged = copy.deepcopy(mod.ledger.build_report())
    forged["parallel_EFT_G7_nonidentifiability"]["core_sha256"] = "0" * 64
    failed = mod._build_report_from_ledger(forged)
    assert failed["n_failed"] > 0
    assert failed["overall_state"] == "EXECUTION_FAIL"


def test_physical_sm_g8_frontier_is_recomputed_and_keeps_g8_open():
    report = mod.build_report()
    scoped = report["physical_SM_G8_identifiability_frontier_resolution"]
    assert scoped["source_bound"] is True
    assert scoped["canonical_G8_contract_audited"] is True
    assert scoped["continuous_absolute_scale_nonidentifiability_proved"] is True
    assert scoped["flavor_and_interference_nonidentifiability_audited"] is True
    assert scoped[
        "repository_frozen_PDG_2025_single_channel_constraint_verified"
    ] is True
    assert scoped["minimal_exhibited_joint_free_real_dimension"] == 1
    assert scoped["unique_proton_lifetime_or_distribution"] is False
    assert scoped["physical_G8_closed"] is False
    assert scoped["release_G8_verified"] is False
    assert scoped["authoritative_G8_closed"] is False
    assert scoped["all_acceptance_criteria_pass"] is False
    assert report["gates"]["G8"]["status"] == mod.ledger.STATUS_BLOCKED
    assert report["checks"][
        "physical_SM_G8_identifiability_frontier_bound_and_G8_open"
    ]

    forged = copy.deepcopy(mod.ledger.build_report())
    forged["physical_SM_G8_identifiability_frontier_contract"][
        "source_bound"
    ] = False
    failed = mod._build_report_from_ledger(forged)
    assert failed["n_failed"] > 0
    assert failed["overall_state"] == "EXECUTION_FAIL"


def test_physical_g7_contract_advances_scoped_work_without_promoting_g7():
    report = mod.build_report()
    scoped = report["physical_G7_component_threshold_resolution"]
    assert scoped["source_bound"] is True
    assert scoped["physical_PS_SM_matter_branching_closed"] is True
    assert scoped["parameterized_one_loop_matter_threshold_kernel_closed"] is True
    assert scoped["exact_two_loop_nonyukawa_gauge_flow_closed"] is True
    assert scoped["physical_component_pole_mass_matrices_closed"] is False
    assert scoped["heavy_vector_matching_closed"] is False
    assert scoped["physical_G7_closed"] is False
    assert scoped["mathematical_G7_closed"] is False
    assert scoped["release_G7_verified"] is False
    assert scoped["authoritative_renormalizable_G7_closed"] is False
    assert report["gates"]["G7"]["status"] == mod.ledger.STATUS_BLOCKED
    assert report["checks"][
        "physical_G7_component_threshold_contract_bound_but_full_G7_open"
    ]

    forged = copy.deepcopy(mod.ledger.build_report())
    forged["physical_G7_component_threshold_contract"]["source_bound"] = False
    failed = mod._build_report_from_ledger(forged)
    assert failed["n_failed"] > 0
    assert failed["overall_state"] == "EXECUTION_FAIL"


def test_yukawa_cgc_and_physical_sm_overlays_are_recomputed_fail_closed():
    report = mod.build_report()
    cgcs = report["normalized_SO10_Yukawa_CGC_resolution"]
    assert cgcs["source_bound"] is True
    assert cgcs["normalized_10_CGCs_closed"] is True
    assert cgcs["normalized_126bar_CGCs_closed"] is True
    assert cgcs["all_declared_representation_CGCs_closed"] is True
    assert cgcs["full_one_two_loop_Yukawa_betas_closed"] is False
    assert cgcs["physical_threshold_matching_and_running_closed"] is False
    assert cgcs["physical_G7_closed"] is False

    physical = report["physical_SM_vacuum_truth_resolution"]
    assert physical["source_bound"] is True
    assert physical["physical_SM_target_exactly_constructed"] is True
    assert physical["standard_SU3C_x_U1em_stabilizer_proved"] is True
    assert physical["old_selected_EFT_stabilizer_label_superseded"] is True
    assert physical["old_selected_EFT_target_actual_stabilizer"] == (
        "SU(3)_C x U(1)_89"
    )
    for gate in ("G3", "G4", "G5", "G6", "G7"):
        assert physical[f"physical_SM_{gate}_closed"] is False

    forged = copy.deepcopy(mod.ledger.build_report())
    forged["normalized_SO10_Yukawa_CGC_contract"]["source_bound"] = False
    failed = mod._build_report_from_ledger(forged)
    assert failed["n_failed"] > 0
    assert failed["overall_state"] == "EXECUTION_FAIL"


def test_physical_sm_radial_equality_resolution_is_recomputed_fail_closed():
    report = mod.build_report()
    scoped = report[
        "physical_SM_source_algebra_equality_frontier_resolution"
    ]
    assert scoped["source_bound"] is True
    assert scoped["core_sha256"] == (
        mod.ledger.PHYSICAL_SM_SOURCE_EQUALITY_CORE_SHA256
    )
    assert scoped["radial_stationary_equality_classified_exactly"] is True
    assert scoped["radial_gcd"] == "t - 1"
    assert scoped["observed_source_Hessian_row_lcm"] == 126000
    assert scoped["reconstructed_aggregate_Hessian_lcm"] == 6300103327590
    assert scoped["direct_source_algebra_stationary_Hessian_available"] is False
    assert scoped["complete_nonradial_equality_orbit_proved"] is False
    assert scoped["old_formal_U1_89_EFT_scope_promoted"] is False
    expected = {
        "G3": mod.ledger.STATUS_OPEN,
        "G4": mod.ledger.STATUS_BLOCKED,
        "G5": mod.ledger.STATUS_CLOSED,
    }
    for gate, status in expected.items():
        assert scoped[f"physical_SM_{gate}_closed"] is False
        assert report["gates"][gate]["status"] == status
    assert report["checks"][
        "physical_SM_radial_equality_frontier_bound_but_G3_G4_G5_open"
    ]

    forged = copy.deepcopy(mod.ledger.build_report())
    forged["physical_SM_source_algebra_equality_frontier"][
        "radial_stationary_equality_classified_exactly"
    ] = False
    failed = mod._build_report_from_ledger(forged)
    assert failed["n_failed"] > 0
    assert failed["overall_state"] == "EXECUTION_FAIL"


def test_physical_sm_five_amplitude_resolution_is_recomputed_fail_closed():
    report = mod.build_report()
    scoped = report["physical_SM_five_amplitude_equality_resolution"]
    assert scoped["source_bound"] is True
    assert scoped["exact_radial_theorem_strictly_extended"] is True
    assert scoped[
        "five_real_amplitude_slice_stationary_equality_classified"
    ] is True
    assert scoped["exact_real_discrete_sign_variant_count"] == 16
    assert scoped["target_strict_minimum_on_five_amplitude_slice"] is True
    assert scoped["full_486_field_stationary_equality_classified"] is False
    assert scoped[
        "continuous_symmetry_orbit_equivalence_of_16_variants_proved"
    ] is False
    assert scoped["direct_source_algebra_full_486_Hessian_available"] is False
    expected = {
        "G3": mod.ledger.STATUS_OPEN,
        "G4": mod.ledger.STATUS_BLOCKED,
        "G5": mod.ledger.STATUS_CLOSED,
    }
    for gate, status in expected.items():
        assert scoped[f"physical_SM_{gate}_closed"] is False
        assert report["gates"][gate]["status"] == status
    assert report["checks"][
        "physical_SM_five_amplitude_equality_bound_but_full_G3_G4_G5_open"
    ]

    forged = copy.deepcopy(mod.ledger.build_report())
    forged["physical_SM_five_amplitude_equality_contract"][
        "source_bound"
    ] = False
    failed = mod._build_report_from_ledger(forged)
    assert failed["n_failed"] > 0
    assert failed["overall_state"] == "EXECUTION_FAIL"


def test_new_source_Hessian_and_branch_mismatch_views_are_recomputed_fail_closed():
    report = mod.build_report()
    hard = report["physical_SM_hard_projector_Hessians_resolution"]
    assert hard["source_bound"] is True
    assert hard["exact_source_Hessian_row_count"] == 10
    assert hard["remaining_active_row_count"] == 27
    assert hard["all_37_active_source_Hessians_closed"] is False
    last_six = report["physical_SM_last_six_Hessians_resolution"]
    assert last_six["source_bound"] is True
    assert last_six["exact_last_six_source_Hessians_closed"] is True
    assert last_six["all_37_active_source_Hessians_available"] is True
    assert (
        last_six["exact_37_row_aggregate_stationarity_kernel_rank_PSD_closed"]
        is False
    )
    aggregate = report["physical_SM_37_row_aggregate_resolution"]
    assert aggregate["source_bound"] is True
    assert aggregate["all_37_active_Hessians_source_derived"] is True
    assert aggregate["exact_source_aggregate_kernel_dimension"] == 38
    assert aggregate["exact_source_aggregate_rank"] == 448
    assert aggregate["exact_source_aggregate_PSD_and_strict_mod_symmetry"] is True
    assert aggregate["full_486_global_equality_orbit_closed"] is False
    local_orbit = report["physical_SM_local_equality_orbit_resolution"]
    assert local_orbit["source_bound"] is True
    assert local_orbit["full_486_local_stationary_orbit_classified"] is True
    assert local_orbit["full_486_local_stationary_equality_orbit_classified"] is True
    assert local_orbit["all_16_sign_variants_one_continuous_K_orbit"] is True
    assert local_orbit["quantitative_neighborhood_radius_proved"] is False
    assert local_orbit["complete_486_global_equality_orbit_classified"] is False
    mismatch = report["physical_SM_G4_G5_branch_mismatch_resolution"]
    assert mismatch["source_bound"] is True
    assert mismatch["exact_branch_mismatch_proved"] is True
    assert mismatch["unit_rescaling_case_count"] == 101
    assert mismatch["global_no_go_for_other_physical_EW_branches"] is False

    forged = copy.deepcopy(mod.ledger.build_report())
    forged["physical_SM_hard_projector_Hessians_contract"]["source_bound"] = False
    failed = mod._build_report_from_ledger(forged)
    assert failed["n_failed"] > 0
    forged = copy.deepcopy(mod.ledger.build_report())
    forged["physical_SM_last_six_Hessians_contract"]["source_bound"] = False
    failed = mod._build_report_from_ledger(forged)
    assert failed["n_failed"] > 0
    forged = copy.deepcopy(mod.ledger.build_report())
    forged["physical_SM_37_row_aggregate_contract"]["source_bound"] = False
    failed = mod._build_report_from_ledger(forged)
    assert failed["n_failed"] > 0
    forged = copy.deepcopy(mod.ledger.build_report())
    forged["physical_SM_local_equality_orbit_contract"]["source_bound"] = False
    failed = mod._build_report_from_ledger(forged)
    assert failed["n_failed"] > 0
    forged = copy.deepcopy(mod.ledger.build_report())
    forged["physical_SM_G4_G5_branch_mismatch_contract"]["source_bound"] = False
    failed = mod._build_report_from_ledger(forged)
    assert failed["n_failed"] > 0


def test_vector_scalar_and_recalculated_G7_views_are_recomputed_fail_closed():
    report = mod.build_report()
    vectors = report["physical_SM_heavy_vector_mass_resolution"]
    assert vectors["source_bound"] is True
    assert vectors["exact_parameterized_tree_vector_mass_matrix_closed"] is True
    assert vectors["exact_vector_rank_kernel_and_Goldstone_image_closed"] is True
    assert vectors["exact_SU3C_x_U1em_vector_sector_resolution_closed"] is True
    assert vectors["parameterized_vector_threshold_log_inputs_closed"] is True
    assert vectors["pole_vector_masses_closed"] is False
    assert vectors["vector_Goldstone_ghost_matching_closed"] is False
    assert vectors["physical_G6_closed"] is False
    assert vectors["physical_G7_closed"] is False

    vector_msbar = report["physical_SM_heavy_vector_MSbar_matching_resolution"]
    assert vector_msbar["source_bound"] is True
    assert vector_msbar[
        "combined_heavy_vector_FPghost_Goldstone_MSbar_kernel_closed"
    ] is True
    assert vector_msbar["finite_MSbar_vector_constant_closed"] is True
    assert vector_msbar["Goldstone_double_count_guard_active"] is True
    assert vector_msbar["arbitrary_Rxi_sector_resolved_matching_closed"] is False
    assert vector_msbar["pole_mass_conversion_closed"] is False
    assert vector_msbar["SM_symmetric_pre_EW_matching_closed"] is False
    assert vector_msbar["complete_scalar_fermion_threshold_matching_closed"] is False
    assert vector_msbar["physical_G6_closed"] is False
    assert vector_msbar["physical_G7_closed"] is False

    vector_rxi = report[
        "physical_SM_vector_Rxi_vacuum_cancellation_resolution"
    ]
    assert vector_rxi["source_bound"] is True
    assert vector_rxi[
        "zero_background_Rxi_vacuum_determinant_cancellation_closed"
    ] is True
    assert vector_rxi["all_37_broken_directions_closed"] is True
    assert vector_rxi["background_covariant_heat_kernel_matching_closed"] is False
    assert vector_rxi[
        "sector_resolved_general_background_determinants_closed"
    ] is False
    assert vector_rxi["pole_vector_masses_closed"] is False
    assert vector_rxi["physical_G6_closed"] is False
    assert vector_rxi["physical_G7_closed"] is False

    scalars = report[
        "conditional_physical_SM_EFT_Hessian_spectrum_resolution"
    ]
    assert scalars["source_bound"] is True
    assert scalars["conditional_reconstructed_tree_scalar_spectrum_closed"] is True
    assert scalars["conditional_tree_Hessian_factorization_closed"] is True
    assert scalars["conditional_tree_sector_assignment_closed"] is True
    assert scalars["source_algebra_derived_tree_scalar_spectrum_closed"] is False
    assert scalars["physical_scalar_pole_spectrum_closed"] is False
    assert scalars["physical_G6_closed"] is False

    frontier = report["physical_SM_G6_G7_closure_frontier_resolution"]
    assert frontier["source_bound"] is True
    assert frontier["continuous_nonidentifiability_proved"] is True
    assert frontier["minimal_closure_path_machine_readable"] is True
    assert len(frontier["minimal_closure_path"]) == 7
    assert frontier["unique_absolute_tree_spectrum"] is False
    assert frontier["unique_pole_spectrum"] is False
    assert frontier["unique_threshold_vector"] is False
    assert frontier["unique_full_RGE_trajectory"] is False
    assert frontier["physical_G6_closed"] is False
    assert frontier["physical_G7_closed"] is False

    recalculated = report["physical_G7_recalculated_input_resolution"]
    assert recalculated["source_bound"] is True
    assert recalculated["all_resolved_scoped_inputs_closed"] is True
    assert all(recalculated["resolved_scoped_inputs"].values())
    assert all(recalculated["superseded_stale_blockers"].values())
    assert all(value is False for value in recalculated["precise_open_inputs"].values())
    assert recalculated["physical_G6_closed"] is False
    assert recalculated["physical_G7_closed"] is False
    assert recalculated["release_G7_verified"] is False
    assert report["checks"][
        "recalculated_G7_inputs_supersede_stale_broad_blockers_only"
    ]
    assert report["checks"][
        "physical_SM_heavy_vector_MSbar_kernel_bound_but_G6_G7_open"
    ]
    assert report["checks"][
        "physical_SM_zero_background_Rxi_vacuum_cancellation_bound_only"
    ]
    assert report["checks"][
        "physical_SM_G6_G7_nonidentifiability_frontier_bound"
    ]
    assert "finite_vector_matching_constants" not in recalculated[
        "precise_open_inputs"
    ]

    for key in (
        "physical_SM_heavy_vector_mass_contract",
        "physical_SM_heavy_vector_MSbar_matching_contract",
        "physical_SM_vector_Rxi_vacuum_cancellation_contract",
        "conditional_physical_SM_EFT_Hessian_spectrum_contract",
        "physical_SM_G6_G7_closure_frontier_contract",
        "physical_G7_recalculated_input_resolution",
    ):
        forged = copy.deepcopy(mod.ledger.build_report())
        forged[key]["source_bound"] = False
        failed = mod._build_report_from_ledger(forged)
        assert failed["n_failed"] > 0
        assert failed["overall_state"] == "EXECUTION_FAIL"

    forged = copy.deepcopy(mod.ledger.build_report())
    forged["physical_SM_vacuum_truth_overlay"]["physical_SM_G3_closed"] = True
    failed = mod._build_report_from_ledger(forged)
    assert failed["n_failed"] > 0
    assert failed["overall_state"] == "EXECUTION_FAIL"


def test_wave_zero_is_first_on_the_critical_path():
    report = mod.build_report()
    assert mod.acyclic() is True
    assert report["critical_path"] == [
        "MODEL_CONTRACT",
        "G1",
        "G2",
        "G3/G4/G5",
        "G6",
        "G7",
        "G8",
    ]
    assert report["dependencies"]["MODEL_CONTRACT"] == []
    assert report["dependencies"]["G1"] == ["MODEL_CONTRACT"]
    wave0 = next(task for task in report["tasks"] if task["id"] == "W0-MODEL-CONTRACT")
    assert wave0["wave"] == 0
    assert (
        wave0["status"]
        == (
            mod.ledger.STATUS_CLOSED
            if report["contract_consistent"]
            else "BLOCKED__EXTERNAL_SARAH_EXECUTION_ATTESTATION_MISSING"
        )
    )
    assert wave0["gates"] == []


def test_legacy_gate_frontier_tracks_contract_state():
    report = mod.build_report()
    gates = report["gates"]
    assert set(gates) == {f"G{i}" for i in range(1, 9)}
    if report["contract_consistent"]:
        assert report["summary"]["closed"] == ["G1", "G2", "G5"]
        assert report["summary"]["open"] == ["G3"]
        assert report["summary"]["blocked"] == ["G4", "G6", "G7", "G8"]
    else:
        assert all(row["status"] == "BLOCKED" for row in gates.values())
        assert report["summary"]["closed"] == []
        assert report["summary"]["n_closed"] == 0
        assert report["summary"]["n_blocked"] == 8


def test_every_gate_has_an_actionable_recertification_task():
    report = mod.build_report()
    gates_with_tasks = {gate for task in report["tasks"] for gate in task["gates"]}
    assert gates_with_tasks == set(report["gates"])
    assert all(task["deliverable"] for task in report["tasks"])
    assert all(task["acceptance"] for task in report["tasks"])


def test_g1_census_component_theorem_and_g2_audit_are_distinct_scoped_results():
    report = mod.build_report()
    scoped = report["gauged_u1x_scalar_subtheorems"]
    assert scoped["G1"]["multiplicity_census_complete"] is True
    assert scoped["G1"][
        "explicit_component_tensor_subset_integration_complete"
    ] is True
    assert scoped["G1"]["character_census_remains_multiplicity_only"] is True
    assert scoped["G1"]["full_G1_closed"] is True
    consistent = report["contract_consistent"]
    assert scoped["G1"]["authoritative_G1_promoted_closed"] is consistent
    assert scoped["G1"]["release_G1_verified"] is consistent
    assert scoped["G1"]["invariant_directions"] == 44
    assert scoped["G1"]["real_potential_parameters"] == 51
    assert scoped["G2"]["scoped_derivative_audit_complete"] is True
    assert scoped["G2"]["authoritative_promotion_blocked_on_full_G1"] is False
    assert scoped["G2"]["authoritative_promotion_blocked_on_model_contract"] is (
        not consistent
    )
    assert scoped["G2"]["real_field_dimension"] == 486
    assert scoped["G2"]["promoted_stationarity_rank"] == 13
    assert scoped["G2"]["promoted_stationarity_nullity"] == 38
    assert scoped["G2"][
        "exact_projector_zero_corrected_normalized_SVD_rank_13"
    ] is True
    assert scoped["G2"]["stationarity_rank_13_exactly_certified"] is True
    assert scoped["G2"]["stationarity_nullity_38_exactly_certified"] is True
    tasks = {item["id"]: item for item in report["tasks"]}
    if not consistent:
        assert tasks["W1-G1-GAUGED-RECERTIFICATION"]["status"] == (
            "SOURCE_BOUND_FULL_MATHEMATICAL_G1_COMPONENT_RING_COMPLETE__"
            "MODEL_CONTRACT_BLOCKED"
        )
        assert tasks["W2-G2-GAUGED-PROJECTION"]["status"] == (
            "SOURCE_BOUND_FULL_MATHEMATICAL_G2_POTENTIAL_COMPLETE__"
            "MODEL_CONTRACT_BLOCKED"
        )
    resolution = report["renormalizable_G1_component_tensor_resolution"]
    assert resolution["source_bound"] is True
    assert resolution["mathematical_G1_closed"] is True
    assert resolution["authoritative_G1_promoted_closed"] is False
    assert resolution["release_G1_verified"] is False
    assert resolution["downstream_integration_completed"] is True
    # The frozen renormalizable theorem retains its original mathematical-only
    # boundary; the live canonical/ledger layer performs authoritative G1
    # promotion after the genuine external attestation.
    assert resolution["release_blockers"] == [mod.ledger.CONTRACT_BLOCKER]
    assert report["gates"]["G1"]["status"] == (
        "CLOSED" if consistent else "BLOCKED"
    )
    assert report["gates"]["G2"]["status"] == (
        "CLOSED" if consistent else "BLOCKED"
    )


def test_historical_option_c_subtheorems_remain_visible():
    historical = mod.build_report()["historical_option_c_subtheorems"]
    assert historical["model_contract_id"] == "historical_option_c_no_x_v20"
    assert historical["authoritative_for_gauged_model"] is False
    assert historical["G1"]["invariant_directions"] == 64
    assert historical["G1"]["real_potential_parameters"] == 91
    assert historical["G2"]["dense_Hessian_shape"] == [486, 486]
    assert historical["G3"]["massive_physical_quotient_dimension"] == 449
    assert historical["G3"]["anchored_witness_negative_modes"] == 46
    assert historical["G3"]["stability_search_iterations"] == 80
    assert historical["G3"]["best_minimum_equilibrated_eigenvalue"] == (
        -0.025502339625368114
    )
    assert historical["G3"]["strict_local_minimum_found"] is False


def test_historical_milestones_are_not_mislabeled_as_authoritative_closure():
    milestones = mod.build_report()["recent_milestones"]
    assert milestones
    assert all(row["scope"] == "historical_option_c_no_x_v20" for row in milestones)
    assert all(row["authoritative_gate_closure"] is False for row in milestones)


def test_constructive_g3_frontier_is_actionable_but_not_promoted():
    report = mod.build_report()
    frontier = report["gauged_u1x_g3_constructive_frontier"]
    assert all(frontier["artifacts_present"].values())
    assert frontier["integrity_pass"] is True
    assert frontier["candidate_nonzero_real_parameters"] == 27
    assert frontier["candidate_real_parameter_count"] == 51
    assert frontier["candidate_J0"] == "-21/200"
    assert frontier["exact_A_square_recoupling_source_bound"] is True
    assert frontier["exact_SOS_BFB_stationarity_source_bound"] is True
    assert frontier["exact_PD_rank"] == 429
    assert frontier["exact_PD_nullity"] == 33
    assert frontier["exact_full_Hessian_rank"] == 448
    assert frontier["fixed_P_branch_exactly_excluded"] is True
    assert frontier["lower_replacement_rejected_for_wrong_symmetry"] is True
    assert frontier["SU5_Delta_PD_exact_global_frontier"] is True
    assert frontier["SU5_Delta_PD_exact_Hessian_rank"] == 429
    assert frontier["SU5_Delta_PD_exact_Hessian_nullity"] == 33
    assert frontier["SU5_Delta_HSX_honest_frontier"] is True
    assert frontier["SU5_Delta_HSX_nonzero_real_parameters"] == 28
    assert frontier["SU5_Delta_HSX_exact_symmetry_ranks"] == [36, 37, 38]
    assert frontier["SU5_Delta_HSX_transverse_dimension"] == 448
    assert frontier["SU5_Delta_HSX_full_Hessian_proof_grade"] is False
    assert frontier["SU5_Delta_HSX_exact_Hessian_closed"] is True
    assert frontier["SU5_Delta_HSX_exact_Hessian_rank"] == 448
    assert frontier["SU5_Delta_HSX_exact_Hessian_nullity"] == 38
    assert frontier["SU5_Delta_HSX_exact_Hessian_PSD"] is True
    assert frontier["SU5_Delta_HSX_exact_Hessian_kernel_is_symmetry"] is True
    assert frontier["SU5_Delta_HSX_exact_quotient_positive"] is True
    assert frontier["SU5_Delta_HSX_full_quartic_BFB_exact"] is True
    assert frontier["SU5_Delta_HSX_finite_field_global_gap_open"] is True
    assert frontier["SU5_Delta_equality_honestly_reduced"] is True
    assert frontier["SU5_Delta_Phi_orbit_audit_honest"] is True
    assert frontier["SU5_Delta_literal_single_Phi_orbit_refuted"] is True
    assert frontier["SU5_Delta_signed_Phi_orbit_theorem_open"] is False
    assert frontier["SU5_Delta_signed_Phi_orbit_theorem_closed"] is True
    assert frontier["SU5_Delta_SU4_Phi_slice_classified"] is True
    assert frontier["SU5_Delta_signed_Phi_local_components_closed"] is True
    assert frontier["SU5_Delta_distant_Phi_components_excluded"] is True
    assert frontier["SU5_Delta_Phi_SU3_fixed_slice_closed"] is True
    assert frontier["SU5_Delta_Phi_SU3_fixed_slice_dimension"] == 16
    assert frontier["SU5_Delta_global_Phi_orbit_lemma_open"] is False
    assert frontier["SU5_Delta_global_Phi_orbit_lemma_closed"] is True
    assert frontier["SU5_Delta_chiral_global_gap_honestly_reduced"] is True
    assert frontier["SU5_Delta_chiral_lower_witness_found"] is False
    assert frontier["SU5_Delta_chiral_small_beta_route_exists"] is True
    assert frontier["SU5_Delta_chiral_beta_1_over_20_global_certified"] is False
    assert frontier["SU5_fixed_F_full_offkernel_gap_closed"] is True
    assert frontier["SU5_fixed_F_gap_equality_is_selected_flag"] is True
    assert frontier["SU5_arbitrary_Phi_offstratum_gap_open"] is True
    assert frontier["SU5_max_negative_all_zero_residual_route_excluded"] is True
    assert (
        frontier["SU5_max_negative_all_zero_residual_strict_margin"]
        == "7859/140295000"
    )
    assert frontier["SU5_max_negative_pure_Delta_full_residual_gap_closed"] is True
    assert frontier["SU5_max_negative_pure_Delta_full_residual_minimum"] == "1/5000"
    assert frontier[
        "SU5_max_negative_rank1_SU3_four_dimensional_slice_closed"
    ] is True
    assert frontier["SU5_max_negative_rank1_SU3_slice_dimension"] == 4
    assert frontier["SU5_max_negative_rank1_SU3_ambient_dimension"] == 16
    assert frontier["SU5_max_negative_rank1_SU3_slice_minimum"] == "1/5000"
    assert frontier["SU5_max_negative_arbitrary_rank1_Phi_open"] is True
    assert frontier["SU5_max_negative_arbitrary_Sigma_orientation_open"] is True
    assert frontier["rank1_SU4_stabilizer_infrastructure_exact"] is True
    assert frontier["rank1_SU4_joint_stabilizer_dimension"] == 15
    assert frontier["rank1_SU4_Phi210_intertwiner_infrastructure_exact"] is True
    assert frontier["rank1_SU4_Phi210_carrier_count"] == 25
    assert frontier["rank1_SU4_Sym2_invariant_dimension"] == 45
    assert frontier["rank1_SU4_aligned_carriers_exact"] is True
    assert frontier["rank1_SU4_aligned_direct_sum_rank"] == 210
    assert frontier["rank1_SU4_physical_real_maps_exact"] is True
    assert frontier["rank1_SU4_Phi210_quadratic_basis_exact"] is True
    assert frontier["rank1_SU4_quadratic_constraint_shape"] == [5952, 551]
    assert frontier["rank1_SU4_quadratic_constraint_rank"] == 506
    assert frontier["rank1_SU4_quadratic_constraint_nullity"] == 45
    assert frontier["rank1_SU4_quadratic_basis_count"] == 45
    assert frontier["rank1_SU4_quadratic_basis_rank"] == 45
    assert frontier["rank1_SU4_quadratic_live_invariance_exact"] is True
    assert frontier["rank1_SU4_Schur_SOS_SDP_open"] is True
    assert frontier["rank1_SU4_arbitrary_Phi_bound_open"] is True
    assert frontier["rank1_SU4_augmented_SOS_census_exact"] is True
    assert frontier["rank1_SU4_augmented_homogeneous_dimension"] == 22_366
    assert frontier["rank1_SU4_augmented_complex_isotypic_type_count"] == 35
    assert frontier["rank1_SU4_augmented_complex_irreducible_copy_count"] == 824
    assert frontier["rank1_SU4_augmented_real_isotypic_block_count"] == 22
    assert frontier["rank1_SU4_augmented_Schur_real_parameter_count"] == 19_594
    assert frontier["rank1_SU4_augmented_invariant_equation_count"] == 6_585
    assert frontier["rank1_SU4_augmented_coordinate_Schur_map_open"] is True
    assert frontier["rank1_SU4_augmented_physical_target_open"] is True
    assert frontier["rank1_SU4_augmented_Schur_SOS_SDP_open"] is True
    assert frontier["rank1_SU4_augmented_cubic_map_exact"] is True
    assert frontier["rank1_SU4_augmented_cubic_carrier_copy_count"] == 540
    assert frontier["rank1_SU4_augmented_cubic_real_variable_count"] == 1_414
    assert frontier["rank1_SU4_augmented_cubic_coordinate_map_shape"] == [
        478,
        1_414,
    ]
    assert frontier["rank1_SU4_augmented_cubic_coordinate_map_nnz"] == 3_145
    assert frontier["rank1_SU4_augmented_cubic_coordinate_map_rank"] == 478
    assert (
        frontier["rank1_SU4_augmented_cubic_coordinate_map_kernel_dimension"]
        == 936
    )
    assert frontier["rank1_SU4_augmented_cubic_zero_placeholder_nonphysical"]
    assert frontier["rank1_SU4_augmented_cubic_other_graded_maps_open"]
    assert frontier["rank1_SU4_augmented_cubic_full_coordinate_map_open"]
    assert frontier["rank1_SU4_augmented_cubic_physical_target_open"]
    assert frontier["rank1_SU4_augmented_cubic_Schur_SOS_SDP_open"]
    assert frontier["rank1_SU4_augmented_cubic_arbitrary_Phi_bound_open"]
    assert frontier["rank1_SU4_augmented_cubic_G3_open"]
    assert frontier["rank1_SU4_augmented_quartic_map_exact"] is True
    assert frontier["rank1_SU4_augmented_quartic_carrier_family_count"] == 35
    assert frontier["rank1_SU4_augmented_quartic_irreducible_copy_count"] == 798
    assert frontier["rank1_SU4_augmented_quartic_real_block_count"] == 22
    assert frontier["rank1_SU4_augmented_quartic_coordinate_map_shape"] == [
        6_057,
        18_085,
    ]
    assert frontier["rank1_SU4_augmented_quartic_coordinate_map_nnz"] == 115_641
    assert frontier["rank1_SU4_augmented_quartic_coordinate_map_rank"] == 6_057
    assert (
        frontier["rank1_SU4_augmented_quartic_coordinate_map_kernel_dimension"]
        == 12_028
    )
    assert frontier["rank1_SU4_augmented_quartic_physical_target_open"]
    assert frontier[
        "rank1_SU4_augmented_quartic_standard_PSD_congruences_open"
    ]
    assert frontier["rank1_SU4_augmented_quartic_SDP_open"]
    assert frontier["rank1_SU4_augmented_quartic_arbitrary_Phi_bound_open"]
    assert frontier["rank1_SU4_augmented_quartic_G3_open"]
    assert frontier[
        "rank1_SU4_legacy_v20_PSD_routes_and_stale_payload_well_formed"
    ]
    assert frontier["rank1_SU4_legacy_v20_physical_target_valid"] is False
    assert frontier["rank1_SU4_legacy_v20_primal_valid"] is False
    assert frontier["rank1_SU4_augmented_standard_PSD_route_count"] == 22
    assert frontier["rank1_SU4_augmented_standard_PSD_parameter_count"] == 19_594
    assert frontier["rank1_SU4_corrected_fixed_endpoint_theorem_exact"]
    assert frontier["rank1_SU4_corrected_positive_Gram_map_shape"] == [
        6_585, 19_594
    ]
    assert frontier["rank1_SU4_corrected_positive_Gram_map_common_denominator"] == 256
    assert frontier["rank1_SU4_corrected_positive_Gram_map_nnz"] == 138_550
    assert frontier["rank1_SU4_corrected_physical_target_common_denominator"] == 576_000
    assert frontier["rank1_SU4_corrected_physical_target_nonzero_count"] == 512
    assert frontier["rank1_SU4_corrected_exact_coefficient_equalities"] == 6_585
    assert frontier["rank1_SU4_corrected_strict_positive_Gram_blocks"] == 22
    assert frontier["rank1_SU4_corrected_strict_positive_LDL_pivots"] == 824
    assert frontier["rank1_SU4_corrected_arbitrary_real_Phi_at_fixed_endpoint"]
    assert frontier["rank1_SU4_corrected_p_zero_set_at_t1_empty"]
    assert frontier["rank1_SU4_corrected_global_Sigma_proved"] is False
    assert frontier["rank1_SU4_corrected_general_H_proved"] is False
    assert frontier["rank1_SU4_corrected_full_Hessian_proved"] is False
    assert frontier["rank1_SU4_corrected_G3_closed"] is False
    assert frontier["SU5_arbitrary_Phi_nonzero_residual_cancellations_open"] is False
    assert (
        frontier["SU5_arbitrary_non_pure_Delta_Sigma_uniform_coercivity_open"]
        is True
    )
    assert frontier["SU5_arbitrary_Phi_uniform_coercivity_open"] is True
    assert frontier["alternative_global_SOS_audit_honestly_open"] is True
    assert frontier["all_vanishing_global_SOS_replacements_excluded"] is True
    assert (
        frontier["nonvanishing_residual_global_SOS_replacements_excluded"]
        is False
    )
    assert frontier["direct_exact_PD_source_binding"] is True
    assert frontier["complete_potential_BFB_exactly_certified"] is True
    assert frontier["selected_vacuum_stationarity_exactly_certified"] is True
    assert frontier["strict_local_minimum_certified"] is True
    assert frontier["global_minimum_certified"] is False
    assert frontier["selected_global_minimum_disproved"] is True
    assert frontier["exact_lower_energy_field_witness_certified"] is True
    assert frontier["constructive_candidate_rejected_for_G3"] is True
    assert frontier["global_uniqueness_certified"] is False
    assert frontier["G3_closed"] is False
    assert report["checks"][
        "constructive_G3_local_minimum_and_global_rejection_integrated"
    ]
    assert report["parallel_EFT_G3_resolution"]["mathematical_G3_closed"] is True
    assert report["parallel_EFT_G3_resolution"]["source_bound"] is True
    assert report["parallel_EFT_G3_resolution"]["raw_sha256"] == mod.EFT_G3_RAW_SHA256
    assert report["parallel_EFT_G3_resolution"]["core_sha256"] == mod.EFT_G3_CORE_SHA256
    assert report["checks"][
        "parallel_EFT_G3_acceptance_raw_and_core_bound"
    ] is True
    assert report["parallel_EFT_G3_resolution"][
        "original_renormalizable_G3_closed"
    ] is False
    g3_task = next(
        task for task in report["tasks"] if task["id"] == "W3-G3-FULL-STATIONARITY"
    )
    assert "SU(5)+Delta" in g3_task["deliverable"]
    assert "four-real-dimensional SU(3) regression is historical" in g3_task["deliverable"]
    assert "corrected v21 exact theorem covers every real Phi210" in g3_task["deliverable"]
    assert "exact SU(4) stabilizer" in g3_task["deliverable"]
    assert "aligned 25-carrier" in g3_task["deliverable"]
    assert "5952x551 rank-506" in g3_task["deliverable"]
    assert "exact augmented census has dimension 22366" in (
        g3_task["deliverable"]
    )
    assert "478x1414 integer coefficient map" in g3_task["deliverable"]
    assert "exact rank 478 and kernel" in g3_task["deliverable"]
    assert "abstract interface placeholder" in g3_task["deliverable"]
    assert "homogeneous quartic map has shape 6057x18085" in g3_task["deliverable"]
    assert "rank 6057" in g3_task["deliverable"]
    assert "kernel dimension 12028" in g3_task["deliverable"]
    assert "legacy v20 assembled physical target is rejected" in g3_task["deliverable"]
    assert "corrected 6585x19594 standard positive-Gram map" in g3_task["deliverable"]
    assert "strict 22-block/824-pivot primal" in g3_task["deliverable"]
    assert (
        "For that historical fixed-H/Sigma frontier, global Sigma, "
        "general/full H, and its then-unassembled Hessian remained open"
        in g3_task["deliverable"]
    )
    assert "exact source-derived 37-row Hessian" in g3_task["deliverable"]
    assert "the full Hessian, and G3 remain open" not in g3_task["deliverable"]
    g6_task = next(task for task in report["tasks"] if task["id"] == "W4-G6-SPECTRUM")
    assert "LOCAL_SOURCE_HESSIAN_CLOSED" in g6_task["status"]
    assert "exact source-derived all-37 Hessian" in g6_task["deliverable"]
    assert "kernel/rank 38/448" in g6_task["deliverable"]
    assert "complete global equality orbit" in g6_task["deliverable"]
    assert "full scalar and fermion mass/mixing" in g6_task["deliverable"]
    assert "derive the scalar Hessian" not in g6_task["deliverable"].lower()
    assert "486-field" in g3_task["acceptance"]
    assert "478x1414 integer map" in report["verdict"]
    assert "kernel dimension 936" in report["verdict"]
    assert "zero placeholder is not a physical target" in report["verdict"]
    assert "homogeneous quartic map is exact-rank-6057" in report["verdict"]
    assert "kernel dimension 12028" in report["verdict"]
    assert "legacy v20 assembled physical target is rejected" in report["verdict"]
    assert "corrected 6585x19594 standard positive-Gram map" in report["verdict"]
    assert "strict 22-block/824-pivot primal" in report["verdict"]
    assert "every real Phi210" in report["verdict"]
    assert (
        "For that historical fixed-H/Sigma frontier, global Sigma, "
        "general/full H, and its then-unassembled Hessian remained open"
        in report["verdict"]
    )
    assert "source-derived all-37 physical-branch Hessian" in report["verdict"]
    assert "the full Hessian, and G3 remain open" not in report["verdict"]
    assert "only a four-real-dimensional Phi sub-slice" not in report["verdict"]
    assert "arbitrary-Phi bound remain open" not in report["verdict"]
    assert "coordinate Schur matrix" not in report["verdict"]
    assert "pending a corrected vacuum and recomputed spectrum" not in report["verdict"]
    assert "corrected SU(3)_C x U(1)_em target/stabilizer" in report["verdict"]
    assert "conditional reconstructed 486-state scalar tree spectrum" in report["verdict"]
    assert "canonical sparse 304-Weyl embedding" in report["verdict"]
    assert "SARAH implicit/identical-Weyl contraction conversion" in report["verdict"]


def test_no_validation_exclusion_or_discovery_claim():
    report = mod.build_report()
    assert "No whole-model validation, exclusion, or discovery claim" in report[
        "new_physics_policy"
    ]
    assert report["checks"]["whole_model_neither_validated_nor_excluded"]


def test_repaired_contract_promotes_source_bound_g1_g2_and_g5():
    current = mod.ledger.build_report()
    inputs = current["model_contract_reports"]
    repaired_x = copy.deepcopy(inputs["exact_X"])
    repaired_x.update(
        contract_consistent=True,
        blocker=None,
        scientific_blockers=[],
        contract_conflicts=[],
        overall_state="PASS",
    )
    repaired_x["flag"]["contract_consistent"] = True
    repaired_x["flag"]["x_selection_rule_consistently_declared"] = True
    bind_tool_native_root_evidence(repaired_x)
    repaired_ledger = mod.ledger._build_report_from_inputs(
        x_report=repaired_x,
        g1_report=inputs["gauged_G1_character_census"],
        g2_report=inputs["gauged_G2_derivative_audit"],
        filter_report=inputs["gauged_scalar_filter"],
        g3_sos_report=inputs["gauged_G3_SOS_candidate"],
        g3_pd_report=inputs["gauged_G3_direct_exact_PD_rank"],
        g3_a_square_report=inputs["gauged_G3_exact_A_square_recoupling"],
        g3_sos_bfb_report=inputs["gauged_G3_exact_SOS_BFB_stationarity"],
    )

    report = mod._build_report_from_ledger(repaired_ledger)

    assert report["n_failed"] == 0, report["audit_failures"]
    assert report["overall_state"] == mod.ledger.STATUS_OPEN
    assert report["summary"]["closed"] == ["G1", "G2", "G5"]
    assert report["summary"]["open"] == ["G3"]
    assert report["summary"]["blocked"] == [
        "G4",
        "G6",
        "G7",
        "G8",
    ]
    task_statuses = {task["id"]: task["status"] for task in report["tasks"]}
    assert task_statuses["W0-MODEL-CONTRACT"] == mod.ledger.STATUS_CLOSED
    assert task_statuses["W1-G1-GAUGED-RECERTIFICATION"] == mod.ledger.STATUS_CLOSED
    assert task_statuses["W2-G2-GAUGED-PROJECTION"] == mod.ledger.STATUS_CLOSED
    assert task_statuses["W3-G3-FULL-STATIONARITY"] == mod.ledger.STATUS_OPEN
    assert task_statuses["W3-G5-FULL-BFB"] == mod.ledger.STATUS_CLOSED
    assert task_statuses["W3-G4-FULL-GAUGE-QUOTIENT"] == "BLOCKED_ON_G3"
    assert report["gates"]["G1"]["status"] == mod.ledger.STATUS_CLOSED
    assert report["gates"]["G2"]["status"] == mod.ledger.STATUS_CLOSED
    assert report["gates"]["G6"]["status"] == mod.ledger.STATUS_BLOCKED
    assert report["gates"]["G8"]["status"] == mod.ledger.STATUS_BLOCKED
    assert "G1/G2 recertification are CLOSED" in report["verdict"]
