#!/usr/bin/env python3
"""Tests for the reduced electroweak backreaction gate."""
from __future__ import annotations

import numpy as np

import exact_reduced_ew_backreaction_v20 as mod


def test_gate_closes_reduced_scope():
    report = mod.build_report()
    assert report["status"] == (
        "REDUCED_EW_BACKREACTION_AND_BFB_CLOSED__FULL_TENSOR_MODEL_OPEN"
    )
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())


def test_generic_portals_are_nonzero_stationary_and_bounded():
    report = mod.build_report()
    generic = report["generic_portal_scenario"]
    assert all(abs(value) > 0.0 for value in generic["h_portals"].values())
    assert generic["quartic_positive_definite"] is True
    assert generic["radial_hessian_positive_by_congruence"] is True
    assert generic["stationarity"]["maximum_relative_residual"] < 1.0e-14
    assert generic["global_radial_minimum"] is True
    assert generic["congruence_identity_residual"] == 0.0


def test_mass_reconstruction_and_hessian_identity():
    vevs, _ = mod.target_vevs()
    eps = mod.epsilon_matrix(mod.GENERIC_H_PORTALS)
    mass2 = mod.reconstructed_mass_squared(vevs, eps)
    residual = mod.stationarity_residual(vevs, eps, mass2)
    assert np.max(np.abs(residual["mass_reconstruction_residual_GeV2"])) == 0.0
    b = mod.quartic_matrix(eps)
    hessian = 2.0 * np.diag(vevs) @ b @ np.diag(vevs)
    assert np.allclose(
        hessian,
        np.asarray(mod.scenario("test", vevs, mod.GENERIC_H_PORTALS)["radial_hessian_GeV2"]),
        rtol=0.0,
        atol=0.0,
    )


def test_generic_portals_expose_hierarchy_tuning():
    report = mod.build_report()
    hierarchy = report["generic_portal_scenario"]["electroweak_hierarchy"]
    assert hierarchy["aggregate_abs_portal_over_h_self"] > 1.0e20
    assert hierarchy["largest_abs_portal_over_h_self"] > 1.0e20
    assert max(report["portal_bounds_for_tuning_budget_10"].values()) < 1.0e-12
    assert report["flag"]["generic_portals_naturally_explain_EW_hierarchy"] is False
    assert report["flag"]["UV_sequestering_or_hierarchy_mechanism_required"] is True


def test_sequestered_benchmark_meets_declared_budget():
    report = mod.build_report()
    scenario = report["sequestered_scenario"]
    burden = scenario["electroweak_hierarchy"]["aggregate_abs_portal_over_h_self"]
    assert burden <= 10.0 * (1.0 + 1.0e-12)
    assert scenario["quartic_positive_definite"] is True
    assert scenario["radial_hessian_positive_by_congruence"] is True
    assert scenario["stationarity"]["maximum_relative_residual"] < 1.0e-14


def test_fail_closed_full_theory_flags():
    flags = mod.build_report()["flag"]
    assert flags["complete_tensor_backreaction"] is False
    assert flags["complete_component_potential"] is False
    assert flags["complete_global_vacuum"] is False
    assert flags["whole_model_validated"] is False
    assert flags["empirical_discovery"] is False
