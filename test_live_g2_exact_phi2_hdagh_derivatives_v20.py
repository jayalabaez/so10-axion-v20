#!/usr/bin/env python3
"""Regression tests for the exact Phi^2 Hdag H channel derivatives."""
from __future__ import annotations

import numpy as np
import pytest

import live_g2_exact_phi2_hdagh_derivatives_v20 as mod


@pytest.fixture(scope="module")
def state():
    return mod.potential.deterministic_state(3004)


@pytest.fixture(scope="module")
def analytic(state):
    return mod.all_direction_derivatives(state)


def test_report_passes_without_closing_G2():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["coverage"]["base_family"] == "Phi2_HdagH_channels"
    assert report["coverage"]["base_family_count_closed_here"] == 1
    assert report["coverage"]["cumulative_base_family_count_with_parents"] == 12
    assert report["coverage"]["base_family_count_total"] == 18
    assert report["coverage"]["remaining_base_families"] == 6
    assert report["coverage"]["expected_direction_count"] > 0
    assert report["coverage"]["expected_direction_count"] == report["coverage"]["observed_direction_count"]
    assert report["coverage"]["parameter_count_closed_here"] > 0
    assert report["coverage"]["basis_indices"] == [0, 1, 2]
    assert report["coverage"]["basis_labels"] == ["1", "45", "54"]
    assert report["flags"]["authoritative_Phi2_HdagH_adapter_closed"]
    assert report["flags"]["all_64_direction_gradients_complete"] is False
    assert report["flags"]["all_64_direction_Hessians_complete"] is False
    assert report["flags"]["G2_closed"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_exact_coefficient_maps_have_expected_shape_and_symmetry():
    audit = mod.coefficient_audit()
    assert audit["interior_table_shape"] == [10, 210, 120]
    assert audit["channel45_nonzero_pair_count"] > 0
    assert audit["channel45_pair_Hermiticity_residual"] < 1.0e-12
    assert audit["channel45_pair_symmetry_residual"] < 1.0e-15


def test_all_three_operators_and_values_match_authoritative_source(state):
    audit = mod.source_normalization_audit(state)
    assert set(audit["operator_residuals"]) == {"1", "45", "54"}
    assert set(audit["value_residuals"]) == {"1", "45", "54"}
    assert audit["maximum_operator_residual"] < 1.0e-10
    assert audit["maximum_value_residual"] < 1.0e-10


def test_selected_family_basis_and_live_values(state, analytic):
    directions = mod.selected_directions(state)
    assert directions
    assert {row.base_family for row in directions} == {mod.BASE_FAMILY}
    assert sorted({row.basis_index for row in directions}) == [0, 1, 2]
    assert sorted({row.basis_label for row in directions}) == ["1", "45", "54"]
    expected = {row.direction_id: row.value for row in directions}
    assert {row.direction_id for row in analytic} == set(expected)
    for row in analytic:
        assert abs(row.value - expected[row.direction_id]) < 1.0e-9
        assert row.gradient.shape == (486,)
        assert row.hessian.shape == (486, 486)
        assert np.all(np.isfinite(row.gradient.real))
        assert np.all(np.isfinite(row.gradient.imag))
        assert np.all(np.isfinite(row.hessian.real))
        assert np.all(np.isfinite(row.hessian.imag))
        assert np.max(np.abs(row.hessian - row.hessian.T)) < 1.0e-10
        if row.self_conjugate:
            assert abs(row.value.imag) < 1.0e-9
            assert np.max(np.abs(row.gradient.imag)) < 1.0e-9
            assert np.max(np.abs(row.hessian.imag)) < 1.0e-9


def test_channel_1_closed_form_blocks(state):
    q = mod.chart.pack(state)
    phi = q[mod.chart.PHI_SLICE]
    h_block = q[mod.chart.H_SLICE]
    h_norm = 0.5 * np.dot(h_block, h_block)
    phi_norm = np.dot(phi, phi)
    value, gradient, hessian = mod.base_derivative(q, 0)
    assert abs(value.real - phi_norm * h_norm) < 1.0e-12
    assert np.max(
        np.abs(gradient[mod.chart.PHI_SLICE].real - 2.0 * h_norm * phi)
    ) < 1.0e-12
    assert np.max(
        np.abs(gradient[mod.chart.H_SLICE].real - phi_norm * h_block)
    ) < 1.0e-12
    assert np.max(
        np.abs(
            hessian[mod.chart.PHI_SLICE, mod.chart.H_SLICE].real
            - 2.0 * np.outer(phi, h_block)
        )
    ) < 1.0e-12


def test_parameter_ids_and_five_point_reconstruction(state, analytic):
    parameters = mod.quadratic.parameter_derivatives(analytic)
    assert parameters
    live_ids = {
        row.parameter_id
        for row in mod.potential.parameter_schema(mod.potential.evaluate_directions(state))
    }
    assert {row.parameter_id for row in parameters}.issubset(live_ids)
    coefficients = mod.quadratic.deterministic_coefficients(parameters)
    audit = mod.quadratic.five_point_directional_audit(state, parameters, coefficients)
    assert audit["value_residual"] < 1.0e-8
    assert audit["first_residual"] < 2.0e-7
    assert audit["second_residual"] < 2.0e-6


def test_unknown_channel_and_direction_are_rejected(state):
    q = mod.chart.pack(state)
    with pytest.raises(KeyError):
        mod.base_derivative(q, 3)
    with pytest.raises(KeyError):
        mod.channel_operator_derivatives(
            q[mod.chart.PHI_SLICE], state.h, "not-a-channel"
        )
    unsupported = next(
        row
        for row in mod.potential.evaluate_directions(state)
        if row.base_family != mod.BASE_FAMILY
    )
    with pytest.raises(KeyError):
        mod.direction_derivative(q, unsupported)
