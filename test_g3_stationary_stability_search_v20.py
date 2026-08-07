#!/usr/bin/env python3
"""Lightweight checks for the G3 stationary-Hessian search machinery."""
from __future__ import annotations

import json

import numpy as np

import g3_stationary_stability_search_v20 as gate


def test_rayleigh_cut_coefficients_reconstruct_linear_matrix_family():
    basis = np.asarray(
        [np.diag([1.0, 0.0]), np.diag([0.0, 2.0])], dtype=float
    )
    congruence = np.eye(2)
    vector = np.asarray([0.6, 0.8])
    cut = gate._cut_coefficients(vector, basis, congruence)
    coefficients = np.asarray([3.0, 5.0])
    matrix = gate._projected_matrix(coefficients, basis, congruence)
    np.testing.assert_allclose(
        cut @ coefficients, vector @ matrix @ vector
    )


def test_generated_stability_artifact_when_present():
    if not gate.OUT_JSON.exists():
        return
    report = json.loads(gate.OUT_JSON.read_text(encoding="utf-8"))
    assert report["coverage"]["directions"] == 64
    assert report["coverage"]["real_parameters"] == 91
    assert report["coverage"]["massive_physical_dimension"] == 449
    assert report["checks"]["all_486_tadpoles_remain_zero"]
    assert report["checks"]["all_couplings_perturbative"]
    assert not report["flags"]["G3_closed"]
