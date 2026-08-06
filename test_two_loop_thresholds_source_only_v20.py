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


def test_scalar_anchor_available_in_clean_source_checkout() -> None:
    anchor = scalar_pd._unification_anchor()
    assert anchor["available"] is True, anchor
    assert anchor["M_I_GeV"] > 0.0
    assert anchor["M_GUT_GeV"] > anchor["M_I_GeV"]
