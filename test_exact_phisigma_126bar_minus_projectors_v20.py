import exact_phisigma_126bar_minus_projectors_v20 as gate


def test_physical_minus_chirality_and_delta_coordinates():
    report = gate.build_report()
    assert report["n_failed"] == 0, report["failures"]
    audit = report["chirality_audit"]
    assert audit["minus_basis_gram_residual"] < 1e-12
    assert audit["minus_basis_hodge_residual"] < 1e-12
    assert audit["opposite_chirality_overlap_residual"] < 1e-12
    assert audit["delta_coordinate_reconstruction_residual"] < 1e-12


def test_six_channel_direct_reconstruction():
    report = gate.build_report()
    audit = report["generic_reconstruction_audit"]
    assert audit["six_channel_reconstruction_residual"] < 1e-11
    assert audit["minimum_common_channel_operator_norm"] > 1e-8
    assert max(audit["noncommon_operator_residuals"].values()) < 1e-11
    assert audit["maximum_hermiticity_residual"] < 1e-12


def test_delta_eigenvectors_and_fail_closed_scope():
    report = gate.build_report()
    assert report["delta_R_audit"]["maximum_eigenvector_residual"] < 1e-11
    assert report["source_correction"]["physical_126bar_chirality"] == "-i"
    assert report["source_correction"]["coordinate_matrices_interchangeable"] is False
    assert report["flag"]["physical_126bar_projector_basis_complete"] is True
    assert report["flag"]["coupled_210_126bar_local_vacuum_complete"] is False
    assert report["flag"]["whole_model_validated"] is False
    assert report["flag"]["empirical_discovery"] is False
