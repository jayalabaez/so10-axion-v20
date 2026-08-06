#!/usr/bin/env python3
from __future__ import annotations

import numpy as np

import exact_muD_482_schur_stability_v20 as schur
import exact_operator_derived_h10_mass_block_v20 as gate


def test_isotropic_soft_limit():
    audit = gate.isotropic_limit_audit()
    assert audit["isotropic_recovery_ok"]
    assert audit["soft_only_real_residual_to_m2_I"] < 1.0e-12


def test_p_channel_structure():
    audit = gate.p_channel_audit()
    assert abs(audit["p_norm"] - 1.0) < 1.0e-12
    assert audit["phi45_operator_norm"] < 1.0e-12
    assert audit["q54_expected_residual"] < 1.0e-12


def test_loewner_transition():
    report = gate.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert report["loewner_stable"]["positive_definite"]
    assert report["spectrum_stable_full"]["zero_modes"] == 33
    assert report["spectrum_stable_full"]["negative_modes"] == 0
    assert report["spectrum_stable_physical"]["zero_modes"] == 0
    assert report["spectrum_stable_physical"]["negative_modes"] == 0
    assert report["spectrum_unstable_physical"]["negative_modes"] > 0 or report[
        "spectrum_unstable_full"
    ]["negative_modes"] > 0 or report["loewner_unstable"][
        "shifted_lambda_min"
    ] < -1.0e-10


def test_fail_closed():
    flags = gate.build_report()["flag"]
    assert flags["complete_operator_derived_H_mass_matrix"]
    assert flags["phi2_hdagh_channels_inserted"]
    assert not flags["hsigma_45_full_vector_complete"]
    assert not flags["nonzero_electroweak_backreaction"]
    assert not flags["complete_multifield_model"]
    assert not flags["whole_model_validated"]


def test_physical_matrix_shape():
    assembled = gate.complex_mass_matrix()
    real = gate.real_mass_matrix(assembled["matrix"])
    assert real.shape == (20, 20)
    matrix = gate.physical_matrix_with_mh(1.0, real)
    old = schur.old_hessian_data()
    assert matrix.shape == (old["physical_hessian"].shape[0] + 20,)*2
