from fractions import Fraction

import numpy as np

import exact_gauged_u1x_g3_kernel_quartic_bound_v20 as gate


def test_exact_30_complex_mixed_kernel_source_binding() -> None:
    kernel = gate.exact_kernel_embedding()
    assert kernel["two_by_two_block_structure_exact"] is True
    assert kernel["active_coordinate_count"] == 60
    assert kernel["zero_coordinate_count"] == 66
    assert kernel["plus_two_eigenspace_dimension"] == 30
    assert kernel["minus_two_eigenspace_dimension"] == 30
    assert kernel["zero_eigenspace_dimension"] == 66
    assert kernel["simultaneous_kernel_complex_dimension"] == 30
    assert kernel["simultaneous_kernel_real_dimension"] == 60
    assert kernel["M_minus_2_embedding_max_abs_residual"] == 0
    assert kernel["C_P_embedding_max_abs_residual"] == 0
    assert np.array_equal(kernel["embedding_gram"], 2 * np.eye(30, dtype=int))


def test_exact_PS_recoupling_and_sharp_SOS_identity() -> None:
    proof = gate.exact_recoupling_certificate()
    assert proof["pair_dimension_sum"] == 465
    assert proof["all_fraction_sums_one"] is True
    assert proof["crossing_identity_exact_on_all_PS_rows"] is True
    assert proof["SOS_identity_exact_on_all_PS_rows"] is True
    assert proof["original_sharp_lower_bound"] == Fraction(33, 32)
    rows = proof["rows"]
    assert rows["A_(35,1,5)"]["original_W_eigenvalue"] == Fraction(17, 16)
    assert rows["B35_(35,1,1)"]["original_W_eigenvalue"] == 1
    assert rows["B100_(20prime,1,5)"]["original_W_eigenvalue"] == 1
    assert rows["C_(45,1,3)"]["original_W_eigenvalue"] == Fraction(209, 144)
    assert rows["D_(20prime,1,1)"]["original_W_eigenvalue"] == Fraction(395, 224)


def test_exact_coherent_pure_2772bar_swapped_weight_witness() -> None:
    witness = gate.exact_coherent_swapped_witness()
    assert witness["norm_squared"] == 16
    assert witness["nonzero_coordinate_count"] == 16
    assert witness["canonical_reconstruction_residual_support"] == ()
    assert witness["minus_i_hodge_residual_support"] == ()
    assert witness["M_P_minus_2_max_abs_residual"] == 0
    assert witness["C_P_max_abs_residual"] == 0
    assert witness["projector_fractions_54_1050bar_2772bar_4125"] == {
        "54": Fraction(0),
        "1050bar": Fraction(0),
        "2772bar": Fraction(1),
        "4125": Fraction(0),
    }
    assert witness["original_weighted_quartic"] == Fraction(17, 16)
    assert witness["swapped_weighted_quartic"] == 1


def test_weight_swap_fails_to_rescue_Delta_R() -> None:
    report = gate.build_report()
    swap = report["swapped_weight_rescue_audit"]
    assert report["n_failed"] == 0
    assert report["flags"]["original_33_over_32_equality_witness_source_bound"] is True
    assert report["flags"]["sharp_kernel_bound_live_generator_reconstruction"] is False
    assert report["flags"]["original_equality_single_PS_phase_orbit_certified"] is False
    assert report["flags"]["swapped_weight_lower_bound_exactly_one"] is True
    assert report["flags"]["simple_2772_4125_weight_swap_rescues_Delta_R"] is False
    assert report["flags"]["G3_closed"] is False
    assert report["flags"]["fixed_P_branch_closed_negative"] is True
    assert swap["sharp_kernel_minimum"] == 1
    assert swap["Delta_R_swapped_weighted_quartic"] == Fraction(49, 48)
    assert swap["coherent_beats_Delta_R_by"] == Fraction(1, 48)
    assert swap["coherent_beats_prior_witness_by"] == Fraction(1, 32)


def test_exact_fixed_P_strict_local_global_no_go() -> None:
    theorem = gate.exact_fixed_P_local_global_no_go()
    assert theorem["exact_X_parameter_count_evaluated"] == 51
    assert theorem["number_of_zero_value_differences"] == 49
    assert theorem["number_of_nonzero_value_differences"] == 2
    assert theorem["nonzero_value_difference_coefficients_over_r4"] == {
        "lambda::O27_B03_126bar_self_projectors": Fraction(-1, 6),
        "lambda::O27_B04_126bar_self_projectors": Fraction(1, 6),
    }
    assert theorem["gap_equals_minus_one_eighth_curvature_exact"] is True
    assert theorem["current_lambda_2772"] == Fraction(17, 128)
    assert theorem["current_lambda_4125"] == Fraction(1, 8)
    assert theorem["current_same_norm_gap_over_r4"] == Fraction(-1, 768)
    assert theorem["current_twofold_curvature_over_r2"] == Fraction(1, 96)
    assert theorem["current_identity_exact"] is True
    assert theorem["tangent_Hessian_signatures_source_bound"] is True
    tangents = theorem["explicit_multiplicity_two_tangents"]
    assert tangents["both_tangents_orthonormal_after_dividing_by_sqrt8"] is True
    assert tangents["both_tangents_have_expected_signature"] is True
    assert tangents["both_tangents_in_exact_mixed_kernel"] is True
    assert theorem["selected_P_plus_Delta_R_strict_local_and_global_possible"] is False
