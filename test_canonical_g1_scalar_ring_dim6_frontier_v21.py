#!/usr/bin/env python3
from __future__ import annotations

import os

import pytest

import canonical_g1_scalar_ring_dim6_frontier_v21 as frontier


def test_frozen_frontier_is_integral_and_fail_closed() -> None:
    report = frontier.load_frozen_report()
    assert report["schema"] == "canonical_g1_scalar_ring_dim6_frontier_v1"
    assert report["n_failed"] == 0
    assert report["overall_state"] == "BLOCKED"
    assert report["closure"][
        "scalar_charge_and_character_multiplicities_through_dimension_six_closed"
    ]
    assert not report["closure"]["constructive_normalized_basis_every_sector_closed"]
    assert report["closure"][
        "renormalizable_v3_SARAH_runtime_attestation_closed"
    ]
    assert not report["closure"][
        "canonical_G1_complete_operator_ring_dim6_closed"
    ]


def test_exact_dimension_six_counts_and_truth_boundary() -> None:
    report = frontier.load_frozen_report()
    counts = report["exact_character_census"]["counts"]
    assert counts["charge_and_so10_allowed_multidegrees"] == 168
    assert counts["complex_invariant_multiplicity"] == 891
    assert counts["multidegrees_by_degree"]["5"] == 39
    assert counts["complex_invariant_multiplicity_by_degree"]["5"] == 119
    assert counts["multidegrees_by_degree"]["6"] == 95
    assert counts["complex_invariant_multiplicity_by_degree"]["6"] == 721
    assert (
        report["constructive_basis_frontier"][
            "degree_five_and_six_complex_directions_requiring_construction"
        ]
        == 840
    )
    assert not report["scope"][
        "scope_ambiguity_must_be_resolved_without_silent_narrowing"
    ]
    assert report["scope"][
        "canonical_G1_wording_explicitly_limits_itself_to_this_scope"
    ]
    assert report["v3_SARAH_runtime_attestation"]["valid"] is True


def test_dependency_pins_are_live_and_unique() -> None:
    report = frontier.load_frozen_report()
    pins = report["dependency_pins"]
    assert len(pins) == len(frontier.DEPENDENCY_PATHS)
    assert len({row["path"] for row in pins}) == len(pins)
    assert pins == frontier._dependency_rows()


def test_small_exact_recomputation() -> None:
    rows = frontier.enumerate_rows((2, 3))
    counts = frontier._counts(rows)
    assert counts["charge_and_so10_allowed_multidegrees"] == 11
    assert counts["complex_invariant_multiplicity"] == 11
    assert counts["potential_orbit_multiplicity"] == 9
    assert all(row["charge"] == {"PQ": 0, "X": 0, "Z17": 0} for row in rows)


@pytest.mark.skipif(
    os.environ.get("RUN_CANONICAL_G1_DIM6_HEAVY") != "1",
    reason="set RUN_CANONICAL_G1_DIM6_HEAVY=1 for the exact eight-minute replay",
)
def test_full_exact_recomputation_matches_frozen_bytes() -> None:
    assert frontier.build_report() == frontier.load_frozen_report()
