import math

import exact_gauged_u1x_g3_su5_delta_hsx_extension_v20 as audit


def test_old_real_h_alignment_does_not_vanish():
    row = audit.exact_phi_h_chiral_square_certificate()
    assert row["old_square_at_F_H_equals_e6"] == audit.Fraction(3, 5)
    assert not row["old_square_vanishes_at_real_H"]
    assert row["source_binding_exact"]


def test_real_h_no_go_includes_complete_exact_x_h_portal_scope():
    row = audit.real_h_exact_no_go_certificate()
    for family in ("O06", "O12", "O15", "O28", "O31", "O35", "O36", "O38", "O45", "O46"):
        assert family in row["scope"]
    assert row["linear_and_chiral_portal_zero_jets"]["source_binding_exact"]
    assert row["O35_45_signature"] == {"negative": 6, "zero": 8, "positive": 6}
    assert row["block_determinant"] == "-c^2"
    assert not row["strict_transverse_minimum_with_real_H_possible"]
    assert row["source_binding_exact"]


def test_chiral_hodge_square_and_exact_symmetry_rank():
    square = audit.exact_phi_h_chiral_square_certificate()
    orbit = audit.exact_orbit_rank_certificate()
    assert square["deterministic_all_component_identity_residual"] == 0.0
    assert square["F_chiral_operator_rank"] == 5
    assert square["F_chiral_operator_Hchi_residual"] < 1e-12
    assert orbit["SO10_rank"] == 36
    assert orbit["SO10_plus_U1X_rank"] == 37
    assert orbit["SO10_plus_U1X_plus_PQ_rank"] == 38
    assert orbit["physical_quotient_dimension"] == 448
    assert orbit["source_binding_exact"]


def test_candidate_coefficient_map_is_exact_x_and_below_4pi():
    symbolic = audit.symbolic_coefficient_map()
    numerical = audit.numerical_coefficient_map()
    contract = set(audit.g2_audit.contract_selection()["parameter_ids"])
    assert len(symbolic) == len(numerical) == 28
    assert set(symbolic) <= contract
    assert numerical["lambda::O36_B01_H_self_quartics"] == 11.0
    assert numerical["lambda::O35_B02_H_Sigma_hermitian"] == 1.0 / 20.0
    assert max(abs(value) for value in numerical.values()) == 11.0
    assert 11.0 < 4.0 * math.pi


def test_hsigma_projector_bound_and_fixed_orientation_test():
    bound = audit.exact_hsigma_current_bound_certificate()
    fierz = bound["exact_coefficient_certificate"]
    fixed = audit.fixed_pd_equal_norm_h_orientation_certificate()
    assert bound["deterministic_source_residual"] < 1e-8
    assert fierz["Gaussian_lattice_residual"] == 0.0
    assert fierz["twice_injection_Gram_is_12I_exact"]
    assert fierz["raw_Sigma_basis_Gram_is_2I_exact"]
    assert fierz["H_generators_are_real_skew_exact"]
    assert fierz["Sigma_generators_are_antihermitian_exact"]
    assert fierz["integer_coefficient_identity_max_abs_residual"] == 0
    assert fierz["all_126_squared_by_10_squared_coefficients_exact"]
    assert fierz["source_binding_exact"]
    assert bound["beta_squared_less_than_4t_exact"]
    assert bound["homogeneous_quartic_BFB_certified"]
    assert not bound["finite_field_global_gap_certified"]
    assert fixed["all_nonnegative"]
    assert fixed["smallest_positive_eigenvalue"] == audit.Fraction(1, 500)
    assert not fixed["lower_equal_norm_H_orientation_found"]


def test_full_positive_f_mixed_kernel_gap_and_signed_f_branch():
    row = audit.fixed_f_mixed_kernel_global_certificate()
    source = row["source_audit"]
    assert row["mixed_kernel_complex_dimension"] == 10
    assert source["positive_F_rank_mod_5"] == 116
    assert source["positive_F_explicit_kernel_annihilation_exact"]
    assert source["positive_F_explicit_kernel_gram_is_8I_exact"]
    assert source["desired_chirality_wedge_coefficient_identity_exact"]
    assert source["chirality_cross_coefficient_tensor_zero_exact"]
    assert source["negative_F_rank_mod_5"] == 126
    assert source["negative_F_mixed_kernel_complex_dimension"] == 0
    assert row["negative_F_mixed_zero_equality_branch_excluded"]
    assert row["global_gap_nonnegative_on_entire_fixed_F_mixed_kernel"]
    assert row["equality_is_one_SU5_orbit"]
    assert not row["lower_witness_on_this_full_kernel"]
    assert row["proof_grade"]


def test_beta_free_all_vanishing_affine_sos_route_is_exactly_excluded():
    row = audit.exact_positive_affine_sos_replacement_no_go_certificate()
    assert row["all_portal_parameters_in_51_parameter_contract"]
    assert all(
        portal["charges"] == {"PQ": 0, "X": 0, "Z17": 0}
        for portal in row["exact_X_portals"].values()
    )
    assert row["O12_scalar_obstruction"]["target_H_dot_H"] == 0j
    assert row["O12_scalar_obstruction"]["H_dot_H_identically_zero_on_chiral_C5"]
    assert row["O15_O38_126_residual_obstruction"]["Phi_contract_Delta_norm"] == 0.0
    assert row["O15_O38_126_residual_obstruction"]["inner_HwedgePhi_Delta"] == 0j
    assert row["O45_210_1050_residual_obstruction"][
        "maximum_source_target_residual"
    ] < 1e-12
    assert row["targeted_G2_gradient_audit"]["gradient_column_rank"] == 6
    assert not row["all_vanishing_positive_affine_SOS_can_replace_beta"]
    assert not row["nonvanishing_residual_gradient_cancellation_construction_excluded"]
    assert row["proof_grade"]


def test_recorded_live_full_hessian_is_strict_on_448_quotient():
    row = audit.RECORDED_LIVE_HESSIAN
    assert row["full_gradient_max_abs_residual"] < 1e-10
    assert row["numerical_symmetry_orbit_rank"] == 38
    assert row["transverse_dimension"] == 448
    assert row["minimum_transverse_eigenvalue"] > 1e-4
    assert row["negative_transverse_eigenvalues_below_minus_1e_minus_9"] == 0
    assert row["zero_transverse_eigenvalues_at_1e_minus_9"] == 0
    assert row["strict_local_minimum_high_confidence_numeric"]
    assert not row["strict_local_minimum_proof_grade"]


def test_report_is_fail_closed_on_global_g3_claim():
    report = audit.build_report()
    assert report["n_failed"] == 0
    assert report["status"] == (
        "EXACT_REAL_H_NO_GO__CHIRAL_H_STRICT_LOCAL_CANDIDATE__GLOBAL_GAP_OPEN"
    )
    assert report["flag"]["real_H_e6_extension_exactly_excluded"]
    assert report["flag"]["chiral_H_exact_stationary_candidate_constructed"]
    assert report["flag"]["strict_448_quotient_local_minimum_high_confidence_numeric"]
    assert report["global_status"]["positive_F_full_mixed_kernel_gap_exact"]
    assert report["global_status"]["negative_F_mixed_zero_kernel_dimension"] == 0
    assert report["global_status"][
        "all_vanishing_affine_SOS_beta_replacement_excluded"
    ]
    assert not report["flag"]["full_global_minimum_certified"]
    assert not report["flag"]["G3_closed"]
    assert not report["flag"]["whole_model_excluded"]
