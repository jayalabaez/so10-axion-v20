#!/usr/bin/env python3
"""Exact generation-time reconstruction of the v21 SU(4) physical RHS.

This source bypasses the invalid v20 raw-Schur extremal-minor fit and
constructs every one of the 6,057
quartic pivot coefficients directly from the ordered 210x210 spectral
operator.  It then assembles the complete 6,585-entry graded RHS.  It is a
generation-time source: the publication's runtime certificate and verifier
are separately HERE-only and relocation-tested.

All physical contractions are Python-integer dot products.  Sparse int64 is
used only for Casimir actions after a conservative pre-operation bound has
proved that the operation cannot overflow; an unsafe bound aborts before the
operation.
"""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
from scipy import sparse


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE_ROOT = Path(
    os.environ.get("SO10_PUBLISHED_API_ROOT", ROOT / "so10-axion-v20-reaudit")
).resolve()
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

import exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20 as cubic
import exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20 as structural_source
import exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20 as quartic
import exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20 as intertwiners
import exact_gauged_u1x_g3_pd_rank_certificate_v20 as rank_source


STATUS = "EXACT_RANK1_SU4_CORRECTED_ORDERED_SPECTRAL_RHS_V21"
PHI_DIMENSION = 210
QUARTIC_ROW_COUNT = 6_057
FULL_ROW_COUNT = 6_585
INT64_MAX = (1 << 63) - 1
BATCH_SIZE = 256

SPECTRAL_NUMERATORS = (
    4_423_680,
    -1_999_872,
    414_336,
    65_728,
    -31_448,
    3_716,
    -178,
    3,
)
SPECTRAL_DENOMINATOR = 221_184_000

QUARTIC_MAP_ARTIFACT = (
    SOURCE_ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.json"
)

# Portable hashes use UTF-8 text with all line endings normalized to LF.
EXPECTED_DEPENDENCY_HASHES = {
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py": (
        "8493a90d9b689bc02479151529ac697425f56087f2bdbebb40176f418b7c0ff8"
    ),
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py": (
        "28633a2dba4d70f019a3e63ca87e8224ca11630a9e7c53bc963aedc6824208c1"
    ),
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py": (
        "589952b9b0a0b6af1543b87c89b0f3626a4bfb9c4219821a915fe04fab8af690"
    ),
    "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py": (
        "76fa77c99b8d6e963e8694acf74280de29ced4c7a7623bffa991aead77329f49"
    ),
    "exact_gauged_u1x_g3_pd_rank_certificate_v20.py": (
        "e2499baf3f7a572df7647ca02f109666a549c9e2c1989110c682ee584e0483c6"
    ),
    QUARTIC_MAP_ARTIFACT.name: (
        "056e1a90c028f0aaca8fb17f2f53dfb02d5e7a33230ec3675537d2778755266a"
    ),
}

IMPORTED_MODULES = {
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py": structural_source,
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py": quartic,
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py": cubic,
    "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py": intertwiners,
    "exact_gauged_u1x_g3_pd_rank_certificate_v20.py": rank_source,
}

EXPECTED_FIRST_PIVOT = 1_155_894
EXPECTED_FIRST_MONOMIAL = (0, 13, 22, 27)
EXPECTED_FIRST_CORRECT = Fraction(27_776, 1_125)

# Frozen only after the complete independent 6,057-row audit succeeded.
EXPECTED_CORRECTED_QUARTIC_DENOMINATOR: int | None = 1_125
EXPECTED_CORRECTED_QUARTIC_NNZ: int | None = 492
EXPECTED_CORRECTED_QUARTIC_SHA256: str | None = (
    "9460ddb239c7af45124396b469d5d633a82d46b72b16427809f3cca4cc39dff4"
)
EXPECTED_CORRECTED_FULL_DENOMINATOR: int | None = 576_000
EXPECTED_CORRECTED_FULL_NNZ: int | None = 512
EXPECTED_CORRECTED_FULL_SHA256: str | None = (
    "14debcfaf02d4b8c20d1d43a2e1f82d6a7390e28428fc63dd21a9c5f90aec0cf"
)


def _portable_sha256(path: Path) -> str:
    payload = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _dependency_hashes() -> dict[str, str]:
    output: dict[str, str] = {}
    for name, module in IMPORTED_MODULES.items():
        path = Path(module.__file__).resolve()
        if path.parent != SOURCE_ROOT or path.name != name:
            raise ImportError(f"explicit generation-source import binding failed for {name}: {path}")
        output[name] = _portable_sha256(path)
    output[QUARTIC_MAP_ARTIFACT.name] = _portable_sha256(QUARTIC_MAP_ARTIFACT)
    if output != EXPECTED_DEPENDENCY_HASHES:
        raise ArithmeticError("ordered-spectral RHS dependency provenance drifted")
    return output


def _jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def _int64_vector_sha256(values: Sequence[int]) -> str:
    if any(abs(int(value)) > INT64_MAX for value in values):
        raise ArithmeticError("fingerprinted vector exceeds signed int64")
    array = np.ascontiguousarray(np.asarray(tuple(values), dtype="<i8"))
    digest = hashlib.sha256()
    digest.update(np.asarray(array.shape, dtype="<i8").tobytes())
    digest.update(array.tobytes())
    return digest.hexdigest()


def _decode_quartic(raw_coordinate: int) -> tuple[int, int, int, int]:
    value = int(raw_coordinate)
    output = [0, 0, 0, 0]
    for position in range(3, -1, -1):
        value, output[position] = divmod(value, PHI_DIMENSION)
    if value or output != sorted(output):
        raise ArithmeticError("noncanonical encoded Gaussian quartic monomial")
    return tuple(output)  # type: ignore[return-value]


def _encode_quartic(indices: Sequence[int]) -> int:
    ordered = tuple(sorted(int(index) for index in indices))
    if len(ordered) != 4 or not all(0 <= index < PHI_DIMENSION for index in ordered):
        raise ValueError("invalid Gaussian quartic monomial")
    output = 0
    for index in ordered:
        output = output * PHI_DIMENSION + index
    return output


@lru_cache(maxsize=1)
def _pair_data() -> tuple[tuple[tuple[int, int], ...], dict[tuple[int, int], int]]:
    pairs = tuple(tuple(map(int, pair)) for pair in cubic._quadratic_pairs_cached())
    if len(pairs) != PHI_DIMENSION * (PHI_DIMENSION + 1) // 2:
        raise ArithmeticError("Gaussian packed-pair census drifted")
    return pairs, {pair: index for index, pair in enumerate(pairs)}


def _ordered_splits(monomial: Sequence[int]) -> tuple[tuple[int, int], ...]:
    """All distinct ordered packed-pair products yielding one monomial."""
    values = tuple(sorted(int(value) for value in monomial))
    if len(values) != 4:
        raise ValueError("quartic split requires four indices")
    _, pair_index = _pair_data()
    output: set[tuple[int, int]] = set()
    slots = range(4)
    for left_slots in itertools.combinations(slots, 2):
        left_set = set(left_slots)
        right_slots = tuple(slot for slot in slots if slot not in left_set)
        left = tuple(sorted(values[slot] for slot in left_slots))
        right = tuple(sorted(values[slot] for slot in right_slots))
        output.add((pair_index[left], pair_index[right]))
    return tuple(sorted(output))


def _edge_coordinate(edge: tuple[int, int]) -> int:
    pairs, _ = _pair_data()
    return _encode_quartic(pairs[edge[0]] + pairs[edge[1]])


@lru_cache(maxsize=None)
def _independent_gaussian_column(column: int) -> tuple[tuple[int, int, int], ...]:
    real_basis, imaginary_basis = intertwiners.gaussian_exterior_basis()
    real = real_basis.getcol(int(column)).tocoo()
    imaginary = imaginary_basis.getcol(int(column)).tocoo()
    values: dict[int, list[int]] = {}
    for row, coefficient in zip(real.row, real.data, strict=True):
        values.setdefault(int(row), [0, 0])[0] += int(coefficient)
    for row, coefficient in zip(imaginary.row, imaginary.data, strict=True):
        values.setdefault(int(row), [0, 0])[1] += int(coefficient)
    return tuple(
        (row, components[0], components[1])
        for row, components in sorted(values.items())
        if components[0] or components[1]
    )


@lru_cache(maxsize=None)
def _independent_ordered_pair_column(
    pair_coordinate: int,
) -> tuple[dict[int, int], dict[int, int]]:
    """Independent packed-Gaussian to ordered-Phi tensor transform."""
    pairs, _ = _pair_data()
    left, right = pairs[int(pair_coordinate)]
    first = _independent_gaussian_column(left)
    second = _independent_gaussian_column(right)
    real: dict[int, int] = {}
    imaginary: dict[int, int] = {}

    def add_outer(one: Iterable[tuple[int, int, int]], two: Iterable[tuple[int, int, int]]) -> None:
        for row_left, real_left, imaginary_left in one:
            for row_right, real_right, imaginary_right in two:
                coordinate = row_left * PHI_DIMENSION + row_right
                real_value = real_left * real_right - imaginary_left * imaginary_right
                imaginary_value = real_left * imaginary_right + imaginary_left * real_right
                if real_value:
                    real[coordinate] = real.get(coordinate, 0) + real_value
                    if not real[coordinate]:
                        del real[coordinate]
                if imaginary_value:
                    imaginary[coordinate] = imaginary.get(coordinate, 0) + imaginary_value
                    if not imaginary[coordinate]:
                        del imaginary[coordinate]

    add_outer(first, second)
    if left != right:
        add_outer(second, first)
    return real, imaginary


def _load_pivots() -> tuple[int, ...]:
    artifact = json.loads(QUARTIC_MAP_ARTIFACT.read_text(encoding="utf-8"))
    certificate = artifact["coefficient_map_certificate"]
    pivots = tuple(int(value) for value in certificate["pivot_physical_quartic_coordinates"])
    if len(pivots) != QUARTIC_ROW_COUNT or len(set(pivots)) != QUARTIC_ROW_COUNT:
        raise ArithmeticError("quartic pivot chart census drifted")
    if structural_source._canonical_sha256(pivots) != certificate[
        "pivot_physical_quartic_coordinates_sha256"
    ]:
        raise ArithmeticError("quartic pivot chart fingerprint drifted")
    return pivots


def _sparse_maximum(matrix: sparse.spmatrix) -> int:
    return max((abs(int(value)) for value in matrix.data), default=0)


def _maximum_row_nnz(matrix: sparse.spmatrix) -> int:
    value = matrix.tocsr()
    counts = np.diff(value.indptr)
    return int(counts.max(initial=0))


def _guarded_matmul(
    left: sparse.spmatrix,
    right: sparse.spmatrix,
    safety: dict[str, Any],
) -> sparse.csr_matrix:
    if left.shape[1] != right.shape[0]:
        raise ValueError("incompatible sparse Casimir multiplication")
    overlap = min(_maximum_row_nnz(left), _maximum_row_nnz(right.T))
    bound = overlap * _sparse_maximum(left) * _sparse_maximum(right)
    safety["maximum_preoperation_matmul_bound"] = max(
        safety["maximum_preoperation_matmul_bound"], int(bound)
    )
    safety["guarded_sparse_matmul_count"] += 1
    if bound > INT64_MAX:
        raise ArithmeticError("Casimir action rejected before unsafe int64 multiplication")
    output = (left.astype(np.int64) @ right.astype(np.int64)).tocsr()
    output.sum_duplicates()
    output.eliminate_zeros()
    if output.dtype != np.int64:
        raise ArithmeticError("Casimir action lost signed-int64 storage")
    safety["maximum_observed_sparse_entry"] = max(
        safety["maximum_observed_sparse_entry"], _sparse_maximum(output)
    )
    return output


def _guarded_scale(
    matrix: sparse.spmatrix,
    coefficient: int,
    safety: dict[str, Any],
) -> sparse.csr_matrix:
    bound = _sparse_maximum(matrix) * abs(int(coefficient))
    safety["maximum_preoperation_scale_bound"] = max(
        safety["maximum_preoperation_scale_bound"], int(bound)
    )
    safety["guarded_sparse_scale_count"] += 1
    if bound > INT64_MAX:
        raise ArithmeticError("spectral scale rejected before unsafe int64 multiplication")
    output = (matrix.astype(np.int64) * int(coefficient)).tocsr()
    output.eliminate_zeros()
    return output


def _guarded_add(
    left: sparse.spmatrix,
    right: sparse.spmatrix,
    safety: dict[str, Any],
) -> sparse.csr_matrix:
    bound = _sparse_maximum(left) + _sparse_maximum(right)
    safety["maximum_preoperation_add_bound"] = max(
        safety["maximum_preoperation_add_bound"], int(bound)
    )
    safety["guarded_sparse_add_count"] += 1
    if bound > INT64_MAX:
        raise ArithmeticError("spectral sum rejected before unsafe int64 addition")
    output = (left.astype(np.int64) + right.astype(np.int64)).tocsr()
    output.sum_duplicates()
    output.eliminate_zeros()
    safety["maximum_observed_sparse_entry"] = max(
        safety["maximum_observed_sparse_entry"], _sparse_maximum(output)
    )
    return output


def _column_matrix(
    coordinates: Sequence[int],
    *,
    independently: bool,
) -> tuple[sparse.csc_matrix, sparse.csc_matrix]:
    rows_real: list[int] = []
    columns_real: list[int] = []
    values_real: list[int] = []
    rows_imaginary: list[int] = []
    columns_imaginary: list[int] = []
    values_imaginary: list[int] = []
    for local_column, coordinate in enumerate(coordinates):
        if independently:
            real, imaginary = _independent_ordered_pair_column(int(coordinate))
        else:
            real, imaginary = structural_source._ordered_pair_column(int(coordinate))
        for row, value in real.items():
            rows_real.append(row)
            columns_real.append(local_column)
            values_real.append(int(value))
        for row, value in imaginary.items():
            rows_imaginary.append(row)
            columns_imaginary.append(local_column)
            values_imaginary.append(int(value))
    shape = (PHI_DIMENSION * PHI_DIMENSION, len(coordinates))
    return (
        sparse.coo_matrix(
            (values_real, (rows_real, columns_real)), shape=shape, dtype=np.int64
        ).tocsc(),
        sparse.coo_matrix(
            (values_imaginary, (rows_imaginary, columns_imaginary)),
            shape=shape,
            dtype=np.int64,
        ).tocsc(),
    )


def _column_dictionary(matrix: sparse.spmatrix, column: int) -> dict[int, int]:
    value = matrix.getcol(int(column)).tocsc()
    return {
        int(row): int(coefficient)
        for row, coefficient in zip(value.indices, value.data, strict=True)
        if coefficient
    }


def _python_dot(left: Mapping[int, int], right: Mapping[int, int]) -> int:
    """No NumPy scalar may enter a physical contraction."""
    if len(left) > len(right):
        left, right = right, left
    return sum(int(value) * int(right.get(int(row), 0)) for row, value in left.items())


def _python_sparse_matvec(
    matrix: sparse.csc_matrix, vector: Mapping[int, int]
) -> dict[int, int]:
    """Exact sparse matrix-vector product with no fixed-width accumulation."""
    output: dict[int, int] = {}
    for column, vector_value in vector.items():
        start, stop = matrix.indptr[int(column)], matrix.indptr[int(column) + 1]
        for pointer in range(start, stop):
            row = int(matrix.indices[pointer])
            updated = output.get(row, 0) + int(matrix.data[pointer]) * int(vector_value)
            if updated:
                output[row] = updated
            else:
                output.pop(row, None)
    return output


def _python_linear_combination(
    accumulator: dict[int, int], vector: Mapping[int, int], coefficient: int
) -> None:
    for row, value in vector.items():
        updated = accumulator.get(int(row), 0) + int(coefficient) * int(value)
        if updated:
            accumulator[int(row)] = updated
        else:
            accumulator.pop(int(row), None)


def first_pivot_python_int_direct() -> dict[str, Any]:
    """Independent row-0 evaluator using only sparse dictionaries/Python ints."""
    pivots = _load_pivots()
    pivot = pivots[0]
    monomial = _decode_quartic(pivot // 2)
    splits = _ordered_splits(monomial)
    operator = rank_source._phi_pair_casimir_integer().tocsc()
    response_cache: dict[
        int, tuple[dict[int, int], dict[int, int]]
    ] = {}

    def response(pair_coordinate: int) -> tuple[dict[int, int], dict[int, int]]:
        cached = response_cache.get(int(pair_coordinate))
        if cached is not None:
            return cached
        source_real, source_imaginary = _independent_ordered_pair_column(
            int(pair_coordinate)
        )
        current_real = dict(source_real)
        current_imaginary = dict(source_imaginary)
        result_real: dict[int, int] = {}
        result_imaginary: dict[int, int] = {}
        _python_linear_combination(result_real, current_real, SPECTRAL_NUMERATORS[0])
        _python_linear_combination(
            result_imaginary, current_imaginary, SPECTRAL_NUMERATORS[0]
        )
        for numerator in SPECTRAL_NUMERATORS[1:]:
            current_real = _python_sparse_matvec(operator, current_real)
            current_imaginary = _python_sparse_matvec(operator, current_imaginary)
            _python_linear_combination(result_real, current_real, numerator)
            _python_linear_combination(result_imaginary, current_imaginary, numerator)
        response_cache[int(pair_coordinate)] = (result_real, result_imaginary)
        return result_real, result_imaginary

    real_numerator = 0
    imaginary_numerator = 0
    for left, right in splits:
        left_real, left_imaginary = _independent_ordered_pair_column(left)
        response_real, response_imaginary = response(right)
        real_numerator += _python_dot(left_real, response_real) - _python_dot(
            left_imaginary, response_imaginary
        )
        imaginary_numerator += _python_dot(left_real, response_imaginary) + _python_dot(
            left_imaginary, response_real
        )
    coefficient = Fraction(real_numerator, SPECTRAL_DENOMINATOR)
    if (
        pivot != EXPECTED_FIRST_PIVOT
        or monomial != EXPECTED_FIRST_MONOMIAL
        or coefficient != EXPECTED_FIRST_CORRECT
        or imaginary_numerator != 0
    ):
        raise ArithmeticError("independent Python-int first-pivot regression failed")
    return {
        "pivot_physical_coordinate": pivot,
        "Gaussian_quartic_monomial": monomial,
        "ordered_splits": splits,
        "real_spectral_numerator": real_numerator,
        "imaginary_spectral_numerator": imaginary_numerator,
        "spectral_denominator": SPECTRAL_DENOMINATOR,
        "coefficient": coefficient,
    }


def _spectral_bilinears(
    edges: Sequence[tuple[int, int]],
    coordinates: Sequence[int],
) -> tuple[dict[tuple[int, int], tuple[int, int]], dict[str, Any]]:
    lefts_by_right: dict[int, list[int]] = defaultdict(list)
    for left, right in edges:
        lefts_by_right[int(right)].append(int(left))

    # Independently duplicate and compare all 3,613 packed->ordered columns.
    for coordinate in coordinates:
        direct = _independent_ordered_pair_column(int(coordinate))
        source = structural_source._ordered_pair_column(int(coordinate))
        if direct != source:
            raise ArithmeticError(
                f"packed-to-ordered transform mismatch at pair column {coordinate}"
            )

    original_columns = {
        int(coordinate): structural_source._ordered_pair_column(int(coordinate))
        for coordinate in coordinates
    }
    operator = rank_source._phi_pair_casimir_integer().tocsr()
    if operator.shape != (PHI_DIMENSION**2, PHI_DIMENSION**2):
        raise ArithmeticError("ordered Casimir shape drifted")
    if (operator - operator.T).nnz:
        raise ArithmeticError("ordered Casimir ceased to be symmetric")

    safety: dict[str, Any] = {
        "fixed_width_storage": "signed int64 only after conservative pre-operation guard",
        "physical_contraction_arithmetic": "Python int",
        "signed_int64_maximum": INT64_MAX,
        "guarded_sparse_matmul_count": 0,
        "guarded_sparse_scale_count": 0,
        "guarded_sparse_add_count": 0,
        "maximum_preoperation_matmul_bound": 0,
        "maximum_preoperation_scale_bound": 0,
        "maximum_preoperation_add_bound": 0,
        "maximum_observed_sparse_entry": 0,
        "unsafe_operation_count": 0,
    }
    table: dict[tuple[int, int], tuple[int, int]] = {}
    for start in range(0, len(coordinates), BATCH_SIZE):
        batch = tuple(coordinates[start : start + BATCH_SIZE])
        current_real, current_imaginary = _column_matrix(batch, independently=False)
        response_real = _guarded_scale(current_real, SPECTRAL_NUMERATORS[0], safety)
        response_imaginary = _guarded_scale(
            current_imaginary, SPECTRAL_NUMERATORS[0], safety
        )
        for numerator in SPECTRAL_NUMERATORS[1:]:
            current_real = _guarded_matmul(operator, current_real, safety)
            current_imaginary = _guarded_matmul(operator, current_imaginary, safety)
            response_real = _guarded_add(
                response_real, _guarded_scale(current_real, numerator, safety), safety
            )
            response_imaginary = _guarded_add(
                response_imaginary,
                _guarded_scale(current_imaginary, numerator, safety),
                safety,
            )
        for local, right_coordinate in enumerate(batch):
            response_rr = _column_dictionary(response_real, local)
            response_ri = _column_dictionary(response_imaginary, local)
            for left_coordinate in lefts_by_right[right_coordinate]:
                left_real, left_imaginary = original_columns[left_coordinate]
                real_value = _python_dot(left_real, response_rr) - _python_dot(
                    left_imaginary, response_ri
                )
                imaginary_value = _python_dot(left_real, response_ri) + _python_dot(
                    left_imaginary, response_rr
                )
                table[(left_coordinate, right_coordinate)] = (
                    int(real_value),
                    int(imaginary_value),
                )

    if set(table) != set(edges):
        raise ArithmeticError("ordered spectral bilinear table is incomplete")
    for (left, right), value in table.items():
        reverse = table.get((right, left))
        if reverse is not None and reverse != value:
            raise ArithmeticError("ordered spectral bilinear form lost symmetry")
    return table, safety


def _primitive_integer_vector(values: Sequence[Fraction]) -> tuple[int, tuple[int, ...]]:
    denominator = math.lcm(*(value.denominator for value in values))
    numerator = tuple(
        int(value.numerator) * (denominator // int(value.denominator)) for value in values
    )
    content = denominator
    for value in numerator:
        content = math.gcd(content, abs(int(value)))
    if content > 1:
        denominator //= content
        numerator = tuple(value // content for value in numerator)
    return int(denominator), numerator


def _construct_quartic() -> dict[str, Any]:
    independent_first = first_pivot_python_int_direct()
    pivots = _load_pivots()
    row_splits = tuple(_ordered_splits(_decode_quartic(pivot // 2)) for pivot in pivots)
    edges = tuple(sorted({edge for splits in row_splits for edge in splits}))
    coordinates = tuple(sorted({coordinate for edge in edges for coordinate in edge}))
    table, safety = _spectral_bilinears(edges, coordinates)

    # Construction path: multiply every ordered pair of packed quadratics and
    # collect its spectral bilinear into a global raw-monomial dictionary.
    constructed_real: dict[int, int] = defaultdict(int)
    constructed_imaginary: dict[int, int] = defaultdict(int)
    for edge, (real_value, imaginary_value) in table.items():
        raw_coordinate = _edge_coordinate(edge)
        constructed_real[raw_coordinate] += int(real_value)
        constructed_imaginary[raw_coordinate] += int(imaginary_value)

    # Independent evaluator path: decode each pivot and enumerate its distinct
    # ordered two-plus-two slot splits directly, without using the global image.
    values: list[Fraction] = []
    mismatch_rows: list[int] = []
    maximum_row_split_count = 0
    for row, (pivot, splits) in enumerate(zip(pivots, row_splits, strict=True)):
        maximum_row_split_count = max(maximum_row_split_count, len(splits))
        direct_real = sum(table[edge][0] for edge in splits)
        direct_imaginary = sum(table[edge][1] for edge in splits)
        raw_coordinate, channel = divmod(int(pivot), 2)
        constructed = (
            constructed_real.get(raw_coordinate, 0)
            if channel == 0
            else constructed_imaginary.get(raw_coordinate, 0)
        )
        direct = direct_real if channel == 0 else direct_imaginary
        if constructed != direct:
            mismatch_rows.append(row)
        values.append(Fraction(int(direct), SPECTRAL_DENOMINATOR))
    if mismatch_rows:
        raise ArithmeticError(f"row-by-row direct evaluator mismatches: {mismatch_rows[:8]}")

    first_monomial = _decode_quartic(pivots[0] // 2)
    if pivots[0] != EXPECTED_FIRST_PIVOT or first_monomial != EXPECTED_FIRST_MONOMIAL:
        raise ArithmeticError("first pivot regression coordinate drifted")
    if values[0] != EXPECTED_FIRST_CORRECT:
        raise ArithmeticError(
            f"first corrected quartic coefficient is {values[0]}, expected {EXPECTED_FIRST_CORRECT}"
        )
    if values[0] != independent_first["coefficient"]:
        raise ArithmeticError("batch construction disagrees with Python-int row-0 evaluator")

    denominator, numerator = _primitive_integer_vector(values)
    fingerprint = _int64_vector_sha256(numerator)
    odd_rows = tuple(index for index, pivot in enumerate(pivots) if pivot % 2)
    if any(values[index] for index in odd_rows):
        raise ArithmeticError("physical spectral target acquired an odd-channel coefficient")
    return {
        "pivots": pivots,
        "values": tuple(values),
        "common_denominator": denominator,
        "numerator": numerator,
        "numerator_sha256": fingerprint,
        "nonzero_count": sum(value != 0 for value in numerator),
        "maximum_absolute_numerator": max(map(abs, numerator), default=0),
        "ordered_edge_count": len(edges),
        "unique_packed_pair_column_count": len(coordinates),
        "row_by_row_direct_evaluator_mismatch_count": len(mismatch_rows),
        "maximum_row_ordered_split_count": maximum_row_split_count,
        "odd_channel_row_count": len(odd_rows),
        "all_odd_channel_coefficients_zero_exact": True,
        "packed_to_ordered_columns_checked_independently": len(coordinates),
        "first_pivot_independent_python_int_direct": independent_first,
        "safety": safety,
    }


def _assemble_full(quartic_result: Mapping[str, Any]) -> dict[str, Any]:
    # Reuse only the audited lower-grade formula API.  No v20 physical-target
    # JSON or assembled target vector is opened anywhere in this module.
    lower = structural_source._build_lower_target()
    constant = (Fraction(lower["constant"]),)
    linear = tuple(Fraction(value) for value in lower["linear"]["SU4_invariant_basis"]["target_coordinates"])
    quadratic = tuple(
        Fraction(value)
        for value in lower["quadratic"]["SU4_invariant_basis"]["target_coordinates"]
    )
    cubic_values = (Fraction(0),) * 478
    quartic_values = tuple(Fraction(value) for value in quartic_result["values"])
    pieces = (constant, linear, quadratic, cubic_values, quartic_values)
    lengths = tuple(len(piece) for piece in pieces)
    if lengths != (1, 4, 45, 478, QUARTIC_ROW_COUNT):
        raise ArithmeticError("full graded target lengths drifted")
    values = tuple(value for piece in pieces for value in piece)
    denominator, numerator = _primitive_integer_vector(values)
    if len(numerator) != FULL_ROW_COUNT:
        raise ArithmeticError("full corrected RHS row count drifted")
    return {
        "values": values,
        "common_denominator": denominator,
        "numerator": numerator,
        "numerator_sha256": _int64_vector_sha256(numerator),
        "total_nonzero_count": sum(value != 0 for value in numerator),
        "nonzero_count_by_grade": tuple(
            sum(value != 0 for value in piece) for piece in pieces
        ),
        "grade_lengths": lengths,
        "maximum_absolute_numerator": max(map(abs, numerator), default=0),
    }


def _require_fingerprint_pins(quartic_result: Mapping[str, Any], full_result: Mapping[str, Any]) -> None:
    expected = (
        EXPECTED_CORRECTED_QUARTIC_DENOMINATOR,
        EXPECTED_CORRECTED_QUARTIC_NNZ,
        EXPECTED_CORRECTED_QUARTIC_SHA256,
        EXPECTED_CORRECTED_FULL_DENOMINATOR,
        EXPECTED_CORRECTED_FULL_NNZ,
        EXPECTED_CORRECTED_FULL_SHA256,
    )
    if any(value is None for value in expected):
        raise ArithmeticError("corrected RHS fingerprint pins have not been frozen")
    observed = (
        quartic_result["common_denominator"],
        quartic_result["nonzero_count"],
        quartic_result["numerator_sha256"],
        full_result["common_denominator"],
        full_result["total_nonzero_count"],
        full_result["numerator_sha256"],
    )
    if observed != expected:
        raise ArithmeticError(f"corrected RHS fingerprint drifted: {observed!r}")


def reconstruct_rhs() -> tuple[np.ndarray, int, dict[str, Any]]:
    """Return the pinned corrected 6,585-vector and compact exact diagnostics."""
    dependencies = _dependency_hashes()
    if SPECTRAL_NUMERATORS != tuple(structural_source.SPECTRAL_NUMERATORS):
        raise ArithmeticError("spectral numerator formula drifted")
    if SPECTRAL_DENOMINATOR != int(structural_source.SPECTRAL_DENOMINATOR):
        raise ArithmeticError("spectral denominator formula drifted")
    quartic_result = _construct_quartic()
    full_result = _assemble_full(quartic_result)
    _require_fingerprint_pins(quartic_result, full_result)
    return (
        np.asarray(full_result["numerator"], dtype=np.int64),
        int(full_result["common_denominator"]),
        {
            "dependency_hashes": dependencies,
            "quartic": quartic_result,
            "full": full_result,
            "v20_physical_target_artifact_read": False,
        },
    )


def build_report(*, require_frozen_fingerprints: bool = True) -> dict[str, Any]:
    dependencies = _dependency_hashes()
    if SPECTRAL_NUMERATORS != tuple(structural_source.SPECTRAL_NUMERATORS):
        raise ArithmeticError("spectral numerator formula drifted")
    if SPECTRAL_DENOMINATOR != int(structural_source.SPECTRAL_DENOMINATOR):
        raise ArithmeticError("spectral denominator formula drifted")
    quartic_result = _construct_quartic()
    full_result = _assemble_full(quartic_result)
    if require_frozen_fingerprints:
        _require_fingerprint_pins(quartic_result, full_result)
    safety = quartic_result["safety"]
    if not all(
        int(safety[key]) <= INT64_MAX
        for key in (
            "maximum_preoperation_matmul_bound",
            "maximum_preoperation_scale_bound",
            "maximum_preoperation_add_bound",
            "maximum_observed_sparse_entry",
        )
    ):
        raise ArithmeticError("recorded int64 safety bound is unsafe")
    return {
        "status": STATUS,
        "scope": {
            "location": "v21 publication bundle generation-time source",
            "repository_modified": False,
            "v20_raw_schur_physical_target_consumed": False,
            "corrected_quartic_RHS_reconstructed_exact": True,
            "corrected_full_6585_RHS_assembled_exact": True,
            "required_corrected_positive_Gram_map_sha256": "1834c8439fa3e44459f7ba871420a4351cd0b4de194dec6f5c4a84c1f39d3a16",
            "semidefinite_feasibility_claimed_by_this_source": False,
            "arbitrary_Phi_endpoint_claimed_by_this_source": False,
            "G3_closed": False,
        },
        "provenance": {
            "hash_algorithm": "SHA256 of UTF-8 text after LF normalization",
            "expected_dependency_hashes": EXPECTED_DEPENDENCY_HASHES,
            "actual_dependency_hashes": dependencies,
            "all_dependency_hashes_match_exact": dependencies
            == EXPECTED_DEPENDENCY_HASHES,
        },
        "formula": {
            "ordered_operator": "sum(k=0..7, n_k K^k) / 221184000",
            "spectral_numerators_degree_0_through_7": SPECTRAL_NUMERATORS,
            "spectral_denominator": SPECTRAL_DENOMINATOR,
            "packed_to_ordered_rule": (
                "x_i*x_j maps to e_i tensor e_j plus e_j tensor e_i when i!=j"
            ),
            "quartic_coefficient_rule": (
                "sum the ordered spectral bilinear over all distinct ordered 2+2 splits"
            ),
        },
        "quartic": {
            "row_count": QUARTIC_ROW_COUNT,
            "common_denominator": quartic_result["common_denominator"],
            "nonzero_count": quartic_result["nonzero_count"],
            "maximum_absolute_numerator": quartic_result[
                "maximum_absolute_numerator"
            ],
            "numerator_sha256": quartic_result["numerator_sha256"],
            "ordered_edge_count": quartic_result["ordered_edge_count"],
            "unique_packed_pair_column_count": quartic_result[
                "unique_packed_pair_column_count"
            ],
            "packed_to_ordered_columns_checked_independently": quartic_result[
                "packed_to_ordered_columns_checked_independently"
            ],
            "row_by_row_direct_evaluator_count": QUARTIC_ROW_COUNT,
            "row_by_row_direct_evaluator_mismatch_count": quartic_result[
                "row_by_row_direct_evaluator_mismatch_count"
            ],
            "odd_channel_row_count": quartic_result["odd_channel_row_count"],
            "all_odd_channel_coefficients_zero_exact": quartic_result[
                "all_odd_channel_coefficients_zero_exact"
            ],
        },
        "full_graded_RHS": {
            "grade_order": ("constant", "linear", "quadratic", "cubic", "quartic"),
            "grade_lengths": full_result["grade_lengths"],
            "row_count": FULL_ROW_COUNT,
            "common_denominator": full_result["common_denominator"],
            "nonzero_count_by_grade": full_result["nonzero_count_by_grade"],
            "total_nonzero_count": full_result["total_nonzero_count"],
            "maximum_absolute_numerator": full_result["maximum_absolute_numerator"],
            "numerator_sha256": full_result["numerator_sha256"],
        },
        "first_pivot_independent_python_int_direct": quartic_result[
            "first_pivot_independent_python_int_direct"
        ],
        "exact_arithmetic_safety": safety,
        "root_cause": {
            "first_exact_discrepancy": (
                "raw-Schur fits oriented highest/conjugate-highest minors, whereas the "
                "physical quartic chart collapses the complete symmetric tensor polynomial"
            ),
            "bounded_target_repair": (
                "replace the extremal-minor raw-Schur RHS with this direct ordered-spectral "
                "6057-row reconstruction"
            ),
            "separate_map_repair": (
                "divide linear_column solved coordinates by 16; grade pairs 00,02,11,12,22 "
                "already match exact carrier evaluations"
            ),
        },
        "proof_grade": True,
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--discover-fingerprints",
        action="store_true",
        help="compute exact fingerprints before they are pinned; still makes no theorem claim",
    )
    args = parser.parse_args()
    report = build_report(require_frozen_fingerprints=not args.discover_fingerprints)
    print(json.dumps(_jsonable(report), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
