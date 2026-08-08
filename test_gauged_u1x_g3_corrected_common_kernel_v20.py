from __future__ import annotations

import os

import pytest

import gauged_u1x_g3_corrected_common_kernel_v20 as audit


def test_exact_H6_radial_stationary_witness_is_physical_and_nonflat() -> None:
    report = audit.exact_h6_radial_curvature_certificate()
    assert report["n_failed"] == 0, report["failures"]
    assert report["certified"] is True
    assert report["radial_coordinate_index"] == 222
    assert report["radial_coordinate_name"] == "H[6].x"
    assert not any(report["exact_symmetry_tangent_row"])
    assert report["invariant_restrictions"] == {
        "lambda::O06_B01_Hdag_H_norm": "t^2/2",
        "lambda::O36_B01_H_self_quartics": "t^4/40",
    }
    assert report["H_sector_coefficients"] == {
        "lambda::O06_B01_Hdag_H_norm": "-t^2 = -2 h^2",
        "lambda::O36_B01_H_self_quartics": "10",
    }
    assert report["anchored_extension"]["normalization_value"] == "1"
    assert report["anchored_extension"]["strictly_inside_4pi_box"] is True


def test_H6_witness_binds_to_actual_O06_O36_compiler_adapters() -> None:
    report = audit.compiler_h6_radial_binding()
    assert report["n_failed"] == 0, report["failures"]
    assert report["certified"] is True
    assert report["maximum_absolute_gradient_residual"] == 0.0
    assert report["observed_H6_radial_curvature"] == report["expected_2t2_curvature"]
    assert report["observed_H6_radial_curvature"] > 0.0
    assert report["H6_column_frobenius_norm"] == report["observed_H6_radial_curvature"]


def test_light_report_keeps_G3_open_and_does_not_fake_heavy_evidence() -> None:
    report = audit.build_report(recompute_heavy=False)
    assert report["n_failed"] == 0, report["failures"]
    assert report["overall_state"] == "OPEN"
    heavy = report["corrected_common_kernel_diagnostic"]
    assert heavy["status"] == "NOT_RECOMPUTED__USE_RECOMPUTE_HEAVY"
    assert heavy["executed"] is False
    recorded = report["recorded_common_kernel_regression"]
    corrected = recorded["corrected_raw_orthonormal_quotient"]
    assert corrected["field_congruence"] == "identity"
    assert corrected["common_Gram_rank"] == 448
    assert corrected["common_Gram_nullity"] == 0
    invalid = recorded["invalidated_reference_equilibration"]
    assert invalid["apparent_common_Gram_nullity_at_1e_minus_8"] == 135
    assert invalid["diagonal_scale_condition_ratio"] > 1.0e8
    assert invalid["scientific_use_for_G3"] is False
    flags = report["flags"]
    assert flags["legacy_common_kernel_dimension_135_invalidated"] is True
    assert flags["exact_H6_radial_flat_direction_refuted"] is True
    assert flags["corrected_common_kernel_full_rank_numerical_only"] is False
    assert flags[
        "corrected_common_kernel_rank_448_nullity_0_recorded_numerical_only"
    ] is True
    assert flags["G3_fixed_vacuum_strict_minimum_certified"] is False
    assert flags["G3_fixed_vacuum_no_go_certified"] is False
    assert flags["G3_closed"] is False


@pytest.mark.skipif(
    os.environ.get("RUN_GAUGED_U1X_G3_COMMON_KERNEL_HEAVY") != "1",
    reason="set RUN_GAUGED_U1X_G3_COMMON_KERNEL_HEAVY=1 for all dense Hessians",
)
def test_corrected_dense_common_kernel_has_no_numerical_physical_flat() -> None:
    report = audit.corrected_common_kernel_diagnostic()
    assert report["n_failed"] == 0, report["failures"]
    assert report["proof_grade"] is False
    corrected = report["corrected_common_kernel"]
    assert corrected["rank"] == 448
    assert corrected["nullity"] == 0
    assert corrected["common_Gram_min_eigenvalue"] > 1.0e-3
    assert corrected["common_Gram_max_eigenvalue"] < 2.0
    assert set(corrected["rank_across_relative_tolerances"].values()) == {448}
    legacy = report["invalidated_legacy_reference_equilibration"]
    assert legacy["scientific_use_for_G3"] is False
    assert legacy["diagonal_scale_condition_ratio"] > 1.0e6
    assert legacy["apparent_common_kernel_diagnostic"]["nullity"] > 0
    assert report["certified_no_go"] is False
    assert report["certified_PSD_feasibility"] is False
