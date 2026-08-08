#!/usr/bin/env python3
"""Focused structural tests for the exact second-stage G3 Hessian gate."""
from __future__ import annotations

import json

import numpy as np

import g3_full_hessian_classification_v20 as gate


def test_historical_option_c_scope_is_explicit():
    assert gate.MODEL_CONTRACT_ID == "historical_option_c_no_x_v20"
    assert gate.AUTHORITATIVE_FOR_MANUSCRIPT is False
    assert gate.MODEL_WIDE_NO_GO_CERTIFIED is False


def test_stage_resolved_gauge_and_pq_quotient_dimensions():
    quotient = gate.physical_quotient_basis()
    assert quotient["gauge"]["pre_rank"] == 33
    assert quotient["gauge"]["increment_rank"] == 3
    assert quotient["gauge"]["total_rank"] == 36
    assert quotient["symmetry_basis"].shape == (486, 37)
    assert quotient["quotient"].shape == (486, 449)
    assert quotient["pq_after_gauge_norm"] > 0.0
    assert quotient["symmetry_quotient_overlap"] < 1.0e-10


def test_congruence_equilibration_preserves_small_example_inertia():
    matrix = np.diag([-1.0e-24, 2.0, 3.0e20])
    balanced = gate.equilibrate_congruence(matrix)["matrix"]
    eigenvalues = np.linalg.eigvalsh(balanced)
    assert np.sum(eigenvalues < 0.0) == 1
    assert np.sum(eigenvalues > 0.0) == 2


def test_generated_full_hessian_artifact_when_present():
    if not gate.OUT_JSON.exists():
        return
    report = json.loads(gate.OUT_JSON.read_text(encoding="utf-8"))
    assert report["coverage"] == {
        "base_families": 18,
        "directions": 64,
        "real_parameters": 91,
        "real_field_dimension": 486,
    }
    assert report["physical_Hessian"]["massive_physical_dimension"] == 449
    assert report["flags"]["full_486x486_stationary_Hessian_assembled"]
    assert report["flags"]["all_36_gauge_directions_quotiented"]
    assert not report["flags"]["G3_closed"]
