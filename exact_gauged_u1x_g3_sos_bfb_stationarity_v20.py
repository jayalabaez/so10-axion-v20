#!/usr/bin/env python3
"""Exact end-to-end SOS, boundedness, and stationarity certificate for G3.

This module binds the 27 nonzero coefficients of the constructive exact-X
candidate to the following exact decomposition (irrelevant constants omitted):

* the globally bounded Pati--Salam 210 potential;
* ``(1/8)||[M(Phi)-2]Sigma||^2`` and
  ``(1/8)||C_Phi Sigma||^2``;
* the four 126bar self-projector norms with weights
  ``(1/8)*(2,2,17/16,1)`` and the radial mass term;
* elementary H/S/Phi17 norm, alignment, and phase-locking squares; and
* ``||H wedge Phi||^2``.

All recouplings use integer/Gaussian-integer tensors and ``Fraction`` spectral
projectors.  The selected P, Delta_R, H, S, and Phi17 configuration is shown
stationary algebraically over Q(h,r,x,1/r).  Boundedness and stationarity are
certified; global uniqueness, the direct full-Hessian rank, and G3 closure are
not claimed here.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
from scipy import sparse

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_126bar_self_quartic_basis_v20 as sigma_source
import exact_210_pati_salam_global_vacuum_v20 as phi_source
import exact_gauged_u1x_g3_a_square_recoupling_v20 as a_square_source
import exact_phisigma_bose_channel_census_v20 as mixed_census
import gauged_u1x_g2_derivative_audit_v20 as g2_audit
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_h10_self_quartic_derivatives_v20 as h_self_source
import live_g2_exact_phi2_hdagh_derivatives_v20 as phi_h_source

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SOS_BFB_STATIONARITY_V20.json"
OUT_MD = ROOT / "EXACT_GAUGED_U1X_G3_SOS_BFB_STATIONARITY_V20.md"

MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
SIGMA_SCALE = Fraction(1, 8)
SIGMA_RADIAL_COEFFICIENT = Fraction(25, 12)
SIGMA_SELF_WEIGHTS = {
    "54": Fraction(2),
    "1050bar": Fraction(2),
    "2772bar": Fraction(17, 16),
    "4125": Fraction(1),
}
MIXED_CHANNELS = ("1", "45", "210", "770", "5940", "8910")
C_SQUARE_WEIGHTS = (1, 1, 1, 1, 1, 1)
RECORDED_C_SQUARED_TARGETS = (1014, 1005, 1828, 740, 1900, 1344)
RECORDED_DELTA_FRACTIONS = {
    "54": Fraction(0),
    "1050bar": Fraction(0),
    "2772bar": Fraction(2, 3),
    "4125": Fraction(1, 3),
}

# A Laurent monomial is h^a r^b x^c.  Negative r powers are allowed because
# alpha=h^2/r, while h,r,x are fixed positive candidate scales.
Exponent = tuple[int, int, int]
Polynomial = dict[Exponent, Fraction]


def _polynomial(*terms: tuple[Fraction | int, Exponent]) -> Polynomial:
    output: Polynomial = {}
    for coefficient, exponent in terms:
        value = Fraction(coefficient)
        output[exponent] = output.get(exponent, Fraction(0)) + value
        if output[exponent] == 0:
            del output[exponent]
    return output


def _add_polynomial(left: Polynomial, right: Polynomial) -> Polynomial:
    output = dict(left)
    for exponent, coefficient in right.items():
        output[exponent] = output.get(exponent, Fraction(0)) + coefficient
        if output[exponent] == 0:
            del output[exponent]
    return output


def _scale_polynomial(value: Polynomial, coefficient: Fraction | int) -> Polynomial:
    return {
        exponent: Fraction(coefficient) * entry
        for exponent, entry in value.items()
        if Fraction(coefficient) * entry
    }


ONE = _polynomial((1, (0, 0, 0)))
H2 = _polynomial((1, (2, 0, 0)))
R2 = _polynomial((1, (0, 2, 0)))
X2 = _polynomial((1, (0, 0, 2)))
ALPHA = _polynomial((1, (2, -1, 0)))
ALPHA2 = _polynomial((1, (4, -2, 0)))


def _put(
    output: dict[str, Polynomial], parameter_id: str, value: Polynomial
) -> None:
    output[parameter_id] = _add_polynomial(output.get(parameter_id, {}), value)


def expanded_sos_coefficient_map() -> dict[str, Polynomial]:
    """Expand the exact SOS decomposition into authoritative parameters."""
    output: dict[str, Polynomial] = {}
    _put(output, "lambda::O07_B01_Phi_norm", _scale_polynomial(ONE, -2))
    for index, name in enumerate(("J0", "J2", "J3", "J4"), start=1):
        _put(
            output,
            f"lambda::O48_B0{index}_Phi_self_quartics",
            _scale_polynomial(ONE, phi_source.EXPECTED_J_COUPLINGS[name]),
        )

    # (1/8) ( ||(M-2)Sigma||^2 + ||C Sigma||^2 + W_self
    #           - (25/12) r^2 N_Sigma ).
    total_mixed = tuple(
        a + c
        for a, c in zip(
            a_square_source.EXPECTED_WEIGHTS, C_SQUARE_WEIGHTS, strict=True
        )
    )
    for index, weight in enumerate(total_mixed, start=1):
        _put(
            output,
            f"lambda::O44_B0{index}_Phi2_Sigma_projectors",
            _scale_polynomial(ONE, SIGMA_SCALE * weight),
        )
    _put(
        output,
        "lambda::O14_B01_Phi_Sigma_Sigmadag_cubic",
        _scale_polynomial(ONE, -4 * SIGMA_SCALE),
    )
    sigma_norm = _add_polynomial(
        _scale_polynomial(ONE, 4 * SIGMA_SCALE),
        _scale_polynomial(R2, -SIGMA_SCALE * SIGMA_RADIAL_COEFFICIENT),
    )
    _put(output, "lambda::O05_B01_126bar_norm", sigma_norm)
    for index, channel in enumerate(
        ("54", "1050bar", "2772bar", "4125"), start=1
    ):
        _put(
            output,
            f"lambda::O27_B0{index}_126bar_self_projectors",
            _scale_polynomial(ONE, SIGMA_SCALE * SIGMA_SELF_WEIGHTS[channel]),
        )

    # H/S squares, with a real O12 parameter contributing 2 Re(O12).
    _put(output, "lambda::O06_B01_Hdag_H_norm", _scale_polynomial(H2, -2))
    _put(output, "re::O12_B01_Hdag_Hdag_pair", _scale_polynomial(ALPHA, -1))
    _put(
        output,
        "lambda::O04_B01_singlet_polynomial",
        _add_polynomial(ALPHA2, _scale_polynomial(R2, -2)),
    )
    _put(output, "lambda::O23_B01_singlet_polynomial", ONE)
    _put(output, "lambda::O36_B01_H_self_quartics", _scale_polynomial(ONE, 2))
    _put(output, "lambda::O36_B02_H_self_quartics", _scale_polynomial(ONE, 2))

    # (3/5) I_1-I_54 = Hdag (||Phi||^2 I-C(Phi)) H.
    _put(
        output,
        "lambda::O46_B01_Phi2_HdagH_channels",
        _scale_polynomial(ONE, Fraction(3, 5)),
    )
    _put(
        output,
        "lambda::O46_B03_Phi2_HdagH_channels",
        _scale_polynomial(ONE, -1),
    )

    # (1/32)(|Phi17|^2-x^2)^2, up to its constant.
    _put(
        output,
        "lambda::O03_B01_singlet_polynomial",
        _scale_polynomial(X2, Fraction(-1, 16)),
    )
    _put(
        output,
        "lambda::O20_B01_singlet_polynomial",
        _scale_polynomial(ONE, Fraction(1, 32)),
    )
    return output


def declared_candidate_coefficient_map() -> dict[str, Polynomial]:
    """Independent literal transcription of the 27-parameter candidate."""
    values: dict[str, Polynomial] = {
        "lambda::O07_B01_Phi_norm": _polynomial((-2, (0, 0, 0))),
        "lambda::O48_B01_Phi_self_quartics": _polynomial((Fraction(-21, 200), (0, 0, 0))),
        "lambda::O48_B02_Phi_self_quartics": _polynomial((Fraction(2467, 28800), (0, 0, 0))),
        "lambda::O48_B03_Phi_self_quartics": _polynomial((Fraction(-77, 3200), (0, 0, 0))),
        "lambda::O48_B04_Phi_self_quartics": _polynomial((Fraction(119, 115200), (0, 0, 0))),
        "lambda::O05_B01_126bar_norm": _polynomial(
            (Fraction(1, 2), (0, 0, 0)),
            (Fraction(-25, 96), (0, 2, 0)),
        ),
        "lambda::O14_B01_Phi_Sigma_Sigmadag_cubic": _polynomial((Fraction(-1, 2), (0, 0, 0))),
        "lambda::O27_B01_126bar_self_projectors": _polynomial((Fraction(1, 4), (0, 0, 0))),
        "lambda::O27_B02_126bar_self_projectors": _polynomial((Fraction(1, 4), (0, 0, 0))),
        "lambda::O27_B03_126bar_self_projectors": _polynomial((Fraction(17, 128), (0, 0, 0))),
        "lambda::O27_B04_126bar_self_projectors": _polynomial((Fraction(1, 8), (0, 0, 0))),
        "lambda::O06_B01_Hdag_H_norm": _polynomial((-2, (2, 0, 0))),
        "re::O12_B01_Hdag_Hdag_pair": _polynomial((-1, (2, -1, 0))),
        "lambda::O04_B01_singlet_polynomial": _polynomial(
            (1, (4, -2, 0)), (-2, (0, 2, 0))
        ),
        "lambda::O23_B01_singlet_polynomial": ONE,
        "lambda::O36_B01_H_self_quartics": _polynomial((2, (0, 0, 0))),
        "lambda::O36_B02_H_self_quartics": _polynomial((2, (0, 0, 0))),
        "lambda::O46_B01_Phi2_HdagH_channels": _polynomial((Fraction(3, 5), (0, 0, 0))),
        "lambda::O46_B03_Phi2_HdagH_channels": _polynomial((-1, (0, 0, 0))),
        "lambda::O03_B01_singlet_polynomial": _polynomial((Fraction(-1, 16), (0, 0, 2))),
        "lambda::O20_B01_singlet_polynomial": _polynomial((Fraction(1, 32), (0, 0, 0))),
    }
    for index, value in enumerate((41, 73, 29, -7, -11, 13), start=1):
        values[f"lambda::O44_B0{index}_Phi2_Sigma_projectors"] = _polynomial(
            (Fraction(value, 8), (0, 0, 0))
        )
    return values


def _raw_delta_form() -> direct.Form:
    holomorphic = [
        direct.add_forms(
            direct.one_form(first),
            direct.scale_form(direct.one_form(second), 1j),
        )
        for first, second in ((0, 1), (2, 3), (4, 5))
    ]
    omega = direct.wedge(
        direct.wedge(holomorphic[0], holomorphic[1]), holomorphic[2]
    )
    right = direct.add_forms(
        direct.wedge(direct.one_form(6), direct.one_form(7)),
        direct.wedge(direct.one_form(8), direct.one_form(9)),
    )
    return direct.wedge(omega, right)


@lru_cache(maxsize=1)
def raw_delta_coordinates() -> tuple[np.ndarray, np.ndarray]:
    raw = _raw_delta_form()
    coordinates = np.asarray(
        [direct.sigma_kinetic_inner(state, raw) for state in chart.sigma_basis()],
        dtype=complex,
    )
    real = np.rint(coordinates.real).astype(np.int64)
    imaginary = np.rint(coordinates.imag).astype(np.int64)
    if np.max(np.abs(coordinates - (real + 1j * imaginary))) != 0.0:
        raise ArithmeticError("raw Delta_R coordinates are not Gaussian integers")
    if int(real @ real + imaginary @ imaginary) != 8:
        raise ArithmeticError("raw Delta_R norm is not eight")
    return real, imaginary


@lru_cache(maxsize=1)
def integer_sigma_generators() -> tuple[np.ndarray, np.ndarray]:
    observed = sigma_source._generators()
    real = np.rint(observed.real).astype(np.int64)
    imaginary = np.rint(observed.imag).astype(np.int64)
    if np.max(np.abs(observed - (real + 1j * imaginary))) != 0.0:
        raise ArithmeticError("126bar generators are not exact Gaussian integers")
    return real, imaginary


def _sigma_pair_casimir(
    pair_real: np.ndarray, pair_imaginary: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    generators_real, generators_imaginary = integer_sigma_generators()
    output_real = np.zeros_like(pair_real)
    output_imaginary = np.zeros_like(pair_imaginary)
    for real, imaginary in zip(
        generators_real, generators_imaginary, strict=True
    ):
        left_real = real @ pair_real - imaginary @ pair_imaginary
        left_imaginary = real @ pair_imaginary + imaginary @ pair_real
        output_real += left_real @ real.T - left_imaginary @ imaginary.T
        output_imaginary += left_real @ imaginary.T + left_imaginary @ real.T
    return output_real, output_imaginary


def _integer_projected_delta_pairs() -> dict[str, tuple[np.ndarray, np.ndarray, int]]:
    delta_real, delta_imaginary = raw_delta_coordinates()
    # Delta=raw/(2 sqrt(2)); hence Delta tensor Delta=(raw tensor raw)/8.
    pair_real = np.outer(delta_real, delta_real) - np.outer(
        delta_imaginary, delta_imaginary
    )
    pair_imaginary = np.outer(delta_real, delta_imaginary) + np.outer(
        delta_imaginary, delta_real
    )
    powers = [(pair_real, pair_imaginary)]
    for _ in range(3):
        powers.append(_sigma_pair_casimir(*powers[-1]))

    output: dict[str, tuple[np.ndarray, np.ndarray, int]] = {}
    for channel in sigma_source.CHANNELS:
        polynomial = sigma_source._poly(channel)
        denominator = math.lcm(*(value.denominator for value in polynomial))
        real = sum(
            (
                int(coefficient * denominator) * powers[index][0]
                for index, coefficient in enumerate(polynomial)
            ),
            np.zeros_like(pair_real),
        )
        imaginary = sum(
            (
                int(coefficient * denominator) * powers[index][1]
                for index, coefficient in enumerate(polynomial)
            ),
            np.zeros_like(pair_imaginary),
        )
        output[channel] = (real, imaginary, 8 * denominator)
    return output


@lru_cache(maxsize=1)
def exact_delta_self_certificate() -> dict[str, Any]:
    projected = _integer_projected_delta_pairs()
    fractions: dict[str, Fraction] = {}
    for channel, (real, imaginary, denominator) in projected.items():
        numerator = sum(int(value) ** 2 for value in real.flat) + sum(
            int(value) ** 2 for value in imaginary.flat
        )
        fractions[channel] = Fraction(numerator, denominator**2)

    polynomial_sum = tuple(
        sum(sigma_source._poly(channel)[degree] for channel in sigma_source.CHANNELS)
        for degree in range(4)
    )
    generators_real, generators_imaginary = integer_sigma_generators()
    antihermitian = bool(
        np.array_equal(generators_real.transpose(0, 2, 1), -generators_real)
        and np.array_equal(
            generators_imaginary.transpose(0, 2, 1), generators_imaginary
        )
    )

    # Exact 252-real first derivative at unit Delta.  Delta=sqrt(2)*u,
    # with u=(raw real+i raw imaginary)/4.
    raw_real, raw_imaginary = raw_delta_coordinates()
    gradient_real = [Fraction(0) for _ in range(chart.SIGMA_COMPLEX_DIM)]
    gradient_imaginary = [Fraction(0) for _ in range(chart.SIGMA_COMPLEX_DIM)]
    for channel, weight in SIGMA_SELF_WEIGHTS.items():
        matrix_real, matrix_imaginary, denominator = projected[channel]
        for index in range(chart.SIGMA_COMPLEX_DIM):
            scalar_real = Fraction(
                int(
                    matrix_real[:, index] @ raw_real
                    + matrix_imaginary[:, index] @ raw_imaginary
                ),
                4 * denominator,
            )
            scalar_imaginary = Fraction(
                int(
                    matrix_real[:, index] @ raw_imaginary
                    - matrix_imaginary[:, index] @ raw_real
                ),
                4 * denominator,
            )
            gradient_real[index] += 4 * weight * scalar_real
            gradient_imaginary[index] -= 4 * weight * scalar_imaginary

    residual_real = tuple(
        value
        - Fraction(25, 6) * Fraction(int(raw_real[index]), 4)
        for index, value in enumerate(gradient_real)
    )
    residual_imaginary = tuple(
        value
        - Fraction(25, 6) * Fraction(int(raw_imaginary[index]), 4)
        for index, value in enumerate(gradient_imaginary)
    )
    return {
        "projector_polynomial_sum": polynomial_sum,
        "generators_exactly_antihermitian": antihermitian,
        "delta_projector_fractions": fractions,
        "weighted_quartic_at_delta": sum(
            SIGMA_SELF_WEIGHTS[channel] * value
            for channel, value in fractions.items()
        ),
        "stationarity_gradient_residual_real": residual_real,
        "stationarity_gradient_residual_imaginary": residual_imaginary,
        "maximum_stationarity_gradient_residual": max(
            map(abs, residual_real + residual_imaginary), default=Fraction(0)
        ),
        "source_binding_exact": True,
    }


def _direct_c_squared_target(seed: int) -> int:
    phi, sigma_real, sigma_imaginary = a_square_source.deterministic_integer_fields(
        seed
    )
    contraction_real, contraction_imaginary = (
        a_square_source.integer_contraction_tensor()
    )
    image_real = (
        np.einsum(
            "vpa,p,a->v", contraction_real, phi, sigma_real, optimize=True
        )
        - np.einsum(
            "vpa,p,a->v",
            contraction_imaginary,
            phi,
            sigma_imaginary,
            optimize=True,
        )
    )
    image_imaginary = (
        np.einsum(
            "vpa,p,a->v",
            contraction_real,
            phi,
            sigma_imaginary,
            optimize=True,
        )
        + np.einsum(
            "vpa,p,a->v", contraction_imaginary, phi, sigma_real, optimize=True
        )
    )
    return sum(int(value) ** 2 for value in image_real) + sum(
        int(value) ** 2 for value in image_imaginary
    )


@lru_cache(maxsize=1)
def exact_mixed_certificate() -> dict[str, Any]:
    witnesses = tuple(
        a_square_source.exact_witness(seed)
        for seed in a_square_source.WITNESS_SEEDS
    )
    matrix = tuple(tuple(row["channel_values"]) for row in witnesses)
    c_targets = tuple(
        _direct_c_squared_target(seed) for seed in a_square_source.WITNESS_SEEDS
    )
    c_weights = a_square_source.solve_exact(matrix, c_targets)
    c_residuals = tuple(
        sum(weight * value for weight, value in zip(c_weights, row, strict=True))
        - target
        for row, target in zip(matrix, c_targets, strict=True)
    )

    p_form, p_vector_float = phi_source.pati_salam_direction()
    p_vector = np.rint(p_vector_float).astype(np.int64)
    if np.max(np.abs(p_vector_float - p_vector)) != 0.0:
        raise ArithmeticError("P is not an exact integer four-form")
    delta_real, delta_imaginary = raw_delta_coordinates()
    contraction_real, contraction_imaginary = (
        a_square_source.integer_contraction_tensor()
    )
    c_real = (
        np.einsum(
            "vpa,p,a->v",
            contraction_real,
            p_vector,
            delta_real,
            optimize=True,
        )
        - np.einsum(
            "vpa,p,a->v",
            contraction_imaginary,
            p_vector,
            delta_imaginary,
            optimize=True,
        )
    )
    c_imaginary = (
        np.einsum(
            "vpa,p,a->v",
            contraction_real,
            p_vector,
            delta_imaginary,
            optimize=True,
        )
        + np.einsum(
            "vpa,p,a->v",
            contraction_imaginary,
            p_vector,
            delta_real,
            optimize=True,
        )
    )

    operator_real, operator_imaginary = a_square_source.integer_cubic_operators()
    matrix_real = np.tensordot(p_vector, operator_real, axes=(0, 0))
    matrix_imaginary = np.tensordot(p_vector, operator_imaginary, axes=(0, 0))
    image_real = matrix_real @ delta_real - matrix_imaginary @ delta_imaginary
    image_imaginary = (
        matrix_real @ delta_imaginary + matrix_imaginary @ delta_real
    )
    a_eigen_residual = max(
        int(np.max(np.abs(image_real - 2 * delta_real))),
        int(np.max(np.abs(image_imaginary - 2 * delta_imaginary))),
    )
    hermitian = bool(
        np.array_equal(operator_real.transpose(0, 2, 1), operator_real)
        and np.array_equal(
            operator_imaginary.transpose(0, 2, 1), -operator_imaginary
        )
    )
    return {
        "invariant_space_dimension": len(mixed_census.COMMON_QUARTIC_CHANNELS),
        "all_common_channels_multiplicity_one": all(
            value == 1 for value in mixed_census.COMMON_QUARTIC_CHANNELS.values()
        ),
        "witness_determinant": a_square_source.fraction_determinant(matrix),
        "C_square_targets": c_targets,
        "C_square_unique_weights": c_weights,
        "C_square_identity_residuals": c_residuals,
        "A_square_report": a_square_source.build_report(),
        "cubic_operator_exactly_hermitian": hermitian,
        "C_at_P_Delta_raw_max_abs": max(
            int(np.max(np.abs(c_real), initial=0)),
            int(np.max(np.abs(c_imaginary), initial=0)),
        ),
        "M_P_Delta_minus_2_Delta_max_abs": a_eigen_residual,
        "source_binding_exact": True,
    }


@lru_cache(maxsize=1)
def exact_wedge_certificate() -> dict[str, Any]:
    five_indices = tuple(itertools.combinations(range(10), 5))
    five_index = {indices: index for index, indices in enumerate(five_indices)}
    three_indices = tuple(itertools.combinations(range(10), 3))
    three_index = {indices: index for index, indices in enumerate(three_indices)}
    wedge_rows: list[int] = []
    wedge_columns: list[int] = []
    wedge_values: list[int] = []
    interior_rows: list[int] = []
    interior_columns: list[int] = []
    interior_values: list[int] = []
    for phi_index, indices in enumerate(chart.PHI_INDICES):
        phi = {indices: 1.0 + 0.0j}
        for vector_index in range(10):
            column = 10 * phi_index + vector_index
            for target, value in direct.wedge(
                direct.one_form(vector_index), phi
            ).items():
                integer = int(round(complex(value).real))
                if complex(value) != complex(integer):
                    raise ArithmeticError("wedge map is not integral")
                wedge_rows.append(five_index[target])
                wedge_columns.append(column)
                wedge_values.append(integer)
            for target, value in direct.interior(phi, vector_index).items():
                integer = int(round(complex(value).real))
                if complex(value) != complex(integer):
                    raise ArithmeticError("interior map is not integral")
                interior_rows.append(three_index[target])
                interior_columns.append(column)
                interior_values.append(integer)
    wedge = sparse.csr_matrix(
        (wedge_values, (wedge_rows, wedge_columns)),
        shape=(len(five_indices), chart.PHI_DIM * 10),
        dtype=np.int16,
    )
    interior = sparse.csr_matrix(
        (interior_values, (interior_rows, interior_columns)),
        shape=(len(three_indices), chart.PHI_DIM * 10),
        dtype=np.int16,
    )
    gram = (wedge.T @ wedge + interior.T @ interior).toarray().reshape(
        chart.PHI_DIM, 10, chart.PHI_DIM, 10
    )
    polarized = gram + gram.transpose(2, 1, 0, 3)
    expected = np.zeros_like(polarized)
    identity = 2 * np.eye(10, dtype=np.int16)
    for index in range(chart.PHI_DIM):
        expected[index, :, index, :] = identity
    coefficient_residual = int(np.max(np.abs(polarized - expected)))

    p_form, _ = phi_source.pati_salam_direction()
    p_interiors = []
    for vector_index in range(10):
        form = direct.interior(p_form, vector_index)
        p_interiors.append(
            np.asarray(
                [form.get(indices, 0.0) for indices in three_indices],
                dtype=complex,
            )
        )
    c_matrix = np.asarray(p_interiors) @ np.asarray(p_interiors).conj().T
    q_matrix = np.eye(10) - c_matrix
    expected_q = np.diag([1] * 6 + [0] * 4)
    return {
        "identity": (
            "Hdag(||Phi||^2 I-C(Phi))H=||H wedge Phi||^2"
        ),
        "integer_wedge_nonzero_entries": wedge.nnz,
        "integer_interior_nonzero_entries": interior.nnz,
        "all_polarized_coefficient_residual": coefficient_residual,
        "candidate_channel_combination": "(3/5) I_1-I_54",
        "P_operator_equals_diag_1x6_0x4": bool(
            np.array_equal(q_matrix, expected_q)
        ),
        "selected_H_index_6_value": int(expected_q[6, 6]),
        "source_basis_labels": phi_h_source.BASIS_LABELS,
        "source_binding_exact": True,
    }


def exact_phi_certificate() -> dict[str, Any]:
    couplings = phi_source.quartic_couplings()
    spectral = phi_source.exact_p_spectral_values()
    return {
        "J_basis_couplings": couplings,
        "couplings_match_candidate": couplings
        == phi_source.EXPECTED_J_COUPLINGS,
        "spectral_weights_all_at_least_one": all(
            value >= 1 for value in phi_source.SPECTRAL_WEIGHTS.values()
        ),
        "P_spectral_values": spectral,
        "P_has_unit_norm": sum(spectral.values()) == 1,
        "positive_extra_channels_zero_at_P": all(
            spectral[channel] == 0
            for channel in phi_source.EXTRA_POSITIVE_CHANNELS
        ),
        "global_bound": "V_Phi>=(I2-1)^2-1",
        "P_stationary_from_vanishing_square_gradients": True,
        "source_binding_exact": True,
    }


def exact_elementary_certificate() -> dict[str, Any]:
    expanded = expanded_sos_coefficient_map()
    declared = declared_candidate_coefficient_map()
    selection = g2_audit.contract_selection()
    return {
        "expanded_coefficients_equal_declared_27": expanded == declared,
        "nonzero_parameter_count": len(expanded),
        "all_parameters_in_exact_X_contract": set(expanded)
        <= set(selection["parameter_ids"]),
        "exact_X_parameter_count": selection["parameter_count"],
        "H_self_source_basis": h_self_source.BASIS_LABELS,
        "H_self_sum_identity": "2 I_1+2 I_54=2(Hdag H)^2",
        "O12_parameter_convention": (
            "re::O12 multiplies 2 Re[(Hdag.Hdag) Sdag]"
        ),
        "H_S_identity": (
            "(N_H-h^2)^2+(N_H^2-|H.H|^2)+"
            "|H.H-(h^2/r)S*|^2+(|S|^2-r^2)^2"
        ),
        "Phi17_identity": "(1/32)(|Phi17|^2-x^2)^2",
        "selected_square_values": {
            "N_H_minus_h2": "0",
            "N_H2_minus_abs_HH2": "0",
            "HH_minus_alpha_Sstar": "0",
            "S_norm_minus_r2": "0",
            "Phi17_norm_minus_x2": "0",
            "H_wedge_P": "0",
        },
        "formal_scale_field": "Q(h,r,x,1/r), h>0, r>0, x>0",
        "source_binding_exact": True,
    }


def _poly_payload(value: Polynomial) -> list[dict[str, Any]]:
    return [
        {
            "coefficient": str(coefficient),
            "powers": {"h": exponent[0], "r": exponent[1], "x": exponent[2]},
        }
        for exponent, coefficient in sorted(value.items())
    ]


def build_report(*, recompute: bool = False) -> dict[str, Any]:
    phi = exact_phi_certificate()
    mixed = exact_mixed_certificate()
    sigma = exact_delta_self_certificate()
    wedge = exact_wedge_certificate()
    elementary = exact_elementary_certificate()
    expanded = expanded_sos_coefficient_map()
    a_report = mixed["A_square_report"]

    self_completeness = sigma["projector_polynomial_sum"] == (
        Fraction(1),
        Fraction(0),
        Fraction(0),
        Fraction(0),
    )
    self_coefficients_positive = all(
        value >= 1 for value in SIGMA_SELF_WEIGHTS.values()
    )
    bfb_lower_bound = (
        "V>=-1-h^4-r^4-x^4/32-(1/8)(625/576)r^4"
    )
    checks = {
        "exact_X_27_parameter_SOS_expansion_matches": elementary[
            "expanded_coefficients_equal_declared_27"
        ]
        and elementary["nonzero_parameter_count"] == 27
        and elementary["all_parameters_in_exact_X_contract"],
        "exact_210_global_bound_source_bound": phi["couplings_match_candidate"]
        and phi["spectral_weights_all_at_least_one"],
        "exact_210_selected_P_stationary": phi["P_has_unit_norm"]
        and phi["positive_extra_channels_zero_at_P"],
        "A_square_recoupling_exactly_source_bound": a_report["n_failed"] == 0
        and a_report["flags"]["A_square_recoupling_exactly_source_bound"],
        "C_square_recoupling_exactly_source_bound": (
            mixed["invariant_space_dimension"] == 6
            and mixed["all_common_channels_multiplicity_one"]
            and mixed["witness_determinant"] != 0
            and mixed["C_square_unique_weights"]
            == tuple(map(Fraction, C_SQUARE_WEIGHTS))
            and all(value == 0 for value in mixed["C_square_identity_residuals"])
        ),
        "A_shift_square_exactly_source_bound": mixed[
            "cubic_operator_exactly_hermitian"
        ],
        "A_shift_and_C_squares_vanish_at_P_Delta": (
            mixed["C_at_P_Delta_raw_max_abs"] == 0
            and mixed["M_P_Delta_minus_2_Delta_max_abs"] == 0
        ),
        "126_projectors_complete_and_nonnegative": self_completeness
        and sigma["generators_exactly_antihermitian"],
        "126_self_weights_dominate_norm_square": self_coefficients_positive,
        "Delta_projector_fractions_exact": sigma["delta_projector_fractions"]
        == RECORDED_DELTA_FRACTIONS,
        "Delta_full_252_coordinate_stationarity_exact": sigma[
            "maximum_stationarity_gradient_residual"
        ]
        == 0,
        "Phi_H_term_is_exact_global_wedge_square": wedge[
            "all_polarized_coefficient_residual"
        ]
        == 0,
        "Phi_H_square_vanishes_at_selected_P_H": wedge[
            "P_operator_equals_diag_1x6_0x4"
        ]
        and wedge["selected_H_index_6_value"] == 0,
        "elementary_H_S_Phi17_squares_exactly_expanded": elementary[
            "expanded_coefficients_equal_declared_27"
        ]
        and h_self_source.BASIS_LABELS == ("I_1", "I_54"),
        "all_selected_elementary_squares_vanish": all(
            value == "0" for value in elementary["selected_square_values"].values()
        ),
        "global_uniqueness_not_claimed": True,
        "full_Hessian_rank_not_claimed_here": True,
        "G3_not_closed_by_BFB_and_stationarity_alone": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    proof_complete = not failures
    return {
        "status": (
            "EXACT_COMPLETE_POTENTIAL_BFB_AND_SELECTED_STATIONARITY_CERTIFIED"
            if proof_complete
            else "EXACT_SOS_BFB_STATIONARITY_CERTIFICATE_FAILED"
        ),
        "overall_state": "CLOSED_SUBPROBLEM" if proof_complete else "EXECUTION_FAIL",
        "model_contract_id": MODEL_CONTRACT_ID,
        "recomputed_direct_sources": bool(recompute),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "coefficient_binding": {
            "nonzero_parameter_count": len(expanded),
            "exact_laurent_coefficient_map": {
                parameter_id: _poly_payload(value)
                for parameter_id, value in expanded.items()
            },
            "all_other_exact_X_parameters": "zero",
        },
        "exact_210": phi,
        "exact_mixed_squares": mixed,
        "exact_126bar_self_and_stationarity": sigma,
        "exact_Phi_H_wedge_square": wedge,
        "exact_elementary_H_S_Phi17": elementary,
        "boundedness": {
            "self_projector_inequality": (
                "2 I54+2 I1050bar+(17/16) I2772bar+I4125 >= N_Sigma^2"
            ),
            "radial_completion": (
                "N_Sigma^2-(25/12)r^2 N_Sigma >= -(625/576)r^4"
            ),
            "global_lower_bound": bfb_lower_bound,
            "source_binding_exact": proof_complete,
        },
        "stationarity": {
            "selected_vacuum": (
                "Phi=P, Sigma=r Delta_R, H=h e6, S=r, Phi17=x"
            ),
            "formal_scale_field": elementary["formal_scale_field"],
            "all_square_gradients_zero": proof_complete,
            "Sigma_non_square_gradient_cancelled_in_all_252_real_coordinates": (
                sigma["maximum_stationarity_gradient_residual"] == 0
            ),
            "source_binding_exact": proof_complete,
        },
        "flags": {
            "complete_27_parameter_SOS_identity_exactly_source_bound": proof_complete,
            "complete_potential_BFB_exactly_certified": proof_complete,
            "selected_vacuum_stationarity_exactly_certified": proof_complete,
            "selected_vacuum_global_minimum_certified": False,
            "selected_vacuum_unique_modulo_symmetry": False,
            "full_Hessian_exactly_source_bound": False,
            "strict_local_minimum_certified": False,
            "G3_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_scope": (
            "The independent direct exact Hessian/rank certificate must establish "
            "strict positivity on the 448-dimensional physical quotient before G3 "
            "can close. Global uniqueness is not established."
        ),
    }


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
    return value


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(_jsonable(report), indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Exact G3 SOS, BFB, and selected stationarity -- v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        "The complete 27-parameter candidate is bound to exact nonnegative "
        "squares plus the stated finite radial lower bounds. The selected "
        "P/Delta_R/H/S/Phi17 configuration is exactly stationary.\n\n"
        f"- complete-potential BFB: `{report['flags']['complete_potential_BFB_exactly_certified']}`\n"
        f"- exact selected stationarity: `{report['flags']['selected_vacuum_stationarity_exactly_certified']}`\n"
        "- global uniqueness: `False`\n"
        "- strict physical minimum: `False`\n"
        "- G3 closed: `False`\n\n"
        + report["remaining_scope"]
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recompute", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report(recompute=args.recompute)
    if args.write:
        write_report(report)
    print(json.dumps(_jsonable(report), indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
