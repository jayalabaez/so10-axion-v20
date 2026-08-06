#!/usr/bin/env python3
from __future__ import annotations

import numpy as np
import pytest

import next_gen_triplet_pure_phisigma_gate_v20 as gate


def test_coupling_schema_is_fail_closed() -> None:
    with pytest.raises(ValueError):
        gate.validate_couplings({"1": 0.1})


def test_legacy_map_formula() -> None:
    mapped = gate.legacy_to_pure_couplings(
        lambda_norm=0.05,
        lambda_45_old=0.02,
        lambda_C=0.04,
    )
    assert mapped == {
        "1": 1.09,
        "45": -0.66,
        "210": 0.04,
        "770": 0.04,
        "5940": 0.04,
        "8910": 0.04,
    }


def test_six_independent_couplings_produce_hermitian_delta() -> None:
    couplings = {
        "1": 0.13,
        "45": -0.08,
        "210": 0.05,
        "770": 0.02,
        "5940": -0.03,
        "8910": 0.04,
    }
    delta = gate.pure_phisigma_delta(
        p=0.9, a=0.4, omega=0.7, couplings=couplings
    )
    assert delta["A_u_sigma_GeV2"].shape == (1, 1)
    assert delta["A_v_sigma_GeV2"].shape == (2, 2)
    assert np.max(
        np.abs(
            delta["A_v_sigma_GeV2"]
            - delta["A_v_sigma_GeV2"].conj().T
        )
    ) < 1.0e-12


def test_authoritative_report_passes_without_overclaim() -> None:
    report = gate.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert report["normalization_and_legacy_map"][
        "maximum_full_block_residual"
    ] < 1.0e-10
    assert report["flag"]["complete_PhiSigma_quartic_triplet_family_inserted"] is True
    assert report["flag"]["complete_PhiSigma_quartic_all_component_family_inserted"] is False
    assert report["flag"]["complete_component_potential"] is False
    assert report["flag"]["physical_triplet_spectrum_complete"] is False
    assert report["flag"]["exact_unique_proton_lifetime"] is False
    assert report["flag"]["whole_model_validated"] is False
    assert report["flag"]["empirical_discovery"] is False
