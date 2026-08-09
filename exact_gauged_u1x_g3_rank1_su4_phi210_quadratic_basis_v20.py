#!/usr/bin/env python3
"""Exact real SU(4)-invariant quadratic basis on the canonical Phi210 chart.

At the certified rank-one endpoint, the live SU(4) stabilizer acts on
``Phi210 = Lambda^4(R^10)`` by fifteen integral real skew matrices.  This
module constructs an explicit basis of every real symmetric matrix ``Q``
satisfying

    Q G_a - G_a Q = 0,  a=1,...,15.

The construction is exact and deterministic.  In the Gaussian exterior
basis, the three Cartan equations leave 551 symmetric weight-zero monomials.
The remaining twelve generator equations give a sparse integer system of
rank 506.  Its 45-dimensional nullspace has a deterministic integral basis.
Pullback through the exact Gaussian change of basis, followed by taking real
and imaginary parts and primitive normalization, gives 45 independent real
integral symmetric 210 by 210 matrices in the live canonical Phi chart.

Completeness is not inferred from a numerical nullity.  Modular rank 506 and
45 exact integer nullvectors prove the reduced-system nullity over Q, while
the independently certified SU(4) branching gives the real-form upper bound

    (10+10+3+1) + (16+1+4) = 24+21 = 45.

This closes only the invariant-quadratic-basis infrastructure needed by a
future augmented Schur/SOS calculation.  It does not construct that SDP,
prove the arbitrary-Phi lower bound, close G3, or validate the full theory.
"""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
import math
from numbers import Integral, Rational
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
from scipy import sparse

import exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20 as intertwiners
import exact_gauged_u1x_g3_rank1_su4_stabilizer_v20 as stabilizer


ROOT = Path(__file__).resolve().parent
OUT_JSON = (
    ROOT
    / "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_QUADRATIC_BASIS_V20.json"
)
OUT_MD = (
    ROOT
    / "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_QUADRATIC_BASIS_V20.md"
)
EXPECTED_MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
MODEL_CONTRACT_ID = stabilizer.MODEL_CONTRACT_ID
EXPECTED_INTERTWINER_STATUS = (
    "EXACT_RANK1_SU4_PHI210_INTERTWINER_INFRASTRUCTURE_CERTIFIED"
)
EXPECTED_INTERTWINER_OVERALL_STATE = (
    "SU4_SCHUR_INFRASTRUCTURE_CLOSED__SDP_AND_G3_OPEN"
)
STATUS = "EXACT_RANK1_SU4_PHI210_QUADRATIC_BASIS_CERTIFIED"
OVERALL_STATE = (
    "SU4_INVARIANT_QUADRATIC_BASIS_CLOSED__AUGMENTED_SDP_AND_G3_OPEN"
)
PHI_DIMENSION = 210
BASIS_DIMENSION = 45
MODULAR_PRIME = 1_000_003

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
SELF_CONJUGATE_REAL_TYPES = {
    "1": {"multiplicity": 4, "symmetric_pairings": 10},
    "6": {"multiplicity": 4, "symmetric_pairings": 10},
    "15": {"multiplicity": 2, "symmetric_pairings": 3},
    "20prime": {"multiplicity": 1, "symmetric_pairings": 1},
}
COMPLEX_HERMITIAN_TYPES = {
    "4/4bar": {"multiplicity": 4, "Hermitian_real_dimension": 16},
    "10/10bar": {"multiplicity": 1, "Hermitian_real_dimension": 1},
    "20/20bar": {"multiplicity": 2, "Hermitian_real_dimension": 4},
}


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    return value


def _sparse_is_zero(matrix: sparse.spmatrix) -> bool:
    value = matrix.tocsr(copy=True)
    value.eliminate_zeros()
    return value.nnz == 0


def _file_sha256(path: Path) -> str:
    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def _update_sparse_hash(digest: Any, matrix: sparse.spmatrix) -> None:
    value = matrix.tocsr(copy=True)
    value.sum_duplicates()
    value.sort_indices()
    value.eliminate_zeros()
    digest.update(np.asarray(value.shape, dtype="<i8").tobytes())
    digest.update(np.asarray(value.indptr, dtype="<i8").tobytes())
    digest.update(np.asarray(value.indices, dtype="<i8").tobytes())
    digest.update(np.asarray(value.data, dtype="<i8").tobytes())


def _sparse_sequence_sha256(matrices: Iterable[sparse.spmatrix]) -> str:
    digest = hashlib.sha256()
    for matrix in matrices:
        _update_sparse_hash(digest, matrix)
    return digest.hexdigest()


def _dense_integer_sha256(matrix: np.ndarray) -> str:
    value = np.asarray(matrix, dtype="<i8")
    digest = hashlib.sha256()
    digest.update(np.asarray(value.shape, dtype="<i8").tobytes())
    digest.update(value.tobytes())
    return digest.hexdigest()


def _upper_triangle_index(row: int, column: int, dimension: int) -> int:
    if not 0 <= row <= column < dimension:
        raise ValueError("upper-triangle index requires 0 <= row <= column < n")
    return row * dimension - row * (row - 1) // 2 + column - row


@lru_cache(maxsize=None)
def _upper_triangle_pair(index: int, dimension: int) -> tuple[int, int]:
    if not 0 <= index < dimension * (dimension + 1) // 2:
        raise ValueError("upper-triangle flat index is out of range")
    offset = 0
    for row in range(dimension):
        width = dimension - row
        if index < offset + width:
            return row, row + index - offset
        offset += width
    raise ArithmeticError("unreachable upper-triangle inverse")


@lru_cache(maxsize=1)
def cartan_weight_zero_pairs() -> tuple[tuple[int, int], ...]:
    """Return the 551 symmetric exterior monomials allowed by all Cartans."""
    weights = intertwiners.exterior_state_weights()
    pairs = []
    for left, left_weight in enumerate(weights):
        for right in range(left, PHI_DIMENSION):
            right_weight = weights[right]
            if all(
                left_weight[axis] + right_weight[axis] == 0
                for axis in range(3)
            ):
                pairs.append((left, right))
    if len(pairs) != 551:
        raise ArithmeticError("Cartan weight-zero monomial census drifted")
    return tuple(pairs)


def _symmetric_matrix_unit(row: int, column: int) -> sparse.csr_matrix:
    if row == column:
        return sparse.csr_matrix(
            ([1], ([row], [column])),
            shape=(PHI_DIMENSION, PHI_DIMENSION),
            dtype=np.int64,
        )
    return sparse.csr_matrix(
        ([1, 1], ([row, column], [column, row])),
        shape=(PHI_DIMENSION, PHI_DIMENSION),
        dtype=np.int64,
    )


@lru_cache(maxsize=1)
def _cartan_reduced_constraint_matrix() -> sparse.csr_matrix:
    """Exact equations from the twelve non-Cartan Gaussian actions.

    Rows use ``(generator, upper-triangle matrix entry)`` ordering.  Columns
    use :func:`cartan_weight_zero_pairs`.  Zero rows are removed without
    changing the remaining deterministic order.
    """
    pairs = cartan_weight_zero_pairs()
    row_count_per_generator = PHI_DIMENSION * (PHI_DIMENSION + 1) // 2
    rows: list[int] = []
    columns: list[int] = []
    values: list[int] = []
    exterior_actions = intertwiners.su4_exterior_actions()
    if len(exterior_actions) != 15:
        raise ArithmeticError("live exterior generator census drifted")

    for generator_index, (real, imaginary) in enumerate(exterior_actions[3:]):
        if bool(real.nnz) == bool(imaginary.nnz):
            raise ArithmeticError(
                "non-Cartan generator is not purely real or purely imaginary"
            )
        generator = real if real.nnz else imaginary
        for variable_index, (left, right) in enumerate(pairs):
            unit = _symmetric_matrix_unit(left, right)
            residual = (generator.T @ unit + unit @ generator).tocoo()
            for row, column, coefficient in zip(
                residual.row,
                residual.col,
                residual.data,
                strict=True,
            ):
                if row <= column and coefficient:
                    rows.append(
                        generator_index * row_count_per_generator
                        + _upper_triangle_index(
                            int(row), int(column), PHI_DIMENSION
                        )
                    )
                    columns.append(variable_index)
                    values.append(int(coefficient))

    matrix = sparse.coo_matrix(
        (values, (rows, columns)),
        shape=(12 * row_count_per_generator, len(pairs)),
        dtype=np.int64,
    ).tocsr()
    matrix.sum_duplicates()
    matrix.eliminate_zeros()
    nonzero_rows = np.flatnonzero(np.diff(matrix.indptr))
    matrix = matrix[nonzero_rows].tocsr()
    matrix.sort_indices()
    if matrix.shape != (5952, 551) or matrix.nnz != 13296:
        raise ArithmeticError("reduced SU(4) constraint system drifted")
    return matrix


def _row_echelon_mod_prime(
    matrix: np.ndarray, prime: int = MODULAR_PRIME
) -> tuple[dict[int, np.ndarray], tuple[int, ...]]:
    """Deterministic reduced row basis over ``F_prime``."""
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


def _rank_mod_prime(matrix: np.ndarray, prime: int = MODULAR_PRIME) -> int:
    _, pivots = _row_echelon_mod_prime(matrix, prime)
    return len(pivots)


@lru_cache(maxsize=1)
def _exterior_nullspace_data() -> tuple[np.ndarray, tuple[int, ...]]:
    constraints = _cartan_reduced_constraint_matrix()
    pivot_rows, pivots = _row_echelon_mod_prime(constraints.toarray())
    free_columns = tuple(
        column for column in range(constraints.shape[1])
        if column not in pivot_rows
    )
    vectors = np.zeros(
        (constraints.shape[1], len(free_columns)), dtype=np.int64
    )
    for output_column, free in enumerate(free_columns):
        vectors[free, output_column] = 1
        for pivot in pivots:
            vectors[pivot, output_column] = -int(
                pivot_rows[pivot][free]
            ) % MODULAR_PRIME
    vectors[vectors > MODULAR_PRIME // 2] -= MODULAR_PRIME
    if vectors.shape != (551, BASIS_DIMENSION):
        raise ArithmeticError("reduced nullspace dimension drifted")
    if int(np.max(np.abs(vectors), initial=0)) != 1:
        raise ArithmeticError("canonical nullvectors ceased to be {-1,0,1}")
    if np.any(constraints @ vectors):
        raise ArithmeticError("modular nullvectors did not lift over Z")
    vectors.setflags(write=False)
    return vectors, free_columns


def exact_exterior_nullspace() -> np.ndarray:
    """Return a copy of the exact 551 by 45 integer nullspace matrix."""
    return _exterior_nullspace_data()[0].copy()


def _exterior_symmetric_matrix(vector: np.ndarray) -> sparse.csr_matrix:
    pairs = cartan_weight_zero_pairs()
    rows: list[int] = []
    columns: list[int] = []
    values: list[int] = []
    for index in np.flatnonzero(vector):
        left, right = pairs[int(index)]
        coefficient = int(vector[index])
        rows.append(left)
        columns.append(right)
        values.append(coefficient)
        if left != right:
            rows.append(right)
            columns.append(left)
            values.append(coefficient)
    matrix = sparse.csr_matrix(
        (values, (rows, columns)),
        shape=(PHI_DIMENSION, PHI_DIMENSION),
        dtype=np.int64,
    )
    matrix.sort_indices()
    return matrix


def _primitive_symmetric_matrix(
    matrix: sparse.spmatrix,
) -> tuple[sparse.csr_matrix, int]:
    value = matrix.tocsr(copy=True)
    value.sum_duplicates()
    value.eliminate_zeros()
    value.sort_indices()
    if value.nnz == 0:
        raise ValueError("zero matrix has no primitive normalization")
    content = 0
    for entry in value.data:
        content = math.gcd(content, abs(int(entry)))
    data = np.asarray(value.data // content, dtype=np.int64)
    value = sparse.csr_matrix(
        (data, value.indices.copy(), value.indptr.copy()),
        shape=value.shape,
        dtype=np.int64,
    )
    if int(value.data[0]) < 0:
        value = -value
    value.sort_indices()
    return value, content


def _upper_triangle_vector(matrix: sparse.spmatrix) -> np.ndarray:
    coo = sparse.triu(matrix, format="coo")
    output = np.zeros(
        PHI_DIMENSION * (PHI_DIMENSION + 1) // 2, dtype=np.int64
    )
    indices = (
        coo.row * PHI_DIMENSION
        - coo.row * (coo.row - 1) // 2
        + coo.col
        - coo.row
    )
    output[indices] = coo.data
    return output


def _select_independent_vectors_mod_prime(
    vectors: Sequence[np.ndarray], prime: int = MODULAR_PRIME
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    pivot_vectors: dict[int, np.ndarray] = {}
    selected: list[int] = []
    pivot_coordinates: list[int] = []
    for index, input_vector in enumerate(vectors):
        vector = np.remainder(input_vector, prime)
        while np.any(vector):
            pivot = int(np.flatnonzero(vector)[0])
            if pivot in pivot_vectors:
                vector = (
                    vector - vector[pivot] * pivot_vectors[pivot]
                ) % prime
                continue
            vector = vector * pow(int(vector[pivot]), -1, prime) % prime
            pivot_vectors[pivot] = vector
            selected.append(index)
            pivot_coordinates.append(pivot)
            break
    return tuple(selected), tuple(pivot_coordinates)


@lru_cache(maxsize=1)
def _basis_data() -> tuple[
    tuple[sparse.csr_matrix, ...], tuple[dict[str, Any], ...], dict[str, Any]
]:
    exterior_vectors, _ = _exterior_nullspace_data()
    basis_real, basis_imaginary = intertwiners.gaussian_exterior_basis()
    basis_real = basis_real.tocsr()
    basis_imaginary = basis_imaginary.tocsr()

    candidates: list[sparse.csr_matrix] = []
    candidate_metadata: list[dict[str, Any]] = []
    for kernel_column in range(exterior_vectors.shape[1]):
        exterior_matrix = _exterior_symmetric_matrix(
            exterior_vectors[:, kernel_column]
        )
        # If B=Br+iBi and B^dagger B=16I, then
        # B^{-T} M B^{-1} = conjugate(B) M B^dagger / 256.
        # The common denominator is immaterial for a basis, and primitive
        # normalization removes the integer content of each real/imaginary
        # numerator independently.
        real_numerator = (
            basis_real @ exterior_matrix @ basis_real.T
            - basis_imaginary @ exterior_matrix @ basis_imaginary.T
        ).tocsr()
        imaginary_numerator = -(
            basis_real @ exterior_matrix @ basis_imaginary.T
            + basis_imaginary @ exterior_matrix @ basis_real.T
        ).tocsr()
        for component, numerator in (
            ("real", real_numerator),
            ("imaginary", imaginary_numerator),
        ):
            numerator.eliminate_zeros()
            if numerator.nnz == 0:
                continue
            primitive, content = _primitive_symmetric_matrix(numerator)
            candidates.append(primitive)
            candidate_metadata.append(
                {
                    "exterior_nullspace_column": kernel_column,
                    "canonical_component": component,
                    "pullback_numerator_content": content,
                    "pre_normalization_denominator": 256,
                }
            )

    candidate_vectors = [_upper_triangle_vector(row) for row in candidates]
    selected, pivot_coordinates = _select_independent_vectors_mod_prime(
        candidate_vectors
    )
    matrices = tuple(candidates[index] for index in selected)
    metadata = tuple(
        {
            **candidate_metadata[index],
            "basis_index": output_index,
            "nnz": matrices[output_index].nnz,
            "maximum_absolute_entry": int(
                np.max(np.abs(matrices[output_index].data), initial=0)
            ),
            "Frobenius_norm_squared": int(
                matrices[output_index]
                .multiply(matrices[output_index])
                .sum()
            ),
            "matrix_sha256": _sparse_sequence_sha256(
                (matrices[output_index],)
            ),
        }
        for output_index, index in enumerate(selected)
    )
    if len(candidates) != 73 or len(matrices) != BASIS_DIMENSION:
        raise ArithmeticError("canonical real candidate rank drifted")
    if any(matrix.dtype != np.int64 for matrix in matrices):
        raise ArithmeticError("canonical basis ceased to be integral int64")

    construction = {
        "nonzero_real_imaginary_candidate_count": len(candidates),
        "selected_candidate_indices": selected,
        "selected_candidate_origins": tuple(
            (
                candidate_metadata[index]["exterior_nullspace_column"],
                candidate_metadata[index]["canonical_component"],
            )
            for index in selected
        ),
        "modular_pivot_upper_triangle_flat_indices": pivot_coordinates,
        "modular_pivot_upper_triangle_coordinates": tuple(
            _upper_triangle_pair(index, PHI_DIMENSION)
            for index in pivot_coordinates
        ),
    }
    return matrices, metadata, construction


def exact_invariant_quadratic_basis() -> tuple[sparse.csr_matrix, ...]:
    """Return the 45 primitive integer symmetric invariant matrices.

    Fresh CSR copies are returned so callers cannot mutate the cached
    publication basis.
    """
    return tuple(matrix.copy() for matrix in _basis_data()[0])


@lru_cache(maxsize=1)
def _quadratic_basis_gram_cached() -> np.ndarray:
    matrices = _basis_data()[0]
    gram = np.zeros((BASIS_DIMENSION, BASIS_DIMENSION), dtype=np.int64)
    for left, left_matrix in enumerate(matrices):
        for right in range(left + 1):
            value = int(left_matrix.multiply(matrices[right]).sum())
            gram[left, right] = value
            gram[right, left] = value
    gram.setflags(write=False)
    return gram


def quadratic_basis_gram_matrix() -> np.ndarray:
    """Return the exact Frobenius Gram matrix of the ordered basis."""
    return _quadratic_basis_gram_cached().copy()


def quadratic_matrix_to_polynomial_coefficients(
    matrix: sparse.spmatrix,
) -> np.ndarray:
    """Encode ``phi.T Q phi`` in the ordered ``i<=j`` monomial basis.

    The convention is deliberately explicit: the diagonal coefficient is
    ``Q[i,i]`` and the off-diagonal coefficient is ``2*Q[i,j]``.  Therefore
    the returned vector contracts directly with monomials ``phi[i]*phi[j]``
    without an implicit symmetry factor.
    """
    value = matrix.tocsr(copy=True)
    value.sum_duplicates()
    value.eliminate_zeros()
    if value.shape != (PHI_DIMENSION, PHI_DIMENSION):
        raise ValueError("quadratic matrix must have shape 210 by 210")
    if not np.issubdtype(value.dtype, np.integer):
        raise TypeError("quadratic matrix must have exact integer entries")
    # Sparse subtraction in the input dtype is not a safe symmetry check for
    # unsigned or boundary-width integers.  Sparse inequality compares the
    # entries without first forming a potentially overflowing difference.
    if (value != value.T).nnz:
        raise ValueError("quadratic matrix must be symmetric")

    # The public polynomial encoding is int64.  Its off-diagonal convention
    # doubles Q[i,j], so validate every live entry with Python integers before
    # allocating or multiplying an int64 output.  In particular, Q[0,1] equal
    # to int64.max must raise instead of silently becoming -2.
    int64 = np.iinfo(np.int64)
    upper = sparse.triu(value, format="coo")
    for row, column, entry in zip(
        upper.row, upper.col, upper.data, strict=True
    ):
        exact_entry = int(entry)
        multiplier = 1 if int(row) == int(column) else 2
        encoded_entry = multiplier * exact_entry
        if encoded_entry < int64.min or encoded_entry > int64.max:
            raise OverflowError(
                "quadratic polynomial encoding exceeds exact int64 capacity"
            )
    output = _upper_triangle_vector(value)
    for row in range(PHI_DIMENSION):
        start = _upper_triangle_index(row, row, PHI_DIMENSION)
        output[start + 1 : start + PHI_DIMENSION - row] *= 2
    return output


def quadratic_polynomial_coefficients_to_matrix(
    coefficients: Sequence[Rational],
) -> tuple[sparse.csr_matrix, int]:
    """Invert the explicit upper-triangle polynomial convention exactly.

    Returns ``(N,d)`` with ``d>0`` representing the symmetric matrix ``N/d``.
    Off-diagonal polynomial coefficients are divided by two, exactly matching
    :func:`quadratic_matrix_to_polynomial_coefficients`.
    """
    expected = PHI_DIMENSION * (PHI_DIMENSION + 1) // 2
    if len(coefficients) != expected:
        raise ValueError(f"expected exactly {expected} polynomial coefficients")
    rational: list[Fraction] = []
    for index, coefficient in enumerate(coefficients):
        if isinstance(coefficient, bool) or not isinstance(
            coefficient, Rational
        ):
            raise TypeError("polynomial coefficients must be exact rationals")
        row, column = _upper_triangle_pair(index, PHI_DIMENSION)
        value = Fraction(coefficient)
        if row != column:
            value /= 2
        rational.append(value)
    denominator = 1
    for value in rational:
        denominator = math.lcm(denominator, value.denominator)
    rows: list[int] = []
    columns: list[int] = []
    entries: list[int] = []
    for index, value in enumerate(rational):
        numerator = value.numerator * (denominator // value.denominator)
        if not numerator:
            continue
        if abs(numerator) > np.iinfo(np.int64).max:
            raise OverflowError("polynomial reconstruction exceeds int64")
        row, column = _upper_triangle_pair(index, PHI_DIMENSION)
        rows.append(row)
        columns.append(column)
        entries.append(int(numerator))
        if row != column:
            rows.append(column)
            columns.append(row)
            entries.append(int(numerator))
    matrix = sparse.csr_matrix(
        (entries, (rows, columns)),
        shape=(PHI_DIMENSION, PHI_DIMENSION),
        dtype=np.int64,
    )
    matrix.sort_indices()
    if matrix.nnz == 0:
        return matrix, 1
    common = denominator
    for entry in matrix.data:
        common = math.gcd(common, abs(int(entry)))
    if common > 1:
        matrix = sparse.csr_matrix(
            (
                np.asarray(matrix.data // common, dtype=np.int64),
                matrix.indices.copy(),
                matrix.indptr.copy(),
            ),
            shape=matrix.shape,
            dtype=np.int64,
        )
        denominator //= common
    return matrix, denominator


@lru_cache(maxsize=1)
def _primitive_polynomial_basis_cached() -> tuple[np.ndarray, tuple[int, ...]]:
    rows = []
    contents = []
    for matrix in _basis_data()[0]:
        coefficients = quadratic_matrix_to_polynomial_coefficients(matrix)
        content = 0
        for entry in coefficients:
            content = math.gcd(content, abs(int(entry)))
        if content == 0:
            raise ArithmeticError("zero quadratic entered the publication basis")
        primitive = coefficients // content
        first = int(primitive[np.flatnonzero(primitive)[0]])
        if first < 0:
            primitive = -primitive
            content = -content
        rows.append(primitive)
        contents.append(content)
    matrix = np.asarray(rows, dtype=np.int64)
    matrix.setflags(write=False)
    return matrix, tuple(contents)


def primitive_quadratic_polynomial_basis() -> tuple[np.ndarray, tuple[int, ...]]:
    """Return primitive polynomial rows and their scale to the integer Qs.

    If ``(P,s)`` is returned, then the polynomial encoded by integer matrix
    ``Q_a`` is ``s[a] * P[a]`` in the explicit ``i<=j`` convention.  Thus
    ``P[a]`` itself corresponds to the rational symmetric matrix ``Q_a/s[a]``.
    """
    matrix, contents = _primitive_polynomial_basis_cached()
    return matrix.copy(), contents


def reconstruct_quadratic_form(
    coefficients: Sequence[Rational],
) -> tuple[sparse.csr_matrix, int]:
    """Reconstruct an exact rational invariant quadratic matrix.

    The returned pair ``(N,d)`` has ``d>0`` and represents ``Q=N/d``.
    Integer and :class:`fractions.Fraction` coefficients are accepted.  The
    numerator is content-reduced against the denominator.
    """
    if len(coefficients) != BASIS_DIMENSION:
        raise ValueError(f"expected exactly {BASIS_DIMENSION} coefficients")
    rational: list[Fraction] = []
    for coefficient in coefficients:
        if isinstance(coefficient, bool) or not isinstance(
            coefficient, Rational
        ):
            raise TypeError("coefficients must be exact rational numbers")
        rational.append(Fraction(coefficient))
    denominator = 1
    for coefficient in rational:
        denominator = math.lcm(denominator, coefficient.denominator)
    integer_coefficients = [
        coefficient.numerator * (denominator // coefficient.denominator)
        for coefficient in rational
    ]
    limit = np.iinfo(np.int64).max
    matrices = _basis_data()[0]
    entry_bound = sum(
        abs(coefficient)
        * int(np.max(np.abs(matrix.data), initial=0))
        for coefficient, matrix in zip(
            integer_coefficients, matrices, strict=True
        )
    )
    if entry_bound > limit:
        raise OverflowError("reconstruction exceeds exact int64 capacity")

    output = sparse.csr_matrix(
        (PHI_DIMENSION, PHI_DIMENSION), dtype=np.int64
    )
    for coefficient, matrix in zip(
        integer_coefficients, matrices, strict=True
    ):
        if coefficient:
            output = output + int(coefficient) * matrix
    output = output.tocsr()
    output.sum_duplicates()
    output.eliminate_zeros()
    output.sort_indices()
    if output.nnz == 0:
        return output, 1
    common = denominator
    for entry in output.data:
        common = math.gcd(common, abs(int(entry)))
    if common > 1:
        output = sparse.csr_matrix(
            (
                np.asarray(output.data // common, dtype=np.int64),
                output.indices.copy(),
                output.indptr.copy(),
            ),
            shape=output.shape,
            dtype=np.int64,
        )
        denominator //= common
    return output, denominator


def evaluate_invariant_quadratics(
    phi: Sequence[Integral],
) -> tuple[int, ...]:
    """Evaluate all 45 basis quadratics exactly on an integral Phi vector."""
    if len(phi) != PHI_DIMENSION:
        raise ValueError(f"expected a Phi vector of length {PHI_DIMENSION}")
    if any(isinstance(value, bool) or not isinstance(value, Integral) for value in phi):
        raise TypeError("Phi entries must be exact integers")
    vector = tuple(int(value) for value in phi)
    values = []
    for matrix in _basis_data()[0]:
        coo = matrix.tocoo()
        total = sum(
            int(entry) * vector[int(row)] * vector[int(column)]
            for row, column, entry in zip(
                coo.row, coo.col, coo.data, strict=True
            )
        )
        values.append(total)
    return tuple(values)


def _real_form_census(
    branching: dict[str, Any],
) -> dict[str, Any]:
    observed = branching.get("observed_irrep_multiplicities")
    branching_exact = observed == EXPECTED_BRANCHING
    self_rows = copy.deepcopy(SELF_CONJUGATE_REAL_TYPES)
    complex_rows = copy.deepcopy(COMPLEX_HERMITIAN_TYPES)
    self_total = sum(
        row["symmetric_pairings"] for row in self_rows.values()
    )
    complex_total = sum(
        row["Hermitian_real_dimension"] for row in complex_rows.values()
    )
    return {
        "complexified_branching": observed,
        "expected_complexified_branching": EXPECTED_BRANCHING,
        "branching_exact": branching_exact,
        "self_conjugate_real_types": self_rows,
        "self_conjugate_symmetric_pairing_dimension": self_total,
        "complex_types_with_conjugates": complex_rows,
        "complex_Hermitian_real_dimension": complex_total,
        "total_real_symmetric_invariant_dimension_upper_bound": (
            self_total + complex_total
        ),
        "dimension_identity": "(10+10+3+1)+(16+1+4)=24+21=45",
        "real_form_argument": (
            "For the real live Phi210 representation, complexification "
            "commutes with taking Lie-algebra invariants. Self-conjugate "
            "real irreps 1, 6, 15 and 20prime contribute m(m+1)/2; each "
            "complex irrep paired with its conjugate contributes the real "
            "dimension m^2 of Hermitian multiplicity matrices."
        ),
        "proof_grade": bool(
            branching_exact
            and self_total == 24
            and complex_total == 21
            and self_total + complex_total == BASIS_DIMENSION
        ),
    }


def _constraint_certificate() -> dict[str, Any]:
    matrix = _cartan_reduced_constraint_matrix()
    nullspace, free_columns = _exterior_nullspace_data()
    modular_rank = _rank_mod_prime(matrix.toarray())
    residual = matrix @ nullspace

    exterior_actions = intertwiners.su4_exterior_actions()
    exterior_invariance = True
    for column in range(nullspace.shape[1]):
        form = _exterior_symmetric_matrix(nullspace[:, column])
        for real, imaginary in exterior_actions:
            real_residual = real.T @ form + form @ real
            imaginary_residual = imaginary.T @ form + form @ imaginary
            if not (
                _sparse_is_zero(real_residual)
                and _sparse_is_zero(imaginary_residual)
            ):
                exterior_invariance = False
                break

    return {
        "Cartan_generator_count": 3,
        "non_Cartan_generator_count": 12,
        "Cartan_weight_zero_symmetric_monomial_count": len(
            cartan_weight_zero_pairs()
        ),
        "reduced_constraint_shape": matrix.shape,
        "reduced_constraint_nnz": matrix.nnz,
        "reduced_constraint_maximum_absolute_entry": int(
            np.max(np.abs(matrix.data), initial=0)
        ),
        "modular_prime": MODULAR_PRIME,
        "reduced_constraint_rank_mod_prime": modular_rank,
        "free_column_count": len(free_columns),
        "integer_nullspace_shape": nullspace.shape,
        "integer_nullspace_maximum_absolute_entry": int(
            np.max(np.abs(nullspace), initial=0)
        ),
        "integer_nullspace_nnz": int(np.count_nonzero(nullspace)),
        "integer_nullspace_residual_zero_exact": not np.any(residual),
        "all_45_nullvectors_invariant_under_all_15_exterior_actions_exact": (
            exterior_invariance
        ),
        "rank_nullity_argument": (
            "Rank 506 after reduction modulo 1000003 is a lower bound on "
            "the rational rank. The 45 displayed integer nullvectors give "
            "the matching upper bound 551-45=506, so the rational rank and "
            "nullity are exactly 506 and 45."
        ),
        "exact_rational_rank": 506 if not np.any(residual) else None,
        "exact_rational_nullity": 45 if not np.any(residual) else None,
        "constraint_sha256": _sparse_sequence_sha256((matrix,)),
        "nullspace_sha256": _dense_integer_sha256(nullspace),
        "proof_grade": bool(
            matrix.shape == (5952, 551)
            and matrix.nnz == 13296
            and modular_rank == 506
            and len(free_columns) == BASIS_DIMENSION
            and nullspace.shape == (551, BASIS_DIMENSION)
            and int(np.max(np.abs(nullspace), initial=0)) == 1
            and not np.any(residual)
            and exterior_invariance
        ),
    }


def _basis_certificate(
    matrices: Sequence[sparse.spmatrix],
) -> dict[str, Any]:
    live_actions = stabilizer.exact_phi210_actions()
    shape_exact = all(
        matrix.shape == (PHI_DIMENSION, PHI_DIMENSION)
        for matrix in matrices
    )
    integral_exact = all(
        np.issubdtype(matrix.dtype, np.integer) for matrix in matrices
    )
    symmetric_exact = all(
        _sparse_is_zero(matrix - matrix.T) for matrix in matrices
    )
    primitive_exact = True
    canonical_sign_exact = True
    for matrix in matrices:
        value = matrix.tocsr(copy=True)
        value.eliminate_zeros()
        if not value.nnz:
            primitive_exact = False
            canonical_sign_exact = False
            continue
        content = 0
        for entry in value.data:
            content = math.gcd(content, abs(int(entry)))
        primitive_exact &= content == 1
        canonical_sign_exact &= int(value.data[0]) > 0

    invariant_exact = len(live_actions) == 15 and all(
        _sparse_is_zero(matrix @ generator - generator @ matrix)
        for matrix in matrices
        for generator in live_actions
    )
    vectors = [_upper_triangle_vector(matrix) for matrix in matrices]
    if vectors:
        stacked = np.column_stack(vectors)
        modular_rank = _rank_mod_prime(stacked.T)
    else:
        stacked = np.zeros((0, 0), dtype=np.int64)
        modular_rank = 0

    gram = np.zeros((len(matrices), len(matrices)), dtype=np.int64)
    for left, left_matrix in enumerate(matrices):
        for right in range(left + 1):
            value = int(left_matrix.multiply(matrices[right]).sum())
            gram[left, right] = value
            gram[right, left] = value
    metadata = []
    polynomial_rows = []
    polynomial_contents = []
    for index, matrix in enumerate(matrices):
        value = matrix.tocsr(copy=True)
        value.eliminate_zeros()
        if (
            value.shape == (PHI_DIMENSION, PHI_DIMENSION)
            and np.issubdtype(value.dtype, np.integer)
            and _sparse_is_zero(value - value.T)
        ):
            polynomial = quadratic_matrix_to_polynomial_coefficients(value)
            content = 0
            for entry in polynomial:
                content = math.gcd(content, abs(int(entry)))
            if content:
                polynomial_rows.append(polynomial // content)
                polynomial_contents.append(content)
        metadata.append(
            {
                "basis_index": index,
                "nnz": value.nnz,
                "maximum_absolute_entry": int(
                    np.max(np.abs(value.data), initial=0)
                ),
                "Frobenius_norm_squared": int(value.multiply(value).sum()),
                "matrix_sha256": _sparse_sequence_sha256((value,)),
            }
        )
    polynomial_matrix = (
        np.asarray(polynomial_rows, dtype=np.int64)
        if polynomial_rows
        else np.zeros((0, 0), dtype=np.int64)
    )
    polynomial_primitive_exact = bool(
        len(polynomial_rows) == len(matrices)
        and all(
            math.gcd(
                *(
                    abs(int(entry))
                    for entry in row
                    if int(entry) != 0
                )
            )
            == 1
            for row in polynomial_rows
        )
    )
    return {
        "matrix_count": len(matrices),
        "matrix_shape": (PHI_DIMENSION, PHI_DIMENSION),
        "ordered_basis_metadata": metadata,
        "total_nnz": sum(matrix.nnz for matrix in matrices),
        "minimum_nnz": min((matrix.nnz for matrix in matrices), default=0),
        "maximum_nnz": max((matrix.nnz for matrix in matrices), default=0),
        "maximum_absolute_entry": max(
            (
                int(np.max(np.abs(matrix.data), initial=0))
                for matrix in matrices
            ),
            default=0,
        ),
        "all_shapes_210_by_210_exact": shape_exact,
        "all_entries_integral_exact": integral_exact,
        "all_matrices_symmetric_exact": symmetric_exact,
        "all_matrices_primitive_exact": primitive_exact,
        "all_canonical_first_entries_positive_exact": canonical_sign_exact,
        "all_45_commute_with_all_15_live_Phi210_generators_exact": (
            invariant_exact
        ),
        "upper_triangle_column_rank_mod_prime": modular_rank,
        "modular_prime": MODULAR_PRIME,
        "basis_sha256": _sparse_sequence_sha256(matrices),
        "Gram_shape": gram.shape,
        "Gram_sha256": _dense_integer_sha256(gram),
        "Gram_minimum_diagonal": min(
            (int(gram[index, index]) for index in range(len(matrices))),
            default=0,
        ),
        "Gram_maximum_diagonal": max(
            (int(gram[index, index]) for index in range(len(matrices))),
            default=0,
        ),
        "Gram_rank_mod_prime": _rank_mod_prime(gram)
        if len(matrices)
        else 0,
        "polynomial_monomial_count": (
            PHI_DIMENSION * (PHI_DIMENSION + 1) // 2
        ),
        "polynomial_upper_triangle_convention": (
            "coefficient(i,i)=Q[i,i]; coefficient(i,j)=2*Q[i,j] "
            "for i<j, so phi^T Q phi is the direct monomial contraction"
        ),
        "primitive_polynomial_rows_exact": polynomial_primitive_exact,
        "integer_matrix_to_primitive_polynomial_scale_factors": (
            polynomial_contents
        ),
        "primitive_polynomial_basis_sha256": (
            _dense_integer_sha256(polynomial_matrix)
            if len(polynomial_rows) == len(matrices)
            else None
        ),
        "primitive_polynomial_basis_rank_mod_prime": (
            _rank_mod_prime(polynomial_matrix)
            if len(polynomial_rows) == len(matrices) and len(matrices)
            else 0
        ),
        "independence_argument": (
            "The displayed 45 upper-triangle coordinate columns have rank "
            "45 modulo 1000003, hence rank 45 over Q and R."
        ),
        "proof_grade": bool(
            len(matrices) == BASIS_DIMENSION
            and shape_exact
            and integral_exact
            and symmetric_exact
            and primitive_exact
            and canonical_sign_exact
            and invariant_exact
            and modular_rank == BASIS_DIMENSION
            and polynomial_primitive_exact
            and _rank_mod_prime(polynomial_matrix) == BASIS_DIMENSION
        ),
    }


def _stabilizer_report_is_live_and_exact(report: dict[str, Any]) -> bool:
    """Bind this stage to the complete live endpoint/stabilizer contract."""
    scope = report.get("scope", {})
    checks = report.get("checks", {})
    tangent = report.get("joint_stabilizer_tangent", {})
    endpoint = tangent.get("fixed_endpoint", {})
    phi210 = report.get("Phi210_action", {})
    required_checks = (
        "fixed_h_minus_q_over_4_endpoint_bound_exact",
        "joint_stabilizer_kernel_exhausted_exactly_by_SU4",
        "Phi210_actions_integral_skew_faithful_and_Lie_exact",
    )
    return bool(
        report == stabilizer.build_report()
        and report.get("model_contract_id") == EXPECTED_MODEL_CONTRACT_ID
        and report.get("status") == stabilizer.STATUS
        and report.get("overall_state") == stabilizer.OVERALL_STATE
        and report.get("n_failed") == 0
        and not report.get("failed_checks")
        and all(checks.get(name) is True for name in required_checks)
        and scope.get("infrastructure_only") is True
        and scope.get("H_fixed_to_h_minus") is True
        and scope.get(
            "Sigma_fixed_to_normalized_explicit_decomposable_pure_spinor_q_over_4"
        )
        is True
        and scope.get("common_continuous_stabilizer_identified_as_SU4")
        is True
        # This is the authoritative live upstream key.  A similarly worded
        # key from another report must not be accepted as a substitute.
        and scope.get("exact_Phi210_SU4_action_available_for_next_stage")
        is True
        and scope.get("G3_closed") is False
        and tangent.get("proof_grade") is True
        and tangent.get("joint_tangent_shape") == (272, 45)
        and tangent.get("exact_tangent_rank_over_Q_R") == 30
        and tangent.get("exact_tangent_nullity") == 15
        and tangent.get("explicit_kernel_is_complete") is True
        and endpoint.get("H") == "h_-=(e0-i e1)/sqrt(2)"
        and endpoint.get("Sigma") == "q/4"
        and endpoint.get("endpoint_binding_exact") is True
        and phi210.get("proof_grade") is True
        and phi210.get("action_count") == 15
        and phi210.get("flattened_action_rank_mod_prime") == 15
        and phi210.get("skew_transpose_max_abs_residual") == 0
        and phi210.get("Lie_commutator_reconstruction_max_abs") == 0
    )


def _carrier_certificate_is_live_and_exact(
    certificate: dict[str, Any], embedded: Any
) -> bool:
    """Require the supplied carrier census to equal both embedded and live data."""
    rows = certificate.get("carriers", ())
    if not isinstance(rows, (tuple, list)):
        rows = ()
    return bool(
        certificate == embedded
        and certificate == intertwiners.exact_carrier_certificate()
        and certificate.get("proof_grade") is True
        and certificate.get("natural_exterior_block_count") == 16
        and certificate.get(
            "all_15_generators_preserve_natural_blocks_exact"
        )
        is True
        and certificate.get("carrier_count") == 25
        and len(rows) == 25
        and all(
            row.get("exact_modular_rank") == row.get("expected_dimension")
            and row.get("C8_eigen_equation_exact") is True
            and row.get("SSYT_character_exact") is True
            for row in rows
        )
        and certificate.get("observed_irrep_multiplicities")
        == EXPECTED_BRANCHING
        and certificate.get("expected_irrep_multiplicities")
        == EXPECTED_BRANCHING
        and certificate.get("concatenated_carrier_shape")
        == (PHI_DIMENSION, PHI_DIMENSION)
        and certificate.get("concatenated_carrier_rank_mod_prime")
        == PHI_DIMENSION
        and certificate.get(
            "all_carrier_dimensions_eigenvalues_characters_exact"
        )
        is True
        and certificate.get("symmetric_self_conjugate_pairings") == 24
        and certificate.get("complex_conjugate_pairings") == 21
        and certificate.get("Sym2_Phi210_SU4_singlet_dimension")
        == BASIS_DIMENSION
        and certificate.get(
            "SU4_invariant_quadratic_multiplicity_sector_dimension"
        )
        == BASIS_DIMENSION
    )


def _intertwiner_report_is_live_and_exact(report: dict[str, Any]) -> bool:
    """Bind branching/intertwining evidence to the live exact upstream report."""
    scope = report.get("scope", {})
    checks = report.get("checks", {})
    certificate = report.get("intertwiner", {})
    branching = report.get("character_branching", {})
    provenance = report.get("companion_stabilizer_provenance", {})
    required_checks = (
        "Gaussian_exterior_basis_Bdagger_B_equals_16I_exact",
        "all_15_live_SU4_intertwinings_exact",
        "SSYT_character_branching_exact",
        "deterministic_25_carrier_decomposition_complete",
        "Sym2_invariant_multiplicity_is_45_exact",
        "companion_embedded_certificates_match_live_inputs",
    )
    return bool(
        report == intertwiners.build_report()
        and report.get("model_contract_id") == EXPECTED_MODEL_CONTRACT_ID
        and report.get("status") == EXPECTED_INTERTWINER_STATUS
        and report.get("overall_state") == EXPECTED_INTERTWINER_OVERALL_STATE
        and report.get("n_failed") == 0
        and not report.get("failures")
        and all(checks.get(name) is True for name in required_checks)
        and checks.get("G3_closed") is False
        and checks.get("SU4_Schur_SDP_constructed") is False
        and checks.get("arbitrary_Phi_bound_proved") is False
        and scope.get("H_fixed_to_h_minus") is True
        and scope.get("Sigma_fixed_to_q_over_4") is True
        and scope.get("rank1_endpoint_SU4_stabilizer_used") is True
        and scope.get("companion_stabilizer_provenance_exact") is True
        and scope.get("Phi210_complexified_representation_resolved") is True
        and scope.get("deterministic_irreducible_carriers_complete") is True
        and scope.get("Sym2_SU4_invariant_dimension_45_proved") is True
        and scope.get("Schur_SOS_SDP_constructed") is False
        and scope.get("arbitrary_real_Phi_lower_bound_proved") is False
        and scope.get("G3_closed") is False
        and certificate.get("proof_grade") is True
        and certificate.get("exterior_basis_shape")
        == (PHI_DIMENSION, PHI_DIMENSION)
        and certificate.get("exterior_basis_Bdagger_B_equals_16I_exact")
        is True
        and certificate.get("intertwining_count") == 15
        and certificate.get("all_15_intertwinings_exact") is True
        and branching.get("proof_grade") is True
        and branching.get("branching_multiplicities") == EXPECTED_BRANCHING
        and provenance.get("all_required_provenance_exact") is True
        and provenance.get("model_contract_id") == EXPECTED_MODEL_CONTRACT_ID
        and provenance.get("status") == stabilizer.STATUS
    )


def _constraint_certificate_is_exact(certificate: dict[str, Any]) -> bool:
    """Validate every rank/nullspace claim against the live integer arrays."""
    matrix = _cartan_reduced_constraint_matrix()
    nullspace, free_columns = _exterior_nullspace_data()
    residual = matrix @ nullspace
    matrix_max = max((abs(int(value)) for value in matrix.data), default=0)
    nullspace_max = max(
        (abs(int(value)) for value in nullspace.flat), default=0
    )
    live_rank = _rank_mod_prime(matrix.toarray())
    return bool(
        certificate.get("proof_grade") is True
        and certificate.get("Cartan_generator_count") == 3
        and certificate.get("non_Cartan_generator_count") == 12
        and certificate.get("Cartan_weight_zero_symmetric_monomial_count")
        == 551
        and certificate.get("reduced_constraint_shape")
        == matrix.shape
        == (5952, 551)
        and certificate.get("reduced_constraint_nnz") == matrix.nnz == 13296
        and certificate.get("reduced_constraint_maximum_absolute_entry")
        == matrix_max
        and certificate.get("modular_prime") == MODULAR_PRIME
        and certificate.get("reduced_constraint_rank_mod_prime")
        == live_rank
        == 506
        and certificate.get("free_column_count")
        == len(free_columns)
        == BASIS_DIMENSION
        and certificate.get("integer_nullspace_shape")
        == nullspace.shape
        == (551, BASIS_DIMENSION)
        and certificate.get("integer_nullspace_maximum_absolute_entry")
        == nullspace_max
        and certificate.get("integer_nullspace_nnz")
        == int(np.count_nonzero(nullspace))
        and certificate.get("integer_nullspace_residual_zero_exact") is True
        and not np.any(residual)
        and certificate.get(
            "all_45_nullvectors_invariant_under_all_15_exterior_actions_exact"
        )
        is True
        and certificate.get("exact_rational_rank") == 506
        and certificate.get("exact_rational_nullity") == BASIS_DIMENSION
        and certificate.get("constraint_sha256")
        == _sparse_sequence_sha256((matrix,))
        and certificate.get("nullspace_sha256")
        == _dense_integer_sha256(nullspace)
    )


def _build_report_from_evidence(
    *,
    companion_model_contract_id: str,
    stabilizer_report: dict[str, Any],
    intertwiner_report: dict[str, Any],
    carrier_certificate: dict[str, Any],
    constraint_certificate: dict[str, Any],
    matrices: Sequence[sparse.spmatrix],
) -> dict[str, Any]:
    basis = _basis_certificate(matrices)
    census = _real_form_census(carrier_certificate)
    stabilizer_ready = _stabilizer_report_is_live_and_exact(stabilizer_report)
    intertwiner_ready = _intertwiner_report_is_live_and_exact(
        intertwiner_report
    )
    carrier_ready = _carrier_certificate_is_live_and_exact(
        carrier_certificate, intertwiner_report.get("carriers")
    )
    companion_ready = bool(
        companion_model_contract_id == EXPECTED_MODEL_CONTRACT_ID
        and MODEL_CONTRACT_ID == EXPECTED_MODEL_CONTRACT_ID
        and stabilizer_ready
        and intertwiner_ready
        and carrier_ready
    )
    constraint_ready = _constraint_certificate_is_exact(
        constraint_certificate
    )
    checks = {
        "model_contract_and_live_companions_exact": companion_ready,
        "Cartan_reduced_constraint_nullity_45_exact": bool(
            constraint_ready
            and constraint_certificate.get("exact_rational_rank") == 506
            and constraint_certificate.get("exact_rational_nullity")
            == BASIS_DIMENSION
        ),
        "real_form_completeness_upper_bound_45_exact": bool(
            census["proof_grade"]
            and census[
                "total_real_symmetric_invariant_dimension_upper_bound"
            ]
            == BASIS_DIMENSION
        ),
        "explicit_real_symmetric_integral_basis_exact": bool(
            basis["proof_grade"]
            and basis["matrix_count"] == BASIS_DIMENSION
            and basis["upper_triangle_column_rank_mod_prime"]
            == BASIS_DIMENSION
        ),
        "all_basis_matrices_live_invariant_exact": bool(
            basis[
                "all_45_commute_with_all_15_live_Phi210_generators_exact"
            ]
        ),
        "lower_and_upper_dimensions_match_exact": bool(
            basis["upper_triangle_column_rank_mod_prime"]
            == census[
                "total_real_symmetric_invariant_dimension_upper_bound"
            ]
            == BASIS_DIMENSION
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    source_paths = {
        "stabilizer": Path(stabilizer.__file__).resolve(),
        "intertwiners": Path(intertwiners.__file__).resolve(),
    }
    return {
        "status": (
            STATUS
            if not failures
            else "RANK1_SU4_PHI210_QUADRATIC_BASIS_EXECUTION_FAILED"
        ),
        "overall_state": (
            OVERALL_STATE
            if not failures
            else "EXECUTION_FAIL"
        ),
        "model_contract_id": MODEL_CONTRACT_ID,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "source_provenance": {
            "stabilizer_module": source_paths["stabilizer"].name,
            "stabilizer_module_sha256": _file_sha256(
                source_paths["stabilizer"]
            ),
            "intertwiner_module": source_paths["intertwiners"].name,
            "intertwiner_module_sha256": _file_sha256(
                source_paths["intertwiners"]
            ),
            "companion_model_contract_id": companion_model_contract_id,
            "stabilizer_status": stabilizer_report.get("status"),
            "intertwiner_status": intertwiner_report.get("status"),
            "stabilizer_report_equals_live_report_exact": stabilizer_ready,
            "intertwiner_report_equals_live_report_exact": intertwiner_ready,
            "carrier_certificate_equals_embedded_and_live_exact": (
                carrier_ready
            ),
            "all_required_live_provenance_exact": companion_ready,
        },
        "constraint_system": constraint_certificate,
        "real_form_completeness": census,
        "quadratic_basis": basis,
        "construction_metadata": _basis_data()[2]
        if len(matrices) == BASIS_DIMENSION
        and all(
            _sparse_sequence_sha256((left,))
            == _sparse_sequence_sha256((right,))
            for left, right in zip(matrices, _basis_data()[0], strict=True)
        )
        else {"canonical_construction_metadata_withheld": True},
        "reconstruction_api": {
            "basis_accessor": "exact_invariant_quadratic_basis()",
            "Gram_accessor": "quadratic_basis_gram_matrix()",
            "exact_reconstruction_accessor": "reconstruct_quadratic_form(coefficients)",
            "integral_evaluation_accessor": "evaluate_invariant_quadratics(phi)",
            "primitive_polynomial_accessor": "primitive_quadratic_polynomial_basis()",
            "matrix_to_polynomial_accessor": (
                "quadratic_matrix_to_polynomial_coefficients(Q)"
            ),
            "polynomial_to_matrix_accessor": (
                "quadratic_polynomial_coefficients_to_matrix(p)"
            ),
            "formula": "Q(c)=sum_{a=0}^{44} c_a Q_a",
            "polynomial_convention": basis[
                "polynomial_upper_triangle_convention"
            ],
            "rational_return_convention": (
                "(integer numerator CSR, positive denominator)"
            ),
            "exact_arithmetic_contract": {
                "integral_evaluation": (
                    "Every Phi entry, matrix entry, product, and accumulator "
                    "is converted to an unbounded Python integer before "
                    "arithmetic."
                ),
                "rational_reconstruction": (
                    "The int64 output preflight is the sum of each live "
                    "coefficient magnitude times that live basis matrix's "
                    "maximum absolute entry."
                ),
                "polynomial_encoding": (
                    "Every live diagonal entry and doubled off-diagonal "
                    "entry is preflighted in Python integers against the "
                    "int64 limits."
                ),
                "live_basis_maximum_absolute_entry": basis[
                    "maximum_absolute_entry"
                ],
            },
            "ordered_basis_hash": basis["basis_sha256"],
            "Gram_hash": basis["Gram_sha256"],
        },
        "scope": {
            "H_fixed_to_h_minus": companion_ready,
            "Sigma_fixed_to_q_over_4": companion_ready,
            "rank1_endpoint_SU4_stabilizer_used": companion_ready,
            "canonical_real_Phi210_chart_used": companion_ready,
            "SU4_invariant_quadratic_form_basis_constructed": not failures,
            "SU4_invariant_quadratic_form_basis_complete": not failures,
            "SU4_invariant_quadratic_form_dimension_45_exact": not failures,
            "augmented_homogeneous_Schur_SOS_SDP_constructed": False,
            "arbitrary_real_Phi_lower_bound_proved": False,
            "arbitrary_rank1_Phi_proved": False,
            "G3_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "next_exact_target": (
            "Use this ordered reconstruction basis together with the exact "
            "aligned carrier actions to assemble the full augmented SU(4)-"
            "equivariant degree-2 Schur/SOS system, including every real/"
            "Hermitian isotypic PSD block and every homogenizing cross term."
        ),
        "verdict": (
            (
                "The complete 45-dimensional real symmetric SU(4)-invariant "
                "quadratic-form space on the live canonical Phi210 chart is "
                "now explicit and exact. This is basis infrastructure only: "
                "the augmented SOS SDP, the arbitrary-Phi bound, and G3 "
                "remain open."
            )
            if not failures
            else (
                "The exact quadratic-basis certificate failed closed; no "
                "basis, SDP, arbitrary-Phi, or G3 conclusion is certified."
            )
        ),
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    return _build_report_from_evidence(
        companion_model_contract_id=stabilizer.MODEL_CONTRACT_ID,
        stabilizer_report=stabilizer.build_report(),
        intertwiner_report=intertwiners.build_report(),
        carrier_certificate=intertwiners.exact_carrier_certificate(),
        constraint_certificate=_constraint_certificate(),
        matrices=_basis_data()[0],
    )


def render_markdown(report: dict[str, Any]) -> str:
    basis = report["quadratic_basis"]
    constraint = report["constraint_system"]
    return "\n".join(
        [
            "# Exact rank-one SU(4) Phi210 quadratic basis -- v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "## Exact construction",
            "",
            "- canonical live space: `Phi210 = Lambda^4(R^10)`;",
            "- Cartan weight-zero symmetric monomials: "
            f"`{constraint['Cartan_weight_zero_symmetric_monomial_count']}`;",
            "- remaining exact constraint rank/nullity: "
            f"`{constraint['exact_rational_rank']}/"
            f"{constraint['exact_rational_nullity']}`;",
            f"- explicit primitive integer matrices: `{basis['matrix_count']}` "
            "of shape `210 x 210`;",
            "- live invariance: every matrix commutes with all `15` exact "
            "Phi210 stabilizer generators;",
            "- exact independence: upper-triangle rank `45` modulo "
            f"`{basis['modular_prime']}`;",
            "- polynomial convention: diagonal `Q_ii`, off-diagonal "
            "`2 Q_ij`, with primitive coefficient rows exposed by the API;",
            "- completeness census: `(10+10+3+1)+(16+1+4)=45`;",
            f"- ordered basis SHA-256: `{basis['basis_sha256']}`;",
            f"- exact Gram SHA-256: `{basis['Gram_sha256']}`.",
            "",
            "## Scientific boundary",
            "",
            "- invariant quadratic basis: `CLOSED`;",
            "- full augmented Schur/SOS SDP: `OPEN`;",
            "- arbitrary-real-Phi lower bound: `OPEN`;",
            "- G3: `OPEN`;",
            "- whole theory: neither validated nor excluded by this result.",
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
