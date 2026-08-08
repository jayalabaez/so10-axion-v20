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
    assert frontier["rank1_SU4_Schur_SOS_SDP_open"] is True
    assert frontier["rank1_SU4_arbitrary_Phi_bound_open"] is True
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
    assert "four-real-dimensional Phi sub-slice" in g3_task["deliverable"]
    assert "16-dimensional SU(3)-fixed space" in g3_task["deliverable"]
    assert "exact SU(4) stabilizer" in g3_task["deliverable"]
    assert "full augmented SU(4)-equivariant degree-2 Schur/SOS SDP" in (
        g3_task["deliverable"]
    )
    assert "486-field" in g3_task["acceptance"]


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
