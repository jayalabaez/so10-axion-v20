#!/usr/bin/env python3
"""Regression tests for the H--Sigma catalogue completion overlay."""
from __future__ import annotations

import exact_hsigma_holomorphic_charge_dressed_completion_v20 as closure
import nonsusy_z17_pq_hsigma_completion_v20 as mod


def test_completion_report_passes():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["flags"]["complete_mixed_invariant_ring"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_completed_catalogue_contains_each_operator_once():
    rows = mod.operator_catalogue(require_x=False)
    names = [row["name"] for row in rows]
    for name in (closure.O54, closure.OPLUS, closure.OMINUS):
        assert names.count(name) == 1
        row = next(item for item in rows if item["name"] == name)
        assert row["status"] == "ALLOWED"
        assert row["multiplicity"] == 1
        assert row["feeds_triplet_mass"] is True


def test_historical_X_comparison_is_explicit():
    rows = {row["name"]: row for row in mod.operator_catalogue(require_x=True)}
    assert rows[closure.O54]["status"] == "ALLOWED"
    assert rows[closure.OPLUS]["status"] == "CHARGE_FORBIDDEN"
    assert rows[closure.OMINUS]["status"] == "CHARGE_FORBIDDEN"
