#!/usr/bin/env python3
"""Regression tests for exact derivatives of both cubic portal families."""
from __future__ import annotations

import numpy as np
import pytest

import live_g2_exact_portal_family_derivatives_v20 as mod


@pytest.fixture(scope="module")
def state():
    return mod.potential.deterministic_state(2604)


@pytest.fixture(scope="module")
def analytic(state):
    return mod.all_direction_derivatives(state)


def test_report_passes_without_closing_G2():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["coverage"]["base_families_closed"] == [
        "Phi_Hdag_Sigmadag",
        "Phi_Hdag_Sigma",
    ]
    assert report["coverage"]["base_family_count_closed_here"] == 2
    assert report["coverage"]["cumulative_base_family_count_with_parent"] == 7
    assert report["coverage"]["base_family_count_total"] == 18
    assert report["coverage"]["direction_count_closed_here"] > 0
    assert report["coverage"]["parameter_count_closed_here"] > 0
    assert all(
        count > 0
        for count in report["coverage"]["expected_direction_counts"].values()
    )
    assert (
        report["coverage"]["expected_direction_counts"]
        == report["coverage"]["observed_direction_counts"]
    )
    assert report["flags"]["two_portal_base_derivative_adapters_closed"]
    assert report["flags"]["all_64_direction_gradients_complete"] is False
    assert report["flags"]["all_64_direction_Hessians_complete"] is False
    assert report["flags"]["G2_closed"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_portal_tensor_and_direct_dagger_tensor():
    tensor = mod.portal_tensor()
    dagger = mod.portal_tensor_dagger_direct()
    assert tensor.shape == (10, 210, 126)
    assert dagger.shape == tensor.shape
    assert np.count_nonzero(np.abs(tensor) > 1.0e-14) > 0
    assert np.max(np.abs(dagger - np.conjugate(tensor))) < 1.0e-15


def test_selected_families_are_authoritative_and_nonzero(state, analytic):
    directions = mod.selected_directions(state)
    assert {row.base_family for row in directions} == set(mod.SELECTED_FAMILIES)
    assert {row.base_family for row in analytic} == set(mod.SELECTED_FAMILIES)
    for family in mod.SELECTED_FAMILIES:
        assert any(row.base_family == family for row in analytic)


def test_base_derivatives_have_only_expected_cross_blocks(state):
    audit = mod.base_support_audit(mod.chart.pack(state))
    assert set(audit) == set(mod.SELECTED_FAMILIES)
    for row in audit.values():
        assert row["inactive_gradient_residual"] < 1.0e-12
        assert row["inactive_Hessian_residual"] < 1.0e-12
        assert row["same_field_Hessian_residual"] < 1.0e-12


def test_all_values_match_authoritative_evaluator(state, analytic):
    expected = {
        row.direction_id: row.value for row in mod.selected_directions(state)
    }
    assert expected
    assert {row.direction_id for row in analytic} == set(expected)
    assert max(
        abs(row.value - expected[row.direction_id]) for row in analytic
    ) < 1.0e-10


def test_all_dense_Hessians_are_symmetric_and_finite(analytic):
    assert analytic
    for row in analytic:
        assert row.gradient.shape == (486,)
        assert row.hessian.shape == (486, 486)
        assert np.all(np.isfinite(row.gradient.real))
        assert np.all(np.isfinite(row.gradient.imag))
        assert np.all(np.isfinite(row.hessian.real))
        assert np.all(np.isfinite(row.hessian.imag))
        assert np.max(np.abs(row.hessian - row.hessian.T)) < 1.0e-12


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


def test_unknown_family_and_direction_are_rejected(state):
    q = mod.chart.pack(state)
    with pytest.raises(KeyError):
        mod.base_derivative(q, "not_a_portal")
    unsupported = next(
        row
        for row in mod.potential.evaluate_directions(state)
        if row.base_family not in mod.SELECTED_FAMILIES
    )
    with pytest.raises(KeyError):
        mod.direction_derivative(q, unsupported)
