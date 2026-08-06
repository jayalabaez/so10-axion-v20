#!/usr/bin/env python3
"""Regression tests for both H--126bar Hermitian quartic channels."""
from __future__ import annotations

import numpy as np
import pytest

import live_g2_exact_hsigma_hermitian_derivatives_v20 as mod


@pytest.fixture(scope="module")
def state():
    return mod.potential.deterministic_state(2904)


@pytest.fixture(scope="module")
def analytic(state):
    return mod.all_direction_derivatives(state)


def test_report_passes_without_closing_G2():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["coverage"]["base_family"] == "H_Sigma_Hermitian_quartics"
    assert report["coverage"]["base_family_count_closed_here"] == 1
    assert report["coverage"]["cumulative_base_family_count_with_parents"] == 11
    assert report["coverage"]["base_family_count_total"] == 18
    assert report["coverage"]["remaining_base_families"] == 7
    assert report["coverage"]["expected_direction_count"] > 0
    assert report["coverage"]["expected_direction_count"] == report["coverage"]["observed_direction_count"]
    assert report["coverage"]["parameter_count_closed_here"] > 0
    assert report["coverage"]["basis_indices"] == [0, 1]
    assert report["coverage"]["basis_labels"] == ["1", "45"]
    assert report["flags"]["authoritative_H_Sigma_adapter_closed"]
    assert report["flags"]["all_64_direction_gradients_complete"] is False
    assert report["flags"]["all_64_direction_Hessians_complete"] is False
    assert report["flags"]["G2_closed"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_generator_matrices_and_current_Hessians():
    audit = mod.generator_audit()
    assert audit["generator_count"] == 45
    assert audit["H_shape"] == [45, 10, 10]
    assert audit["Sigma_shape"] == [45, 126, 126]
    assert audit["H_anti_Hermiticity_residual"] < 1.0e-12
    assert audit["Sigma_anti_Hermiticity_residual"] < 1.0e-11
    assert audit["H_current_Hessian_symmetry_residual"] < 1.0e-12
    assert audit["Sigma_current_Hessian_symmetry_residual"] < 1.0e-12


def test_both_base_values_match_direct_current_source(state):
    q = mod.chart.pack(state)
    expected = mod.direct_source_values(state)
    for index, label in enumerate(mod.BASIS_LABELS):
        value, gradient, hessian = mod.base_derivative(q, index)
        assert abs(value - expected[label]) < 1.0e-9
        assert gradient.shape == (486,)
        assert hessian.shape == (486, 486)
        assert np.max(np.abs(hessian - hessian.T)) < 1.0e-10


def test_selected_family_basis_and_live_values(state, analytic):
    directions = mod.selected_directions(state)
    assert directions
    assert {row.base_family for row in directions} == {mod.BASE_FAMILY}
    assert sorted({row.basis_index for row in directions}) == [0, 1]
    assert sorted({row.basis_label for row in directions}) == [
        "1",
        "45",
    ]
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


def test_channel_1_normalization_is_product_of_canonical_norms(state):
    q = mod.chart.pack(state)
    value, gradient, hessian = mod.base_derivative(q, 0)
    h = q[mod.chart.H_SLICE]
    sigma = q[mod.chart.SIGMA_SLICE]
    n_h = 0.5 * np.dot(h, h)
    n_sigma = 0.5 * np.dot(sigma, sigma)
    assert abs(value.real - n_h * n_sigma) < 1.0e-12
    assert np.max(
        np.abs(gradient[mod.chart.H_SLICE].real - n_sigma * h)
    ) < 1.0e-12
    assert np.max(
        np.abs(gradient[mod.chart.SIGMA_SLICE].real - n_h * sigma)
    ) < 1.0e-12
    assert np.max(
        np.abs(
            hessian[mod.chart.H_SLICE, mod.chart.SIGMA_SLICE].real
            - np.outer(h, sigma)
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
