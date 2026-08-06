#!/usr/bin/env python3
from __future__ import annotations

import numpy as np

import exact_hsigma_hermitian_family_closure_v20 as family


def test_representation_inventory_is_complete_and_multiplicity_free() -> None:
    assert sum(k * v for k, v in family.H_BILINEAR_IRREPS.items()) == 100
    assert sum(k * v for k, v in family.SIGMA_BILINEAR_IRREPS.items()) == 126**2
    assert family.COMMON_IRREPS == {1: 1, 45: 1}


def test_canonical_background_norms() -> None:
    values = family.background_norms(h_u=0.37, h_d=-0.19, v_r=0.83)
    assert abs(values["n_H0"] - (0.37**2 + 0.19**2)) < 1e-12
    assert abs(values["n_Sigma0"] - 0.83**2) < 1e-12


def test_exact_singlet_tensor_expansion_matches_formula_all_colors() -> None:
    inputs = {
        "h_u": 0.13,
        "h_d": 0.07,
        "v_r": 0.9,
        "lambda_hsigma_1": 0.31,
    }
    expected = family.analytic_singlet_blocks(**inputs)
    for color_index in range(3):
        observed = family.extract_singlet_blocks(color_index=color_index, **inputs)
        for key in expected:
            assert np.max(np.abs(observed[key] - expected[key])) < 1e-10
        assert observed["reconstruction_residual"] < 1e-10
        assert np.max(np.abs(observed["cross_charge_Hermitian_diagnostic"])) < 1e-10
        assert np.max(np.abs(observed["same_charge_holomorphic_diagnostic"])) < 1e-10
        assert np.max(np.abs(observed["self_holomorphic_diagnostic"])) < 1e-10


def test_combined_family_closed_formula() -> None:
    blocks = family.analytic_family_blocks(
        h_u=0.2,
        h_d=-0.1,
        v_r=0.8,
        lambda_hsigma_1=0.3,
        lambda_hsigma_45=-0.2,
    )
    h2 = 0.2**2 + 0.1**2
    assert np.allclose(blocks["A_u_GeV2"], np.diag([(0.3 + 0.2) * 0.8**2, 0.3 * h2]))
    assert np.allclose(
        blocks["A_v_GeV2"],
        np.diag([(0.3 - 0.2) * 0.8**2, 0.3 * h2, 0.3 * h2]),
    )
    assert np.max(np.abs(blocks["B_holomorphic_GeV2"])) == 0.0


def test_authoritative_report_passes_without_overclaim() -> None:
    report = family.build_report()
    assert report["n_failed"] == 0
    assert report["flag"]["all_HSigma_Hermitian_bilinear_quartics_complete"] is True
    assert report["flag"]["all_HSigma_invariants_complete"] is False
    assert report["flag"]["complete_component_potential"] is False
    assert report["flag"]["physical_triplet_spectrum_complete"] is False
    assert report["flag"]["exact_unique_proton_lifetime"] is False
    assert report["flag"]["whole_model_validated"] is False
    assert report["flag"]["empirical_discovery"] is False
