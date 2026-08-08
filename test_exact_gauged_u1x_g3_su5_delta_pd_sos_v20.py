"""Regression tests for the exact SU(5)-singlet + Delta_R SOS candidate."""

from fractions import Fraction

import exact_gauged_u1x_g3_su5_delta_pd_sos_v20 as certificate


def test_exact_certificate_passes_without_closing_full_g3() -> None:
    report = certificate.build_report()

    assert report["n_failed"] == 0
    assert report["status"] == "EXACT_SU5_DELTA_PD_GLOBAL_SOS_CANDIDATE_CERTIFIED"
    assert report["overall_state"] == "CLOSED_PD_SUBPROBLEM"
    assert report["scope"]["Phi_Sigma_global_minimum_exact"] is True
    assert report["scope"]["full_486_field_stationarity"] is False
    assert report["scope"]["G3_closed"] is False


def test_exact_su5_phi_and_delta_residuals_vanish() -> None:
    phi = certificate.exact_phi_projector_certificate()
    sigma = certificate.exact_sigma_certificate()

    assert phi["raw_norm_squared"] == 10
    assert phi["raw_projector_values"] == certificate.EXPECTED_PHI_PROJECTOR_VALUES_RAW
    assert phi["raw_projector_sum"] == 100
    assert phi["I54_exactly_zero"] is True
    assert phi["I4125_exactly_zero"] is True
    assert sigma["I54_exactly_zero"] is True
    assert sigma["I1050bar_exactly_zero"] is True
    assert sigma["weighted_quartic_at_Delta"] == Fraction(1)


def test_exact_mixed_squares_vanish_and_stabilizer_is_sm() -> None:
    mixed = certificate.exact_mixed_zero_certificate()
    stabilizer = certificate.exact_stabilizer_certificate()

    assert mixed["M_eigen_residual_max_abs"] == 0
    assert mixed["C_residual_max_abs"] == 0
    assert stabilizer["exact_rational_rank"] == 33
    assert stabilizer["exact_stabilizer_dimension"] == 12
    assert stabilizer["exact_stabilizer_dimension"] == stabilizer["SM_dimension"]


def test_exact_t_eighth_pd_hessian_has_only_gauge_zero_modes() -> None:
    hessian = certificate.exact_pd_hessian_rank_certificate()

    assert hessian["physical_sigma_weight"] == "1/8"
    assert hessian["positive_Gram_decomposition"] is True
    assert hessian["exact_gauge_tangent_rank"] == 33
    assert hessian["gauge_kernel_component_max_abs_residual"] == {
        "Phi": 0,
        "Sigma": 0,
        "mixed": 0,
    }
    assert hessian["modular_certificate"]["prime_verified_by_trial_division"] is True
    assert hessian["modular_certificate"]["rank_over_Fp"] == 429
    assert hessian["rational_rank_upper_bound_from_kernel"] == 429
    assert hessian["exact_Hessian_rank"] == 429
    assert hessian["exact_Hessian_nullity"] == 33
    assert hessian["all_zero_modes_are_SO10_orbit_tangents"] is True
    assert hessian["strictly_positive_on_SO10_quotient"] is True
    assert hessian["local_equality_set_is_single_SO10_orbit"] is True
    assert hessian["global_equality_orbit_classification_complete"] is False
    assert hessian["proof_grade"] is True


def test_exact_x_coefficient_map_is_small_and_complete() -> None:
    report = certificate.build_report()
    coefficient = report["coefficient_map"]

    assert coefficient["nonzero_count"] == 17
    assert coefficient["missing_from_exact_X_contract"] == []
    assert coefficient["maximum_absolute_physical_coefficient"] == 73.0 / 8.0
    assert certificate.symbolic_coefficient_map()[
        "lambda::O44_B02_Phi2_Sigma_projectors"
    ] == "73/8"
