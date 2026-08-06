#!/usr/bin/env python3
"""Regression tests for five authoritative nonzero G2 derivative adapters."""
from __future__ import annotations

import numpy as np
import pytest

import live_g2_exact_quadratic_family_derivatives_v20 as mod


@pytest.fixture(scope="module")
def state():
    return mod.potential.deterministic_state(2504)


@pytest.fixture(scope="module")
def direction_rows(state):
    return mod.selected_directions(state)


@pytest.fixture(scope="module")
def analytic_rows(state):
    return mod.all_direction_derivatives(state)


def test_full_report_passes_fail_closed():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["coverage"]["base_family_count_closed"] == 5
    assert report["coverage"]["base_family_count_total"] == 18
    assert report["coverage"]["direction_count_closed"] > 0
    assert report["coverage"]["parameter_count_closed"] > 0
    assert all(
        count > 0
        for count in report["coverage"]["expected_direction_counts"].values()
    )
    assert (
        report["coverage"]["expected_direction_counts"]
        == report["coverage"]["observed_direction_counts"]
    )
    assert report["flags"]["five_authoritative_nonzero_family_adapters_closed"]
    assert report["flags"]["all_64_direction_gradients_complete"] is False
    assert report["flags"]["all_64_direction_Hessians_complete"] is False
    assert report["flags"]["G2_closed"] is False


def test_selected_families_are_authoritative_and_nonzero(direction_rows):
    assert set(mod.SELECTED_FAMILIES) == {
        "singlet_polynomial",
        "126bar_norm",
        "Hdag_Hdag_pair",
        "Hdag_H_norm",
        "Phi_norm",
    }
    assert {row.base_family for row in direction_rows} == set(mod.SELECTED_FAMILIES)
    for family in mod.SELECTED_FAMILIES:
        assert any(row.base_family == family for row in direction_rows)


def test_direction_values_match_authoritative_evaluator(direction_rows, analytic_rows):
    expected = {row.direction_id: row.value for row in direction_rows}
    assert expected
    assert {row.direction_id for row in analytic_rows} == set(expected)
    assert max(
        abs(row.value - expected[row.direction_id]) for row in analytic_rows
    ) < 1.0e-10


def test_all_dense_Hessians_are_symmetric_and_finite(analytic_rows):
    assert analytic_rows
    for row in analytic_rows:
        assert row.gradient.shape == (486,)
        assert row.hessian.shape == (486, 486)
        assert np.all(np.isfinite(row.gradient.real))
        assert np.all(np.isfinite(row.gradient.imag))
        assert np.all(np.isfinite(row.hessian.real))
        assert np.all(np.isfinite(row.hessian.imag))
        assert np.max(np.abs(row.hessian - row.hessian.T)) < 1.0e-12


def test_self_conjugate_derivatives_are_real(analytic_rows):
    for row in analytic_rows:
        if row.self_conjugate:
            assert abs(row.value.imag) < 1.0e-10
            assert np.max(np.abs(row.gradient.imag)) < 1.0e-10
            assert np.max(np.abs(row.hessian.imag)) < 1.0e-10


def test_parameter_derivatives_use_live_schema(state, analytic_rows):
    parameters = mod.parameter_derivatives(analytic_rows)
    assert parameters
    live_ids = {
        row.parameter_id
        for row in mod.potential.parameter_schema(
            mod.potential.evaluate_directions(state)
        )
    }
    assert {row.parameter_id for row in parameters}.issubset(live_ids)
    assert len({row.parameter_id for row in parameters}) == len(parameters)


def test_analytic_assembly_matches_five_point_reconstruction(state, analytic_rows):
    parameters = mod.parameter_derivatives(analytic_rows)
    coefficients = mod.deterministic_coefficients(parameters)
    audit = mod.five_point_directional_audit(state, parameters, coefficients)
    assert audit["value_residual"] < 1.0e-9
    assert audit["first_residual"] < 1.0e-8
    assert audit["second_residual"] < 1.0e-7


def test_unknown_family_and_parameter_are_rejected(state, analytic_rows):
    q = mod.chart.pack(state)
    with pytest.raises(KeyError):
        mod.base_derivative(q, "not_a_live_family")
    unsupported = next(
        row
        for row in mod.potential.evaluate_directions(state)
        if row.base_family not in mod.SELECTED_FAMILIES
    )
    with pytest.raises(KeyError):
        mod.direction_derivative(q, unsupported)
    parameters = mod.parameter_derivatives(analytic_rows)
    with pytest.raises(KeyError):
        mod.assemble(parameters, {"not-a-live-derivative": 1.0})


def test_base_quadratic_normalizations_are_canonical(state):
    q = mod.chart.pack(state)
    sigma_value, sigma_gradient, sigma_hessian = mod.base_derivative(
        q, "126bar_norm"
    )
    sigma_block = q[mod.chart.SIGMA_SLICE]
    assert abs(sigma_value.real - 0.5 * np.dot(sigma_block, sigma_block)) < 1.0e-12
    assert np.max(
        np.abs(sigma_gradient[mod.chart.SIGMA_SLICE].real - sigma_block)
    ) < 1.0e-12
    assert np.max(
        np.abs(
            sigma_hessian[
                mod.chart.SIGMA_SLICE, mod.chart.SIGMA_SLICE
            ].real
            - np.eye(mod.chart.SIGMA_REAL_DIM)
        )
    ) < 1.0e-12

    phi_value, phi_gradient, phi_hessian = mod.base_derivative(q, "Phi_norm")
    phi_block = q[mod.chart.PHI_SLICE]
    assert abs(phi_value.real - np.dot(phi_block, phi_block)) < 1.0e-12
    assert np.max(
        np.abs(phi_gradient[mod.chart.PHI_SLICE].real - 2.0 * phi_block)
    ) < 1.0e-12
    assert np.max(
        np.abs(
            phi_hessian[mod.chart.PHI_SLICE, mod.chart.PHI_SLICE].real
            - 2.0 * np.eye(mod.chart.PHI_DIM)
        )
    ) < 1.0e-12
