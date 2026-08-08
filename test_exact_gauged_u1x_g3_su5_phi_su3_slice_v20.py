import exact_gauged_u1x_g3_su5_phi_su3_slice_v20 as su3_slice


def test_global_covariant_reduction_is_exact_on_complete_quartic_basis():
    reduction = su3_slice.build_report()["global_covariant_reduction"]
    assert reduction["complete_quartic_invariant_dimension"] == 4
    assert reduction["independent_exact_sample_count"] == 4
    assert reduction["sample_J_evaluation_determinant"] != 0
    assert reduction["I45_sample_identity_max_abs_residual"] == "0"
    assert reduction["I54_sample_identity_max_abs_residual"] == "0"
    assert reduction["global_consequence_of_I54_zero"] == "C=(2*N/5)*identity_10"


def test_displayed_basis_is_the_complete_su3_fixed_space():
    fixed = su3_slice.build_report()["SU3_fixed_space"]
    assert fixed["integral_generator_count"] == 8
    assert fixed["stacked_action_rank_mod_prime"] == 194
    assert fixed["exact_fixed_space_dimension"] == 16
    assert fixed["displayed_basis_rank_mod_prime"] == 16
    assert fixed["generator_times_basis_max_abs"] == 0
    assert fixed["basis_Gram_is_expected_diagonal"] is True
    assert fixed["displayed_basis_is_complete_fixed_space"] is True


def test_live_projectors_reduce_to_exact_45_quadrics():
    equations = su3_slice.build_report()["projector_equations"]
    assert equations["pair_monomial_count"] == 136
    assert equations["restricted_Gram_shape"] == (136, 136)
    assert equations["reduced_relation_count"] == 45
    assert equations["relation_rank_from_identity_pivot_block"] == 45
    assert equations["Gram_rank_mod_prime_lower_bound"] == 45
    assert equations["Gram_rowspace_identity_max_abs_residual"] == 0
    assert equations["exact_Gram_rowspace_equals_relation_rowspace"] is True


def test_real_sos_rows_remove_all_omega3_wedge_r4_directions():
    equations = su3_slice.build_report()["projector_equations"]
    assert equations["real_SOS_obstruction_rows"] == (24, 15, 29, 32, 34)
    assert equations["real_SOS_obstruction_rows_match"] is True
    assert equations["real_consequence"].startswith("ReOmega_e6=ImOmega_e6")


def test_remaining_real_locus_is_exactly_signed_kahler_in_the_slice():
    zero_locus = su3_slice.build_report()["real_zero_locus"]
    assert zero_locus["branch_plus"]["canonical_integer_solution_residual_max_abs"] == 0
    assert zero_locus["branch_minus"]["canonical_integer_solution_residual_max_abs"] == 0
    assert zero_locus["branch_plus"]["all_45_relations_mod_sphere_residual_max_abs"] == 0
    assert zero_locus["branch_minus"]["all_45_relations_mod_sphere_residual_max_abs"] == 0
    assert zero_locus["converse_derivation"]["necessary_and_sufficient_over_reals"] is True
    assert zero_locus["classified_nonzero_locus"] == "R^* SO(10).F"
    assert zero_locus["classified_unit_locus"] == "SO(10).F union SO(10).(-F)"


def test_su3_slice_closure_does_not_overclaim_global_g3():
    report = su3_slice.build_report()
    assert report["n_failed"] == 0
    assert report["overall_state"] == "SU3_FIXED_SLICE_CLOSED"
    assert report["scope"]["complete_16_real_dimensional_SU3_fixed_space_classified"] is True
    assert report["scope"]["all_arbitrary_real_four_forms_classified"] is False
    assert report["scope"]["disconnected_distant_components_excluded"] is False
    assert report["scope"]["corrected_signed_global_orbit_theorem_proved"] is False
    assert report["scope"]["G3_closed"] is False
