#!/usr/bin/env python3
"""Regression tests for the fail-closed alternative global-SOS audit."""
from fractions import Fraction

import exact_gauged_u1x_g3_alternative_global_sos_audit_v20 as audit


def test_exact_current_gram_excludes_zero_residual_completion() -> None:
    row = audit.exact_current_gram_no_go_certificate()
    assert row["source_maximum_abs_residual"] < 1.0e-12
    assert row["exact_leading_principal_minors"] == (
        Fraction(9, 5),
        Fraction(36, 25),
        Fraction(27, 15625),
    )
    assert row["exact_determinant_at_target"] == Fraction(27, 15625)
    assert row["rank"] == 3
    assert row["positive_definite"]
    assert row["holds_for_every_nonzero_r"]
    assert row["proof_grade"]


def test_reduced_searches_are_diagnostic_and_find_no_lower_witness() -> None:
    row = audit.reduced_numerical_searches()
    assert row["diagnostic_only"]
    assert row["phi_polynomial_validation_residual"] < 1.0e-8
    assert len(row["configurations"]) == 5
    assert not row["any_lower_witness_found"]
    assert all(
        candidate["minimum_gap_found"] >= -audit.LOWER_WITNESS_TOLERANCE
        for candidate in row["configurations"]
    )
    assert all(not candidate["counts_as_global_proof"] for candidate in row["configurations"])


def test_unique_chiral_quartic_zero_residual_routes_are_excluded() -> None:
    row = audit.exact_unique_chiral_quartic_no_go_certificate()
    assert row["source_maximum_abs_residual"] < 1.0e-12
    assert row["O28_quadratic_covariants"]["Gram_determinant"] == Fraction(
        193536, 3125
    )
    assert row["O28_quadratic_covariants"]["linearly_independent"]
    assert row["O31_quadratic_covariant"]["nonzero_isotropic"]
    assert row["all_vanishing_O28_completion_excluded"]
    assert row["all_vanishing_O31_completion_excluded"]
    assert not row["nonvanishing_residual_cancellations_excluded"]
    assert row["proof_grade"]


def test_report_remains_fail_closed() -> None:
    report = audit.build_report()
    flags = report["flags"]
    assert report["n_failed"] == 0
    assert report["status"] == (
        "ALTERNATIVE_GLOBAL_SOS_AUDIT_COMPLETE__NO_CERTIFIED_REPLACEMENT"
    )
    assert flags["all_vanishing_45_current_Gram_completion_excluded"]
    assert flags["all_vanishing_affine_SOS_completion_excluded"]
    assert flags["all_vanishing_unique_chiral_quartic_completion_excluded"]
    assert not flags["globally_certifiable_alternative_found"]
    assert not flags["nonvanishing_residual_gradient_cancellation_excluded"]
    assert not flags["different_vacuum_orbit_excluded"]
    assert not flags["current_candidate_global_minimum_certified"]
    assert not flags["G3_closed"]
    assert not flags["whole_model_excluded"]
