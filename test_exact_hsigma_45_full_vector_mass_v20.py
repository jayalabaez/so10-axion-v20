#!/usr/bin/env python3
from __future__ import annotations

import numpy as np

import exact_hsigma_45_full_vector_mass_v20 as gate
import exact_operator_derived_h10_mass_block_v20 as mass_block


def test_spectrum_and_hermiticity():
    matrix = gate.delta_r_mass_matrix()
    spectrum = gate.spectrum_audit(matrix)
    assert spectrum["hermiticity_residual"] < 1.0e-12
    assert spectrum["n_positive"] == 5
    assert spectrum["n_negative"] == 5
    assert abs(spectrum["lambda_max"] - 1.0) < 1.0e-10
    assert abs(spectrum["lambda_min"] + 1.0) < 1.0e-10
    assert abs(spectrum["trace"]) < 1.0e-10


def test_ew_cross_check():
    audit = gate.electroweak_cross_check()
    assert audit["matches_closed_sign_pattern"]
    assert audit["absolute_unit_residual"] < 1.0e-10


def test_loewner_insertion():
    report = gate.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert report["inserted_benchmark"]["spectrum_full"]["zero_modes"] == 33
    assert report["flag"]["hsigma_45_full_vector_complete"]


def test_mass_block_wires_nonzero_coupling():
    assembled = mass_block.complex_mass_matrix(lambda_hsigma_45=0.5)
    residual = assembled["contributions"]["hsigma_45"]
    assert residual.shape == (10, 10)
    assert float(np.linalg.norm(residual)) > 0.1
