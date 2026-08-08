#!/usr/bin/env python3
"""Regression tests for the complete selected-vacuum H10 mass block."""
from __future__ import annotations

import numpy as np

import exact_complete_h10_selected_vacuum_mass_block_v20 as mod


def test_complete_report_passes_fail_closed():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert all(report["checks"].values())
    assert report["model_contract_id"] == "historical_option_c_no_x_v20"
    assert report["authoritative_for_manuscript"] is False
    assert report["model_wide_no_go_certified"] is False
    assert "NONAUTHORITATIVE" in report["status"]
    assert report["flags"][
        "historical_option_c_H_only_quadratic_block_reproduced"
    ]
    assert report["flags"]["phi17_dressings_allowed_by_manuscript_u1x"] is False
    assert report["flags"]["complete_482_real_Hessian"] is False
    assert report["flags"]["whole_model_validated"] is False


def test_effective_b_contains_both_phi17_orientations():
    value = mod.effective_b(
        kappa10=1.0,
        s_expectation=2.0,
        phi17_expectation=3.0 + 4.0j,
        eta_plus=5.0,
        eta_minus=7.0,
    )
    expected = 2.0 * (1.0 + 5.0 * (3.0 + 4.0j) + 7.0 * (3.0 - 4.0j))
    assert abs(value - expected) < 1.0e-12


def test_holomorphic_block_has_exact_plusminus_spectrum():
    b_value = 0.6 - 0.8j
    matrix = mod.holomorphic_real_mass_matrix(b_value)
    eigenvalues = np.linalg.eigvalsh(matrix)
    assert np.max(np.abs(eigenvalues - np.asarray([-1.0] * 10 + [1.0] * 10))) < 1.0e-12
    assert np.max(np.abs(matrix - matrix.T)) < 1.0e-12
    assert abs(np.trace(matrix)) < 1.0e-12


def test_real_quadratic_form_reconstructs_complex_potential():
    audit = mod.quadratic_reconstruction_audit()
    assert audit["absolute_residual"] < 1.0e-12


def test_stable_and_unstable_examples_are_distinguished():
    report = mod.build_report()
    assert report["stable_benchmark"]["negative_modes"] == 0
    assert report["stable_benchmark"]["minimum_eigenvalue"] > 0.0
    assert report["unstable_benchmark"]["negative_modes"] > 0
    assert report["unstable_benchmark"]["minimum_eigenvalue"] < 0.0
