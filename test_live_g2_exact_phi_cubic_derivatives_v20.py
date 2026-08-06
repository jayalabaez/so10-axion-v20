#!/usr/bin/env python3
"""Regression tests for exact derivatives of the unique 210 cubic."""
from __future__ import annotations

import numpy as np

import live_g2_exact_phi_cubic_derivatives_v20 as mod


def test_report_passes_fail_closed():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["coverage"]["base_families_closed_total"] == 7
    assert report["flags"]["B08_derivative_adapter_closed"]
    assert report["flags"]["G2_closed"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_two_form_operator_basis_is_symmetric_and_complete():
    operators = mod.basis_operators()
    assert operators.shape == (210, 45, 45)
    assert np.max(np.abs(operators - np.swapaxes(operators, 1, 2))) < 1.0e-12
    assert np.linalg.matrix_rank(operators.reshape(210, -1), 1.0e-12) == 210


def test_operator_cubic_matches_authoritative_value():
    state = mod.potential.deterministic_state(808)
    derivative = mod.analytic_derivative(state)
    source = mod.selected_direction(state)
    assert abs(derivative.value - source.value.real) < 1.0e-10
    assert abs(source.value.imag) < 1.0e-10


def test_closed_singlet_formula_matches_operator_and_source():
    audit = mod.singlet_formula_audit()
    assert audit["operator_authoritative_residual"] < 1.0e-12
    assert audit["operator_formula_residual"] < 1.0e-12


def test_gradient_and_Hessian_have_only_Phi_support():
    state = mod.potential.deterministic_state(808)
    derivative = mod.analytic_derivative(state)
    outside = np.ones(486, dtype=bool)
    outside[mod.chart.PHI_SLICE] = False
    assert np.max(np.abs(derivative.gradient[outside])) < 1.0e-15
    assert np.max(np.abs(derivative.hessian[np.ix_(outside, outside)])) < 1.0e-15
    assert np.max(np.abs(derivative.hessian[np.ix_(outside, ~outside)])) < 1.0e-15
    assert np.max(np.abs(derivative.hessian - derivative.hessian.T)) < 1.0e-12


def test_five_point_reconstruction_matches_exact_derivatives():
    state = mod.potential.deterministic_state(808)
    derivative = mod.analytic_derivative(state)
    audit = mod.directional_audit(state, derivative)
    assert audit["value_residual"] < 1.0e-9
    assert audit["first_residual"] < 1.0e-8
    assert audit["second_residual"] < 1.0e-7


def test_gradient_and_Hessian_formulas_by_small_direction():
    state = mod.potential.deterministic_state(808)
    q = mod.chart.pack(state)
    derivative = mod.analytic_derivative(state)
    direction = np.zeros(486)
    direction[0] = 0.6
    direction[17] = -0.8
    direction /= np.linalg.norm(direction)
    step = 0.03

    def value(offset):
        return mod.authoritative_value(q + offset * direction, derivative.direction_id)

    first = (value(-2*step)-8*value(-step)+8*value(step)-value(2*step))/(12*step)
    second = (-value(2*step)+16*value(step)-30*value(0)+16*value(-step)-value(-2*step))/(12*step**2)
    assert abs(first - derivative.gradient @ direction) < 1.0e-8
    assert abs(second - direction @ derivative.hessian @ direction) < 1.0e-7
