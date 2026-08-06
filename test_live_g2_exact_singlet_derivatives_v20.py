#!/usr/bin/env python3
"""Regression tests for exact all-64 four-singlet derivatives."""
from __future__ import annotations

import numpy as np
import pytest

import live_g2_exact_singlet_derivatives_v20 as mod


@pytest.fixture(scope="module")
def state():
    return mod.potential.deterministic_state(2404)


@pytest.fixture(scope="module")
def report():
    return mod.build_report()


def test_report_passes_without_closing_g2(report):
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["scope"]["global_indices"] == [482, 483, 484, 485]
    assert report["scope"]["coordinate_names"] == [
        "S.x",
        "S.y",
        "Phi17.x",
        "Phi17.y",
    ]
    assert report["scope"]["complete_gradient_entries"] == 4
    assert report["scope"]["complete_symmetric_Hessian_entries"] == 10
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
    parameters = mod.parameter_jets(operators)
    schema = mod.potential.parameter_schema(
        mod.potential.evaluate_directions(state)
    )
    assert len(operators) == 64
    assert len({row.direction_id for row in operators}) == 64
    assert len(parameters) == 91
    assert {row.parameter_id for row in parameters} == {
        row.parameter_id for row in schema
    }
    assert max(row.value_reconstruction_residual for row in operators) < 1.0e-10


def test_jet_product_rule_and_power():
    local = np.asarray([0.7, -0.2, 0.4, 0.9])
    factors = mod.variable_jets(local)
    jet = factors["S"] ** 2 * factors["Sb"] * factors["X"]
    powers = (2, 1, 1, 0)
    audit = mod.monomial_finite_difference_audit(local, [powers])
    assert abs(jet.value - mod.monomial_value(local, powers)) < 1.0e-14
    assert audit["maximum_gradient_residual"] < 2.0e-7
    assert audit["maximum_Hessian_residual"] < 3.0e-6


def test_parameter_Hessians_are_symmetric(state):
    for row in mod.parameter_jets(mod.operator_jets(state)):
        assert row.gradient.shape == (4,)
        assert row.hessian.shape == (4, 4)
        assert np.max(np.abs(row.hessian - row.hessian.T)) < 1.0e-12


def test_combined_derivatives_match_live_value_and_finite_difference(state):
    directions = mod.potential.evaluate_directions(state)
    schema = mod.potential.parameter_schema(directions)
    coefficients = mod.potential.deterministic_coefficients(schema)
    exact = mod.assemble(
        mod.parameter_jets(mod.operator_jets(state)), coefficients
    )
    audit = mod.combined_finite_difference_audit(state, coefficients)
    assert abs(
        exact["value"] - mod.potential.potential_value(directions, coefficients)
    ) < 1.0e-9
    assert exact["gradient"].shape == (4,)
    assert exact["hessian"].shape == (4, 4)
    assert np.max(np.abs(exact["hessian"] - exact["hessian"].T)) < 1.0e-12
    assert audit["value_residual"] < 1.0e-9
    assert audit["gradient_residual"] < 2.0e-5
    assert audit["Hessian_residual"] < 2.0e-3


def test_invalid_local_coordinate_lengths_are_rejected(state):
    with pytest.raises(ValueError):
        mod.variable_jets(np.zeros(3))
    with pytest.raises(ValueError):
        mod.state_with_local_coordinates(state, np.zeros(5))
