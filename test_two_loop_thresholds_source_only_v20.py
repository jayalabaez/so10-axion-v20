#!/usr/bin/env python3
from __future__ import annotations

import math

import scalar_vacuum_proton_decay_v20 as scalar_pd
import two_loop_thresholds_v20 as thresholds


def test_bracketed_root_solves_without_scipy() -> None:
    root = thresholds.bracketed_root(lambda x: x * x - 2.0, 0.0, 2.0)
    assert abs(root - math.sqrt(2.0)) < 1e-11


def test_source_only_unification_regression() -> None:
    one = thresholds.solve_unification(two_loop=False)
    two = thresholds.solve_unification(two_loop=True)
    assert abs(one["M_I_GeV"] / 6.3139e11 - 1.0) < 2e-3
    assert abs(one["M_GUT_GeV"] / 9.9176e15 - 1.0) < 2e-3
    assert abs(one["alpha_inv_GUT"] - 37.313) < 0.02
    assert abs(one["PS_matching_residual"]) < 1e-10
    assert two["M_I_GeV"] > 0.0
    assert two["M_GUT_GeV"] > two["M_I_GeV"]
    assert two["scheme"] == "heuristic-two-loop-shift-diagnostic"


def test_heuristic_branch_is_explicitly_fail_closed_for_g7() -> None:
    report = thresholds.build_report()
    assert report["status"] == thresholds.STATUS
    assert report["artifact_class"] == "diagnostic_only"
    assert report["n_failed"] == 0
    assert all(report["checks"].values())
    flags = report["flag"]
    assert flags["heuristic_calibrated_two_loop_like_shifts_used"]
    assert not flags["exact_two_loop_beta_system_used"]
    assert not flags["authoritative_full_inventory_gauge_polynomial_used"]
    assert not flags["physical_component_pole_masses_used"]
    assert not flags["heavy_vector_Goldstone_ghost_matching_used"]
    assert not flags["physical_component_threshold_matching_complete"]
    assert flags["diagnostic_only_for_physical_G7"]
    assert not flags["physical_G7_closed"]
    assert not flags["mathematical_G7_closed"]
    assert not flags["release_G7_verified"]
    assert "calibrated additive offsets" in report["honest_limitation"]


def test_scalar_anchor_available_in_clean_source_checkout() -> None:
    anchor = scalar_pd._unification_anchor()
    assert anchor["available"] is True, anchor
    assert anchor["M_I_GeV"] > 0.0
    assert anchor["M_GUT_GeV"] > anchor["M_I_GeV"]
