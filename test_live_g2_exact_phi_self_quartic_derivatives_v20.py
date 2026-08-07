#!/usr/bin/env python3
"""Regression tests for exact pure-Phi210 quartic derivatives."""
from __future__ import annotations

import numpy as np
import pytest

import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_phi_self_quartic_derivatives_v20 as mod


@pytest.fixture(scope="module")
def state():
    return potential.deterministic_state(3204)


@pytest.fixture(scope="module")
def report():
    return mod.build_report()


def test_report_passes_fail_closed(report):
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["overall_state"] == "PARTIAL"
    assert report["flags"]["authoritative_Phi_self_quartic_adapter_closed"]
    assert report["flags"]["all_four_pair_Casimir_moment_derivatives_exact"]
    assert report["flags"]["cumulative_thirteen_of_eighteen_base_adapters_closed"]
    assert report["flags"]["G2_closed"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_exact_authoritative_coverage(report):
    coverage = report["coverage"]
    assert coverage["base_family"] == "Phi_self_quartics"
    assert coverage["expected_direction_count"] > 0
    assert coverage["observed_direction_count"] == coverage["expected_direction_count"]
    assert coverage["basis_indices"] == [0, 1, 2, 3]
    assert coverage["basis_labels"] == ["J0", "J2", "J3", "J4"]
    assert coverage["real_field_dimension"] == 486
    assert coverage["Hessian_shape"] == [486, 486]
    assert coverage["remaining_base_families"] == 5


def test_values_match_authoritative_source(report):
    assert report["source_normalization_audit"]["maximum_residual"] < 1.0e-8
    assert report["maximum_direction_value_residual"] < 1.0e-8


def test_j0_has_independent_closed_form(report):
    audit = report["J0_closed_form_audit"]
    assert audit["value_residual"] < 1.0e-10
    assert audit["gradient_residual"] < 1.0e-9
    assert audit["Hessian_residual"] < 1.0e-8


def test_base_support_and_hessian_symmetry(state):
    q = chart.pack(state)
    for index in range(4):
        value, gradient, hessian = mod.base_derivative(q, index)
        assert np.isfinite(value.real)
        assert gradient.shape == (486,)
        assert hessian.shape == (486, 486)
        assert np.max(np.abs(hessian - hessian.T)) < 1.0e-8
        assert np.max(np.abs(gradient[chart.H_SLICE])) == 0.0
        assert np.max(np.abs(gradient[chart.SIGMA_SLICE])) == 0.0
        assert np.max(np.abs(gradient[chart.S_SLICE])) == 0.0
        assert np.max(np.abs(gradient[chart.X_SLICE])) == 0.0


def test_unknown_basis_index_rejected(state):
    with pytest.raises(KeyError):
        mod.base_derivative(chart.pack(state), 4)


def test_five_point_reconstruction(report):
    audit = report["directional_reconstruction"]
    assert audit["value_residual"] < 1.0e-7
    assert audit["first_residual"] < 5.0e-6
    assert audit["second_residual"] < 5.0e-5
