#!/usr/bin/env python3
"""Regression tests for the live 64-direction arbitrary-field G2 compiler."""
from __future__ import annotations

import numpy as np
import pytest

import live_g2_arbitrary_component_potential_values_v20 as mod


@pytest.fixture(scope="module")
def state():
    return mod.deterministic_state()


@pytest.fixture(scope="module")
def directions(state):
    return mod.evaluate_directions(state)


def test_full_report_passes_fail_closed():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["flags"]["all_64_arbitrary_component_values_callable"]
    assert report["flags"]["real_Hermitian_potential_assembled"]
    assert report["flags"]["field_gradient_complete"] is False
    assert report["flags"]["field_Hessian_complete"] is False
    assert report["flags"]["G2_closed"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_exact_counts_and_unique_ids(directions):
    parameters = mod.parameter_schema(directions)
    assert len(directions) == 64
    assert len({row.direction_id for row in directions}) == 64
    assert len({row.orbit_index for row in directions}) == 48
    assert len(parameters) == 91
    assert len({row.parameter_id for row in parameters}) == 91
    assert len(mod.coefficient_jacobian(directions)) == 91


def test_all_18_base_families_are_used(directions):
    actual = {row.base_family for row in directions}
    expected = {row["id"] for row in mod.ledger.BASE_FAMILIES.values()}
    assert actual == expected


def test_self_conjugate_directions_are_real(directions):
    residual = max(
        abs(row.value.imag) for row in directions if row.self_conjugate
    )
    assert residual < 1.0e-9


def test_all_values_are_finite_and_each_family_has_nonzero_probe(directions):
    assert all(np.isfinite(row.value.real) for row in directions)
    assert all(np.isfinite(row.value.imag) for row in directions)
    for family in {row.base_family for row in directions}:
        assert any(
            abs(row.value) > 1.0e-12
            for row in directions
            if row.base_family == family
        )


def test_potential_is_linear_in_91_real_parameters(directions):
    parameters = mod.parameter_schema(directions)
    jacobian = mod.coefficient_jacobian(directions)
    coefficients = mod.deterministic_coefficients(parameters)
    expected = sum(coefficients[name] * jacobian[name] for name in jacobian)
    assert abs(mod.potential_value(directions, coefficients) - expected) < 1.0e-12
    assert mod.potential_value(directions, {}) == 0.0


def test_one_hot_coefficient_convention(directions):
    jacobian = mod.coefficient_jacobian(directions)
    for name in list(jacobian)[:12]:
        assert abs(
            mod.potential_value(directions, {name: 1.0}) - jacobian[name]
        ) < 1.0e-12


def test_unknown_coefficient_is_rejected(directions):
    with pytest.raises(KeyError):
        mod.potential_value(directions, {"not-a-live-parameter": 1.0})


def test_all_64_directions_have_exact_homogeneous_degree(state, directions):
    audit = mod.scaling_audit(state, directions)
    assert audit["maximum_relative_residual"] < 1.0e-8


def test_chiral_sigma_orientation_is_enforced(state):
    bad = mod.FieldState(
        phi=state.phi,
        h=state.h,
        sigma=mod.conjugate_form(state.sigma),
        s=state.s,
        x=state.x,
    )
    with pytest.raises(ValueError):
        bad.validated()
