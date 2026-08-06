#!/usr/bin/env python3
"""Regression tests for exact H10 self-quartic derivatives."""
from __future__ import annotations

import numpy as np

import live_g2_exact_h10_self_quartic_derivatives_v20 as mod


def test_report_passes_fail_closed():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["coverage"]["base_families_closed_total"] == 6
    assert report["coverage"]["base_families_total"] == 18
    assert report["flags"]["B13_derivative_adapter_closed"]
    assert report["flags"]["G2_closed"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_G1_B13_has_two_directions_and_exact_values():
    state = mod.potential.deterministic_state(1313)
    source = sorted(mod.selected_directions(state), key=lambda row: row.basis_index)
    derivatives = mod.direction_derivatives(state)
    assert len(source) == len(derivatives) == 2
    assert [row.basis_index for row in source] == [0, 1]
    assert max(abs(left.value - right.value) for left, right in zip(derivatives, source)) < 1.0e-10


def test_I1_and_I54_dense_derivatives_live_only_in_H_block():
    state = mod.potential.deterministic_state(1313)
    for row in mod.direction_derivatives(state):
        outside = np.ones(486, dtype=bool)
        outside[mod.chart.H_SLICE] = False
        assert np.max(np.abs(row.gradient[outside])) < 1.0e-15
        assert np.max(np.abs(row.hessian[np.ix_(outside, outside)])) < 1.0e-15
        assert np.max(np.abs(row.hessian[np.ix_(outside, ~outside)])) < 1.0e-15
        assert np.max(np.abs(row.hessian - row.hessian.T)) < 1.0e-12


def test_I1_formula_matches_closed_form():
    state = mod.potential.deterministic_state(51)
    q = mod.chart.pack(state)
    i1, _ = mod.base_derivatives(q)
    h = q[mod.chart.H_SLICE]
    n = 0.5 * float(np.dot(h, h))
    expected_gradient = 2.0 * n * h
    expected_hessian = 2.0 * np.outer(h, h) + 2.0 * n * np.eye(20)
    assert abs(i1.value - n**2) < 1.0e-12
    assert np.max(np.abs(i1.gradient[mod.chart.H_SLICE] - expected_gradient)) < 1.0e-12
    assert np.max(np.abs(i1.hessian[mod.chart.H_SLICE, mod.chart.H_SLICE] - expected_hessian)) < 1.0e-12


def test_five_point_reconstruction_is_exact():
    state = mod.potential.deterministic_state(1313)
    derivatives = mod.direction_derivatives(state)
    audit = mod.directional_audit(state, derivatives)
    assert audit["value_residual"] < 1.0e-9
    assert audit["first_residual"] < 1.0e-8
    assert audit["second_residual"] < 1.0e-7


def test_assembled_two_coupling_Hessian_is_symmetric():
    state = mod.potential.deterministic_state(1313)
    rows = mod.direction_derivatives(state)
    coefficients = {
        f"lambda::{rows[0].direction_id}": 0.4,
        f"lambda::{rows[1].direction_id}": -0.2,
    }
    assembled = mod.assemble(rows, coefficients)
    assert assembled["gradient"].shape == (486,)
    assert assembled["hessian"].shape == (486, 486)
    assert np.max(np.abs(assembled["hessian"] - assembled["hessian"].T)) < 1.0e-12
