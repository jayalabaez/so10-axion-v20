#!/usr/bin/env python3
"""Regression tests for the authoritative H10 self-quartic derivatives."""
from __future__ import annotations

import numpy as np
import pytest

import live_g2_exact_h10_self_quartic_derivatives_v20 as mod


@pytest.fixture(scope="module")
def state():
    return mod.potential.deterministic_state(2804)


@pytest.fixture(scope="module")
def analytic(state):
    return mod.all_direction_derivatives(state)


def test_report_passes_without_closing_G2():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["coverage"]["base_family"] == "H_self_quartics"
    assert report["coverage"]["base_family_count_closed_here"] == 1
    assert report["coverage"]["cumulative_base_family_count_with_parents"] == 10
    assert report["coverage"]["base_family_count_total"] == 18
    assert report["coverage"]["remaining_base_families"] == 8
    assert report["coverage"]["expected_direction_count"] > 0
    assert (
        report["coverage"]["expected_direction_count"]
        == report["coverage"]["observed_direction_count"]
    )
    assert report["coverage"]["parameter_count_closed_here"] > 0
    assert report["coverage"]["basis_indices"] == [0, 1]
    assert report["coverage"]["basis_labels"] == ["I_1", "I_54"]
    assert report["flags"]["authoritative_H_self_quartic_adapter_closed"]
    assert report["flags"]["all_64_direction_gradients_complete"] is False
    assert report["flags"]["all_64_direction_Hessians_complete"] is False
    assert report["flags"]["G2_closed"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_selected_family_and_basis_are_authoritative(state, analytic):
    directions = mod.selected_directions(state)
    assert directions
    assert {row.base_family for row in directions} == {"H_self_quartics"}
    assert {row.base_family for row in analytic} == {"H_self_quartics"}
    assert sorted({row.basis_index for row in directions}) == [0, 1]
    assert sorted({row.basis_label for row in directions}) == ["I_1", "I_54"]


def test_base_formulas_match_authoritative_values(state):
    q = mod.chart.pack(state)
    directions = {
        row.basis_index: row for row in mod.selected_directions(state)
    }
    for basis_index in (0, 1):
        value, gradient, hessian = mod.base_derivative(q, basis_index)
        assert abs(value - directions[basis_index].value) < 1.0e-10
        assert gradient.shape == (486,)
        assert hessian.shape == (486, 486)
        assert np.max(np.abs(hessian - hessian.T)) < 1.0e-12


def test_I1_and_I54_canonical_normalizations(state):
    q_h = mod.chart.pack(state)[mod.chart.H_SLICE]
    norm = 0.5 * np.dot(q_h, q_h)
    i1_value, i1_gradient, i1_hessian = mod.base_derivative(
        mod.chart.pack(state), 0
    )
    assert abs(i1_value.real - norm**2) < 1.0e-12
    assert np.max(
        np.abs(i1_gradient[mod.chart.H_SLICE].real - 2.0 * norm * q_h)
    ) < 1.0e-12
    expected_i1_hessian = 2.0 * np.outer(q_h, q_h) + 2.0 * norm * np.eye(
        mod.chart.H_REAL_DIM
    )
    assert np.max(
        np.abs(
            i1_hessian[mod.chart.H_SLICE, mod.chart.H_SLICE].real
            - expected_i1_hessian
        )
    ) < 1.0e-12

    pair, _, _ = mod.h_squared_jet(q_h)
    i54_value, _, _ = mod.base_derivative(mod.chart.pack(state), 1)
    assert abs(i54_value.real - abs(pair) ** 2) < 1.0e-12


def test_all_dressed_values_and_dense_support(state, analytic):
    expected = {
        row.direction_id: row.value for row in mod.selected_directions(state)
    }
    assert {row.direction_id for row in analytic} == set(expected)
    for row in analytic:
        assert abs(row.value - expected[row.direction_id]) < 1.0e-10
        assert row.gradient.shape == (486,)
        assert row.hessian.shape == (486, 486)
        assert np.all(np.isfinite(row.gradient.real))
        assert np.all(np.isfinite(row.hessian.real))
        assert np.max(np.abs(row.hessian - row.hessian.T)) < 1.0e-12
        if row.self_conjugate:
            assert abs(row.value.imag) < 1.0e-10
            assert np.max(np.abs(row.gradient.imag)) < 1.0e-10
            assert np.max(np.abs(row.hessian.imag)) < 1.0e-10
    audit = mod.base_support_audit(mod.chart.pack(state))
    assert set(audit) == {"I_1", "I_54"}
    for row in audit.values():
        assert row["inactive_gradient_residual"] < 1.0e-12
        assert row["inactive_Hessian_residual"] < 1.0e-12


def test_parameter_ids_and_five_point_reconstruction(state, analytic):
    parameters = mod.quadratic.parameter_derivatives(analytic)
    assert parameters
    live_ids = {
        row.parameter_id
        for row in mod.potential.parameter_schema(
            mod.potential.evaluate_directions(state)
        )
    }
    assert {row.parameter_id for row in parameters}.issubset(live_ids)
    coefficients = mod.quadratic.deterministic_coefficients(parameters)
    audit = mod.quadratic.five_point_directional_audit(
        state, parameters, coefficients
    )
    assert audit["value_residual"] < 1.0e-9
    assert audit["first_residual"] < 1.0e-8
    assert audit["second_residual"] < 1.0e-7


def test_unknown_basis_and_direction_are_rejected(state):
    q = mod.chart.pack(state)
    with pytest.raises(KeyError):
        mod.base_derivative(q, 2)
    unsupported = next(
        row
        for row in mod.potential.evaluate_directions(state)
        if row.base_family != mod.BASE_FAMILY
    )
    with pytest.raises(KeyError):
        mod.direction_derivative(q, unsupported)
