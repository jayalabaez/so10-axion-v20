from __future__ import annotations

import math
import os

import pytest

import gauged_u1x_g3_sos_candidate_v20 as candidate


def test_sparse_candidate_is_bound_to_the_exact_x_parameter_contract() -> None:
    scales = candidate.hierarchy_scales()
    coefficients = candidate.full_coefficient_vector(scales)
    symbolic = candidate.symbolic_nonzero_coefficients()
    assert len(coefficients) == 51
    assert set(symbolic) <= set(coefficients)
    assert sum(value != 0.0 for value in coefficients.values()) == 27
    assert max(abs(value) for value in coefficients.values()) == pytest.approx(73 / 8)
    assert max(abs(value) for value in coefficients.values()) < 4 * math.pi


def test_candidate_records_exact_rational_structure_and_non_wlog_anchor() -> None:
    report = candidate.build_report()
    coefficients = report["coefficient_vector"]["evaluated_all_51"]
    assert coefficients["lambda::O48_B01_Phi_self_quartics"] == pytest.approx(
        -21 / 200
    )
    assert report["checks"]["historical_positive_J0_anchor_excludes_candidate"]
    assert not report["flags"][
        "positive_J0_normalization_is_without_loss_of_generality"
    ]
    assert candidate.A_SQUARED_RECOUPLING == (40, 72, 28, -8, -12, 12)
    assert candidate.TOTAL_MIXED_RECOUPLING == (41, 73, 29, -7, -11, 13)
    assert report["checks"]["exact_A_square_recoupling_is_source_bound"]
    assert report["flags"]["A_square_recoupling_exactly_source_bound"]


def test_boundedness_and_stationarity_are_exact_without_G3_overclaim() -> None:
    report = candidate.build_report()
    assert report["n_failed"] == 0
    assert report["boundedness_decomposition"]["conditional_global_lower_bound"] < 0
    flags = report["flags"]
    assert flags["manifest_BFB_decomposition_candidate_constructed"]
    assert flags["complete_potential_BFB_exactly_certified"]
    assert flags["selected_vacuum_stationarity_exactly_compiler_certified"]
    assert not flags["selected_vacuum_global_minimum_certified"]
    assert flags["selected_vacuum_global_minimum_disproved"]
    assert not flags["selected_vacuum_unique_modulo_symmetry"]
    assert flags["exact_lower_energy_field_witness_certified"]
    assert flags["constructive_candidate_rejected_for_G3"]
    assert flags["full_448_PSD_feasibility_certified"]
    assert flags["strict_local_minimum_certified"]
    assert not flags["G3_closed"]


def test_exact_symmetry_scope_is_36_plus_1_plus_1() -> None:
    quotient = candidate.build_report()["symmetry_quotient"]
    assert quotient["SO10_broken_rank"] == 36
    assert quotient["SO10_plus_U1X_rank"] == 37
    assert quotient["SO10_plus_U1X_plus_global_PQ_rank"] == 38
    assert quotient["massive_transverse_dimension"] == 448


def test_direct_exact_rank_certificate_promotes_only_local_claims() -> None:
    report = candidate.build_report()
    certificate = report["exact_rank_certificate"]
    assert report["conditional_exact_rank_certificate"] is certificate
    ranks = certificate["direct_exact_ranks"]
    assert certificate["n_failed"] == 0
    assert ranks["H_Phi_plus_K"] == {
        "rank": 429,
        "nullity": 33,
        "PSD": True,
    }
    assert certificate["exact_full_kernel_argument"]["exact_full_Hessian_rank"] == 448
    flags = report["flags"]
    assert not flags["P_plus_Delta_Qsqrt2_component_LDL_conditional"]
    assert not flags["full_448_kernel_count_conditional"]
    assert flags["P_plus_Delta_source_binding_exactly_certified"]
    assert flags["full_448_kernel_count_exact"]
    assert flags["full_448_PSD_feasibility_certified"]
    assert flags["strict_local_minimum_certified"]
    assert not flags["selected_vacuum_global_minimum_certified"]
    assert flags["selected_vacuum_global_minimum_disproved"]
    assert not flags["selected_vacuum_unique_modulo_symmetry"]
    assert not flags["G3_closed"]


def test_exact_global_gap_gate_rejects_only_the_selected_candidate() -> None:
    report = candidate.build_report()
    witness = report["exact_global_counterexample_certificate"]
    assert witness["n_failed"] == 0
    assert witness["flags"]["lower_energy_field_witness_exactly_certified"]
    assert witness["flags"]["selected_vacuum_global_minimum_disproved"]
    assert report["flags"]["constructive_candidate_rejected_for_G3"]
    assert not report["flags"]["whole_model_excluded"]


@pytest.mark.skipif(
    os.environ.get("RUN_HEAVY_G3_SOS_CANDIDATE") != "1",
    reason="set RUN_HEAVY_G3_SOS_CANDIDATE=1 for the dense 486-real recomputation",
)
def test_live_compiler_candidate_recomputation_is_numerical_only() -> None:
    heavy = candidate.run_heavy_recomputation()
    assert heavy["parameter_rows_assembled"] == 28
    assert heavy["nonzero_parameter_count"] == 27
    assert heavy["compiler_gradient_max_abs_residual"] < 1.0e-12
    assert heavy["P_plus_Delta"]["gauge_rank"] == 33
    assert heavy["P_plus_Delta"]["quotient_dimension"] == 429
    assert heavy["P_plus_Delta"]["minimum_eigenvalue"] > 0.0
    assert heavy["full_massive_transverse"]["dimension"] == 448
    assert not heavy["full_massive_transverse"]["strict_local_minimum_certified"]
    assert not heavy["full_massive_transverse"]["PSD_feasibility_certified"]
