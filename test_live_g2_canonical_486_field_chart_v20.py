#!/usr/bin/env python3
"""Regression tests for the canonical 486-real G2 field chart."""
from __future__ import annotations

import numpy as np
import pytest

import live_g2_canonical_486_field_chart_v20 as chart


def test_report_passes_without_closing_g2():
    report = chart.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["dimensions"]["total_real"] == 486
    assert report["dimensions"]["symmetric_Hessian_entries"] == 118341
    assert report["flags"]["canonical_486_real_chart_complete"]
    assert report["flags"]["complete_field_gradient"] is False
    assert report["flags"]["complete_field_Hessian"] is False
    assert report["flags"]["G2_closed"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_exact_slice_partition_and_labels():
    assert chart.PHI_SLICE == slice(0, 210)
    assert chart.H_SLICE == slice(210, 230)
    assert chart.SIGMA_SLICE == slice(230, 482)
    assert chart.S_SLICE == slice(482, 484)
    assert chart.X_SLICE == slice(484, 486)
    labels = chart.coordinate_labels()
    assert len(labels) == 486
    assert len(set(labels)) == 486


def test_state_roundtrip_and_kinetic_metric():
    state = chart.values.deterministic_state(486)
    coordinates = chart.pack(state)
    restored = chart.unpack(coordinates)
    audit = chart.state_roundtrip_audit(state)
    assert coordinates.shape == (486,)
    assert max(audit.values()) < 1.0e-11
    assert abs(
        chart.field_kinetic_quadratic(restored)
        - chart.coordinate_kinetic_quadratic(coordinates)
    ) < 1.0e-11


def test_sigma_basis_is_orthonormal_and_physical():
    audit = chart.sigma_basis_audit()
    assert audit["dimension"] == 126
    assert audit["Gram_residual"] < 1.0e-12
    assert audit["maximum_minus_i_Hodge_residual"] < 1.0e-12


def test_selected_one_hot_coordinates_roundtrip():
    audit = chart.selected_one_hot_roundtrip_audit()
    assert audit["indices"] == [0, 209, 210, 229, 230, 481, 482, 483, 484, 485]
    assert audit["maximum_residual"] < 1.0e-12


def test_all_operator_values_and_potential_survive_roundtrip():
    state = chart.values.deterministic_state(486)
    audit = chart.direction_value_roundtrip_audit(state)
    assert audit["direction_count"] == 64
    assert audit["maximum_abs_residual"] < 1.0e-9
    directions = chart.values.evaluate_directions(state)
    parameters = chart.values.parameter_schema(directions)
    coefficients = chart.values.deterministic_coefficients(parameters)
    source = chart.values.potential_value(directions, coefficients)
    restored = chart.potential_from_coordinates(chart.pack(state), coefficients)
    assert abs(source - restored) < 1.0e-9


def test_invalid_coordinate_lengths_are_rejected():
    with pytest.raises(ValueError):
        chart.unpack(np.zeros(485))
    with pytest.raises(ValueError):
        chart.unpack(np.zeros(487))
    with pytest.raises(ValueError):
        chart.coordinate_kinetic_quadratic(np.zeros(485))
