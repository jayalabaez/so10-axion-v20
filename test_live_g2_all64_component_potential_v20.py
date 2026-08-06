#!/usr/bin/env python3
"""Regression tests for the unified all-64 G2 value evaluator."""
from __future__ import annotations

import numpy as np

import live_g2_all64_component_potential_v20 as mod


def test_report_passes_fail_closed():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["flags"]["complete_G2_component_potential_value_evaluator"]
    assert report["flags"]["complete_G2_gradient"] is False
    assert report["flags"]["complete_G2_Hessian"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_all_base_and_live_direction_counts():
    state = mod.deterministic_state()
    base = mod.base_direction_values(
        phi=state["phi"], h=state["h"], sigma=state["sigma"]
    )
    assert len(base) == 18
    assert sum(len(values) for values in base.values()) == 34
    directions = mod.operator_directions(**state)
    assert len(directions) == 64
    assert len({row["id"] for row in directions}) == 64


def test_coupling_schema_is_91_real_parameters():
    directions = mod.operator_directions(**mod.deterministic_state())
    schema = mod.coupling_schema(directions)
    assert schema["directions"] == 64
    assert schema["real_couplings"] + schema["complex_couplings"] == 64
    assert schema["real_parameters"] == 91


def test_manifestly_real_potential_reconstruction():
    directions = mod.operator_directions(**mod.deterministic_state())
    couplings = mod.deterministic_couplings(directions)
    result = mod.potential_value(directions, couplings)
    assert np.isfinite(result["value"])
    assert abs(result["value"] - sum(result["contributions"].values())) < 1.0e-10


def test_self_conjugate_directions_are_real():
    directions = mod.operator_directions(**mod.deterministic_state())
    residual = max(
        abs(complex(row["operator_value"]).imag)
        for row in directions
        if row["self_conjugate"]
    )
    assert residual < 1.0e-8
