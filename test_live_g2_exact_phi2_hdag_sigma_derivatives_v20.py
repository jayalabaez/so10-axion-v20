#!/usr/bin/env python3
"""Regression tests for Phi2 Hdag Sigma derivatives."""
from __future__ import annotations

import numpy as np
import pytest

import live_g2_exact_phi2_hdag_sigma_derivatives_v20 as mod


@pytest.fixture(scope="module")
def state():
    return mod.potential.deterministic_state(3707)


@pytest.fixture(scope="module")
def analytic(state):
    return mod.all_direction_derivatives(state)


def test_report_passes_without_closing_g2():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert report["coverage"]["base_family"] == mod.BASE_FAMILY
    assert report["coverage"]["basis_labels"] == list(mod.BASIS_LABELS)
    assert report["flags"]["G2_closed"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_values_shapes_and_symmetry(state, analytic):
    expected = {
        row.direction_id: row.value for row in mod.selected_directions(state)
    }
    assert len(analytic) == len(expected) == 2
    for row in analytic:
        assert abs(row.value - expected[row.direction_id]) < 1.0e-10
        assert row.gradient.shape == (486,)
        assert row.hessian.shape == (486, 486)
        assert np.max(np.abs(row.hessian - row.hessian.T)) < 1.0e-10


def test_unknown_basis_rejected(state):
    with pytest.raises(KeyError):
        mod.base_derivative(mod.chart.pack(state), 2)
