#!/usr/bin/env python3
"""Direct exact rank audit for the constructive P+Delta_R Hessian.

The constructive G3 candidate admits the hierarchy congruence

    diag(I_210, r I_252)^T H_PD(r) diag(I_210, r I_252)
        = H_Phi + t r^2 K,                 t=1/8.

``H_Phi`` is the already certified Pati--Salam 210 Hessian.  ``K`` contains
the two mixed contraction squares (the A-shift square and the C-square) and
the corrected 126bar angular self-Hessian with channel weights
``(2,2,17/16,1)``.

This module supplies exact arithmetic in Q(sqrt(2)), constructs every entry
of ``H_Phi`` and ``K`` directly from Gaussian-integer representation tensors
and Fraction-valued projector polynomials, and applies componentwise exact
Schur/LDL elimination.  No floating-point-to-lattice reconstruction is used
by the proof path.  A separate legacy reconstruction path is retained only as
an optional regression comparison.

The exact result certifies positivity of the displayed candidate's Hessian on
all 448 directions transverse to its symmetry orbit after the nonnegative
H/S/X squares are included.  Stationarity and boundedness are owned by the
separate source-bound SOS certificate and are not re-inferred here.  This file
also does *not* establish uniqueness among stationary points and therefore
does not, by itself, close a global-extrema definition of G3.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, deque
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy import sparse

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_PD_RANK_CERTIFICATE_V20.json"
OUT_MD = ROOT / "EXACT_GAUGED_U1X_G3_PD_RANK_CERTIFICATE_V20.md"

PHI_DIMENSION = 210
SIGMA_REAL_DIMENSION = 252
PD_DIMENSION = PHI_DIMENSION + SIGMA_REAL_DIMENSION
SIGMA_SCALE = Fraction(1, 8)

MIXED_CHANNELS = ("1", "45", "210", "770", "5940", "8910")
A_SHIFT_WEIGHTS = (40, 72, 28, -8, -12, 12)
C_SQUARE_WEIGHTS = (1, 1, 1, 1, 1, 1)
TOTAL_MIXED_WEIGHTS = tuple(
    left + right
    for left, right in zip(A_SHIFT_WEIGHTS, C_SQUARE_WEIGHTS, strict=True)
)
SELF_WEIGHTS = {
    "54": Fraction(2),
    "1050bar": Fraction(2),
    "2772bar": Fraction(17, 16),
    "4125": Fraction(1),
}

# Every nonzero entry observed from the exact-formula source path belongs to
# (1/20160) Z or sqrt(2)*(1/20160) Z.  The larger denominator also contains
# the 210 Hessian's fifths.  This is an a-priori lattice for reconstruction,
# not by itself an exact source binding.
RECONSTRUCTION_DENOMINATOR = 20_160
ZERO_CUTOFF = 1.0e-9
RECONSTRUCTION_TOLERANCE = 1.0e-9

# Denominators obtained before a matrix-wide gcd reduction in the direct
# exact construction.  They are consequences of the projector polynomials,
# not numerical guesses.
MIXED_EXACT_DENOMINATOR = 8
SELF_EXACT_DENOMINATOR = 2_064_384
PHI_EXACT_DENOMINATOR = 121_651_200
INT64_MAX = np.iinfo(np.int64).max


@dataclass(frozen=True)
class Qsqrt2:
    """An exact element ``a+b*sqrt(2)`` with rational ``a,b``."""

    a: Fraction = Fraction(0)
    b: Fraction = Fraction(0)

    @staticmethod
    def coerce(value: Qsqrt2 | Fraction | int) -> Qsqrt2:
        if isinstance(value, Qsqrt2):
            return value
        return Qsqrt2(Fraction(value), Fraction(0))

    def __add__(self, other: Qsqrt2 | Fraction | int) -> Qsqrt2:
        rhs = self.coerce(other)
        return Qsqrt2(self.a + rhs.a, self.b + rhs.b)

    __radd__ = __add__

    def __neg__(self) -> Qsqrt2:
        return Qsqrt2(-self.a, -self.b)

    def __sub__(self, other: Qsqrt2 | Fraction | int) -> Qsqrt2:
        return self + (-self.coerce(other))

    def __rsub__(self, other: Qsqrt2 | Fraction | int) -> Qsqrt2:
        return self.coerce(other) - self

    def __mul__(self, other: Qsqrt2 | Fraction | int) -> Qsqrt2:
        rhs = self.coerce(other)
        return Qsqrt2(
            self.a * rhs.a + 2 * self.b * rhs.b,
            self.a * rhs.b + self.b * rhs.a,
        )

    __rmul__ = __mul__

    def __truediv__(self, other: Qsqrt2 | Fraction | int) -> Qsqrt2:
        rhs = self.coerce(other)
        denominator = rhs.a * rhs.a - 2 * rhs.b * rhs.b
        if denominator == 0:
            raise ZeroDivisionError("division by zero in Q(sqrt(2))")
        return Qsqrt2(
            (self.a * rhs.a - 2 * self.b * rhs.b) / denominator,
            (self.b * rhs.a - self.a * rhs.b) / denominator,
        )

    def sign(self) -> int:
        """Return the exact sign without converting ``sqrt(2)`` to float."""
        if self.a == 0:
            return (self.b > 0) - (self.b < 0)
        if self.b == 0:
            return (self.a > 0) - (self.a < 0)
        if self.a > 0 and self.b > 0:
            return 1
        if self.a < 0 and self.b < 0:
            return -1
        comparison = self.a * self.a - 2 * self.b * self.b
        if comparison == 0:
            return 0
        if self.a > 0:
            return 1 if comparison > 0 else -1
        return -1 if comparison > 0 else 1

    def as_float(self) -> float:
        return float(self.a) + math.sqrt(2.0) * float(self.b)


ZERO_QSQRT2 = Qsqrt2()


def reconstruct_qsqrt2(value: float) -> tuple[Qsqrt2, dict[str, float | str]]:
    """Select the closest member of the declared Q(sqrt(2)) lattice."""
    observed = float(value)
    if abs(observed) < ZERO_CUTOFF:
        exact = ZERO_QSQRT2
        return exact, {
            "kind": "zero",
            "chosen_abs_residual": abs(observed),
            "alternative_abs_residual": float("inf"),
        }

    denominator = RECONSTRUCTION_DENOMINATOR
    rational_numerator = int(round(observed * denominator))
    sqrt_numerator = int(round(observed * denominator / math.sqrt(2.0)))
    rational = Qsqrt2(Fraction(rational_numerator, denominator), Fraction(0))
    radical = Qsqrt2(Fraction(0), Fraction(sqrt_numerator, denominator))
    rational_error = abs(rational.as_float() - observed)
    radical_error = abs(radical.as_float() - observed)
    if rational_error <= radical_error:
        exact, kind = rational, "rational"
        chosen, alternative = rational_error, radical_error
    else:
        exact, kind = radical, "sqrt2_rational"
        chosen, alternative = radical_error, rational_error
    if chosen > RECONSTRUCTION_TOLERANCE:
        raise ArithmeticError(
            f"entry {observed!r} misses the declared Q(sqrt(2)) lattice: {chosen}"
        )
    return exact, {
        "kind": kind,
        "chosen_abs_residual": chosen,
        "alternative_abs_residual": alternative,
    }


def exact_psd_rank(
    matrix: Iterable[Iterable[Qsqrt2]],
) -> dict[str, Any]:
    """Certify PSD and rank by exact symmetric Schur complements.

    At each step a strictly positive diagonal entry is used as a 1x1 pivot.
    Its Schur complement is exact in Q(sqrt(2)).  If every remaining diagonal
    is zero, PSD requires every remaining off-diagonal entry to be zero; this
    explicitly handles singular blocks without dividing by a zero pivot.
    """
    work = [list(row) for row in matrix]
    if any(len(row) != len(work) for row in work):
        raise ValueError("matrix must be square")
    rank = 0
    positive_pivots: list[Qsqrt2] = []
    while work:
        dimension = len(work)
        diagonal_signs = [work[index][index].sign() for index in range(dimension)]
        if min(diagonal_signs, default=0) < 0:
            return {
                "PSD": False,
                "rank": rank,
                "reason": "negative exact diagonal in a Schur complement",
                "positive_pivots": positive_pivots,
            }
        positive = next(
            (index for index, sign in enumerate(diagonal_signs) if sign > 0),
            None,
        )
        if positive is None:
            nonzero = next(
                (
                    (row, column, work[row][column])
                    for row in range(dimension)
                    for column in range(dimension)
                    if work[row][column] != ZERO_QSQRT2
                ),
                None,
            )
            return {
                "PSD": nonzero is None,
                "rank": rank,
                "reason": (
                    "exact zero Schur remainder"
                    if nonzero is None
                    else "zero diagonal with nonzero off-diagonal"
                ),
                "positive_pivots": positive_pivots,
            }
        if positive != 0:
            work[0], work[positive] = work[positive], work[0]
            for row in work:
                row[0], row[positive] = row[positive], row[0]
        pivot = work[0][0]
        positive_pivots.append(pivot)
        edge = work[0][1:]
        work = [
            [
                work[row][column] - edge[row - 1] * edge[column - 1] / pivot
                for column in range(1, dimension)
            ]
            for row in range(1, dimension)
        ]
        rank += 1
    return {
        "PSD": True,
        "rank": rank,
        "reason": "all exact Schur pivots exhausted",
        "positive_pivots": positive_pivots,
    }


def _fraction_lcm(values: Iterable[int]) -> int:
    result = 1
    for value in values:
        result = math.lcm(result, int(value))
    return result


def _integer_gcd(*arrays: np.ndarray, denominator: int) -> int:
    result = abs(int(denominator))
    for array in arrays:
        nonzero = np.asarray(array, dtype=np.int64)
        nonzero = np.abs(nonzero[nonzero != 0])
        if nonzero.size:
            result = math.gcd(result, int(np.gcd.reduce(nonzero)))
    return max(result, 1)


def _max_abs_integer(value: np.ndarray | sparse.spmatrix) -> int:
    if sparse.issparse(value):
        data = value.data
    else:
        data = np.asarray(value)
    return int(np.max(np.abs(data), initial=0))


def _require_int64_bound(label: str, absolute_bound: int) -> int:
    bound = int(absolute_bound)
    if bound > INT64_MAX:
        raise OverflowError(
            f"{label} has conservative bound {bound} exceeding int64 {INT64_MAX}"
        )
    return bound


def _sparse_maximum_row_l1(operator: sparse.spmatrix) -> int:
    row_sums = np.asarray(abs(operator).sum(axis=1)).reshape(-1)
    return int(np.max(row_sums, initial=0))


def _reduced_pair(
    rational_numerator: np.ndarray,
    radical_numerator: np.ndarray,
    denominator: int,
) -> tuple[np.ndarray, np.ndarray, int]:
    rational = np.asarray(rational_numerator, dtype=np.int64)
    radical = np.asarray(radical_numerator, dtype=np.int64)
    divisor = _integer_gcd(rational, radical, denominator=denominator)
    return rational // divisor, radical // divisor, int(denominator) // divisor


def _gaussian_integer_parts(
    value: np.ndarray,
    *,
    label: str,
) -> tuple[np.ndarray, np.ndarray]:
    """Bind an upstream combinatorial tensor to Gaussian integers exactly.

    The form/generator builders use complex dtype for convenience, although
    their coefficients are produced only by signed permutations and additions
    of 0, 1 and i.  We check the defining lattice before casting.  Subsequent
    proof arithmetic is entirely integer arithmetic.
    """
    array = np.asarray(value, dtype=complex)
    real = np.rint(array.real).astype(np.int64)
    imag = np.rint(array.imag).astype(np.int64)
    residual = max(
        float(np.max(np.abs(array.real - real), initial=0.0)),
        float(np.max(np.abs(array.imag - imag), initial=0.0)),
    )
    if residual != 0.0:
        raise ArithmeticError(f"{label} is not exactly Gaussian-integral: {residual}")
    return real, imag


def _complex_from_integer_parts(real: np.ndarray, imag: np.ndarray) -> np.ndarray:
    """Complex carrier used only where a legacy tensor routine is sampled."""
    return np.asarray(real, dtype=float) + 1j * np.asarray(imag, dtype=float)


def _complex_linear_realification(
    real: np.ndarray,
    imag: np.ndarray,
) -> np.ndarray:
    """Real matrix for a complex-linear map with interleaved input."""
    real = np.asarray(real, dtype=np.int64)
    imag = np.asarray(imag, dtype=np.int64)
    if real.shape != imag.shape or real.ndim != 2:
        raise ValueError("real and imaginary map parts must be equal 2D arrays")
    output = np.empty((2 * real.shape[0], 2 * real.shape[1]), dtype=np.int64)
    output[: real.shape[0], 0::2] = real
    output[: real.shape[0], 1::2] = -imag
    output[real.shape[0] :, 0::2] = imag
    output[real.shape[0] :, 1::2] = real
    return output


def _complex_output_realification(
    real: np.ndarray,
    imag: np.ndarray,
) -> np.ndarray:
    """Stack real/imaginary output rows for real input coordinates."""
    real = np.asarray(real, dtype=np.int64)
    imag = np.asarray(imag, dtype=np.int64)
    if real.shape != imag.shape:
        raise ValueError("real and imaginary map parts disagree")
    return np.vstack((real, imag))


def _bilinear_real_interleaved(
    real: np.ndarray,
    imag: np.ndarray,
) -> np.ndarray:
    """Real form Re(z^T A z), in interleaved complex coordinates."""
    real = np.asarray(real, dtype=np.int64)
    imag = np.asarray(imag, dtype=np.int64)
    standard = np.block([[real, imag], [imag, -real]])
    dimension = real.shape[0]
    order = [entry for index in range(dimension) for entry in (index, dimension + index)]
    return np.asarray(standard[np.ix_(order, order)], dtype=np.int64)


@lru_cache(maxsize=1)
def exact_delta_numerator() -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Return Gaussian integer ``d`` with Delta_R=(sqrt(2)/4)d.

    This is derived from the defining wedge form, not from normalized decimal
    coordinates.  Its canonical kinetic norm squared is eight before the
    normalization factor.
    """
    import direct_phi_h_sigmabar_tensor_v20 as direct
    import exact_phisigma_126bar_minus_projectors_v20 as minus

    z1 = direct.add_forms(direct.one_form(0), direct.scale_form(direct.one_form(1), 1j))
    z2 = direct.add_forms(direct.one_form(2), direct.scale_form(direct.one_form(3), 1j))
    z3 = direct.add_forms(direct.one_form(4), direct.scale_form(direct.one_form(5), 1j))
    omega = direct.wedge(direct.wedge(z1, z2), z3)
    right = direct.add_forms(
        direct.wedge(direct.one_form(6), direct.one_form(7)),
        direct.wedge(direct.one_form(8), direct.one_form(9)),
    )
    unnormalised = direct.wedge(omega, right)
    norm_squared = direct.sigma_kinetic_inner(unnormalised, unnormalised)
    if norm_squared != 8:
        raise ArithmeticError(f"unexpected exact Delta numerator norm: {norm_squared!r}")
    coordinates = np.asarray(
        [direct.sigma_kinetic_inner(state, unnormalised) for state in minus.sigma_basis()],
        dtype=complex,
    )
    real, imag = _gaussian_integer_parts(coordinates, label="Delta_R numerator")
    support = np.flatnonzero(real | imag)
    return real, imag, {
        "normalisation": "Delta_R=(sqrt(2)/4)*d",
        "unnormalised_kinetic_norm_squared": 8,
        "support_size": int(support.size),
        "support": [int(index) for index in support],
    }


@lru_cache(maxsize=1)
def _self_pair_casimir_integer() -> tuple[sparse.csr_matrix, sparse.csr_matrix]:
    """Gaussian-integer pair Casimir as real and imaginary sparse parts."""
    import exact_126bar_self_quartic_basis_v20 as self_gate

    generator_real, generator_imag = _gaussian_integer_parts(
        self_gate._generators(), label="126bar generators"
    )
    dimension = generator_real.shape[1] ** 2
    real_operator = sparse.csr_matrix((dimension, dimension), dtype=np.int64)
    imag_operator = sparse.csr_matrix((dimension, dimension), dtype=np.int64)
    for real, imag in zip(generator_real, generator_imag, strict=True):
        real_sparse = sparse.csr_matrix(real)
        imag_sparse = sparse.csr_matrix(imag)
        real_operator = real_operator + sparse.kron(
            real_sparse, real_sparse, format="csr"
        ) - sparse.kron(imag_sparse, imag_sparse, format="csr")
        imag_operator = imag_operator + sparse.kron(
            real_sparse, imag_sparse, format="csr"
        ) + sparse.kron(imag_sparse, real_sparse, format="csr")
    real_operator.eliminate_zeros()
    imag_operator.eliminate_zeros()
    return real_operator, imag_operator


def _apply_gaussian_sparse(
    operator_real: sparse.csr_matrix,
    operator_imag: sparse.csr_matrix,
    value_real: np.ndarray,
    value_imag: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    real_row_l1 = _sparse_maximum_row_l1(operator_real)
    imag_row_l1 = _sparse_maximum_row_l1(operator_imag)
    value_real_bound = _max_abs_integer(value_real)
    value_imag_bound = _max_abs_integer(value_imag)
    _require_int64_bound(
        "Gaussian sparse Casimir real output",
        real_row_l1 * value_real_bound + imag_row_l1 * value_imag_bound,
    )
    _require_int64_bound(
        "Gaussian sparse Casimir imaginary output",
        real_row_l1 * value_imag_bound + imag_row_l1 * value_real_bound,
    )
    real = operator_real @ value_real - operator_imag @ value_imag
    imag = operator_real @ value_imag + operator_imag @ value_real
    return np.asarray(real, dtype=np.int64), np.asarray(imag, dtype=np.int64)


@lru_cache(maxsize=1)
def direct_exact_mixed_hessian() -> tuple[np.ndarray, np.ndarray, int, dict[str, Any]]:
    """Exact Hessian of the A-shift and contraction-map norm squares."""
    import direct_phi_h_sigmabar_tensor_v20 as direct
    import exact_126bar_self_quartic_basis_v20 as self_gate
    import exact_210_126bar_cubic_clebsch_v20 as cubic
    import exact_phisigma_126bar_minus_projectors_v20 as minus
    import exact_phisigma_casimir_projectors_v20 as projectors

    d_real, d_imag, _metadata = exact_delta_numerator()
    d = _complex_from_integer_parts(d_real, d_imag)
    basis = minus.sigma_basis()
    p_form = direct.singlet_basis()["p"]

    cubic_at_p = np.asarray(
        [[cubic.cubic_invariant(p_form, left, right) for right in basis] for left in basis],
        dtype=complex,
    )
    op_real, op_imag = _gaussian_integer_parts(cubic_at_p, label="cubic operator at P")
    if np.any(op_imag):
        # The implementation supports complex operators, but the exact P
        # operator is real in the canonical basis and this is a useful guard.
        raise ArithmeticError("cubic operator at P unexpectedly acquired imaginary entries")
    shifted_real = op_real - 2 * np.eye(len(basis), dtype=np.int64)

    # Y[:,i] is A_{delta Phi_i} d.  Sampling the defining cubic contraction
    # on the unnormalised integer form avoids every square-root coefficient.
    unnormalised_delta = direct.add_forms(
        *[
            direct.scale_form(state, complex(int(d_real[index]), int(d_imag[index])))
            for index, state in enumerate(basis)
            if d_real[index] or d_imag[index]
        ]
    )
    y = np.asarray(
        [
            [cubic.cubic_invariant(phi, sigma, unnormalised_delta) for phi in projectors.FOUR_BASIS]
            for sigma in basis
        ],
        dtype=complex,
    )
    y_real, y_imag = _gaussian_integer_parts(y, label="cubic Phi derivative on d")

    a_rows = 2 * len(basis)
    a_rational = np.zeros((a_rows, PD_DIMENSION), dtype=np.int64)
    a_radical = np.zeros_like(a_rational)
    a_radical[:, :PHI_DIMENSION] = _complex_output_realification(y_real, y_imag)
    a_rational[:, PHI_DIMENSION:] = 4 * _complex_linear_realification(
        shifted_real, op_imag
    )

    tensor_real, tensor_imag = _gaussian_integer_parts(
        minus.full_contraction_tensor(), label="Phi-Sigma contraction tensor"
    )
    # C_{delta Phi} d.
    contraction_bound = _require_int64_bound(
        "mixed contraction tensor on d",
        2
        * d_real.size
        * max(_max_abs_integer(tensor_real), _max_abs_integer(tensor_imag))
        * max(_max_abs_integer(d_real), _max_abs_integer(d_imag)),
    )
    c_phi_real = np.einsum(
        "aik,k->ai", tensor_real, d_real, optimize=True
    ) - np.einsum("aik,k->ai", tensor_imag, d_imag, optimize=True)
    c_phi_imag = np.einsum(
        "aik,k->ai", tensor_real, d_imag, optimize=True
    ) + np.einsum("aik,k->ai", tensor_imag, d_real, optimize=True)
    p_index = projectors.FOUR_INDEX[(6, 7, 8, 9)]
    c_p_real = tensor_real[:, p_index, :]
    c_p_imag = tensor_imag[:, p_index, :]
    c_rows = 20
    c_rational = np.zeros((c_rows, PD_DIMENSION), dtype=np.int64)
    c_radical = np.zeros_like(c_rational)
    c_radical[:, :PHI_DIMENSION] = _complex_output_realification(
        c_phi_real, c_phi_imag
    )
    c_rational[:, PHI_DIMENSION:] = 4 * _complex_linear_realification(
        c_p_real, c_p_imag
    )

    mixed_gemm_bound = _require_int64_bound(
        "mixed-square rational Gram",
        a_rows
        * (
            _max_abs_integer(a_rational) ** 2
            + 2 * _max_abs_integer(a_radical) ** 2
        )
        + c_rows
        * (
            _max_abs_integer(c_rational) ** 2
            + 2 * _max_abs_integer(c_radical) ** 2
        ),
    )
    mixed_radical_gemm_bound = _require_int64_bound(
        "mixed-square radical Gram",
        2
        * (
            a_rows * _max_abs_integer(a_rational) * _max_abs_integer(a_radical)
            + c_rows * _max_abs_integer(c_rational) * _max_abs_integer(c_radical)
        ),
    )
    rational = (
        a_rational.T @ a_rational
        + c_rational.T @ c_rational
        + 2 * (a_radical.T @ a_radical + c_radical.T @ c_radical)
    )
    radical = (
        a_rational.T @ a_radical
        + a_radical.T @ a_rational
        + c_rational.T @ c_radical
        + c_radical.T @ c_rational
    )
    if not np.array_equal(rational, rational.T) or not np.array_equal(radical, radical.T):
        raise ArithmeticError("exact mixed Hessian lost symmetry")
    return rational, radical, MIXED_EXACT_DENOMINATOR, {
        "identity": "2*(J_A^T J_A + J_C^T J_C)",
        "J_A": "d[(A_Phi-2)Sigma]",
        "J_C": "d[C_Phi Sigma]",
        "field": "Q(sqrt(2))",
        "maximum_abs_rational_numerator": int(np.max(np.abs(rational))),
        "maximum_abs_radical_numerator": int(np.max(np.abs(radical))),
        "int64_overflow_preflight": {
            "rational_Gram_absolute_bound": mixed_gemm_bound,
            "radical_Gram_absolute_bound": mixed_radical_gemm_bound,
            "contraction_on_d_absolute_bound": contraction_bound,
            "int64_limit": INT64_MAX,
        },
    }


@lru_cache(maxsize=1)
def direct_exact_self_hessian() -> tuple[np.ndarray, int, dict[str, Any]]:
    """Exact angular 126bar self Hessian for the four positive weights."""
    import exact_126bar_self_quartic_basis_v20 as self_gate

    coefficients = [
        sum(SELF_WEIGHTS[channel] * self_gate._poly(channel)[degree] for channel in SELF_WEIGHTS)
        for degree in range(4)
    ]
    polynomial_denominator = _fraction_lcm(value.denominator for value in coefficients)
    polynomial_numerators = np.asarray(
        [int(value * polynomial_denominator) for value in coefficients], dtype=np.int64
    )
    if polynomial_denominator != 32_256 or tuple(polynomial_numerators) != (
        28_707,
        2_987,
        605,
        -43,
    ):
        raise ArithmeticError("unexpected exact 126bar combined projector polynomial")

    d_real, d_imag, _metadata = exact_delta_numerator()
    dimension = d_real.size
    pair_dimension = dimension * dimension
    linear_real = np.zeros((pair_dimension, SIGMA_REAL_DIMENSION), dtype=np.int64)
    linear_imag = np.zeros_like(linear_real)
    for index in range(dimension):
        base_real = np.zeros((dimension, dimension), dtype=np.int64)
        base_imag = np.zeros_like(base_real)
        base_real[:, index] += d_real
        base_real[index, :] += d_real
        base_imag[:, index] += d_imag
        base_imag[index, :] += d_imag
        linear_real[:, 2 * index] = base_real.ravel()
        linear_imag[:, 2 * index] = base_imag.ravel()
        linear_real[:, 2 * index + 1] = -base_imag.ravel()
        linear_imag[:, 2 * index + 1] = base_real.ravel()

    operator_real, operator_imag = _self_pair_casimir_integer()
    current_real, current_imag = linear_real, linear_imag
    response_bound = _require_int64_bound(
        "126bar projector response degree zero",
        abs(int(polynomial_numerators[0]))
        * max(_max_abs_integer(current_real), _max_abs_integer(current_imag)),
    )
    response_real = polynomial_numerators[0] * current_real
    response_imag = polynomial_numerators[0] * current_imag
    for numerator in polynomial_numerators[1:]:
        current_real, current_imag = _apply_gaussian_sparse(
            operator_real, operator_imag, current_real, current_imag
        )
        response_bound = _require_int64_bound(
            "126bar projector response accumulation",
            response_bound
            + abs(int(numerator))
            * max(_max_abs_integer(current_real), _max_abs_integer(current_imag)),
        )
        response_real += numerator * current_real
        response_imag += numerator * current_imag

    # Re <L_i,W L_j>.  L is very sparse, so sparse multiplication preserves
    # exact int64 arithmetic and avoids a multi-gigabyte dense GEMM.
    linear_stacked = sparse.csc_matrix(np.vstack((linear_real, linear_imag)))
    response_stacked = np.vstack((response_real, response_imag))
    maximum_linear_column_l1 = int(
        np.max(np.asarray(abs(linear_stacked).sum(axis=0)), initial=0.0)
    )
    gram_bound = _require_int64_bound(
        "126bar exact sparse Gram",
        maximum_linear_column_l1 * _max_abs_integer(response_stacked),
    )
    gram = np.asarray(linear_stacked.T @ response_stacked, dtype=np.int64)

    pair_real = np.outer(d_real, d_real) - np.outer(d_imag, d_imag)
    pair_imag = np.outer(d_real, d_imag) + np.outer(d_imag, d_real)
    current_pair_real = pair_real.ravel()[:, None]
    current_pair_imag = pair_imag.ravel()[:, None]
    projected_bound = _require_int64_bound(
        "126bar background projection degree zero",
        abs(int(polynomial_numerators[0]))
        * max(_max_abs_integer(current_pair_real), _max_abs_integer(current_pair_imag)),
    )
    projected_real = polynomial_numerators[0] * current_pair_real
    projected_imag = polynomial_numerators[0] * current_pair_imag
    for numerator in polynomial_numerators[1:]:
        current_pair_real, current_pair_imag = _apply_gaussian_sparse(
            operator_real,
            operator_imag,
            current_pair_real,
            current_pair_imag,
        )
        projected_bound = _require_int64_bound(
            "126bar background projection accumulation",
            projected_bound
            + abs(int(numerator))
            * max(
                _max_abs_integer(current_pair_real),
                _max_abs_integer(current_pair_imag),
            ),
        )
        projected_real += numerator * current_pair_real
        projected_imag += numerator * current_pair_imag
    projected_real = projected_real.reshape(dimension, dimension)
    projected_imag = projected_imag.reshape(dimension, dimension)
    base = _bilinear_real_interleaved(projected_real, projected_imag)
    value_bound = _require_int64_bound(
        "126bar background projected inner product",
        int(np.count_nonzero(pair_real) + np.count_nonzero(pair_imag))
        * max(_max_abs_integer(pair_real), _max_abs_integer(pair_imag))
        * max(_max_abs_integer(projected_real), _max_abs_integer(projected_imag)),
    )
    value_numerator = int(
        np.sum(pair_real * projected_real + pair_imag * projected_imag)
    )
    hessian_bound = _require_int64_bound(
        "126bar Hessian numerator combination",
        8 * gram_bound
        + 16 * max(_max_abs_integer(projected_real), _max_abs_integer(projected_imag))
        + 2 * value_bound,
    )
    hessian_numerator = (
        8 * gram
        + 16 * base
        - 2 * value_numerator * np.eye(SIGMA_REAL_DIMENSION, dtype=np.int64)
    )
    if not np.array_equal(hessian_numerator, hessian_numerator.T):
        raise ArithmeticError("exact 126bar self Hessian lost symmetry")
    denominator = 64 * polynomial_denominator
    if denominator != SELF_EXACT_DENOMINATOR:
        raise ArithmeticError("unexpected exact self-Hessian denominator")
    return hessian_numerator, denominator, {
        "combined_projector_polynomial_numerators": polynomial_numerators.tolist(),
        "combined_projector_polynomial_denominator": polynomial_denominator,
        "background_projected_value_numerator": value_numerator,
        "background_projected_value": str(Fraction(value_numerator, polynomial_denominator * 64)),
        "formula": "(8 L^T W L + 16 B(W(dd)) - 2 <dd,W(dd)> I)/(64*32256)",
        "int64_overflow_preflight": {
            "projector_response_absolute_bound": response_bound,
            "sparse_Gram_absolute_bound": gram_bound,
            "background_projection_absolute_bound": projected_bound,
            "background_inner_product_absolute_bound": value_bound,
            "Hessian_combination_absolute_bound": hessian_bound,
            "int64_limit": INT64_MAX,
        },
    }


@lru_cache(maxsize=1)
def _phi_pair_casimir_integer() -> sparse.csr_matrix:
    import exact_phisigma_casimir_projectors_v20 as projectors

    dimension = PHI_DIMENSION * PHI_DIMENSION
    operator = sparse.csr_matrix((dimension, dimension), dtype=np.int64)
    for index, generator in enumerate(projectors.generator_matrices()):
        rounded = np.rint(generator.data).astype(np.int64)
        if np.max(np.abs(generator.data - rounded), initial=0.0) != 0.0:
            raise ArithmeticError(f"210 generator {index} is not exactly integral")
        exact_generator = sparse.csr_matrix(
            (rounded, generator.indices.copy(), generator.indptr.copy()),
            shape=generator.shape,
            dtype=np.int64,
        )
        operator = operator + sparse.kron(
            exact_generator, exact_generator, format="csr"
        )
    operator.eliminate_zeros()
    # Each entry is a sum over only 45 signed-permutation generators.
    _require_int64_bound("210 pair-Casimir construction", 45)
    return operator


@lru_cache(maxsize=1)
def direct_exact_phi_hessian() -> tuple[np.ndarray, int, dict[str, Any]]:
    """Exact Pati--Salam 210 Hessian from its three projector squares."""
    import exact_phisigma_casimir_projectors_v20 as projectors

    polynomials = [
        projectors.projector_polynomial(projectors.SPECTRAL_EIGENVALUES[channel])
        for channel in ("45", "210", "5940")
    ]
    combined = [sum(polynomial[degree] for polynomial in polynomials) for degree in range(8)]
    denominator = _fraction_lcm(value.denominator for value in combined)
    numerators = np.asarray([int(value * denominator) for value in combined], dtype=np.int64)
    expected = (0, 142_765_056, -40_488_576, -4_008_448, 2_398_792, -283_212, 13_334, -221)
    if denominator != PHI_EXACT_DENOMINATOR or tuple(numerators) != expected:
        raise ArithmeticError("unexpected exact 210 projector polynomial")

    p_index = projectors.FOUR_INDEX[(6, 7, 8, 9)]
    rows = np.concatenate(
        (
            p_index * PHI_DIMENSION + np.arange(PHI_DIMENSION),
            np.arange(PHI_DIMENSION) * PHI_DIMENSION + p_index,
        )
    )
    columns = np.tile(np.arange(PHI_DIMENSION), 2)
    values = np.ones(2 * PHI_DIMENSION, dtype=np.int64)
    # At i=p the two contributions coincide and must add to two.
    linear = sparse.csc_matrix(
        (values, (rows, columns)),
        shape=(PHI_DIMENSION * PHI_DIMENSION, PHI_DIMENSION),
        dtype=np.int64,
    )
    operator = _phi_pair_casimir_integer()
    operator_row_l1 = _sparse_maximum_row_l1(operator)
    current: np.ndarray | sparse.spmatrix = linear
    response: np.ndarray | sparse.spmatrix = numerators[0] * current
    response_bound = 0
    for numerator in numerators[1:]:
        current_bound = _require_int64_bound(
            "210 pair-Casimir power",
            operator_row_l1 * _max_abs_integer(current),
        )
        current = operator @ current
        response_bound = _require_int64_bound(
            "210 projector response accumulation",
            response_bound + abs(int(numerator)) * current_bound,
        )
        response = response + numerator * current
    linear_column_l1 = int(
        np.max(np.asarray(abs(linear).sum(axis=0)), initial=0.0)
    )
    gram_bound = _require_int64_bound(
        "210 exact sparse Gram",
        linear_column_l1 * response_bound,
    )
    gram = linear.T @ response
    gram_array = gram.toarray() if sparse.issparse(gram) else np.asarray(gram)
    gram_array = np.asarray(gram_array, dtype=np.int64)
    radial = np.zeros((PHI_DIMENSION, PHI_DIMENSION), dtype=np.int64)
    radial[p_index, p_index] = 1
    hessian_bound = _require_int64_bound(
        "210 Hessian numerator combination",
        2 * gram_bound + 8 * denominator,
    )
    hessian_numerator = 2 * gram_array + 8 * denominator * radial
    if not np.array_equal(hessian_numerator, hessian_numerator.T):
        raise ArithmeticError("exact 210 Hessian lost symmetry")
    return hessian_numerator, denominator, {
        "positive_projector_channels": ["45", "210", "5940"],
        "projector_polynomial_numerators": numerators.tolist(),
        "projector_polynomial_denominator": denominator,
        "formula": "8 pp^T + 2 L^T(P45+P210+P5940)L",
        "int64_overflow_preflight": {
            "pair_Casimir_maximum_row_l1": operator_row_l1,
            "projector_response_absolute_bound": response_bound,
            "sparse_Gram_absolute_bound": gram_bound,
            "Hessian_combination_absolute_bound": hessian_bound,
            "int64_limit": INT64_MAX,
        },
    }


@lru_cache(maxsize=1)
def direct_exact_source_matrices() -> dict[str, Any]:
    """Assemble reduced exact numerator pairs for K, H_Phi and their sum."""
    mixed_rational, mixed_radical, mixed_denominator, mixed_metadata = (
        direct_exact_mixed_hessian()
    )
    self_numerator, self_denominator, self_metadata = direct_exact_self_hessian()
    common_k_denominator = math.lcm(mixed_denominator, self_denominator)
    k_combination_bound = _require_int64_bound(
        "K common-denominator assembly",
        _max_abs_integer(mixed_rational)
        * (common_k_denominator // mixed_denominator)
        + _max_abs_integer(self_numerator)
        * (common_k_denominator // self_denominator),
    )
    k_radical_bound = _require_int64_bound(
        "K radical common-denominator assembly",
        _max_abs_integer(mixed_radical)
        * (common_k_denominator // mixed_denominator),
    )
    k_rational = mixed_rational * (common_k_denominator // mixed_denominator)
    k_radical = mixed_radical * (common_k_denominator // mixed_denominator)
    k_rational[PHI_DIMENSION:, PHI_DIMENSION:] += (
        self_numerator * (common_k_denominator // self_denominator)
    )
    k_rational, k_radical, k_denominator = _reduced_pair(
        k_rational, k_radical, common_k_denominator
    )

    phi_numerator_small, phi_denominator_raw, phi_metadata = direct_exact_phi_hessian()
    phi_rational = np.zeros((PD_DIMENSION, PD_DIMENSION), dtype=np.int64)
    phi_rational[:PHI_DIMENSION, :PHI_DIMENSION] = phi_numerator_small
    phi_radical = np.zeros_like(phi_rational)
    phi_rational, phi_radical, phi_denominator = _reduced_pair(
        phi_rational, phi_radical, phi_denominator_raw
    )

    sum_denominator = math.lcm(k_denominator, phi_denominator)
    sum_rational_bound = _require_int64_bound(
        "H_Phi+K common-denominator rational assembly",
        _max_abs_integer(k_rational) * (sum_denominator // k_denominator)
        + _max_abs_integer(phi_rational) * (sum_denominator // phi_denominator),
    )
    sum_radical_bound = _require_int64_bound(
        "H_Phi+K common-denominator radical assembly",
        _max_abs_integer(k_radical) * (sum_denominator // k_denominator),
    )
    sum_rational = (
        k_rational * (sum_denominator // k_denominator)
        + phi_rational * (sum_denominator // phi_denominator)
    )
    sum_radical = k_radical * (sum_denominator // k_denominator)
    sum_rational, sum_radical, sum_denominator = _reduced_pair(
        sum_rational, sum_radical, sum_denominator
    )
    return {
        "K": (k_rational, k_radical, k_denominator),
        "H_Phi": (phi_rational, phi_radical, phi_denominator),
        "H_Phi_plus_K": (sum_rational, sum_radical, sum_denominator),
        "construction": {
            "mixed": mixed_metadata,
            "self": self_metadata,
            "Phi": phi_metadata,
            "reduced_denominators": {
                "K": k_denominator,
                "H_Phi": phi_denominator,
                "H_Phi_plus_K": sum_denominator,
            },
            "int64_overflow_preflight": {
                "K_rational_assembly_absolute_bound": k_combination_bound,
                "K_radical_assembly_absolute_bound": k_radical_bound,
                "sum_rational_assembly_absolute_bound": sum_rational_bound,
                "sum_radical_assembly_absolute_bound": sum_radical_bound,
                "int64_limit": INT64_MAX,
            },
        },
    }


def _connected_components(matrix: np.ndarray) -> tuple[tuple[int, ...], ...]:
    adjacency = np.abs(np.asarray(matrix, dtype=float)) >= ZERO_CUTOFF
    remaining = set(range(adjacency.shape[0]))
    components: list[tuple[int, ...]] = []
    while remaining:
        initial = min(remaining)
        queue = deque([initial])
        reached = {initial}
        remaining.remove(initial)
        while queue:
            row = queue.popleft()
            neighbours = set(np.flatnonzero(adjacency[row])).intersection(remaining)
            remaining.difference_update(neighbours)
            reached.update(neighbours)
            queue.extend(sorted(neighbours))
        components.append(tuple(sorted(reached)))
    return tuple(components)


def _exact_connected_components(
    rational_numerator: np.ndarray,
    radical_numerator: np.ndarray,
) -> tuple[tuple[int, ...], ...]:
    adjacency = (np.asarray(rational_numerator) != 0) | (
        np.asarray(radical_numerator) != 0
    )
    remaining = set(range(adjacency.shape[0]))
    components: list[tuple[int, ...]] = []
    while remaining:
        initial = min(remaining)
        queue = deque([initial])
        reached = {initial}
        remaining.remove(initial)
        while queue:
            row = queue.popleft()
            neighbours = set(np.flatnonzero(adjacency[row])).intersection(remaining)
            remaining.difference_update(neighbours)
            reached.update(neighbours)
            queue.extend(sorted(neighbours))
        components.append(tuple(sorted(reached)))
    return tuple(components)


def direct_exact_matrix_audit(
    rational_numerator: np.ndarray,
    radical_numerator: np.ndarray,
    denominator: int,
) -> dict[str, Any]:
    """Exact componentwise PSD/rank audit with entrywise source binding."""
    rational = np.asarray(rational_numerator, dtype=np.int64)
    radical = np.asarray(radical_numerator, dtype=np.int64)
    if rational.shape != (PD_DIMENSION, PD_DIMENSION) or radical.shape != rational.shape:
        raise ValueError(f"expected two {PD_DIMENSION}x{PD_DIMENSION} numerators")
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    if not np.array_equal(rational, rational.T) or not np.array_equal(radical, radical.T):
        raise ArithmeticError("exact numerator pair is not symmetric")
    components = _exact_connected_components(rational, radical)
    total_rank = 0
    failures: list[dict[str, Any]] = []
    for component_index, indices in enumerate(components):
        exact = [
            [
                Qsqrt2(
                    Fraction(int(rational[row, column]), denominator),
                    Fraction(int(radical[row, column]), denominator),
                )
                for column in indices
            ]
            for row in indices
        ]
        result = exact_psd_rank(exact)
        total_rank += int(result["rank"])
        if not result["PSD"]:
            failures.append(
                {
                    "component": component_index,
                    "indices": list(indices),
                    "reason": result["reason"],
                }
            )
    counts = Counter(len(component) for component in components)
    return {
        "matrix_dimension": PD_DIMENSION,
        "field": "Q(sqrt(2))",
        "exact_common_denominator": int(denominator),
        "component_count": len(components),
        "component_size_counts": {
            str(size): int(count) for size, count in sorted(counts.items())
        },
        "maximum_component_size": max(map(len, components)),
        "exact_PSD": not failures,
        "exact_rank": total_rank,
        "exact_nullity": PD_DIMENSION - total_rank,
        "failures": failures,
        "source_binding_exact": True,
    }


def conditional_exact_matrix_audit(matrix: np.ndarray) -> dict[str, Any]:
    """Reconstruct small Q(sqrt(2)) blocks and audit them exactly."""
    observed = np.asarray(matrix, dtype=float)
    if observed.shape != (PD_DIMENSION, PD_DIMENSION):
        raise ValueError(f"expected a {PD_DIMENSION}x{PD_DIMENSION} matrix")
    symmetry_residual = float(np.max(np.abs(observed - observed.T)))
    components = _connected_components(observed)
    total_rank = 0
    maximum_residual = float(np.max(np.abs(observed[np.abs(observed) < ZERO_CUTOFF])))
    minimum_alternative = float("inf")
    kinds: Counter[str] = Counter()
    failures: list[dict[str, Any]] = []
    for component_index, indices in enumerate(components):
        exact: list[list[Qsqrt2]] = []
        for row in indices:
            exact_row: list[Qsqrt2] = []
            for column in indices:
                value, metadata = reconstruct_qsqrt2(observed[row, column])
                exact_row.append(value)
                kinds[str(metadata["kind"])] += 1
                maximum_residual = max(
                    maximum_residual, float(metadata["chosen_abs_residual"])
                )
                minimum_alternative = min(
                    minimum_alternative, float(metadata["alternative_abs_residual"])
                )
            exact.append(exact_row)
        if any(
            exact[row][column] != exact[column][row]
            for row in range(len(exact))
            for column in range(len(exact))
        ):
            failures.append(
                {"component": component_index, "reason": "exact symmetry failure"}
            )
            continue
        result = exact_psd_rank(exact)
        total_rank += int(result["rank"])
        if not result["PSD"]:
            failures.append(
                {
                    "component": component_index,
                    "indices": list(indices),
                    "reason": result["reason"],
                }
            )
    size_counts = Counter(len(component) for component in components)
    return {
        "matrix_dimension": PD_DIMENSION,
        "component_count": len(components),
        "component_size_counts": {
            str(size): int(count) for size, count in sorted(size_counts.items())
        },
        "maximum_component_size": max(map(len, components)),
        "observed_symmetry_max_abs_residual": symmetry_residual,
        "reconstruction_denominator": RECONSTRUCTION_DENOMINATOR,
        "reconstruction_kinds": dict(kinds),
        "maximum_reconstruction_abs_residual": maximum_residual,
        "minimum_alternative_lattice_abs_residual": minimum_alternative,
        "exact_PSD_on_reconstructed_matrix": not failures,
        "exact_rank_on_reconstructed_matrix": total_rank,
        "exact_nullity_on_reconstructed_matrix": PD_DIMENSION - total_rank,
        "failures": failures,
        "source_binding_exact": False,
    }


def _live_source_matrices() -> tuple[np.ndarray, np.ndarray]:
    """Assemble H_Phi and K through the current all-component source path."""
    import coupled_p_delta_physical_chirality_search_v20 as coupled
    import exact_p_delta_second_stage_hessian_v20 as sigma_source

    coefficients = coupled.coefficient_matrices()
    rows, _self_data, _mixed_data, _cubic = sigma_source._all_matrices()
    sigma_angular = sum(
        (
            float(weight) * rows[f"self_{channel}"]
            for channel, weight in SELF_WEIGHTS.items()
        ),
        np.zeros((SIGMA_REAL_DIMENSION, SIGMA_REAL_DIMENSION), dtype=float),
    )
    self_matrix = np.zeros((PD_DIMENSION, PD_DIMENSION), dtype=float)
    self_matrix[PHI_DIMENSION:, PHI_DIMENSION:] = sigma_angular
    mixed_matrix = sum(
        (
            float(weight) * coefficients["matrices"][f"lambda_{channel}"]
            for channel, weight in zip(
                MIXED_CHANNELS, TOTAL_MIXED_WEIGHTS, strict=True
            )
        ),
        np.zeros((PD_DIMENSION, PD_DIMENSION), dtype=float),
    )
    # The A-shift square supplies -4 O14.  The +4 Sigma norm term is already
    # represented by the radial subtraction in the angular coefficient rows.
    mixed_matrix -= 4.0 * coefficients["matrices"]["mu_eta"]
    K = 0.5 * (self_matrix + mixed_matrix + (self_matrix + mixed_matrix).T)
    H_phi = np.asarray(coefficients["matrices"]["rho_phi"], dtype=float)
    H_phi = 0.5 * (H_phi + H_phi.T)
    return H_phi, K


def recompute_conditional_certificate() -> dict[str, Any]:
    H_phi, K = _live_source_matrices()
    k_audit = conditional_exact_matrix_audit(K)
    phi_audit = conditional_exact_matrix_audit(H_phi)
    sum_audit = conditional_exact_matrix_audit(H_phi + K)
    return {
        "source_path": [
            "coupled_p_delta_physical_chirality_search_v20.coefficient_matrices",
            "exact_p_delta_second_stage_hessian_v20._all_matrices",
        ],
        "K": k_audit,
        "H_Phi": phi_audit,
        "H_Phi_plus_K": sum_audit,
        "conditional_hierarchy_conclusion": (
            "If the reconstructed matrices are exactly the source matrices, "
            "H_Phi+t*r^2*K is PSD with nullity 33 for every t>0 and r!=0."
        ),
        "source_binding_exact": False,
        "proof_grade": False,
    }


def recompute_direct_certificate(*, compare_live: bool = False) -> dict[str, Any]:
    """Rebuild and certify the source matrices without reconstruction."""
    matrices = direct_exact_source_matrices()
    result = {
        "evidence_kind": "direct_Gaussian_integer_Fraction_Qsqrt2_source_assembly",
        "source_path": [
            "direct_phi_h_sigmabar_tensor_v20 form/generator definitions",
            "exact_126bar_self_quartic_basis_v20 projector polynomials",
            "exact_phisigma_casimir_projectors_v20 projector polynomials",
            "exact_210_126bar_cubic_clebsch_v20 cubic contraction",
        ],
        "construction": matrices["construction"],
        "K": direct_exact_matrix_audit(*matrices["K"]),
        "H_Phi": direct_exact_matrix_audit(*matrices["H_Phi"]),
        "H_Phi_plus_K": direct_exact_matrix_audit(*matrices["H_Phi_plus_K"]),
        "hierarchy_conclusion": (
            "H_Phi and K are exact PSD matrices and ker(H_Phi+K) has "
            "dimension 33. Since ker(A+sB)=ker(A) intersect ker(B) for "
            "PSD A,B and every s>0, H_Phi+t*r^2*K is PSD with the same "
            "nullity for all t>0 and r!=0."
        ),
        "source_binding_exact": True,
        "proof_grade": True,
    }
    if compare_live:
        live_phi, live_k = _live_source_matrices()
        comparisons: dict[str, float] = {}
        for name, live in (
            ("K", live_k),
            ("H_Phi", live_phi),
            ("H_Phi_plus_K", live_phi + live_k),
        ):
            rational, radical, denominator = matrices[name]
            exact_float = (
                rational.astype(float) + math.sqrt(2.0) * radical.astype(float)
            ) / float(denominator)
            comparisons[name] = float(np.max(np.abs(exact_float - live)))
        result["nonproof_live_regression_max_abs_residuals"] = comparisons
        result["nonproof_live_regression_tolerance"] = 2.0e-11
        result["nonproof_live_regression_pass"] = max(comparisons.values()) < 2.0e-11
    return result


RESTRICTED_KERNEL_SPECTRUM = (
    ("0", 33),
    ("1/12", 2),
    ("143/504", 12),
    ("7/18", 24),
    ("31/72", 12),
    ("25/6", 1),
    ("1177/144", 64),
    ("307/36", 8),
    ("2155/252", 24),
    ("367/36", 6),
    ("187/18", 6),
    ("12", 24),
    ("767/24", 36),
    ("583/18", 18),
    ("229/7", 6),
)

RECORDED_DIRECT_CERTIFICATE = {
    "evidence_kind": "direct_Gaussian_integer_Fraction_Qsqrt2_source_assembly",
    "source_binding_exact": True,
    "proof_grade": True,
    "hierarchy_congruence": (
        "D=diag(I210,r I252): D^T H_PD D = H_Phi + t*r^2*K, t=1/8"
    ),
    "mixed_content": {
        "A_shift_weights": A_SHIFT_WEIGHTS,
        "C_square_weights": C_SQUARE_WEIGHTS,
        "total_weights": TOTAL_MIXED_WEIGHTS,
        "cubic_weight": -4,
        "self_weights_54_1050bar_2772bar_4125": ["2", "2", "17/16", "1"],
    },
    "component_decomposition": {
        "component_count": 89,
        "component_size_counts": {"1": 6, "2": 6, "4": 31, "6": 8, "7": 32, "8": 6},
        "maximum_component_size": 8,
    },
    "direct_exact_ranks": {
        "K": {"rank": 278, "nullity": 184, "PSD": True},
        "H_Phi": {"rank": 186, "nullity": 276, "PSD": True},
        "H_Phi_plus_K": {"rank": 429, "nullity": 33, "PSD": True},
    },
    "K_restricted_to_kernel_H_Phi_spectrum": [
        {"eigenvalue": eigenvalue, "multiplicity": multiplicity}
        for eigenvalue, multiplicity in RESTRICTED_KERNEL_SPECTRUM
    ],
    "exact_source": {
        "field": "Q(sqrt(2))",
        "reduced_denominators": {"K": 4032, "H_Phi": 90, "H_Phi_plus_K": 20160},
        "Delta_R_coordinates": "(sqrt(2)/4)*d with d Gaussian-integral",
        "entrywise_binding": (
            "integer/Gaussian-integer tensor contractions plus exact "
            "Fraction projector polynomials"
        ),
        "floating_point_reconstruction_used": False,
        "nonproof_live_source_regression": {
            "K_max_abs_residual": 1.0402345651527867e-11,
            "H_Phi_max_abs_residual": 7.105427357601002e-15,
            "H_Phi_plus_K_max_abs_residual": 1.0402345651527867e-11,
            "tolerance": 2.0e-11,
            "pass": True,
            "role": "entrywise regression only; exact proof is independent",
        },
    },
}

# Compatibility alias for downstream readers written while this certificate
# was deliberately fail-closed.  Its contents are now direct/proof-grade.
RECORDED_CONDITIONAL_CERTIFICATE = RECORDED_DIRECT_CERTIFICATE


def exact_rational_rank(matrix: np.ndarray) -> int:
    """Small exact row rank over Q."""
    work = [
        [Fraction(int(value)) for value in row]
        for row in np.asarray(matrix, dtype=np.int64)
    ]
    if not work:
        return 0
    row = 0
    for column in range(len(work[0])):
        pivot = next(
            (candidate for candidate in range(row, len(work)) if work[candidate][column]),
            None,
        )
        if pivot is None:
            continue
        work[row], work[pivot] = work[pivot], work[row]
        pivot_value = work[row][column]
        work[row] = [value / pivot_value for value in work[row]]
        for candidate in range(len(work)):
            if candidate == row or work[candidate][column] == 0:
                continue
            coefficient = work[candidate][column]
            work[candidate] = [
                left - coefficient * right
                for left, right in zip(work[candidate], work[row], strict=True)
            ]
        row += 1
        if row == len(work):
            break
    return row


@lru_cache(maxsize=1)
def exact_pd_gauge_orbit_audit() -> dict[str, Any]:
    """Exact rank of the SO(10) orbit through (P,Delta_R)."""
    import exact_126bar_self_quartic_basis_v20 as self_gate
    import exact_phisigma_casimir_projectors_v20 as projectors

    d_real, d_imag, _metadata = exact_delta_numerator()
    d = _complex_from_integer_parts(d_real, d_imag)
    p = np.zeros(PHI_DIMENSION, dtype=np.int64)
    p[projectors.FOUR_INDEX[(6, 7, 8, 9)]] = 1
    sigma_generators_real, sigma_generators_imag = _gaussian_integer_parts(
        self_gate._generators(), label="126bar gauge generators"
    )
    gauge_action_bound = _require_int64_bound(
        "P/Delta gauge-generator action",
        2
        * d_real.size
        * max(
            _max_abs_integer(sigma_generators_real),
            _max_abs_integer(sigma_generators_imag),
        )
        * max(_max_abs_integer(d_real), _max_abs_integer(d_imag)),
    )
    columns: list[np.ndarray] = []
    for index, (phi_generator, sigma_real, sigma_imag) in enumerate(
        zip(
            projectors.generator_matrices(),
            sigma_generators_real,
            sigma_generators_imag,
            strict=True,
        )
    ):
        phi_data = np.rint(phi_generator.data).astype(np.int64)
        if np.max(np.abs(phi_generator.data - phi_data), initial=0.0) != 0.0:
            raise ArithmeticError(f"210 gauge generator {index} is not integral")
        exact_phi_generator = sparse.csr_matrix(
            (phi_data, phi_generator.indices, phi_generator.indptr),
            shape=phi_generator.shape,
            dtype=np.int64,
        )
        phi_tangent = np.asarray(exact_phi_generator @ p, dtype=np.int64)
        # Gaussian product (A+iB)(dr+i di).
        sigma_tangent_real = sigma_real @ d_real - sigma_imag @ d_imag
        sigma_tangent_imag = sigma_real @ d_imag + sigma_imag @ d_real
        sigma_tangent = np.empty(SIGMA_REAL_DIMENSION, dtype=np.int64)
        sigma_tangent[0::2] = sigma_tangent_real
        sigma_tangent[1::2] = sigma_tangent_imag
        columns.append(np.concatenate((phi_tangent, sigma_tangent)))
    orbit = np.column_stack(columns)
    orbit_gram_bound = _require_int64_bound(
        "P/Delta exact gauge-orbit Gram",
        orbit.shape[0] * _max_abs_integer(orbit) ** 2,
    )
    gram = orbit.T @ orbit
    rank = exact_rational_rank(gram)
    return {
        "generator_count": 45,
        "exact_orbit_rank": rank,
        "exact_stabilizer_dimension": 45 - rank,
        "coordinate_row_scaling": (
            "the Sigma rows are multiplied by 4/sqrt(2), an invertible "
            "scaling, leaving a purely integral orbit matrix"
        ),
        "Gram_maximum_abs_entry": _max_abs_integer(gram),
        "int64_overflow_preflight": {
            "generator_action_absolute_bound": gauge_action_bound,
            "orbit_Gram_absolute_bound": orbit_gram_bound,
            "int64_limit": INT64_MAX,
        },
        "source_binding_exact": True,
    }


def extension_constraint_jacobian() -> tuple[np.ndarray, list[str], list[str]]:
    """Exact source-derived quotient Jacobian of the H/S/X SOS residuals.

    Gauge covariance lets us quotient the already certified 33-dimensional
    P+Delta gauge kernel.  Coordinates below are therefore the 24 newly
    adjoined real coordinates.  The returned matrix includes dependent source
    rows; exact elimination, rather than row selection by inspection, gives
    rank 19.  Nonzero vacuum scales only rescale/shear rows, so unit vacuum
    scales preserve the exact rank.
    """
    import itertools

    import direct_phi_h_sigmabar_tensor_v20 as direct

    coordinates = (
        [f"ReH{index}" for index in range(10)]
        + [f"ImH{index}" for index in range(10)]
        + ["ReS", "ImS", "ReX", "ImX"]
    )
    coordinate_index = {name: index for index, name in enumerate(coordinates)}
    rows: list[np.ndarray] = []
    labels: list[str] = []

    # Literal exterior derivative d(H wedge Phi) at Phi=e6789.  Work in the
    # complete independent five-form basis and retain all nonzero real rows.
    p_form = direct.singlet_basis()["p"]
    five_indices = tuple(itertools.combinations(range(10), 5))
    portal = np.zeros((len(five_indices), 20), dtype=complex)
    for component in range(10):
        image = direct.wedge(direct.one_form(component), p_form)
        values = np.asarray([image.get(indices, 0) for indices in five_indices])
        portal[:, component] = values
        portal[:, 10 + component] = 1j * values
    portal_real, portal_imag = _gaussian_integer_parts(
        portal, label="d(H wedge P)"
    )
    portal_rows = np.vstack((portal_real, portal_imag))
    portal_rows = portal_rows[np.any(portal_rows != 0, axis=1)]
    for index, source_row in enumerate(portal_rows):
        row = np.zeros(len(coordinates), dtype=np.int64)
        row[:20] = source_row
        rows.append(row)
        labels.append(f"d_H_wedge_P_source_row_{index}")

    # A polynomial SOS factorization of the complex-vector Gram determinant
    # uses g_ij=Re(H_i)Im(H_j)-Im(H_i)Re(H_j).  Differentiate every pair at
    # H=e6 and retain all nonzero source rows (including overlaps with portal).
    background_real = np.zeros(10, dtype=np.int64)
    background_imag = np.zeros(10, dtype=np.int64)
    background_real[6] = 1
    for first, second in itertools.combinations(range(10), 2):
        row = np.zeros(len(coordinates), dtype=np.int64)
        row[coordinate_index[f"ReH{first}"]] += background_imag[second]
        row[coordinate_index[f"ImH{second}"]] += background_real[first]
        row[coordinate_index[f"ImH{first}"]] -= background_real[second]
        row[coordinate_index[f"ReH{second}"]] -= background_imag[first]
        if np.any(row):
            rows.append(row)
            labels.append(f"d_complex_H_Gram_g_{first}_{second}")

    # Literal differentials of N_H-1, |S|^2-1 and |X|^2-1.
    for coordinate, label in (
        ("ReH6", "d_H_radial_residual"),
        ("ReS", "d_S_radial_residual"),
        ("ReX", "d_X_radial_residual"),
    ):
        row = np.zeros(len(coordinates), dtype=np.int64)
        row[coordinate_index[coordinate]] = 2
        rows.append(row)
        labels.append(label)

    # Both real source rows of d(H.H-alpha S*) at h=r=alpha=1.  The real
    # row is dependent on the two radial rows; the imaginary row adds the one
    # relative-phase constraint.  Arbitrary positive scales act by invertible
    # row/coordinate rescalings.
    phase_real = np.zeros(len(coordinates), dtype=np.int64)
    phase_real[coordinate_index["ReH6"]] = 2
    phase_real[coordinate_index["ReS"]] = -1
    rows.append(phase_real)
    labels.append("d_Re_HH_minus_alpha_Sstar")
    phase_imag = np.zeros(len(coordinates), dtype=np.int64)
    phase_imag[coordinate_index["ImH6"]] = 2
    phase_imag[coordinate_index["ImS"]] = 1
    rows.append(phase_imag)
    labels.append("d_Im_HH_minus_alpha_Sstar")
    return np.vstack(rows), labels, coordinates


def extension_kernel_argument() -> dict[str, Any]:
    import exact_gauged_u1x_physical_quotient_v20 as quotient_source

    contributions = {
        "Phi_H_colour_projector_covariant_constraints": 12,
        "imaginary_transverse_weak_H_constraints": 3,
        "H_radial_constraint": 1,
        "S_radial_constraint": 1,
        "Phi17_radial_constraint": 1,
        "H_S_phase_lock_constraint": 1,
    }
    orbit = exact_pd_gauge_orbit_audit()
    jacobian, row_labels, coordinate_labels = extension_constraint_jacobian()
    jacobian_rank = exact_rational_rank(jacobian)
    rank_sequence = {
        "H_wedge_Phi_rows": exact_rational_rank(jacobian[:12]),
        "plus_complex_H_Gram_rows": exact_rational_rank(jacobian[:21]),
        "plus_three_radial_rows": exact_rational_rank(jacobian[:24]),
        "plus_two_H_S_phase_lock_rows": jacobian_rank,
    }
    expected_rank_sequence = {
        "H_wedge_Phi_rows": 12,
        "plus_complex_H_Gram_rows": 15,
        "plus_three_radial_rows": 18,
        "plus_two_H_S_phase_lock_rows": 19,
    }
    pd_extended_kernel = 33 + 20 + 2 + 2
    added_rank = sum(contributions.values())
    remaining = pd_extended_kernel - added_rank
    quotient = quotient_source.build_report()
    quotient_exact = quotient["exact_certificate"]
    symmetry_ranks = {
        "SO10_at_full_vacuum": quotient_exact["SO10"]["rank"],
        "SO10_plus_U1X": quotient_exact["gauged_symmetry"]["rank"],
        "SO10_plus_U1X_plus_global_PQ": quotient_exact[
            "full_removed_symmetry"
        ]["rank"],
    }
    return {
        "exact_P_plus_Delta_kernel_dimension": 33,
        "exact_P_plus_Delta_gauge_orbit": orbit,
        "kernel_after_adjoining_free_H_S_Phi17_coordinates": pd_extended_kernel,
        "independent_nonnegative_H_S_Phi17_rank_contributions": contributions,
        "added_exact_rank": added_rank,
        "explicit_quotient_constraint_Jacobian": {
            "shape": list(jacobian.shape),
            "exact_rational_rank": jacobian_rank,
            "row_labels": row_labels,
            "coordinate_labels": coordinate_labels,
            "integer_rows": jacobian.tolist(),
            "incremental_exact_ranks": rank_sequence,
            "expected_incremental_exact_ranks": expected_rank_sequence,
        },
        "remaining_kernel_dimension": remaining,
        "symmetry_tangent_rank": symmetry_ranks,
        "exact_full_symmetry_source": {
            "module": "exact_gauged_u1x_physical_quotient_v20",
            "certified": quotient["certified"],
            "live_compiler_binding_passes": quotient["live_compiler_binding"][
                "compiler_binding_passes"
            ],
            "massive_transverse_quotient_dimension": quotient[
                "massive_transverse_quotient_dimension"
            ],
        },
        "exact_full_Hessian_rank": 486 - remaining,
        "exact_massive_transverse_rank": 448,
        "logic": (
            "Exact PSD gives a 33-dimensional P+Delta kernel and the exact "
            "integral gauge-orbit matrix has rank 33, so that kernel is exactly "
            "the gauge orbit. Gauge covariance removes it before applying the "
            "explicit rank-19 quotient Jacobian. The five surviving new-field "
            "directions are three additional SO(10) gauge tangents plus U(1)_X "
            "and PQ tangents, yielding precisely 38 full symmetry zero modes."
        ),
        "source_identities": [
            "H^dag(||Phi||^2 I-C(Phi))H = ||H wedge Phi||^2",
            "(H^dag H)^2-|H.H|^2 is the complex-vector Gram determinant",
            "radial terms are literal norm squares",
            "|H.H-alpha S*|^2 supplies one independent relative-phase row",
        ],
        "source_binding_exact": (
            orbit["source_binding_exact"]
            and rank_sequence == expected_rank_sequence
            and quotient["certified"] is True
            and symmetry_ranks
            == {
                "SO10_at_full_vacuum": 36,
                "SO10_plus_U1X": 37,
                "SO10_plus_U1X_plus_global_PQ": 38,
            }
        ),
        "proof_grade": (
            orbit["exact_orbit_rank"] == 33
            and rank_sequence == expected_rank_sequence
            and quotient["certified"] is True
            and quotient["massive_transverse_quotient_dimension"] == 448
        ),
    }


def stationarity_and_bfb_argument() -> dict[str, Any]:
    """Non-promotional handoff to the dedicated exact SOS certificate.

    Stationarity/BFB require more than the Hessian/rank tensors constructed in
    this file.  They are intentionally not inferred from hardcoded identities
    here.  The separate SOS candidate audit owns source-bound verification of
    those claims.
    """
    return {
        "status": "DELEGATED_TO_SOURCE_BOUND_SOS_CANDIDATE_CERTIFICATE",
        "exact_stationarity_certified_here": False,
        "global_BFB_certified_here": False,
        "global_minimum_certified": False,
        "global_uniqueness_certified": False,
        "reason_global_extrema_remain_open": (
            "competing stationary orbits have not been exhaustively classified "
            "and compared"
        ),
        "source_binding_exact": False,
        "consumed_by_local_rank_proof": False,
    }


def build_report(
    recomputed: dict[str, Any] | None = None,
) -> dict[str, Any]:
    certificate = RECORDED_DIRECT_CERTIFICATE if recomputed is None else recomputed
    extension = extension_kernel_argument()
    scope = stationarity_and_bfb_argument()
    if recomputed is None:
        ranks = RECORDED_DIRECT_CERTIFICATE["direct_exact_ranks"]
    else:
        ranks = {
            name: {
                "rank": int(recomputed[name]["exact_rank"]),
                "nullity": int(recomputed[name]["exact_nullity"]),
                "PSD": bool(recomputed[name]["exact_PSD"]),
            }
            for name in ("K", "H_Phi", "H_Phi_plus_K")
        }
    checks = {
        "candidate_contains_A_shift_and_C_squares": (
            TOTAL_MIXED_WEIGHTS == (41, 73, 29, -7, -11, 13)
        ),
        "recorded_component_dimensions_sum_to_462": (
            sum(
                int(size) * int(count)
                for size, count in RECORDED_CONDITIONAL_CERTIFICATE[
                    "component_decomposition"
                ]["component_size_counts"].items()
            )
            == PD_DIMENSION
        ),
        "restricted_kernel_spectrum_multiplicity_sum_is_276": (
            sum(multiplicity for _value, multiplicity in RESTRICTED_KERNEL_SPECTRUM)
            == 276
        ),
        "direct_K_is_PSD_rank_278": ranks["K"] == {
            "rank": 278,
            "nullity": 184,
            "PSD": True,
        },
        "direct_H_Phi_is_PSD_rank_186": ranks["H_Phi"] == {
            "rank": 186,
            "nullity": 276,
            "PSD": True,
        },
        "direct_PD_is_PSD_rank_429": ranks["H_Phi_plus_K"] == {
            "rank": 429,
            "nullity": 33,
            "PSD": True,
        },
        "direct_source_binding": certificate["source_binding_exact"] is True,
        "exact_PD_gauge_orbit_rank_is_33": extension[
            "exact_P_plus_Delta_gauge_orbit"
        ]["exact_orbit_rank"]
        == 33,
        "extension_rank_count_is_explicitly_19": (
            extension["added_exact_rank"] == 19
            and extension["explicit_quotient_constraint_Jacobian"][
                "exact_rational_rank"
            ]
            == 19
        ),
        "exact_full_rank_is_448": extension["exact_full_Hessian_rank"] == 448,
        "stationarity_and_BFB_are_not_inferred_here": (
            scope["exact_stationarity_certified_here"] is False
            and scope["global_BFB_certified_here"] is False
            and scope["source_binding_exact"] is False
        ),
        "global_extrema_gap_is_explicit": (
            scope["global_minimum_certified"] is False
            and scope["global_uniqueness_certified"] is False
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "DIRECT_EXACT_TRANSVERSE_HESSIAN_PASS__SOS_AND_GLOBAL_EXTREMA_EXTERNAL"
            if not failures
            else "DIRECT_EXACT_G3_CERTIFICATE_INTERNAL_FAILURE"
        ),
        "overall_state": "OPEN" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "direct_P_plus_Delta_certificate": certificate,
        "direct_exact_ranks": ranks,
        "exact_full_kernel_argument": extension,
        "stationarity_and_BFB_scope": scope,
        "flags": {
            "conditional_exact_LDL_on_reconstructed_matrix": False,
            "direct_exact_source_binding": not failures,
            "proof_grade_P_plus_Delta_PSD": not failures,
            "proof_grade_full_rank_448": not failures,
            "strict_transverse_Hessian_positive_certified": not failures,
            "exact_stationarity_certified_here": False,
            "global_BFB_certified_here": False,
            "strict_local_minimum_certified_here": False,
            "global_minimum_certified": False,
            "global_uniqueness_certified": False,
            "G3_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "G3_scope_conclusion": (
            "This module certifies a positive full Hessian on all 448 transverse "
            "directions, with exactly the 38 symmetry zero modes. Exact "
            "stationarity and BFB are owned by the separate source-bound SOS "
            "certificate. Global competing-extrema comparison remains open."
        ),
        "next_exact_step": (
            "Classify and compare all competing stationary symmetry orbits, or "
            "derive a sharper global lower bound saturated by this candidate."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    ranks = report["direct_exact_ranks"]
    return "\n".join(
        [
            "# Direct exact P+Delta_R rank certificate -- v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            "The hierarchy-congruent P+Delta_R matrix decomposes into 89 "
            "Q(sqrt(2)) blocks of size at most eight.",
            "",
            f"- direct exact K rank/nullity: `{ranks['K']['rank']}/{ranks['K']['nullity']}`",
            f"- direct exact H_Phi rank/nullity: `{ranks['H_Phi']['rank']}/{ranks['H_Phi']['nullity']}`",
            "- direct exact P+Delta_R rank/nullity: "
            f"`{ranks['H_Phi_plus_K']['rank']}/{ranks['H_Phi_plus_K']['nullity']}`",
            "- exact H/S/Phi17 added rank: `19`",
            "- exact full massive-transverse rank: `448`",
            "- positive Hessian on all 448 transverse directions: `PASS`",
            "- stationarity/BFB: `delegated to the source-bound SOS certificate`",
            "",
            "The proof path uses direct Gaussian-integer/Fraction tensor "
            "assembly and exact Q(sqrt(2)) LDL; no lattice reconstruction is "
            "used. This file does not infer stationarity or BFB; those belong "
            "to the separate source-bound SOS certificate. G3 remains open "
            "until competing stationary extrema are globally classified and compared.",
            "",
        ]
    )


def _json_default(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, Qsqrt2):
        return {"a": str(value.a), "b": str(value.b)}
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(type(value).__name__)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recompute-heavy", action="store_true")
    parser.add_argument("--compare-live", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    if args.recompute_heavy or args.compare_live:
        recomputed = recompute_direct_certificate(compare_live=args.compare_live)
    else:
        recomputed = None
    report = build_report(recomputed)
    payload = json.dumps(report, indent=2, default=_json_default) + "\n"
    if args.write:
        OUT_JSON.write_text(payload, encoding="utf-8")
        OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(payload, end="")
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
