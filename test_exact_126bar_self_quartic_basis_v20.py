import exact_126bar_self_quartic_basis_v20 as gate


def test_complete_operator_basis_and_character_identity():
    report = gate.build_report()
    assert report["n_failed"] == 0, report["failures"]
    result = report["representation_result"]
    assert result["n_charge_neutral_self_quartics"] == 4
    assert result["symmetric_square_dimension"] == 8001
    assert result["character_audit"]["maximum_identity_abs_residual"] < 1e-40
    assert report["generic_projector_audit"]["minimum_channel_norm"] > 1e-8


def test_delta_r_fractions_and_gauge_orbit():
    report = gate.build_report()
    audit = report["delta_R_Hessian_audit"]
    values = audit["invariant_values_at_delta_R"]
    assert values["54"] < 1e-12
    assert values["1050bar"] < 1e-12
    assert abs(values["4125"] - 1 / 3) < 1e-12
    assert abs(values["2772bar"] - 2 / 3) < 1e-12
    assert audit["orbit_rank"] == 33
    assert audit["zero_cluster_multiplicity"] == 33


def test_opposite_sign_no_go_and_fail_closed_scope():
    report = gate.build_report()
    audit = report["delta_R_Hessian_audit"]
    no_go = audit["no_go_certificate"]
    assert audit["obstruction_36_multiplicity"] == 36
    assert audit["obstruction_2_multiplicity"] == 2
    assert no_go["strictly_positive_self_sector_Hessian_possible"] is False
    assert no_go["equal_couplings_extra_flat_modes"] == 38
    assert no_go["equal_couplings_total_zero_modes"] == 71
    assert report["flag"]["mixed_210_126bar_channels_required"] is True
    assert report["flag"]["complete_multifield_potential"] is False
    assert report["flag"]["whole_model_validated"] is False
    assert report["flag"]["empirical_discovery"] is False
