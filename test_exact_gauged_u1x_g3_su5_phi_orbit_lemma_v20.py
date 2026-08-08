import exact_gauged_u1x_g3_su5_phi_orbit_lemma_v20 as orbit_lemma


def test_literal_single_orbit_statement_has_exact_counterexample():
    report = orbit_lemma.build_report()
    witness = report["opposite_orbit_counterexample"]
    assert witness["I54_raw_both"] == 0
    assert witness["I4125_raw_both"] == 0
    assert witness["raw_cubic_plus"] == 60
    assert witness["raw_cubic_minus"] == -60
    assert witness["not_SO10_conjugate"] is True
    assert witness["literal_single_orbit_lemma_refuted"] is True


def test_complete_su4_invariant_slice_is_exactly_classified():
    report = orbit_lemma.build_report()
    certificate = report["SU4_invariant_slice"]
    assert certificate["I54_matrix_identity_max_abs_residual"] == 0
    assert certificate["I4125_matrix_identity_max_abs_residual"] == 0
    assert certificate["I54_identity"] == "(3*a^2-3*b^2+4*c^2)^2/35"
    assert certificate["I4125_identity"] == "80*(a^2-b^2-c^2)^2/21"
    assert certificate["common_real_zero_locus"] == "c=0 and a^2=b^2"
    assert certificate["complex_five_direction_obstructed"] is True


def test_linearized_excess_is_recorded_without_global_overclaim():
    report = orbit_lemma.build_report()
    warning = report["linearized_warning"]
    assert warning["unit_norm_plus_projector_linearized_rank"] == 180
    assert warning["linearized_nullity"] == 30
    assert warning["SO10_orbit_tangent_rank"] == 20
    assert warning["excess_linearized_nullity"] == 10
    assert report["corrected_global_lemma"]["proved"] is False
    assert report["scope"]["corrected_signed_two_orbit_theorem_proved"] is False
    assert report["scope"]["G3_closed"] is False


def test_report_integrity():
    report = orbit_lemma.build_report()
    assert report["n_failed"] == 0
    assert report["status"] == (
        "LITERAL_SINGLE_ORBIT_LEMMA_REFUTED__SIGNED_GLOBAL_LEMMA_OPEN"
    )
