#!/usr/bin/env python3
"""Regression tests for the joint H10 cross-coupling Schur envelope."""
from __future__ import annotations

import numpy as np

import exact_joint_h10_cross_schur_stability_v20 as mod


def test_joint_report_passes_fail_closed():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["flags"]["joint_necessary_and_sufficient_local_bound"]
    assert report["flags"]["complete_G2_component_potential"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_six_real_coefficient_basis_blocks_are_constructed():
    basis = mod.basis_blocks()
    assert basis["old"].shape[0] == 6
    assert basis["physical"].shape[0] == 6
    assert [row["name"] for row in basis["rows"]] == list(mod.COEFFICIENT_NAMES)
    assert all(row["gauge_residual"] < 1.0e-9 for row in basis["rows"])


def test_complex_cubic_unit_matches_authoritative_block():
    audit = mod.cubic_unit_reconstruction_audit()
    assert audit["maximum_abs_residual"] < 1.0e-12
    assert audit["reconstructed_rank"] == audit["authoritative_rank"]


def test_direct_combination_matches_six_basis_expansion():
    coefficients = mod.coefficient_vector(
        mu_d=0.4 + 0.3j,
        eta_210=-0.2 + 0.1j,
        eta_1050=0.15 - 0.07j,
    )
    direct = mod.combined_old_to_h(
        mu_d=0.4 + 0.3j,
        eta_210=-0.2 + 0.1j,
        eta_1050=0.15 - 0.07j,
    )
    expanded = mod.linear_combination_from_basis(coefficients)["old"]
    assert np.max(np.abs(direct - expanded)) < 1.0e-12


def test_operator_gram_reconstructs_joint_schur_operator():
    coefficients = mod.coefficient_vector(
        mu_d=0.3 - 0.2j,
        eta_210=0.11 + 0.06j,
        eta_1050=-0.08 + 0.04j,
    )
    schur = mod.schur_from_coefficients(coefficients)
    assert schur["symmetry_residual"] < 1.0e-10
    assert schur["gram_reconstruction_residual"] < 1.0e-9
    assert schur["lambda_min"] > -1.0e-8


def test_critical_mass_separates_stable_flat_and_tachyonic_regions():
    report = mod.build_report()
    above = report["benchmarks"]["above"]
    equality = report["benchmarks"]["equality"]
    below = report["benchmarks"]["below"]
    assert above["loewner_minimum"] > 0.0
    assert above["spectrum"]["physical_negative_modes"] == 0
    assert above["spectrum"]["physical_zero_modes"] == 0
    assert above["spectrum"]["full_zero_modes"] == 33
    assert abs(equality["loewner_minimum"]) < 1.0e-7
    assert equality["spectrum"]["physical_zero_modes"] >= 1
    assert below["loewner_minimum"] < 0.0
    assert below["spectrum"]["physical_negative_modes"] >= 1
