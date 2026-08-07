#!/usr/bin/env python3
"""Regression tests for the first full-coordinate G3 stationarity gate."""
from __future__ import annotations

import g3_full_stationarity_feasibility_v20 as mod


def test_g3_first_order_gate_executes_without_overclaiming():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["overall_state"] == "PARTIAL"
    assert report["flags"]["G1_closed"]
    assert report["flags"]["G2_closed"]
    assert report["flags"]["G3_first_order_feasibility_executed"]
    assert report["flags"]["G3_closed"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_stationarity_matrix_has_complete_parameter_coverage():
    report = mod.build_report()
    matrix = report["stationarity_matrix"]
    assert matrix["shape"] == [486, 91]
    assert matrix["nonzero_parameter_columns"] + matrix[
        "zero_parameter_columns_at_candidate"
    ] == 91
    assert matrix["independent_constraint_rank"] == 7
    assert matrix["total_coupling_nullity"] == 84
    assert matrix["active_parameter_nullity"] == 46
    assert matrix["active_coordinate_row_count"] == 21


def test_explicit_stationarity_witness_and_gauge_identity_pass():
    report = mod.build_report()
    matrix = report["stationarity_matrix"]
    gauge = report["gauge_invariance"]
    assert matrix["stationary_gradient_relative_residual"] < 1.0e-10
    assert gauge["orbit_matrix_shape"] == [486, 45]
    assert gauge["orbit_rank"] == 33
    assert gauge["maximum_Ward_residual"] < 1.0e-10


def test_fast_projector_gradients_match_independent_values():
    audit = mod.build_report()["fast_gradient_audit"]
    assert audit["parameter_count"] == 18
    assert audit["relative_residual"] < 2.0e-8


def test_scientific_boundary_is_explicit():
    report = mod.build_report()
    interpretation = report["scientific_interpretation"]
    assert interpretation["first_order_stationarity_feasible"]
    assert interpretation["stationarity_uniquely_determines_couplings"] is False
    assert interpretation["coupling_solution_dimension"] == 84
    assert "gauge-quotiented Hessian" in interpretation["reason_G3_remains_open"]
