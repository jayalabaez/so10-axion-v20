import exact_s_phi17_renormalizable_phase_gate_v20 as gate


def test_complete_renormalizable_singlet_census():
    report = gate.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert report["renormalizable_singlet_operators"] == [
        "|Phi17|^2",
        "|Phi17|^4",
        "|S|^2",
        "|S|^2|Phi17|^2",
        "|S|^4",
    ]


def test_phi17_phase_obstruction():
    report = gate.build_report()
    assert report["theorem"]["minimum_pure_phi17_phase_sensitive_power"] == 17
    assert report["hessian"]["phi17_phase_zero"] is True
    assert report["flag"]["phi17_phase_resolved"] is False


def test_bounded_radial_but_fail_closed_full_model():
    report = gate.build_report()
    assert min(report["hessian"]["quartic_matrix_eigenvalues"]) > 0
    assert min(report["hessian"]["radial_hessian_eigenvalues"]) > 0
    assert report["flag"]["singlet_renormalizable_operator_census_complete"] is True
    assert report["flag"]["complete_10H_S_Phi17_potential"] is False
    assert report["flag"]["complete_multifield_model"] is False
    assert report["flag"]["whole_model_validated"] is False
    assert report["flag"]["empirical_discovery"] is False
