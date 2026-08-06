#!/usr/bin/env python3
"""Regression tests for the multiplicity-two catalogue overlay."""
from __future__ import annotations

import exact_phi2_hdag_sigmabar_two_channel_family_v20 as closure
import nonsusy_z17_pq_phi2_hdag_sigmabar_completion_v20 as mod


def test_completion_report_passes_fail_closed():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["flags"]["complete_mixed_tensor_basis"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_operator_registered_once_with_two_coefficients():
    rows = mod.operator_catalogue(require_x=False)
    matches = [row for row in rows if row["name"] == closure.OPERATOR]
    assert len(matches) == 1
    row = matches[0]
    assert row["status"] == "ALLOWED"
    assert row["multiplicity"] == 2
    assert len(row["channel_names"]) == 2
    assert row["selected_vacuum_HPhi_ranks"] == [3, 4]
