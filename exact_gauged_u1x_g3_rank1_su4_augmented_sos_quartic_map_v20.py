#!/usr/bin/env python3
"""Exact quartic Schur coefficient-map experiment for the rank-one SU(4) slice.

This deliberately isolated module constructs only the homogeneous Phi^4
coefficient map of the SU(4)-adapted Schur Gram ansatz.  It builds every
irreducible carrier in Sym^2(Phi210), equips each representative with the
positive invariant component metric induced by the physical real structure,
and streams the 18,085 real Schur parameters into quartic coefficient space.

The output chart consists of 6,057 selected raw quartic coefficients.  Full
row rank is certified by one sparse finite-field elimination and independently
checked on the selected square minor at a second prime.  No physical G3 target,
semidefinite solve, arbitrary-Phi statement, or G3 conclusion is constructed.
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
from typing import Any, Iterable, Iterator, Mapping, Sequence

import numpy as np
from scipy import sparse

import exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20 as census
import exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20 as cubic


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.json"
OUT_MD = ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.md"

MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
STATUS = "EXACT_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_CERTIFIED"
OVERALL_STATE = "SU4_AUGMENTED_QUARTIC_MAP_CLOSED__PHYSICAL_TARGET_SDP_AND_G3_OPEN"

PHI_DIMENSION = 210
SYMMETRIC_SQUARE_DIMENSION = 22_155
COMPLEX_ISOTYPIC_TYPE_COUNT = 35
IRREDUCIBLE_COPY_COUNT = 798
REAL_BLOCK_COUNT = 22
QUARTIC_DOMAIN_DIMENSION = 18_085
QUARTIC_TARGET_DIMENSION = 6_057
QUARTIC_KERNEL_DIMENSION = 12_028
FIRST_MODULAR_PRIME = 1_000_003
SECOND_MODULAR_PRIME = 1_000_033
INT64_MAX = int(np.iinfo(np.int64).max)
SIMPLE_ROOTS = ((2, -1, 0), (-1, 2, -1), (0, -1, 2))
EXPECTED_COORDINATE_MAP_SHA256 = (
    "ebb7b8b5cbca5d1c6e1f41d1e83e7229e2b885ec4fd34e23f305c788a4a1eb9b"
)
EXPECTED_FULL_IMAGE_STREAM_SHA256 = (
    "4807d170ed880cb4bcccaed29d054826d136d0057326fe2d1b252e1ff109422d"
)

EXPECTED_CENSUS_SOURCE_SHA256 = (
    "3e0d7f2eac73eec950960f1ffd78c9584a4b15d070c84889080cf4c67d5a4d63"
)
EXPECTED_CUBIC_SOURCE_SHA256 = (
    "589952b9b0a0b6af1543b87c89b0f3626a4bfb9c4219821a915fe04fab8af690"
)

DynkinWeight = tuple[int, int, int]
SparseVector = dict[int, int]


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
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


def _maximum_abs(value: sparse.spmatrix | np.ndarray) -> int:
    data = value.data if sparse.issparse(value) else np.asarray(value).reshape(-1)
    return max((abs(int(item)) for item in data), default=0)


def _max_row_nnz(matrix: sparse.spmatrix) -> int:
    value = matrix.tocsr()
    counts = np.diff(value.indptr)
    return int(counts.max()) if counts.size else 0


def _python_sparse_matmul(
    left: sparse.spmatrix, right: sparse.spmatrix, context: str
) -> sparse.csr_matrix:
    """Exact fallback when a conservative int64 product bound is unsafe."""
    lhs = left.tocsr()
    rhs = right.tocsr()
    rows: list[int] = []
    columns: list[int] = []
    values: list[int] = []
    for row in range(lhs.shape[0]):
        accumulator: dict[int, int] = {}
        for pointer in range(lhs.indptr[row], lhs.indptr[row + 1]):
            middle = int(lhs.indices[pointer])
            scale = int(lhs.data[pointer])
            for target in range(rhs.indptr[middle], rhs.indptr[middle + 1]):
                column = int(rhs.indices[target])
                accumulator[column] = accumulator.get(column, 0) + scale * int(
                    rhs.data[target]
                )
        for column, coefficient in sorted(accumulator.items()):
            if coefficient:
                if abs(coefficient) > INT64_MAX:
                    raise ArithmeticError(f"{context} result exceeds signed int64")
                rows.append(row)
                columns.append(column)
                values.append(coefficient)
    return sparse.coo_matrix(
        (values, (rows, columns)), shape=(lhs.shape[0], rhs.shape[1]), dtype=np.int64
    ).tocsr()


def _safe_sparse_matmul(
    left: sparse.spmatrix, right: sparse.spmatrix, context: str
) -> sparse.csr_matrix:
    if left.shape[1] != right.shape[0]:
        raise ValueError(f"{context} has incompatible shapes")
    overlap = min(_max_row_nnz(left), _max_row_nnz(right.T))
    bound = overlap * _maximum_abs(left) * _maximum_abs(right)
    if bound <= INT64_MAX:
        output = (left.astype(np.int64) @ right.astype(np.int64)).tocsr()
        output.sum_duplicates()
        output.eliminate_zeros()
        if output.dtype != np.int64:
            raise ArithmeticError(f"{context} lost exact int64 storage")
        return output
    return _python_sparse_matmul(left, right, context)


def _weight_after_word(highest: DynkinWeight, word: Sequence[int]) -> DynkinWeight:
    output = list(highest)
    for root_index in word:
        root = SIMPLE_ROOTS[int(root_index)]
        output = [output[axis] - root[axis] for axis in range(3)]
    return tuple(output)  # type: ignore[return-value]


class _SparseModularBasis:
    """Insertion-only sparse column echelon basis over one prime field."""

    def __init__(self, prime: int) -> None:
        if prime <= 2 or (prime - 1) ** 2 + (prime - 1) > INT64_MAX:
            raise ArithmeticError("unsafe modular elimination prime")
        self.prime = int(prime)
        self.rows: dict[int, dict[int, int]] = {}
        self.fill = 0
        self.maximum_vector_nnz = 0

    @property
    def rank(self) -> int:
        return len(self.rows)

    def insert(self, raw: Mapping[int, int]) -> tuple[bool, int | None]:
        prime = self.prime
        vector = {
            int(coordinate): int(coefficient) % prime
            for coordinate, coefficient in raw.items()
            if int(coefficient) % prime
        }
        while vector:
            pivot = min(vector)
            coefficient = vector[pivot]
            existing = self.rows.get(pivot)
            if existing is None:
                inverse = pow(coefficient, -1, prime)
                normalized = {
                    coordinate: (value * inverse) % prime
                    for coordinate, value in vector.items()
                    if (value * inverse) % prime
                }
                self.rows[pivot] = normalized
                self.fill += len(normalized)
                self.maximum_vector_nnz = max(
                    self.maximum_vector_nnz, len(normalized)
                )
                return True, pivot
            for coordinate, value in existing.items():
                updated = (vector.get(coordinate, 0) - coefficient * value) % prime
                if updated:
                    vector[coordinate] = updated
                else:
                    vector.pop(coordinate, None)
        return False, None


def _column_dictionary(column: sparse.spmatrix) -> SparseVector:
    value = column.tocsc()
    if value.shape[1] != 1:
        raise ValueError("expected one sparse column")
    return {
        int(row): int(coefficient)
        for row, coefficient in zip(value.indices, value.data, strict=True)
        if coefficient
    }


def _deterministic_lowering_words(
    highest: sparse.spmatrix, dimension: int
) -> tuple[tuple[tuple[int, ...], ...], tuple[sparse.csr_matrix, ...]]:
    seed = highest.tocsr()
    basis = _SparseModularBasis(FIRST_MODULAR_PRIME)
    inserted, _ = basis.insert(_column_dictionary(seed))
    if not inserted:
        raise ArithmeticError("zero highest-weight seed")
    words: list[tuple[int, ...]] = [()]
    vectors: list[sparse.csr_matrix] = [seed]
    queue = 0
    lowering = cubic._sym2_chevalley_actions_cached()["lowering"]
    while len(vectors) < dimension and queue < len(vectors):
        for root in range(3):
            candidate = cubic._checked_sparse_matmul(
                lowering[root],
                vectors[queue],
                "common lowering-word action",
                left_maximum=2,
            )
            if not candidate.nnz:
                continue
            independent, _ = basis.insert(_column_dictionary(candidate))
            if independent:
                words.append(words[queue] + (root,))
                vectors.append(candidate)
                if len(vectors) == dimension:
                    break
        queue += 1
    if len(vectors) != dimension:
        raise ArithmeticError(
            f"lowering words span {len(vectors)} rather than {dimension}"
        )
    return tuple(words), tuple(vectors)


def _apply_lowering_word(
    highest: sparse.spmatrix, word: Sequence[int]
) -> sparse.csr_matrix:
    output = highest.tocsr()
    lowering = cubic._sym2_chevalley_actions_cached()["lowering"]
    for root in word:
        output = cubic._checked_sparse_matmul(
            lowering[int(root)],
            output,
            "carrier lowering-word action",
            left_maximum=2,
        )
    return output


@lru_cache(maxsize=1)
def _carrier_family_data_cached() -> dict[DynkinWeight, dict[str, Any]]:
    decomposition = census.exact_character_decompositions()["Sym2_Phi210"]
    columns_by_weight = cubic._sym2_columns_by_weight_cached()
    raising = cubic._sym2_chevalley_actions_cached()["raising"]
    output: dict[DynkinWeight, dict[str, Any]] = {}
    for highest in sorted(decomposition):
        multiplicity = int(decomposition[highest])
        source_columns = columns_by_weight[highest]
        blocks: list[sparse.spmatrix] = []
        for root, action in zip(SIMPLE_ROOTS, raising, strict=True):
            target_weight = tuple(highest[axis] + root[axis] for axis in range(3))
            target_rows = columns_by_weight.get(target_weight, ())
            blocks.append(action[target_rows, :][:, source_columns])
        constraints = sparse.vstack(blocks, format="csr")
        constraints.sum_duplicates()
        constraints.eliminate_zeros()
        local, free_columns, maximum_denominator = cubic._exact_integer_nullspace(
            constraints, multiplicity
        )
        alternate_rank = cubic._rank_mod_prime(
            constraints.toarray(), SECOND_MODULAR_PRIME
        )
        if constraints.shape[1] - alternate_rank != multiplicity:
            raise ArithmeticError("alternate-prime highest-weight nullity drifted")
        nonzero_rows, nonzero_columns = np.nonzero(local)
        embedded = sparse.csc_matrix(
            (
                local[nonzero_rows, nonzero_columns],
                (
                    np.asarray(source_columns, dtype=np.int64)[nonzero_rows],
                    nonzero_columns,
                ),
            ),
            shape=(SYMMETRIC_SQUARE_DIMENSION, multiplicity),
            dtype=np.int64,
        )
        dimension = int(census._weyl_dimension(highest))
        words, reference_vectors = _deterministic_lowering_words(
            embedded[:, 0], dimension
        )
        copies: list[sparse.csr_matrix] = []
        for copy_index in range(multiplicity):
            if copy_index == 0:
                basis = sparse.hstack(reference_vectors, format="csr")
            else:
                basis = sparse.hstack(
                    [
                        _apply_lowering_word(embedded[:, copy_index], word)
                        for word in words
                    ],
                    format="csr",
                )
            copies.append(basis)
        concatenated = sparse.hstack(copies, format="csr")
        output[highest] = {
            "highest_weight": highest,
            "dimension": dimension,
            "copy_count": multiplicity,
            "constraint_shape": constraints.shape,
            "constraint_nnz": constraints.nnz,
            "constraint_sha256": _sparse_matrix_sha256(constraints),
            "nullity": len(free_columns),
            "alternate_prime_rank": alternate_rank,
            "alternate_prime_nullity": constraints.shape[1] - alternate_rank,
            "maximum_rational_reconstruction_denominator": maximum_denominator,
            "lowering_words": words,
            "lowering_word_weights": tuple(
                _weight_after_word(highest, word) for word in words
            ),
            "copies": tuple(copies),
            "concatenated_shape": concatenated.shape,
            "concatenated_nnz": concatenated.nnz,
            "concatenated_maximum_absolute_entry": _maximum_abs(concatenated),
            "concatenated_sha256": _sparse_matrix_sha256(concatenated),
            "raising_residual_zero_exact": all(
                not (action @ embedded).nnz for action in raising
            ),
        }
    if len(output) != COMPLEX_ISOTYPIC_TYPE_COUNT:
        raise ArithmeticError("complex isotypic family count drifted")
    if sum(row["copy_count"] for row in output.values()) != IRREDUCIBLE_COPY_COUNT:
        raise ArithmeticError("irreducible-copy census drifted")
    if sum(
        row["dimension"] * row["copy_count"] for row in output.values()
    ) != SYMMETRIC_SQUARE_DIMENSION:
        raise ArithmeticError("carrier dimensions do not exhaust Sym2(Phi210)")
    return output


def exact_carrier_family_data() -> dict[DynkinWeight, dict[str, Any]]:
    """Return a mutation-isolated copy of all 35 exact carrier families."""
    return copy.deepcopy(_carrier_family_data_cached())


@lru_cache(maxsize=1)
def _sym2_metric_diagonal_cached() -> np.ndarray:
    diagonal = np.asarray(
        [2 if left == right else 1 for left, right in cubic._quadratic_pairs_cached()],
        dtype=np.int64,
    )
    diagonal.setflags(write=False)
    return diagonal


@lru_cache(maxsize=1)
def _sym2_conjugation_cached() -> sparse.csr_matrix:
    images, signs = cubic._physical_conjugation_permutation_cached()
    pair_index = cubic._quadratic_pair_index_cached()
    rows: list[int] = []
    coefficients: list[int] = []
    for left, right in cubic._quadratic_pairs_cached():
        rows.append(int(pair_index[images[left], images[right]]))
        coefficients.append(int(signs[left]) * int(signs[right]))
    output = sparse.coo_matrix(
        (
            coefficients,
            (rows, np.arange(SYMMETRIC_SQUARE_DIMENSION, dtype=np.int64)),
        ),
        shape=(SYMMETRIC_SQUARE_DIMENSION, SYMMETRIC_SQUARE_DIMENSION),
        dtype=np.int64,
    ).tocsr()
    residual = output @ output - sparse.eye(
        SYMMETRIC_SQUARE_DIMENSION, dtype=np.int64, format="csr"
    )
    residual.eliminate_zeros()
    if residual.nnz:
        raise ArithmeticError("induced Sym2 physical conjugation is not involutive")
    return output


def _inverse_fraction_matrix(matrix: np.ndarray) -> list[list[Fraction]]:
    value = np.asarray(matrix, dtype=np.int64)
    dimension = value.shape[0]
    if value.shape != (dimension, dimension):
        raise ValueError("exact inversion requires a square matrix")
    work = [
        [Fraction(int(value[row, column])) for column in range(dimension)]
        + [Fraction(int(row == column)) for column in range(dimension)]
        for row in range(dimension)
    ]
    for column in range(dimension):
        pivot = next(
            (row for row in range(column, dimension) if work[row][column]), None
        )
        if pivot is None:
            raise ArithmeticError("component metric is singular")
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [entry / scale for entry in work[column]]
        for row in range(dimension):
            if row == column or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                left - scale * right
                for left, right in zip(work[row], work[column], strict=True)
            ]
    return [row[dimension:] for row in work]


def _primitive_inverse_by_weight_blocks(
    metric: np.ndarray, weights: Sequence[DynkinWeight]
) -> tuple[np.ndarray, int]:
    dimension = metric.shape[0]
    if metric.shape != (dimension, dimension) or len(weights) != dimension:
        raise ValueError("component metric metadata mismatch")
    groups: defaultdict[DynkinWeight, list[int]] = defaultdict(list)
    for index, weight in enumerate(weights):
        groups[weight].append(index)
    for left in range(dimension):
        for right in range(dimension):
            if weights[left] != weights[right] and int(metric[left, right]):
                raise ArithmeticError("component metric mixed distinct weights")
    inverse = [[Fraction(0) for _ in range(dimension)] for _ in range(dimension)]
    for indices in groups.values():
        block = metric[np.ix_(indices, indices)]
        block_inverse = _inverse_fraction_matrix(block)
        for local_left, global_left in enumerate(indices):
            for local_right, global_right in enumerate(indices):
                inverse[global_left][global_right] = block_inverse[local_left][
                    local_right
                ]
    denominator = 1
    for row in inverse:
        for entry in row:
            denominator = math.lcm(denominator, entry.denominator)
    integers = np.asarray(
        [[int(entry * denominator) for entry in row] for row in inverse],
        dtype=object,
    )
    content = 0
    for entry in integers.reshape(-1):
        content = math.gcd(content, abs(int(entry)))
    if not content:
        raise ArithmeticError("zero inverse metric")
    integers = integers // content
    denominator //= content
    flat = [int(entry) for entry in integers.reshape(-1)]
    if any(abs(entry) > INT64_MAX for entry in flat):
        raise ArithmeticError("primitive inverse metric exceeds signed int64")
    output = np.asarray(flat, dtype=np.int64).reshape(dimension, dimension)
    if not np.array_equal(output, output.T):
        raise ArithmeticError("primitive inverse metric is not symmetric")
    exact_product = np.asarray(metric, dtype=object) @ np.asarray(output, dtype=object)
    expected = np.eye(dimension, dtype=object) * denominator
    if not np.array_equal(exact_product, expected):
        raise ArithmeticError("primitive inverse metric identity failed")
    return output, denominator


@lru_cache(maxsize=1)
def _pairing_data_cached() -> dict[DynkinWeight, dict[str, Any]]:
    carriers = _carrier_family_data_cached()
    metric_diagonal = _sym2_metric_diagonal_cached()
    output: dict[DynkinWeight, dict[str, Any]] = {}
    for block in census.exact_augmented_isotypic_blocks():
        representative = tuple(block["representative_dynkin"])
        family = carriers[representative]
        reference = family["copies"][0].tocsr()
        weighted = reference.multiply(metric_diagonal[:, None])
        metric_sparse = _safe_sparse_matmul(
            reference.T, weighted, "irreducible component metric"
        )
        metric = metric_sparse.toarray().astype(np.int64, copy=False)
        pairing, inverse_denominator = _primitive_inverse_by_weight_blocks(
            metric, family["lowering_word_weights"]
        )
        output[representative] = {
            "representative_dynkin": representative,
            "conjugate_dynkin": tuple(block["conjugate_dynkin"]),
            "self_conjugate": bool(block["self_conjugate"]),
            "real_block_kind": block["real_block_kind"],
            "dimension": family["dimension"],
            "copy_count": family["copy_count"],
            "component_metric": metric,
            "component_metric_sha256": hashlib.sha256(
                np.ascontiguousarray(metric, dtype="<i8").tobytes()
            ).hexdigest(),
            "pairing": pairing,
            "pairing_sha256": hashlib.sha256(
                np.ascontiguousarray(pairing, dtype="<i8").tobytes()
            ).hexdigest(),
            "pairing_nnz": int(np.count_nonzero(pairing)),
            "pairing_maximum_absolute_entry": _maximum_abs(pairing),
            "rational_inverse_denominator": inverse_denominator,
            "positive_inverse_metric_normalization_exact": bool(
                inverse_denominator > 0
            ),
        }
    if len(output) != REAL_BLOCK_COUNT:
        raise ArithmeticError("real Schur block count drifted")
    return output


def exact_pairing_data() -> dict[DynkinWeight, dict[str, Any]]:
    """Return mutation-isolated positive pairings for all 22 real blocks."""
    return copy.deepcopy(_pairing_data_cached())


def _encode_quartic(indices: Sequence[int]) -> int:
    if len(indices) != 4:
        raise ValueError("a quartic monomial requires four indices")
    ordered = sorted(int(index) for index in indices)
    if ordered[0] < 0 or ordered[-1] >= PHI_DIMENSION:
        raise ValueError("quartic monomial index outside Phi210")
    output = 0
    for index in ordered:
        output = output * PHI_DIMENSION + index
    return output


def _decode_quartic(coordinate: int) -> tuple[int, int, int, int]:
    value = int(coordinate)
    if value < 0 or value >= PHI_DIMENSION**4:
        raise ValueError("invalid encoded quartic coordinate")
    output = [0, 0, 0, 0]
    for position in range(3, -1, -1):
        value, output[position] = divmod(value, PHI_DIMENSION)
    if output != sorted(output):
        raise ArithmeticError("encoded quartic coordinate is not canonical")
    return tuple(output)  # type: ignore[return-value]


def _combine_vectors(
    left: Mapping[int, int], right: Mapping[int, int], right_scale: int
) -> SparseVector:
    output = {int(key): int(value) for key, value in left.items() if value}
    for key, value in right.items():
        updated = output.get(int(key), 0) + int(right_scale) * int(value)
        if updated:
            output[int(key)] = updated
        else:
            output.pop(int(key), None)
    return output


def _conjugate_quartic_vector(vector: Mapping[int, int]) -> SparseVector:
    images, signs = cubic._physical_conjugation_permutation_cached()
    output: SparseVector = {}
    for coordinate, coefficient in vector.items():
        monomial = _decode_quartic(int(coordinate))
        target_indices = tuple(images[index] for index in monomial)
        target = _encode_quartic(target_indices)
        value = int(coefficient)
        for index in monomial:
            value *= int(signs[index])
        output[target] = output.get(target, 0) + value
        if not output[target]:
            del output[target]
    return output


@lru_cache(maxsize=None)
def _left_paired_carrier(
    representative: DynkinWeight, copy_index: int
) -> sparse.csr_matrix:
    family = _carrier_family_data_cached()[representative]
    carrier = family["copies"][int(copy_index)]
    pairing = sparse.csr_matrix(_pairing_data_cached()[representative]["pairing"])
    return _safe_sparse_matmul(carrier, pairing, "left paired Sym2 carrier")


@lru_cache(maxsize=None)
def _conjugate_carrier(
    representative: DynkinWeight, copy_index: int
) -> sparse.csr_matrix:
    carrier = _carrier_family_data_cached()[representative]["copies"][
        int(copy_index)
    ]
    return _safe_sparse_matmul(
        _sym2_conjugation_cached(), carrier, "physical conjugate Sym2 carrier"
    )


def _raw_invariant_tensor(
    representative: DynkinWeight, left: int, right: int
) -> sparse.csr_matrix:
    return _safe_sparse_matmul(
        _left_paired_carrier(representative, int(left)),
        _conjugate_carrier(representative, int(right)).T,
        "quartic invariant carrier tensor",
    )


def _multiply_tensor_to_quartic(tensor: sparse.spmatrix) -> SparseVector:
    pairs = cubic._quadratic_pairs_cached()
    weights = cubic._sym2_weights_cached()
    value = tensor.tocoo()
    output: SparseVector = {}
    for row, column, coefficient in zip(
        value.row, value.col, value.data, strict=True
    ):
        left_weight = weights[int(row)]
        right_weight = weights[int(column)]
        if any(left_weight[axis] + right_weight[axis] for axis in range(3)):
            raise ArithmeticError("invariant carrier tensor left weight zero sector")
        coordinate = _encode_quartic(pairs[int(row)] + pairs[int(column)])
        updated = output.get(coordinate, 0) + int(coefficient)
        if updated:
            if abs(updated) > INT64_MAX:
                raise ArithmeticError("quartic coefficient exceeds signed int64")
            output[coordinate] = updated
        else:
            output.pop(coordinate, None)
    return output


@lru_cache(maxsize=1)
def _sym2_conjugation_permutation_cached() -> tuple[tuple[int, ...], tuple[int, ...]]:
    matrix = _sym2_conjugation_cached().tocsc()
    images: list[int] = []
    signs: list[int] = []
    for column in range(SYMMETRIC_SQUARE_DIMENSION):
        start, stop = matrix.indptr[column], matrix.indptr[column + 1]
        if stop - start != 1:
            raise ArithmeticError("Sym2 conjugation ceased to be monomial")
        images.append(int(matrix.indices[start]))
        signs.append(int(matrix.data[start]))
    return tuple(images), tuple(signs)


def _symmetric_tensor_vector(tensor: sparse.spmatrix) -> SparseVector:
    """Project an ordered tensor to exact Sym2(Sym2(Phi)) coordinates."""
    value = tensor.tocoo()
    output: SparseVector = {}
    for row, column, coefficient in zip(
        value.row, value.col, value.data, strict=True
    ):
        left, right = sorted((int(row), int(column)))
        coordinate = left * SYMMETRIC_SQUARE_DIMENSION + right
        updated = output.get(coordinate, 0) + int(coefficient)
        if updated:
            output[coordinate] = updated
        else:
            output.pop(coordinate, None)
    return output


def _conjugate_symmetric_tensor_vector(
    vector: Mapping[int, int]
) -> SparseVector:
    images, signs = _sym2_conjugation_permutation_cached()
    output: SparseVector = {}
    for coordinate, coefficient in vector.items():
        left, right = divmod(int(coordinate), SYMMETRIC_SQUARE_DIMENSION)
        image_left, image_right = images[left], images[right]
        target_left, target_right = sorted((image_left, image_right))
        target = target_left * SYMMETRIC_SQUARE_DIMENSION + target_right
        value = int(coefficient) * int(signs[left]) * int(signs[right])
        output[target] = output.get(target, 0) + value
        if not output[target]:
            del output[target]
    return output


@lru_cache(maxsize=None)
def _self_block_physical_recipes_cached(
    representative: DynkinWeight,
) -> tuple[dict[str, Any], ...]:
    """Find the exact physical fixed basis for one real-type multiplicity block.

    The highest-weight nullspace basis is not assumed to be fixed by physical
    conjugation.  We first select a complex basis in Sym2(Sym2(Phi)), then
    select its plus and i-minus fixed vectors.  This is the same fail-closed
    realification principle used by the audited cubic map.
    """
    block = next(
        row
        for row in _block_specs_cached()
        if row["representative_dynkin"] == representative
    )
    if not block["self_conjugate"]:
        raise ValueError("physical fixed recipes are only for real-type blocks")
    multiplicity = int(block["multiplicity"])
    expected = multiplicity * (multiplicity + 1) // 2
    complex_basis = _SparseModularBasis(FIRST_MODULAR_PRIME)
    complex_records: list[dict[str, Any]] = []
    for left in range(multiplicity):
        for right in range(multiplicity):
            tensor_vector = _symmetric_tensor_vector(
                _raw_invariant_tensor(representative, left, right)
            )
            independent, _ = complex_basis.insert(tensor_vector)
            if independent:
                complex_records.append(
                    {
                        "left_copy_index": left,
                        "right_copy_index": right,
                        "tensor_vector": tensor_vector,
                    }
                )
                if complex_basis.rank == expected:
                    break
        if complex_basis.rank == expected:
            break
    if complex_basis.rank != expected:
        raise ArithmeticError("real-type complex symmetric block basis is incomplete")

    physical_basis = _SparseModularBasis(FIRST_MODULAR_PRIME)
    selected: list[dict[str, Any]] = []
    for record in complex_records:
        tensor_vector = record["tensor_vector"]
        conjugate = _conjugate_symmetric_tensor_vector(tensor_vector)
        for component, scale, channel in (
            ("physical_fixed_plus", 1, 0),
            ("physical_fixed_i_minus", -1, 1),
        ):
            combined = _combine_vectors(tensor_vector, conjugate, scale)
            doubled = {
                2 * coordinate + channel: coefficient
                for coordinate, coefficient in combined.items()
            }
            independent, _ = physical_basis.insert(doubled)
            if independent:
                selected.append(
                    {
                        "left_copy_index": record["left_copy_index"],
                        "right_copy_index": record["right_copy_index"],
                        "physical_component": component,
                    }
                )
                if physical_basis.rank == expected:
                    break
        if physical_basis.rank == expected:
            break
    if physical_basis.rank != expected or len(selected) != expected:
        raise ArithmeticError("real-type physical fixed block basis is incomplete")

    # The same displayed basis must survive an arithmetically independent prime.
    alternate = _SparseModularBasis(SECOND_MODULAR_PRIME)
    for record in selected:
        tensor_vector = _symmetric_tensor_vector(
            _raw_invariant_tensor(
                representative,
                int(record["left_copy_index"]),
                int(record["right_copy_index"]),
            )
        )
        conjugate = _conjugate_symmetric_tensor_vector(tensor_vector)
        scale = 1 if record["physical_component"] == "physical_fixed_plus" else -1
        channel = 0 if scale == 1 else 1
        combined = _combine_vectors(tensor_vector, conjugate, scale)
        alternate.insert(
            {
                2 * coordinate + channel: coefficient
                for coordinate, coefficient in combined.items()
            }
        )
    if alternate.rank != expected:
        raise ArithmeticError("real-type physical basis failed at second prime")
    return tuple(copy.deepcopy(selected))


@lru_cache(maxsize=1)
def _block_specs_cached() -> tuple[dict[str, Any], ...]:
    rows: list[dict[str, Any]] = []
    ordinal = 0
    for block_index, block in enumerate(census.exact_augmented_isotypic_blocks()):
        representative = tuple(block["representative_dynkin"])
        multiplicity = int(block["graded_multiplicities_t2_tPhi_Phi2"][2])
        if multiplicity != _carrier_family_data_cached()[representative]["copy_count"]:
            raise ArithmeticError("quartic block multiplicity drifted")
        start = ordinal
        if block["self_conjugate"]:
            parameter_count = multiplicity * (multiplicity + 1) // 2
        else:
            parameter_count = multiplicity**2
        ordinal += parameter_count
        rows.append(
            {
                "block_index": block_index,
                "representative_dynkin": representative,
                "conjugate_dynkin": tuple(block["conjugate_dynkin"]),
                "self_conjugate": bool(block["self_conjugate"]),
                "real_block_kind": block["real_block_kind"],
                "PSD_cone": block["PSD_cone"],
                "multiplicity": multiplicity,
                "quartic_parameter_count": parameter_count,
                "first_domain_ordinal": start,
                "past_last_domain_ordinal": ordinal,
            }
        )
    if len(rows) != REAL_BLOCK_COUNT or ordinal != QUARTIC_DOMAIN_DIMENSION:
        raise ArithmeticError("quartic real block parameter census drifted")
    return tuple(rows)


def quartic_block_metadata() -> tuple[dict[str, Any], ...]:
    """Return mutation-isolated metadata for the 22 quartic PSD blocks."""
    return copy.deepcopy(_block_specs_cached())


def _physical_image(raw: Mapping[int, int], component: str) -> SparseVector:
    conjugate = _conjugate_quartic_vector(raw)
    if component == "diagonal":
        if dict(raw) != conjugate:
            raise ArithmeticError("diagonal Hermitian image is not physically real")
        combined = dict(raw)
        channel = 0
    elif component in ("real_off_diagonal", "physical_fixed_plus"):
        combined = _combine_vectors(raw, conjugate, 1)
        channel = 0
        if _conjugate_quartic_vector(combined) != combined:
            raise ArithmeticError("real off-diagonal image failed conjugation")
    elif component in ("imaginary_off_diagonal", "physical_fixed_i_minus"):
        combined = _combine_vectors(raw, conjugate, -1)
        channel = 1
        if _conjugate_quartic_vector(combined) != {
            coordinate: -coefficient for coordinate, coefficient in combined.items()
        }:
            raise ArithmeticError("imaginary off-diagonal image failed conjugation")
    else:
        raise ValueError("unknown physical Schur component")
    # Channel zero stores real coefficients.  Channel one stores the real
    # coefficient multiplying i times an anti-real polynomial.
    return {2 * coordinate + channel: coefficient for coordinate, coefficient in combined.items()}


def _iter_domain_images() -> Iterator[tuple[dict[str, Any], SparseVector]]:
    ordinal = 0
    for block in _block_specs_cached():
        representative = block["representative_dynkin"]
        multiplicity = int(block["multiplicity"])
        if block["self_conjugate"]:
            recipes = _self_block_physical_recipes_cached(representative)
            if len(recipes) != int(block["quartic_parameter_count"]):
                raise ArithmeticError("real-type physical recipe count drifted")
            for recipe in recipes:
                left = int(recipe["left_copy_index"])
                right = int(recipe["right_copy_index"])
                component = str(recipe["physical_component"])
                raw = _multiply_tensor_to_quartic(
                    _raw_invariant_tensor(representative, left, right)
                )
                metadata = {
                    "ordinal": ordinal,
                    "block_index": block["block_index"],
                    "representative_dynkin": representative,
                    "left_copy_index": left,
                    "right_copy_index": right,
                    "physical_component": component,
                }
                yield metadata, _physical_image(raw, component)
                ordinal += 1
            continue
        for left in range(multiplicity):
            diagonal_raw = _multiply_tensor_to_quartic(
                _raw_invariant_tensor(representative, left, left)
            )
            metadata = {
                "ordinal": ordinal,
                "block_index": block["block_index"],
                "representative_dynkin": representative,
                "left_copy_index": left,
                "right_copy_index": left,
                "physical_component": "diagonal",
            }
            yield metadata, _physical_image(diagonal_raw, "diagonal")
            ordinal += 1
            for right in range(left + 1, multiplicity):
                raw = _multiply_tensor_to_quartic(
                    _raw_invariant_tensor(representative, left, right)
                )
                metadata = {
                    "ordinal": ordinal,
                    "block_index": block["block_index"],
                    "representative_dynkin": representative,
                    "left_copy_index": left,
                    "right_copy_index": right,
                    "physical_component": "real_off_diagonal",
                }
                yield metadata, _physical_image(raw, "real_off_diagonal")
                ordinal += 1
                metadata = {
                    **metadata,
                    "ordinal": ordinal,
                    "physical_component": "imaginary_off_diagonal",
                }
                yield metadata, _physical_image(raw, "imaginary_off_diagonal")
                ordinal += 1
    if ordinal != QUARTIC_DOMAIN_DIMENSION:
        raise ArithmeticError("streamed quartic domain count drifted")


def _selected_minor_rank(
    coordinate_map: sparse.spmatrix,
    selected_columns: Sequence[int],
    prime: int,
) -> tuple[int, int, int]:
    value = coordinate_map.tocsc()
    basis = _SparseModularBasis(prime)
    for column in selected_columns:
        start, stop = value.indptr[int(column)], value.indptr[int(column) + 1]
        vector = {
            int(row): int(coefficient)
            for row, coefficient in zip(
                value.indices[start:stop], value.data[start:stop], strict=True
            )
        }
        basis.insert(vector)
    return basis.rank, basis.fill, basis.maximum_vector_nnz


@lru_cache(maxsize=1)
def _coordinate_map_data_cached() -> dict[str, Any]:
    first_basis = _SparseModularBasis(FIRST_MODULAR_PRIME)
    selected_columns: list[int] = []
    pivot_coordinates: list[int] = []
    first_pass_image_count = 0
    for metadata, image in _iter_domain_images():
        first_pass_image_count += 1
        independent, pivot = first_basis.insert(image)
        if independent:
            selected_columns.append(int(metadata["ordinal"]))
            if pivot is None:
                raise ArithmeticError("independent column has no pivot")
            pivot_coordinates.append(pivot)
            if first_basis.rank == QUARTIC_TARGET_DIMENSION:
                break
    if first_basis.rank != QUARTIC_TARGET_DIMENSION:
        raise ArithmeticError("quartic map failed to reach invariant target rank")
    first_fill = first_basis.fill
    first_maximum_vector_nnz = first_basis.maximum_vector_nnz
    del first_basis

    row_index = {
        coordinate: row for row, coordinate in enumerate(pivot_coordinates)
    }
    rows: list[int] = []
    columns: list[int] = []
    coefficients: list[int] = []
    block_nnz: Counter[int] = Counter()
    component_counts: Counter[str] = Counter()
    image_digest = hashlib.sha256()
    maximum_image_nnz = 0
    maximum_image_coefficient = 0
    second_pass_image_count = 0
    for metadata, image in _iter_domain_images():
        column = int(metadata["ordinal"])
        second_pass_image_count += 1
        component_counts[str(metadata["physical_component"])] += 1
        maximum_image_nnz = max(maximum_image_nnz, len(image))
        maximum_image_coefficient = max(
            maximum_image_coefficient,
            max((abs(int(value)) for value in image.values()), default=0),
        )
        image_digest.update(column.to_bytes(8, "little", signed=False))
        for coordinate, coefficient in sorted(image.items()):
            image_digest.update(int(coordinate).to_bytes(8, "little", signed=False))
            image_digest.update(int(coefficient).to_bytes(8, "little", signed=True))
            row = row_index.get(int(coordinate))
            if row is not None:
                rows.append(row)
                columns.append(column)
                coefficients.append(int(coefficient))
                block_nnz[int(metadata["block_index"])] += 1
    if second_pass_image_count != QUARTIC_DOMAIN_DIMENSION:
        raise ArithmeticError("full quartic map stream ended early")
    coordinate_map = sparse.coo_matrix(
        (coefficients, (rows, columns)),
        shape=(QUARTIC_TARGET_DIMENSION, QUARTIC_DOMAIN_DIMENSION),
        dtype=np.int64,
    ).tocsr()
    coordinate_map.sum_duplicates()
    coordinate_map.eliminate_zeros()
    second_rank, second_fill, second_maximum_vector_nnz = _selected_minor_rank(
        coordinate_map, selected_columns, SECOND_MODULAR_PRIME
    )
    if second_rank != QUARTIC_TARGET_DIMENSION:
        raise ArithmeticError("selected quartic minor failed at second prime")
    if sum(component_counts.values()) != QUARTIC_DOMAIN_DIMENSION:
        raise ArithmeticError("physical component census drifted")
    return {
        "coordinate_map": coordinate_map,
        "selected_domain_columns": tuple(selected_columns),
        "pivot_physical_quartic_coordinates": tuple(pivot_coordinates),
        "first_pass_image_count_until_full_rank": first_pass_image_count,
        "first_prime_rank": QUARTIC_TARGET_DIMENSION,
        "first_prime_elimination_fill": first_fill,
        "first_prime_maximum_basis_vector_nnz": first_maximum_vector_nnz,
        "second_prime_selected_minor_rank": second_rank,
        "second_prime_elimination_fill": second_fill,
        "second_prime_maximum_basis_vector_nnz": second_maximum_vector_nnz,
        "full_stream_image_count": second_pass_image_count,
        "physical_component_counts": dict(component_counts),
        "coordinate_map_block_nnz": dict(block_nnz),
        "maximum_full_image_nnz": maximum_image_nnz,
        "maximum_full_image_absolute_coefficient": maximum_image_coefficient,
        "full_image_stream_sha256": image_digest.hexdigest(),
    }


def exact_quartic_coordinate_map() -> sparse.csr_matrix:
    """Return a defensive copy of the exact 6,057 by 18,085 integer map."""
    return _coordinate_map_data_cached()["coordinate_map"].copy()


def quartic_target_coordinate_metadata() -> tuple[dict[str, Any], ...]:
    """Decode the selected physical coefficient chart without exposing cache state."""
    output: list[dict[str, Any]] = []
    for row, coordinate in enumerate(
        _coordinate_map_data_cached()["pivot_physical_quartic_coordinates"]
    ):
        raw, channel = divmod(int(coordinate), 2)
        output.append(
            {
                "row": row,
                "quartic_monomial": _decode_quartic(raw),
                "physical_channel": "real" if channel == 0 else "i_times_anti_real",
            }
        )
    return tuple(output)


@lru_cache(maxsize=1)
def _metric_certificate_cached() -> dict[str, Any]:
    diagonal = _sym2_metric_diagonal_cached()
    metric = sparse.diags(diagonal, dtype=np.int64, format="csr")
    real_residuals: list[int] = []
    imaginary_residuals: list[int] = []
    for real_action, imaginary_action in cubic._sym2_compact_actions_cached():
        real_residual = real_action.T @ metric + metric @ real_action
        real_residual.eliminate_zeros()
        real_residuals.append(real_residual.nnz)
        # The stored imaginary coefficient represents i*B.  Hermitian
        # invariance is therefore D*B-B^T*D=0, with the opposite sign.
        imaginary_residual = metric @ imaginary_action - imaginary_action.T @ metric
        imaginary_residual.eliminate_zeros()
        imaginary_residuals.append(imaginary_residual.nnz)
    conjugation = _sym2_conjugation_cached()
    conjugation_residual = conjugation.T @ metric @ conjugation - metric
    conjugation_residual.eliminate_zeros()
    return {
        "coordinate_metric_diagonal_convention": (
            "2 on Phi_i^2 and 1 on Phi_i*Phi_j for i<j"
        ),
        "metric_diagonal_value_counts": {
            "1": int(np.count_nonzero(diagonal == 1)),
            "2": int(np.count_nonzero(diagonal == 2)),
        },
        "all_15_compact_real_action_residuals_zero_exact": not any(real_residuals),
        "all_15_compact_imaginary_action_residuals_zero_exact": not any(
            imaginary_residuals
        ),
        "physical_conjugation_is_metric_orthogonal_exact": not conjugation_residual.nnz,
        "physical_conjugation_is_signed_monomial_involution_exact": True,
        "proof_grade": bool(
            not any(real_residuals)
            and not any(imaginary_residuals)
            and not conjugation_residual.nnz
        ),
    }


@lru_cache(maxsize=1)
def _representative_invariance_certificate_cached() -> dict[str, Any]:
    actions = (
        cubic._sym2_chevalley_actions_cached()["cartan"]
        + cubic._sym2_chevalley_actions_cached()["raising"]
        + cubic._sym2_chevalley_actions_cached()["lowering"]
    )
    rows: list[dict[str, Any]] = []
    for block in _block_specs_cached():
        representative = block["representative_dynkin"]
        tensor = _raw_invariant_tensor(representative, 0, 0)
        symmetric_tensor = tensor + tensor.T
        symmetric_tensor.sum_duplicates()
        symmetric_tensor.eliminate_zeros()
        residual_nnz: list[int] = []
        for action in actions:
            residual = action @ symmetric_tensor + symmetric_tensor @ action.T
            residual.eliminate_zeros()
            residual_nnz.append(residual.nnz)
        raw_image = _multiply_tensor_to_quartic(tensor)
        physical_diagonal = _conjugate_quartic_vector(raw_image) == raw_image
        rows.append(
            {
                "representative_dynkin": representative,
                "symmetric_tensor_nnz": symmetric_tensor.nnz,
                "symmetric_tensor_sha256": _sparse_matrix_sha256(
                    symmetric_tensor
                ),
                "all_9_Chevalley_tensor_residuals_zero_exact": not any(
                    residual_nnz
                ),
                "representative_diagonal_image_physically_real_exact": (
                    physical_diagonal
                ),
            }
        )
    return {
        "representative_count": len(rows),
        "rows": tuple(rows),
        "all_22_representatives_all_9_Chevalley_residuals_zero_exact": all(
            row["all_9_Chevalley_tensor_residuals_zero_exact"] for row in rows
        ),
        "all_22_representative_diagonal_images_physically_real_exact": all(
            row["representative_diagonal_image_physically_real_exact"]
            for row in rows
        ),
        "proof_grade": bool(
            len(rows) == REAL_BLOCK_COUNT
            and all(
                row["all_9_Chevalley_tensor_residuals_zero_exact"]
                and row["representative_diagonal_image_physically_real_exact"]
                for row in rows
            )
        ),
    }


def _carrier_certificate() -> dict[str, Any]:
    families = _carrier_family_data_cached()
    rows: list[dict[str, Any]] = []
    for highest, family in families.items():
        rows.append(
            {
                key: family[key]
                for key in (
                    "highest_weight",
                    "dimension",
                    "copy_count",
                    "constraint_shape",
                    "constraint_nnz",
                    "constraint_sha256",
                    "nullity",
                    "alternate_prime_rank",
                    "alternate_prime_nullity",
                    "maximum_rational_reconstruction_denominator",
                    "concatenated_shape",
                    "concatenated_nnz",
                    "concatenated_maximum_absolute_entry",
                    "concatenated_sha256",
                    "raising_residual_zero_exact",
                )
            }
        )
    total_nnz = sum(row["concatenated_nnz"] for row in rows)
    return {
        "complex_isotypic_family_count": len(rows),
        "irreducible_copy_count": sum(row["copy_count"] for row in rows),
        "total_carrier_dimension_with_multiplicity": sum(
            row["dimension"] * row["copy_count"] for row in rows
        ),
        "total_concatenated_nnz": total_nnz,
        "estimated_CSR_storage_bytes_int64": (
            total_nnz * (8 + 4)
            + COMPLEX_ISOTYPIC_TYPE_COUNT
            * (SYMMETRIC_SQUARE_DIMENSION + 1)
            * 4
        ),
        "maximum_absolute_carrier_entry": max(
            row["concatenated_maximum_absolute_entry"] for row in rows
        ),
        "families_sha256": _canonical_json_sha256(rows),
        "rows": tuple(rows),
        "all_exact_highest_nullities_match_at_two_primes": all(
            row["nullity"] == row["alternate_prime_nullity"] == row["copy_count"]
            for row in rows
        ),
        "all_exact_raising_residuals_zero": all(
            row["raising_residual_zero_exact"] for row in rows
        ),
        "proof_grade": bool(
            len(rows) == COMPLEX_ISOTYPIC_TYPE_COUNT
            and sum(row["copy_count"] for row in rows) == IRREDUCIBLE_COPY_COUNT
            and sum(row["dimension"] * row["copy_count"] for row in rows)
            == SYMMETRIC_SQUARE_DIMENSION
            and all(
                row["nullity"]
                == row["alternate_prime_nullity"]
                == row["copy_count"]
                and row["raising_residual_zero_exact"]
                for row in rows
            )
        ),
    }


def _pairing_certificate() -> dict[str, Any]:
    pairings = _pairing_data_cached()
    rows: list[dict[str, Any]] = []
    for representative, record in pairings.items():
        rows.append(
            {
                key: record[key]
                for key in (
                    "representative_dynkin",
                    "conjugate_dynkin",
                    "self_conjugate",
                    "real_block_kind",
                    "dimension",
                    "copy_count",
                    "component_metric_sha256",
                    "pairing_sha256",
                    "pairing_nnz",
                    "pairing_maximum_absolute_entry",
                    "rational_inverse_denominator",
                    "positive_inverse_metric_normalization_exact",
                )
            }
        )
    metric = _metric_certificate_cached()
    return {
        "real_block_count": len(rows),
        "rows": tuple(rows),
        "pairings_sha256": _canonical_json_sha256(rows),
        "maximum_absolute_pairing_entry": max(
            row["pairing_maximum_absolute_entry"] for row in rows
        ),
        "component_metric": metric,
        "all_pairings_are_positive_integer_multiples_of_inverse_metrics_exact": all(
            row["positive_inverse_metric_normalization_exact"] for row in rows
        ),
        "proof_grade": bool(
            len(rows) == REAL_BLOCK_COUNT
            and metric["proof_grade"]
            and all(
                row["positive_inverse_metric_normalization_exact"] for row in rows
            )
        ),
    }


def _realification_certificate() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for block in _block_specs_cached():
        if block["self_conjugate"]:
            recipes = _self_block_physical_recipes_cached(
                block["representative_dynkin"]
            )
            counts = Counter(row["physical_component"] for row in recipes)
            recipe_hash = _canonical_json_sha256(recipes)
        else:
            multiplicity = int(block["multiplicity"])
            counts = Counter(
                {
                    "diagonal": multiplicity,
                    "real_off_diagonal": multiplicity * (multiplicity - 1) // 2,
                    "imaginary_off_diagonal": multiplicity
                    * (multiplicity - 1)
                    // 2,
                }
            )
            recipe_hash = None
        rows.append(
            {
                **block,
                "physical_component_counts": dict(counts),
                "real_type_fixed_basis_recipe_sha256": recipe_hash,
            }
        )
    return {
        "block_count": len(rows),
        "domain_dimension": sum(row["quartic_parameter_count"] for row in rows),
        "rows": tuple(rows),
        "integer_realification_convention": (
            "plus directions use v+J(v); imaginary directions store v-J(v) "
            "in the i-times-anti-real channel. No division by two is hidden."
        ),
        "ordered_tensor_multiplication_convention": (
            "Every ordered Q_ab matrix entry is summed once into its canonical "
            "quartic monomial. Off-diagonal multiplicity variables explicitly "
            "add the conjugate ordered entry; no additional Gram factor is hidden."
        ),
        "real_type_warning_for_future_SDP": (
            "The exact fixed bases are not asserted to be standard symmetric-"
            "matrix coordinates. A congruence from these bases to S_+^m(R) must "
            "be constructed before an SDP; this rank-only module does not do so."
        ),
        "all_real_type_fixed_bases_checked_at_both_primes": True,
        "proof_grade": bool(
            len(rows) == REAL_BLOCK_COUNT
            and sum(row["quartic_parameter_count"] for row in rows)
            == QUARTIC_DOMAIN_DIMENSION
        ),
    }


def _map_certificate() -> dict[str, Any]:
    data = _coordinate_map_data_cached()
    matrix = data["coordinate_map"].tocsr()
    matrix_hash = _sparse_matrix_sha256(matrix)
    if matrix_hash != EXPECTED_COORDINATE_MAP_SHA256:
        raise ArithmeticError("quartic coordinate-map hash drifted")
    if data["full_image_stream_sha256"] != EXPECTED_FULL_IMAGE_STREAM_SHA256:
        raise ArithmeticError("full quartic image-stream hash drifted")
    selected_hash = _canonical_json_sha256(data["selected_domain_columns"])
    pivot_hash = _canonical_json_sha256(
        data["pivot_physical_quartic_coordinates"]
    )
    return {
        "shape": matrix.shape,
        "nnz": matrix.nnz,
        "density": Fraction(matrix.nnz, matrix.shape[0] * matrix.shape[1]),
        "coordinate_map_sha256": matrix_hash,
        "full_image_stream_sha256": data["full_image_stream_sha256"],
        "selected_domain_columns": data["selected_domain_columns"],
        "selected_domain_columns_sha256": selected_hash,
        "pivot_physical_quartic_coordinates": data[
            "pivot_physical_quartic_coordinates"
        ],
        "pivot_physical_quartic_coordinates_sha256": pivot_hash,
        "first_modular_prime": FIRST_MODULAR_PRIME,
        "second_modular_prime": SECOND_MODULAR_PRIME,
        "first_pass_image_count_until_full_rank": data[
            "first_pass_image_count_until_full_rank"
        ],
        "first_prime_rank": data["first_prime_rank"],
        "second_prime_selected_minor_rank": data[
            "second_prime_selected_minor_rank"
        ],
        "rank_over_Q_exact": QUARTIC_TARGET_DIMENSION,
        "kernel_dimension_over_Q_exact": QUARTIC_KERNEL_DIMENSION,
        "rank_argument": (
            "The first-prime streamed echelon selects 6,057 columns and raw "
            "physical coefficient rows. Their square minor has rank 6,057 at "
            "the independent second prime. Modular full rank is a lower bound "
            "over Q, while the exact invariant census gives the matching 6,057 "
            "row upper bound."
        ),
        "first_prime_elimination_fill": data["first_prime_elimination_fill"],
        "first_prime_maximum_basis_vector_nnz": data[
            "first_prime_maximum_basis_vector_nnz"
        ],
        "second_prime_elimination_fill": data[
            "second_prime_elimination_fill"
        ],
        "second_prime_maximum_basis_vector_nnz": data[
            "second_prime_maximum_basis_vector_nnz"
        ],
        "full_stream_image_count": data["full_stream_image_count"],
        "physical_component_counts": data["physical_component_counts"],
        "coordinate_map_block_nnz": data["coordinate_map_block_nnz"],
        "maximum_full_image_nnz": data["maximum_full_image_nnz"],
        "maximum_full_image_absolute_coefficient": data[
            "maximum_full_image_absolute_coefficient"
        ],
        "estimated_dense_int32_bytes_avoided": (
            QUARTIC_TARGET_DIMENSION * QUARTIC_DOMAIN_DIMENSION * 4
        ),
        "estimated_dense_int64_bytes_avoided": (
            QUARTIC_TARGET_DIMENSION * QUARTIC_DOMAIN_DIMENSION * 8
        ),
        "coordinate_map_CSR": {
            "indptr": matrix.indptr,
            "indices": matrix.indices,
            "data": matrix.data,
        },
        "proof_grade": bool(
            matrix.shape
            == (QUARTIC_TARGET_DIMENSION, QUARTIC_DOMAIN_DIMENSION)
            and data["first_prime_rank"] == QUARTIC_TARGET_DIMENSION
            and data["second_prime_selected_minor_rank"]
            == QUARTIC_TARGET_DIMENSION
            and QUARTIC_DOMAIN_DIMENSION - QUARTIC_TARGET_DIMENSION
            == QUARTIC_KERNEL_DIMENSION
        ),
    }


def _provenance_certificate() -> dict[str, Any]:
    census_path = Path(census.__file__).resolve()
    cubic_path = Path(cubic.__file__).resolve()
    census_hash = _file_sha256(census_path)
    cubic_hash = _file_sha256(cubic_path)
    if census_hash != EXPECTED_CENSUS_SOURCE_SHA256:
        raise ArithmeticError("pinned census source hash drifted")
    if cubic_hash != EXPECTED_CUBIC_SOURCE_SHA256:
        raise ArithmeticError("pinned cubic source hash drifted")
    return {
        "census_source": census_path.name,
        "census_source_sha256_canonical_LF": census_hash,
        "cubic_source": cubic_path.name,
        "cubic_source_sha256_canonical_LF": cubic_hash,
        "census_status": census.STATUS,
        "census_overall_state": census.OVERALL_STATE,
        "cubic_status": cubic.STATUS,
        "cubic_overall_state": cubic.OVERALL_STATE,
        "pinned_grade_counts": {
            "domain": tuple(census.EXPECTED_DOMAIN_GRADE_COUNTS),
            "target": tuple(census.EXPECTED_TARGET_GRADE_COUNTS),
            "kernel": tuple(census.EXPECTED_KERNEL_GRADE_COUNTS),
        },
        "dependency_hashes_match_exact": True,
        "proof_grade": bool(
            census.EXPECTED_DOMAIN_GRADE_COUNTS[4]
            == QUARTIC_DOMAIN_DIMENSION
            and census.EXPECTED_TARGET_GRADE_COUNTS[4]
            == QUARTIC_TARGET_DIMENSION
            and census.EXPECTED_KERNEL_GRADE_COUNTS[4]
            == QUARTIC_KERNEL_DIMENSION
        ),
    }


@lru_cache(maxsize=1)
def _build_report_cached() -> dict[str, Any]:
    provenance = _provenance_certificate()
    carriers = _carrier_certificate()
    pairings = _pairing_certificate()
    realification = _realification_certificate()
    invariance = _representative_invariance_certificate_cached()
    coefficient_map = _map_certificate()
    proof_grade = bool(
        provenance["proof_grade"]
        and carriers["proof_grade"]
        and pairings["proof_grade"]
        and realification["proof_grade"]
        and invariance["proof_grade"]
        and coefficient_map["proof_grade"]
    )
    return {
        "model_contract_id": MODEL_CONTRACT_ID,
        "status": STATUS,
        "overall_state": OVERALL_STATE,
        "scope": {
            "homogeneous_quartic_Schur_coefficient_map_constructed_exact": True,
            "all_35_complex_carrier_families_constructed_exact": True,
            "all_22_real_block_pairings_constructed_exact": True,
            "physical_quartic_target_constructed": False,
            "standard_PSD_congruences_for_real_type_fixed_bases_constructed": False,
            "semidefinite_feasibility_solved": False,
            "arbitrary_Phi_stationarity_or_lower_bound_proved": False,
            "G3_closed": False,
        },
        "dimensions": {
            "Phi": PHI_DIMENSION,
            "Sym2_Phi": SYMMETRIC_SQUARE_DIMENSION,
            "complex_isotypic_types": COMPLEX_ISOTYPIC_TYPE_COUNT,
            "irreducible_copies": IRREDUCIBLE_COPY_COUNT,
            "real_Schur_blocks": REAL_BLOCK_COUNT,
            "quartic_domain": QUARTIC_DOMAIN_DIMENSION,
            "quartic_target": QUARTIC_TARGET_DIMENSION,
            "quartic_kernel": QUARTIC_KERNEL_DIMENSION,
        },
        "provenance": provenance,
        "carrier_certificate": carriers,
        "pairing_certificate": pairings,
        "realification_certificate": realification,
        "representative_invariance_certificate": invariance,
        "coefficient_map_certificate": coefficient_map,
        "cache_and_mutation_contract": {
            "private_lru_caches_used_for_exact_heavy_objects": True,
            "public_sparse_map_returns_defensive_copy": True,
            "public_carrier_and_pairing_data_return_deep_copies": True,
            "unverified_external_binary_cache_used": False,
        },
        "arithmetic_contract": {
            "integer_carriers_pairings_images_and_coordinate_map": True,
            "rational_operations_restricted_to_exact_metric_inversion": True,
            "signed_int64_results_checked_or_python_integer_fallback": True,
            "first_modular_prime": FIRST_MODULAR_PRIME,
            "second_modular_prime": SECOND_MODULAR_PRIME,
        },
        "proof_grade": proof_grade,
        "honest_conclusion": (
            "The exact homogeneous quartic coefficient map has rank 6,057 and "
            "kernel dimension 12,028. This closes only that map/rank interface. "
            "The physical target, PSD-coordinate congruences for real-type "
            "blocks, SDP feasibility, arbitrary-Phi theorem, and G3 remain open."
        ),
    }


def build_report() -> dict[str, Any]:
    """Build and return a defensive copy of the exact quartic certificate."""
    return copy.deepcopy(_build_report_cached())


def render_markdown(report: Mapping[str, Any]) -> str:
    dimensions = report["dimensions"]
    coefficient_map = report["coefficient_map_certificate"]
    carriers = report["carrier_certificate"]
    pairings = report["pairing_certificate"]
    scope = report["scope"]
    lines = [
        "# Exact rank-one SU(4) augmented-SOS quartic map (v20)",
        "",
        f"Status: `{report['status']}`",
        "",
        "## Certified result",
        "",
        (
            f"The streamed exact integer map has shape "
            f"`{dimensions['quartic_target']} x {dimensions['quartic_domain']}`, "
            f"rank `{coefficient_map['rank_over_Q_exact']}`, and kernel dimension "
            f"`{coefficient_map['kernel_dimension_over_Q_exact']}`."
        ),
        "",
        (
            f"It contains `{coefficient_map['nnz']}` nonzeros and has SHA-256 "
            f"`{coefficient_map['coordinate_map_sha256']}`."
        ),
        "",
        "The rank is witnessed at primes "
        f"`{coefficient_map['first_modular_prime']}` and "
        f"`{coefficient_map['second_modular_prime']}`.",
        "",
        "## Exact representation data",
        "",
        f"- complex carrier families: `{carriers['complex_isotypic_family_count']}`",
        f"- irreducible copies: `{carriers['irreducible_copy_count']}`",
        f"- real Schur blocks: `{pairings['real_block_count']}`",
        f"- total carrier nonzeros: `{carriers['total_concatenated_nnz']}`",
        f"- maximum carrier coefficient: `{carriers['maximum_absolute_carrier_entry']}`",
        f"- maximum pairing coefficient: `{pairings['maximum_absolute_pairing_entry']}`",
        "",
        "Real-type multiplicity bases were realified by exact fixed-space "
        "selection, with both plus and i-minus directions checked at both primes.",
        "",
        "## Scope boundary",
        "",
        f"- physical quartic target constructed: `{scope['physical_quartic_target_constructed']}`",
        f"- standard real-type PSD congruences constructed: `{scope['standard_PSD_congruences_for_real_type_fixed_bases_constructed']}`",
        f"- SDP solved: `{scope['semidefinite_feasibility_solved']}`",
        f"- arbitrary-Phi theorem proved: `{scope['arbitrary_Phi_stationarity_or_lower_bound_proved']}`",
        f"- G3 closed: `{scope['G3_closed']}`",
        "",
        report["honest_conclusion"],
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write", action="store_true", help="write the exact JSON and Markdown reports"
    )
    parser.add_argument(
        "--summary", action="store_true", help="print a compact JSON summary"
    )
    arguments = parser.parse_args(argv)
    report = build_report()
    if arguments.write:
        OUT_JSON.write_text(
            json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        OUT_MD.write_text(render_markdown(report), encoding="utf-8")
    if arguments.summary or not arguments.write:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "overall_state": report["overall_state"],
                    "dimensions": report["dimensions"],
                    "map_sha256": report["coefficient_map_certificate"][
                        "coordinate_map_sha256"
                    ],
                    "proof_grade": report["proof_grade"],
                    "scope": report["scope"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
