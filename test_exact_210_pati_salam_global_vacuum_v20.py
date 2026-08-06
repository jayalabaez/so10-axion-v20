#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction

import numpy as np

import exact_210_pati_salam_global_vacuum_v20 as vacuum


def test_exact_quartic_sum_of_squares_map() -> None:
    assert vacuum.quartic_couplings() == vacuum.EXPECTED_J_COUPLINGS
    values = vacuum.exact_p_spectral_values()
    assert sum(values.values()) == Fraction(1)
    assert values["45"] == 0
    assert values["210"] == 0
    assert values["5940"] == 0


def test_global_bound_is_saturated_at_pati_salam_direction() -> None:
    v = 0.5
    p_form, p_vector = vacuum.pati_salam_direction()
    assert abs(vacuum.quartic_value(p_form) - 1.0) < 1.0e-12
    value, gradient, _ = vacuum.potential_gradient_hessian(
        v * p_vector, v=v
    )
    assert abs(value + v**4) < 1.0e-12
    assert np.max(np.abs(gradient)) < 1.0e-10


def test_full_hessian_has_exact_goldstones_and_positive_spectrum() -> None:
    v = 0.5
    _, p_vector = vacuum.pati_salam_direction()
    _, _, hessian = vacuum.potential_gradient_hessian(v * p_vector, v=v)
    eigenvalues = np.linalg.eigvalsh(hessian)
    expected = (
        (0.0, 24),
        (2.0 / 9.0, 90),
        (3.0 / 8.0, 80),
        (3.0 / 5.0, 15),
        (2.0, 1),
    )
    clusters = vacuum.eigenvalue_clusters(eigenvalues)
    assert len(clusters) == len(expected)
    for row, (value, multiplicity) in zip(clusters, expected):
        assert abs(float(row["eigenvalue"]) - value) < 1.0e-10
        assert int(row["multiplicity"]) == multiplicity
    assert np.sum(eigenvalues < -1.0e-9) == 0


def test_pati_salam_stabilizer() -> None:
    _, p_vector = vacuum.pati_salam_direction()
    audit = vacuum.generator_stabilizer_audit(0.5 * p_vector)
    assert audit["unbroken_generator_count"] == 21
    assert audit["broken_generator_count"] == 24
    assert audit["broken_orbit_rank"] == 24
    assert audit["pattern_mismatches"] == []


def test_authoritative_report_passes_without_overclaim() -> None:
    report = vacuum.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert report["flag"]["210_quartic_bounded_below"] is True
    assert report["flag"]["global_Pati_Salam_210_vacuum"] is True
    assert report["flag"]["physical_210_Hessian_complete_at_benchmark"] is True
    assert report["flag"]["complete_multi_field_potential"] is False
    assert report["flag"]["unique_full_vacuum"] is False
    assert report["flag"]["physical_full_model_Hessian_complete"] is False
    assert report["flag"]["full_physical_threshold_spectrum_complete"] is False
    assert report["flag"]["exact_unique_proton_lifetime"] is False
    assert report["flag"]["whole_model_validated"] is False
    assert report["flag"]["empirical_discovery"] is False
