#!/usr/bin/env python3
import numpy as np

import exact_phi2_hdagh_channel_family_v20 as gate


def test_representation_census():
    census = gate.representation_census()
    assert census["common_channels"] == {"1": 1, "45": 1, "54": 1}
    assert census["total_multiplicity"] == 3
    assert census["dimension_check_10bar_tensor_10"] == 100


def test_generic_channel_algebra():
    audit = gate.algebra_audit(gate.generic_phi())
    assert max(audit["hermiticity_residuals"].values()) < 1.0e-12
    assert audit["offdiagonal_orthogonality_residual"] < 1.0e-11
    assert audit["operator_span_rank"] == 3
    assert min(audit["operator_norms_squared"].values()) > 1.0e-10


def test_so10_covariance():
    audit = gate.covariance_audit(gate.generic_phi())
    assert audit["maximum_relative_residual"] < 1.0e-7


def test_pati_salam_background():
    audit = gate.p_background_audit()
    assert abs(audit["p_norm"] - 1.0) < 1.0e-12
    assert audit["adjoint_45_norm"] < 1.0e-12
    assert audit["q54_expected_residual"] < 1.0e-12
    expected = np.asarray([-0.4] * 6 + [0.6] * 4)
    assert np.max(np.abs(np.sort(audit["q54_eigenvalues"]) - np.sort(expected))) < 1.0e-12


def test_report_fail_closed():
    report = gate.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert report["flag"]["phi2_hdagh_channel_count_closed"] is True
    assert report["flag"]["all_three_all_component_tensor_maps_constructed"] is True
    assert report["flag"]["complete_mixed_invariant_ring"] is False
    assert report["flag"]["whole_model_validated"] is False
    assert report["flag"]["empirical_discovery"] is False
