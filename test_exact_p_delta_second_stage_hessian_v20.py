import exact_p_delta_second_stage_hessian_v20 as gate


def test_all_component_cubic_and_upstreams():
    report = gate.build_report()
    assert report["n_failed"] == 0, report["failures"]
    cubic = report["cubic_all_component_audit"]
    assert cubic["hermiticity_residual"] < 1e-12
    assert cubic["delta_eigen_residual"] < 1e-12
    assert abs(cubic["delta_eigenvalue"] - 2.0) < 1e-12
    assert cubic["spectrum_clusters"] == {"-2.0": 30, "0.0": 66, "2.0": 30}


def test_bounded_tachyon_free_fixed_p_hessian():
    report = gate.build_report()
    benchmark = report["benchmark"]
    bound = benchmark["boundedness_certificate"]
    assert bound["minimum_self_projector_weight"] > 0.0
    assert bound["strict_mixed_quartic_margin"] > 0.0
    assert benchmark["negative_modes"] == 0
    assert benchmark["zero_modes"] == 9
    assert benchmark["PS_to_SM_orbit_rank"] == 9
    assert benchmark["Goldstone_alignment_residual"] < 1e-10
    assert benchmark["minimum_physical_eigenvalue"] > 0.0


def test_fail_closed_full_model_scope():
    report = gate.build_report()
    flags = report["flag"]
    assert flags["fixed_P_second_stage_stabilized"] is True
    assert flags["full_simultaneous_vacuum_complete"] is False
    assert flags["complete_multifield_Hessian"] is False
    assert flags["physical_threshold_spectrum_complete"] is False
    assert flags["exact_unique_proton_lifetime"] is False
    assert flags["whole_model_validated"] is False
    assert flags["empirical_discovery"] is False
