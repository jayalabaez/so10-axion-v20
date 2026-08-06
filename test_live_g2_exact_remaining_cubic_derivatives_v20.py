#!/usr/bin/env python3
"""Regression tests for the pure-Phi and Phi-Sigma cubic derivatives."""
from __future__ import annotations

import numpy as np
import pytest

import live_g2_exact_remaining_cubic_derivatives_v20 as mod


@pytest.fixture(scope="module")
def state():
    return mod.potential.deterministic_state(2704)


@pytest.fixture(scope="module")
def analytic(state):
    return mod.all_direction_derivatives(state)


def test_report_passes_without_closing_G2():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["coverage"]["base_families_closed"] == [
        "Phi_Sigma_Sigmadag_cubic",
        "Phi_cubic",
    ]
    assert report["coverage"]["base_family_count_closed_here"] == 2
    assert report["coverage"]["cumulative_base_family_count_with_parents"] == 9
    assert report["coverage"]["base_family_count_total"] == 18
    assert report["coverage"]["remaining_base_families"] == 9
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
    assert report["flags"]["remaining_two_cubic_base_adapters_closed"]
    assert report["flags"]["all_cubic_base_adapters_closed_cumulatively"]
    assert report["flags"]["all_64_direction_gradients_complete"] is False
    assert report["flags"]["all_64_direction_Hessians_complete"] is False
    assert report["flags"]["G2_closed"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_exact_coefficient_operator_shapes_and_symmetries():
    phi_basis = mod.phi_two_form_basis()
    operators = mod.phi_sigma_operators()
    assert phi_basis.shape == (210, 45, 45)
    assert np.max(np.abs(phi_basis - np.swapaxes(phi_basis, 1, 2))) < 1.0e-15
    assert operators.shape == (210, 126, 126)
    assert np.count_nonzero(np.abs(operators) > 1.0e-14) > 0
    assert (
        np.max(np.abs(operators - np.swapaxes(operators.conj(), 1, 2)))
        < 1.0e-12
    )


def test_undressed_base_values_match_original_source_evaluators(state):
    q = mod.chart.pack(state)
    phi_value, _, _ = mod.base_derivative(q, "Phi_cubic")
    mixed_value, _, _ = mod.base_derivative(
        q, "Phi_Sigma_Sigmadag_cubic"
    )
    expected_phi = mod.phi_self.cubic_invariant(state.phi)
    expected_mixed = mod.phi_sigma_source.cubic_invariant(
        state.phi, state.sigma, state.sigma
    )
    assert abs(phi_value - expected_phi) < 1.0e-10
    assert abs(mixed_value - expected_mixed) < 1.0e-9


def test_selected_families_are_authoritative_and_nonzero(state, analytic):
    directions = mod.selected_directions(state)
    assert {row.base_family for row in directions} == set(mod.SELECTED_FAMILIES)
    assert {row.base_family for row in analytic} == set(mod.SELECTED_FAMILIES)
    for family in mod.SELECTED_FAMILIES:
        assert any(row.base_family == family for row in analytic)


def test_all_dressed_values_match_authoritative_evaluator(state, analytic):
    expected = {
        row.direction_id: row.value for row in mod.selected_directions(state)
    }
    assert expected
    assert {row.direction_id for row in analytic} == set(expected)
    assert max(
        abs(row.value - expected[row.direction_id]) for row in analytic
    ) < 1.0e-9


def test_base_support_and_dense_Hessian_contracts(state, analytic):
    audit = mod.base_support_audit(mod.chart.pack(state))
    assert set(audit) == set(mod.SELECTED_FAMILIES)
    for row in audit.values():
        assert row["inactive_gradient_residual"] < 1.0e-11
        assert row["inactive_Hessian_residual"] < 1.0e-11
        assert row["forbidden_block_residual"] < 1.0e-11
    for row in analytic:
        assert row.gradient.shape == (486,)
        assert row.hessian.shape == (486, 486)
        assert np.all(np.isfinite(row.gradient.real))
        assert np.all(np.isfinite(row.gradient.imag))
        assert np.all(np.isfinite(row.hessian.real))
        assert np.all(np.isfinite(row.hessian.imag))
        assert np.max(np.abs(row.hessian - row.hessian.T)) < 1.0e-11
        if row.self_conjugate:
            assert abs(row.value.imag) < 1.0e-9
            assert np.max(np.abs(row.gradient.imag)) < 1.0e-9
            assert np.max(np.abs(row.hessian.imag)) < 1.0e-9


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
    assert audit["value_residual"] < 1.0e-8
    assert audit["first_residual"] < 2.0e-7
    assert audit["second_residual"] < 2.0e-6


def test_unknown_family_and_direction_are_rejected(state):
    q = mod.chart.pack(state)
    with pytest.raises(KeyError):
        mod.base_derivative(q, "not_a_cubic_family")
    unsupported = next(
        row
        for row in mod.potential.evaluate_directions(state)
        if row.base_family not in mod.SELECTED_FAMILIES
    )
    with pytest.raises(KeyError):
        mod.direction_derivative(q, unsupported)
