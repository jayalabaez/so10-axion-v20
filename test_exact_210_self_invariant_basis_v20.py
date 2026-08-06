#!/usr/bin/env python3
from __future__ import annotations

import math

import numpy as np
import pytest

import exact_210_self_invariant_basis_v20 as self210


def test_exact_symmetric_power_singlet_counts() -> None:
    assert self210.racah_speiser_trivial_multiplicity(2) == 1
    assert self210.racah_speiser_trivial_multiplicity(3) == 1
    assert self210.racah_speiser_trivial_multiplicity(4) == 4


def test_unique_cubic_singlet_formula() -> None:
    p, a, omega = 0.9, 0.4, 0.7
    observed = self210.cubic_invariant(
        self210.singlet_form(p, a, omega)
    )
    expected = (
        2.0 * a**3 / math.sqrt(3.0)
        + 2.0 * math.sqrt(3.0) * a * omega**2
        + 3.0 * p * omega**2
    )
    assert abs(observed - expected) < 1.0e-12


def test_quartic_basis_and_exact_crossing_identities() -> None:
    samples = self210.deterministic_integer_samples()
    moments = [self210.integer_pair_moments(sample) for sample in samples]
    matrix = [
        [row[index] for index in (0, 2, 3, 4)]
        for row in moments[:4]
    ]
    assert self210.determinant_four(matrix) != 0
    for row in moments:
        assert row[1] == 0
        base = tuple(row[index] for index in (0, 2, 3, 4))
        for degree, coefficients in self210.HIGHER_MOMENT_REDUCTIONS.items():
            assert sum(
                coefficients[index] * base[index]
                for index in range(4)
            ) == row[degree]


def test_potential_schema_is_fail_closed() -> None:
    phi = self210.singlet_form(0.9, 0.4, 0.7)
    with pytest.raises(ValueError):
        self210.self_potential(
            phi,
            mass_sq=1.0,
            cubic_coupling=0.1,
            quartic_couplings={"J0": 0.1},
        )
    value = self210.self_potential(
        phi,
        mass_sq=1.0,
        cubic_coupling=0.1,
        quartic_couplings={
            "J0": 0.01,
            "J2": 0.001,
            "J3": -0.0001,
            "J4": 0.00001,
        },
    )
    assert np.isfinite(value)


def test_authoritative_report_passes_without_overclaim() -> None:
    report = self210.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert report["exact_hilbert_count"]["Sym2_trivial_multiplicity"] == 1
    assert report["exact_hilbert_count"]["Sym3_trivial_multiplicity"] == 1
    assert report["exact_hilbert_count"]["Sym4_trivial_multiplicity"] == 4
    assert report["flag"]["complete_210_self_operator_basis"] is True
    assert report["flag"]["complete_component_potential"] is False
    assert report["flag"]["unique_full_vacuum"] is False
    assert report["flag"]["physical_full_Hessian_complete"] is False
    assert report["flag"]["physical_threshold_spectrum_complete"] is False
    assert report["flag"]["exact_unique_proton_lifetime"] is False
    assert report["flag"]["whole_model_validated"] is False
    assert report["flag"]["empirical_discovery"] is False
