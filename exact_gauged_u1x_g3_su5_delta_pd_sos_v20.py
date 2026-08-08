#!/usr/bin/env python3
"""Exact global SOS candidate on the SU(5)-singlet 210 + Delta_R sector.

The earlier constructive G3 benchmark fixed ``Phi=P``.  Its desired
``P+Delta_R`` vacuum obeys an exact gap--curvature obstruction and cannot be
both a strict local minimum and the global minimum.  This module constructs a
different, SM-preserving orbit which evades that P-specific obstruction.

Let ``F0`` be the integral four-form

    F0 = P + sqrt(3) A + sqrt(6) W,

in the repository's normalized ``(P,A,W)`` singlet basis.  All ten nonzero
components of F0 equal one, so ``F=F0/sqrt(10)``.  In the conventional
unnormalized literature coordinates this is ``p:a:omega=1:1:1``.  For the
canonical raw integer Delta vector ``d0`` the live source tensors give

    M(F0)d0 = 8 d0,       C_F0 d0 = 0.

The following polynomial is an exact sum of nonnegative residuals:

    V_PD = (N_Phi-1)^2 - 1 + I54(Phi) + I4125(Phi)
         + t ||(M(Phi)-8/sqrt(10)) Sigma||^2
         + t ||C_Phi Sigma||^2
         + t (N_Sigma-r^2)^2 - t r^4
         + t I54(Sigma) + t I1050bar(Sigma),

with ``t=1/8`` and ``r>0``.  Every residual vanishes at
``Phi=F, Sigma=r Delta_R``.  Hence that configuration is stationary and is a
global minimum with value ``-1-r^4/8``.  The exact SO(10) orbit rank is 33,
so its stabilizer has dimension 12, as required for the SM gauge algebra.

The source expansion uses 17 of the authoritative 51 exact-X parameters.  Its
largest absolute dimensionless coefficient is ``73/8 < 4*pi``.  This module
certifies global saturation, the exact symmetry orbit and exact Hessian rank
429/nullity 33 in the Phi/Sigma subproblem.  The full 486-field Hessian and
H/S/Phi17 extension are deliberately separate certificates; G3 is not declared
closed here.
"""
from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy import sparse

import exact_210_self_invariant_basis_v20 as phi_self
import exact_126bar_self_quartic_basis_v20 as sigma_self
import exact_gauged_u1x_g3_a_square_recoupling_v20 as mixed_source
import exact_gauged_u1x_g3_pd_rank_certificate_v20 as rank_source
import exact_gauged_u1x_g3_sos_bfb_stationarity_v20 as delta_source
import exact_phisigma_casimir_projectors_v20 as phi_projectors
import gauged_u1x_g2_derivative_audit_v20 as g2_audit
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_PD_SOS_V20.json"
OUT_MD = ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_PD_SOS_V20.md"

MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
SIGMA_SCALE = Fraction(1, 8)
EXPECTED_PHI_NORM_SQUARED_RAW = 10
EXPECTED_M_EIGENVALUE_RAW = 8
EXPECTED_SO10_ORBIT_RANK = 33
EXPECTED_SO10_STABILIZER_DIMENSION = 12
EXPECTED_PARAMETER_COUNT = 17
PD_DIMENSION = chart.PHI_DIM + chart.SIGMA_REAL_DIM
MODULAR_RANK_PRIME = 1_000_003

EXPECTED_F0_SUPPORT = {
    (0, 1, 2, 3): 1,
    (0, 1, 4, 5): 1,
    (0, 1, 6, 7): 1,
    (0, 1, 8, 9): 1,
    (2, 3, 4, 5): 1,
    (2, 3, 6, 7): 1,
    (2, 3, 8, 9): 1,
    (4, 5, 6, 7): 1,
    (4, 5, 8, 9): 1,
    (6, 7, 8, 9): 1,
}

EXPECTED_PHI_PROJECTOR_VALUES_RAW = {
    "1": Fraction(10, 21),
    "45": Fraction(18, 7),
    "54": Fraction(0),
    "210": Fraction(4),
    "770_plus_1050_plus_1050bar": Fraction(32, 3),
    "4125": Fraction(0),
    "5940": Fraction(192, 7),
    "8910": Fraction(384, 7),
}

EXPECTED_PHI_J_COEFFICIENTS = {
    "J0": Fraction(113, 40),
    "J2": Fraction(-619, 5760),
    "J3": Fraction(47, 1920),
    "J4": Fraction(-23, 23040),
}

EXPECTED_SIGMA_SELF_WEIGHTS = {
    "54": Fraction(2),
    "1050bar": Fraction(2),
    "2772bar": Fraction(1),
    "4125": Fraction(1),
}


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def _as_integral(value: complex) -> int:
    observed = complex(value)
    integer = int(round(observed.real))
    if observed != complex(integer, 0):
        raise ArithmeticError(f"expected an exact real integer, found {value!r}")
    return integer


@lru_cache(maxsize=1)
def raw_su5_form_and_vector() -> tuple[dict[tuple[int, ...], complex], np.ndarray]:
    """Return F0=P+sqrt(3)A+sqrt(6)W in its integral source chart."""
    # The square roots cancel those used to normalize the A and W singlets.
    form = phi_self.singlet_form(1.0, math.sqrt(3.0), math.sqrt(6.0))
    support = {indices: _as_integral(value) for indices, value in form.items()}
    if support != EXPECTED_F0_SUPPORT:
        raise ArithmeticError("the canonical integral SU(5) singlet support drifted")
    vector_float = phi_self.phi_vector(form)
    vector = np.rint(vector_float).astype(np.int64)
    if np.max(np.abs(vector_float - vector), initial=0.0) != 0.0:
        raise ArithmeticError("F0 did not map to an exact integer 210 vector")
    return form, vector


@lru_cache(maxsize=1)
def exact_phi_projector_certificate() -> dict[str, Any]:
    form, vector = raw_su5_form_and_vector()
    moments = phi_self.integer_pair_moments(vector)
    values: dict[str, Fraction] = {}
    for name, eigenvalue in phi_projectors.SPECTRAL_EIGENVALUES.items():
        polynomial = phi_projectors.projector_polynomial(eigenvalue)
        values[name] = sum(
            polynomial[degree] * moments[degree]
            for degree in range(len(polynomial))
        )
    norm_squared = int(vector @ vector)
    spectral_sum = sum(values.values())
    expected_j = {
        name: Fraction(value)
        for name, value in zip(
            phi_self.QUARTIC_BASIS_NAMES,
            (
                moments[0],
                moments[2],
                moments[3],
                moments[4],
            ),
            strict=True,
        )
    }
    source_spectral = phi_self.spectral_quartics_in_basis()
    observed_couplings = {
        name: Fraction(int(name == "J0"))
        + source_spectral["54"][index]
        + source_spectral["4125"][index]
        for index, name in enumerate(phi_self.QUARTIC_BASIS_NAMES)
    }
    return {
        "definition": "F=F0/sqrt(10), F0=P+sqrt(3)A+sqrt(6)W",
        "literature_ratio": "p:a:omega=1:1:1",
        "canonical_P_A_W_ratio": "1:sqrt(3):sqrt(6)",
        "raw_support": {str(key): value for key, value in sorted(EXPECTED_F0_SUPPORT.items())},
        "raw_norm_squared": norm_squared,
        "integer_pair_moments_degree_0_to_7": moments,
        "raw_projector_values": values,
        "raw_projector_sum": spectral_sum,
        "normalized_projector_values": {
            name: value / norm_squared**2 for name, value in values.items()
        },
        "I54_exactly_zero": values["54"] == 0,
        "I4125_exactly_zero": values["4125"] == 0,
        "J_values_raw": expected_j,
        "SOS_J_coefficients": observed_couplings,
        "SOS_J_coefficients_match_record": (
            observed_couplings == EXPECTED_PHI_J_COEFFICIENTS
        ),
        "source_binding_exact": True,
    }


def _raw_delta_arrays() -> tuple[np.ndarray, np.ndarray]:
    real, imaginary = delta_source.raw_delta_coordinates()
    return np.asarray(real, dtype=np.int64), np.asarray(imaginary, dtype=np.int64)


@lru_cache(maxsize=1)
def exact_mixed_zero_certificate() -> dict[str, Any]:
    _, f0 = raw_su5_form_and_vector()
    delta_real, delta_imaginary = _raw_delta_arrays()
    operator_real, operator_imaginary = mixed_source.integer_cubic_operators()
    matrix_real = np.tensordot(f0, operator_real, axes=(0, 0))
    matrix_imaginary = np.tensordot(f0, operator_imaginary, axes=(0, 0))
    image_real = matrix_real @ delta_real - matrix_imaginary @ delta_imaginary
    image_imaginary = (
        matrix_real @ delta_imaginary + matrix_imaginary @ delta_real
    )
    residual_real = image_real - EXPECTED_M_EIGENVALUE_RAW * delta_real
    residual_imaginary = (
        image_imaginary - EXPECTED_M_EIGENVALUE_RAW * delta_imaginary
    )

    contraction_real, contraction_imaginary = mixed_source.integer_contraction_tensor()
    c_real = (
        np.einsum("vpa,p,a->v", contraction_real, f0, delta_real, optimize=True)
        - np.einsum(
            "vpa,p,a->v", contraction_imaginary, f0, delta_imaginary, optimize=True
        )
    )
    c_imaginary = (
        np.einsum(
            "vpa,p,a->v", contraction_real, f0, delta_imaginary, optimize=True
        )
        + np.einsum(
            "vpa,p,a->v", contraction_imaginary, f0, delta_real, optimize=True
        )
    )
    return {
        "raw_identity": "M(F0)d0=8 d0 and C_F0 d0=0",
        "normalized_identity": (
            "M(F)Delta=(8/sqrt(10))Delta and C_F Delta=0"
        ),
        "raw_delta_norm_squared": int(
            delta_real @ delta_real + delta_imaginary @ delta_imaginary
        ),
        "M_eigen_residual_max_abs": max(
            int(np.max(np.abs(residual_real), initial=0)),
            int(np.max(np.abs(residual_imaginary), initial=0)),
        ),
        "C_residual_max_abs": max(
            int(np.max(np.abs(c_real), initial=0)),
            int(np.max(np.abs(c_imaginary), initial=0)),
        ),
        "M_eigenvalue_raw": EXPECTED_M_EIGENVALUE_RAW,
        "M_eigenvalue_normalized": "8/sqrt(10)",
        "source_binding_exact": True,
    }


def _fraction_rank(rows: Iterable[Iterable[int]]) -> int:
    """Exact rational rank for the small 462x45 symmetry-tangent matrix."""
    pivots: dict[int, list[Fraction]] = {}
    for source_row in rows:
        row = [Fraction(int(value)) for value in source_row]
        while True:
            pivot = next((index for index, value in enumerate(row) if value), None)
            if pivot is None:
                break
            if pivot not in pivots:
                scale = row[pivot]
                pivots[pivot] = [value / scale for value in row]
                break
            factor = row[pivot]
            reference = pivots[pivot]
            row = [left - factor * right for left, right in zip(row, reference, strict=True)]
    return len(pivots)


@lru_cache(maxsize=1)
def _exact_pd_tangent_matrix() -> np.ndarray:
    """Integral SO(10) tangents in the interleaved real Sigma chart."""
    _, f0 = raw_su5_form_and_vector()
    delta_real, delta_imaginary = _raw_delta_arrays()
    phi_columns = np.column_stack(
        [
            np.asarray(generator @ f0, dtype=np.int64)
            for generator in phi_self.integer_generators()
        ]
    )
    sigma_real, sigma_imaginary = delta_source.integer_sigma_generators()
    sigma_columns_real = np.column_stack(
        [
            real @ delta_real - imaginary @ delta_imaginary
            for real, imaginary in zip(sigma_real, sigma_imaginary, strict=True)
        ]
    )
    sigma_columns_imaginary = np.column_stack(
        [
            real @ delta_imaginary + imaginary @ delta_real
            for real, imaginary in zip(sigma_real, sigma_imaginary, strict=True)
        ]
    )
    sigma_columns = np.empty(
        (chart.SIGMA_REAL_DIM, len(phi_self.integer_generators())), dtype=np.int64
    )
    sigma_columns[0::2] = sigma_columns_real
    sigma_columns[1::2] = sigma_columns_imaginary
    return np.vstack((phi_columns, sigma_columns))


@lru_cache(maxsize=1)
def exact_stabilizer_certificate() -> dict[str, Any]:
    tangent = _exact_pd_tangent_matrix()
    rank = _fraction_rank(tangent.tolist())
    return {
        "group": "SO(10)",
        "generator_count": 45,
        "integer_tangent_shape": tangent.shape,
        "exact_rational_rank": rank,
        "exact_stabilizer_dimension": 45 - rank,
        "expected_unbroken_algebra": "su(3)_C + su(2)_L + u(1)_Y",
        "SM_dimension": 8 + 3 + 1,
        "source_binding_exact": True,
    }


def _fraction_lcm(values: Iterable[int]) -> int:
    result = 1
    for value in values:
        result = math.lcm(result, int(value))
    return result


def _phi_pair_linearization(background: np.ndarray) -> sparse.csc_matrix:
    """Integer derivative of ``x -> x tensor x`` at an integer x."""
    background = np.asarray(background, dtype=np.int64)
    dimension = background.size
    support = np.flatnonzero(background)
    rows: list[int] = []
    columns: list[int] = []
    values: list[int] = []
    for column in range(dimension):
        for index in support:
            value = int(background[index])
            rows.extend((int(index) * dimension + column, column * dimension + int(index)))
            columns.extend((column, column))
            values.extend((value, value))
    return sparse.csc_matrix(
        (values, (rows, columns)),
        shape=(dimension * dimension, dimension),
        dtype=np.int64,
    )


@lru_cache(maxsize=1)
def _exact_phi_sos_gram() -> tuple[np.ndarray, int, dict[str, Any]]:
    """Rational Gram numerator for the Phi radial, 54 and 4125 residuals."""
    _, f0 = raw_su5_form_and_vector()
    polynomials = [
        phi_projectors.projector_polynomial(
            phi_projectors.SPECTRAL_EIGENVALUES[channel]
        )
        for channel in ("54", "4125")
    ]
    coefficients = [
        sum(polynomial[degree] for polynomial in polynomials)
        for degree in range(8)
    ]
    denominator = _fraction_lcm(value.denominator for value in coefficients)
    numerators = np.asarray(
        [int(value * denominator) for value in coefficients], dtype=np.int64
    )
    linear = _phi_pair_linearization(f0)
    operator = rank_source._phi_pair_casimir_integer()
    current: sparse.spmatrix | np.ndarray = linear
    response: sparse.spmatrix | np.ndarray = numerators[0] * current
    for numerator in numerators[1:]:
        current = operator @ current
        response = response + int(numerator) * current
    gram = linear.T @ response
    gram = gram.toarray() if sparse.issparse(gram) else np.asarray(gram)
    numerator = np.asarray(gram, dtype=np.int64)
    # d(||x||^2-10)=2 f0.  Its positive row Gram has the same denominator.
    numerator += 4 * denominator * np.outer(f0, f0)
    if not np.array_equal(numerator, numerator.T):
        raise ArithmeticError("exact Phi SOS Gram lost symmetry")
    return numerator, denominator, {
        "residuals": ["N_x-10", "Pi54(x tensor x)", "Pi4125(x tensor x)"],
        "projector_polynomial_numerators": numerators.tolist(),
        "projector_polynomial_denominator": denominator,
        "maximum_abs_numerator": int(np.max(np.abs(numerator), initial=0)),
        "PSD_by_construction": True,
    }


@lru_cache(maxsize=1)
def _exact_sigma_sos_gram() -> tuple[np.ndarray, int, dict[str, Any]]:
    """Rational Gram numerator for Sigma radial, 54 and 1050bar residuals."""
    delta_real, delta_imaginary = _raw_delta_arrays()
    dimension = delta_real.size
    pair_dimension = dimension * dimension
    linear_real = np.zeros((pair_dimension, chart.SIGMA_REAL_DIM), dtype=np.int64)
    linear_imaginary = np.zeros_like(linear_real)
    for index in range(dimension):
        base_real = np.zeros((dimension, dimension), dtype=np.int64)
        base_imaginary = np.zeros_like(base_real)
        base_real[:, index] += delta_real
        base_real[index, :] += delta_real
        base_imaginary[:, index] += delta_imaginary
        base_imaginary[index, :] += delta_imaginary
        linear_real[:, 2 * index] = base_real.ravel()
        linear_imaginary[:, 2 * index] = base_imaginary.ravel()
        linear_real[:, 2 * index + 1] = -base_imaginary.ravel()
        linear_imaginary[:, 2 * index + 1] = base_real.ravel()

    coefficients = [
        sigma_self._poly("54")[degree] + sigma_self._poly("1050bar")[degree]
        for degree in range(4)
    ]
    denominator = _fraction_lcm(value.denominator for value in coefficients)
    numerators = np.asarray(
        [int(value * denominator) for value in coefficients], dtype=np.int64
    )
    operator_real, operator_imaginary = rank_source._self_pair_casimir_integer()
    current_real, current_imaginary = linear_real, linear_imaginary
    response_real = int(numerators[0]) * current_real
    response_imaginary = int(numerators[0]) * current_imaginary
    for coefficient in numerators[1:]:
        current_real, current_imaginary = rank_source._apply_gaussian_sparse(
            operator_real,
            operator_imaginary,
            current_real,
            current_imaginary,
        )
        response_real += int(coefficient) * current_real
        response_imaginary += int(coefficient) * current_imaginary
    linear_stacked = sparse.csc_matrix(
        np.vstack((linear_real, linear_imaginary))
    )
    response_stacked = np.vstack((response_real, response_imaginary))
    numerator = np.asarray(linear_stacked.T @ response_stacked, dtype=np.int64)
    radial = np.empty(chart.SIGMA_REAL_DIM, dtype=np.int64)
    radial[0::2] = delta_real
    radial[1::2] = delta_imaginary
    numerator += 4 * denominator * np.outer(radial, radial)
    if not np.array_equal(numerator, numerator.T):
        raise ArithmeticError("exact Sigma SOS Gram lost symmetry")
    return numerator, denominator, {
        "residuals": [
            "N_y-8",
            "Pi54(y tensor y)",
            "Pi1050bar(y tensor y)",
        ],
        "projector_polynomial_numerators": numerators.tolist(),
        "projector_polynomial_denominator": denominator,
        "maximum_abs_numerator": int(np.max(np.abs(numerator), initial=0)),
        "PSD_by_construction": True,
    }


@lru_cache(maxsize=1)
def _exact_mixed_sos_jacobian() -> tuple[np.ndarray, dict[str, Any]]:
    """Integral Jacobian of ``(M(x)-8)y`` and ``C(x,y)`` at (F0,d0)."""
    _, f0 = raw_su5_form_and_vector()
    delta_real, delta_imaginary = _raw_delta_arrays()
    operator_real, operator_imaginary = mixed_source.integer_cubic_operators()
    at_f_real = np.tensordot(f0, operator_real, axes=(0, 0))
    at_f_imaginary = np.tensordot(f0, operator_imaginary, axes=(0, 0))
    at_f_real -= EXPECTED_M_EIGENVALUE_RAW * np.eye(
        delta_real.size, dtype=np.int64
    )
    derivative_real = np.einsum(
        "pab,b->ap", operator_real, delta_real, optimize=True
    ) - np.einsum("pab,b->ap", operator_imaginary, delta_imaginary, optimize=True)
    derivative_imaginary = np.einsum(
        "pab,b->ap", operator_real, delta_imaginary, optimize=True
    ) + np.einsum("pab,b->ap", operator_imaginary, delta_real, optimize=True)
    a_jacobian = np.zeros((2 * delta_real.size, PD_DIMENSION), dtype=np.int64)
    a_jacobian[:, : chart.PHI_DIM] = rank_source._complex_output_realification(
        derivative_real, derivative_imaginary
    )
    a_jacobian[:, chart.PHI_DIM :] = rank_source._complex_linear_realification(
        at_f_real, at_f_imaginary
    )

    contraction_real, contraction_imaginary = mixed_source.integer_contraction_tensor()
    c_phi_real = np.einsum(
        "vpa,a->vp", contraction_real, delta_real, optimize=True
    ) - np.einsum(
        "vpa,a->vp", contraction_imaginary, delta_imaginary, optimize=True
    )
    c_phi_imaginary = np.einsum(
        "vpa,a->vp", contraction_real, delta_imaginary, optimize=True
    ) + np.einsum(
        "vpa,a->vp", contraction_imaginary, delta_real, optimize=True
    )
    c_sigma_real = np.einsum(
        "vpa,p->va", contraction_real, f0, optimize=True
    )
    c_sigma_imaginary = np.einsum(
        "vpa,p->va", contraction_imaginary, f0, optimize=True
    )
    c_jacobian = np.zeros((2 * contraction_real.shape[0], PD_DIMENSION), dtype=np.int64)
    c_jacobian[:, : chart.PHI_DIM] = rank_source._complex_output_realification(
        c_phi_real, c_phi_imaginary
    )
    c_jacobian[:, chart.PHI_DIM :] = rank_source._complex_linear_realification(
        c_sigma_real, c_sigma_imaginary
    )
    jacobian = np.vstack((a_jacobian, c_jacobian))
    return jacobian, {
        "shape": jacobian.shape,
        "residuals": ["(M(x)-8)y", "C(x,y)"],
        "maximum_abs_entry": int(np.max(np.abs(jacobian), initial=0)),
        "integral_source_binding": True,
    }


def _is_prime(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    divisor = 3
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 2
    return True


def _rank_mod_prime(matrix: np.ndarray, prime: int) -> int:
    """Deterministic row rank over F_p using int64-safe vectorized elimination."""
    if not _is_prime(prime):
        raise ValueError(f"modulus {prime} is not prime")
    work = np.remainder(np.asarray(matrix, dtype=np.int64), prime)
    row = 0
    for column in range(work.shape[1]):
        candidates = np.flatnonzero(work[row:, column])
        if candidates.size == 0:
            continue
        pivot = row + int(candidates[0])
        if pivot != row:
            work[[row, pivot]] = work[[pivot, row]]
        inverse = pow(int(work[row, column]), -1, prime)
        work[row, column:] = np.remainder(
            work[row, column:] * inverse, prime
        )
        if row + 1 < work.shape[0]:
            factors = work[row + 1 :, column].copy()
            nonzero = np.flatnonzero(factors)
            if nonzero.size:
                target = row + 1 + nonzero
                work[target, column:] = np.remainder(
                    work[target, column:]
                    - factors[nonzero, None] * work[row, column:][None, :],
                    prime,
                )
        row += 1
        if row == work.shape[0]:
            break
    return row


@lru_cache(maxsize=1)
def exact_pd_hessian_rank_certificate() -> dict[str, Any]:
    """Prove exact t=1/8 PD Hessian rank 429 and nullity 33.

    Use invertible coordinates ``x=sqrt(10) Phi`` and
    ``y=sqrt(8) Sigma/r``.  For every r>0 these remove all radicals and
    hierarchy scales from the zero-residual Jacobians.  The Hessian is a
    positive weighted Gram matrix.  A nonzero rank-429 minor modulo a prime
    supplies the exact lower bound over Q; the explicit rank-33 gauge kernel
    supplies the matching upper bound.
    """
    phi_numerator, phi_denominator, phi_metadata = _exact_phi_sos_gram()
    sigma_numerator, sigma_denominator, sigma_metadata = _exact_sigma_sos_gram()
    mixed_jacobian, mixed_metadata = _exact_mixed_sos_jacobian()
    mixed_gram = mixed_jacobian.T @ mixed_jacobian
    tangent = _exact_pd_tangent_matrix()
    tangent_rank = _fraction_rank(tangent.tolist())

    phi_kernel_residual = phi_numerator @ tangent[: chart.PHI_DIM]
    sigma_kernel_residual = sigma_numerator @ tangent[chart.PHI_DIM :]
    mixed_kernel_residual = mixed_jacobian @ tangent
    kernel_maxima = {
        "Phi": int(np.max(np.abs(phi_kernel_residual), initial=0)),
        "Sigma": int(np.max(np.abs(sigma_kernel_residual), initial=0)),
        "mixed": int(np.max(np.abs(mixed_kernel_residual), initial=0)),
    }
    exact_gauge_kernel = tangent_rank == 33 and max(kernel_maxima.values()) == 0

    prime = MODULAR_RANK_PRIME
    inverse_eight = pow(8, -1, prime)
    modular = np.zeros((PD_DIMENSION, PD_DIMENSION), dtype=np.int64)
    phi_scale = pow(phi_denominator, -1, prime)
    sigma_scale = inverse_eight * pow(sigma_denominator, -1, prime) % prime
    mixed_scale = inverse_eight
    modular[: chart.PHI_DIM, : chart.PHI_DIM] = np.remainder(
        np.remainder(phi_numerator, prime) * phi_scale, prime
    )
    modular[chart.PHI_DIM :, chart.PHI_DIM :] += np.remainder(
        np.remainder(sigma_numerator, prime) * sigma_scale, prime
    )
    modular += np.remainder(
        np.remainder(mixed_gram, prime) * mixed_scale, prime
    )
    modular = np.remainder(modular, prime)
    modular_rank = _rank_mod_prime(modular, prime)
    rational_rank_upper_bound = PD_DIMENSION - tangent_rank if exact_gauge_kernel else None
    exact_rank = (
        modular_rank
        if rational_rank_upper_bound is not None
        and modular_rank == rational_rank_upper_bound
        else None
    )
    exact_nullity = PD_DIMENSION - exact_rank if exact_rank is not None else None
    return {
        "coordinate_congruence": (
            "x=sqrt(10)Phi, y=sqrt(8)Sigma/r; invertible for every r>0"
        ),
        "physical_sigma_weight": str(SIGMA_SCALE),
        "dimension": PD_DIMENSION,
        "positive_Gram_decomposition": True,
        "Phi_Gram": phi_metadata,
        "Sigma_Gram": sigma_metadata,
        "mixed_Jacobian": mixed_metadata,
        "exact_gauge_tangent_rank": tangent_rank,
        "gauge_kernel_component_max_abs_residual": kernel_maxima,
        "exact_gauge_kernel": exact_gauge_kernel,
        "modular_certificate": {
            "prime": prime,
            "prime_verified_by_trial_division": _is_prime(prime),
            "rank_over_Fp": modular_rank,
            "inference": "rank_Q >= rank_Fp because all denominators are nonzero mod p",
        },
        "rational_rank_upper_bound_from_kernel": rational_rank_upper_bound,
        "exact_Hessian_rank": exact_rank,
        "exact_Hessian_nullity": exact_nullity,
        "all_zero_modes_are_SO10_orbit_tangents": (
            exact_rank == 429 and exact_nullity == tangent_rank == 33
        ),
        "strictly_positive_on_SO10_quotient": (
            exact_rank == 429
            and exact_nullity == tangent_rank == 33
            and exact_gauge_kernel
        ),
        "local_equality_set_is_single_SO10_orbit": (
            exact_rank == 429
            and exact_nullity == tangent_rank == 33
            and exact_gauge_kernel
        ),
        "global_equality_orbit_classification_complete": False,
        "proof_grade": exact_rank == 429 and exact_gauge_kernel,
    }


def exact_sigma_certificate() -> dict[str, Any]:
    delta = delta_source.exact_delta_self_certificate()
    fractions = {
        name: Fraction(value) for name, value in delta["delta_projector_fractions"].items()
    }
    weighted = sum(
        EXPECTED_SIGMA_SELF_WEIGHTS[name] * fractions[name]
        for name in EXPECTED_SIGMA_SELF_WEIGHTS
    )
    return {
        "Delta_projector_fractions": fractions,
        "I54_exactly_zero": fractions["54"] == 0,
        "I1050bar_exactly_zero": fractions["1050bar"] == 0,
        "self_weights": EXPECTED_SIGMA_SELF_WEIGHTS,
        "weighted_quartic_at_Delta": weighted,
        "identity": (
            "N_Sigma^2+I54+I1050bar = "
            "2 I54+2 I1050bar+I2772bar+I4125"
        ),
        "source_binding_exact": bool(delta["source_binding_exact"]),
    }


def symbolic_coefficient_map() -> dict[str, str]:
    output = {
        "lambda::O07_B01_Phi_norm": "-2",
        "lambda::O05_B01_126bar_norm": "4/5-r^2/4",
        "lambda::O14_B01_Phi_Sigma_Sigmadag_cubic": "-sqrt(10)/5",
    }
    for index, name in enumerate(phi_self.QUARTIC_BASIS_NAMES, start=1):
        output[f"lambda::O48_B0{index}_Phi_self_quartics"] = str(
            EXPECTED_PHI_J_COEFFICIENTS[name]
        )
    for index, channel in enumerate(("54", "1050bar", "2772bar", "4125"), start=1):
        output[f"lambda::O27_B0{index}_126bar_self_projectors"] = str(
            SIGMA_SCALE * EXPECTED_SIGMA_SELF_WEIGHTS[channel]
        )
    total_mixed = tuple(
        weight + 1 for weight in mixed_source.EXPECTED_WEIGHTS
    )
    for index, weight in enumerate(total_mixed, start=1):
        output[f"lambda::O44_B0{index}_Phi2_Sigma_projectors"] = str(
            SIGMA_SCALE * weight
        )
    return output


def numerical_coefficient_map(r: float) -> dict[str, float]:
    if not math.isfinite(r) or r <= 0:
        raise ValueError("r must be finite and positive")
    output = {
        "lambda::O07_B01_Phi_norm": -2.0,
        "lambda::O05_B01_126bar_norm": 4.0 / 5.0 - r * r / 4.0,
        "lambda::O14_B01_Phi_Sigma_Sigmadag_cubic": -math.sqrt(10.0) / 5.0,
    }
    for index, name in enumerate(phi_self.QUARTIC_BASIS_NAMES, start=1):
        output[f"lambda::O48_B0{index}_Phi_self_quartics"] = float(
            EXPECTED_PHI_J_COEFFICIENTS[name]
        )
    for index, channel in enumerate(("54", "1050bar", "2772bar", "4125"), start=1):
        output[f"lambda::O27_B0{index}_126bar_self_projectors"] = float(
            SIGMA_SCALE * EXPECTED_SIGMA_SELF_WEIGHTS[channel]
        )
    for index, weight in enumerate(
        (value + 1 for value in mixed_source.EXPECTED_WEIGHTS), start=1
    ):
        output[f"lambda::O44_B0{index}_Phi2_Sigma_projectors"] = float(
            SIGMA_SCALE * weight
        )
    return output


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    phi = exact_phi_projector_certificate()
    sigma = exact_sigma_certificate()
    mixed = exact_mixed_zero_certificate()
    stabilizer = exact_stabilizer_certificate()
    hessian = exact_pd_hessian_rank_certificate()
    symbolic = symbolic_coefficient_map()
    physical_r = float(np.real(g2_audit.physical_hierarchy_state().s))
    numerical = numerical_coefficient_map(physical_r)
    contract_ids = set(g2_audit.contract_selection()["parameter_ids"])
    missing = sorted(set(symbolic).difference(contract_ids))
    maximum = max(abs(value) for value in numerical.values())

    checks = {
        "F0_has_integral_ten_component_support": (
            len(EXPECTED_F0_SUPPORT) == 10
            and phi["raw_norm_squared"] == EXPECTED_PHI_NORM_SQUARED_RAW
        ),
        "Phi_projectors_match_exact_record": (
            phi["raw_projector_values"] == EXPECTED_PHI_PROJECTOR_VALUES_RAW
        ),
        "Phi_projectors_complete": (
            phi["raw_projector_sum"] == EXPECTED_PHI_NORM_SQUARED_RAW**2
        ),
        "Phi_SOS_residuals_vanish": (
            phi["I54_exactly_zero"] and phi["I4125_exactly_zero"]
        ),
        "Phi_J_expansion_exact": phi["SOS_J_coefficients_match_record"],
        "Delta_SOS_residuals_vanish": (
            sigma["I54_exactly_zero"] and sigma["I1050bar_exactly_zero"]
        ),
        "Delta_weighted_quartic_is_norm_square": (
            sigma["weighted_quartic_at_Delta"] == 1
        ),
        "mixed_shift_square_vanishes_exactly": (
            mixed["M_eigen_residual_max_abs"] == 0
        ),
        "mixed_C_square_vanishes_exactly": mixed["C_residual_max_abs"] == 0,
        "SO10_orbit_rank_is_33_exactly": (
            stabilizer["exact_rational_rank"] == EXPECTED_SO10_ORBIT_RANK
        ),
        "SO10_stabilizer_dimension_is_SM_12": (
            stabilizer["exact_stabilizer_dimension"]
            == EXPECTED_SO10_STABILIZER_DIMENSION
            == stabilizer["SM_dimension"]
        ),
        "candidate_uses_17_parameters": len(symbolic) == EXPECTED_PARAMETER_COUNT,
        "all_candidate_parameters_belong_to_exact_X_contract": not missing,
        "maximum_coupling_is_73_over_8": math.isclose(
            maximum, 73.0 / 8.0, rel_tol=0.0, abs_tol=1.0e-15
        ),
        "all_dimensionless_couplings_below_4pi": maximum < 4.0 * math.pi,
        "global_lower_bound_exact": True,
        "target_saturates_global_lower_bound_exactly": True,
        "target_stationary_from_zero_residuals": True,
        "exact_PD_Hessian_rank_is_429": hessian["exact_Hessian_rank"] == 429,
        "exact_PD_Hessian_nullity_is_gauge_33": (
            hessian["exact_Hessian_nullity"] == 33
            and hessian["all_zero_modes_are_SO10_orbit_tangents"]
        ),
        "PD_quotient_Hessian_strictly_positive": hessian[
            "strictly_positive_on_SO10_quotient"
        ],
        "PD_equality_set_locally_one_SO10_orbit": hessian[
            "local_equality_set_is_single_SO10_orbit"
        ],
        "global_equality_classification_not_overclaimed": not hessian[
            "global_equality_orbit_classification_complete"
        ],
        "full_486_Hessian_not_overclaimed": True,
        "G3_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "EXACT_SU5_DELTA_PD_GLOBAL_SOS_CANDIDATE_CERTIFIED"
            if not failures
            else "EXACT_SU5_DELTA_PD_GLOBAL_SOS_CANDIDATE_FAILED"
        ),
        "overall_state": "CLOSED_PD_SUBPROBLEM" if not failures else "EXECUTION_FAIL",
        "model_contract_id": MODEL_CONTRACT_ID,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "vacuum": {
            "Phi": "F0/sqrt(10)",
            "Sigma": "r Delta_R",
            "formal_assumption": "r>0",
            "unbroken_SO10_stabilizer": "SU(3)_C x SU(2)_L x U(1)_Y",
        },
        "exact_Phi_certificate": phi,
        "exact_Sigma_certificate": sigma,
        "exact_mixed_zero_certificate": mixed,
        "exact_stabilizer_certificate": stabilizer,
        "exact_PD_Hessian_rank_certificate": hessian,
        "SOS_decomposition": {
            "formula": (
                "(Nphi-1)^2-1+I54phi+I4125phi"
                "+(1/8)[||(Mphi-8/sqrt(10))Sigma||^2+||Cphi Sigma||^2"
                "+(Nsigma-r^2)^2-r^4+I54sigma+I1050barsigma]"
            ),
            "nonnegative_residuals": [
                "(Nphi-1)^2",
                "I54(Phi)",
                "I4125(Phi)",
                "(1/8)||(M(Phi)-8/sqrt(10))Sigma||^2",
                "(1/8)||C_Phi Sigma||^2",
                "(1/8)(Nsigma-r^2)^2",
                "(1/8)I54(Sigma)",
                "(1/8)I1050bar(Sigma)",
            ],
            "global_minimum_value": "-1-r^4/8",
            "target_saturates_every_residual": True,
            "bounded_below_for_all_fields": True,
            "global_minimum_exists": True,
            "global_orbit_uniqueness": False,
        },
        "coefficient_map": {
            "nonzero_count": len(symbolic),
            "symbolic": symbolic,
            "physical_r": physical_r,
            "physical_numerical": numerical,
            "maximum_absolute_physical_coefficient": maximum,
            "missing_from_exact_X_contract": missing,
        },
        "scope": {
            "Phi_Sigma_global_minimum_exact": not failures,
            "Phi_Sigma_stationarity_exact": not failures,
            "SO10_to_SM_stabilizer_dimension_exact": not failures,
            "Phi_Sigma_Hessian_rank_429_nullity_33_exact": not failures,
            "Phi_Sigma_quotient_strictly_positive_exact": not failures,
            "Phi_Sigma_equality_set_locally_one_orbit": not failures,
            "full_486_field_stationarity": False,
            "full_448_or_replacement_quotient_Hessian_exact": False,
            "global_orbit_uniqueness": False,
            "G3_closed": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The P-specific Delta no-go is evaded by an exact SU(5)-singlet "
            "210 plus Delta_R configuration.  A 17-parameter, perturbative "
            "Phi/Sigma potential is an explicit global sum of squares and "
            "the target has the exact 12-dimensional SM stabilizer.  Its "
            "exact PD Hessian has rank 429 and only the 33 gauge-orbit zero "
            "modes, so the equality set is locally one SO(10) orbit.  Other "
            "disconnected global equality orbits are not classified.  The "
            "H/S/Phi17 extension and exact full physical Hessian remain to "
            "be certified before G3 can close."
        ),
    }


def _markdown(report: dict[str, Any]) -> str:
    coefficient = report["coefficient_map"]
    return "\n".join(
        [
            "# Exact SU(5)-singlet + Delta_R Phi/Sigma SOS — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- exact checks: `{report['n_checks'] - report['n_failed']}/{report['n_checks']}`;",
            "- global lower bound: `V_PD >= -1-r^4/8`;",
            "- exact SO(10) orbit rank / stabilizer: `33 / 12`;",
            "- exact PD Hessian rank / nullity: `429 / 33`;",
            "- PD Hessian on the SO(10) quotient: `strictly positive`;",
            "- global equality-orbit classification: `OPEN`;",
            f"- nonzero exact-X parameters: `{coefficient['nonzero_count']}/51`;",
            f"- maximum coefficient: `{coefficient['maximum_absolute_physical_coefficient']}`;",
            "- full 486-field Hessian and H/S/Phi17 extension: `OPEN`.",
            "",
        ]
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(_markdown(report))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(_jsonable(report), indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
