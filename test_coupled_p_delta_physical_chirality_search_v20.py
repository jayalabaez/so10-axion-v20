import coupled_p_delta_physical_chirality_search_v20 as gate


def test_physical_chirality_and_noether_identity():
    report = gate.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert report["source_correction"]["all_126bar_blocks_use_minus_i_basis"] is True
    assert report["source_correction"]["legacy_plus_i_mixed_matrices_used"] is False
    assert report["search"]["Noether_H_times_orbit_residual"] < 1e-7
    assert report["search"]["transverse_phi_gradient_norm"] < 1e-7


def test_complete_coupled_hessian_spectrum():
    report = gate.build_report()
    search = report["search"]
    assert search["gauge_orbit_rank"] == 33
    assert search["negative_modes"] == 0
    assert search["zero_modes"] == 33
    assert search["gauge_alignment_residual"] < 1e-6
    assert search["minimum_physical_eigenvalue"] > 1e-6
    assert search["bfb_margin"] > 0.0


def test_fail_closed_remaining_model_scope():
    report = gate.build_report()
    flags = report["flag"]
    assert flags["coupled_210_126bar_local_vacuum_complete"] is True
    assert flags["complete_multifield_model"] is False
    assert flags["global_vacuum_unique"] is False
    assert flags["physical_threshold_spectrum_complete"] is False
    assert flags["exact_unique_proton_lifetime"] is False
    assert flags["whole_model_validated"] is False
    assert flags["empirical_discovery"] is False
