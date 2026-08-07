#!/usr/bin/env python3
from __future__ import annotations

import numpy as np
import pytest

import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_final_mixed_quartic_derivatives_v20 as mod


@pytest.fixture(scope="module")
def state():
    return potential.deterministic_state(3704)


@pytest.fixture(scope="module")
def report():
    return mod.build_report()


def test_report_passes(report):
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["flags"]["final_two_mixed_quartic_adapters_closed"]
    assert report["flags"]["all_eighteen_base_family_adapters_available"]
    assert report["flags"]["G2_closed"] is False


def test_exact_final_coverage(report):
    c = report["coverage"]
    assert c["expected_direction_counts"] == {
        mod.PHISIGMA_FAMILY: 6,
        mod.PHIHSIGMA_FAMILY: 2,
    }
    assert c["observed_direction_counts"] == c["expected_direction_counts"]
    assert c["direction_count_closed_here"] == 8
    assert c["parameter_count_closed_here"] == 10
    assert c["cumulative_base_family_count_with_parents"] == 18
    assert c["remaining_base_families"] == 0


def test_authoritative_values(report):
    assert report["targeted_value_layer_audit"]["maximum_residual"] < 2.0e-11
    assert report["maximum_direction_value_residual"] < 2.0e-11


def test_dense_shapes_and_symmetry(state):
    q = chart.pack(state)
    rows = mod.all_base_derivatives(q)
    assert len(rows[mod.PHISIGMA_FAMILY]) == 6
    assert len(rows[mod.PHIHSIGMA_FAMILY]) == 2
    for family_rows in rows.values():
        for value, gradient, hessian in family_rows:
            assert np.isfinite(value.real) and np.isfinite(value.imag)
            assert gradient.shape == (486,)
            assert hessian.shape == (486, 486)
            assert np.max(np.abs(hessian - hessian.T)) < 1.0e-10


def test_unknown_family_and_basis_rejected(state):
    q = chart.pack(state)
    with pytest.raises(KeyError):
        mod.base_derivative(q, "not_a_family", 0)
    with pytest.raises(KeyError):
        mod.base_derivative(q, mod.PHISIGMA_FAMILY, 6)


def test_independent_directional_reconstruction(report):
    audit = report["directional_reconstruction"]
    assert audit["value_residual"] < 1.0e-9
    assert audit["first_residual"] < 1.0e-7
    assert audit["second_residual"] < 1.0e-6
