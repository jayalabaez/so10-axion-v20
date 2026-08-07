#!/usr/bin/env python3
"""Fail-closed alignment tests for authoritative G1 and G2 family IDs."""
from __future__ import annotations

import live_g1_tensor_closure_ledger_v20 as g1
import live_g2_derivative_coverage_ledger_v20 as coverage
import live_g2_exact_h10_self_quartic_derivatives_v20 as h10
import live_g2_exact_hsigma_hermitian_derivatives_v20 as hsigma
import live_g2_exact_phi2_hdagh_derivatives_v20 as phi2h


EXPECTED_RENAMED = {
    (0, 0, 0, 2, 2): ("126bar_self_projectors", ["54", "1050bar", "2772bar", "4125"]),
    (0, 0, 1, 2, 1): (
        "unique_Hdag_Sigma2_Sigmadag",
        ["graph (0,1,0,2,3,2) on degrees (1,5,5,5)"],
    ),
    (0, 0, 2, 2, 0): (
        "unique_Hdag2_Sigma2",
        ["graph (0,0,1,1,0,4) on degrees (1,1,5,5)"],
    ),
    (0, 1, 1, 1, 1): (
        "H_Sigma_hermitian",
        ["channel_1", "channel_45"],
    ),
    (0, 2, 2, 0, 0): ("H_self_quartics", ["I_1", "I_54"]),
    (2, 0, 0, 1, 1): (
        "Phi2_Sigma_projectors",
        ["1", "45", "210", "770", "5940", "8910"],
    ),
    (2, 0, 1, 1, 0): (
        "Phi2_Hdag_Sigma_210_1050",
        ["210", "1050"],
    ),
    (2, 1, 1, 0, 0): (
        "Phi2_HdagH_channels",
        ["1", "45", "54"],
    ),
}


def test_authoritative_ids_and_labels_are_normalized_once():
    for key, (family_id, labels) in EXPECTED_RENAMED.items():
        row = g1.BASE_FAMILIES[key]
        assert row["id"] == family_id
        assert row["basis"] == labels


def test_all_18_authoritative_family_ids_are_unique():
    ids = [row["id"] for row in g1.BASE_FAMILIES.values()]
    assert len(ids) == 18
    assert len(set(ids)) == 18


def test_implemented_adapter_constants_match_authoritative_ledger():
    assert h10.BASE_FAMILY == g1.BASE_FAMILIES[(0, 2, 2, 0, 0)]["id"]
    assert list(h10.BASIS_LABELS) == g1.BASE_FAMILIES[(0, 2, 2, 0, 0)]["basis"]
    assert hsigma.BASE_FAMILY == g1.BASE_FAMILIES[(0, 1, 1, 1, 1)]["id"]
    assert list(hsigma.BASIS_LABELS) == g1.BASE_FAMILIES[(0, 1, 1, 1, 1)]["basis"]
    assert phi2h.BASE_FAMILY == g1.BASE_FAMILIES[(2, 1, 1, 0, 0)]["id"]
    assert list(phi2h.BASIS_LABELS) == g1.BASE_FAMILIES[(2, 1, 1, 0, 0)]["basis"]


def test_coverage_partition_uses_only_authoritative_ids():
    authoritative = {row["id"] for row in g1.BASE_FAMILIES.values()}
    covered = set(coverage.covered_families())
    remaining = set(coverage.EXPECTED_REMAINING_FAMILIES)
    assert len(covered) == 12
    assert len(remaining) == 6
    assert covered.isdisjoint(remaining)
    assert covered | remaining == authoritative


def test_renamed_ids_do_not_coexist_with_stale_aliases():
    stale = {
        "126bar_self_quartics",
        "Hdag_Sigma2_Sigmadag",
        "Hdag2_Sigma2",
        "H_Sigma_Hermitian_quartics",
        "Phi2_Sigma_Sigmadag",
        "Phi2_Hdag_Sigma",
        "Phi2_Hdag_H",
    }
    authoritative = {row["id"] for row in g1.BASE_FAMILIES.values()}
    assert authoritative.isdisjoint(stale)
