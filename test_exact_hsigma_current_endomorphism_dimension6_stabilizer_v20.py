from __future__ import annotations

from fractions import Fraction as Q

import exact_hsigma_current_endomorphism_dimension6_stabilizer_v20 as theorem


def test_exact_integer_sources_and_selected_spectrum() -> None:
    source = theorem.exact_integer_source_certificate()
    selected = theorem.exact_selected_operator_certificate()
    assert source["H_generators_real_skew_exact"]
    assert source["Sigma_generators_antihermitian_exact"]
    assert source["Delta_is_pair_34_kernel_vector_exact"]
    assert selected["K_H_Hermitian_exact"]
    assert selected["minimal_polynomial_zero_exact"]
    assert selected["exact_spectrum"] == {"-1": 35, "0": 56, "+1": 35}
    assert selected["K_H_Delta_R_zero_exact"]


def test_exact_six_real_flat_jacobian_and_chart_normalization() -> None:
    row = theorem.exact_six_flat_jacobian_certificate()
    assert row["number_of_real_flats"] == 6
    assert row["real_Jacobian_rank"] == 6
    assert row["selected_r"] == Q(1, 5)
    assert row["selected_gamma"] == Q(1, 20)
    assert row["selected_exact_Hessian_lift"] == Q(1, 500)
    assert row["matches_old_B02_flat_lift_exactly"]


def test_exact_global_plucker_restriction() -> None:
    row = theorem.exact_plucker_restriction_certificate()
    assert row["cleared_denominator"] == 32
    assert row["observed_nonzero_canonical_monomials"] == 12
    assert row["expected_nonzero_canonical_monomials"] == 12
    assert row["all_canonical_polynomial_coefficients_exact"]
    assert row["exact_global_identity"] == (
        "||K_H Sigma(z)||^2=||h||^2 ||h wedge z||^2"
    )
    assert "iff h wedge z=0" in row["zero_condition"]


def test_covariance_psd_and_realification_factor() -> None:
    row = theorem.exact_covariance_psd_and_uv_certificate()
    assert row["global_PSD"] == "gamma O6>=0 for gamma>=0"
    assert "(1/2)||A_real q||^2" in row["canonical_realification"]
    assert "gamma J_real^T J_real" in row["canonical_realification"]
    assert "negative coefficient" in row["UV_interpretation"]


def test_report_is_exact_and_fail_closed() -> None:
    report = theorem.build_report()
    assert report["closure_flags"]["dimension6_operator_exact"]
    assert report["closure_flags"]["six_beta0_quotient_flats_lifted"]
    assert report["closure_flags"]["plus_F_incident_flag_zero_preserved"]
    assert not report["closure_flags"]["full_486_Hessian_recompiled"]
    assert not report["closure_flags"]["renormalizable_UV_completion_proved"]
    assert not report["closure_flags"]["G3_closed"]
    assert not report["closure_flags"]["G4_closed"]
