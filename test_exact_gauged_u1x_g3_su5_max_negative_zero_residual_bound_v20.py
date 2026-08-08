from fractions import Fraction

import exact_gauged_u1x_g3_su5_max_negative_zero_residual_bound_v20 as bound


def test_live_affine_source_has_exact_rank_and_kernel_split() -> None:
    source = bound.exact_affine_constraint_source()
    kernel = bound.exact_kernel_decomposition_certificate()
    assert source["matrix_shape"] == (776, 210)
    assert source["chiral_integrality_residual"] == 0.0
    assert source["particular_solution_residual_max_abs"] == 0
    assert kernel["exact_rank"] == 168
    assert kernel["exact_nullity"] == 42
    assert kernel["K0_no_01_indices_dimension"] == 35
    assert kernel["K2_both_01_indices_dimension"] == 7
    assert kernel["kernel_basis_has_no_one_01_index_entries"] is True
    assert kernel["z0_dot_full_kernel_max_abs"] == 0
    assert kernel["central_contraction_identities_computed_exactly"] is True
    assert not any(kernel["central_contraction_identity_residuals"].values())
    assert kernel["proof_grade"] is True


def test_live_hsx_pd_coefficients_and_chiral_normalization_are_bound() -> None:
    live = bound.live_hsx_coefficient_binding_certificate()
    assert live["live_symbolic_sigma_quartic_coefficients"] == {
        "O27_B03": Fraction(1, 8),
        "O27_B04": Fraction(1, 8),
    }
    assert live["live_selected_sigma_norm_squared"] == Fraction(1, 25)
    assert live["live_beta_coefficient"] == Fraction(1, 20)
    assert live["live_H_norm_coefficient"] == Fraction(-2)
    assert live["live_H_self_coefficients_O36_B01_B02"] == (
        Fraction(11),
        Fraction(1),
    )
    assert live["live_chiral_coefficients_O46_B01_B02_B03"] == (
        Fraction(3, 5),
        Fraction(1),
        Fraction(-1),
    )
    assert live["chiral_affine_row_norm_factor"] == Fraction(1, 40)
    assert live["PD_sigma_scale"] == Fraction(1, 8)
    assert live["PD_raw_F_norm_squared"] == 10
    assert live["PD_raw_mixed_M_eigenvalue"] == 8
    assert live["PD_source_reports"]["PD_n_failed"] == 0
    assert live["PD_source_reports"]["HSX_n_failed"] == 0
    assert live["proof_grade"] is True


def test_current_saturation_and_radial_minimum_are_exact() -> None:
    current = bound.exact_current_and_radial_certificate()
    assert current["raw_current"] == -16
    assert current["normalized_current"] == Fraction(-1)
    assert current["current_lower_bound_saturated"] is True
    assert current["Sigma_self_residuals_zero"] is True
    assert current["global_minimizer"] == {
        "u": Fraction(1001, 995),
        "v": Fraction(48, 199),
    }
    assert current["gradient_at_minimizer"] == {
        "du": Fraction(0),
        "dv": Fraction(0),
    }
    assert current["global_minimum"] == Fraction(-7001, 995000)
    assert current["normalized_affine_stratum_domain"] == "u>0 and v>0"
    assert current["raw_H_norm_squared"] == 2
    assert current["raw_Sigma_norm_squared"] == 8
    assert current["raw_current_imaginary_abs"] == 0
    assert current["radial_boundaries"]["u_equals_zero_lower_bound"] == 1
    assert current["radial_boundaries"]["v_equals_zero_lower_bound"] == Fraction(
        1, 5000
    )
    assert current["proof_grade"] is True


def test_phi_coercive_bound_and_strict_margin_are_exact() -> None:
    particular = bound.exact_particular_phi_certificate()
    phi_bound = bound.exact_phi_coercive_bound_certificate()
    assert particular["N_Phi"] == Fraction(4, 5)
    assert particular["I54_Phi"] == Fraction(2, 125)
    assert particular["I4125_Phi"] == Fraction(8, 45)
    assert particular["complete_Phi_SOS_gap_at_particular_solution"] == Fraction(
        263, 1125
    )
    assert phi_bound["polynomial_identity_exact"] is True
    assert phi_bound["I54_exact_sample_basis_determinant"] != 0
    assert phi_bound["I54_sample_identity_max_abs_residual"] == "0"
    assert phi_bound["trace_5C_minus_2N_identity_residual"] == 0
    assert phi_bound["traceless_diagonal_Cauchy_coefficient"] == Fraction(5, 2)
    assert phi_bound["I54_diagonal_lower_bound_coefficient"] == Fraction(1, 560)
    assert phi_bound["lower_bound"] == Fraction(1, 141)
    assert phi_bound["proof_grade"] is True
    assert (
        bound.PHI_ANGULAR_LOWER_BOUND + bound.RADIAL_CURRENT_MINIMUM
        == bound.FINAL_STRATUM_MARGIN
        == Fraction(7859, 140295000)
    )


def test_report_closes_only_the_max_negative_all_zero_stratum() -> None:
    report = bound.build_report()
    assert report["status"] == (
        "EXACT_PURE_DELTA_MAX_NEGATIVE_MIXED_ZERO_ROUTE_EXCLUDED"
    )
    assert report["overall_state"] == (
        "CLOSED_PURE_DELTA_MAX_NEGATIVE_MIXED_ZERO_STRATUM__ARBITRARY_PHI_OPEN"
    )
    assert report["n_failed"] == 0
    assert report["scope"]["strongest_all_zero_max_negative_route_excluded"]
    assert report["scope"][
        "strongest_pure_Delta_mixed_zero_max_negative_route_excluded"
    ]
    assert report["scope"]["normalized_affine_stratum_requires_u_gt_0_v_gt_0"]
    assert report["scope"]["u_zero_and_v_zero_boundaries_closed_separately"]
    assert report["scope"]["nonzero_residual_cancellations_excluded"] is False
    assert report["scope"]["arbitrary_Phi_global_gap_proved"] is False
    assert report["scope"]["G3_closed"] is False
