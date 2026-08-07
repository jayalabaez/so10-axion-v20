#!/usr/bin/env python3
from __future__ import annotations

import numpy as np
import pytest

import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_unique_hsigma_chiral_derivatives_v20 as mod


@pytest.fixture(scope="module")
def state():
    return potential.deterministic_state(3404)


@pytest.fixture(scope="module")
def report():
    return mod.build_report()


def test_report_passes(report):
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["flags"]["both_unique_chiral_HSigma_adapters_closed"]
    assert report["flags"]["cumulative_sixteen_of_eighteen_base_adapters_closed"]
    assert report["flags"]["G2_closed"] is False


def test_exact_coverage(report):
    c = report["coverage"]
    assert set(c["base_families_closed_here"]) == set(mod.SELECTED_FAMILIES)
    assert c["expected_direction_counts"] == {mod.FAMILY_A: 1, mod.FAMILY_B: 1}
    assert c["observed_direction_counts"] == c["expected_direction_counts"]
    assert c["parameter_count_closed_here"] == 4
    assert c["cumulative_base_family_count_with_parents"] == 16
    assert c["remaining_base_families"] == 2


def test_authoritative_values(report):
    assert report["targeted_value_layer_audit"]["maximum_residual"] < 1.0e-10
    assert report["maximum_direction_value_residual"] < 1.0e-10


def test_dense_shapes_symmetry_and_support(state):
    q = chart.pack(state)
    active = np.zeros(chart.TOTAL_DIM, dtype=bool)
    active[chart.H_SLICE] = True
    active[chart.SIGMA_SLICE] = True
    for family in mod.SELECTED_FAMILIES:
        value, gradient, hessian = mod.base_derivative(q, family)
        assert np.isfinite(value.real) and np.isfinite(value.imag)
        assert gradient.shape == (486,)
        assert hessian.shape == (486, 486)
        assert np.max(np.abs(hessian - hessian.T)) < 1.0e-10
        assert np.max(np.abs(gradient[~active]), initial=0.0) == 0.0
        assert np.max(np.abs(hessian[~active, :]), initial=0.0) == 0.0
        assert np.max(np.abs(hessian[:, ~active]), initial=0.0) == 0.0


def test_unknown_family_rejected(state):
    with pytest.raises(KeyError):
        mod.base_derivative(chart.pack(state), "not_a_family")


def test_independent_directional_reconstruction(report):
    audit = report["directional_reconstruction"]
    assert audit["value_residual"] < 1.0e-10
    assert audit["first_residual"] < 1.0e-8
    assert audit["second_residual"] < 1.0e-8
