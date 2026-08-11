import exact_gauged_u1x_g3_su5_equality_orbit_v20 as gate


def test_report_executes_without_internal_failures():
    report = gate.build_report()
    assert report["n_failed"] == 0
    assert report["overall_state"] == "GLOBAL_EQUALITY_ORBITS_CLOSED"
    assert report["status"] == (
        "EXACT_GLOBAL_EQUALITY_CLASSIFICATION__"
        "SIGNED_PHI_THEOREM_CLOSED__G3_OPEN"
    )


def test_fixed_f_sigma_equality_is_exactly_plucker_and_one_orbit():
    report = gate.build_report()
    kernel = report["fixed_F_mixed_kernel"]
    plucker = report["fixed_F_Plucker_classification"]
    assert kernel["exact_real_nullity"] == 20
    assert kernel["kernel_residual_max_abs"] == 0
    assert plucker["Pi54_response_max_abs"] == 0
    assert plucker["matrix_identity_max_abs_residual"] == 0
    assert plucker["fixed_F_Sigma_equality_is_one_orbit"] is True


def test_fixed_delta_tau_plus_sign_patterns_are_exactly_two_and_equivalent():
    report = gate.build_report()
    diagonal = report["fixed_Delta_diagonal_classification"]
    assert diagonal["rowspaces_are_equal"] is True
    assert diagonal["fixed_Delta_signed_solutions_count"] == 2
    assert diagonal["only_F_plus_and_F_minus"] is True
    assert diagonal["projector_zero_overall_SO10_orbit_signs"] == (
        "tau=+1",
        "tau=-1",
    )
    assert diagonal["global_tau_minus_is_not_SO10_equivalent_to_tau_plus"] is True
    assert diagonal["fixed_Delta_solutions_lie_in_global_tau_plus_orbit"] is True
    assert diagonal["equivalence_map"]["determinant"] == 1
    assert diagonal["equivalence_map"]["maps_F_plus_to_F_minus"] is True
    assert diagonal["equivalence_map"]["maps_Delta_to_minus_Delta"] is True


def test_literal_one_orbit_is_refuted_but_negative_orbit_is_mixed_excluded():
    report = gate.build_report()
    audit = report["Phi_orbit_lemma_audit"]
    exclusion = report["negative_F_mixed_exclusion"]
    assert audit["opposite_orbit_counterexample"]["raw_cubic_plus"] == 60
    assert audit["opposite_orbit_counterexample"]["raw_cubic_minus"] == -60
    assert audit["scope"]["literal_plus_orbit_only_statement_refuted"] is True
    assert exclusion["rank_over_Fp"] == 252
    assert exclusion["exact_real_nullity"] == 0
    assert exclusion["minus_F_global_equality_branch_excluded"] is True


def test_complete_su3_fixed_slice_is_retained_as_historical_subtheorem():
    report = gate.build_report()
    su3 = report["Phi_SU3_fixed_slice_theorem"]
    assert su3["n_failed"] == 0
    assert su3["overall_state"] == "SU3_FIXED_SLICE_CLOSED"
    assert su3["scope"][
        "complete_16_real_dimensional_SU3_fixed_space_classified"
    ] is True
    assert su3["scope"][
        "nondiagonal_Omega3_wedge_R4_directions_included"
    ] is True
    assert su3["scope"][
        "all_nonzero_slice_solutions_are_signed_Kahler_squares"
    ] is True
    assert su3["scope"]["all_arbitrary_real_four_forms_classified"] is False
    assert report["scope"][
        "complete_SU3_fixed_Phi_slice_classified_exactly"
    ] is True
    assert report["scope"]["corrected_signed_Phi_orbit_theorem_open"] is False
    assert report["scope"]["corrected_signed_Phi_orbit_theorem_proved"] is True


def test_global_claims_close_only_the_equality_orbit_lemma():
    report = gate.build_report()
    assert report["remaining_global_lemma"]["proved"] is True
    assert report["remaining_global_lemma"]["literal_single_orbit_version_refuted"] is True
    assert "SO(10).F or SO(10).(-F)" in report["remaining_global_lemma"]["statement"]
    assert report["scope"]["minus_F_mixed_branch_excluded_exact"] is True
    assert report["scope"]["corrected_signed_Phi_orbit_theorem_open"] is False
    assert report["scope"]["signed_Phi_orbits_locally_isolated_exactly"] is True
    assert report["scope"]["distant_disconnected_Phi_components_excluded"] is True
    assert report["remaining_global_lemma"][
        "signed_orbits_locally_isolated_exactly"
    ] is True
    assert report["remaining_global_lemma"][
        "complete_SU3_fixed_slice_classified_exactly"
    ] is True
    assert report["scope"]["all_arbitrary_Phi_global_equalities_classified"] is True
    assert report["scope"]["local_one_orbit_can_be_strengthened_globally"] is True
    assert report["scope"]["global_equality_orbit_classification_complete"] is True
    assert report["scope"]["quantitative_beta_global_coercivity_proved"] is False
    assert report["scope"]["G3_closed"] is False


def test_global_theorem_binds_frozen_source_and_records_external_dependency():
    report = gate.build_report()
    theorem = report["Phi_global_signed_zero_theorem"]
    assert theorem["frozen_source_sha256"] == (
        "17038c6fb82ba565a16228f5f5c03026f0ab8e3ad7959792498c2785b9653066"
    )
    assert theorem["core_sha256"] == (
        "db493a74303a57862f09c2a92118ea3d66b8b12ecbaea9162155d4ab3baafecc"
    )
    dependency = theorem["external_theorem_dependency"]
    assert dependency["kind"] == "published subgroup-classification theorem"
    assert "Dynkin" in dependency["theorem"]
    assert "imported" in dependency["repository_scope"]
