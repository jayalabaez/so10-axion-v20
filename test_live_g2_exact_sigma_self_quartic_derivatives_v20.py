#!/usr/bin/env python3
"""Regression tests for exact 126bar self-projector derivatives."""
from __future__ import annotations

import numpy as np
import pytest

import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_sigma_self_quartic_derivatives_v20 as mod


@pytest.fixture(scope="module")
def state():
    return potential.deterministic_state(3304)


@pytest.fixture(scope="module")
def report():
    return mod.build_report()


def test_report_passes_fail_closed(report):
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["overall_state"] == "PARTIAL"
    assert report["flags"]["authoritative_126bar_self_projector_adapter_closed"]
    assert report["flags"]["all_four_projector_derivatives_exact"]
    assert report["flags"]["cumulative_fourteen_of_eighteen_base_adapters_closed"]
    assert report["flags"]["G2_closed"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_exact_authoritative_coverage(report):
    coverage = report["coverage"]
    assert coverage["base_family"] == "126bar_self_projectors"
    assert coverage["expected_direction_count"] == 4
    assert coverage["observed_direction_count"] == 4
    assert coverage["parameter_count_closed_here"] == 4
    assert coverage["basis_indices"] == [0, 1, 2, 3]
    assert coverage["basis_labels"] == ["1050bar", "2772bar", "4125", "54"]
    assert coverage["real_field_dimension"] == 486
    assert coverage["Hessian_shape"] == [486, 486]
    assert coverage["remaining_base_families"] == 4


def test_values_match_authoritative_source(report):
    assert report["source_normalization_audit"]["maximum_residual"] < 1.0e-12
    assert report["maximum_direction_value_residual"] < 1.0e-12


def test_base_support_and_hessian_symmetry(state):
    q = chart.pack(state)
    for index in range(4):
        value, gradient, hessian = mod.base_derivative(q, index)
        assert np.isfinite(value.real)
        assert gradient.shape == (486,)
        assert hessian.shape == (486, 486)
        assert np.max(np.abs(hessian - hessian.T)) < 1.0e-10
        assert np.max(np.abs(gradient[chart.PHI_SLICE])) == 0.0
        assert np.max(np.abs(gradient[chart.H_SLICE])) == 0.0
        assert np.max(np.abs(gradient[chart.S_SLICE])) == 0.0
        assert np.max(np.abs(gradient[chart.X_SLICE])) == 0.0


def test_unknown_basis_index_rejected(state):
    with pytest.raises(KeyError):
        mod.base_derivative(chart.pack(state), 4)


def test_independent_directional_reconstruction(report):
    audit = report["directional_reconstruction"]
    assert audit["value_residual"] < 1.0e-12
    assert audit["first_residual"] < 1.0e-10
    assert audit["second_residual"] < 1.0e-9
