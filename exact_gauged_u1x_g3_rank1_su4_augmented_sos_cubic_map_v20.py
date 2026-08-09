#!/usr/bin/env python3
"""Exact full cubic Schur interface at the rank-one SU(4) endpoint.

The augmented degree-two Gram representation is

    Sym^2(R*t (+) Phi210) = <t^2> (+) t*Phi210 (+) Sym^2(Phi210).

This module constructs the complete off-diagonal cubic interface between
``t*Phi210`` and ``Sym^2(Phi210)``.  It is not a dimension-only argument:
all 1,414 invariant cross tensors are built exactly, realified with the live
physical conjugation, multiplied in the symmetric algebra (including the
factor two from an off-diagonal symmetric Gram block), and restricted to a
deterministic 478-coordinate chart on the abstract invariant cubic coefficient
space.

The construction uses only integer/rational representation data.  Exact
highest-weight kernels in ``Sym^2(Phi210)`` supply every required carrier;
the frozen common lowering words align them with the Phi210 carriers.
Primitive contragredient pairings give the complexified invariant tensors.
The physical antilinear real structure then gives an explicit 1,414-element
real basis.  The resulting sparse integer matrix has shape 478 by 1,414,
rank 478 modulo a safe prime, and hence rank 478 over Q and R.  The exact
kernel dimension is 936.  Its right-hand side for the G3 gap's cubic sector
is not constructed here.  The module exposes an exact zero vector of length
478 only as an abstract reserved interface placeholder; it is not a physical
G3 target and certifies no physical cubic-zero statement.

This closes only the cubic coefficient-map interface.  It does not construct
the remaining degree-zero, -one, -two, or -four coefficient maps, the full
PSD Schur/SOS feasibility problem, the physical G3 target vector, an
arbitrary-Phi lower bound, or G3.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import copy
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
from scipy import sparse

import exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20 as aligned
import exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20 as census
import exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20 as intertwiners
import exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20 as quadratics


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.json"
OUT_MD = ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.md"

MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
STATUS = "EXACT_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_CERTIFIED"
OVERALL_STATE = "SU4_AUGMENTED_CUBIC_MAP_CLOSED__FULL_SDP_AND_G3_OPEN"

PHI_DIMENSION = 210
SYMMETRIC_SQUARE_DIMENSION = 22_155
COMPLEX_CUBIC_DOMAIN_DIMENSION = 1_414
REAL_CUBIC_DOMAIN_DIMENSION = 1_414
CUBIC_TARGET_DIMENSION = 478
CUBIC_KERNEL_DIMENSION = 936
WEIGHT_ZERO_DOMAIN_COORDINATE_COUNT = 65_474
WEIGHT_ZERO_CUBIC_MONOMIAL_COUNT = 21_910
MODULAR_PRIME = 1_000_003
INT64_MAX = int(np.iinfo(np.int64).max)
GRAM_CROSS_MULTIPLIER = 2

EXPECTED_CENSUS_MODULE = (
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py"
)
EXPECTED_ALIGNED_MODULE = (
    "exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py"
)
EXPECTED_INTERTWINER_MODULE = (
    "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py"
)
EXPECTED_QUADRATIC_MODULE = (
    "exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py"
)

# Filled from the frozen, independently audited dependency chain.  These
# values are intentionally fail-closed; a dependency change requires a fresh
# exact regeneration and audit of this module.
EXPECTED_CENSUS_SOURCE_SHA256 = (
    "3e0d7f2eac73eec950960f1ffd78c9584a4b15d070c84889080cf4c67d5a4d63"
)
EXPECTED_CENSUS_REPORT_SHA256 = (
    "703a3819fea5afe857757082190f9cf1e22f283ab0ddcc882c2f011b65ba58f3"
)
EXPECTED_ALIGNED_SOURCE_SHA256 = (
    "5671857444bda7d53db45393e28a3b9ac0784d0f2a63aa1e541eb5e356d23ccc"
)
EXPECTED_INTERTWINER_SOURCE_SHA256 = (
    "76fa77c99b8d6e963e8694acf74280de29ced4c7a7623bffa991aead77329f49"
)
EXPECTED_QUADRATIC_SOURCE_SHA256 = (
    "4eec63ba40b888de736c84f607019ba0f21915028b423578502893744bab1060"
)
EXPECTED_QUADRATIC_REPORT_SHA256 = (
    "497a8c1db29e7d88f30bd1cc68902cc7981da4a3fefd5586bd15bad323d1e259"
)
EXPECTED_QUADRATIC_BASIS_SHA256 = (
    "27c0649758c87aa2cbe39ae04596f4bd6df511ba3ca4004013bdcf936599b694"
)
EXPECTED_CENSUS_STATUS = (
    "EXACT_RANK1_SU4_AUGMENTED_SOS_CENSUS_AND_UNIVERSAL_MAP_CERTIFIED"
)
EXPECTED_CENSUS_OVERALL_STATE = (
    "SU4_AUGMENTED_SOS_CENSUS_CLOSED__SCHUR_EMBEDDINGS_SDP_AND_G3_OPEN"
)
EXPECTED_ALIGNED_STATUS = (
    "EXACT_RANK1_SU4_ALIGNED_CARRIER_INFRASTRUCTURE_CERTIFIED"
)

IRREP_ORDER = (
    "1",
    "4",
    "4bar",
    "6",
    "10",
    "10bar",
    "20",
    "20bar",
    "20prime",
    "15",
)
CONJUGATE_IRREP = {
    "1": "1",
    "4": "4bar",
    "4bar": "4",
    "6": "6",
    "10": "10bar",
    "10bar": "10",
    "20": "20bar",
    "20bar": "20",
    "20prime": "20prime",
    "15": "15",
}
EXPECTED_PHI_MULTIPLICITY = {
    "1": 4,
    "4": 4,
    "4bar": 4,
    "6": 4,
    "10": 1,
    "10bar": 1,
    "20": 2,
    "20bar": 2,
    "20prime": 1,
    "15": 2,
}
EXPECTED_SYM2_MULTIPLICITY = {
    "1": 45,
    "4": 60,
    "4bar": 60,
    "6": 62,
    "10": 39,
    "10bar": 39,
    "20": 62,
    "20bar": 62,
    "20prime": 42,
    "15": 69,
}
EXPECTED_COMPLEX_DOMAIN_COUNTS = {
    "1": 180,
    "4": 240,
    "4bar": 240,
    "6": 248,
    "10": 39,
    "10bar": 39,
    "20": 124,
    "20bar": 124,
    "20prime": 42,
    "15": 138,
}
EXPECTED_REAL_BLOCK_COUNTS = {
    (0, 0, 0): 180,
    (0, 0, 1): 480,
    (0, 0, 2): 78,
    (0, 1, 0): 248,
    (0, 1, 1): 248,
    (0, 2, 0): 42,
    (1, 0, 1): 138,
}
EXPECTED_HIGHEST_CONSTRAINTS = {
    "1": ((744, 551), 1_662),
    "4": ((438, 404), 1_030),
    "4bar": ((438, 404), 1_030),
    "6": ((400, 370), 910),
    "10": ((147, 165), 332),
    "10bar": ((147, 165), 332),
    "20": ((134, 182), 336),
    "20bar": ((134, 182), 336),
    "20prime": ((91, 117), 200),
    "15": ((201, 248), 508),
}

SIMPLE_ROOTS = (
    (2, -1, 0),
    (-1, 2, -1),
    (0, -1, 2),
)

DynkinWeight = tuple[int, int, int]
SparseVector = dict[int, int]
RationalMatrix = tuple[np.ndarray, int]


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, Counter):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    return value


def _file_sha256(path: Path) -> str:
    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def _canonical_json_sha256(value: Any) -> str:
    payload = json.dumps(
        _jsonable(value), ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def _sparse_matrix_sha256(matrix: sparse.spmatrix) -> str:
    value = matrix.tocsr(copy=True)
    value.sum_duplicates()
    value.sort_indices()
    value.eliminate_zeros()
    digest = hashlib.sha256()
    digest.update(np.asarray(value.shape, dtype="<i8").tobytes())
    digest.update(np.asarray(value.indptr, dtype="<i8").tobytes())
    digest.update(np.asarray(value.indices, dtype="<i8").tobytes())
    digest.update(np.asarray(value.data, dtype="<i8").tobytes())
    return digest.hexdigest()


def _sparse_vector_sha256(vector: Mapping[int, int]) -> str:
    digest = hashlib.sha256()
    for coordinate, coefficient in sorted(vector.items()):
        digest.update(int(coordinate).to_bytes(8, "little", signed=False))
        digest.update(int(coefficient).to_bytes(8, "little", signed=True))
    return digest.hexdigest()


def _maximum_abs(matrix: sparse.spmatrix | np.ndarray) -> int:
    values = matrix.data if sparse.issparse(matrix) else np.asarray(matrix).reshape(-1)
    return max((abs(int(value)) for value in values), default=0)


def _matmul_bound(
    left: sparse.spmatrix | np.ndarray,
    right: sparse.spmatrix | np.ndarray,
) -> int:
    if left.shape[1] != right.shape[0]:
        raise ValueError("incompatible exact matrix product")
    return int(left.shape[1]) * _maximum_abs(left) * _maximum_abs(right)


def _checked_sparse_matmul(
    left: sparse.spmatrix,
    right: sparse.spmatrix,
    context: str,
    *,
    left_maximum: int | None = None,
    right_maximum: int | None = None,
) -> sparse.csr_matrix:
    if left.shape[1] != right.shape[0]:
        raise ValueError(f"{context} has incompatible shapes")
    left_bound = (
        _maximum_abs(left) if left_maximum is None else int(left_maximum)
    )
    right_bound = (
        _maximum_abs(right) if right_maximum is None else int(right_maximum)
    )
    if left_bound < 0 or right_bound < 0:
        raise ValueError("precomputed matrix maxima cannot be negative")
    bound = int(left.shape[1]) * left_bound * right_bound
    if bound > INT64_MAX:
        raise ArithmeticError(f"{context} exceeds signed-int64 safety")
    result = (left.astype(np.int64) @ right.astype(np.int64)).tocsr()
    result.sum_duplicates()
    result.eliminate_zeros()
    if result.dtype != np.int64:
        raise ArithmeticError(f"{context} lost exact int64 storage")
    return result


def _checked_dense_matmul(
    left: np.ndarray, right: np.ndarray, context: str
) -> np.ndarray:
    left = np.asarray(left, dtype=np.int64)
    right = np.asarray(right, dtype=np.int64)
    if _matmul_bound(left, right) > INT64_MAX:
        exact = np.asarray(left, dtype=object) @ np.asarray(right, dtype=object)
        values = [int(value) for value in exact.reshape(-1)]
        if any(abs(value) > INT64_MAX for value in values):
            raise ArithmeticError(f"{context} result exceeds signed-int64")
        return np.asarray(values, dtype=np.int64).reshape(exact.shape)
    return left @ right


def _primitive_sparse_vector(vector: Mapping[int, int]) -> tuple[SparseVector, int, int]:
    compact = {int(key): int(value) for key, value in vector.items() if value}
    if not compact:
        return {}, 1, 1
    content = 0
    for value in compact.values():
        content = math.gcd(content, abs(value))
    sign = -1 if compact[min(compact)] < 0 else 1
    return (
        {key: sign * value // content for key, value in compact.items()},
        content,
        sign,
    )


def _combine_sparse_vectors(
    left: Mapping[int, int], right: Mapping[int, int], right_scale: int
) -> SparseVector:
    output = {int(key): int(value) for key, value in left.items() if value}
    for key, value in right.items():
        updated = output.get(int(key), 0) + int(right_scale) * int(value)
        if updated:
            output[int(key)] = updated
        elif int(key) in output:
            del output[int(key)]
    return output


def _row_echelon_mod_prime(
    matrix: np.ndarray, prime: int = MODULAR_PRIME
) -> tuple[dict[int, np.ndarray], tuple[int, ...]]:
    update_bound = (prime - 1) ** 2 + (prime - 1)
    if prime <= 2 or update_bound > INT64_MAX:
        raise ArithmeticError("unsafe modular elimination prime")
    rows = np.remainder(np.asarray(matrix, dtype=np.int64), prime)
    pivot_rows: dict[int, np.ndarray] = {}
    for input_row in rows:
        row = input_row.copy()
        while np.any(row):
            pivot = int(np.flatnonzero(row)[0])
            if pivot in pivot_rows:
                row = (row - row[pivot] * pivot_rows[pivot]) % prime
                continue
            row = row * pow(int(row[pivot]), -1, prime) % prime
            pivot_rows[pivot] = row
            break
    pivots = tuple(sorted(pivot_rows))
    for pivot in reversed(pivots):
        row = pivot_rows[pivot]
        for earlier in pivots:
            if earlier >= pivot:
                break
            coefficient = int(pivot_rows[earlier][pivot])
            if coefficient:
                pivot_rows[earlier] = (
                    pivot_rows[earlier] - coefficient * row
                ) % prime
    return pivot_rows, pivots


def _rational_reconstruct(residue: int, modulus: int) -> Fraction:
    """Reconstruct the unique small rational represented modulo ``modulus``."""
    residue %= modulus
    if residue == 0:
        return Fraction(0)
    bound = math.isqrt(modulus // 2)
    old_remainder, remainder = modulus, residue
    old_denominator, denominator = 0, 1
    while abs(remainder) > bound:
        quotient = old_remainder // remainder
        old_remainder, remainder = (
            remainder,
            old_remainder - quotient * remainder,
        )
        old_denominator, denominator = (
            denominator,
            old_denominator - quotient * denominator,
        )
    numerator = remainder
    if denominator < 0:
        numerator = -numerator
        denominator = -denominator
    if (
        denominator == 0
        or denominator > bound
        or abs(numerator) > bound
        or math.gcd(abs(numerator), denominator) != 1
        or (residue * denominator - numerator) % modulus
    ):
        raise ArithmeticError("modular entry has no unique small rational lift")
    return Fraction(numerator, denominator)


def _exact_integer_nullspace(
    matrix: sparse.spmatrix,
    expected_nullity: int,
) -> tuple[np.ndarray, tuple[int, ...], int]:
    dense = matrix.toarray().astype(np.int64, copy=False)
    pivot_rows, pivots = _row_echelon_mod_prime(dense)
    free_columns = tuple(
        column for column in range(matrix.shape[1]) if column not in pivot_rows
    )
    if len(free_columns) != expected_nullity:
        raise ArithmeticError("modular nullity disagrees with exact character census")
    rational_columns: list[list[Fraction]] = []
    for free in free_columns:
        vector = [Fraction(0) for _ in range(matrix.shape[1])]
        vector[free] = Fraction(1)
        for pivot in pivots:
            vector[pivot] = -_rational_reconstruct(
                int(pivot_rows[pivot][free]), MODULAR_PRIME
            )
        rational_columns.append(vector)
    output = np.zeros((matrix.shape[1], expected_nullity), dtype=np.int64)
    maximum_denominator = 1
    for column, vector in enumerate(rational_columns):
        denominator = 1
        for value in vector:
            denominator = math.lcm(denominator, value.denominator)
        maximum_denominator = max(maximum_denominator, denominator)
        integers = [int(value * denominator) for value in vector]
        content = 0
        for value in integers:
            content = math.gcd(content, abs(value))
        integers = [value // content for value in integers]
        first = next(value for value in integers if value)
        if first < 0:
            integers = [-value for value in integers]
        if any(abs(value) > INT64_MAX for value in integers):
            raise ArithmeticError("exact nullspace lift exceeds signed-int64")
        output[:, column] = integers
    if np.any(matrix @ output):
        raise ArithmeticError("modular nullspace did not lift exactly over Z")
    return output, free_columns, maximum_denominator


def _select_sparse_independent_vectors(
    vectors: Sequence[Mapping[int, int]],
    prime: int = MODULAR_PRIME,
) -> tuple[tuple[int, ...], tuple[int, ...], int]:
    basis: dict[int, dict[int, int]] = {}
    selected: list[int] = []
    pivot_coordinates: list[int] = []
    for index, raw in enumerate(vectors):
        vector = {
            int(coordinate): int(value) % prime
            for coordinate, value in raw.items()
            if int(value) % prime
        }
        while vector:
            pivot = min(vector)
            coefficient = vector[pivot]
            if pivot not in basis:
                inverse = pow(coefficient, -1, prime)
                normalized = {
                    coordinate: (value * inverse) % prime
                    for coordinate, value in vector.items()
                    if (value * inverse) % prime
                }
                basis[pivot] = normalized
                selected.append(index)
                pivot_coordinates.append(pivot)
                break
            for coordinate, value in basis[pivot].items():
                updated = (
                    vector.get(coordinate, 0) - coefficient * value
                ) % prime
                if updated:
                    vector[coordinate] = updated
                elif coordinate in vector:
                    del vector[coordinate]
    return tuple(selected), tuple(pivot_coordinates), sum(map(len, basis.values()))


def _rank_mod_prime(matrix: np.ndarray, prime: int = MODULAR_PRIME) -> int:
    return len(_row_echelon_mod_prime(matrix, prime)[1])


@lru_cache(maxsize=1)
def _quadratic_pairs_cached() -> tuple[tuple[int, int], ...]:
    pairs = tuple(
        (left, right)
        for left in range(PHI_DIMENSION)
        for right in range(left, PHI_DIMENSION)
    )
    if len(pairs) != SYMMETRIC_SQUARE_DIMENSION:
        raise ArithmeticError("symmetric-square monomial census drifted")
    return pairs


@lru_cache(maxsize=1)
def _quadratic_pair_index_cached() -> np.ndarray:
    output = np.empty((PHI_DIMENSION, PHI_DIMENSION), dtype=np.int32)
    for index, (left, right) in enumerate(_quadratic_pairs_cached()):
        output[left, right] = index
        output[right, left] = index
    output.setflags(write=False)
    return output


@lru_cache(maxsize=1)
def _sym2_weights_cached() -> tuple[DynkinWeight, ...]:
    weights = intertwiners.exterior_state_weights()
    output = tuple(
        tuple(weights[left][axis] + weights[right][axis] for axis in range(3))
        for left, right in _quadratic_pairs_cached()
    )
    return output  # type: ignore[return-value]


@lru_cache(maxsize=1)
def _sym2_columns_by_weight_cached() -> dict[DynkinWeight, tuple[int, ...]]:
    rows: defaultdict[DynkinWeight, list[int]] = defaultdict(list)
    for index, weight in enumerate(_sym2_weights_cached()):
        rows[weight].append(index)
    return {weight: tuple(indices) for weight, indices in rows.items()}


def _sym2_action(generator: sparse.spmatrix) -> sparse.csr_matrix:
    """Exact induced action on the ordered commutative quadratic monomials."""
    value = generator.tocsc(copy=True)
    value.sum_duplicates()
    value.eliminate_zeros()
    if value.shape != (PHI_DIMENSION, PHI_DIMENSION):
        raise ValueError("Phi210 generator has the wrong shape")
    if not np.issubdtype(value.dtype, np.integer):
        raise TypeError("Phi210 generator must have exact integer entries")
    pair_index = _quadratic_pair_index_cached()
    rows: list[int] = []
    columns: list[int] = []
    coefficients: list[int] = []
    for column, (left, right) in enumerate(_quadratic_pairs_cached()):
        for pointer in range(value.indptr[left], value.indptr[left + 1]):
            image = int(value.indices[pointer])
            rows.append(int(pair_index[image, right]))
            columns.append(column)
            coefficients.append(int(value.data[pointer]))
        for pointer in range(value.indptr[right], value.indptr[right + 1]):
            image = int(value.indices[pointer])
            rows.append(int(pair_index[left, image]))
            columns.append(column)
            coefficients.append(int(value.data[pointer]))
    output = sparse.coo_matrix(
        (coefficients, (rows, columns)),
        shape=(SYMMETRIC_SQUARE_DIMENSION, SYMMETRIC_SQUARE_DIMENSION),
        dtype=np.int64,
    ).tocsr()
    output.sum_duplicates()
    output.eliminate_zeros()
    return output


@lru_cache(maxsize=1)
def _sym2_chevalley_actions_cached() -> dict[str, tuple[sparse.csr_matrix, ...]]:
    actions = aligned.chevalley_actions()
    output = {
        kind: tuple(_sym2_action(generator) for generator in actions[kind])
        for kind in ("cartan", "raising", "lowering")
    }
    maxima = {
        kind: max(_maximum_abs(matrix) for matrix in family)
        for kind, family in output.items()
    }
    if maxima != {"cartan": 4, "raising": 2, "lowering": 2}:
        raise ArithmeticError(
            "Sym2 Chevalley action maxima changed from the pinned exact bounds"
        )
    return output


@lru_cache(maxsize=1)
def _sym2_compact_actions_cached() -> tuple[
    tuple[sparse.csr_matrix, sparse.csr_matrix], ...
]:
    return tuple(
        (_sym2_action(real), _sym2_action(imaginary))
        for real, imaginary in intertwiners.su4_exterior_actions()
    )


@lru_cache(maxsize=1)
def _highest_weight_data_cached() -> dict[str, dict[str, Any]]:
    columns_by_weight = _sym2_columns_by_weight_cached()
    raising = _sym2_chevalley_actions_cached()["raising"]
    output: dict[str, dict[str, Any]] = {}
    for irrep in IRREP_ORDER:
        highest = tuple(intertwiners.IRREP_DATA[irrep]["dynkin"])
        source_columns = columns_by_weight[highest]
        blocks = []
        for root, action in zip(SIMPLE_ROOTS, raising, strict=True):
            target_weight = tuple(
                highest[axis] + root[axis] for axis in range(3)
            )
            target_rows = columns_by_weight.get(target_weight, ())
            blocks.append(action[target_rows, :][:, source_columns])
        constraints = sparse.vstack(blocks, format="csr")
        constraints.sum_duplicates()
        constraints.eliminate_zeros()
        expected_shape, expected_nnz = EXPECTED_HIGHEST_CONSTRAINTS[irrep]
        if constraints.shape != expected_shape or constraints.nnz != expected_nnz:
            raise ArithmeticError(f"{irrep} highest-weight constraint drifted")
        local_vectors, free_columns, maximum_denominator = (
            _exact_integer_nullspace(
                constraints, EXPECTED_SYM2_MULTIPLICITY[irrep]
            )
        )
        nonzero_rows, nonzero_columns = np.nonzero(local_vectors)
        values = local_vectors[nonzero_rows, nonzero_columns]
        embedded = sparse.csc_matrix(
            (
                values,
                (
                    np.asarray(source_columns, dtype=np.int64)[nonzero_rows],
                    nonzero_columns,
                ),
            ),
            shape=(
                SYMMETRIC_SQUARE_DIMENSION,
                EXPECTED_SYM2_MULTIPLICITY[irrep],
            ),
            dtype=np.int64,
        )
        output[irrep] = {
            "highest_weight": highest,
            "source_weight_space_dimension": len(source_columns),
            "constraint_shape": constraints.shape,
            "constraint_nnz": constraints.nnz,
            "constraint_sha256": _sparse_matrix_sha256(constraints),
            "modular_rank": len(free_columns) and (
                constraints.shape[1] - len(free_columns)
            ),
            "nullity": len(free_columns),
            "free_columns": free_columns,
            "maximum_rational_reconstruction_denominator": maximum_denominator,
            "rank_nullity_argument": (
                f"Rank {constraints.shape[1] - len(free_columns)} modulo "
                f"{MODULAR_PRIME} is a lower bound over Q; the displayed "
                f"{len(free_columns)} independent exact integer nullvectors "
                "give the matching upper bound."
            ),
            "highest_vectors": embedded,
            "highest_vectors_nnz": embedded.nnz,
            "highest_vectors_maximum_absolute_entry": _maximum_abs(embedded),
            "highest_vectors_sha256": _sparse_matrix_sha256(embedded),
            "raising_residual_zero_exact": all(
                not (action @ embedded).nnz for action in raising
            ),
        }
    return output


def _apply_lowering_word(
    vector: sparse.spmatrix, word: Sequence[int]
) -> sparse.csr_matrix:
    output = vector.tocsr(copy=True)
    lowering = _sym2_chevalley_actions_cached()["lowering"]
    for root in word:
        if isinstance(root, bool) or not isinstance(root, (int, np.integer)):
            raise TypeError("lowering word contains a non-integer root")
        root_index = int(root)
        if not 0 <= root_index < 3:
            raise ValueError("lowering word contains an invalid simple root")
        output = _checked_sparse_matmul(
            lowering[root_index],
            output,
            "Sym2 lowering-word action",
            left_maximum=2,
        )
    output.eliminate_zeros()
    return output


@lru_cache(maxsize=1)
def _target_carrier_data_cached() -> dict[str, dict[str, Any]]:
    aligned_data = aligned.exact_aligned_carrier_data()
    highest_data = _highest_weight_data_cached()
    output: dict[str, dict[str, Any]] = {}
    target_chevalley_actions = (
        _sym2_chevalley_actions_cached()["cartan"]
        + _sym2_chevalley_actions_cached()["raising"]
        + _sym2_chevalley_actions_cached()["lowering"]
    )
    for irrep in IRREP_ORDER:
        words = tuple(aligned_data["families"][irrep]["lowering_words"])
        highest = highest_data[irrep]["highest_vectors"]
        copies: list[sparse.csr_matrix] = []
        for copy_index in range(highest.shape[1]):
            highest_vector = highest[:, copy_index]
            copies.append(
                sparse.hstack(
                    [
                        _apply_lowering_word(highest_vector, word)
                        for word in words
                    ],
                    format="csr",
                )
            )
        concatenated = sparse.hstack(copies, format="csc")
        individual_copy_ranks = []
        for basis in copies:
            basis_csc = basis.tocsc()
            independent, _, _ = _select_sparse_independent_vectors(
                [
                    {
                        int(row): int(value)
                        for row, value in zip(
                            basis_csc.indices[
                                basis_csc.indptr[column] : basis_csc.indptr[column + 1]
                            ],
                            basis_csc.data[
                                basis_csc.indptr[column] : basis_csc.indptr[column + 1]
                            ],
                            strict=True,
                        )
                    }
                    for column in range(basis_csc.shape[1])
                ]
            )
            individual_copy_ranks.append(len(independent))
        every_copy_full_rank = all(
            rank == int(aligned_data["families"][irrep]["dimension"])
            for rank in individual_copy_ranks
        )
        # Independent highest vectors are a basis of Hom(V_lambda,Sym2Phi).
        # Every nonzero map from the irreducible V_lambda is injective, so the
        # exact evaluation isomorphism gives the whole direct-sum rank without
        # a costly 22,155 by 6,032 dense elimination.
        evaluation_rank = (
            len(copies) * int(aligned_data["families"][irrep]["dimension"])
            if every_copy_full_rank
            else 0
        )

        source_chevalley_actions, source_imaginary_residuals_zero = (
            _source_chevalley_actions(aligned_data["families"][irrep])
        )
        reference_chevalley_intertwinings = True
        checked_component_count = 0
        reference_basis = copies[0]
        for target_action, source_action in zip(
            target_chevalley_actions,
            source_chevalley_actions,
            strict=True,
        ):
            numerator, denominator = source_action
            numerator = np.asarray(numerator, dtype=np.int64)
            denominator = int(denominator)
            if target_action.nnz or np.any(numerator):
                checked_component_count += 1
            left = _checked_sparse_matmul(
                target_action,
                reference_basis,
                "reference target Chevalley action",
            )
            right = _checked_sparse_matmul(
                reference_basis,
                sparse.csr_matrix(numerator),
                "reference source Chevalley action",
            )
            residual = left.multiply(denominator) - right
            residual.eliminate_zeros()
            if residual.nnz:
                reference_chevalley_intertwinings = False
                break
        output[irrep] = {
            **{
                key: value
                for key, value in highest_data[irrep].items()
                if key != "highest_vectors"
            },
            "irrep": irrep,
            "dimension": int(aligned_data["families"][irrep]["dimension"]),
            "copy_count": len(copies),
            "lowering_word_count": len(words),
            "copies": tuple(copies),
            "concatenated_shape": concatenated.shape,
            "concatenated_nnz": concatenated.nnz,
            "individual_copy_ranks_mod_prime": tuple(individual_copy_ranks),
            "every_copy_full_rank_mod_prime": every_copy_full_rank,
            "concatenated_rank_by_highest_weight_evaluation_exact": (
                evaluation_rank
            ),
            "highest_weight_evaluation_rank_argument": (
                "The displayed independent highest vectors form a basis of "
                "Hom(V_lambda,Sym2Phi). Every nonzero homomorphism from the "
                "irreducible V_lambda is injective; evaluation therefore has "
                "rank multiplicity times irrep dimension."
            ),
            "concatenated_sha256": _sparse_matrix_sha256(concatenated),
            "maximum_absolute_entry": _maximum_abs(concatenated),
            "checked_Chevalley_action_count": checked_component_count,
            "source_Chevalley_imaginary_residuals_zero_exact": (
                source_imaginary_residuals_zero
            ),
            "reference_copy_all_9_Chevalley_actions_intertwine_exact": (
                reference_chevalley_intertwinings
            ),
            "every_copy_alignment_follows_from_highest_weight_universality_exact": bool(
                highest_data[irrep]["raising_residual_zero_exact"]
                and every_copy_full_rank
                and len(words)
                == int(aligned_data["families"][irrep]["dimension"])
            ),
            "proof_grade": bool(
                highest_data[irrep]["raising_residual_zero_exact"]
                and len(copies) == EXPECTED_SYM2_MULTIPLICITY[irrep]
                and len(words)
                == int(aligned_data["families"][irrep]["dimension"])
                and every_copy_full_rank
                and source_imaginary_residuals_zero
                and reference_chevalley_intertwinings
            ),
        }
    return output


def _rational_matrix_entries(value: RationalMatrix) -> list[list[Fraction]]:
    numerator, denominator = value
    denominator = int(denominator)
    if denominator <= 0:
        raise ArithmeticError("source-action denominator is not positive")
    return [
        [Fraction(int(entry), denominator) for entry in row]
        for row in np.asarray(numerator)
    ]


def _rational_linear_combination(
    terms: Sequence[tuple[RationalMatrix, Fraction]],
) -> RationalMatrix:
    if not terms:
        raise ValueError("rational linear combination requires a term")
    shape = np.asarray(terms[0][0][0]).shape
    denominator = 1
    for (numerator, source_denominator), coefficient in terms:
        if np.asarray(numerator).shape != shape:
            raise ValueError("rational matrix shapes disagree")
        denominator = math.lcm(
            denominator,
            int(source_denominator) * coefficient.denominator,
        )
    exact = np.zeros(shape, dtype=object)
    for (numerator, source_denominator), coefficient in terms:
        scale = (
            denominator
            * coefficient.numerator
            // (int(source_denominator) * coefficient.denominator)
        )
        exact += scale * np.asarray(numerator, dtype=object)
    integers = [int(value) for value in exact.reshape(-1)]
    common = denominator
    for value in integers:
        common = math.gcd(common, abs(value))
    denominator //= common
    integers = [value // common for value in integers]
    if any(abs(value) > INT64_MAX for value in integers):
        raise ArithmeticError("rational combination exceeds signed-int64")
    return np.asarray(integers, dtype=np.int64).reshape(shape), denominator


def _source_chevalley_actions(
    family: Mapping[str, Any],
) -> tuple[tuple[RationalMatrix, ...], bool]:
    records = {record["label"]: record for record in family["source_actions"]}
    cartan = tuple(records[f"H{index}"]["imaginary"] for index in range(1, 4))
    raising: list[RationalMatrix] = []
    lowering: list[RationalMatrix] = []
    residuals_zero = True
    for pair in ("12", "23", "34"):
        x = records[f"X{pair}"]
        y = records[f"Y{pair}"]
        raising.append(
            _rational_linear_combination(
                (
                    (x["real"], Fraction(1, 2)),
                    (y["imaginary"], Fraction(1, 2)),
                )
            )
        )
        lowering.append(
            _rational_linear_combination(
                (
                    (x["real"], Fraction(-1, 2)),
                    (y["imaginary"], Fraction(1, 2)),
                )
            )
        )
        raising_imaginary = _rational_linear_combination(
            (
                (x["imaginary"], Fraction(1, 2)),
                (y["real"], Fraction(-1, 2)),
            )
        )
        lowering_imaginary = _rational_linear_combination(
            (
                (x["imaginary"], Fraction(-1, 2)),
                (y["real"], Fraction(-1, 2)),
            )
        )
        residuals_zero = bool(
            residuals_zero
            and not np.any(raising_imaginary[0])
            and not np.any(lowering_imaginary[0])
        )
    return cartan + tuple(raising) + tuple(lowering), residuals_zero


def _word_weights(irrep: str, words: Sequence[Sequence[int]]) -> tuple[DynkinWeight, ...]:
    highest = tuple(intertwiners.IRREP_DATA[irrep]["dynkin"])
    output = []
    for word in words:
        weight = list(highest)
        for root in word:
            for axis in range(3):
                weight[axis] -= SIMPLE_ROOTS[int(root)][axis]
        output.append(tuple(weight))
    return tuple(output)  # type: ignore[return-value]


def _pairing_constraint_matrix(
    source_irrep: str,
    target_irrep: str,
    aligned_data: Mapping[str, Any],
) -> tuple[sparse.csr_matrix, tuple[tuple[int, int], ...]]:
    source_family = aligned_data["families"][source_irrep]
    target_family = aligned_data["families"][target_irrep]
    source_words = tuple(source_family["lowering_words"])
    target_words = tuple(target_family["lowering_words"])
    source_weights = _word_weights(source_irrep, source_words)
    target_weights = _word_weights(target_irrep, target_words)
    variables = tuple(
        (left, right)
        for left, left_weight in enumerate(source_weights)
        for right, right_weight in enumerate(target_weights)
        if all(
            left_weight[axis] + right_weight[axis] == 0
            for axis in range(3)
        )
    )
    if not variables:
        raise ArithmeticError("contragredient pairing has no weight-zero entries")
    row_equations: defaultdict[
        tuple[int, int, int, str], dict[int, Fraction]
    ] = defaultdict(dict)
    for generator_index, (source_record, target_record) in enumerate(
        zip(
            source_family["source_actions"],
            target_family["source_actions"],
            strict=True,
        )
    ):
        for component in ("real", "imaginary"):
            source_action = _rational_matrix_entries(source_record[component])
            target_action = _rational_matrix_entries(target_record[component])
            for variable_index, (left, right) in enumerate(variables):
                # Tensor-coefficient invariance is A*C + C*B^T = 0.
                for output_left in range(len(source_words)):
                    coefficient = source_action[output_left][left]
                    if coefficient:
                        key = (
                            generator_index,
                            output_left,
                            right,
                            component,
                        )
                        row_equations[key][variable_index] = (
                            row_equations[key].get(variable_index, Fraction(0))
                            + coefficient
                        )
                for output_right in range(len(target_words)):
                    coefficient = target_action[output_right][right]
                    if coefficient:
                        key = (
                            generator_index,
                            left,
                            output_right,
                            component,
                        )
                        row_equations[key][variable_index] = (
                            row_equations[key].get(variable_index, Fraction(0))
                            + coefficient
                        )
    rows: list[int] = []
    columns: list[int] = []
    values: list[int] = []
    output_row = 0
    for key in sorted(row_equations):
        equation = {
            column: coefficient
            for column, coefficient in row_equations[key].items()
            if coefficient
        }
        if not equation:
            continue
        denominator = 1
        for coefficient in equation.values():
            denominator = math.lcm(denominator, coefficient.denominator)
        integers = {
            column: int(coefficient * denominator)
            for column, coefficient in equation.items()
        }
        content = 0
        for coefficient in integers.values():
            content = math.gcd(content, abs(coefficient))
        first_column = min(integers)
        sign = -1 if integers[first_column] < 0 else 1
        for column, coefficient in integers.items():
            rows.append(output_row)
            columns.append(column)
            values.append(sign * coefficient // content)
        output_row += 1
    matrix = sparse.coo_matrix(
        (values, (rows, columns)),
        shape=(output_row, len(variables)),
        dtype=np.int64,
    ).tocsr()
    matrix.sum_duplicates()
    matrix.eliminate_zeros()
    return matrix, variables


@lru_cache(maxsize=1)
def _pairing_data_cached() -> dict[str, dict[str, Any]]:
    aligned_data = aligned.exact_aligned_carrier_data()
    output: dict[str, dict[str, Any]] = {}
    for source_irrep in IRREP_ORDER:
        target_irrep = CONJUGATE_IRREP[source_irrep]
        constraints, variables = _pairing_constraint_matrix(
            source_irrep, target_irrep, aligned_data
        )
        nullspace, free_columns, maximum_denominator = (
            _exact_integer_nullspace(constraints, 1)
        )
        dimension = int(aligned_data["families"][source_irrep]["dimension"])
        matrix = np.zeros((dimension, dimension), dtype=np.int64)
        for variable_index, (left, right) in enumerate(variables):
            matrix[left, right] = int(nullspace[variable_index, 0])
        if not np.any(matrix):
            raise ArithmeticError("zero contragredient pairing")

        all_compact_residuals_zero = True
        source_actions = aligned_data["families"][source_irrep]["source_actions"]
        target_actions = aligned_data["families"][target_irrep]["source_actions"]
        for source_record, target_record in zip(
            source_actions, target_actions, strict=True
        ):
            for component in ("real", "imaginary"):
                source_numerator, source_denominator = source_record[component]
                target_numerator, target_denominator = target_record[component]
                left = _checked_dense_matmul(
                    np.asarray(source_numerator, dtype=np.int64),
                    matrix,
                    "pairing left action",
                )
                right = _checked_dense_matmul(
                    matrix,
                    np.asarray(target_numerator, dtype=np.int64).T,
                    "pairing right action",
                )
                residual = (
                    int(target_denominator) * left
                    + int(source_denominator) * right
                )
                if np.any(residual):
                    all_compact_residuals_zero = False
                    break
            if not all_compact_residuals_zero:
                break
        output[source_irrep] = {
            "source_irrep": source_irrep,
            "target_contragredient_irrep": target_irrep,
            "dimension": dimension,
            "weight_zero_variable_count": len(variables),
            "constraint_shape": constraints.shape,
            "constraint_nnz": constraints.nnz,
            "constraint_sha256": _sparse_matrix_sha256(constraints),
            "modular_rank": constraints.shape[1] - len(free_columns),
            "exact_nullity": len(free_columns),
            "maximum_rational_reconstruction_denominator": maximum_denominator,
            "rank_nullity_argument": (
                f"Rank {constraints.shape[1] - len(free_columns)} modulo "
                f"{MODULAR_PRIME} plus the displayed exact primitive integer "
                "nullvector proves rational nullity one."
            ),
            "matrix": matrix,
            "matrix_nnz": int(np.count_nonzero(matrix)),
            "matrix_maximum_absolute_entry": _maximum_abs(matrix),
            "matrix_sha256": hashlib.sha256(
                np.ascontiguousarray(matrix, dtype="<i8").tobytes()
            ).hexdigest(),
            "all_15_compact_tensor_invariance_equations_exact": (
                all_compact_residuals_zero
            ),
            "proof_grade": bool(
                len(free_columns) == 1 and all_compact_residuals_zero
            ),
        }
    return output


@lru_cache(maxsize=1)
def _weight_zero_cubic_coordinates_cached() -> tuple[
    tuple[tuple[int, int, int], ...], dict[tuple[int, int, int], int]
]:
    weights = intertwiners.exterior_state_weights()
    triples: list[tuple[int, int, int]] = []
    indices: dict[tuple[int, int, int], int] = {}
    for first in range(PHI_DIMENSION):
        for second in range(first, PHI_DIMENSION):
            for third in range(second, PHI_DIMENSION):
                if all(
                    weights[first][axis]
                    + weights[second][axis]
                    + weights[third][axis]
                    == 0
                    for axis in range(3)
                ):
                    triple = (first, second, third)
                    indices[triple] = len(triples)
                    triples.append(triple)
    if len(triples) != WEIGHT_ZERO_CUBIC_MONOMIAL_COUNT:
        raise ArithmeticError("weight-zero cubic monomial census drifted")
    return tuple(triples), indices


def _multiply_domain_tensor(vector: Mapping[int, int]) -> SparseVector:
    pairs = _quadratic_pairs_cached()
    triple_index = _weight_zero_cubic_coordinates_cached()[1]
    output: SparseVector = {}
    for coordinate, coefficient in vector.items():
        first, pair_coordinate = divmod(
            int(coordinate), SYMMETRIC_SQUARE_DIMENSION
        )
        second, third = pairs[pair_coordinate]
        triple = tuple(sorted((first, second, third)))
        target = triple_index[triple]
        updated = output.get(target, 0) + GRAM_CROSS_MULTIPLIER * int(
            coefficient
        )
        if updated:
            output[target] = updated
        elif target in output:
            del output[target]
    return output


def _real_block_representative(irrep: str) -> DynkinWeight:
    highest = tuple(intertwiners.IRREP_DATA[irrep]["dynkin"])
    conjugate = tuple(
        intertwiners.IRREP_DATA[CONJUGATE_IRREP[irrep]]["dynkin"]
    )
    return min(highest, conjugate)  # type: ignore[return-value]


@lru_cache(maxsize=1)
def _original_domain_data_cached() -> tuple[dict[str, Any], ...]:
    aligned_data = aligned.exact_aligned_carrier_data()
    target_data = _target_carrier_data_cached()
    pairing_data = _pairing_data_cached()
    records: list[dict[str, Any]] = []
    ordinal = 0
    for source_irrep in IRREP_ORDER:
        target_irrep = CONJUGATE_IRREP[source_irrep]
        pairing = sparse.csr_matrix(pairing_data[source_irrep]["matrix"])
        source_carriers = tuple(
            carrier
            for carrier in aligned_data["carriers"]
            if carrier["irrep"] == source_irrep
        )
        target_carriers = target_data[target_irrep]["copies"]
        for source_carrier in source_carriers:
            source_basis = source_carrier["exterior_basis"].tocsr()
            source_pairing = _checked_sparse_matmul(
                source_basis, pairing, "source carrier pairing"
            )
            for target_copy_index, target_basis in enumerate(target_carriers):
                tensor = _checked_sparse_matmul(
                    source_pairing,
                    target_basis.T.tocsr(),
                    "invariant cubic-domain tensor",
                ).tocoo()
                raw = {
                    int(row) * SYMMETRIC_SQUARE_DIMENSION + int(column): int(value)
                    for row, column, value in zip(
                        tensor.row, tensor.col, tensor.data, strict=True
                    )
                    if value
                }
                primitive, content, sign = _primitive_sparse_vector(raw)
                if not primitive:
                    raise ArithmeticError("zero invariant domain tensor")
                image = _multiply_domain_tensor(primitive)
                records.append(
                    {
                        "ordinal": ordinal,
                        "source_irrep": source_irrep,
                        "source_copy_index": int(source_carrier["copy_index"]),
                        "target_irrep": target_irrep,
                        "target_copy_index": target_copy_index,
                        "real_block_representative": _real_block_representative(
                            source_irrep
                        ),
                        "domain_vector": primitive,
                        "domain_content_removed": content,
                        "domain_sign_normalization": sign,
                        "domain_nnz": len(primitive),
                        "domain_sha256": _sparse_vector_sha256(primitive),
                        "image_vector": image,
                        "image_nnz": len(image),
                        "image_sha256": _sparse_vector_sha256(image),
                    }
                )
                ordinal += 1
    if len(records) != COMPLEX_CUBIC_DOMAIN_DIMENSION:
        raise ArithmeticError("complex cubic-domain tensor census drifted")
    return tuple(records)


@lru_cache(maxsize=1)
def _physical_conjugation_permutation_cached() -> tuple[
    tuple[int, ...], tuple[int, ...]
]:
    matrix = aligned.exterior_conjugation().tocsc()
    images: list[int] = []
    signs: list[int] = []
    for column in range(PHI_DIMENSION):
        start, stop = matrix.indptr[column], matrix.indptr[column + 1]
        if stop - start != 1:
            raise ArithmeticError("physical conjugation ceased to be monomial")
        images.append(int(matrix.indices[start]))
        sign = int(matrix.data[start])
        if sign not in (-1, 1):
            raise ArithmeticError("physical conjugation sign drifted")
        signs.append(sign)
    if sorted(images) != list(range(PHI_DIMENSION)):
        raise ArithmeticError("physical conjugation is not a permutation")
    return tuple(images), tuple(signs)


def _conjugate_domain_vector(vector: Mapping[int, int]) -> SparseVector:
    images, signs = _physical_conjugation_permutation_cached()
    pairs = _quadratic_pairs_cached()
    pair_index = _quadratic_pair_index_cached()
    output: SparseVector = {}
    for coordinate, coefficient in vector.items():
        first, pair_coordinate = divmod(
            int(coordinate), SYMMETRIC_SQUARE_DIMENSION
        )
        second, third = pairs[pair_coordinate]
        image_first = images[first]
        image_second = images[second]
        image_third = images[third]
        target_pair = int(pair_index[image_second, image_third])
        target = image_first * SYMMETRIC_SQUARE_DIMENSION + target_pair
        value = (
            int(coefficient)
            * signs[first]
            * signs[second]
            * signs[third]
        )
        output[target] = output.get(target, 0) + value
        if output[target] == 0:
            del output[target]
    return output


def _conjugate_cubic_vector(vector: Mapping[int, int]) -> SparseVector:
    images, signs = _physical_conjugation_permutation_cached()
    triples, triple_index = _weight_zero_cubic_coordinates_cached()
    output: SparseVector = {}
    for coordinate, coefficient in vector.items():
        first, second, third = triples[int(coordinate)]
        target_triple = tuple(
            sorted((images[first], images[second], images[third]))
        )
        target = triple_index[target_triple]
        value = (
            int(coefficient)
            * signs[first]
            * signs[second]
            * signs[third]
        )
        output[target] = output.get(target, 0) + value
        if output[target] == 0:
            del output[target]
    return output


def _normalize_physical_candidate(
    domain: Mapping[int, int], image: Mapping[int, int]
) -> tuple[SparseVector, SparseVector, int, int]:
    primitive_domain, content, sign = _primitive_sparse_vector(domain)
    if not primitive_domain:
        return {}, {}, 1, 1
    primitive_image: SparseVector = {}
    for coordinate, coefficient in image.items():
        if int(coefficient) % content:
            raise ArithmeticError(
                "physical-domain primitive normalization does not divide image"
            )
        value = sign * int(coefficient) // content
        if value:
            primitive_image[int(coordinate)] = value
    if primitive_image != _multiply_domain_tensor(primitive_domain):
        raise ArithmeticError("physical multiplication ceased to be linear")
    return primitive_domain, primitive_image, content, sign


@lru_cache(maxsize=1)
def _physical_domain_data_cached() -> dict[str, Any]:
    original = _original_domain_data_cached()
    raw_domain_dimension = PHI_DIMENSION * SYMMETRIC_SQUARE_DIMENSION
    candidates: list[dict[str, Any]] = []
    all_multiplications_commute = True
    for record in original:
        domain = record["domain_vector"]
        image = record["image_vector"]
        conjugate_domain = _conjugate_domain_vector(domain)
        conjugate_image = _conjugate_cubic_vector(image)
        if _multiply_domain_tensor(conjugate_domain) != conjugate_image:
            all_multiplications_commute = False
        for component, scale, offset in (
            ("real_plus", 1, 0),
            ("imaginary_minus", -1, raw_domain_dimension),
        ):
            combined_domain = _combine_sparse_vectors(
                domain, conjugate_domain, scale
            )
            combined_image = _combine_sparse_vectors(
                image, conjugate_image, scale
            )
            normalized_domain, normalized_image, content, sign = (
                _normalize_physical_candidate(combined_domain, combined_image)
            )
            if not normalized_domain:
                continue
            doubled_domain = {
                offset + coordinate: coefficient
                for coordinate, coefficient in normalized_domain.items()
            }
            image_offset = (
                0
                if component == "real_plus"
                else WEIGHT_ZERO_CUBIC_MONOMIAL_COUNT
            )
            doubled_image = {
                image_offset + coordinate: coefficient
                for coordinate, coefficient in normalized_image.items()
            }
            conjugated_normalized_domain = _conjugate_domain_vector(
                normalized_domain
            )
            conjugated_normalized_image = _conjugate_cubic_vector(
                normalized_image
            )
            expected_sign = 1 if component == "real_plus" else -1
            physical_exact = bool(
                conjugated_normalized_domain
                == {
                    coordinate: expected_sign * coefficient
                    for coordinate, coefficient in normalized_domain.items()
                }
                and conjugated_normalized_image
                == {
                    coordinate: expected_sign * coefficient
                    for coordinate, coefficient in normalized_image.items()
                }
            )
            candidates.append(
                {
                    "candidate_index": len(candidates),
                    "origin_ordinal": record["ordinal"],
                    "source_irrep": record["source_irrep"],
                    "target_irrep": record["target_irrep"],
                    "source_copy_index": record["source_copy_index"],
                    "target_copy_index": record["target_copy_index"],
                    "real_block_representative": record[
                        "real_block_representative"
                    ],
                    "physical_component": component,
                    "domain_vector": doubled_domain,
                    "undoubled_domain_vector": normalized_domain,
                    "image_vector": doubled_image,
                    "undoubled_image_vector": normalized_image,
                    "content_removed": content,
                    "sign_normalization": sign,
                    "physical_real_structure_exact": physical_exact,
                }
            )
    selected_indices, pivot_coordinates, elimination_fill = (
        _select_sparse_independent_vectors(
            [candidate["domain_vector"] for candidate in candidates]
        )
    )
    if len(selected_indices) != REAL_CUBIC_DOMAIN_DIMENSION:
        raise ArithmeticError("physical cubic-domain basis rank drifted")
    selected = tuple(candidates[index] for index in selected_indices)
    block_counts = Counter(
        record["real_block_representative"] for record in selected
    )
    if dict(block_counts) != EXPECTED_REAL_BLOCK_COUNTS:
        raise ArithmeticError("physical real-block variable counts drifted")
    all_physical = all(
        record["physical_real_structure_exact"] for record in selected
    )
    return {
        "candidate_count": len(candidates),
        "selected_candidate_indices": selected_indices,
        "domain_pivot_coordinates": pivot_coordinates,
        "modular_elimination_fill": elimination_fill,
        "basis": selected,
        "basis_count": len(selected),
        "real_block_counts": dict(block_counts),
        "all_multiplications_commute_with_physical_conjugation_exact": (
            all_multiplications_commute
        ),
        "all_selected_vectors_satisfy_physical_real_structure_exact": (
            all_physical
        ),
        "proof_grade": bool(
            all_multiplications_commute
            and all_physical
            and len(selected) == REAL_CUBIC_DOMAIN_DIMENSION
            and dict(block_counts) == EXPECTED_REAL_BLOCK_COUNTS
        ),
    }


@lru_cache(maxsize=1)
def _coordinate_map_data_cached() -> dict[str, Any]:
    physical = _physical_domain_data_cached()
    basis = physical["basis"]
    rows: list[int] = []
    columns: list[int] = []
    values: list[int] = []
    for column, record in enumerate(basis):
        for row, value in record["image_vector"].items():
            rows.append(int(row))
            columns.append(column)
            values.append(int(value))
    full_image = sparse.coo_matrix(
        (values, (rows, columns)),
        shape=(
            2 * WEIGHT_ZERO_CUBIC_MONOMIAL_COUNT,
            REAL_CUBIC_DOMAIN_DIMENSION,
        ),
        dtype=np.int64,
    ).tocsc()
    full_image.sum_duplicates()
    full_image.eliminate_zeros()
    column_vectors = [
        {
            int(row): int(value)
            for row, value in zip(
                full_image.indices[
                    full_image.indptr[column] : full_image.indptr[column + 1]
                ],
                full_image.data[
                    full_image.indptr[column] : full_image.indptr[column + 1]
                ],
                strict=True,
            )
        }
        for column in range(full_image.shape[1])
    ]
    independent_columns, pivot_rows, elimination_fill = (
        _select_sparse_independent_vectors(column_vectors)
    )
    if len(independent_columns) != CUBIC_TARGET_DIMENSION:
        raise ArithmeticError("explicit physical cubic map rank drifted")
    coordinate_map = full_image[list(pivot_rows), :].tocsr()
    minor = coordinate_map[:, list(independent_columns)].toarray()
    minor_rank = _rank_mod_prime(minor)
    if minor_rank != CUBIC_TARGET_DIMENSION:
        raise ArithmeticError("selected cubic coordinate minor is singular")
    triples = _weight_zero_cubic_coordinates_cached()[0]
    target_metadata = tuple(
        {
            "coordinate_index": output_index,
            "physical_component": (
                "real"
                if pivot < WEIGHT_ZERO_CUBIC_MONOMIAL_COUNT
                else "imaginary"
            ),
            "weight_zero_cubic_coordinate": (
                pivot % WEIGHT_ZERO_CUBIC_MONOMIAL_COUNT
            ),
            "Gaussian_exterior_monomial": triples[
                pivot % WEIGHT_ZERO_CUBIC_MONOMIAL_COUNT
            ],
        }
        for output_index, pivot in enumerate(pivot_rows)
    )
    return {
        "full_physical_image": full_image,
        "full_physical_image_shape": full_image.shape,
        "full_physical_image_nnz": full_image.nnz,
        "full_physical_image_maximum_absolute_entry": _maximum_abs(full_image),
        "full_physical_image_sha256": _sparse_matrix_sha256(full_image),
        "independent_domain_column_indices": independent_columns,
        "target_pivot_rows": pivot_rows,
        "target_coordinate_metadata": target_metadata,
        "modular_elimination_fill": elimination_fill,
        "coordinate_map": coordinate_map,
        "coordinate_map_shape": coordinate_map.shape,
        "coordinate_map_nnz": coordinate_map.nnz,
        "coordinate_map_maximum_absolute_entry": _maximum_abs(coordinate_map),
        "coordinate_map_sha256": _sparse_matrix_sha256(coordinate_map),
        "rank_mod_prime": len(independent_columns),
        "selected_minor_rank_mod_prime": minor_rank,
        "selected_minor_determinant_nonzero_mod_prime": True,
        "selected_minor_sha256": hashlib.sha256(
            np.ascontiguousarray(minor, dtype="<i8").tobytes()
        ).hexdigest(),
        "exact_rank": CUBIC_TARGET_DIMENSION,
        "exact_kernel_dimension": (
            REAL_CUBIC_DOMAIN_DIMENSION - CUBIC_TARGET_DIMENSION
        ),
        "rank_argument": (
            "The displayed 478 by 478 minor is nonsingular modulo 1000003, "
            "so the rational/real rank is at least 478. The independently "
            "certified invariant cubic target dimension is 478, so the rank "
            "is exactly 478; rank-nullity gives kernel dimension 936."
        ),
        "proof_grade": bool(
            coordinate_map.shape
            == (CUBIC_TARGET_DIMENSION, REAL_CUBIC_DOMAIN_DIMENSION)
            and len(independent_columns) == CUBIC_TARGET_DIMENSION
            and minor_rank == CUBIC_TARGET_DIMENSION
            and REAL_CUBIC_DOMAIN_DIMENSION - CUBIC_TARGET_DIMENSION
            == CUBIC_KERNEL_DIMENSION
        ),
    }


def exact_cubic_coordinate_map() -> sparse.csr_matrix:
    """Return the exact 478 by 1,414 integer map in Gram convention."""
    return _coordinate_map_data_cached()["coordinate_map"].copy()


def abstract_zero_cubic_interface_placeholder() -> np.ndarray:
    """Return the reserved zero placeholder, never a physical G3 target."""
    return np.zeros(CUBIC_TARGET_DIMENSION, dtype=np.int64)


def cubic_domain_basis_metadata() -> tuple[dict[str, Any], ...]:
    """Return mutation-isolated metadata for the 1,414 physical variables."""
    return tuple(
        {
            key: copy.deepcopy(value)
            for key, value in record.items()
            if key
            not in {
                "domain_vector",
                "undoubled_domain_vector",
                "image_vector",
                "undoubled_image_vector",
            }
        }
        for record in _physical_domain_data_cached()["basis"]
    )


def cubic_target_coordinate_metadata() -> tuple[dict[str, Any], ...]:
    return copy.deepcopy(
        _coordinate_map_data_cached()["target_coordinate_metadata"]
    )


def _target_carrier_certificate() -> dict[str, Any]:
    data = _target_carrier_data_cached()
    rows = tuple(
        {
            key: copy.deepcopy(value)
            for key, value in data[irrep].items()
            if key != "copies"
        }
        for irrep in IRREP_ORDER
    )
    total_copies = sum(row["copy_count"] for row in rows)
    total_dimension = sum(
        row["copy_count"] * row["dimension"] for row in rows
    )
    return {
        "representation": "required Phi210 isotypes inside Sym2(Phi210)",
        "irrep_family_count": len(rows),
        "families": rows,
        "total_complex_carrier_copy_count": total_copies,
        "total_isotypic_dimension": total_dimension,
        "all_highest_weight_nullities_match_character_census_exact": all(
            row["nullity"] == EXPECTED_SYM2_MULTIPLICITY[row["irrep"]]
            for row in rows
        ),
        "all_highest_vectors_raise_to_zero_exact": all(
            row["raising_residual_zero_exact"] for row in rows
        ),
        "all_common_lowering_word_carriers_have_full_rank_exact": all(
            row["concatenated_rank_by_highest_weight_evaluation_exact"]
            == row["concatenated_shape"][1]
            for row in rows
        ),
        "all_reference_copies_intertwine_9_Chevalley_actions_exact": all(
            row["reference_copy_all_9_Chevalley_actions_intertwine_exact"]
            for row in rows
        ),
        "all_copies_aligned_by_exact_highest_weight_universality": all(
            row[
                "every_copy_alignment_follows_from_highest_weight_universality_exact"
            ]
            for row in rows
        ),
        "proof_grade": bool(
            len(rows) == 10
            and total_copies == sum(EXPECTED_SYM2_MULTIPLICITY.values())
            and total_dimension == 6_032
            and all(row["proof_grade"] for row in rows)
        ),
    }


def _pairing_certificate() -> dict[str, Any]:
    data = _pairing_data_cached()
    rows = tuple(
        {
            key: copy.deepcopy(value)
            for key, value in data[irrep].items()
            if key != "matrix"
        }
        for irrep in IRREP_ORDER
    )
    return {
        "pairing_family_count": len(rows),
        "families": rows,
        "all_pairing_spaces_one_dimensional_exact": all(
            row["exact_nullity"] == 1 for row in rows
        ),
        "all_15_compact_tensor_equations_exact": all(
            row["all_15_compact_tensor_invariance_equations_exact"]
            for row in rows
        ),
        "proof_grade": bool(
            len(rows) == 10 and all(row["proof_grade"] for row in rows)
        ),
    }


def _domain_certificate() -> dict[str, Any]:
    original = _original_domain_data_cached()
    physical = _physical_domain_data_cached()
    complex_counts = Counter(row["source_irrep"] for row in original)
    original_nnz = sum(row["domain_nnz"] for row in original)
    original_image_nnz = sum(row["image_nnz"] for row in original)
    selected = physical["basis"]
    component_counts = Counter(row["physical_component"] for row in selected)
    selected_metadata_hash = _canonical_json_sha256(
        cubic_domain_basis_metadata()
    )
    census_blocks = census.exact_augmented_isotypic_blocks()
    all_22_rows = tuple(
        {
            "representative_dynkin": tuple(block["representative_dynkin"]),
            "real_block_kind": block["real_block_kind"],
            "tPhi_multiplicity": block[
                "graded_multiplicities_t2_tPhi_Phi2"
            ][1],
            "Phi2_multiplicity": block[
                "graded_multiplicities_t2_tPhi_Phi2"
            ][2],
            "expected_cubic_cross_real_parameter_count": block[
                "cubic_tPhi_to_Phi2_cross_real_parameter_count"
            ],
            "constructed_physical_basis_variable_count": physical[
                "real_block_counts"
            ].get(tuple(block["representative_dynkin"]), 0),
            "all_variables_constructed_exact": (
                block["cubic_tPhi_to_Phi2_cross_real_parameter_count"]
                == physical["real_block_counts"].get(
                    tuple(block["representative_dynkin"]), 0
                )
            ),
        }
        for block in census_blocks
    )
    return {
        "complexified_domain_basis_count": len(original),
        "expected_complexified_counts_by_irrep": EXPECTED_COMPLEX_DOMAIN_COUNTS,
        "observed_complexified_counts_by_irrep": dict(complex_counts),
        "complexified_raw_tensor_total_nnz": original_nnz,
        "complexified_raw_image_total_nnz": original_image_nnz,
        "physical_candidate_count": physical["candidate_count"],
        "physical_basis_count": physical["basis_count"],
        "physical_component_counts": dict(component_counts),
        "physical_real_block_counts": physical["real_block_counts"],
        "all_22_augmented_block_rows": all_22_rows,
        "all_22_block_provenance_rows_exact": all(
            row["all_variables_constructed_exact"] for row in all_22_rows
        ),
        "nonzero_cubic_block_count": sum(
            row["constructed_physical_basis_variable_count"] > 0
            for row in all_22_rows
        ),
        "domain_basis_metadata_sha256": selected_metadata_hash,
        "domain_modular_pivot_count": len(
            physical["domain_pivot_coordinates"]
        ),
        "domain_modular_elimination_fill": physical[
            "modular_elimination_fill"
        ],
        "all_multiplications_commute_with_physical_conjugation_exact": physical[
            "all_multiplications_commute_with_physical_conjugation_exact"
        ],
        "all_selected_vectors_satisfy_physical_real_structure_exact": physical[
            "all_selected_vectors_satisfy_physical_real_structure_exact"
        ],
        "Gram_symmetric_off_diagonal_multiplier": GRAM_CROSS_MULTIPLIER,
        "proof_grade": bool(
            len(original) == COMPLEX_CUBIC_DOMAIN_DIMENSION
            and dict(complex_counts) == EXPECTED_COMPLEX_DOMAIN_COUNTS
            and physical["proof_grade"]
            and physical["basis_count"] == REAL_CUBIC_DOMAIN_DIMENSION
            and all(row["all_variables_constructed_exact"] for row in all_22_rows)
            and sum(physical["real_block_counts"].values())
            == REAL_CUBIC_DOMAIN_DIMENSION
        ),
    }


def _map_certificate() -> dict[str, Any]:
    data = _coordinate_map_data_cached()
    zero_placeholder = abstract_zero_cubic_interface_placeholder()
    target_metadata = cubic_target_coordinate_metadata()
    return {
        "source_coordinate_space": (
            "1,414-element exact real-structure-fixed invariant basis of the "
            "t*Phi210 <-> Sym2(Phi210) Schur cross blocks"
        ),
        "target_coordinate_space": (
            "478 deterministic real/imaginary Gaussian-exterior monomial "
            "coefficient pivots on Sym3(Phi210)^SU4"
        ),
        "Gram_convention": (
            "z^T Q z; every t*Phi-to-Phi2 off-diagonal entry contributes "
            "twice, and the published matrix includes this factor two"
        ),
        "full_physical_image_shape": data["full_physical_image_shape"],
        "full_physical_image_nnz": data["full_physical_image_nnz"],
        "full_physical_image_maximum_absolute_entry": data[
            "full_physical_image_maximum_absolute_entry"
        ],
        "full_physical_image_sha256": data["full_physical_image_sha256"],
        "coordinate_map_shape": data["coordinate_map_shape"],
        "coordinate_map_nnz": data["coordinate_map_nnz"],
        "coordinate_map_maximum_absolute_entry": data[
            "coordinate_map_maximum_absolute_entry"
        ],
        "coordinate_map_sha256": data["coordinate_map_sha256"],
        "modular_prime": MODULAR_PRIME,
        "rank_mod_prime": data["rank_mod_prime"],
        "selected_minor_rank_mod_prime": data[
            "selected_minor_rank_mod_prime"
        ],
        "selected_minor_determinant_nonzero_mod_prime": data[
            "selected_minor_determinant_nonzero_mod_prime"
        ],
        "selected_minor_sha256": data["selected_minor_sha256"],
        "exact_rank": data["exact_rank"],
        "exact_kernel_dimension": data["exact_kernel_dimension"],
        "rank_argument": data["rank_argument"],
        "independent_domain_column_indices": data[
            "independent_domain_column_indices"
        ],
        "target_pivot_row_count": len(data["target_pivot_rows"]),
        "target_coordinate_metadata_sha256": _canonical_json_sha256(
            target_metadata
        ),
        "target_real_coordinate_count": sum(
            row["physical_component"] == "real" for row in target_metadata
        ),
        "target_imaginary_coordinate_count": sum(
            row["physical_component"] == "imaginary"
            for row in target_metadata
        ),
        "abstract_zero_interface_placeholder_shape": zero_placeholder.shape,
        "abstract_zero_interface_placeholder_dtype": str(
            zero_placeholder.dtype
        ),
        "abstract_zero_interface_placeholder_nnz": int(
            np.count_nonzero(zero_placeholder)
        ),
        "all_478_abstract_interface_placeholder_entries_zero_exact": bool(
            zero_placeholder.shape == (CUBIC_TARGET_DIMENSION,)
            and zero_placeholder.dtype == np.int64
            and not np.any(zero_placeholder)
        ),
        "abstract_zero_placeholder_is_not_a_physical_G3_target": True,
        "physical_G3_gap_target_vector_constructed": False,
        "physical_G3_gap_cubic_zero_RHS_certified": False,
        "proof_grade": data["proof_grade"],
    }


def _arithmetic_certificate() -> dict[str, Any]:
    target_data = _target_carrier_data_cached()
    pairing_data = _pairing_data_cached()
    coordinate_data = _coordinate_map_data_cached()
    maximum_live_entry = max(
        [
            coordinate_data["full_physical_image_maximum_absolute_entry"],
            coordinate_data["coordinate_map_maximum_absolute_entry"],
        ]
        + [row["maximum_absolute_entry"] for row in target_data.values()]
        + [row["matrix_maximum_absolute_entry"] for row in pairing_data.values()]
    )
    modular_update_bound = (MODULAR_PRIME - 1) ** 2 + (
        MODULAR_PRIME - 1
    )
    conservative_product_bound = (
        SYMMETRIC_SQUARE_DIMENSION
        * maximum_live_entry
        * max(2, maximum_live_entry)
    )
    return {
        "storage_dtype": "signed int64",
        "Python_integer_sparse_aggregation_exact": True,
        "Fraction_based_constraint_denominator_clearing_exact": True,
        "modular_rational_reconstruction_verified_over_Z_exact": True,
        "checked_sparse_products_reject_unsafe_int64_bounds": True,
        "maximum_live_absolute_entry": maximum_live_entry,
        "conservative_live_product_absolute_bound": conservative_product_bound,
        "modular_row_update_absolute_bound": modular_update_bound,
        "signed_int64_maximum": INT64_MAX,
        "all_recorded_bounds_fit_signed_int64": bool(
            conservative_product_bound <= INT64_MAX
            and modular_update_bound <= INT64_MAX
        ),
        "proof_grade": bool(
            conservative_product_bound <= INT64_MAX
            and modular_update_bound <= INT64_MAX
        ),
    }


def _provenance_certificate(
    *,
    census_report: Mapping[str, Any],
    aligned_report: Mapping[str, Any],
) -> dict[str, Any]:
    census_path = Path(census.__file__).resolve()
    aligned_path = Path(aligned.__file__).resolve()
    intertwiner_path = Path(intertwiners.__file__).resolve()
    quadratic_path = Path(quadratics.__file__).resolve()
    census_source_hash = _file_sha256(census_path)
    aligned_source_hash = _file_sha256(aligned_path)
    intertwiner_source_hash = _file_sha256(intertwiner_path)
    quadratic_source_hash = _file_sha256(quadratic_path)
    census_report_hash = _canonical_json_sha256(census_report)
    census_scope = census_report.get("scope", {})
    census_provenance = census_report.get("source_provenance", {})
    aligned_scope = aligned_report.get("scope", {})
    exact = bool(
        census_path == ROOT / EXPECTED_CENSUS_MODULE
        and aligned_path == ROOT / EXPECTED_ALIGNED_MODULE
        and intertwiner_path == ROOT / EXPECTED_INTERTWINER_MODULE
        and quadratic_path == ROOT / EXPECTED_QUADRATIC_MODULE
        and census_source_hash == EXPECTED_CENSUS_SOURCE_SHA256
        and census_report_hash == EXPECTED_CENSUS_REPORT_SHA256
        and aligned_source_hash == EXPECTED_ALIGNED_SOURCE_SHA256
        and intertwiner_source_hash == EXPECTED_INTERTWINER_SOURCE_SHA256
        and quadratic_source_hash == EXPECTED_QUADRATIC_SOURCE_SHA256
        and census_provenance.get("quadratic_module")
        == EXPECTED_QUADRATIC_MODULE
        and census_provenance.get("quadratic_source_sha256")
        == EXPECTED_QUADRATIC_SOURCE_SHA256
        and census_provenance.get("quadratic_report_sha256")
        == EXPECTED_QUADRATIC_REPORT_SHA256
        and census_provenance.get("quadratic_basis_sha256")
        == EXPECTED_QUADRATIC_BASIS_SHA256
        and census_provenance.get("all_required_frozen_API_provenance_exact")
        is True
        and census_report.get("status") == EXPECTED_CENSUS_STATUS
        and census_report.get("overall_state") == EXPECTED_CENSUS_OVERALL_STATE
        and census_report.get("model_contract_id") == MODEL_CONTRACT_ID
        and census_report.get("n_failed") == 0
        and census_scope.get(
            "augmented_homogeneous_representation_census_constructed"
        )
        is True
        and census_scope.get("all_22_real_Hermitian_Schur_block_sizes_certified")
        is True
        and census_scope.get("Schur_coordinate_6585_by_19594_coefficient_matrix_constructed")
        is False
        and census_scope.get("physical_G3_gap_target_vector_constructed")
        is False
        and census_scope.get("physical_G3_gap_cubic_zero_RHS_certified")
        is False
        and aligned_report.get("status") == EXPECTED_ALIGNED_STATUS
        and aligned_report.get("model_contract_id") == MODEL_CONTRACT_ID
        and aligned_report.get("n_failed") == 0
        and aligned_scope.get("aligned_complexified_Phi210_carriers_constructed")
        is True
        and aligned_scope.get(
            "physical_real_structure_and_Gaussian_embeddings_constructed"
        )
        is True
        and tuple(census.schur_parameter_grade_counts())
        == (1, 4, 90, 1_414, 18_085)
        and tuple(census.target_invariant_grade_counts())
        == (1, 4, 45, 478, 6_057)
    )
    return {
        "model_contract_id": MODEL_CONTRACT_ID,
        "census_module": census_path.name,
        "census_source_sha256": census_source_hash,
        "expected_census_source_sha256": EXPECTED_CENSUS_SOURCE_SHA256,
        "census_report_sha256": census_report_hash,
        "expected_census_report_sha256": EXPECTED_CENSUS_REPORT_SHA256,
        "census_status": census_report.get("status"),
        "census_n_failed": census_report.get("n_failed"),
        "census_physical_G3_gap_target_vector_constructed": census_scope.get(
            "physical_G3_gap_target_vector_constructed"
        ),
        "census_physical_G3_gap_cubic_zero_RHS_certified": census_scope.get(
            "physical_G3_gap_cubic_zero_RHS_certified"
        ),
        "aligned_module": aligned_path.name,
        "aligned_source_sha256": aligned_source_hash,
        "expected_aligned_source_sha256": EXPECTED_ALIGNED_SOURCE_SHA256,
        "aligned_status": aligned_report.get("status"),
        "aligned_n_failed": aligned_report.get("n_failed"),
        "intertwiner_module": intertwiner_path.name,
        "intertwiner_source_sha256": intertwiner_source_hash,
        "expected_intertwiner_source_sha256": (
            EXPECTED_INTERTWINER_SOURCE_SHA256
        ),
        "quadratic_module": quadratic_path.name,
        "quadratic_source_sha256": quadratic_source_hash,
        "expected_quadratic_source_sha256": EXPECTED_QUADRATIC_SOURCE_SHA256,
        "quadratic_report_sha256": census_provenance.get(
            "quadratic_report_sha256"
        ),
        "expected_quadratic_report_sha256": EXPECTED_QUADRATIC_REPORT_SHA256,
        "quadratic_basis_sha256": census_provenance.get(
            "quadratic_basis_sha256"
        ),
        "expected_quadratic_basis_sha256": EXPECTED_QUADRATIC_BASIS_SHA256,
        "live_Schur_parameter_grade_counts": tuple(
            census.schur_parameter_grade_counts()
        ),
        "live_target_invariant_grade_counts": tuple(
            census.target_invariant_grade_counts()
        ),
        "all_required_frozen_provenance_exact": exact,
        "proof_grade": exact,
    }


def _build_report_from_evidence(
    *,
    provenance: Mapping[str, Any],
    targets: Mapping[str, Any],
    pairings: Mapping[str, Any],
    domain: Mapping[str, Any],
    cubic_map: Mapping[str, Any],
    arithmetic: Mapping[str, Any],
) -> dict[str, Any]:
    canonical_provenance = _provenance_certificate(
        census_report=census.build_report(),
        aligned_report=aligned.build_report(),
    )
    canonical_targets = _target_carrier_certificate()
    canonical_pairings = _pairing_certificate()
    canonical_domain = _domain_certificate()
    canonical_map = _map_certificate()
    canonical_arithmetic = _arithmetic_certificate()
    block_rows = domain.get("all_22_augmented_block_rows", ())
    checks = {
        "frozen_census_aligned_quadratic_and_intertwiner_provenance_exact": bool(
            provenance.get("proof_grade")
            and provenance.get("all_required_frozen_provenance_exact")
            and _canonical_json_sha256(provenance)
            == _canonical_json_sha256(canonical_provenance)
            and provenance.get("model_contract_id") == MODEL_CONTRACT_ID
            and provenance.get("census_source_sha256")
            == EXPECTED_CENSUS_SOURCE_SHA256
            and provenance.get("census_report_sha256")
            == EXPECTED_CENSUS_REPORT_SHA256
            and provenance.get("aligned_source_sha256")
            == EXPECTED_ALIGNED_SOURCE_SHA256
            and provenance.get("intertwiner_source_sha256")
            == EXPECTED_INTERTWINER_SOURCE_SHA256
            and provenance.get("quadratic_source_sha256")
            == EXPECTED_QUADRATIC_SOURCE_SHA256
            and provenance.get("quadratic_report_sha256")
            == EXPECTED_QUADRATIC_REPORT_SHA256
            and provenance.get("quadratic_basis_sha256")
            == EXPECTED_QUADRATIC_BASIS_SHA256
            and tuple(provenance.get("live_Schur_parameter_grade_counts", ()))
            == (1, 4, 90, 1_414, 18_085)
            and tuple(provenance.get("live_target_invariant_grade_counts", ()))
            == (1, 4, 45, 478, 6_057)
            and provenance.get(
                "census_physical_G3_gap_target_vector_constructed"
            )
            is False
            and provenance.get(
                "census_physical_G3_gap_cubic_zero_RHS_certified"
            )
            is False
        ),
        "all_required_Sym2_highest_weight_carriers_exact": bool(
            targets.get("proof_grade")
            and _canonical_json_sha256(targets)
            == _canonical_json_sha256(canonical_targets)
            and targets.get("irrep_family_count") == 10
            and targets.get("total_complex_carrier_copy_count") == 540
            and targets.get("total_isotypic_dimension") == 6_032
        ),
        "all_target_carriers_use_frozen_common_words_and_actions_exact": bool(
            targets.get("all_highest_vectors_raise_to_zero_exact") is True
            and targets.get(
                "all_common_lowering_word_carriers_have_full_rank_exact"
            )
            is True
            and targets.get(
                "all_reference_copies_intertwine_9_Chevalley_actions_exact"
            )
            is True
            and targets.get(
                "all_copies_aligned_by_exact_highest_weight_universality"
            )
            is True
        ),
        "all_ten_contragredient_pairings_exact": bool(
            pairings.get("proof_grade")
            and _canonical_json_sha256(pairings)
            == _canonical_json_sha256(canonical_pairings)
            and pairings.get("pairing_family_count") == 10
            and pairings.get("all_pairing_spaces_one_dimensional_exact") is True
            and pairings.get("all_15_compact_tensor_equations_exact") is True
        ),
        "all_1414_complexified_cross_tensors_constructed_exact": bool(
            domain.get("proof_grade")
            and _canonical_json_sha256(domain)
            == _canonical_json_sha256(canonical_domain)
            and domain.get("complexified_domain_basis_count")
            == COMPLEX_CUBIC_DOMAIN_DIMENSION
            and domain.get("observed_complexified_counts_by_irrep")
            == EXPECTED_COMPLEX_DOMAIN_COUNTS
        ),
        "physical_realification_rank_1414_exact": bool(
            domain.get("physical_basis_count") == REAL_CUBIC_DOMAIN_DIMENSION
            and domain.get(
                "all_multiplications_commute_with_physical_conjugation_exact"
            )
            is True
            and domain.get(
                "all_selected_vectors_satisfy_physical_real_structure_exact"
            )
            is True
        ),
        "all_22_real_Hermitian_block_rows_and_1414_variables_exact": bool(
            len(block_rows) == 22
            and domain.get("all_22_block_provenance_rows_exact") is True
            and domain.get("nonzero_cubic_block_count") == 7
            and sum(
                int(row.get("constructed_physical_basis_variable_count", 0))
                for row in block_rows
            )
            == REAL_CUBIC_DOMAIN_DIMENSION
        ),
        "explicit_integer_478_by_1414_coordinate_map_exact": bool(
            cubic_map.get("proof_grade")
            and _canonical_json_sha256(cubic_map)
            == _canonical_json_sha256(canonical_map)
            and tuple(cubic_map.get("coordinate_map_shape", ()))
            == (CUBIC_TARGET_DIMENSION, REAL_CUBIC_DOMAIN_DIMENSION)
        ),
        "exact_rank_478_and_kernel_936_certified": bool(
            cubic_map.get("rank_mod_prime") == CUBIC_TARGET_DIMENSION
            and cubic_map.get("selected_minor_rank_mod_prime")
            == CUBIC_TARGET_DIMENSION
            and cubic_map.get("selected_minor_determinant_nonzero_mod_prime")
            is True
            and cubic_map.get("exact_rank") == CUBIC_TARGET_DIMENSION
            and cubic_map.get("exact_kernel_dimension") == CUBIC_KERNEL_DIMENSION
        ),
        "abstract_478_coordinate_zero_placeholder_exact_and_nonphysical": bool(
            cubic_map.get(
                "all_478_abstract_interface_placeholder_entries_zero_exact"
            )
            is True
            and cubic_map.get(
                "abstract_zero_placeholder_is_not_a_physical_G3_target"
            )
            is True
            and tuple(
                cubic_map.get("abstract_zero_interface_placeholder_shape", ())
            )
            == (CUBIC_TARGET_DIMENSION,)
            and cubic_map.get("abstract_zero_interface_placeholder_nnz") == 0
            and cubic_map.get("physical_G3_gap_target_vector_constructed")
            is False
            and cubic_map.get("physical_G3_gap_cubic_zero_RHS_certified")
            is False
        ),
        "integer_rational_and_modular_arithmetic_safety_exact": bool(
            arithmetic.get("proof_grade")
            and _canonical_json_sha256(arithmetic)
            == _canonical_json_sha256(canonical_arithmetic)
            and arithmetic.get("all_recorded_bounds_fit_signed_int64") is True
        ),
        "full_SDP_and_G3_absence_declared_fail_closed": bool(
            cubic_map.get(
                "abstract_zero_placeholder_is_not_a_physical_G3_target"
            )
            is True
            and cubic_map.get("physical_G3_gap_target_vector_constructed")
            is False
            and cubic_map.get("physical_G3_gap_cubic_zero_RHS_certified")
            is False
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    ready = not failures
    return {
        "status": STATUS if ready else "RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_EXECUTION_FAILED",
        "overall_state": OVERALL_STATE if ready else "EXECUTION_FAIL",
        "model_contract_id": MODEL_CONTRACT_ID,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "source_provenance": copy.deepcopy(provenance),
        "Sym2_target_carriers": copy.deepcopy(targets),
        "contragredient_pairings": copy.deepcopy(pairings),
        "physical_cubic_domain": copy.deepcopy(domain),
        "cubic_coordinate_map": copy.deepcopy(cubic_map),
        "exact_arithmetic_safety": copy.deepcopy(arithmetic),
        "public_exact_APIs": {
            "coordinate_map": "exact_cubic_coordinate_map()",
            "abstract_zero_interface_placeholder": (
                "abstract_zero_cubic_interface_placeholder()"
            ),
            "domain_metadata": "cubic_domain_basis_metadata()",
            "target_metadata": "cubic_target_coordinate_metadata()",
            "map_convention": (
                "478 abstract coefficient pivots by 1414 real-structure-fixed "
                "Schur cross variables, including the off-diagonal Gram factor two"
            ),
        },
        "scope": {
            "H_fixed_to_h_minus": ready,
            "Sigma_fixed_to_q_over_4": ready,
            "rank1_endpoint_SU4_stabilizer_used": ready,
            "all_1414_real_structure_fixed_cubic_Schur_cross_variables_constructed": ready,
            "explicit_478_by_1414_cubic_coordinate_map_constructed": ready,
            "cubic_map_rank_478_and_kernel_dimension_936_exact": ready,
            "abstract_478_coordinate_zero_placeholder_available": ready,
            "degree_zero_coefficient_map_constructed": False,
            "degree_one_coefficient_map_constructed": False,
            "degree_two_coefficient_map_constructed": False,
            "degree_four_coefficient_map_constructed": False,
            "full_6585_by_19594_Schur_coordinate_matrix_constructed": False,
            "physical_G3_gap_target_vector_constructed": False,
            "physical_G3_gap_cubic_zero_RHS_certified": False,
            "augmented_Schur_SOS_SDP_constructed": False,
            "augmented_Schur_SOS_SDP_feasibility_certified": False,
            "augmented_Schur_SOS_SDP_infeasibility_certified": False,
            "arbitrary_real_Phi_lower_bound_proved": False,
            "arbitrary_rank1_Phi_proved": False,
            "G3_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "next_exact_target": (
            "Construct the remaining exact Schur coefficient maps, especially "
            "the 18,085-to-6,057 quartic sector, then bind the physical gap "
            "target and solve/rationalize the complete 22-block PSD system."
        ),
        "verdict": (
            "The complete cubic Schur interface is now explicit and exact: all "
            "1,414 real-structure-fixed cross variables map through a certified integer "
            "478 by 1,414 matrix of exact rank 478 and kernel dimension 936, "
            "with a reserved abstract zero placeholder for its 478-coordinate "
            "interface. No physical G3 target or physical cubic-zero statement "
            "is constructed. The other graded maps, full PSD feasibility, "
            "arbitrary-Phi bound, and G3 remain open."
            if ready
            else "The cubic Schur-interface audit failed closed; no SDP or G3 conclusion is certified."
        ),
    }


@lru_cache(maxsize=1)
def _build_report_cached() -> dict[str, Any]:
    provenance = _provenance_certificate(
        census_report=census.build_report(),
        aligned_report=aligned.build_report(),
    )
    return _build_report_from_evidence(
        provenance=provenance,
        targets=_target_carrier_certificate(),
        pairings=_pairing_certificate(),
        domain=_domain_certificate(),
        cubic_map=_map_certificate(),
        arithmetic=_arithmetic_certificate(),
    )


def build_report() -> dict[str, Any]:
    return copy.deepcopy(_build_report_cached())


def render_markdown(report: Mapping[str, Any]) -> str:
    targets = report["Sym2_target_carriers"]
    domain = report["physical_cubic_domain"]
    cubic_map = report["cubic_coordinate_map"]
    block_lines = [
        "| SU(4) block | kind | `m(tPhi)` | `m(Phi2)` | variables | built |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in domain["all_22_augmented_block_rows"]:
        block_lines.append(
            "| `{}` | {} | {} | {} | {} | {} |".format(
                tuple(row["representative_dynkin"]),
                row["real_block_kind"],
                row["tPhi_multiplicity"],
                row["Phi2_multiplicity"],
                row["expected_cubic_cross_real_parameter_count"],
                row["constructed_physical_basis_variable_count"],
            )
        )
    return "\n".join(
        [
            "# Exact rank-one SU(4) augmented cubic Schur map -- v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "## Exact construction",
            "",
            f"- required `Sym2(Phi210)` carrier copies: `{targets['total_complex_carrier_copy_count']}` "
            f"across `{targets['irrep_family_count']}` irreducible families;",
            f"- real-structure-fixed cubic Schur variables: `{domain['physical_basis_count']:,}`;",
            f"- coordinate matrix: `{tuple(cubic_map['coordinate_map_shape'])}`, "
            f"`{cubic_map['coordinate_map_nnz']:,}` nonzero entries, SHA-256 "
            f"`{cubic_map['coordinate_map_sha256']}`;",
            f"- exact rank: `{cubic_map['exact_rank']}`; exact kernel dimension: "
            f"`{cubic_map['exact_kernel_dimension']}`;",
            "- reserved abstract zero interface placeholder: "
            f"`{cubic_map['abstract_zero_interface_placeholder_nnz']}` nonzero "
            f"entries among `{CUBIC_TARGET_DIMENSION}` coordinates.",
            "",
            "The reserved zero placeholder is not a physical G3 target. This "
            "certificate neither constructs the physical target nor certifies "
            "that its cubic right-hand side vanishes.",
            "",
            "The matrix uses the symmetric Gram convention `z^T Q z`, so the "
            "off-diagonal `t*Phi <-> Phi2` multiplier two is already included.",
            "",
            "## All 22 real/Hermitian block rows",
            "",
            *block_lines,
            "",
            "## Exact rank proof",
            "",
            cubic_map["rank_argument"],
            "",
            "## Deliberate open scope",
            "",
            "This cubic interface does not construct the other four graded "
            "coefficient maps, the complete 6,585 by 19,594 matrix, the physical "
            "G3 target, or any PSD feasibility/infeasibility certificate. "
            "The arbitrary-Phi bound and G3 therefore remain open.",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, default=OUT_JSON)
    parser.add_argument("--markdown", type=Path, default=OUT_MD)
    arguments = parser.parse_args(argv)
    report = build_report()
    arguments.json.write_text(
        json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    arguments.markdown.write_text(render_markdown(report), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_checks": report["n_checks"],
                "n_failed": report["n_failed"],
                "map_shape": report["cubic_coordinate_map"][
                    "coordinate_map_shape"
                ],
                "exact_rank": report["cubic_coordinate_map"]["exact_rank"],
                "exact_kernel_dimension": report["cubic_coordinate_map"][
                    "exact_kernel_dimension"
                ],
                "G3_closed": report["scope"]["G3_closed"],
            },
            sort_keys=True,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
