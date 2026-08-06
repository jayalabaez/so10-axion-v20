#!/usr/bin/env python3
from __future__ import annotations

import numpy as np

import exact_phisigma_all_component_projectors_v20 as allq


def test_arbitrary_component_pure_invariants_reconstruct_C() -> None:
    audit = allq._all_component_reconstruction_audit()
    assert audit["reconstruction_abs_residual"] < 1.0e-9
    assert audit["minimum_channel_overlap"] > 1.0e-10


def test_full_operator_shapes_and_hermiticity() -> None:
    for channel in allq.CHANNELS:
        operator = allq.evaluate_full_sigma_operator(
            channel, p=0.9, a=0.4, omega=0.7
        )
        assert operator.shape == (126, 126)
        assert np.max(np.abs(operator - operator.conj().T)) < 1.0e-10


def test_authoritative_report_passes_without_overclaim() -> None:
    report = allq.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert report["full_126_background_certificate"][
        "coefficient_matrix_count"
    ] == 36
    assert report["flag"][
        "all_PhiSigma_quartic_all_component_Clebsches_complete"
    ] is True
    assert report["flag"]["complete_component_potential"] is False
    assert report["flag"]["unique_full_vacuum"] is False
    assert report["flag"]["physical_full_Hessian_complete"] is False
    assert report["flag"]["physical_threshold_spectrum_complete"] is False
    assert report["flag"]["exact_unique_proton_lifetime"] is False
    assert report["flag"]["whole_model_validated"] is False
    assert report["flag"]["empirical_discovery"] is False
