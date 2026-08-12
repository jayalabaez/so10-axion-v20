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
    external["valid"] = True
    for name in (
        "tool_native_model_format_matches_path",
        "external_process_command_matches_tool",
        "input_manifest_schema_is_supported",
        "input_manifest_sha256_matches_entries",
        "primary_model_is_bound_in_input_manifest",
        "validation_driver_is_bound_to_command",
        "captured_process_log_is_hash_bound",
        "captured_process_log_has_all_required_pass_markers",
    ):
        external["checks"][name] = True


def test_roadmap_audit_succeeds_but_science_is_blocked():
    report = mod.build_report()
    assert report["status"] == (
        "G1_G8_EXECUTION_ROADMAP_READY__WAVE0_MODEL_CONTRACT_BLOCKED"
    )
    assert report["overall_state"] == "BLOCKED"
    assert report["n_failed"] == 0, report["audit_failures"]
    assert report["contract_consistent"] is False
    assert report["scientific_blockers"]


def test_parallel_eft_g4_g5_are_pinned_without_promoting_legacy_gates():
    report = mod.build_report()
    g4 = report["parallel_EFT_G4_resolution"]
    g5 = report["parallel_EFT_G5_resolution"]
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
    for name in ("G3", "G4", "G5"):
        assert report["gates"][name]["status"] == mod.ledger.STATUS_BLOCKED
    assert report["checks"]["parallel_EFT_G4_mathematical_raw_and_core_bound"]
    assert report["checks"]["parallel_EFT_G5_mathematical_raw_and_core_bound"]

    for key in ("parallel_EFT_G4_mathematical", "parallel_EFT_G5_mathematical"):
        forged_ledger = copy.deepcopy(mod.ledger.build_report())
        forged_ledger[key]["core_sha256"] = "0" * 64
        forged_roadmap = mod._build_report_from_ledger(forged_ledger)
        assert forged_roadmap["n_failed"] > 0
        assert forged_roadmap["overall_state"] == "EXECUTION_FAIL"


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
        == "BLOCKED__EXTERNAL_SARAH_EXECUTION_ATTESTATION_MISSING"
    )
    assert wave0["gates"] == []


def test_all_gates_are_blocked_and_closed_summary_is_empty():
    report = mod.build_report()
    gates = report["gates"]
    assert set(gates) == {f"G{i}" for i in range(1, 9)}
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


def test_gauged_g1_g2_calculations_are_complete_and_await_promotion_only():
    report = mod.build_report()
    scoped = report["gauged_u1x_scalar_subtheorems"]
    assert scoped["G1"]["invariant_directions"] == 44
    assert scoped["G1"]["real_potential_parameters"] == 51
    assert scoped["G2"]["real_field_dimension"] == 486
    assert scoped["G2"]["promoted_stationarity_rank"] == 13
    assert scoped["G2"]["promoted_stationarity_nullity"] == 38
    assert scoped["G2"][
        "exact_projector_zero_corrected_normalized_SVD_rank_13"
    ] is True
    assert scoped["G2"]["stationarity_rank_13_exactly_certified"] is True
    assert scoped["G2"]["stationarity_nullity_38_exactly_certified"] is True
    for task_id in (
        "W1-G1-GAUGED-RECERTIFICATION",
        "W2-G2-GAUGED-PROJECTION",
    ):
        task = next(item for item in report["tasks"] if item["id"] == task_id)
        assert task["status"].startswith("SCOPED_CALCULATION_COMPLETE")
    assert report["gates"]["G1"]["status"] == "BLOCKED"
    assert report["gates"]["G2"]["status"] == "BLOCKED"


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
    assert "Global Sigma, general/full H, the full Hessian, and G3 remain open" in g3_task["deliverable"]
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
    assert "Global Sigma, general/full H, the full Hessian, and G3 remain open" in report["verdict"]
    assert "only a four-real-dimensional Phi sub-slice" not in report["verdict"]
    assert "arbitrary-Phi bound remain open" not in report["verdict"]
    assert "coordinate Schur matrix" not in report["verdict"]


def test_no_validation_exclusion_or_discovery_claim():
    report = mod.build_report()
    assert "No whole-model validation, exclusion, or discovery claim" in report[
        "new_physics_policy"
    ]
    assert report["checks"]["whole_model_neither_validated_nor_excluded"]


def test_repaired_contract_advances_the_roadmap_without_audit_failure():
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
    task_statuses = {task["id"]: task["status"] for task in report["tasks"]}
    assert task_statuses["W0-MODEL-CONTRACT"] == mod.ledger.STATUS_CLOSED
    assert task_statuses["W1-G1-GAUGED-RECERTIFICATION"] == mod.ledger.STATUS_CLOSED
    assert task_statuses["W2-G2-GAUGED-PROJECTION"] == mod.ledger.STATUS_CLOSED
    assert task_statuses["W3-G3-FULL-STATIONARITY"] == mod.ledger.STATUS_OPEN
    assert task_statuses["W3-G5-FULL-BFB"] == mod.ledger.STATUS_CLOSED
    assert task_statuses["W3-G4-FULL-GAUGE-QUOTIENT"] == "BLOCKED_ON_G3"
    assert report["gates"]["G6"]["status"] == mod.ledger.STATUS_BLOCKED
    assert report["gates"]["G8"]["status"] == mod.ledger.STATUS_BLOCKED
