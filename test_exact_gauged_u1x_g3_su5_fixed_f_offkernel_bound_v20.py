import numpy as np

import exact_gauged_u1x_g3_su5_fixed_f_offkernel_bound_v20 as audit


def test_source_matrices_are_exact_gaussian_hermitian_sources():
    source = audit.exact_source_matrices()
    assert source["A_real"].shape == (136, 126)
    assert source["A_imaginary"].shape == (136, 126)
    for prefix in ("mixed_gram", "plus_scaled"):
        real = source[f"{prefix}_real"]
        imaginary = source[f"{prefix}_imaginary"]
        assert real.dtype == np.int64
        assert imaginary.dtype == np.int64
        assert np.array_equal(real, real.T)
        assert np.array_equal(imaginary, -imaginary.T)
    assert source["current_scaled_integrality_residual"] == 0.0


def test_exact_mixed_gap_polynomial_and_kernel_rank():
    row = audit.exact_mixed_gap_certificate()
    polynomial = row["polynomial_certificate"]
    assert row["raw_spectral_roots"] == audit.MIXED_RAW_ROOTS
    assert row["normalized_positive_spectral_gap_lower_bound"] == audit.Fraction(6, 5)
    assert row["kernel_complex_dimension"] == 10
    assert row["exact_kernel_rank_certificate"] == 116
    assert polynomial["all_primes_verified"]
    assert polynomial["CRT_modulus_exceeds_twice_bound"]
    assert polynomial["all_modular_residuals_zero"]
    assert polynomial["exact_matrix_polynomial_annihilation"]
    assert row["proof_grade"]


def test_exact_pure_hplus_current_bound_polynomial():
    row = audit.exact_plus_current_error_bound_certificate()
    polynomial = row["polynomial_certificate"]
    assert row["annihilating_polynomial_roots"] == audit.PLUS_SCALED_ROOTS
    assert min(row["annihilating_polynomial_roots"]) == 0
    assert polynomial["roots_distinct_and_nonnegative"]
    assert polynomial["CRT_modulus_exceeds_twice_bound"]
    assert polynomial["all_modular_residuals_zero"]
    assert polynomial["exact_matrix_polynomial_annihilation"]
    assert row["constant_5_over_8_certified"]
    assert row["proof_grade"]


def test_cross_block_bound_is_source_bound_and_exact():
    row = audit.exact_cross_block_certificate()
    assert row["kernel_cross_block_zero_exact"]
    assert row["projector_identity_source_exact"]
    assert row["C_squared"] == audit.Fraction(25, 6)
    assert "b^2*(a-2*b)^2" in row["completion_of_square_identity"]
    assert row["proof_grade"]


def test_fixed_f_equality_is_source_bound_flag_orbit():
    row = audit.exact_fixed_f_equality_certificate()
    transitivity = row["constructive_SU5_transitivity_certificate"]
    assert all(row["exact_polynomial_source_checks"].values())
    assert all(transitivity["machine_checks"].values())
    assert transitivity["determinant_final_phase_exponent"] == 0
    assert transitivity["proof_grade"]
    assert row["S_Phi17_phase_charge_determinant"] == -68
    assert row["equality_is_one_SO10_x_U1X_x_PQ_orbit"]
    assert row["proof_grade"]


def test_rational_inside_outside_patch_margins():
    row = audit.exact_scalar_patch_certificate()
    inside = row["inside_box"]
    outside = row["outside_box"]
    assert inside["mixed_residual_coefficient_margin"] == audit.Fraction(467, 5760)
    assert inside["h_minus_coefficient_margin"] == audit.Fraction(23, 40)
    assert outside["u_at_least_11_over_10_boundary_margin"] == audit.Fraction(7, 4000)
    assert outside["u_halfspace_derivative_margin"] == audit.Fraction(187, 1000)
    assert outside["v_at_least_1_over_2_boundary_margin"] == audit.Fraction(207, 160000)
    assert outside["v_halfspace_derivative_margin"] == audit.Fraction(103, 1600)
    assert row["proof_grade"]


def test_report_closes_only_the_full_fixed_f_subproblem():
    report = audit.build_report()
    assert report["n_failed"] == 0
    assert report["status"] == "EXACT_FIXED_F_FULL_OFFKERNEL_BETA_GAP_CERTIFIED"
    assert report["overall_state"] == "CLOSED_FIXED_F_GLOBAL_SUBPROBLEM"
    assert report["checks"]["cross_block_bound_exact"]
    assert report["checks"]["full_fixed_F_equality_orbit_exact"]
    assert report["scope"]["global_gap_nonnegative_on_full_fixed_F_stratum"]
    assert report["scope"]["equality_is_selected_SU5_flag_orbit"]
    assert not report["scope"]["arbitrary_Phi_proved"]
    assert not report["scope"]["G3_closed"]
