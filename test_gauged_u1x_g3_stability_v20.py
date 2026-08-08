from __future__ import annotations

import inspect
import json

import pytest

import gauged_u1x_g3_stability_v20 as audit

def test_default_path_is_light_and_heavy_recomputation_is_opt_in() -> None:
    signature = inspect.signature(audit.build_report)
    assert signature.parameters["recompute_heavy"].default is False
    assert signature.parameters["max_iterations"].default == 80


def test_loader_rejects_a_stale_G2_artifact(tmp_path, monkeypatch) -> None:
    stale = {
        "model_contract_id": "gauged_u1x_phi17_v20",
        "flags": {"G2_gauged_u1x_derivatives_certified": True},
    }
    path = tmp_path / "stale.json"
    path.write_text(json.dumps(stale), encoding="utf-8")
    monkeypatch.setattr(audit, "UPSTREAM_G2_JSON", path)
    with pytest.raises(RuntimeError, match="stale or failed upstream G2 artifact"):
        audit.load_upstream_g2_report()


def test_authoritative_counts_and_structural_symmetry_quotient() -> None:
    report = audit.build_report()
    assert report["model_contract_id"] == "gauged_u1x_phi17_v20"
    coverage = report["coverage"]
    assert coverage["invariant_directions"] == 44
    assert coverage["real_parameters"] == 51
    assert coverage["real_field_dimension"] == 486
    assert coverage["stationarity_rank"] == 13
    assert coverage["stationarity_nullity"] == 38
    assert coverage["exact_stationarity_rank"] == 13
    assert coverage["exact_stationarity_nullity"] == 38
    assert coverage["exact_stationarity_rank_lower_bound"] == 13
    assert coverage["gauge_quotient_dimension_including_axion"] == 449
    assert coverage["massive_transverse_quotient_dimension"] == 448
    assert coverage["physical_quotient_dimension"] == 448
    symmetry = report["symmetry_quotient"]
    assert "includes the physical axion" in symmetry["interpretation"]
    assert symmetry["dimension_certification"].startswith("exact")
    assert symmetry["SO10_physical_rank"] == 36
    assert symmetry["SO10_plus_U1X_rank"] == 37
    assert symmetry["gauge_quotient_dimension_including_axion"] == 449
    assert symmetry["global_PQ_independent"] is True
    assert symmetry["SO10_plus_U1X_plus_PQ_rank"] == 38
    assert symmetry["massive_transverse_quotient_dimension"] == 448
    assert symmetry["physical_quotient_dimension"] == 448
    assert symmetry["numerical_massive_transverse_basis_dimension"] == 448
    assert symmetry["symmetry_quotient_overlap"] < 1.0e-12
    assert symmetry["quotient_orthonormality_residual"] < 1.0e-12
    exact = symmetry["exact_certificate"]
    assert exact["certified"] is True
    assert exact["SO10"]["minor"]["determinant"] == "1"
    assert exact["gauged_SO10_U1X"]["rank"] == 37
    assert exact["gauged_SO10_U1X"]["minor"]["determinant"] == "-2"
    assert exact["U1X_PQ_independence"]["determinant"] == -68
    assert exact["full_SO10_U1X_global_PQ"]["rank"] == 38
    assert exact["full_SO10_U1X_global_PQ"]["minor"]["determinant"] == "34"
    assert exact["live_compiler_binding"]["compiler_binding_passes"] is True


def test_exact_stationarity_contract_closes_rank_but_not_stability() -> None:
    stationarity = audit.build_report()["stationarity_contract"]
    assert stationarity["analytic_zero_gradient_parameter_ids"] == [
        "lambda::O27_B01_126bar_self_projectors",
        "lambda::O27_B02_126bar_self_projectors",
        "lambda::O44_B03_Phi2_Sigma_projectors",
    ]
    assert stationarity["exact_three_zero_gradient_certificates"] is True
    assert stationarity["exact_rank_lower_bound"] == 13
    lower = stationarity["exact_rank_lower_bound_certificate"]
    assert lower["determinant_nonzero"] is True
    assert lower["exact_rank_upper_bound_certified"] is True
    assert stationarity["exact_rank_upper_bound_certified"] is True
    assert stationarity["stationarity_rank_13_exactly_certified"] is True
    assert stationarity["stationarity_nullity_38_exactly_certified"] is True
    assert stationarity["exact_stationarity_nullspace_certified"] is False
    assert stationarity["exact_stationarity_rank_certificate_open"] is False
    stable = stationarity["exact_informed_constraint_representation"]
    assert stable["upstream_certified"] is True
    assert stable["compiler_pivot_rows"] == [
        0,
        36,
        40,
        209,
        222,
        223,
        234,
        235,
        380,
        482,
        484,
    ]
    assert stable["exact_unit_parameter_ids"] == [
        "re::O31_B01_unique_Hdag2_Sigma2",
        "im::O31_B01_unique_Hdag2_Sigma2",
    ]
    assert stable["legacy_column_normalize_backscale_used"] is False
    witness = stationarity["exact_stationary_witness"]
    assert witness["gradient_exactly_zero"] is True
    assert witness["normalization_value"] == "1"
    assert witness["strictly_inside_4pi_box"] is True
    assert witness["P24_trace"] == 288
    h6 = stationarity["exact_H6_radial_nonflat_witness"]
    assert h6["certified"] is True
    assert h6["radial_coordinate_index"] == 222
    assert h6["radial_coordinate_name"] == "H[6].x"
    assert not any(h6["exact_symmetry_tangent_row"])
    assert h6["exact_first_derivative"].endswith("= 0")
    assert "4 h^2 > 0" in h6["exact_second_derivative"]


def test_stationarity_constructor_delegates_to_exact_informed_rows(
    monkeypatch,
) -> None:
    sentinel = {"certified": True, "constraint_rows": "stable"}
    monkeypatch.setattr(
        audit.exact_rank_source,
        "exact_informed_stationarity_constraints",
        lambda rows: sentinel,
    )
    assert audit._stationarity_family(()) is sentinel


def test_reference_derived_field_congruence_cannot_be_reused() -> None:
    with pytest.raises(RuntimeError, match="reference-derived field congruence"):
        audit._physical_stationary_pencil((), {})


def test_all_legacy_stationary_family_numerics_are_quarantined() -> None:
    evidence = audit.recorded_numerical_evidence()
    invalidation = evidence["legacy_stationary_family_invalidation"]
    assert invalidation["status"] == "INVALIDATED"
    assert invalidation["invalidated"] is True
    assert invalidation["scientific_use_for_G3"] is False
    assert invalidation[
        "maximum_false_constraint_residual_for_exact_witness"
    ] > 0.014
    counterexample = invalidation["exact_counterexample"]
    assert counterexample["dense_stationarity_gradient_exactly_zero"] is True
    assert counterexample["exact_P24_trace"] == 288
    for key in ("finite_cut_search", "normalized_common_kernel", "solver_attempts"):
        row = evidence[key]
        assert row["status"] == "INVALIDATED"
        assert row["invalidated"] is True
        assert row["scientific_use_for_G3"] is False


def test_reference_equilibrated_135_flat_claim_is_a_numerical_artifact() -> None:
    reaudit = audit.build_report()["corrected_common_kernel_reaudit"]
    assert reaudit["proof_grade"] is False
    recorded = reaudit["recorded_numerical_regression"]
    corrected = recorded["corrected_raw_orthonormal_quotient"]
    assert corrected["field_congruence"] == "identity"
    assert corrected["common_Gram_rank"] == 448
    assert corrected["common_Gram_nullity"] == 0
    assert corrected["common_Gram_min_eigenvalue"] > 1.0e-3
    invalid = recorded["invalidated_reference_equilibration"]
    assert invalid["diagonal_scale_condition_ratio"] > 1.0e8
    assert invalid["apparent_common_Gram_rank_at_1e_minus_8"] == 313
    assert invalid["apparent_common_Gram_nullity_at_1e_minus_8"] == 135
    assert invalid["invalidated"] is True
    assert invalid["scientific_use_for_G3"] is False
    assert reaudit["strict_local_minimum_certified"] is False
    assert reaudit["PSD_feasibility_certified"] is False
    assert reaudit["fixed_vacuum_no_go_certified"] is False


def test_constructive_candidate_replaces_the_non_WLOG_positive_J0_slice() -> None:
    report = audit.build_report()
    candidate = report["constructive_candidate_reaudit"]
    coefficients = candidate["coefficient_vector"]
    assert candidate["n_failed"] == 0
    assert coefficients["nonzero_count"] == 27
    assert coefficients["maximum_absolute_coefficient"] == pytest.approx(73 / 8)
    assert coefficients["symbolic_nonzero"][
        audit.NORMALIZATION_PARAMETER_ID
    ] == "-21/200"
    assert report["checks"]["historical_positive_J0_anchor_is_not_WLOG"]
    formulation = report["SDP_formulation"]
    assert formulation["historical_positive_J0_anchor_WLOG"] is False
    assert not any("= 1" in equation for equation in formulation["equations_after_unblock"])
    flags = report["flags"]
    assert flags["constructive_sparse_27_parameter_candidate_found"] is True
    assert flags["historical_positive_J0_normalization_invalidated"] is True
    assert flags["constructive_A_square_recoupling_exactly_source_bound"] is True
    assert flags["constructive_candidate_conditional_rank448_evidence"] is False
    assert flags["constructive_candidate_exact_rank448_certificate"] is True
    assert flags["constructive_candidate_direct_exact_source_binding"] is True
    assert flags["G3_fixed_vacuum_PSD_feasible_certified"] is True
    assert flags["G3_fixed_vacuum_strict_minimum_certified"] is True
    assert flags["complete_potential_BFB"] is True
    assert flags["G3_selected_vacuum_global_no_go_certified"] is True
    assert flags["exact_lower_energy_field_witness_certified"] is True
    assert flags["constructive_candidate_rejected_for_G3"] is True
    assert flags["G3_closed"] is False


def test_Casimir_blocks_and_exact_P24_survive_only_as_structural_results() -> None:
    block = audit.recorded_numerical_evidence()["symmetry_block_reduction"]
    assert block["status"] == "STRUCTURAL_ONLY__STATIONARY_SOLVES_INVALIDATED"
    assert block["unbroken_gauge_algebra"]["physical_dimension"] == 9
    assert [row["dimension"] for row in block["Casimir_blocks"]] == [
        20,
        20,
        84,
        84,
        56,
        48,
        64,
        72,
    ]
    assert block["block_dimension_sum"] == 448
    assert block["exact_P24_certificate"]["rank"] == 24
    assert block["exact_P24_certificate"]["trace"] == 24
    assert block["exact_P24_certificate"]["idempotence_exact"] is True
    invalid = block["invalidated_stationary_family_results"]
    assert invalid["block_solver"]["status"] == "INVALIDATED"
    trace = invalid["candidate_trace_obstruction"]
    assert trace["status"] == "INVALIDATED"
    assert trace["contradicted_by_exact_stationary_witness_trace_288"] is True
    assert block["PSD_feasibility_certified"] is False
    assert block["PSD_infeasibility_certified"] is False


def test_heavy_request_recomputes_diagnostic_but_keeps_solver_closed(
    monkeypatch,
) -> None:
    diagnostic = {
        "n_failed": 0,
        "proof_grade": False,
        "corrected_common_kernel": {"rank": 448, "nullity": 0},
        "certified_no_go": False,
        "certified_PSD_feasibility": False,
    }
    monkeypatch.setattr(
        audit.corrected_kernel_source,
        "corrected_common_kernel_diagnostic",
        lambda: diagnostic,
    )
    heavy = audit.run_heavy_recomputation(max_iterations=1)
    assert heavy["status"] == (
        "CORRECTED_COMMON_KERNEL_RECOMPUTED__SDP_SOLVER_BLOCKED"
    )
    assert heavy["executed"] is True
    assert heavy["dense_Hessians_assembled"] is True
    assert heavy["solver_started"] is False
    assert heavy["proof_grade"] is False
    assert heavy["corrected_common_kernel_diagnostic"] == diagnostic
    assert heavy["PSD_feasibility_certified"] is False
    assert heavy["PSD_infeasibility_certified"] is False
    report = audit.build_report(recompute_heavy=True, max_iterations=1)
    assert report["overall_state"] == "OPEN"
    assert report["n_failed"] == 0
    assert report["heavy_recomputation"] == heavy


def test_report_rejects_selected_global_vacuum_without_excluding_model() -> None:
    report = audit.build_report()
    assert report["status"] == (
        "G3_SELECTED_VACUUM_REJECTED_BY_EXACT_GLOBAL_COUNTEREXAMPLE"
    )
    assert report["overall_state"] == "OPEN"
    assert report["n_failed"] == 0, report["failures"]
    flags = report["flags"]
    assert flags["G3_numerical_rank13_stationarity_family_constructed"] is True
    assert flags["G3_exact_informed_13_row_constraints_ready"] is True
    assert flags["legacy_stationary_family_numerics_invalidated"] is True
    assert flags["exact_three_structural_zero_gradient_certificates"] is True
    assert flags["stationarity_rank_lower_bound_13_exactly_certified"] is True
    assert flags["stationarity_rank_upper_bound_13_only_numerical"] is False
    assert flags["stationarity_rank_upper_bound_13_exactly_certified"] is True
    assert flags["stationarity_rank_13_exactly_certified"] is True
    assert flags["stationarity_nullity_38_exactly_certified"] is True
    assert flags["G3_stationary_nullspace_certified"] is False
    assert flags["exact_P24_structural_certificate"] is True
    assert flags["exact_stationary_witness_trace_288"] is True
    assert flags[
        "exact_H6_radial_nonflat_stationary_witness_certified"
    ] is True
    assert flags[
        "legacy_reference_equilibrated_common_kernel_135_invalidated"
    ] is True
    assert flags[
        "corrected_common_kernel_rank448_nullity0_numerical_only"
    ] is True
    assert flags["corrected_common_kernel_proof_grade"] is False
    assert flags["corrected_common_kernel_recomputed_this_invocation"] is False
    assert flags["exact_SO10_orbit_rank_36_certified"] is True
    assert flags["exact_gauge_orbit_rank_37_certified"] is True
    assert flags[
        "gauge_quotient_dimension_449_including_axion_certified"
    ] is True
    assert flags["exact_full_symmetry_orbit_rank_38_certified"] is True
    assert flags[
        "massive_transverse_quotient_dimension_448_certified"
    ] is True
    assert flags["G3_massive_transverse_projection_basis_constructed"] is True
    assert flags["G3_corrected_physical_quotient_constructed"] is True
    assert flags["physical_quotient_dimension_448_certified"] is True
    assert flags["G3_fixed_vacuum_strict_minimum_certified"] is True
    assert flags["G3_fixed_vacuum_PSD_feasible_certified"] is True
    assert flags["G3_fixed_vacuum_no_go_certified"] is False
    assert flags["G3_selected_vacuum_global_no_go_certified"] is True
    assert flags["exact_lower_energy_field_witness_certified"] is True
    assert flags["constructive_candidate_rejected_for_G3"] is True
    assert flags["complete_potential_BFB"] is True
    assert flags["global_competing_extrema_exhausted"] is False
    assert flags["G3_closed"] is False
    assert flags["whole_model_validated"] is False
    assert flags["whole_model_excluded"] is False


def test_dimension_six_locking_operator_is_not_overclaimed_as_a_rescue() -> None:
    boundary = audit.build_report()["dimension_six_boundary"]
    assert (
        boundary["included_in_renormalizable_44_direction_51_parameter_pencil"]
        is False
    )
    facts = boundary["exact_selected_vacuum_facts"]
    assert facts["P54_DeltaR_DeltaR"] == 0.0
    assert facts["selected_H10_H10_mass_block"] == 0.0
    assert facts["selected_phase_curvature"] == 0.0
    assert facts["phase_vector_is_parallel_to_lambda4"] is True
