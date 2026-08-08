"""Tests for the exact constructive G3 A-square recoupling."""
from __future__ import annotations

import os
from fractions import Fraction

import pytest

import exact_gauged_u1x_g3_a_square_recoupling_v20 as certificate


def test_recorded_exact_witness_is_nonsingular_and_unique() -> None:
    report = certificate.build_report()
    exact = report["certificate"]
    assert report["n_failed"] == 0
    assert exact["witness_determinant"] == certificate.RECORDED_DETERMINANT
    assert exact["witness_determinant"] != 0
    assert exact["unique_weights"] == tuple(
        Fraction(value) for value in certificate.EXPECTED_WEIGHTS
    )
    assert all(value == 0 for value in exact["identity_residuals"])


def test_recoupling_closes_only_its_exact_subproblem() -> None:
    report = certificate.build_report()
    assert report["flags"]["A_square_recoupling_exactly_source_bound"]
    assert not report["flags"]["complete_potential_BFB_exactly_certified"]
    assert not report["flags"]["full_Hessian_exactly_source_bound"]
    assert not report["flags"]["strict_local_minimum_certified"]
    assert not report["flags"]["G3_closed"]


@pytest.mark.skipif(
    os.environ.get("SO10_RUN_EXACT_A_SQUARE_RECOUPLING") != "1",
    reason="set SO10_RUN_EXACT_A_SQUARE_RECOUPLING=1 for direct integer-source rebuild",
)
def test_direct_integer_source_rebuild_matches_recorded_certificate() -> None:
    report = certificate.build_report(recompute=True)
    exact = report["certificate"]
    assert report["n_failed"] == 0
    assert exact["recomputed"] is True
    assert exact["source_tensor_counts"] == {
        "generator_nonzero_entries": 5040,
        "C_Gaussian_nonzero_entries": 1260,
        "M_Gaussian_nonzero_entries": 12600,
    }
    assert exact["unique_weights"] == tuple(
        Fraction(value) for value in certificate.EXPECTED_WEIGHTS
    )
    assert all(value == 0 for value in exact["identity_residuals"])
