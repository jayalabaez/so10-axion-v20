#!/usr/bin/env python3
"""Regression tests for the exact four-singlet G2 derivative block."""
from __future__ import annotations

import numpy as np
import pytest

import live_g2_exact_singlet_derivatives_v20 as mod


@pytest.fixture(scope="module")
def state():
    return mod.values.deterministic_state(2404)


@pytest.fixture(scope="module")
def report():
    return mod.build_report()


def test_report_passes_without_closing_g2(report):
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["scope"]["global_coordinate_indices"] == [482, 483, 484, 485]
    assert report["scope"]["singlet_gradient_entries_complete"] == 4
    assert report["scope"]["singlet_symmetric_Hessian_entries_complete"] == 10
    assert report["scope"]["full_gradient_entries_required"] == 486
    assert report["scope"]["full_symmetric_Hessian_entries_required"] == 118341
    assert report["flags"]["singlet_gradient_4_complete"]
    assert report["flags"]["singlet_Hessian_4x4_complete"]
    assert report["flags"]["complete_486_gradient"] is False
    assert report["flags"]["complete_486_Hessian"] is False
    assert report["flags"]["G2_closed"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_all_64_operator_and_91_parameter_jets_exist(state):
    operators = mod.operator_jets(state)
    parameters = mod.parameter_derivative_tensors(state)
    assert len(operators) == 64
    assert len({row["direction_id"] for row in operators}) == 64
    assert len(parameters) == 91
    assert len(set(parameters)) == 91
    assert max(row["value_reconstruction_residual"] for row in operators) < 1.0e-10


def test_jet_product_rule_and_power_are_exact():
    q = np.asarray([0.7, -0.2, 0.4, 0.9])
    variables = mod.singlet_variable_jets(q)
    jet = variables["S"] ** 2 * variables["Sb"] * variables["X"]
    exponents = (2, 1, 1, 0)
    audit = mod.monomial_finite_difference_audit(q, [exponents])
    assert abs(jet.value - mod.monomial_value(q, exponents)) < 1.0e-14
    assert audit["maximum_gradient_residual"] < 2.0e-7
    assert audit["maximum_hessian_residual"] < 3.0e-6


def test_parameter_resolved_hessians_are_symmetric(state):
    tensors = mod.parameter_derivative_tensors(state)
    for tensor in tensors.values():
        gradient = np.asarray(tensor["gradient"])
        hessian = np.asarray(tensor["hessian"])
        assert gradient.shape == (4,)
        assert hessian.shape == (4, 4)
        assert np.max(np.abs(hessian - hessian.T)) < 1.0e-12


def test_combined_jet_matches_full_potential_and_finite_difference(state):
    directions = mod.values.evaluate_directions(state)
    parameters = mod.values.parameter_schema(directions)
    coefficients = mod.values.deterministic_coefficients(parameters)
    exact = mod.potential_singlet_jet(state, coefficients)
    direct = mod.values.potential_value(directions, coefficients)
    finite = mod.combined_finite_difference_audit(state, coefficients)
    assert abs(exact["value"] - direct) < 1.0e-9
    assert np.asarray(exact["gradient"]).shape == (4,)
    assert np.asarray(exact["hessian"]).shape == (4, 4)
    assert np.max(np.abs(exact["hessian"] - exact["hessian"].T)) < 1.0e-12
    assert finite["value_residual"] < 1.0e-9
    assert finite["gradient_max_abs_residual"] < 2.0e-5
    assert finite["hessian_max_abs_residual"] < 2.0e-3


def test_invalid_singlet_coordinate_lengths_are_rejected(state):
    with pytest.raises(ValueError):
        mod.singlet_variable_jets(np.zeros(3))
    with pytest.raises(ValueError):
        mod.singlet_state_from_coordinates(state, np.zeros(5))
