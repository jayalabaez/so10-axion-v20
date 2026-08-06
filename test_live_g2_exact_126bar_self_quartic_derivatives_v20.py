#!/usr/bin/env python3
"""Regression tests for exact 126bar self-projector quartic derivatives."""
from __future__ import annotations

import numpy as np
import pytest

import live_g2_exact_126bar_self_quartic_derivatives_v20 as mod


@pytest.fixture(scope="module")
def state():
    return mod.potential.deterministic_state(3504)


@pytest.fixture(scope="module")
def analytic(state):
    return mod.all_direction_derivatives(state)


def test_report_passes_without_closing_g2():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["coverage"]["base_family"] == mod.BASE_FAMILY
    assert report["coverage"]["basis_labels"] == list(mod.BASIS_LABELS)
    assert report["coverage"]["real_field_dimension"] == 486
    assert report["coverage"]["Hessian_shape"] == [486, 486]
    assert report["flags"]["G2_closed"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_authoritative_values_shapes_and_support(state):
    q = mod.chart.pack(state)
    sigma = mod.chart._unpack_complex_interleaved(q[mod.chart.SIGMA_SLICE])
    expected = mod.source.quartics(sigma)
    for index, label in enumerate(mod.BASIS_LABELS):
        value, gradient, hessian = mod.base_derivative(q, index)
        assert abs(value - expected[label]) < 1.0e-10
        assert gradient.shape == (486,)
        assert hessian.shape == (486, 486)
        assert np.max(np.abs(hessian - hessian.T)) < 1.0e-10
        assert np.max(np.abs(gradient[mod.chart.SIGMA_SLICE].imag)) < 1.0e-12


def test_gradient_and_hessian_vector_match_finite_differences(state):
    q = mod.chart.pack(state)
    rng = np.random.default_rng(3505)
    direction = rng.normal(size=486)
    direction /= np.linalg.norm(direction)
    step = 2.0e-4
    for index in range(len(mod.BASIS_LABELS)):
        value, gradient, hessian = mod.base_derivative(q, index)
        lower = mod.base_derivative(q - step * direction, index)[0].real
        upper = mod.base_derivative(q + step * direction, index)[0].real
        numerical_gradient = (upper - lower) / (2.0 * step)
        numerical_hvp = (upper - 2.0 * value.real + lower) / step**2
        assert abs(numerical_gradient - gradient.real @ direction) < 3.0e-5
        assert abs(numerical_hvp - direction @ hessian.real @ direction) < 3.0e-4


def test_dressed_values_and_parameter_reconstruction(state, analytic):
    expected = {row.direction_id: row.value for row in mod.selected_directions(state)}
    assert {row.direction_id for row in analytic} == set(expected)
    for row in analytic:
        assert abs(row.value - expected[row.direction_id]) < 1.0e-10
        assert row.gradient.shape == (486,)
        assert row.hessian.shape == (486, 486)
        assert np.max(np.abs(row.hessian - row.hessian.T)) < 1.0e-10
    parameters = mod.quadratic.parameter_derivatives(analytic)
    audit = mod.quadratic.five_point_directional_audit(
        state, parameters, mod.quadratic.deterministic_coefficients(parameters)
    )
    assert audit["value_residual"] < 1.0e-9
    assert audit["first_residual"] < 2.0e-7
    assert audit["second_residual"] < 2.0e-6


def test_unknown_basis_and_direction_are_rejected(state):
    with pytest.raises(KeyError):
        mod.base_derivative(mod.chart.pack(state), 4)
    unsupported = next(row for row in mod.potential.evaluate_directions(state)
                       if row.base_family != mod.BASE_FAMILY)
    with pytest.raises(KeyError):
        mod.direction_derivative(mod.chart.pack(state), unsupported)
