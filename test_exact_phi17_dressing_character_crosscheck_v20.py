#!/usr/bin/env python3
"""Regression tests for the exact D5 Phi17 dressing cross-check."""
from __future__ import annotations

import exact_phi17_dressing_character_crosscheck_v20 as mod


def test_character_crosscheck_passes_fail_closed():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["flags"]["complete_mixed_tensor_basis"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_all_seven_rows_have_exact_multiplicity_one():
    rows = mod.multiplicity_rows()
    assert len(rows) == 7
    assert all(
        row["exact_so10_singlet_multiplicity"] == 1
        for row in rows.values()
    )
    assert all(row["matches"] for row in rows.values())


def test_real_210_dagger_counts_map_to_same_P_field():
    mapped = mod.census_counts({"210_H_dag": 1, "210_H": 1, "Phi17": 1})
    assert mapped == {"P": 2, "X": 1}
