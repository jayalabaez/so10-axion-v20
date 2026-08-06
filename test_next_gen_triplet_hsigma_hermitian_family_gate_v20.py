#!/usr/bin/env python3
from __future__ import annotations

import copy

import numpy as np
import pytest

import exact_hsigma_hermitian_family_closure_v20 as family
import next_gen_triplet_hsigma_hermitian_family_gate_v20 as gate


def test_background_norm_contract_is_fail_closed() -> None:
    norm, residuals, inputs = gate._inputs()
    bad = copy.deepcopy(norm)
    bad["h_norm_sq"] += 0.01
    with pytest.raises(ValueError):
        gate.build_with_hsigma_hermitian_family(
            norm_parameters=bad,
            anisotropic_residual_m2=residuals,
            **inputs,
        )


def test_45_is_inserted_once_and_does_not_change_B() -> None:
    norm, residuals, inputs = gate._inputs()
    full = gate.build_with_hsigma_hermitian_family(
        norm_parameters=norm,
        anisotropic_residual_m2=residuals,
        **inputs,
    )
    zero_inputs = dict(inputs)
    zero_inputs["lambda_hsigma_45"] = 0.0
    base = gate.build_with_hsigma_hermitian_family(
        norm_parameters=norm,
        anisotropic_residual_m2=residuals,
        **zero_inputs,
    )
    expected_family = family.analytic_family_blocks(
        h_u=inputs["h_u"],
        h_d=inputs["h_d"],
        v_r=inputs["v_r"],
        lambda_hsigma_1=norm["lambda10_126"],
        lambda_hsigma_45=inputs["lambda_hsigma_45"],
    )
    expected_singlet = family.analytic_singlet_blocks(
        h_u=inputs["h_u"],
        h_d=inputs["h_d"],
        v_r=inputs["v_r"],
        lambda_hsigma_1=norm["lambda10_126"],
    )
    for key in expected_family:
        observed = full[key] - base[key]
        expected = expected_family[key] - expected_singlet[key]
        assert np.max(np.abs(observed - expected)) < 1e-12
    assert np.max(np.abs(full["B_holomorphic_GeV2"] - base["B_holomorphic_GeV2"])) < 1e-12


def test_authoritative_integration_report_passes_without_overclaim() -> None:
    report = gate.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert report["flag"]["complete_HSigma_Hermitian_bilinear_family_inserted"] is True
    assert report["flag"]["all_HSigma_invariants_complete"] is False
    assert report["flag"]["complete_component_potential"] is False
    assert report["flag"]["physical_triplet_spectrum_complete"] is False
    assert report["flag"]["exact_unique_proton_lifetime"] is False
    assert report["flag"]["whole_model_validated"] is False
    assert report["flag"]["empirical_discovery"] is False
