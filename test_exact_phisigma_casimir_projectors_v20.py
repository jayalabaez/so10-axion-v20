#!/usr/bin/env python3
from __future__ import annotations

import numpy as np

import exact_phisigma_casimir_projectors_v20 as projectors
import exact_portal_norm_square_triplet_channel_v20 as exact_c


def test_projector_polynomials_are_cardinal() -> None:
    eigenvalues = tuple(dict.fromkeys(projectors.SPECTRAL_EIGENVALUES.values()))
    for target in eigenvalues:
        coefficients = projectors.projector_polynomial(target)
        for probe in eigenvalues:
            value = sum(
                float(coefficient) * float(probe) ** degree
                for degree, coefficient in enumerate(coefficients)
            )
            expected = 1.0 if probe == target else 0.0
            assert abs(value - expected) < 1.0e-10


def test_pure_channels_reconstruct_exact_C_block() -> None:
    p, a, omega = 0.9, 0.4, 0.7
    blocks = {
        channel: projectors.evaluate_channel_blocks(channel, p, a, omega)
        for channel in projectors.COMMON_CHANNEL_EIGENVALUES
    }
    reconstructed = {
        key: sum(
            (row[key] for row in blocks.values()),
            np.zeros_like(next(iter(blocks.values()))[key]),
        )
        for key in ("A_u_sigma_GeV2", "A_v_sigma_GeV2")
    }
    expected = exact_c.analytic_sigma_blocks(p, a, omega)
    for key in expected:
        assert np.max(np.abs(reconstructed[key] - expected[key])) < 1.0e-9


def test_authoritative_report_passes_without_overclaim() -> None:
    report = projectors.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert report["flag"]["all_PhiSigma_quartic_triplet_Clebsches_complete"] is True
    assert report["flag"]["all_PhiSigma_quartic_all_component_Clebsches_complete"] is False
    assert report["flag"]["complete_component_potential"] is False
    assert report["flag"]["physical_triplet_spectrum_complete"] is False
    assert report["flag"]["exact_unique_proton_lifetime"] is False
    assert report["flag"]["whole_model_validated"] is False
    assert report["flag"]["empirical_discovery"] is False
