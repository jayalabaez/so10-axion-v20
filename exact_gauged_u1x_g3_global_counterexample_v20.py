#!/usr/bin/env python3
"""Exact global-minimality counterexample for the constructive G3 candidate.

The current exact-X candidate has a selected stationary configuration

    Phi=P,  Sigma=r Delta_R,  H=h e6,  S=r,  Phi17=x.

Its Sigma-dependent hard sector is

    (1/8) [ ||(M(Phi)-2)Sigma||^2 + ||C_Phi Sigma||^2
            + W(Sigma) - (25/12) r^2 ||Sigma||^2 ],

where

    W=2 I54 + 2 I1050bar + (17/16) I2772bar + I4125.

This module constructs a canonical Gaussian-integer 126bar vector ``z``
directly in the live -i-Hodge chart.  Exact source tensors prove

    (M(P)-2)z=0,  C_P z=0,

while exact Fraction Casimir projectors give, for ``u=z/sqrt(8)``,

    (I54,I1050bar,I2772bar,I4125)=(0,0,1/2,1/2).

Consequently W(u)=33/32<25/24=W(Delta_R).  Optimizing only the Sigma norm
gives ||Sigma_*||^2=(100/99)r^2 and lowers the complete candidate potential
by exactly (25/19008)r^4 for r>0.  This disproves global minimality and hence
global uniqueness of the selected vacuum.  It does not contradict the exact
strict-local-minimum certificate and does not exclude the whole model/theory.

Only integer/Gaussian-integer arrays and ``Fraction`` arithmetic enter the
proof path.  Floating-point invariant evaluators are deliberately excluded.
"""
from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_126bar_self_quartic_basis_v20 as sigma_source
import exact_210_pati_salam_global_vacuum_v20 as phi_source
import exact_gauged_u1x_g3_a_square_recoupling_v20 as mixed_source
import exact_gauged_u1x_g3_sos_bfb_stationarity_v20 as candidate_source
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_GLOBAL_COUNTEREXAMPLE_V20.json"
OUT_MD = ROOT / "EXACT_GAUGED_U1X_G3_GLOBAL_COUNTEREXAMPLE_V20.md"

MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"

# Coordinates are zero-based coefficients in chart.sigma_basis(), the
# canonical physical -i-Hodge 126bar basis.  Keeping real and imaginary parts
# separate makes the complete proof path Gaussian-integral.
WITNESS_COORDINATES = (
    (75, 1, 0),
    (77, 0, -1),
    (78, 0, -1),
    (80, 1, 0),
    (111, -1, 0),
    (113, 0, 1),
    (114, 0, 1),
    (116, -1, 0),
)
EXPECTED_WITNESS_NORM_SQUARED = 8

# This explicit support binds the coordinate indices to the repository's
# canonical basis ordering.  A basis-order or chirality drift therefore fails
# the certificate instead of silently changing the witness.
EXPECTED_CANONICAL_BASIS_SUPPORT = {
    75: (((0, 2, 4, 6, 7), 1, 0), ((1, 3, 5, 8, 9), 0, -1)),
    77: (((0, 2, 4, 6, 9), 1, 0), ((1, 3, 5, 7, 8), 0, -1)),
    78: (((0, 2, 4, 7, 8), 1, 0), ((1, 3, 5, 6, 9), 0, -1)),
    80: (((0, 2, 4, 8, 9), 1, 0), ((1, 3, 5, 6, 7), 0, -1)),
    111: (((0, 4, 5, 6, 7), 1, 0), ((1, 2, 3, 8, 9), 0, 1)),
    113: (((0, 4, 5, 6, 9), 1, 0), ((1, 2, 3, 7, 8), 0, 1)),
    114: (((0, 4, 5, 7, 8), 1, 0), ((1, 2, 3, 6, 9), 0, 1)),
    116: (((0, 4, 5, 8, 9), 1, 0), ((1, 2, 3, 6, 7), 0, 1)),
}

EXPECTED_KAPPA = {
    "54": Fraction(15),
    "1050bar": Fraction(7),
    "2772bar": Fraction(-5),
    "4125": Fraction(1),
}
PROJECTOR_CHANNELS = ("54", "1050bar", "2772bar", "4125")
EXPECTED_PROJECTOR_FRACTIONS = {
    "54": Fraction(0),
    "1050bar": Fraction(0),
    "2772bar": Fraction(1, 2),
    "4125": Fraction(1, 2),
}
EXPECTED_RAW_PROJECTOR_VALUES = {
    channel: value * EXPECTED_WITNESS_NORM_SQUARED**2
    for channel, value in EXPECTED_PROJECTOR_FRACTIONS.items()
}

SIGMA_SCALE = Fraction(1, 8)
SIGMA_RADIAL_COEFFICIENT = Fraction(25, 12)
SIGMA_SELF_WEIGHTS = {
    "54": Fraction(2),
    "1050bar": Fraction(2),
    "2772bar": Fraction(17, 16),
    "4125": Fraction(1),
}
EXPECTED_WITNESS_WEIGHTED_QUARTIC = Fraction(33, 32)
EXPECTED_DELTA_WEIGHTED_QUARTIC = Fraction(25, 24)
EXPECTED_OPTIMAL_NORM_SQUARED_OVER_R2 = Fraction(100, 99)
EXPECTED_COMPETITOR_HARD_ENERGY_OVER_R4 = Fraction(-625, 4752)
EXPECTED_SELECTED_HARD_ENERGY_OVER_R4 = Fraction(-25, 192)
EXPECTED_ENERGY_IMPROVEMENT_OVER_R4 = Fraction(25, 19008)
EXPECTED_SAME_NORM_IMPROVEMENT_OVER_R4 = Fraction(1, 768)


def _poly(*terms: tuple[Fraction | int, tuple[int, int, int]]) -> dict[tuple[int, int, int], Fraction]:
    return {exponent: Fraction(coefficient) for coefficient, exponent in terms}


# Exact nonzero candidate parameters containing Sigma.  The comparison with
# the complete 27-parameter source map below ensures that no hidden H/S/X
# coupling changes when only Sigma is replaced by the competitor.
EXPECTED_SIGMA_PARAMETER_COEFFICIENTS = {
    "lambda::O05_B01_126bar_norm": _poly(
        (Fraction(1, 2), (0, 0, 0)),
        (Fraction(-25, 96), (0, 2, 0)),
    ),
    "lambda::O14_B01_Phi_Sigma_Sigmadag_cubic": _poly(
        (Fraction(-1, 2), (0, 0, 0))
    ),
    "lambda::O27_B01_126bar_self_projectors": _poly(
        (Fraction(1, 4), (0, 0, 0))
    ),
    "lambda::O27_B02_126bar_self_projectors": _poly(
        (Fraction(1, 4), (0, 0, 0))
    ),
    "lambda::O27_B03_126bar_self_projectors": _poly(
        (Fraction(17, 128), (0, 0, 0))
    ),
    "lambda::O27_B04_126bar_self_projectors": _poly(
        (Fraction(1, 8), (0, 0, 0))
    ),
    "lambda::O44_B01_Phi2_Sigma_projectors": _poly(
        (Fraction(41, 8), (0, 0, 0))
    ),
    "lambda::O44_B02_Phi2_Sigma_projectors": _poly(
        (Fraction(73, 8), (0, 0, 0))
    ),
    "lambda::O44_B03_Phi2_Sigma_projectors": _poly(
        (Fraction(29, 8), (0, 0, 0))
    ),
    "lambda::O44_B04_Phi2_Sigma_projectors": _poly(
        (Fraction(-7, 8), (0, 0, 0))
    ),
    "lambda::O44_B05_Phi2_Sigma_projectors": _poly(
        (Fraction(-11, 8), (0, 0, 0))
    ),
    "lambda::O44_B06_Phi2_Sigma_projectors": _poly(
        (Fraction(13, 8), (0, 0, 0))
    ),
}


def _as_gaussian_integer(value: complex) -> tuple[int, int]:
    observed = complex(value)
    real = int(round(observed.real))
    imaginary = int(round(observed.imag))
    if observed != complex(real, imaginary):
        raise ArithmeticError(f"non-Gaussian-integer source entry: {value!r}")
    return real, imaginary


def _form_support(form: direct.Form) -> tuple[tuple[tuple[int, ...], int, int], ...]:
    output = []
    for indices, value in sorted(form.items()):
        real, imaginary = _as_gaussian_integer(value)
        if real or imaginary:
            output.append((indices, real, imaginary))
    return tuple(output)


@lru_cache(maxsize=1)
def canonical_witness_certificate() -> dict[str, Any]:
    basis = chart.sigma_basis()
    if len(basis) != chart.SIGMA_COMPLEX_DIM:
        raise ArithmeticError("canonical Sigma basis has the wrong dimension")

    real = np.zeros(chart.SIGMA_COMPLEX_DIM, dtype=np.int64)
    imaginary = np.zeros(chart.SIGMA_COMPLEX_DIM, dtype=np.int64)
    for index, real_value, imaginary_value in WITNESS_COORDINATES:
        if not 0 <= index < chart.SIGMA_COMPLEX_DIM:
            raise IndexError(f"Sigma witness index {index} is outside the chart")
        if real[index] or imaginary[index]:
            raise ArithmeticError(f"duplicate Sigma witness index {index}")
        real[index] = real_value
        imaginary[index] = imaginary_value

    observed_support = {
        index: _form_support(basis[index])
        for index, _, _ in WITNESS_COORDINATES
    }
    witness_form: direct.Form = {}
    for index, real_value, imaginary_value in WITNESS_COORDINATES:
        witness_form = direct.add_forms(
            witness_form,
            direct.scale_form(basis[index], complex(real_value, imaginary_value)),
        )

    kinetic_real, kinetic_imaginary = _as_gaussian_integer(
        direct.sigma_kinetic_inner(witness_form, witness_form)
    )
    hodge_residual = direct.add_forms(
        direct.hodge_star(witness_form), direct.scale_form(witness_form, 1j)
    )
    hodge_residual_support = _form_support(hodge_residual)
    norm_squared = int(real @ real + imaginary @ imaginary)

    return {
        "coordinate_convention": (
            "zero-based coefficients in live_g2_canonical_486_field_chart_v20."
            "sigma_basis(), the physical -i-Hodge 126bar basis"
        ),
        "nonzero_coordinates": tuple(
            {
                "index": index,
                "real": real_value,
                "imaginary": imaginary_value,
            }
            for index, real_value, imaginary_value in WITNESS_COORDINATES
        ),
        "canonical_basis_support": observed_support,
        "canonical_basis_support_matches_record": (
            observed_support == EXPECTED_CANONICAL_BASIS_SUPPORT
        ),
        "raw_norm_squared": norm_squared,
        "form_kinetic_norm_squared": kinetic_real,
        "form_kinetic_inner_imaginary": kinetic_imaginary,
        "minus_i_hodge_residual_support": hodge_residual_support,
        "physical_minus_i_hodge_chirality_exact": not hodge_residual_support,
        "normalized_unit_vector": "u=z/sqrt(8)",
        "real_coordinates": tuple(map(int, real)),
        "imaginary_coordinates": tuple(map(int, imaginary)),
        "source_binding_exact": True,
    }


def _witness_arrays() -> tuple[np.ndarray, np.ndarray]:
    certificate = canonical_witness_certificate()
    return (
        np.asarray(certificate["real_coordinates"], dtype=np.int64),
        np.asarray(certificate["imaginary_coordinates"], dtype=np.int64),
    )


def _pati_salam_vector() -> tuple[np.ndarray, tuple[tuple[int, tuple[int, ...], int], ...]]:
    _, observed = phi_source.pati_salam_direction()
    integer = np.rint(observed).astype(np.int64)
    if np.max(np.abs(observed - integer), initial=0.0) != 0.0:
        raise ArithmeticError("Pati-Salam P is not an exact integer source vector")
    support = tuple(
        (index, chart.PHI_INDICES[index], int(value))
        for index, value in enumerate(integer)
        if value
    )
    return integer, support


@lru_cache(maxsize=1)
def exact_mixed_kernel_certificate() -> dict[str, Any]:
    z_real, z_imaginary = _witness_arrays()
    p_vector, p_support = _pati_salam_vector()

    contraction_real, contraction_imaginary = mixed_source.integer_contraction_tensor()
    expected_contraction_shape = (
        direct.N,
        chart.PHI_DIM,
        chart.SIGMA_COMPLEX_DIM,
    )
    if contraction_real.shape != expected_contraction_shape:
        raise ArithmeticError("C contraction source tensor has the wrong shape")
    if contraction_imaginary.shape != expected_contraction_shape:
        raise ArithmeticError("imaginary C source tensor has the wrong shape")

    c_real = (
        np.einsum(
            "vpa,p,a->v",
            contraction_real,
            p_vector,
            z_real,
            optimize=True,
        )
        - np.einsum(
            "vpa,p,a->v",
            contraction_imaginary,
            p_vector,
            z_imaginary,
            optimize=True,
        )
    )
    c_imaginary = (
        np.einsum(
            "vpa,p,a->v",
            contraction_real,
            p_vector,
            z_imaginary,
            optimize=True,
        )
        + np.einsum(
            "vpa,p,a->v",
            contraction_imaginary,
            p_vector,
            z_real,
            optimize=True,
        )
    )

    operator_real, operator_imaginary = mixed_source.integer_cubic_operators()
    expected_operator_shape = (
        chart.PHI_DIM,
        chart.SIGMA_COMPLEX_DIM,
        chart.SIGMA_COMPLEX_DIM,
    )
    if operator_real.shape != expected_operator_shape:
        raise ArithmeticError("cubic M source tensor has the wrong shape")
    if operator_imaginary.shape != expected_operator_shape:
        raise ArithmeticError("imaginary cubic M source tensor has the wrong shape")

    matrix_real = np.tensordot(p_vector, operator_real, axes=(0, 0))
    matrix_imaginary = np.tensordot(p_vector, operator_imaginary, axes=(0, 0))
    image_real = matrix_real @ z_real - matrix_imaginary @ z_imaginary
    image_imaginary = matrix_real @ z_imaginary + matrix_imaginary @ z_real
    residual_real = image_real - 2 * z_real
    residual_imaginary = image_imaginary - 2 * z_imaginary

    c_nonzero = tuple(
        (index, int(c_real[index]), int(c_imaginary[index]))
        for index in range(direct.N)
        if c_real[index] or c_imaginary[index]
    )
    a_nonzero = tuple(
        (index, int(residual_real[index]), int(residual_imaginary[index]))
        for index in range(chart.SIGMA_COMPLEX_DIM)
        if residual_real[index] or residual_imaginary[index]
    )
    hermitian = bool(
        np.array_equal(operator_real.transpose(0, 2, 1), operator_real)
        and np.array_equal(
            operator_imaginary.transpose(0, 2, 1), -operator_imaginary
        )
    )

    return {
        "P_definition": "P=e_[6,7,8,9] in the canonical real 210 chart",
        "P_support": p_support,
        "P_norm_squared": int(p_vector @ p_vector),
        "A_operator_convention": "A_P=M(P), from the live cubic source tensor",
        "C_output_complex_dimension": direct.N,
        "C_P_z_nonzero_residuals": c_nonzero,
        "C_P_z_norm_squared": sum(int(value) ** 2 for value in c_real)
        + sum(int(value) ** 2 for value in c_imaginary),
        "A_P_minus_2_z_nonzero_residuals": a_nonzero,
        "A_P_minus_2_z_norm_squared": sum(int(value) ** 2 for value in residual_real)
        + sum(int(value) ** 2 for value in residual_imaginary),
        "cubic_source_tensor_exactly_hermitian": hermitian,
        "contraction_tensor_shape": contraction_real.shape,
        "cubic_operator_tensor_shape": operator_real.shape,
        "source_binding_exact": True,
    }


@lru_cache(maxsize=1)
def _integer_sigma_generators() -> tuple[np.ndarray, np.ndarray]:
    real, imaginary = candidate_source.integer_sigma_generators()
    if real.shape != (45, chart.SIGMA_COMPLEX_DIM, chart.SIGMA_COMPLEX_DIM):
        raise ArithmeticError("126bar generator source has the wrong shape")
    if imaginary.shape != real.shape:
        raise ArithmeticError("126bar generator source parts disagree in shape")
    return real, imaginary


def _casimir_growth_factor() -> int:
    real, imaginary = _integer_sigma_generators()
    factor = 0
    for generator_real, generator_imaginary in zip(real, imaginary, strict=True):
        row_l1 = max(
            int(value)
            for value in np.sum(
                np.abs(generator_real).astype(np.int64)
                + np.abs(generator_imaginary).astype(np.int64),
                axis=1,
            )
        )
        factor += row_l1**2
    return factor


def _sigma_pair_casimir(
    pair_real: np.ndarray, pair_imaginary: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Apply the 126 pair Casimir exactly, with a pre-overflow guard."""
    input_real = np.asarray(pair_real, dtype=np.int64)
    input_imaginary = np.asarray(pair_imaginary, dtype=np.int64)
    expected_shape = (chart.SIGMA_COMPLEX_DIM, chart.SIGMA_COMPLEX_DIM)
    if input_real.shape != expected_shape or input_imaginary.shape != expected_shape:
        raise ValueError("Sigma pair must be a pair of 126x126 integer matrices")

    maximum = max(
        int(np.max(np.abs(input_real), initial=0)),
        int(np.max(np.abs(input_imaginary), initial=0)),
    )
    if maximum * _casimir_growth_factor() > np.iinfo(np.int64).max:
        raise OverflowError("pair-Casimir int64 bound is not proof-safe")

    generators_real, generators_imaginary = _integer_sigma_generators()
    output_real = np.zeros_like(input_real)
    output_imaginary = np.zeros_like(input_imaginary)
    for real, imaginary in zip(
        generators_real, generators_imaginary, strict=True
    ):
        left_real = real @ input_real - imaginary @ input_imaginary
        left_imaginary = real @ input_imaginary + imaginary @ input_real
        output_real += left_real @ real.T - left_imaginary @ imaginary.T
        output_imaginary += left_real @ imaginary.T + left_imaginary @ real.T
    return output_real, output_imaginary


def _projector_polynomial(channel: str) -> tuple[Fraction, ...]:
    if channel not in sigma_source.KAPPA:
        raise KeyError(channel)
    target = Fraction(sigma_source.KAPPA[channel])
    coefficients = [Fraction(1)]
    denominator = Fraction(1)
    for other_value in sigma_source.KAPPA.values():
        other = Fraction(other_value)
        if other == target:
            continue
        output = [Fraction(0)] * (len(coefficients) + 1)
        for degree, coefficient in enumerate(coefficients):
            output[degree] -= other * coefficient
            output[degree + 1] += coefficient
        coefficients = output
        denominator *= target - other
    return tuple(coefficient / denominator for coefficient in coefficients)


def _project_from_powers(
    powers: tuple[tuple[np.ndarray, np.ndarray], ...], channel: str
) -> tuple[np.ndarray, np.ndarray, int]:
    polynomial = _projector_polynomial(channel)
    denominator = math.lcm(*(value.denominator for value in polynomial))
    numerators = tuple(int(value * denominator) for value in polynomial)
    absolute_bound = sum(
        abs(coefficient)
        * max(
            int(np.max(np.abs(real), initial=0)),
            int(np.max(np.abs(imaginary), initial=0)),
        )
        for coefficient, (real, imaginary) in zip(numerators, powers, strict=True)
    )
    if absolute_bound > np.iinfo(np.int64).max:
        raise OverflowError("projector numerator int64 bound is not proof-safe")

    result_real = sum(
        (
            coefficient * power[0]
            for coefficient, power in zip(numerators, powers, strict=True)
        ),
        np.zeros_like(powers[0][0]),
    )
    result_imaginary = sum(
        (
            coefficient * power[1]
            for coefficient, power in zip(numerators, powers, strict=True)
        ),
        np.zeros_like(powers[0][1]),
    )
    return result_real, result_imaginary, denominator


@lru_cache(maxsize=1)
def exact_self_projector_certificate() -> dict[str, Any]:
    z_real, z_imaginary = _witness_arrays()
    norm_squared = int(z_real @ z_real + z_imaginary @ z_imaginary)
    pair_real = np.outer(z_real, z_real) - np.outer(z_imaginary, z_imaginary)
    pair_imaginary = np.outer(z_real, z_imaginary) + np.outer(
        z_imaginary, z_real
    )
    powers = [(pair_real, pair_imaginary)]
    for _ in range(3):
        powers.append(_sigma_pair_casimir(*powers[-1]))
    powers_tuple = tuple(powers)

    projected = {
        channel: _project_from_powers(powers_tuple, channel)
        for channel in PROJECTOR_CHANNELS
    }
    raw_values: dict[str, Fraction] = {}
    fractions: dict[str, Fraction] = {}
    eigen_residuals: dict[str, int] = {}
    for channel, (real, imaginary, denominator) in projected.items():
        numerator = sum(int(value) ** 2 for value in real.flat) + sum(
            int(value) ** 2 for value in imaginary.flat
        )
        raw_values[channel] = Fraction(numerator, denominator**2)
        fractions[channel] = raw_values[channel] / norm_squared**2

        image_real, image_imaginary = _sigma_pair_casimir(real, imaginary)
        eigenvalue = Fraction(sigma_source.KAPPA[channel])
        cleared_real = eigenvalue.denominator * image_real - int(
            eigenvalue.numerator
        ) * real
        cleared_imaginary = eigenvalue.denominator * image_imaginary - int(
            eigenvalue.numerator
        ) * imaginary
        eigen_residuals[channel] = max(
            int(np.max(np.abs(cleared_real), initial=0)),
            int(np.max(np.abs(cleared_imaginary), initial=0)),
        )

    common_denominator = math.lcm(
        *(denominator for _, _, denominator in projected.values())
    )
    reconstructed_real = sum(
        (
            (common_denominator // denominator) * real
            for real, _, denominator in projected.values()
        ),
        np.zeros_like(pair_real),
    )
    reconstructed_imaginary = sum(
        (
            (common_denominator // denominator) * imaginary
            for _, imaginary, denominator in projected.values()
        ),
        np.zeros_like(pair_imaginary),
    )
    reconstruction_residual = max(
        int(
            np.max(
                np.abs(reconstructed_real - common_denominator * pair_real),
                initial=0,
            )
        ),
        int(
            np.max(
                np.abs(
                    reconstructed_imaginary
                    - common_denominator * pair_imaginary
                ),
                initial=0,
            )
        ),
    )

    orthogonality: dict[str, Fraction] = {}
    for left_index, left in enumerate(PROJECTOR_CHANNELS):
        left_real, left_imaginary, left_denominator = projected[left]
        for right in PROJECTOR_CHANNELS[left_index + 1 :]:
            right_real, right_imaginary, right_denominator = projected[right]
            numerator = sum(
                int(a) * int(b)
                for a, b in zip(left_real.flat, right_real.flat, strict=True)
            ) + sum(
                int(a) * int(b)
                for a, b in zip(
                    left_imaginary.flat, right_imaginary.flat, strict=True
                )
            )
            orthogonality[f"{left}__{right}"] = Fraction(
                numerator, left_denominator * right_denominator
            )

    polynomials = {
        channel: _projector_polynomial(channel) for channel in PROJECTOR_CHANNELS
    }
    polynomial_sum = tuple(
        sum(polynomials[channel][degree] for channel in PROJECTOR_CHANNELS)
        for degree in range(4)
    )
    weighted_quartic = sum(
        SIGMA_SELF_WEIGHTS[channel] * fractions[channel]
        for channel in PROJECTOR_CHANNELS
    )
    generators_real, generators_imaginary = _integer_sigma_generators()
    antihermitian = bool(
        np.array_equal(generators_real.transpose(0, 2, 1), -generators_real)
        and np.array_equal(
            generators_imaginary.transpose(0, 2, 1), generators_imaginary
        )
    )

    return {
        "pair_convention": "holomorphic z tensor z (not z tensor conjugate(z))",
        "source_pair_Casimir_eigenvalues": {
            channel: Fraction(sigma_source.KAPPA[channel])
            for channel in PROJECTOR_CHANNELS
        },
        "projector_polynomials": polynomials,
        "projector_polynomial_sum": polynomial_sum,
        "raw_projector_values_for_z": raw_values,
        "normalized_projector_fractions_for_u": fractions,
        "normalized_fraction_sum": sum(fractions.values()),
        "projected_pair_reconstruction_max_abs_residual": reconstruction_residual,
        "projected_pair_orthogonality_inner_products": orthogonality,
        "projector_eigen_equation_max_abs_residuals": eigen_residuals,
        "weighted_quartic_formula": (
            "W=2 I54+2 I1050bar+(17/16) I2772bar+I4125"
        ),
        "weighted_quartic_at_u": weighted_quartic,
        "weighted_quartic_at_Delta_R": EXPECTED_DELTA_WEIGHTED_QUARTIC,
        "strict_weight_improvement": (
            EXPECTED_DELTA_WEIGHTED_QUARTIC - weighted_quartic
        ),
        "generators_exactly_antihermitian": antihermitian,
        "casimir_int64_growth_factor": _casimir_growth_factor(),
        "source_binding_exact": True,
    }


@lru_cache(maxsize=1)
def exact_candidate_source_certificate() -> dict[str, Any]:
    expanded = candidate_source.expanded_sos_coefficient_map()
    declared = candidate_source.declared_candidate_coefficient_map()
    sigma_entries = {
        parameter_id: value
        for parameter_id, value in expanded.items()
        if "Sigma" in parameter_id or "126bar" in parameter_id
    }
    source_weights = {
        channel: Fraction(value)
        for channel, value in candidate_source.SIGMA_SELF_WEIGHTS.items()
    }
    delta_fractions = {
        channel: Fraction(value)
        for channel, value in candidate_source.RECORDED_DELTA_FRACTIONS.items()
    }
    delta_weighted_quartic = sum(
        source_weights[channel] * delta_fractions[channel]
        for channel in PROJECTOR_CHANNELS
    )
    return {
        "model_contract_id": candidate_source.MODEL_CONTRACT_ID,
        "nonzero_parameter_count": len(expanded),
        "expanded_map_equals_declared_map": expanded == declared,
        "all_other_exact_X_parameters": "zero by the complete source map",
        "nonzero_Sigma_parameter_count": len(sigma_entries),
        "nonzero_Sigma_parameters": sigma_entries,
        "nonzero_Sigma_parameters_match_record": (
            sigma_entries == EXPECTED_SIGMA_PARAMETER_COEFFICIENTS
        ),
        "Sigma_scale": Fraction(candidate_source.SIGMA_SCALE),
        "Sigma_radial_coefficient": Fraction(
            candidate_source.SIGMA_RADIAL_COEFFICIENT
        ),
        "Sigma_self_weights": source_weights,
        "Delta_R_projector_fractions": delta_fractions,
        "Delta_R_weighted_quartic": delta_weighted_quartic,
        "hard_Sigma_sector": (
            "(1/8)[||(M(Phi)-2)Sigma||^2+||C_Phi Sigma||^2+"
            "W(Sigma)-(25/12)r^2||Sigma||^2]"
        ),
        "source_binding_exact": True,
    }


@lru_cache(maxsize=1)
def exact_energy_certificate() -> dict[str, Any]:
    projector = exact_self_projector_certificate()
    source = exact_candidate_source_certificate()
    weight = Fraction(projector["weighted_quartic_at_u"])
    delta_weight = Fraction(source["Delta_R_weighted_quartic"])
    scale = Fraction(source["Sigma_scale"])
    radial = Fraction(source["Sigma_radial_coefficient"])

    optimal_norm = radial / (2 * weight)
    competitor_energy = scale * (
        weight * optimal_norm**2 - radial * optimal_norm
    )
    selected_energy = scale * (delta_weight - radial)
    improvement = selected_energy - competitor_energy
    same_norm_energy = scale * (weight - radial)
    same_norm_improvement = selected_energy - same_norm_energy

    return {
        "formal_scale_assumption": "r>0",
        "unit_direction": "u=z/sqrt(8)",
        "competitor_field": (
            "Phi=P, Sigma=(5r/(3 sqrt(22))) z, H=h e6, S=r, Phi17=x"
        ),
        "all_non_Sigma_fields": "identical to the selected stationary vacuum",
        "hard_ray_polynomial": (
            "E_hard(n)/r^4=(1/8)[(33/32)(n/r^2)^2-"
            "(25/12)(n/r^2)]"
        ),
        "positive_ray_quartic_coefficient": weight,
        "optimal_Sigma_norm_squared_over_r_squared": optimal_norm,
        "optimality_first_derivative_residual": 2 * weight * optimal_norm
        - radial,
        "optimality_second_derivative": 2 * weight,
        "competitor_hard_Sigma_energy_over_r4": competitor_energy,
        "selected_hard_Sigma_energy_over_r4": selected_energy,
        "selected_minus_competitor_energy_over_r4": improvement,
        "strict_improvement_for_r_positive": improvement > 0,
        "same_norm_competitor_hard_energy_over_r4": same_norm_energy,
        "same_norm_selected_minus_competitor_energy_over_r4": (
            same_norm_improvement
        ),
        "full_potential_difference": (
            "V_selected-V_competitor=(25/19008)r^4; every other exact "
            "candidate term is unchanged"
        ),
        "actual_global_minimum_location": "not established",
        "source_binding_exact": True,
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    witness = canonical_witness_certificate()
    mixed = exact_mixed_kernel_certificate()
    projector = exact_self_projector_certificate()
    source = exact_candidate_source_certificate()
    energy = exact_energy_certificate()

    checks = {
        "model_contract_matches_exact_X_candidate": (
            source["model_contract_id"] == MODEL_CONTRACT_ID
        ),
        "complete_27_parameter_candidate_map_source_bound": (
            source["nonzero_parameter_count"] == 27
            and source["expanded_map_equals_declared_map"]
        ),
        "all_nonzero_Sigma_parameters_match_exact_record": (
            source["nonzero_Sigma_parameter_count"]
            == len(EXPECTED_SIGMA_PARAMETER_COEFFICIENTS)
            and source["nonzero_Sigma_parameters_match_record"]
        ),
        "hard_Sigma_coefficients_match_candidate": (
            source["Sigma_scale"] == SIGMA_SCALE
            and source["Sigma_radial_coefficient"]
            == SIGMA_RADIAL_COEFFICIENT
            and source["Sigma_self_weights"] == SIGMA_SELF_WEIGHTS
        ),
        "canonical_minus_i_Hodge_basis_support_exact": (
            witness["canonical_basis_support_matches_record"]
            and witness["physical_minus_i_hodge_chirality_exact"]
        ),
        "witness_norm_squared_is_eight": (
            witness["raw_norm_squared"] == EXPECTED_WITNESS_NORM_SQUARED
            and witness["form_kinetic_norm_squared"]
            == EXPECTED_WITNESS_NORM_SQUARED
            and witness["form_kinetic_inner_imaginary"] == 0
        ),
        "P_is_exact_canonical_e6789": (
            mixed["P_support"] == ((209, (6, 7, 8, 9), 1),)
            and mixed["P_norm_squared"] == 1
        ),
        "C_P_z_vanishes_exactly": (
            not mixed["C_P_z_nonzero_residuals"]
            and mixed["C_P_z_norm_squared"] == 0
        ),
        "A_P_minus_2_z_vanishes_exactly": (
            not mixed["A_P_minus_2_z_nonzero_residuals"]
            and mixed["A_P_minus_2_z_norm_squared"] == 0
            and mixed["cubic_source_tensor_exactly_hermitian"]
        ),
        "126_pair_Casimir_source_eigenvalues_exact": (
            projector["source_pair_Casimir_eigenvalues"] == EXPECTED_KAPPA
            and projector["generators_exactly_antihermitian"]
        ),
        "126_projectors_are_complete_orthogonal_and_exact": (
            projector["projector_polynomial_sum"]
            == (Fraction(1), Fraction(0), Fraction(0), Fraction(0))
            and projector["projected_pair_reconstruction_max_abs_residual"] == 0
            and all(
                value == 0
                for value in projector[
                    "projected_pair_orthogonality_inner_products"
                ].values()
            )
            and all(
                value == 0
                for value in projector[
                    "projector_eigen_equation_max_abs_residuals"
                ].values()
            )
        ),
        "raw_projector_values_match_exact_witness": (
            projector["raw_projector_values_for_z"]
            == EXPECTED_RAW_PROJECTOR_VALUES
        ),
        "normalized_projector_fractions_are_0_0_half_half": (
            projector["normalized_projector_fractions_for_u"]
            == EXPECTED_PROJECTOR_FRACTIONS
            and projector["normalized_fraction_sum"] == 1
        ),
        "witness_weighted_quartic_is_33_over_32": (
            projector["weighted_quartic_at_u"]
            == EXPECTED_WITNESS_WEIGHTED_QUARTIC
        ),
        "witness_weight_is_strictly_below_Delta_R": (
            source["Delta_R_weighted_quartic"]
            == EXPECTED_DELTA_WEIGHTED_QUARTIC
            and projector["strict_weight_improvement"] == Fraction(1, 96)
        ),
        "optimal_competitor_norm_is_100_over_99_r2": (
            energy["optimal_Sigma_norm_squared_over_r_squared"]
            == EXPECTED_OPTIMAL_NORM_SQUARED_OVER_R2
            and energy["optimality_first_derivative_residual"] == 0
            and energy["optimality_second_derivative"] > 0
        ),
        "hard_Sigma_energies_match_exact_values": (
            energy["competitor_hard_Sigma_energy_over_r4"]
            == EXPECTED_COMPETITOR_HARD_ENERGY_OVER_R4
            and energy["selected_hard_Sigma_energy_over_r4"]
            == EXPECTED_SELECTED_HARD_ENERGY_OVER_R4
        ),
        "strict_full_candidate_energy_lowering_is_25_over_19008_r4": (
            energy["selected_minus_competitor_energy_over_r4"]
            == EXPECTED_ENERGY_IMPROVEMENT_OVER_R4
            and energy["strict_improvement_for_r_positive"]
        ),
        "same_norm_direction_already_lowers_energy": (
            energy["same_norm_selected_minus_competitor_energy_over_r4"]
            == EXPECTED_SAME_NORM_IMPROVEMENT_OVER_R4
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    proof_complete = not failures

    return {
        "status": (
            "EXACT_GAUGED_U1X_G3_GLOBAL_COUNTEREXAMPLE_CERTIFIED"
            if proof_complete
            else "EXACT_GAUGED_U1X_G3_GLOBAL_COUNTEREXAMPLE_FAILED"
        ),
        "overall_state": (
            "SELECTED_GLOBAL_MINIMUM_CLAIM_FALSIFIED"
            if proof_complete
            else "EXECUTION_FAIL"
        ),
        "model_contract_id": MODEL_CONTRACT_ID,
        "proof_scope": (
            "Exact counterexample to global minimality of the current 27-parameter "
            "constructive G3 candidate for every r>0"
        ),
        "arithmetic": "Gaussian integers plus fractions.Fraction; no float proof step",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "canonical_witness": witness,
        "exact_mixed_kernel": mixed,
        "exact_126bar_projectors": projector,
        "exact_candidate_source_binding": source,
        "exact_energy_comparison": energy,
        "flags": {
            "exact_global_counterexample_source_bound": proof_complete,
            "lower_energy_field_witness_exactly_certified": proof_complete,
            "selected_vacuum_global_minimum_disproved": proof_complete,
            "selected_vacuum_unique_global_minimum_modulo_symmetry_disproved": (
                proof_complete
            ),
            "selected_vacuum_strict_local_minimum_remains_valid": True,
            "strict_local_minimum_recomputed_here": False,
            "actual_global_minimum_classified": False,
            "G3_selected_global_claim_falsified": proof_complete,
            "G3_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "whole_theory_excluded": False,
        },
        "interpretation": (
            "A strict local minimum may have a lower disconnected competitor. "
            "This exact witness invalidates only the selected vacuum's global-"
            "minimum and global-uniqueness claims. It neither locates the true "
            "global minimum nor excludes the full model or theory."
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


def _markdown(report: dict[str, Any]) -> str:
    energy = report["exact_energy_comparison"]
    flags = report["flags"]
    return "\n".join(
        (
            "# Exact gauged-U(1)X G3 global counterexample -- v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            "For the canonical physical 126bar vector",
            "",
            "`z[75]=z[80]=1, z[77]=z[78]=-i, "
            "z[111]=z[116]=-1, z[113]=z[114]=+i`,",
            "",
            "the exact source tensors give `||z||^2=8`, "
            "`(M(P)-2)z=0`, and `C_P z=0`.",
            "",
            "For `u=z/sqrt(8)`, the exact projector fractions are",
            "",
            "`(I54,I1050bar,I2772bar,I4125)=(0,0,1/2,1/2)`,",
            "",
            "so `W(u)=33/32 < 25/24=W(Delta_R)`.",
            "",
            "The optimal competitor is",
            "",
            "`Phi=P, Sigma=(5r/(3 sqrt(22)))z, H=h e6, S=r, Phi17=x`,",
            "",
            "with",
            "",
            f"- `||Sigma||^2/r^2 = {energy['optimal_Sigma_norm_squared_over_r_squared']}`",
            f"- competitor hard Sigma energy: `{energy['competitor_hard_Sigma_energy_over_r4']} r^4`",
            f"- selected hard Sigma energy: `{energy['selected_hard_Sigma_energy_over_r4']} r^4`",
            f"- exact lowering: `{energy['selected_minus_competitor_energy_over_r4']} r^4`",
            "",
            f"- selected global minimum disproved: `{flags['selected_vacuum_global_minimum_disproved']}`",
            f"- selected global uniqueness disproved: `{flags['selected_vacuum_unique_global_minimum_modulo_symmetry_disproved']}`",
            f"- strict local minimum remains valid: `{flags['selected_vacuum_strict_local_minimum_remains_valid']}`",
            f"- actual global minimum classified: `{flags['actual_global_minimum_classified']}`",
            f"- whole model excluded: `{flags['whole_model_excluded']}`",
            f"- whole theory excluded: `{flags['whole_theory_excluded']}`",
            "",
            "The strict comparison assumes `r>0`, as does the candidate's "
            "formal scale contract. The artifact does not classify the true "
            "global minimum and does not modify the independent local-Hessian "
            "certificate.",
            "",
        )
    )


def write_report(
    report: dict[str, Any],
    *,
    json_path: Path = OUT_JSON,
    markdown_path: Path = OUT_MD,
) -> None:
    json_path.write_text(
        json.dumps(_jsonable(report), indent=2) + "\n", encoding="utf-8"
    )
    markdown_path.write_text(_markdown(report), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(_jsonable(report), indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
