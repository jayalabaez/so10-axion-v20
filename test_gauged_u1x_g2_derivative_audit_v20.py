#!/usr/bin/env python3
"""Regression tests for the corrected gauged-U(1)_X G2 derivative audit."""
from __future__ import annotations

import os

import numpy as np
import pytest

import gauged_u1x_g2_derivative_audit_v20 as audit
import live_g2_canonical_486_field_chart_v20 as chart


def test_authoritative_selection_is_44_51_on_the_486_chart() -> None:
    selection = audit.contract_selection()
    assert selection["model_contract_id"] == "gauged_u1x_phi17_v20"
    assert selection["direction_count"] == 44
    assert selection["parameter_count"] == 51
    assert selection["real_field_dimension"] == 486
    assert len(selection["base_families"]) == 18
    assert len(set(selection["direction_ids"])) == 44
    assert len(set(selection["parameter_ids"])) == 51


def test_u1x_generator_rotates_every_complex_block_with_declared_charge() -> None:
    generator = audit.u1x_generator_matrix()
    assert generator.shape == (486, 486)
    assert np.array_equal(generator + generator.T, np.zeros_like(generator))
    assert np.count_nonzero(generator) == 276
    assert np.count_nonzero(generator[chart.PHI_SLICE, :]) == 0

    blocks = (
        (chart.H_SLICE, -2),
        (chart.SIGMA_SLICE, -2),
        (chart.S_SLICE, 4),
        (chart.X_SLICE, 17),
    )
    for block, charge in blocks:
        for real_index in range(block.start, block.stop, 2):
            imaginary_index = real_index + 1
            assert generator[real_index, imaginary_index] == -charge
            assert generator[imaginary_index, real_index] == charge


def test_u1x_tangent_matches_Tq_in_the_canonical_interleaved_chart() -> None:
    q = np.zeros(chart.TOTAL_DIM, dtype=float)
    q[chart.PHI_SLICE.start] = 3.0
    for block in (chart.H_SLICE, chart.SIGMA_SLICE, chart.S_SLICE, chart.X_SLICE):
        q[block.start] = 1.25
        q[block.start + 1] = -0.75
    state = chart.unpack(q)
    tangent = audit.u1x_tangent(state)
    assert tangent.shape == (486,)
    assert np.allclose(tangent, audit.u1x_generator_matrix() @ q)
    assert np.count_nonzero(tangent[chart.PHI_SLICE]) == 0
    assert np.linalg.norm(tangent[chart.X_SLICE]) > 0.0


def test_rank_policy_names_all_three_exact_structural_zero_columns() -> None:
    assert audit.ANALYTIC_ZERO_GRADIENT_PARAMETER_IDS == (
        "lambda::O27_B01_126bar_self_projectors",
        "lambda::O27_B02_126bar_self_projectors",
        "lambda::O44_B03_Phi2_Sigma_projectors",
    )
    assert audit.ANALYTIC_ZERO_GRADIENT_ATOL == 1.0e-27
    assert audit.NORMALIZED_RANK_TOLERANCE == 1.0e-10
    assert audit.EXPECTED_PROMOTED_STATIONARITY_RANK == 13
    assert audit.EXPECTED_PROMOTED_STATIONARITY_NULLITY == 38


def test_exact_delta_r_projector_zero_certificate_uses_gaussian_integers() -> None:
    certificate = audit.exact_delta_r_projector_zero_certificate()
    assert certificate["n_failed"] == 0, certificate["failures"]
    assert certificate["certified"] is True
    assert certificate["arithmetic_domain"].startswith("Gaussian integers Z[i]")
    assert certificate["canonical_basis_dimension"] == 126
    assert certificate["exact_delta_R"]["form_component_count"] == 16
    assert certificate["exact_delta_R"]["nonzero_coordinate_count"] == 8
    assert certificate["exact_delta_R"]["coordinate_integer_squared_norm"] == 8
    assert certificate["exact_generators"]["count"] == 45
    assert certificate["exact_generators"]["nonzero_entries"] == 3150
    assert certificate["Delta_R_pair"]["nonzero_entries"] == 64
    assert certificate["Delta_R_pair"]["annihilating_polynomial"] == (
        "(K-1)(K+5)=K^2+4K-5"
    )
    assert certificate["Delta_R_pair"]["annihilator_residual_nonzero_entries"] == 0
    assert certificate["Delta_R_pair"]["annihilator_residual_integer_squared_norm"] == 0

    projectors = certificate["projectors"]
    assert projectors["54"]["integer_polynomial_coefficients_low_to_high"] == [
        35,
        -33,
        -3,
        1,
    ]
    assert projectors["1050bar"][
        "integer_polynomial_coefficients_low_to_high"
    ] == [-75, 65, 11, -1]
    assert projectors["54"]["projected_pair_exactly_zero"] is True
    assert projectors["1050bar"]["projected_pair_exactly_zero"] is True
    assert projectors["4125"]["projected_pair_exactly_zero"] is False
    assert projectors["2772bar"]["projected_pair_exactly_zero"] is False
    assert all(
        row["projector_eigen_equation_exactly_satisfied"]
        for row in projectors.values()
    )
    assert certificate["projector_reconstruction"]["residual_nonzero_entries"] == 0
    assert certificate["parameter_channel_map"] == {
        "lambda::O27_B01_126bar_self_projectors": "54",
        "lambda::O27_B02_126bar_self_projectors": "1050bar",
    }
    assert certificate["gradient_implication"][
        "exact_projected_pair_zero_implies_full_real_gradient_zero"
    ] is True


def test_exact_sigma_basis_and_delta_r_are_bound_to_live_chart_conventions() -> None:
    certificate = audit.exact_sigma_chart_convention_certificate()
    assert certificate["n_failed"] == 0, certificate["failures"]
    assert certificate["certified"] is True
    assert certificate["basis_dimension"] == 126
    assert certificate["basis_mismatch_indices"] == []
    assert certificate["exact_Delta_R_kinetic_norm_squared"] == 8
    assert certificate["direct_Delta_R_normalization"] == (
        "exact unnormalized Delta_R / sqrt(8)"
    )
    assert certificate["direct_Delta_R_max_abs_component_residual"] == 0.0
    assert certificate["chart_Delta_R_max_abs_coordinate_residual"] == 0.0


def test_exact_phi210_projector_p24_and_stationary_witness_certificate() -> None:
    certificate = audit.exact_phi_projector_and_stationary_witness_certificate()
    assert certificate["n_failed"] == 0, certificate["failures"]
    assert certificate["certified"] is True
    zero = certificate["O44_B03_210_gradient_zero"]
    assert zero["parameter_id"] == "lambda::O44_B03_Phi2_Sigma_projectors"
    assert zero["integer_polynomial_coefficients_low_to_high"] == [
        0,
        258048,
        -152832,
        -32,
        8024,
        -1140,
        58,
        -1,
    ]
    assert zero["P210_pp_numerator_nonzero_entries"] == 0
    assert zero["P210_Delta_pair_numerator_nonzero_entries"] == 360
    assert zero["P210_Delta_pair_p_column_max_abs_entry"] == 0
    assert zero["P210_Delta_pair_p_row_max_abs_entry"] == 0
    assert zero["certified"] is True
    safety = certificate["integer_arithmetic_safety"]
    assert safety["certified"] is True
    assert safety["maximum_preflight_bound"] == 10517766144
    assert safety["maximum_preflight_bound"] < safety["signed_int64_maximum"]
    assert safety["Phi_generator_structure"] == {
        "generator_count": 45,
        "maximum_abs_generator_entry": 1,
        "maximum_nonzero_entries_per_generator_row": 1,
        "maximum_nonzero_entries_per_generator_column": 1,
        "active_generators_per_basis_row_minimum": 24,
        "active_generators_per_basis_row_maximum": 24,
        "maximum_simultaneous_contributions_per_pair_Casimir_output_entry": 24,
    }
    assert safety["P24_dense_operation_safety"]["certified"] is True
    assert certificate["P24"] == {
        "representation": "Phi210",
        "unbroken_sector": "C_SU3=20/3 and Q^2=0",
        "formula": "C6(C6-16I)(C6-36I)(I+Q^2)/3840, C6=6 C_SU3",
        "entry_domain": "(1/4) Z",
        "rank": 24,
        "trace": 24,
        "idempotence_exact": True,
    }
    witness = certificate["stationary_witness"]
    assert witness["gradient_exactly_zero"] is True
    assert witness["strictly_inside_4pi_box"] is True
    assert witness["P24_trace_coefficients"] == {
        "lambda::O07_B01_Phi_norm": 48,
        "lambda::O48_B01_Phi_self_quartics": 96,
        "lambda::O48_B02_Phi_self_quartics": 1152,
    }
    assert witness["P24_trace"] == 288


def test_int64_preflights_reject_unsafe_inputs_before_matrix_arithmetic() -> None:
    unsafe_pair = np.zeros(
        (chart.PHI_DIM, chart.PHI_DIM), dtype=object
    )
    unsafe_pair[0, 0] = audit._INT64_MAX // 24 + 1
    with pytest.raises(OverflowError, match="pair-Casimir preflight envelope"):
        audit._exact_phi_pair_casimir(unsafe_pair)

    outside_storage = np.asarray([[audit._INT64_MAX + 1]], dtype=object)
    with pytest.raises(OverflowError, match="outside signed int64"):
        audit._checked_int64_array(outside_storage, label="test input")


def test_exact_stationarity_certificate_proves_rank_13_nullity_38() -> None:
    certificate = audit.exact_stationarity_rank_lower_bound_certificate()
    assert certificate["row_count"] == 13
    assert certificate["column_count"] == 13
    assert certificate["determinant_nonzero"] is True
    assert certificate["certified_rank_lower_bound"] == 13
    assert certificate["exact_rank_upper_bound_certified"] is True
    assert certificate["exact_rank_13_certified"] is True
    assert certificate["exact_nullity_38_certified"] is True
    assert certificate["exact_rank_factorization"]["formula"] == (
        "A = L A[pivot_rows,:]"
    )


def test_so10_generator_matrices_reproduce_the_canonical_orbit() -> None:
    generators = audit.so10_generator_matrices()
    assert len(generators) == 45
    assert all(generator.shape == (486, 486) for generator in generators)
    assert max(np.max(np.abs(generator + generator.T)) for generator in generators) == 0.0
    state = audit.physical_hierarchy_state()
    q = chart.pack(state)
    matrix_orbit = np.column_stack([generator @ q for generator in generators])
    assert np.allclose(matrix_orbit, chart.gauge_orbit_matrix(state))


@pytest.mark.skipif(
    os.environ.get("RUN_GAUGED_U1X_G2_HEAVY") != "1",
    reason=(
        "set RUN_GAUGED_U1X_G2_HEAVY=1 to generate all 44 dense 486x486 "
        "Hessians"
    ),
)
def test_full_dense_gauged_u1x_g2_audit() -> None:
    report = audit.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["counts"]["invariant_directions"] == 44
    assert report["counts"]["real_parameters"] == 51
    assert report["counts"]["real_field_dimension"] == 486
    stationary = report["stationary_Hessian_bridge"]
    assert stationary["raw_dense_rank_diagnostic"]["rank"] == 14
    assert stationary["raw_dense_rank_diagnostic"]["certified"] is False
    assert stationary["promoted_stationarity_matrix"]["rank"] == 13
    assert stationary["promoted_stationarity_matrix"]["nullity"] == 38
    assert stationary["promoted_stationarity_matrix"][
        "exact_projector_zero_corrected_normalized_SVD_rank_13"
    ] is True
    assert stationary["promoted_stationarity_matrix"][
        "stationarity_rank_13_exactly_certified"
    ] is True
    assert stationary["promoted_stationarity_matrix"][
        "exact_nonzero_13x13_minor_certified"
    ] is True
    assert stationary["promoted_stationarity_matrix"][
        "exact_rank_lower_bound"
    ] == 13
    assert stationary["promoted_stationarity_matrix"][
        "exact_rank_upper_bound_certified"
    ] is True
    assert stationary["promoted_stationarity_matrix"][
        "exact_rank_certificate_missing"
    ] is False
    assert stationary["promoted_stationarity_matrix"][
        "stationarity_nullity_38_exactly_certified"
    ] is True
    assert stationary["promoted_stationarity_matrix"][
        "exact_compiler_minor_binding"
    ]["certified"] is True
    stable = stationary["promoted_stationarity_matrix"][
        "exact_informed_13_row_constraint_representation"
    ]
    assert stable["certified"] is True
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
    assert stable["rank"] == 13
    assert stable["nullity"] == 38
    assert 0.98 < min(stable["singular_values"])
    assert max(stable["singular_values"]) < 1.02
    assert stable["exact_stationary_witness_max_abs_residual"] == 0.0
    assert stationary["analytic_zero_promotion"]["symbolic_exact_zero_proof_present"] is True
    assert stationary["analytic_zero_promotion"]["exact_projector_zero_certificate"][
        "certified"
    ] is True
    assert stationary["analytic_zero_promotion"][
        "exact_phi_210_gradient_zero_certificate"
    ]["certified"] is True
    assert stationary["analytic_zero_promotion"][
        "raw_residue_magnitudes_are_not_used_for_zero_promotion"
    ] is True
    assert stationary["witness_source"] == "exact_rational_Phi_stationary_witness"
    assert stationary["raw_dense_stationarity_max_abs_residual"] == 0.0
    assert stationary["exact_stationary_witness_certificate"]["P24_trace"] == 288
    compiler_trace = stationary["exact_P24_trace_dense_compiler_binding"]
    assert compiler_trace["n_failed"] == 0, compiler_trace["failures"]
    assert compiler_trace["certified"] is True
    assert compiler_trace["compiler_P24_trace_coefficients"] == {
        "lambda::O07_B01_Phi_norm": 48.0,
        "lambda::O48_B01_Phi_self_quartics": 96.0,
        "lambda::O48_B02_Phi_self_quartics": 1152.0,
    }
    assert compiler_trace["compiled_witness_P24_trace"] == 288.0
    assert compiler_trace["compiled_witness_Hessian_max_abs_residual"] == 0.0
    assert report["flags"]["G2_gauged_u1x_derivatives_certified"] is True
    assert report["flags"]["exact_Delta_R_projector_zero_certificate"] is True
    assert report["flags"][
        "exact_projector_zero_corrected_normalized_SVD_rank_13"
    ] is True
    assert report["flags"]["stationarity_rank_13_exactly_certified"] is True
    assert report["flags"]["stationarity_nullity_38_exactly_certified"] is True
    assert report["flags"][
        "stationarity_rank_lower_bound_13_exactly_certified"
    ] is True
    assert report["flags"][
        "stationarity_rank_upper_bound_13_only_numerical"
    ] is False
    assert report["flags"][
        "stationarity_rank_upper_bound_13_exactly_certified"
    ] is True
    assert report["flags"][
        "compiler_gradients_bound_to_exact_nonzero_13x13_minor"
    ] is True
    assert report["flags"][
        "exact_informed_13_row_constraint_representation_ready"
    ] is True
    assert report["flags"]["exact_stationary_witness_regression_passes"] is True
    assert report["flags"][
        "exact_Sigma_conventions_bound_to_live_compiler_chart"
    ] is True
    assert report["flags"]["exact_Phi_int64_preflight_safety_certified"] is True
    assert report["flags"][
        "exact_P24_trace_288_bound_to_compiled_dense_Hessian"
    ] is True
    assert report["flags"]["promoted_rank_13_numerical_policy_reproduced"] is False
    assert report["Ward_identities"][
        "maximum_parameter_SO10_differentiated_Ward_relative_residual"
    ] < audit.WARD_RELATIVE_TOLERANCE
    assert report["flags"]["G3_closed"] is False
    assert report["flags"]["whole_model_validated"] is False
    assert report["flags"]["whole_model_excluded"] is False
