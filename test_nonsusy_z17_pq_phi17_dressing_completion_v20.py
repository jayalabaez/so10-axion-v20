#!/usr/bin/env python3
"""Regression tests for the canonical neutral-Phi17 dressing overlay."""
from __future__ import annotations

import exact_phi17_neutral_dressing_completion_v20 as closure
import nonsusy_z17_pq_phi17_dressing_completion_v20 as mod


def test_completion_report_passes():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["flags"]["complete_mixed_invariant_ring"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_all_fifteen_required_dressings_present_once():
    rows = mod.operator_catalogue(require_x=False)
    names = [row["name"] for row in rows]
    assert len(closure.required_dressing_names()) == 15
    for name in closure.required_dressing_names():
        assert names.count(name) == 1


def test_seven_new_entries_are_allowed_and_multiplicity_one():
    rows = {row["name"]: row for row in mod.operator_catalogue(require_x=False)}
    for addition in closure.ADDITIONS:
        row = rows[addition["name"]]
        assert row["status"] == "ALLOWED"
        assert row["multiplicity"] == 1
        assert row["completion_source"] == (
            "exact_phi17_neutral_dressing_completion_v20"
        )
