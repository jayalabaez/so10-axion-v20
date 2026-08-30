#!/usr/bin/env python3
"""Regression tests for the exact authoritative gauge-polynomial audit."""

from fractions import Fraction

import pytest

import exact_authoritative_so10_u1x_gauge_betas_v20 as mod


def test_group_theory_casimir_identity_and_corrected_values():
    assert mod.casimir_so10("16") == Fraction(45, 8)
    assert mod.casimir_so10("10") == Fraction(9, 2)
    assert mod.casimir_so10("126") == Fraction(25, 2)
    assert mod.casimir_so10("210") == Fraction(12)
    for rep in mod.T_SO10:
        assert (
            mod.casimir_so10(rep) * mod.DIM_SO10[rep]
            == mod.dynkin_so10(rep) * mod.DIM_G_SO10
        )


def test_authoritative_multiplicities_and_anomalies():
    assert sum(row.generations for row in mod.AUTHORITATIVE_FERMIONS) == 19
    assert (
        sum(row.generations for row in mod.SO10_BETWEEN_MGUT_AND_VPHI_FERMIONS)
        == 13
    )
    assert mod.anomaly_coefficients(mod.AUTHORITATIVE_FERMIONS) == {
        "SO10_squared_X_in_T10_units": 0,
        "gravity_squared_X": 0,
        "X_cubed": 0,
    }


def test_all_active_exact_gauge_polynomial():
    a = mod.one_loop_coefficients(
        mod.AUTHORITATIVE_FERMIONS, mod.AUTHORITATIVE_SCALARS
    )
    b = mod.two_loop_nonyukawa_matrix(
        mod.AUTHORITATIVE_FERMIONS, mod.AUTHORITATIVE_SCALARS
    )
    assert a == {"SO10": Fraction(52, 3), "X": Fraction(10843)}
    assert b == {
        "SO10": {"SO10": Fraction(25013, 6), "X": Fraction(4536)},
        "X": {"SO10": Fraction(204120), "X": Fraction(7242180)},
    }


def test_mid_interval_exact_so10_polynomial():
    a = mod.one_loop_coefficients(
        mod.SO10_BETWEEN_MGUT_AND_VPHI_FERMIONS, mod.AUTHORITATIVE_SCALARS
    )
    b = mod.two_loop_nonyukawa_matrix(
        mod.SO10_BETWEEN_MGUT_AND_VPHI_FERMIONS, mod.AUTHORITATIVE_SCALARS
    )
    assert a["SO10"] == Fraction(28, 3)
    assert b["SO10"]["SO10"] == Fraction(22283, 6)


def test_gauge_only_pole_integral_is_monotonic_and_fail_closed():
    a = Fraction(28, 3)
    b = Fraction(22283, 6)
    short = mod.gauge_only_pole_log_interval(20.0, a=a, b=b)
    long = mod.gauge_only_pole_log_interval(40.0, a=a, b=b)
    assert 0.0 < short < long
    with pytest.raises(ValueError):
        mod.gauge_only_pole_log_interval(0.0, a=a, b=b)


def test_report_closes_only_scoped_subtheorem():
    report = mod.build_report()
    assert report["status"] == mod.STATUS
    assert report["n_failed"] == 0
    assert all(report["checks"].values())
    flags = report["classification"]
    assert flags["authoritative_field_inventory_closed"]
    assert flags["exact_nonyukawa_two_loop_gauge_polynomial_closed"]
    assert not flags["full_two_loop_gauge_beta_closed"]
    assert not flags["full_two_loop_Yukawa_scalar_dimensionful_EFT_system_closed"]
    assert not flags["component_threshold_matching_closed"]
    assert not flags["physical_G6_input_accepted_for_G7"]
    assert not flags["mathematical_G7_closed"]
    assert not flags["release_G7_verified"]


def test_report_is_deterministic():
    report = mod.build_report()
    assert report["core_sha256"] == mod.EXPECTED_CORE_SHA256
    assert report["source_sha256"] == mod._sha256(mod.Path(mod.__file__).resolve())
