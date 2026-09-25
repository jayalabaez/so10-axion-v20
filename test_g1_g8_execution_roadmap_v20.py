#!/usr/bin/env python3
"""Tests for the contract-aware G1-G8 execution roadmap."""
from __future__ import annotations

import copy

import g1_g8_execution_roadmap_v20 as mod
import g3_sm_target_track_v20 as sm_track


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


def test_roadmap_audit_succeeds_with_attested_contract_and_g3_closed_on_sm_track():
    report = mod.build_report()
    assert report["status"] == (
        "G1_G8_EXECUTION_ROADMAP_READY__G1_G2_G3_G5_CLOSED__G4_OPEN"
    )
    assert report["overall_state"] == "OPEN"
    assert report["n_failed"] == 0, report["audit_failures"]
    assert report["contract_consistent"] is True
    assert report["scientific_blockers"] == list(sm_track.DOWNSTREAM_BLOCKERS)
    assert "G3_SM_PRESERVING_TARGET_REQUIRED" not in report["scientific_blockers"]
    assert report["checks"]["w3_g3_closed_only_through_sm_track"] is True
    assert report["gates"]["G3"]["closing_track"] == sm_track.TRACK_NAME
    assert report["g3_sm_target_track"]["closed"] is True
    assert report["g3_sm_target_track"]["downstream_caveats_resolved"] is False
    verdict = report["verdict"]
    assert verdict.startswith(
        "Wave 0 and the gauged scalar G1/G2 recertification are CLOSED. G3 is "
        "CLOSED on the SM Pati-Salam track (g3_sm_target_track_v20 through "
        "final_g3_acceptance_gate_v20): " + sm_track.CLOSURE_SCOPE
    )
    assert sm_track.CAVEAT_ROUTING_SENTENCE in verdict
    assert "W3-G4 is OPEN: recompute the ranks 34/35 (quotients 452/451)" in verdict
    assert "Diagnostics that cannot close G3: the historical 27-of-51" in verdict
    assert verdict.endswith(
        "The historical 64/91 saddle/search remains scoped to option C."
    )


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
    assert wave0["status"] == "CLOSED"
    assert wave0["gates"] == []


def test_attested_contract_closes_g1_g2_g3_g5_and_opens_g4():
    report = mod.build_report()
    gates = report["gates"]
    assert set(gates) == {f"G{i}" for i in range(1, 9)}
    assert {name: row["status"] for name, row in gates.items()} == {
        "G1": "CLOSED",
        "G2": "CLOSED",
        "G3": "CLOSED",
        "G4": "OPEN",
        "G5": "CLOSED",
        "G6": "BLOCKED",
        "G7": "BLOCKED",
        "G8": "BLOCKED",
    }
    assert report["summary"]["closed"] == ["G1", "G2", "G3", "G5"]
    assert report["summary"]["open"] == ["G4"]
    assert report["summary"]["blocked"] == ["G6", "G7", "G8"]
    assert report["summary"]["n_closed"] == 4
    assert report["summary"]["n_blocked"] == 3
    task_statuses = {task["id"]: task["status"] for task in report["tasks"]}
    assert task_statuses["W3-G3-FULL-STATIONARITY"] == "CLOSED"
    assert task_statuses["W3-G4-FULL-GAUGE-QUOTIENT"] == "OPEN"
    assert task_statuses["W3-G5-FULL-BFB"] == "CLOSED"
    # Late waves name only the gates they still wait on (G3 and G5 are CLOSED).
    assert task_statuses["W4-G6-SPECTRUM"] == "BLOCKED_ON_G4"
    assert task_statuses["W5-G7-TWO-LOOP"] == "BLOCKED_ON_G6_AND_EXTERNAL_VALIDATION"
    assert task_statuses["W6-G8-PROTON"] == "BLOCKED_ON_G6_G7"
    assert report["checks"]["late_wave_tasks_match_ledger_closure_waves"] is True


def test_late_wave_task_statuses_follow_the_gate_frontier():
    # The static table is the all-BLOCKED (unrepaired-contract) frontier.
    static = {task["id"]: task["status"] for task in mod.TASKS}
    assert static["W4-G6-SPECTRUM"] == "BLOCKED_ON_G3_G4_G5"
    assert static["W6-G8-PROTON"] == "BLOCKED_ON_G3_G6_G7"
    assert mod._late_task_statuses(
        {f"G{i}": mod.ledger.STATUS_BLOCKED for i in range(1, 9)}
    ) == {
        "W4-G6-SPECTRUM": "BLOCKED_ON_G3_G4_G5",
        "W6-G8-PROTON": "BLOCKED_ON_G3_G6_G7",
    }
    assert mod._late_task_statuses(
        {f"G{i}": mod.ledger.STATUS_CLOSED for i in range(1, 9)}
    ) == {"W4-G6-SPECTRUM": "OPEN", "W6-G8-PROTON": "OPEN"}
    # The roadmap mirrors the ledger's own closure waves 4 and 6.
    ledger_report = mod.ledger.build_report()
    waves = {wave["wave"]: wave["status"] for wave in ledger_report["closure_waves"]}
    report = mod._build_report_from_ledger(ledger_report)
    statuses = _task_statuses(report)
    assert statuses["W4-G6-SPECTRUM"] == waves[4] == "BLOCKED_ON_G4"
    assert statuses["W6-G8-PROTON"] == waves[6] == "BLOCKED_ON_G6_G7"
    # A ledger whose closure waves disagree with its gate frontier is an audit failure.
    drifted = copy.deepcopy(ledger_report)
    for wave in drifted["closure_waves"]:
        if wave["wave"] == 4:
            wave["status"] = "OPEN"
    report = mod._build_report_from_ledger(drifted)
    assert report["overall_state"] == "EXECUTION_FAIL"
    assert report["audit_failures"] == ["late_wave_tasks_match_ledger_closure_waves"]
    missing = {key: value for key, value in ledger_report.items() if key != "closure_waves"}
    report = mod._build_report_from_ledger(missing)
    assert "late_wave_tasks_match_ledger_closure_waves" in report["audit_failures"]


def test_every_gate_has_an_actionable_recertification_task():
    report = mod.build_report()
    gates_with_tasks = {gate for task in report["tasks"] for gate in task["gates"]}
    assert gates_with_tasks == set(report["gates"])
    assert all(task["deliverable"] for task in report["tasks"])
    assert all(task["acceptance"] for task in report["tasks"])


def test_gauged_g1_g2_calculations_are_complete_and_promoted():
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
        assert task["status"] == "CLOSED"
    assert report["gates"]["G1"]["status"] == "CLOSED"
    assert report["gates"]["G2"]["status"] == "CLOSED"


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
    assert frontier["SU5_Delta_signed_Phi_orbit_theorem_open"] is True
    assert frontier["SU5_Delta_SU4_Phi_slice_classified"] is True
    assert frontier["SU5_Delta_signed_Phi_local_components_closed"] is True
    assert frontier["SU5_Delta_distant_Phi_components_excluded"] is False
    assert frontier["SU5_Delta_Phi_SU3_fixed_slice_closed"] is True
    assert frontier["SU5_Delta_Phi_SU3_fixed_slice_dimension"] == 16
    assert frontier["SU5_Delta_global_Phi_orbit_lemma_open"] is True
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
    g3_task = next(
        task for task in report["tasks"] if task["id"] == "W3-G3-FULL-STATIONARITY"
    )
    assert "SU(5)+Delta" in g3_task["deliverable"]
    assert g3_task["deliverable"].startswith("construct an SM-preserving G3 candidate")
    assert "not an SM vacuum" in g3_task["deliverable"]
    assert (
        "is only an integrity-checked diagnostic track that cannot close G3"
        in g3_task["deliverable"]
    )
    assert "mathematical problem only" not in g3_task["deliverable"]
    assert "prove a uniform coercive global gap" not in g3_task["deliverable"]
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
    assert "Global Sigma and general/full H remain open for that non-SM point (the exact 448/38 full Hessian is certified separately)" in g3_task["deliverable"]
    assert "G3 remain open" not in g3_task["deliverable"]
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
    assert "Global Sigma and general/full H remain open for that non-SM point (the exact 448/38 full Hessian is certified separately)" in report["verdict"]
    assert "G3 remain open" not in report["verdict"]
    assert "only a four-real-dimensional Phi sub-slice" not in report["verdict"]
    assert "arbitrary-Phi bound remain open" not in report["verdict"]
    assert "coordinate Schur matrix" not in report["verdict"]


SM_TRACK_DONE_FRAGMENT = (
    "done: the SM Pati-Salam track (g3_sm_target_track_v20) closes G3 "
    "through final_g3_acceptance_gate_v20."
)
SM_TRACK_NOT_CERTIFIED_FRAGMENT = (
    "the SM Pati-Salam track (g3_sm_target_track_v20) is not certified, so "
    "G3 stays open."
)


def _w3_g3_task(report):
    return next(task for task in report["tasks"] if task["id"] == mod.W3_G3_TASK_ID)


def _task_statuses(report):
    return {task["id"]: task["status"] for task in report["tasks"]}


def _ledger_with_sm_track_inputs(sm_inputs):
    """A fresh ledger on the committed contract with the given SM-track inputs."""
    inputs = mod.ledger.build_report()["model_contract_reports"]
    return mod.ledger._build_report_from_inputs(
        x_report=inputs["exact_X"],
        g1_report=inputs["gauged_G1_character_census"],
        g2_report=inputs["gauged_G2_derivative_audit"],
        filter_report=inputs["gauged_scalar_filter"],
        g3_sm_track_inputs=sm_inputs,
    )


def test_w3_g3_deliverable_records_the_sm_track_closure_and_caveat_routing():
    report = mod.build_report()
    deliverable = _w3_g3_task(report)["deliverable"]
    assert mod.W3_G3_TASK_ID == "W3-G3-FULL-STATIONARITY"
    assert deliverable == mod.w3_g3_deliverable(True)
    assert deliverable.startswith(
        "construct an SM-preserving G3 candidate and certify it through the "
        "final gate; " + SM_TRACK_DONE_FRAGMENT
    )
    assert sm_track.WITNESS_SENTENCE in deliverable
    assert sm_track.CAVEAT_ROUTING_SENTENCE in deliverable
    assert SM_TRACK_NOT_CERTIFIED_FRAGMENT not in deliverable
    assert "still needs its model-level caveats resolved" not in deliverable
    # The equality-set binding is kept as an informational record.
    assert report["g3_sm_pati_salam_equality_set_binding"]["certified"] is True
    assert report["g3_sm_pati_salam_equality_set_binding"]["n_failed"] == 0
    # The static task table is fail-closed: it never carries the "done" clause.
    static = next(task for task in mod.TASKS if task["id"] == mod.W3_G3_TASK_ID)
    assert static["deliverable"] == mod.w3_g3_deliverable(False)
    assert SM_TRACK_NOT_CERTIFIED_FRAGMENT in static["deliverable"]
    assert sm_track.CAVEAT_ROUTING_SENTENCE in static["deliverable"]
    assert SM_TRACK_DONE_FRAGMENT not in static["deliverable"]
    assert static["status"] == (
        "SM_PATI_SALAM_TRACK_READY__CHIRAL_H_DIAGNOSTIC_ONLY__BLOCKED_ON_G2_PROMOTION"
    )
    # Only a literal True closes the clause.
    assert mod.w3_g3_deliverable(1) == mod.w3_g3_deliverable(False)


def test_w3_g4_and_g5_tasks_are_rebound_to_the_sm_witness():
    tasks = {task["id"]: task for task in mod.TASKS}
    g4 = tasks["W3-G4-FULL-GAUGE-QUOTIENT"]
    assert g4["status"] == "RANKS_34_35_AT_SM_WITNESS_PENDING__BLOCKED_ON_G3"
    assert "rank 34 (gauge" in g4["deliverable"] and "quotient 452" in g4["deliverable"]
    assert "rank 35" in g4["deliverable"] and "quotient 451" in g4["deliverable"]
    assert "eps -> 0 tuned" in g4["deliverable"]
    g5 = tasks["W3-G5-FULL-BFB"]
    assert g5["status"] == (
        "SCOPED_BFB_CERTIFICATE_ON_PATI_SALAM_VECTOR__BLOCKED_ON_MODEL_CONTRACT_PROMOTION"
    )
    assert "V4 >= |q|^4/167" in g5["deliverable"]
    assert g5["acceptance"] == (
        "the exact BFB bound covers every asymptotic field direction for the "
        "coupling vector of the accepted G3 witness"
    )


def test_w3_g3_fails_closed_when_the_sm_track_is_not_certified():
    sm_inputs = sm_track.load_inputs()
    sm_inputs["candidate"] = {}
    forged_ledger = _ledger_with_sm_track_inputs(sm_inputs)
    assert forged_ledger["n_failed"] == 0, forged_ledger["failures"]
    assert forged_ledger["g3_sm_target_track"]["closed"] is False

    report = mod._build_report_from_ledger(forged_ledger)

    assert report["n_failed"] == 0, report["audit_failures"]
    assert report["status"] == (
        "G1_G8_EXECUTION_ROADMAP_READY__G3_SM_TRACK_NOT_CERTIFIED__G3_OPEN"
    )
    assert report["overall_state"] == "OPEN"
    statuses = _task_statuses(report)
    assert statuses["W3-G3-FULL-STATIONARITY"] == "OPEN"
    assert statuses["W3-G4-FULL-GAUGE-QUOTIENT"] == "BLOCKED_ON_G3"
    assert statuses["W3-G5-FULL-BFB"] == "OPEN"
    assert statuses["W4-G6-SPECTRUM"] == "BLOCKED_ON_G3_G4_G5"
    assert statuses["W6-G8-PROTON"] == "BLOCKED_ON_G3_G6_G7"
    assert report["checks"]["late_wave_tasks_match_ledger_closure_waves"] is True
    assert report["gates"]["G3"]["status"] == "OPEN"
    assert report["gates"]["G4"]["status"] == "BLOCKED"
    assert report["gates"]["G5"]["status"] == "OPEN"
    deliverable = _w3_g3_task(report)["deliverable"]
    assert deliverable == mod.w3_g3_deliverable(False)
    assert SM_TRACK_DONE_FRAGMENT not in deliverable
    assert sm_track.CAVEAT_ROUTING_SENTENCE in deliverable
    assert report["verdict"].startswith(
        "Wave 0 and the gauged scalar G1/G2 recertification are CLOSED. G3 is "
        "OPEN because the SM Pati-Salam track (g3_sm_target_track_v20), its "
        "only closure route, is not certified (blockers: "
    )
    assert "sm_candidate_report_executes" in report["verdict"]
    assert sm_track.CLOSURE_SCOPE not in report["verdict"]


def test_forged_ledger_g3_closure_is_an_audit_failure():
    ledger_report = mod.ledger.build_report()
    gates = ledger_report["gates"]
    # G3 CLOSED without a closed SM track: the frontier no longer matches.
    without_track = {
        key: value
        for key, value in ledger_report.items()
        if key != "g3_sm_target_track"
    }
    report = mod._build_report_from_ledger(without_track)
    assert report["overall_state"] == "EXECUTION_FAIL"
    assert "gate_frontier_matches_contract_state" in report["audit_failures"]
    assert "task_frontier_matches_contract_state" not in report["audit_failures"]
    # The ledger's closure waves still follow its (forged) CLOSED G3.
    assert "late_wave_tasks_match_ledger_closure_waves" in report["audit_failures"]
    assert _task_statuses(report)["W3-G3-FULL-STATIONARITY"] == "OPEN"
    assert _task_statuses(report)["W4-G6-SPECTRUM"] == "BLOCKED_ON_G3_G4"
    # G3 CLOSED through any other track is rejected.
    wrong_track = dict(ledger_report)
    wrong_track["gates"] = {
        **gates,
        "G3": {**gates["G3"], "closing_track": "chiral_H_SU5_Delta"},
    }
    report = mod._build_report_from_ledger(wrong_track)
    assert report["overall_state"] == "EXECUTION_FAIL"
    for name in (
        "historical_saddle_search_not_promoted",
        "constructive_G3_local_minimum_and_global_rejection_integrated",
        "w3_g3_closed_only_through_sm_track",
    ):
        assert name in report["audit_failures"], name
    # A G5 row without the Pati-Salam binding reopens W3-G5 and breaks the frontier.
    unbound_g5 = dict(ledger_report)
    unbound_g5["gates"] = {
        **gates,
        "G5": {
            key: value
            for key, value in gates["G5"].items()
            if key != "bfb_coupling_vector"
        },
    }
    report = mod._build_report_from_ledger(unbound_g5)
    assert report["overall_state"] == "EXECUTION_FAIL"
    assert _task_statuses(report)["W3-G5-FULL-BFB"] == "OPEN"
    assert "gate_frontier_matches_contract_state" in report["audit_failures"]


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
    assert report["status"] == (
        "G1_G8_EXECUTION_ROADMAP_READY__G1_G2_G3_G5_CLOSED__G4_OPEN"
    )
    assert report["summary"]["closed"] == ["G1", "G2", "G3", "G5"]
    assert report["summary"]["open"] == ["G4"]
    task_statuses = {task["id"]: task["status"] for task in report["tasks"]}
    assert task_statuses["W0-MODEL-CONTRACT"] == mod.ledger.STATUS_CLOSED
    assert task_statuses["W1-G1-GAUGED-RECERTIFICATION"] == mod.ledger.STATUS_CLOSED
    assert task_statuses["W2-G2-GAUGED-PROJECTION"] == mod.ledger.STATUS_CLOSED
    assert task_statuses["W3-G3-FULL-STATIONARITY"] == mod.ledger.STATUS_CLOSED
    assert task_statuses["W3-G5-FULL-BFB"] == mod.ledger.STATUS_CLOSED
    assert task_statuses["W3-G4-FULL-GAUGE-QUOTIENT"] == mod.ledger.STATUS_OPEN
    assert report["gates"]["G4"]["status"] == mod.ledger.STATUS_OPEN
    assert report["gates"]["G6"]["status"] == mod.ledger.STATUS_BLOCKED
    assert report["gates"]["G8"]["status"] == mod.ledger.STATUS_BLOCKED
