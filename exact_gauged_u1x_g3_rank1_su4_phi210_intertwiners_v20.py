#!/usr/bin/env python3
"""Exact SU(4) intertwiners and carrier census for the rank-one G3 endpoint.

The rank-one endpoint stabilizer fixes the real plane ``(0,1)`` and acts as
``SU(4)`` on the four complex planes ``(2,3),(4,5),(6,7),(8,9)``.  This file
constructs an exact Gaussian-integer change of basis for
``Phi210 = Lambda^4(R^10)`` and proves that it intertwines all fifteen live
stabilizer generators.

In the Gaussian one-form basis the complexified vector branches as

    10_C = 1 + 1 + 4 + 4bar.

An independent semistandard-Young-tableau character calculation then gives

    210_C = 4*1 + 4*4 + 4*4bar + 4*6 + 2*15
            + 10 + 10bar + 2*20 + 2*20bar + 20prime.

The integral, eight-times-standard quadratic Casimir ``C8`` has spectrum

    0^4, 15^32, 20^24, 32^30, 36^20, 39^80, 48^20.

Its split minimal polynomial is checked by exact integer sparse arithmetic.
Modular ranks, together with that annihilating polynomial, certify all seven
eigenspace dimensions over Q.  Finally the sixteen natural exterior blocks
are split by exact Casimir filters into twenty-five deterministic carriers;
their SSYT characters and combined rank 210 prove completeness.

This is representation-theory infrastructure for the proposed SU(4)-Schur
SDP.  It does not construct that SDP, prove an arbitrary-Phi lower bound, or
close G3.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from functools import lru_cache
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy import sparse

import exact_gauged_u1x_g3_rank1_su4_stabilizer_v20 as stabilizer


ROOT = Path(__file__).resolve().parent
OUT_JSON = (
    ROOT
    / "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_INTERTWINERS_V20.json"
)
OUT_MD = (
    ROOT
    / "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_INTERTWINERS_V20.md"
)
EXPECTED_MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
MODEL_CONTRACT_ID = stabilizer.MODEL_CONTRACT_ID
MODULAR_PRIME = 1_000_003

VECTOR_DIMENSION = 10
PHI_DIMENSION = 210
EXTERIOR_DEGREE = 4
CANONICAL_FOUR_STATES = tuple(
    itertools.combinations(range(VECTOR_DIMENSION), EXTERIOR_DEGREE)
)

# The first two states are SU(4) singlets.  The next four are the fundamental
# and the last four its conjugate.  Every column has one-form norm squared 2.
GAUSSIAN_ONE_FORM_LABELS = (
    "z0",
    "z0bar",
    "z1",
    "z2",
    "z3",
    "z4",
    "z1bar",
    "z2bar",
    "z3bar",
    "z4bar",
)
FUNDAMENTAL_WEIGHTS = (
    (1, 0, 0),
    (-1, 1, 0),
    (0, -1, 1),
    (0, 0, -1),
)
ONE_FORM_WEIGHTS = (
    (0, 0, 0),
    (0, 0, 0),
    *FUNDAMENTAL_WEIGHTS,
    *(tuple(-entry for entry in weight) for weight in FUNDAMENTAL_WEIGHTS),
)

# SU(4) Dynkin labels and their canonical GL(4) partitions.  The latter are
# used only by the independent SSYT enumerator below.
IRREP_DATA = {
    "1": {"dynkin": (0, 0, 0), "partition": (), "dimension": 1, "C8": 0},
    "4": {"dynkin": (1, 0, 0), "partition": (1,), "dimension": 4, "C8": 15},
    "4bar": {
        "dynkin": (0, 0, 1),
        "partition": (1, 1, 1),
        "dimension": 4,
        "C8": 15,
    },
    "6": {
        "dynkin": (0, 1, 0),
        "partition": (1, 1),
        "dimension": 6,
        "C8": 20,
    },
    "15": {
        "dynkin": (1, 0, 1),
        "partition": (2, 1, 1),
        "dimension": 15,
        "C8": 32,
    },
    "10": {
        "dynkin": (2, 0, 0),
        "partition": (2,),
        "dimension": 10,
        "C8": 36,
    },
    "10bar": {
        "dynkin": (0, 0, 2),
        "partition": (2, 2, 2),
        "dimension": 10,
        "C8": 36,
    },
    "20": {
        "dynkin": (1, 1, 0),
        "partition": (2, 1),
        "dimension": 20,
        "C8": 39,
    },
    "20bar": {
        "dynkin": (0, 1, 1),
        "partition": (2, 2, 1),
        "dimension": 20,
        "C8": 39,
    },
    "20prime": {
        "dynkin": (0, 2, 0),
        "partition": (2, 2),
        "dimension": 20,
        "C8": 48,
    },
}
EXPECTED_BRANCHING = {
    "1": 4,
    "4": 4,
    "4bar": 4,
    "6": 4,
    "15": 2,
    "10": 1,
    "10bar": 1,
    "20": 2,
    "20bar": 2,
    "20prime": 1,
}
EXPECTED_C8_SPECTRUM = {
    0: 4,
    15: 32,
    20: 24,
    32: 30,
    36: 20,
    39: 80,
    48: 20,
}
C8_ROOTS = tuple(EXPECTED_C8_SPECTRUM)


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, Counter):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def _maximum_abs(matrix: sparse.spmatrix | np.ndarray) -> int:
    if sparse.issparse(matrix):
        return int(np.max(np.abs(matrix.data), initial=0))
    return int(np.max(np.abs(np.asarray(matrix)), initial=0))


def _sparse_is_zero(matrix: sparse.spmatrix) -> bool:
    value = matrix.copy()
    value.eliminate_zeros()
    return value.nnz == 0


def _matrix_sha256(*matrices: sparse.spmatrix | np.ndarray) -> str:
    digest = hashlib.sha256()
    for matrix in matrices:
        dense = (
            matrix.toarray() if sparse.issparse(matrix) else np.asarray(matrix)
        )
        canonical = np.ascontiguousarray(dense, dtype="<i8")
        digest.update(str(canonical.shape).encode("ascii"))
        digest.update(canonical.tobytes())
    return digest.hexdigest()


def _gaussian_add(
    left: tuple[sparse.csr_matrix, sparse.csr_matrix],
    right: tuple[sparse.csr_matrix, sparse.csr_matrix],
) -> tuple[sparse.csr_matrix, sparse.csr_matrix]:
    return (
        (left[0] + right[0]).tocsr(),
        (left[1] + right[1]).tocsr(),
    )


def _gaussian_scale(
    value: tuple[sparse.csr_matrix, sparse.csr_matrix], coefficient: int
) -> tuple[sparse.csr_matrix, sparse.csr_matrix]:
    return (
        (coefficient * value[0]).tocsr(),
        (coefficient * value[1]).tocsr(),
    )


def _gaussian_matmul(
    left: tuple[sparse.csr_matrix, sparse.csr_matrix],
    right: tuple[sparse.csr_matrix, sparse.csr_matrix],
) -> tuple[sparse.csr_matrix, sparse.csr_matrix]:
    return (
        (left[0] @ right[0] - left[1] @ right[1]).tocsr(),
        (left[0] @ right[1] + left[1] @ right[0]).tocsr(),
    )


@lru_cache(maxsize=1)
def gaussian_one_form_basis() -> tuple[np.ndarray, np.ndarray]:
    """Return the exact Gaussian one-form matrix ``U=(Ur+i Ui)``."""
    real = np.zeros((VECTOR_DIMENSION, VECTOR_DIMENSION), dtype=np.int64)
    imaginary = np.zeros_like(real)
    planes = ((0, 1),) + tuple(stabilizer.COMPLEX_PLANES)
    for plane_index, (even, odd) in enumerate(planes):
        plus_column = 0 if plane_index == 0 else 1 + plane_index
        minus_column = 1 if plane_index == 0 else 5 + plane_index
        real[even, plus_column] = 1
        imaginary[odd, plus_column] = 1
        real[even, minus_column] = 1
        imaginary[odd, minus_column] = -1
    return real, imaginary


def _wedge_gaussian_one_forms(
    columns: tuple[int, ...],
) -> dict[tuple[int, ...], tuple[int, int]]:
    one_real, one_imaginary = gaussian_one_form_basis()
    terms: dict[tuple[int, ...], tuple[int, int]] = {(): (1, 0)}
    for column in columns:
        one_terms = tuple(
            (row, int(one_real[row, column]), int(one_imaginary[row, column]))
            for row in range(VECTOR_DIMENSION)
            if one_real[row, column] or one_imaginary[row, column]
        )
        updated: defaultdict[tuple[int, ...], list[int]] = defaultdict(
            lambda: [0, 0]
        )
        for indices, (left_real, left_imaginary) in terms.items():
            for row, right_real, right_imaginary in one_terms:
                if row in indices:
                    continue
                sign = -1 if sum(index > row for index in indices) % 2 else 1
                target = tuple(sorted(indices + (row,)))
                product_real = (
                    left_real * right_real
                    - left_imaginary * right_imaginary
                )
                product_imaginary = (
                    left_real * right_imaginary
                    + left_imaginary * right_real
                )
                updated[target][0] += sign * product_real
                updated[target][1] += sign * product_imaginary
        terms = {
            indices: (parts[0], parts[1])
            for indices, parts in updated.items()
            if parts != [0, 0]
        }
    return terms


@lru_cache(maxsize=1)
def gaussian_exterior_basis(
) -> tuple[sparse.csr_matrix, sparse.csr_matrix]:
    """Gaussian integer ``B: Lambda^4(1+1+4+4bar) -> Phi210_C``."""
    row_index = {
        state: index for index, state in enumerate(CANONICAL_FOUR_STATES)
    }
    real = sparse.lil_matrix(
        (PHI_DIMENSION, PHI_DIMENSION), dtype=np.int64
    )
    imaginary = sparse.lil_matrix(real.shape, dtype=np.int64)
    for column, state in enumerate(CANONICAL_FOUR_STATES):
        for indices, (real_value, imaginary_value) in (
            _wedge_gaussian_one_forms(state).items()
        ):
            row = row_index[indices]
            if real_value:
                real[row, column] = real_value
            if imaginary_value:
                imaginary[row, column] = imaginary_value
    return real.tocsr(), imaginary.tocsr()


def _so10_vector_generator(a: int, b: int) -> np.ndarray:
    result = np.zeros((VECTOR_DIMENSION, VECTOR_DIMENSION), dtype=np.int64)
    result[a, b] = 1
    result[b, a] = -1
    return result


@lru_cache(maxsize=1)
def su4_vector_actions() -> tuple[np.ndarray, ...]:
    output = []
    for definition in stabilizer.su4_generator_definitions():
        matrix = np.zeros(
            (VECTOR_DIMENSION, VECTOR_DIMENSION), dtype=np.int64
        )
        for (a, b), coefficient in definition["so10_coefficients"].items():
            matrix += int(coefficient) * _so10_vector_generator(a, b)
        output.append(matrix)
    if len(output) != 15:
        raise ArithmeticError("SU(4) generator census drifted")
    return tuple(output)


def _action_in_gaussian_one_form_basis(
    action: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    one_real, one_imaginary = gaussian_one_form_basis()
    numerator_real = (
        one_real.T @ action @ one_real
        + one_imaginary.T @ action @ one_imaginary
    )
    numerator_imaginary = (
        one_real.T @ action @ one_imaginary
        - one_imaginary.T @ action @ one_real
    )
    if np.any(numerator_real % 2) or np.any(numerator_imaginary % 2):
        raise ArithmeticError("Gaussian one-form action left the Z[i] lattice")
    return numerator_real // 2, numerator_imaginary // 2


def _exterior_action(
    one_real: np.ndarray, one_imaginary: np.ndarray
) -> tuple[sparse.csr_matrix, sparse.csr_matrix]:
    state_index = {
        state: index for index, state in enumerate(CANONICAL_FOUR_STATES)
    }
    rows: list[int] = []
    columns: list[int] = []
    real_values: list[int] = []
    imaginary_values: list[int] = []
    entries: defaultdict[tuple[int, int], list[int]] = defaultdict(
        lambda: [0, 0]
    )
    for column, state in enumerate(CANONICAL_FOUR_STATES):
        for position, old in enumerate(state):
            for new in range(VECTOR_DIMENSION):
                real_value = int(one_real[new, old])
                imaginary_value = int(one_imaginary[new, old])
                if not real_value and not imaginary_value:
                    continue
                sequence = list(state)
                sequence[position] = new
                if len(set(sequence)) != EXTERIOR_DEGREE:
                    continue
                sign = -1 if sum(
                    sequence[left] > sequence[right]
                    for left in range(EXTERIOR_DEGREE)
                    for right in range(left + 1, EXTERIOR_DEGREE)
                ) % 2 else 1
                row = state_index[tuple(sorted(sequence))]
                entries[(row, column)][0] += sign * real_value
                entries[(row, column)][1] += sign * imaginary_value
    for (row, column), (real_value, imaginary_value) in entries.items():
        if real_value:
            rows.append(row)
            columns.append(column)
            real_values.append(real_value)
            imaginary_values.append(0)
        if imaginary_value:
            rows.append(row)
            columns.append(column)
            real_values.append(0)
            imaginary_values.append(imaginary_value)
    shape = (PHI_DIMENSION, PHI_DIMENSION)
    real = sparse.coo_matrix(
        (real_values, (rows, columns)), shape=shape, dtype=np.int64
    ).tocsr()
    imaginary = sparse.coo_matrix(
        (imaginary_values, (rows, columns)), shape=shape, dtype=np.int64
    ).tocsr()
    real.eliminate_zeros()
    imaginary.eliminate_zeros()
    return real, imaginary


@lru_cache(maxsize=1)
def su4_exterior_actions(
) -> tuple[tuple[sparse.csr_matrix, sparse.csr_matrix], ...]:
    return tuple(
        _exterior_action(*_action_in_gaussian_one_form_basis(action))
        for action in su4_vector_actions()
    )


def exterior_state_weights() -> tuple[tuple[int, int, int], ...]:
    return tuple(
        tuple(sum(ONE_FORM_WEIGHTS[index][axis] for index in state)
              for axis in range(3))
        for state in CANONICAL_FOUR_STATES
    )


@lru_cache(maxsize=None)
def ssyt_character(partition: tuple[int, ...]) -> Counter[tuple[int, int, int]]:
    """Enumerate the exact SU(4) character of a Young diagram by SSYTs."""
    if any(length < 0 for length in partition):
        raise ValueError("partition rows must be nonnegative")
    if any(partition[index] < partition[index + 1]
           for index in range(len(partition) - 1)):
        raise ValueError("partition rows must be weakly decreasing")
    cells = tuple(
        (row, column)
        for row, length in enumerate(partition)
        for column in range(length)
    )
    values: dict[tuple[int, int], int] = {}
    contents: Counter[tuple[int, int, int, int]] = Counter()

    def visit(position: int, counts: list[int]) -> None:
        if position == len(cells):
            contents[tuple(counts)] += 1
            return
        row, column = cells[position]
        lower = 0
        if column:
            lower = max(lower, values[(row, column - 1)])
        if row and column < partition[row - 1]:
            lower = max(lower, values[(row - 1, column)] + 1)
        for entry in range(lower, 4):
            values[(row, column)] = entry
            counts[entry] += 1
            visit(position + 1, counts)
            counts[entry] -= 1
        values.pop((row, column), None)

    visit(0, [0, 0, 0, 0])
    character: Counter[tuple[int, int, int]] = Counter()
    for content, multiplicity in contents.items():
        character[
            (
                content[0] - content[1],
                content[1] - content[2],
                content[2] - content[3],
            )
        ] += multiplicity
    return character


def _scaled_character_sum() -> Counter[tuple[int, int, int]]:
    total: Counter[tuple[int, int, int]] = Counter()
    for name, multiplicity in EXPECTED_BRANCHING.items():
        for weight, count in ssyt_character(
            tuple(IRREP_DATA[name]["partition"])
        ).items():
            total[weight] += multiplicity * count
    return +total


@lru_cache(maxsize=1)
def exact_character_certificate() -> dict[str, Any]:
    observed = Counter(exterior_state_weights())
    reconstructed = _scaled_character_sum()
    multiplicity_histogram = Counter(observed.values())
    irrep_rows = []
    for name, multiplicity in EXPECTED_BRANCHING.items():
        character = ssyt_character(tuple(IRREP_DATA[name]["partition"]))
        irrep_rows.append(
            {
                "irrep": name,
                "dynkin_labels": IRREP_DATA[name]["dynkin"],
                "partition": IRREP_DATA[name]["partition"],
                "SSYT_dimension": sum(character.values()),
                "expected_dimension": IRREP_DATA[name]["dimension"],
                "multiplicity": multiplicity,
                "C8_eigenvalue": IRREP_DATA[name]["C8"],
                "n_distinct_weights": len(character),
            }
        )
    zero = (0, 0, 0)
    return {
        "vector_branching": "10_C = 1 + 1 + 4 + 4bar",
        "Phi210_branching": (
            "4*1 + 4*4 + 4*4bar + 4*6 + 2*15 + 10 + 10bar "
            "+ 2*20 + 2*20bar + 20prime"
        ),
        "exterior_dimension": sum(observed.values()),
        "exterior_distinct_weight_count": len(observed),
        "exterior_zero_weight_multiplicity": observed[zero],
        "exterior_weight_multiplicity_histogram": dict(
            sorted(multiplicity_histogram.items())
        ),
        "SSYT_irreps": irrep_rows,
        "SSYT_reconstructed_dimension": sum(reconstructed.values()),
        "SSYT_character_identity_exact": observed == reconstructed,
        "all_SSYT_dimensions_exact": all(
            row["SSYT_dimension"] == row["expected_dimension"]
            for row in irrep_rows
        ),
        "branching_multiplicities": EXPECTED_BRANCHING,
        "proof_grade": bool(
            sum(observed.values()) == PHI_DIMENSION
            and len(observed) == 65
            and observed[zero] == 12
            and multiplicity_histogram
            == Counter({1: 14, 2: 24, 3: 12, 6: 6, 8: 8, 12: 1})
            and observed == reconstructed
            and all(
                row["SSYT_dimension"] == row["expected_dimension"]
                for row in irrep_rows
            )
        ),
    }


def _cartan_coefficient_matrix() -> np.ndarray:
    # Four times the inverse A3 Cartan matrix.
    return np.asarray(
        ((3, 2, 1), (2, 4, 2), (1, 2, 3)), dtype=np.int64
    )


@lru_cache(maxsize=1)
def integral_c8() -> tuple[sparse.csr_matrix, sparse.csr_matrix]:
    """Eight times the standard SU(4) Casimir in the exterior basis."""
    generators = su4_exterior_actions()
    shape = (PHI_DIMENSION, PHI_DIMENSION)
    zero = sparse.csr_matrix(shape, dtype=np.int64)
    result = (zero.copy(), zero.copy())
    for generator in generators[3:]:
        result = _gaussian_add(
            result,
            _gaussian_scale(_gaussian_matmul(generator, generator), -2),
        )
    cartan_metric = _cartan_coefficient_matrix()
    for left in range(3):
        for right in range(3):
            result = _gaussian_add(
                result,
                _gaussian_scale(
                    _gaussian_matmul(generators[left], generators[right]),
                    -int(cartan_metric[left, right]),
                ),
            )
    result[0].eliminate_zeros()
    result[1].eliminate_zeros()
    return result


@lru_cache(maxsize=1)
def integral_c8_phi210() -> sparse.csr_matrix:
    """The same integral C8 in the live real canonical Phi210 chart."""
    generators = stabilizer.exact_phi210_actions()
    result = sparse.csr_matrix(
        (PHI_DIMENSION, PHI_DIMENSION), dtype=np.int64
    )
    for generator in generators[3:]:
        result = result - 2 * (generator @ generator)
    cartan_metric = _cartan_coefficient_matrix()
    for left in range(3):
        for right in range(3):
            result = result - int(cartan_metric[left, right]) * (
                generators[left] @ generators[right]
            )
    result = result.tocsr()
    result.eliminate_zeros()
    return result


def _rank_mod_prime(matrix: np.ndarray, prime: int = MODULAR_PRIME) -> int:
    work = np.remainder(np.asarray(matrix, dtype=np.int64), prime).copy()
    n_rows, n_columns = work.shape
    pivot_row = 0
    for column in range(n_columns):
        candidates = np.flatnonzero(work[pivot_row:, column])
        if candidates.size == 0:
            continue
        selected = pivot_row + int(candidates[0])
        if selected != pivot_row:
            work[[pivot_row, selected]] = work[[selected, pivot_row]]
        inverse = pow(int(work[pivot_row, column]), -1, prime)
        work[pivot_row] = np.remainder(work[pivot_row] * inverse, prime)
        below = np.flatnonzero(work[pivot_row + 1 :, column]) + pivot_row + 1
        if below.size:
            factors = work[below, column].copy()
            work[below] = np.remainder(
                work[below] - factors[:, None] * work[pivot_row], prime
            )
        pivot_row += 1
        if pivot_row == n_rows:
            break
    return pivot_row


def _independent_columns_mod_prime(
    matrix: np.ndarray, prime: int = MODULAR_PRIME
) -> tuple[int, ...]:
    work = np.remainder(np.asarray(matrix, dtype=np.int64), prime).copy()
    n_rows, n_columns = work.shape
    pivot_row = 0
    pivot_columns: list[int] = []
    for column in range(n_columns):
        candidates = np.flatnonzero(work[pivot_row:, column])
        if candidates.size == 0:
            continue
        selected = pivot_row + int(candidates[0])
        if selected != pivot_row:
            work[[pivot_row, selected]] = work[[selected, pivot_row]]
        inverse = pow(int(work[pivot_row, column]), -1, prime)
        work[pivot_row] = np.remainder(work[pivot_row] * inverse, prime)
        below = np.flatnonzero(work[pivot_row + 1 :, column]) + pivot_row + 1
        if below.size:
            factors = work[below, column].copy()
            work[below] = np.remainder(
                work[below] - factors[:, None] * work[pivot_row], prime
            )
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == n_rows:
            break
    return tuple(pivot_columns)


def _polynomial_coefficients(roots: Iterable[int]) -> tuple[int, ...]:
    coefficients = [1]
    for root in roots:
        updated = [0] * (len(coefficients) + 1)
        for degree, coefficient in enumerate(coefficients):
            updated[degree] -= int(root) * coefficient
            updated[degree + 1] += coefficient
        coefficients = updated
    return tuple(coefficients)


@lru_cache(maxsize=1)
def exact_c8_certificate() -> dict[str, Any]:
    c8_real, c8_imaginary = integral_c8()
    c8_phi = integral_c8_phi210()
    basis_real, basis_imaginary = gaussian_exterior_basis()
    c8_intertwining_real = c8_phi @ basis_real - basis_real @ c8_real
    c8_intertwining_imaginary = c8_phi @ basis_imaginary - basis_imaginary @ c8_real
    identity = sparse.identity(PHI_DIMENSION, dtype=np.int64, format="csr")
    current = identity
    intermediate_maxima = []
    for root in C8_ROOTS:
        current = ((c8_real - root * identity) @ current).tocsr()
        current.eliminate_zeros()
        intermediate_maxima.append(_maximum_abs(current))
    annihilates = _sparse_is_zero(current)

    modular_nullities = {}
    dense_c8 = c8_real.toarray().astype(np.int64)
    for root in C8_ROOTS:
        rank = _rank_mod_prime(
            dense_c8 - root * np.eye(PHI_DIMENSION, dtype=np.int64)
        )
        modular_nullities[root] = PHI_DIMENSION - rank

    commutators_exact = []
    for generator_real, generator_imaginary in su4_exterior_actions():
        commutators_exact.append(
            _sparse_is_zero(c8_real @ generator_real - generator_real @ c8_real)
            and _sparse_is_zero(
                c8_real @ generator_imaginary
                - generator_imaginary @ c8_real
            )
        )
    polynomial = _polynomial_coefficients(C8_ROOTS)
    return {
        "normalization": "C8 = 8 times the standard SU(4) quadratic Casimir",
        "construction": (
            "-2*sum_(12 roots) G^2 - "
            "sum_ij (4*A3_inverse)_ij H_i H_j"
        ),
        "shape": c8_real.shape,
        "integral": True,
        "imaginary_part_zero_exact": _sparse_is_zero(c8_imaginary),
        "symmetric_exact": _sparse_is_zero(c8_real - c8_real.T),
        "maximum_absolute_entry": _maximum_abs(c8_real),
        "exterior_basis_nonzero_entry_count": c8_real.nnz,
        "canonical_Phi210_nonzero_entry_count": c8_phi.nnz,
        "canonical_Phi210_symmetric_exact": _sparse_is_zero(
            c8_phi - c8_phi.T
        ),
        "canonical_to_exterior_C8_intertwining_exact": (
            _sparse_is_zero(c8_intertwining_real)
            and _sparse_is_zero(c8_intertwining_imaginary)
        ),
        "commutes_with_all_15_generators_exact": all(commutators_exact),
        "minimal_polynomial_roots": C8_ROOTS,
        "minimal_polynomial_coefficients_ascending": polynomial,
        "minimal_polynomial_annihilates_exact": annihilates,
        "annihilator_intermediate_maxima": intermediate_maxima,
        "int64_arithmetic_safe": max(intermediate_maxima) < int(
            np.iinfo(np.int64).max
        ),
        "modular_prime": MODULAR_PRIME,
        "modular_eigenspace_nullities": modular_nullities,
        "expected_spectrum_multiplicities": EXPECTED_C8_SPECTRUM,
        "modular_nullities_sum": sum(modular_nullities.values()),
        "spectrum_exact_over_Q": bool(
            annihilates
            and modular_nullities == EXPECTED_C8_SPECTRUM
            and sum(modular_nullities.values()) == PHI_DIMENSION
        ),
        "minimal_polynomial_exact": bool(
            annihilates
            and modular_nullities == EXPECTED_C8_SPECTRUM
            and all(value > 0 for value in modular_nullities.values())
        ),
        "exterior_matrix_sha256": _matrix_sha256(c8_real),
        "canonical_Phi210_matrix_sha256": _matrix_sha256(c8_phi),
        "exact_spectrum_argument": (
            "The split square-free integer annihilator decomposes Q^210 into "
            "the seven rational eigenspaces.  Reduction modulo the recorded "
            "prime gives upper bounds on their rational nullities; those "
            "seven bounds sum to 210, so every bound is attained exactly."
        ),
        "proof_grade": bool(
            _sparse_is_zero(c8_imaginary)
            and _sparse_is_zero(c8_real - c8_real.T)
            and c8_real.nnz == 388
            and c8_phi.nnz == 750
            and _sparse_is_zero(c8_phi - c8_phi.T)
            and _sparse_is_zero(c8_intertwining_real)
            and _sparse_is_zero(c8_intertwining_imaginary)
            and all(commutators_exact)
            and annihilates
            and modular_nullities == EXPECTED_C8_SPECTRUM
            and sum(modular_nullities.values()) == PHI_DIMENSION
        ),
    }


def _natural_block_key(state: tuple[int, ...]) -> tuple[tuple[int, ...], int, int]:
    singlets = tuple(index for index in state if index < 2)
    fundamental = sum(2 <= index < 6 for index in state)
    antifundamental = sum(6 <= index < 10 for index in state)
    return singlets, fundamental, antifundamental


def natural_exterior_blocks() -> dict[
    tuple[tuple[int, ...], int, int], tuple[int, ...]
]:
    blocks: defaultdict[tuple[tuple[int, ...], int, int], list[int]] = defaultdict(list)
    for index, state in enumerate(CANONICAL_FOUR_STATES):
        blocks[_natural_block_key(state)].append(index)
    return {key: tuple(columns) for key, columns in sorted(blocks.items())}


def _carrier_specs() -> tuple[dict[str, Any], ...]:
    specs: list[dict[str, Any]] = []

    def add(
        singlets: tuple[int, ...],
        b: int,
        c: int,
        irreps: tuple[str, ...],
    ) -> None:
        block_name = (
            "none" if not singlets else "_".join(
                GAUSSIAN_ONE_FORM_LABELS[index] for index in singlets
            )
        )
        for irrep in irreps:
            specs.append(
                {
                    "name": f"{block_name}__b{b}_c{c}__{irrep}",
                    "natural_block": (singlets, b, c),
                    "irrep": irrep,
                    "C8": IRREP_DATA[irrep]["C8"],
                    "expected_dimension": IRREP_DATA[irrep]["dimension"],
                    "block_eigenvalues": tuple(
                        dict.fromkeys(IRREP_DATA[name]["C8"] for name in irreps)
                    ),
                }
            )

    add((), 0, 4, ("1",))
    add((), 1, 3, ("10", "6"))
    add((), 2, 2, ("1", "15", "20prime"))
    add((), 3, 1, ("10bar", "6"))
    add((), 4, 0, ("1",))
    for singlet in ((0,), (1,)):
        add(singlet, 0, 3, ("4",))
        add(singlet, 1, 2, ("4bar", "20"))
        add(singlet, 2, 1, ("4", "20bar"))
        add(singlet, 3, 0, ("4bar",))
    add((0, 1), 0, 2, ("6",))
    add((0, 1), 1, 1, ("1", "15"))
    add((0, 1), 2, 0, ("6",))
    return tuple(specs)


def _filtered_block(
    columns: tuple[int, ...], eigenvalue: int, block_eigenvalues: tuple[int, ...]
) -> sparse.csr_matrix:
    identity = sparse.identity(PHI_DIMENSION, dtype=np.int64, format="csr")
    selector = sparse.csc_matrix(
        (
            np.ones(len(columns), dtype=np.int64),
            (np.asarray(columns), np.arange(len(columns))),
        ),
        shape=(PHI_DIMENSION, len(columns)),
        dtype=np.int64,
    ).tocsr()
    result = selector
    c8_real, c8_imaginary = integral_c8()
    if not _sparse_is_zero(c8_imaginary):
        raise ArithmeticError("C8 unexpectedly acquired an imaginary part")
    for other in block_eigenvalues:
        if other != eigenvalue:
            result = ((c8_real - other * identity) @ result).tocsr()
    result.eliminate_zeros()
    return result


@lru_cache(maxsize=1)
def exact_carrier_certificate() -> dict[str, Any]:
    blocks = natural_exterior_blocks()
    block_id = {
        column: key for key, columns in blocks.items() for column in columns
    }
    natural_invariance = True
    for generator in su4_exterior_actions():
        for part in generator:
            coo = part.tocoo()
            if any(block_id[int(row)] != block_id[int(column)]
                   for row, column in zip(coo.row, coo.col, strict=True)):
                natural_invariance = False
                break

    c8_real, _ = integral_c8()
    identity = sparse.identity(PHI_DIMENSION, dtype=np.int64, format="csr")
    weights = exterior_state_weights()
    carriers = []
    carrier_bases: list[sparse.csr_matrix] = []
    observed_multiplicities: Counter[str] = Counter()
    for spec in _carrier_specs():
        columns = blocks[spec["natural_block"]]
        filtered = _filtered_block(
            columns, int(spec["C8"]), tuple(spec["block_eigenvalues"])
        )
        dense = filtered.toarray().astype(np.int64)
        pivots = _independent_columns_mod_prime(dense)
        basis = filtered[:, pivots].tocsr()
        carrier_bases.append(basis)
        dimension = len(pivots)
        eigen_residual = (c8_real - int(spec["C8"]) * identity) @ basis

        weight_multiplicities: Counter[tuple[int, int, int]] = Counter()
        for weight in sorted(set(weights[index] for index in columns)):
            local_columns = tuple(
                local for local, global_column in enumerate(columns)
                if weights[global_column] == weight
            )
            weight_multiplicities[weight] = _rank_mod_prime(
                dense[:, local_columns]
            )
        weight_multiplicities = +weight_multiplicities
        expected_character = ssyt_character(
            tuple(IRREP_DATA[spec["irrep"]]["partition"])
        )
        observed_multiplicities[spec["irrep"]] += 1
        carriers.append(
            {
                "name": spec["name"],
                "natural_block": spec["natural_block"],
                "natural_block_dimension": len(columns),
                "irrep": spec["irrep"],
                "C8_eigenvalue": spec["C8"],
                "expected_dimension": spec["expected_dimension"],
                "exact_modular_rank": dimension,
                "C8_eigen_equation_exact": _sparse_is_zero(eigen_residual),
                "SSYT_character_exact": (
                    weight_multiplicities == expected_character
                ),
                "n_distinct_weights": len(weight_multiplicities),
                "basis_maximum_absolute_entry": _maximum_abs(basis),
                "basis_sha256": _matrix_sha256(basis),
            }
        )

    complete_basis = sparse.hstack(carrier_bases, format="csr")
    complete_rank = _rank_mod_prime(complete_basis.toarray())
    all_rows_exact = all(
        row["exact_modular_rank"] == row["expected_dimension"]
        and row["C8_eigen_equation_exact"]
        and row["SSYT_character_exact"]
        for row in carriers
    )

    # For a real SU(4) representation: the self-conjugate carriers contribute
    # m(m+1)/2 symmetric pairings, while complex-conjugate carrier families
    # contribute m_R*m_Rbar.  All listed self-conjugate types have symmetric
    # invariant forms.
    self_conjugate = ("1", "6", "15", "20prime")
    symmetric_self_pairings = sum(
        observed_multiplicities[name]
        * (observed_multiplicities[name] + 1)
        // 2
        for name in self_conjugate
    )
    conjugate_pairings = (
        observed_multiplicities["4"] * observed_multiplicities["4bar"]
        + observed_multiplicities["10"]
        * observed_multiplicities["10bar"]
        + observed_multiplicities["20"]
        * observed_multiplicities["20bar"]
    )
    invariant_symmetric_square_dimension = (
        symmetric_self_pairings + conjugate_pairings
    )
    return {
        "natural_exterior_block_count": len(blocks),
        "natural_exterior_block_dimensions": sorted(
            len(columns) for columns in blocks.values()
        ),
        "all_15_generators_preserve_natural_blocks_exact": natural_invariance,
        "carrier_count": len(carriers),
        "carriers": carriers,
        "observed_irrep_multiplicities": dict(observed_multiplicities),
        "expected_irrep_multiplicities": EXPECTED_BRANCHING,
        "concatenated_carrier_shape": complete_basis.shape,
        "concatenated_carrier_rank_mod_prime": complete_rank,
        "concatenated_carrier_sha256": _matrix_sha256(complete_basis),
        "all_carrier_dimensions_eigenvalues_characters_exact": all_rows_exact,
        "symmetric_self_conjugate_pairings": symmetric_self_pairings,
        "complex_conjugate_pairings": conjugate_pairings,
        "Sym2_Phi210_SU4_singlet_dimension": (
            invariant_symmetric_square_dimension
        ),
        "real_representation_decomposition": (
            "4*1_R + 4*6_R + 2*15_R + 20prime_R + "
            "4*(4_C)_R + (10_C)_R + 2*(20_C)_R"
        ),
        "exact_carrier_rank_argument": (
            "Each denominator-free C8 filter acts inside one invariant, "
            "multiplicity-free exterior block.  Its weightwise modular ranks "
            "equal the corresponding irreducible SSYT character; the 25 "
            "filtered images concatenate to modular rank 210."
        ),
        "SU4_invariant_quadratic_multiplicity_sector_dimension": 45,
        "proof_grade": bool(
            natural_invariance
            and len(blocks) == 16
            and len(carriers) == 25
            and all_rows_exact
            and observed_multiplicities == Counter(EXPECTED_BRANCHING)
            and complete_basis.shape == (PHI_DIMENSION, PHI_DIMENSION)
            and complete_rank == PHI_DIMENSION
            and invariant_symmetric_square_dimension == 45
        ),
    }


@lru_cache(maxsize=1)
def exact_intertwiner_certificate() -> dict[str, Any]:
    one_real, one_imaginary = gaussian_one_form_basis()
    one_gram_real = one_real.T @ one_real + one_imaginary.T @ one_imaginary
    one_gram_imaginary = (
        one_real.T @ one_imaginary - one_imaginary.T @ one_real
    )
    basis_real, basis_imaginary = gaussian_exterior_basis()
    gram_real = basis_real.T @ basis_real + basis_imaginary.T @ basis_imaginary
    gram_imaginary = (
        basis_real.T @ basis_imaginary - basis_imaginary.T @ basis_real
    )

    phi_actions = stabilizer.exact_phi210_actions()
    exterior_actions = su4_exterior_actions()
    intertwinings = []
    for label, phi_action, exterior_action in zip(
        stabilizer.SU4_LABELS, phi_actions, exterior_actions, strict=True
    ):
        left = (
            (phi_action @ basis_real).tocsr(),
            (phi_action @ basis_imaginary).tocsr(),
        )
        right = _gaussian_matmul(
            (basis_real, basis_imaginary), exterior_action
        )
        residual = (left[0] - right[0], left[1] - right[1])
        intertwinings.append(
            {
                "generator": label,
                "real_residual_max_abs": _maximum_abs(residual[0]),
                "imaginary_residual_max_abs": _maximum_abs(residual[1]),
                "exact": _sparse_is_zero(residual[0])
                and _sparse_is_zero(residual[1]),
            }
        )

    weights = exterior_state_weights()
    cartan_exact = []
    for axis, (real, imaginary) in enumerate(exterior_actions[:3]):
        expected = sparse.diags(
            [weight[axis] for weight in weights],
            dtype=np.int64,
            format="csr",
        )
        cartan_exact.append(
            _sparse_is_zero(real)
            and _sparse_is_zero(imaginary - expected)
        )
    identity10 = np.eye(VECTOR_DIMENSION, dtype=np.int64)
    identity210 = sparse.identity(
        PHI_DIMENSION, dtype=np.int64, format="csr"
    )
    return {
        "one_form_labels": GAUSSIAN_ONE_FORM_LABELS,
        "one_form_definitions": (
            "z0=e0+i e1, z0bar=e0-i e1, "
            "zj=e_(2j)+i e_(2j+1), zjbar=conjugate(zj), j=1..4"
        ),
        "one_form_branching": "1 + 1 + 4 + 4bar",
        "one_form_Gram_real_exact": np.array_equal(
            one_gram_real, 2 * identity10
        ),
        "one_form_Gram_imaginary_zero_exact": not np.any(
            one_gram_imaginary
        ),
        "exterior_basis_shape": basis_real.shape,
        "exterior_basis_real_nnz": basis_real.nnz,
        "exterior_basis_imaginary_nnz": basis_imaginary.nnz,
        "exterior_basis_Bdagger_B_equals_16I_exact": (
            _sparse_is_zero(gram_real - 16 * identity210)
            and _sparse_is_zero(gram_imaginary)
        ),
        "exterior_basis_sha256": _matrix_sha256(
            basis_real, basis_imaginary
        ),
        "intertwining_convention": "G_Phi B = B G_Lambda4",
        "intertwining_count": len(intertwinings),
        "intertwinings": intertwinings,
        "all_15_intertwinings_exact": all(
            row["exact"] for row in intertwinings
        ),
        "Cartan_convention": (
            "H_k acts as i times the recorded Dynkin-weight coordinate"
        ),
        "Cartan_weight_diagonalization_exact": all(cartan_exact),
        "n_distinct_Cartan_weights": len(set(weights)),
        "zero_weight_multiplicity": Counter(weights)[(0, 0, 0)],
        "proof_grade": bool(
            np.array_equal(one_gram_real, 2 * identity10)
            and not np.any(one_gram_imaginary)
            and _sparse_is_zero(gram_real - 16 * identity210)
            and _sparse_is_zero(gram_imaginary)
            and len(intertwinings) == 15
            and all(row["exact"] for row in intertwinings)
            and all(cartan_exact)
            and len(set(weights)) == 65
            and Counter(weights)[(0, 0, 0)] == 12
        ),
    }


def _nested_get(value: dict[str, Any], *keys: str) -> Any:
    current: Any = value
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def _build_report_from_certificates(
    *,
    companion_model_contract_id: str,
    companion_report: dict[str, Any],
    companion_tangent: dict[str, Any],
    companion_phi210: dict[str, Any],
    intertwiner: dict[str, Any],
    character: dict[str, Any],
    c8: dict[str, Any],
    carriers: dict[str, Any],
) -> dict[str, Any]:
    """Assemble fail-closed against the live endpoint/stabilizer provenance."""
    contract_exact = bool(
        MODEL_CONTRACT_ID == EXPECTED_MODEL_CONTRACT_ID
        and companion_model_contract_id == MODEL_CONTRACT_ID
        and companion_report.get("model_contract_id") == MODEL_CONTRACT_ID
    )
    companion_scope_exact = bool(
        companion_report.get("n_failed") == 0
        and companion_report.get("n_checks") == 8
        and len(companion_report.get("checks", {})) == 8
        and companion_report.get("status") == stabilizer.STATUS
        and companion_report.get("overall_state")
        == stabilizer.OVERALL_STATE
        and all(companion_report.get("checks", {}).values())
        and _nested_get(companion_report, "scope", "infrastructure_only")
        is True
        and _nested_get(companion_report, "scope", "H_fixed_to_h_minus")
        is True
        and _nested_get(
            companion_report,
            "scope",
            "Sigma_fixed_to_normalized_explicit_decomposable_pure_spinor_q_over_4",
        )
        is True
        and _nested_get(
            companion_report,
            "scope",
            "common_continuous_stabilizer_identified_as_SU4",
        )
        is True
        and _nested_get(
            companion_report,
            "scope",
            "exact_Phi210_SU4_action_available_for_next_stage",
        )
        is True
    )
    tangent_provenance_exact = bool(
        companion_tangent.get("proof_grade") is True
        and _nested_get(companion_tangent, "fixed_endpoint", "H")
        == "h_-=(e0-i e1)/sqrt(2)"
        and _nested_get(companion_tangent, "fixed_endpoint", "Sigma")
        == "q/4"
        and _nested_get(
            companion_tangent, "fixed_endpoint", "endpoint_binding_exact"
        )
        is True
        and _nested_get(
            companion_tangent,
            "fixed_endpoint",
            "H_numerator_norm_squared",
        )
        == 2
        and _nested_get(
            companion_tangent,
            "fixed_endpoint",
            "q_coordinate_norm_squared",
        )
        == 16
        and _nested_get(
            companion_tangent,
            "source_actions",
            "H_generators_integral_real_skew",
        )
        is True
        and _nested_get(
            companion_tangent,
            "source_actions",
            "Sigma_generators_Gaussian_integral_antihermitian",
        )
        is True
        and _nested_get(
            companion_tangent,
            "source_actions",
            "ordered_generator_labels_match_exactly",
        )
        is True
        and companion_tangent.get("exact_tangent_rank_over_Q_R") == 30
        and companion_tangent.get("exact_tangent_nullity") == 15
        and companion_tangent.get("explicit_kernel_is_complete") is True
    )
    phi210_provenance_exact = bool(
        companion_phi210.get("proof_grade") is True
        and companion_phi210.get("representation")
        == "real Lambda^4(R^10) = Phi210"
        and companion_phi210.get("ordered_labels") == stabilizer.SU4_LABELS
        and companion_phi210.get("action_count") == 15
        and companion_phi210.get("all_action_dtypes_integral") is True
        and companion_phi210.get("skew_transpose_max_abs_residual") == 0
        and companion_phi210.get("flattened_action_rank_mod_prime") == 15
        and companion_phi210.get("Lie_commutator_reconstruction_max_abs")
        == 0
    )
    embedded_certificates_match = bool(
        companion_report.get("joint_stabilizer_tangent")
        == companion_tangent
        and companion_report.get("Phi210_action") == companion_phi210
    )
    checks = {
        "companion_model_contract_matches_exactly": contract_exact,
        "companion_stabilizer_report_green_and_endpoint_scoped": (
            companion_scope_exact
        ),
        "companion_h_minus_q_over_4_tangent_provenance_exact": (
            tangent_provenance_exact
        ),
        "companion_Phi210_action_provenance_exact": phi210_provenance_exact,
        "companion_embedded_certificates_match_live_inputs": (
            embedded_certificates_match
        ),
        "Gaussian_exterior_basis_Bdagger_B_equals_16I_exact": intertwiner[
            "proof_grade"
        ]
        and intertwiner["exterior_basis_shape"] == (210, 210)
        and intertwiner["exterior_basis_Bdagger_B_equals_16I_exact"],
        "all_15_live_SU4_intertwinings_exact": bool(
            intertwiner["proof_grade"]
            and intertwiner["intertwining_count"] == 15
            and len(intertwiner["intertwinings"]) == 15
            and all(row["exact"] for row in intertwiner["intertwinings"])
            and intertwiner["all_15_intertwinings_exact"]
        ),
        "Cartan_weights_exact": bool(
            intertwiner["proof_grade"]
            and intertwiner["Cartan_weight_diagonalization_exact"]
            and intertwiner["n_distinct_Cartan_weights"] == 65
            and intertwiner["zero_weight_multiplicity"] == 12
        ),
        "SSYT_character_branching_exact": character["proof_grade"],
        "integral_C8_spectrum_and_minimal_polynomial_exact": c8[
            "proof_grade"
        ],
        "deterministic_25_carrier_decomposition_complete": carriers[
            "proof_grade"
        ],
        "Sym2_invariant_multiplicity_is_45_exact": (
            carriers["Sym2_Phi210_SU4_singlet_dimension"] == 45
        ),
        "arbitrary_Phi_bound_proved": False,
        "SU4_Schur_SDP_constructed": False,
        "G3_closed": False,
    }
    open_checks = {
        "arbitrary_Phi_bound_proved",
        "SU4_Schur_SDP_constructed",
        "G3_closed",
    }
    failures = [
        name for name, passed in checks.items()
        if name not in open_checks and not passed
    ]
    companion_ready = bool(
        contract_exact
        and companion_scope_exact
        and tangent_provenance_exact
        and phi210_provenance_exact
        and embedded_certificates_match
    )
    return {
        "status": (
            "EXACT_RANK1_SU4_PHI210_INTERTWINER_INFRASTRUCTURE_CERTIFIED"
            if not failures
            else "RANK1_SU4_PHI210_INTERTWINER_EXECUTION_FAILED"
        ),
        "overall_state": (
            "SU4_SCHUR_INFRASTRUCTURE_CLOSED__SDP_AND_G3_OPEN"
            if not failures
            else "EXECUTION_FAIL"
        ),
        "model_contract_id": MODEL_CONTRACT_ID,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "companion_stabilizer_provenance": {
            "module": (
                "exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py"
            ),
            "model_contract_id": companion_model_contract_id,
            "status": companion_report.get("status"),
            "overall_state": companion_report.get("overall_state"),
            "n_failed": companion_report.get("n_failed"),
            "fixed_endpoint": companion_tangent.get("fixed_endpoint"),
            "tangent_proof_grade": companion_tangent.get("proof_grade"),
            "Phi210_action_proof_grade": companion_phi210.get(
                "proof_grade"
            ),
            "all_required_provenance_exact": companion_ready,
        },
        "intertwiner": intertwiner,
        "character_branching": character,
        "integral_C8": c8,
        "carriers": carriers,
        "scope": {
            "H_fixed_to_h_minus": companion_ready,
            "Sigma_fixed_to_q_over_4": companion_ready,
            "rank1_endpoint_SU4_stabilizer_used": companion_ready,
            "companion_stabilizer_provenance_exact": companion_ready,
            "Phi210_complexified_representation_resolved": not failures,
            "deterministic_irreducible_carriers_complete": not failures,
            "Sym2_SU4_invariant_dimension_45_proved": not failures,
            "SU4_invariant_quadratic_form_basis_constructed": False,
            "Schur_SOS_SDP_constructed": False,
            "arbitrary_real_Phi_lower_bound_proved": False,
            "arbitrary_rank1_Phi_proved": False,
            "G3_closed": False,
            "whole_model_excluded": False,
        },
        "next_exact_target": (
            "Construct the full augmented SU(4)-equivariant degree-2 "
            "Schur/SOS SDP with every real/Hermitian isotypic block and all "
            "homogenizing cross terms; the certified 45-dimensional "
            "quadratic invariant sector is only one input. Then rationalize "
            "any feasible certificate and verify every block by exact LDL."
        ),
        "verdict": (
            "The exact rank-one SU(4) representation infrastructure is "
            "complete: B dagger B=16I, all fifteen live intertwinings, the "
            "SSYT branching, integral C8 spectrum/minimal polynomial, and "
            "twenty-five carriers of total rank 210 are certified.  This "
            "proves the 45-dimensional symmetric multiplicity census only; "
            "the SDP, an arbitrary-Phi bound, and G3 remain open."
        ),
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    companion_report = stabilizer.build_report()
    companion_tangent = stabilizer.exact_stabilizer_tangent_certificate()
    companion_phi210 = stabilizer.exact_phi210_action_certificate()
    return _build_report_from_certificates(
        companion_model_contract_id=stabilizer.MODEL_CONTRACT_ID,
        companion_report=companion_report,
        companion_tangent=companion_tangent,
        companion_phi210=companion_phi210,
        intertwiner=exact_intertwiner_certificate(),
        character=exact_character_certificate(),
        c8=exact_c8_certificate(),
        carriers=exact_carrier_certificate(),
    )


def render_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Exact rank-one SU(4) Phi210 intertwiners -- v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "- Gaussian exterior basis: `B^dagger B = 16 I_210`;",
            "- live stabilizer intertwinings: `15/15` exact;",
            "- branching: `4*1 + 4*4 + 4*4bar + 4*6 + 2*15 + 10 "
            "+ 10bar + 2*20 + 2*20bar + 20prime`;",
            "- integral C8 spectrum: `0^4, 15^32, 20^24, 32^30, "
            "36^20, 39^80, 48^20`;",
            "- deterministic carriers: `25`, combined exact rank `210`;",
            "- `dim Sym^2(Phi210)^SU(4) = 45`;",
            "- SU(4)-Schur SDP: `OPEN`;",
            "- arbitrary-Phi lower bound: `OPEN`;",
            "- G3: `OPEN`.",
            "",
            f"**Next:** {report['next_exact_target']}",
            "",
        ]
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(
        json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(_jsonable(report), indent=2, sort_keys=True))
    return int(report["n_failed"] != 0)


if __name__ == "__main__":
    raise SystemExit(main())
