#!/usr/bin/env python3
import numpy as np

import exact_h10_self_quartic_family_v20 as gate


def test_exact_channel_count():
    census = gate.representation_census()
    assert census["Sym2_10"] == {"1": 1, "54": 1}
    assert census["dimension"]["left"] == census["dimension"]["right"] == 55
    assert census["quartic_singlet_multiplicity"] == 2
    assert census["independent_adjoint_45_channel"] is False


def test_projector_and_current_identities():
    for vector in gate.sample_vectors().values():
        values = gate.invariants(vector)
        assert values["projector_completeness_residual"] < 1.0e-12
        assert values["current_identity_residual"] < 1.0e-12


def test_two_pure_channels_independent():
    audit = gate.independence_audit()
    assert audit["rank"] == 2
    assert abs(audit["determinant"]) > 1.0e-6


def test_exact_bfb_cone_endpoints():
    assert gate.bfb(0.7, -0.2)["strictly_positive_away_from_origin"] is True
    boundary = gate.bfb(0.4, -0.4)
    assert boundary["bounded_from_below"] is True
    assert boundary["strictly_positive_away_from_origin"] is False
    assert gate.bfb(-0.1, 0.5)["bounded_from_below"] is False
    assert gate.bfb(0.2, -0.3)["bounded_from_below"] is False


def test_ratio_range_realizes_both_boundaries():
    audit = gate.ratio_range_audit()
    assert audit["covers_endpoint_zero"] is True
    assert audit["covers_endpoint_one"] is True
    assert np.min(audit["ratios"]) >= -1.0e-12
    assert np.max(audit["ratios"]) <= 1.0 + 1.0e-12


def test_report_fail_closed():
    report = gate.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert report["flag"]["h10_self_quartic_count_closed"] is True
    assert report["flag"]["h10_self_quartic_tensor_basis_closed"] is True
    assert report["flag"]["h10_isolated_quartic_BFB_cone_closed"] is True
    assert report["flag"]["complete_mixed_invariant_ring"] is False
    assert report["flag"]["whole_model_validated"] is False
    assert report["flag"]["empirical_discovery"] is False
