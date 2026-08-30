#!/usr/bin/env python3
"""Fail-closed checks for the frozen constructive canonical-G1 channel basis."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CHANNELS = ROOT / "CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json"
FRONTIER = ROOT / "CANONICAL_G1_SCALAR_RING_DIM6_FRONTIER_V21.json"
SOURCE = ROOT / "canonical_g1_susyno_channel_basis_v21.wls"
FIELD_ORDER = ("P", "H", "Hb", "D", "Db")


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _rows():
    channels = _load(CHANNELS)
    frontier = _load(FRONTIER)
    lower = {tuple(row["count_tuple"]): row for row in channels["rows"]}
    upper = {
        tuple(row["count_tuple"]): row
        for row in frontier["exact_character_census"]["rows"]
    }
    return channels, upper, lower


def test_all_constructive_sectors_equal_the_independent_character_census():
    report, upper, lower = _rows()
    assert report["schema"] == "canonical_g1_susyno_channel_basis_v1"
    assert type(report["n_failed"]) is int and report["n_failed"] == 0
    assert len(upper) == len(lower) == 168
    assert set(upper) == set(lower)
    assert all(value is True for value in report["checks"].values())
    for key, expected in upper.items():
        observed = lower[key]
        assert observed["degree"] == expected["degree"]
        assert observed["monomial"] == expected["monomial"]
        assert observed["upper_bound_character_multiplicity"] == expected[
            "so10_singlet_multiplicity"
        ]
        assert observed["constructive_channel_count"] == expected[
            "so10_singlet_multiplicity"
        ] == len(observed["channels"])


def test_every_channel_label_is_typed_unique_and_sequential():
    _report, upper, lower = _rows()
    for key, row in lower.items():
        active = [
            field
            for field in FIELD_ORDER
            if upper[key]["counts"].get(field, 0) > 0
        ]
        labels = row["channels"]
        assert [item["basis_index"] for item in labels] == list(
            range(1, len(labels) + 1)
        )
        assert len({json.dumps(item, sort_keys=True) for item in labels}) == len(
            labels
        )
        for item in labels:
            assert set(item) == {
                "basis_index",
                "plethysm_irreps",
                "plethysm_copy_indices",
                "final_singlet_copy_index",
            }
            assert list(item["plethysm_irreps"]) == active
            assert list(item["plethysm_copy_indices"]) == active
            assert all(
                isinstance(label, list)
                and len(label) == 5
                and all(type(value) is int and value >= 0 for value in label)
                for label in item["plethysm_irreps"].values()
            )
            assert all(
                type(value) is int and value >= 1
                for value in item["plethysm_copy_indices"].values()
            )
            assert type(item["final_singlet_copy_index"]) is int
            assert item["final_singlet_copy_index"] >= 1


def test_degree_totals_and_Hermitian_conjugate_dimensions_are_exact():
    report, upper, lower = _rows()
    totals = {
        degree: sum(
            row["constructive_channel_count"]
            for row in lower.values()
            if row["degree"] == degree
        )
        for degree in range(1, 7)
    }
    assert totals == {1: 0, 2: 5, 3: 6, 4: 40, 5: 119, 6: 721}
    assert sum(totals.values()) == 891
    assert report["construction"]["basis_direction_count"] == 891
    for key, expected in upper.items():
        conjugate = tuple(expected["conjugate_count_tuple"])
        assert conjugate in lower
        assert lower[conjugate]["constructive_channel_count"] == lower[key][
            "constructive_channel_count"
        ]


def test_Wolfram_source_has_a_nonmutating_replay_mode_and_exact_scope_boundary():
    source = SOURCE.read_text(encoding="utf-8")
    assert 'checkMode = MemberQ[$ScriptCommandLine, "--check"]' in source
    assert "frozen channel report drifted" in source
    assert "Component Clebsches are deliberately left to canonical" in source
    report_scope = _load(CHANNELS)["scope"]
    assert report_scope == (
        "derivative-free scalar polynomial operator ring through engineering "
        "dimension six"
    )
