"""Regression tests for exact Hdag Sigma^2 Sigmadag derivatives."""
from __future__ import annotations

import numpy as np
import pytest

import live_g2_exact_hdag_sigma2_sigmadag_derivatives_v20 as mod


@pytest.fixture(scope="module")
def state():
    return mod.potential.deterministic_state(3004)


@pytest.fixture(scope="module")
def analytic(state):
    return mod.all_direction_derivatives(state)


@pytest.fixture(scope="module")
def report():
    return mod.build_report()


def test_report_passes_without_closing_g2(report):
    assert report["n_failed"] == 0, report["failures"]
    assert report["coverage"]["base_family"] == mod.BASE_FAMILY
    assert report["coverage"]["basis_indices"] == [0]
    assert report["coverage"]["basis_labels"] == list(mod.BASIS_LABELS)
    assert report["flags"]["G2_closed"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_value_matches_authoritative_evaluator_and_hessian_is_symmetric(state, analytic):
    expected = {row.direction_id: row.value for row in mod.selected_directions(state)}
    assert len(analytic) == 1
    for row in analytic:
        assert abs(row.value - expected[row.direction_id]) < 1.0e-10
        assert row.gradient.shape == (486,)
        assert row.hessian.shape == (486, 486)
        assert np.max(np.abs(row.hessian - row.hessian.T)) < 1.0e-12


def test_invalid_basis_is_rejected(state):
    with pytest.raises(KeyError):
        mod.base_derivative(mod.chart.pack(state), 1)
