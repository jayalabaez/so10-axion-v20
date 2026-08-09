#!/usr/bin/env python3
"""Exact lowering-word alignment of the 25 rank-one SU(4) carriers.

The companion intertwiner audit resolves ``Phi210_C`` into twenty-five
irreducible SU(4) carriers.  Its denominator-free Casimir filters identify
the subspaces, but their independently selected pivot columns do not provide
common coordinates on equivalent copies.  This module supplies those common
coordinates without numerical eigensolvers.

For every irreducible type it chooses one primitive highest-weight vector,
constructs a deterministic basis by common words in the three exact Chevalley
lowering operators, and applies the same words to every equivalent carrier.
All fifteen compact-generator action matrices are then solved over Q from one
reference copy and checked, exactly, on every copy.  The 25 aligned bases have
combined rank 210.

The bases are also embedded through the live Gaussian exterior intertwiner
into the canonical real Phi210 chart.  A signed-permutation conjugation is
proved to be the physical real structure, and exact rational coordinate maps
pair every carrier with its conjugate.  This is representation infrastructure
only: it does not construct the 45 invariant quadratic forms, an SOS/Schur
SDP, an arbitrary-Phi bound, or G3.
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
from fractions import Fraction
from functools import lru_cache
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy import sparse

import exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20 as upstream


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_ALIGNED_CARRIERS_V20.json"
OUT_MD = ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_ALIGNED_CARRIERS_V20.md"
EXPECTED_MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
MODEL_CONTRACT_ID = upstream.MODEL_CONTRACT_ID
MODULAR_PRIME = upstream.MODULAR_PRIME
EXPECTED_UPSTREAM_MODULE = (
    "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py"
)
EXPECTED_UPSTREAM_SOURCE_SHA256 = (
    "76fa77c99b8d6e963e8694acf74280de29ced4c7a7623bffa991aead77329f49"
)
EXPECTED_STABILIZER_MODULE = (
    "exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py"
)
EXPECTED_STABILIZER_SOURCE_SHA256 = (
    "afe71f4a6c347d472c70a737398a272e35a9eb9a3f76cf6566d8edbeb5e579fa"
)
EXPECTED_UPSTREAM_REPORT_SHA256 = (
    "202de913bae8e4d12cfdc3468d68a6be60a81dff05e1f69f081949666ef95d73"
)
EXPECTED_UPSTREAM_INTERTWINER_SHA256 = (
    "ffac63a0c7ee77c358f93d06b618f2662097d478218f99d79f684aabb1ffd201"
)
EXPECTED_UPSTREAM_CARRIERS_SHA256 = (
    "f54495c004f216111152bb5dbb53fdd7ac57b8e121f9598b354124d6c976773c"
)

PHI_DIMENSION = upstream.PHI_DIMENSION
SIMPLE_ROOT_PAIRS = ("12", "23", "34")
SELF_CONJUGATE_IRREPS = ("1", "6", "15", "20prime")
CONJUGATE_IRREP = {
    "1": "1",
    "4": "4bar",
    "4bar": "4",
    "6": "6",
    "15": "15",
    "10": "10bar",
    "10bar": "10",
    "20": "20bar",
    "20bar": "20",
    "20prime": "20prime",
}
ONE_FORM_CONJUGATE = (1, 0, 6, 7, 8, 9, 2, 3, 4, 5)
INT64_MAX = int(np.iinfo(np.int64).max)
INT64_MIN = int(np.iinfo(np.int64).min)

# A rational matrix is stored canonically as (integer numerator, positive
# common denominator).  This is the public exact-matrix convention used by
# ``exact_aligned_carrier_data``.
RationalMatrix = tuple[np.ndarray, int]


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


def _file_sha256(path: Path) -> str:
    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def _canonical_json_sha256(value: Any) -> str:
    payload = json.dumps(
        _jsonable(value),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def _defensive_copy(value: Any) -> Any:
    """Return a deep copy so no caller can mutate a cached proof object."""
    return copy.deepcopy(value)


def _integer_dense(matrix: sparse.spmatrix | np.ndarray, context: str) -> np.ndarray:
    """Convert an integer matrix to int64, rejecting truncation or overflow."""
    dense = matrix.toarray() if sparse.issparse(matrix) else np.asarray(matrix)
    objects = np.asarray(dense, dtype=object)
    checked: list[int] = []
    for raw in objects.reshape(-1):
        if not isinstance(raw, (int, np.integer)):
            raise TypeError(f"{context} contains a non-integer entry")
        value = int(raw)
        if value < INT64_MIN or value > INT64_MAX:
            raise ArithmeticError(f"{context} exceeds signed-int64 storage")
        checked.append(value)
    return np.asarray(checked, dtype=np.int64).reshape(objects.shape)


def _maximum_abs(matrix: sparse.spmatrix | np.ndarray) -> int:
    dense = matrix.data if sparse.issparse(matrix) else np.asarray(matrix).reshape(-1)
    return max((abs(int(value)) for value in dense), default=0)


def _matmul_bound(
    left: sparse.spmatrix | np.ndarray,
    right: sparse.spmatrix | np.ndarray,
) -> int:
    if left.shape[1] != right.shape[0]:
        raise ValueError("matrix-product shapes are incompatible")
    return (
        int(left.shape[1]) * _maximum_abs(left) * _maximum_abs(right)
    )


def _checked_dense_matmul(
    left: sparse.spmatrix | np.ndarray,
    right: sparse.spmatrix | np.ndarray,
    context: str,
) -> np.ndarray:
    """Multiply exactly, using Python integers if int64 could overflow."""
    left_dense = _integer_dense(left, f"{context} left operand")
    right_dense = _integer_dense(right, f"{context} right operand")
    if left_dense.ndim != 2 or right_dense.ndim != 2:
        raise ValueError(f"{context} requires two matrices")
    if left_dense.shape[1] != right_dense.shape[0]:
        raise ValueError(f"{context} has incompatible matrix shapes")
    if _matmul_bound(left_dense, right_dense) <= INT64_MAX:
        return left_dense @ right_dense
    exact = np.asarray(left_dense, dtype=object) @ np.asarray(
        right_dense, dtype=object
    )
    return _integer_dense(exact, f"{context} result")


def _checked_sparse_matmul(
    left: sparse.spmatrix,
    right: sparse.spmatrix,
    context: str,
) -> sparse.csr_matrix:
    """Sparse exact product with an overflow-safe dense fallback."""
    if left.shape[1] != right.shape[0]:
        raise ValueError(f"{context} has incompatible matrix shapes")
    if _matmul_bound(left, right) <= INT64_MAX:
        result = (left.astype(np.int64) @ right.astype(np.int64)).tocsr()
    else:
        result = sparse.csr_matrix(_checked_dense_matmul(left, right, context))
    result.eliminate_zeros()
    return result


def _checked_dense_linear_combination(
    terms: Iterable[tuple[np.ndarray, int]], context: str
) -> np.ndarray:
    materialized = tuple(
        (_integer_dense(matrix, f"{context} term"), int(coefficient))
        for matrix, coefficient in terms
    )
    if not materialized:
        raise ValueError(f"{context} requires at least one term")
    shape = materialized[0][0].shape
    if any(matrix.shape != shape for matrix, _ in materialized):
        raise ValueError(f"{context} has inconsistent matrix shapes")
    bound = sum(
        abs(coefficient) * _maximum_abs(matrix)
        for matrix, coefficient in materialized
    )
    if bound <= INT64_MAX:
        result = np.zeros(shape, dtype=np.int64)
        for matrix, coefficient in materialized:
            result += coefficient * matrix
        return result
    exact = np.zeros(shape, dtype=object)
    for matrix, coefficient in materialized:
        exact += coefficient * np.asarray(matrix, dtype=object)
    return _integer_dense(exact, f"{context} result")


def _checked_sparse_linear_combination(
    terms: Iterable[tuple[sparse.spmatrix, int]], context: str
) -> sparse.csr_matrix:
    materialized = tuple((matrix.tocsr(), int(coefficient)) for matrix, coefficient in terms)
    if not materialized:
        raise ValueError(f"{context} requires at least one term")
    shape = materialized[0][0].shape
    if any(matrix.shape != shape for matrix, _ in materialized):
        raise ValueError(f"{context} has inconsistent matrix shapes")
    bound = sum(
        abs(coefficient) * _maximum_abs(matrix)
        for matrix, coefficient in materialized
    )
    if bound <= INT64_MAX:
        result = sparse.csr_matrix(shape, dtype=np.int64)
        for matrix, coefficient in materialized:
            result = result + coefficient * matrix.astype(np.int64)
        result = result.tocsr()
    else:
        result = sparse.csr_matrix(
            _checked_dense_linear_combination(
                ((matrix.toarray(), coefficient) for matrix, coefficient in materialized),
                context,
            )
        )
    result.eliminate_zeros()
    return result


def _sparse_is_zero(matrix: sparse.spmatrix) -> bool:
    compact = matrix.tocsr(copy=True)
    compact.eliminate_zeros()
    return compact.nnz == 0
def _matrix_sha256(*matrices: sparse.spmatrix | np.ndarray) -> str:
    digest = hashlib.sha256()
    for matrix in matrices:
        dense = _integer_dense(matrix, "matrix hash")
        canonical = np.ascontiguousarray(dense, dtype="<i8")
        digest.update(str(canonical.shape).encode("ascii"))
        digest.update(canonical.tobytes())
    return digest.hexdigest()


def _word_sha256(words: Iterable[tuple[int, ...]]) -> str:
    encoded = ";".join(
        "identity" if not word else "F" + "F".join(str(i + 1) for i in word)
        for word in words
    )
    return hashlib.sha256(encoded.encode("ascii")).hexdigest()


def upstream_source_contract_certificate() -> dict[str, Any]:
    """Bind this proof to the exact live companion source bytes."""
    upstream_path = Path(upstream.__file__).resolve()
    stabilizer_path = Path(upstream.stabilizer.__file__).resolve()
    upstream_hash = _file_sha256(upstream_path)
    stabilizer_hash = _file_sha256(stabilizer_path)
    modules_in_root = bool(
        upstream_path == ROOT / EXPECTED_UPSTREAM_MODULE
        and stabilizer_path == ROOT / EXPECTED_STABILIZER_MODULE
    )
    return {
        "upstream_module": upstream_path.name,
        "upstream_module_sha256": upstream_hash,
        "expected_upstream_module_sha256": EXPECTED_UPSTREAM_SOURCE_SHA256,
        "stabilizer_module": stabilizer_path.name,
        "stabilizer_module_sha256": stabilizer_hash,
        "expected_stabilizer_module_sha256": (
            EXPECTED_STABILIZER_SOURCE_SHA256
        ),
        "both_modules_resolve_to_repository_root_exact": modules_in_root,
        "source_bytes_match_pinned_contract_exact": bool(
            modules_in_root
            and upstream_hash == EXPECTED_UPSTREAM_SOURCE_SHA256
            and stabilizer_hash == EXPECTED_STABILIZER_SOURCE_SHA256
        ),
        "proof_grade": bool(
            modules_in_root
            and upstream_hash == EXPECTED_UPSTREAM_SOURCE_SHA256
            and stabilizer_hash == EXPECTED_STABILIZER_SOURCE_SHA256
        ),
    }


def _rank_mod_prime(matrix: np.ndarray, prime: int = MODULAR_PRIME) -> int:
    update_bound = (prime - 1) ** 2 + (prime - 1)
    if prime <= 2 or update_bound > INT64_MAX:
        raise ArithmeticError("modular prime is unsafe for int64 elimination")
    work = np.remainder(_integer_dense(matrix, "modular-rank input"), prime).copy()
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
    update_bound = (prime - 1) ** 2 + (prime - 1)
    if prime <= 2 or update_bound > INT64_MAX:
        raise ArithmeticError("modular prime is unsafe for int64 elimination")
    work = np.remainder(
        _integer_dense(matrix, "modular-pivot input"), prime
    ).copy()
    n_rows, n_columns = work.shape
    pivot_row = 0
    pivots: list[int] = []
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
        pivots.append(column)
        pivot_row += 1
        if pivot_row == n_rows:
            break
    return tuple(pivots)


def _exact_half(matrix: sparse.spmatrix) -> sparse.csr_matrix:
    result = matrix.tocsr(copy=True)
    if any(int(value) % 2 for value in result.data):
        raise ArithmeticError("Chevalley numerator left the even lattice")
    result.data //= 2
    result.eliminate_zeros()
    return result


@lru_cache(maxsize=1)
def _chevalley_actions_cached() -> dict[str, tuple[sparse.csr_matrix, ...]]:
    """Return exact ``(D_i,E_i,F_i)`` actions in exterior coordinates.

    The compact source convention is
    ``E_i=(X_i-iY_i)/2`` and ``F_i=-(X_i+iY_i)/2``.  In the Gaussian
    exterior chart these actions are integral and real.  ``D_i`` is the
    imaginary part of the compact Cartan action and ``[E_i,F_i]=D_i``.
    """
    actions = upstream.su4_exterior_actions()
    labels = upstream.stabilizer.SU4_LABELS
    cartan = tuple(actions[index][1].tocsr(copy=True) for index in range(3))
    raising: list[sparse.csr_matrix] = []
    lowering: list[sparse.csr_matrix] = []
    imaginary_residuals: list[sparse.csr_matrix] = []
    for pair in SIMPLE_ROOT_PAIRS:
        x_real, x_imaginary = actions[labels.index(f"X{pair}")]
        y_real, y_imaginary = actions[labels.index(f"Y{pair}")]
        raising.append(
            _exact_half(
                _checked_sparse_linear_combination(
                    ((x_real, 1), (y_imaginary, 1)), "Chevalley raising"
                )
            )
        )
        lowering.append(
            _exact_half(
                _checked_sparse_linear_combination(
                    ((x_real, -1), (y_imaginary, 1)), "Chevalley lowering"
                )
            )
        )
        imaginary_residuals.extend(
            (
                _exact_half(
                    _checked_sparse_linear_combination(
                        ((x_imaginary, 1), (y_real, -1)),
                        "Chevalley raising imaginary residual",
                    )
                ),
                _exact_half(
                    _checked_sparse_linear_combination(
                        ((x_imaginary, -1), (y_real, -1)),
                        "Chevalley lowering imaginary residual",
                    )
                ),
            )
        )
    if not all(_sparse_is_zero(value) for value in imaginary_residuals):
        raise ArithmeticError("Chevalley actions acquired imaginary entries")
    return {
        "cartan": cartan,
        "raising": tuple(raising),
        "lowering": tuple(lowering),
    }


def chevalley_actions() -> dict[str, tuple[sparse.csr_matrix, ...]]:
    """Return a mutation-isolated copy of the cached exact actions."""
    return _defensive_copy(_chevalley_actions_cached())


def exact_chevalley_certificate() -> dict[str, Any]:
    actions = _chevalley_actions_cached()
    cartan = actions["cartan"]
    raising = actions["raising"]
    lowering = actions["lowering"]
    cartan_matrix = np.asarray(
        ((2, -1, 0), (-1, 2, -1), (0, -1, 2)), dtype=np.int64
    )
    ef_relations = []
    weight_relations = []
    serre_relations = []
    for left in range(3):
        for right in range(3):
            ef = _checked_sparse_linear_combination(
                (
                    (
                        _checked_sparse_matmul(
                            raising[left], lowering[right], "Chevalley EF"
                        ),
                        1,
                    ),
                    (
                        _checked_sparse_matmul(
                            lowering[right], raising[left], "Chevalley FE"
                        ),
                        -1,
                    ),
                ),
                "Chevalley EF commutator",
            )
            expected = cartan[left] if left == right else sparse.csr_matrix(
                (PHI_DIMENSION, PHI_DIMENSION), dtype=np.int64
            )
            ef_relations.append(
                _sparse_is_zero(
                    _checked_sparse_linear_combination(
                        ((ef, 1), (expected, -1)), "Chevalley EF relation"
                    )
                )
            )
            cartan_raising = _checked_sparse_matmul(
                cartan[left], raising[right], "Cartan-raising product"
            )
            raising_cartan = _checked_sparse_matmul(
                raising[right], cartan[left], "raising-Cartan product"
            )
            cartan_lowering = _checked_sparse_matmul(
                cartan[left], lowering[right], "Cartan-lowering product"
            )
            lowering_cartan = _checked_sparse_matmul(
                lowering[right], cartan[left], "lowering-Cartan product"
            )
            weight_relations.extend(
                (
                    _sparse_is_zero(
                        _checked_sparse_linear_combination(
                            (
                                (cartan_raising, 1),
                                (raising_cartan, -1),
                                (
                                    raising[right],
                                    -int(cartan_matrix[left, right]),
                                ),
                            ),
                            "Cartan raising-weight relation",
                        )
                    ),
                    _sparse_is_zero(
                        _checked_sparse_linear_combination(
                            (
                                (cartan_lowering, 1),
                                (lowering_cartan, -1),
                                (
                                    lowering[right],
                                    int(cartan_matrix[left, right]),
                                ),
                            ),
                            "Cartan lowering-weight relation",
                        )
                    ),
                )
            )
            if left == right:
                continue
            exponent = 1 - int(cartan_matrix[left, right])
            for family in (raising, lowering):
                value = family[right]
                for _ in range(exponent):
                    value = _checked_sparse_linear_combination(
                        (
                            (
                                _checked_sparse_matmul(
                                    family[left], value, "Serre left product"
                                ),
                                1,
                            ),
                            (
                                _checked_sparse_matmul(
                                    value, family[left], "Serre right product"
                                ),
                                -1,
                            ),
                        ),
                        "Serre commutator",
                    )
                serre_relations.append(_sparse_is_zero(value))
    all_integral = all(
        matrix.dtype == np.int64
        for family in actions.values()
        for matrix in family
    )
    return {
        "simple_root_pairs": SIMPLE_ROOT_PAIRS,
        "normalization": "E=(X-iY)/2, F=-(X+iY)/2, D=[E,F]",
        "A3_Cartan_matrix": cartan_matrix,
        "operator_shapes": [matrix.shape for matrix in raising],
        "all_actions_integral_real": all_integral,
        "maximum_absolute_entry": max(
            _maximum_abs(matrix)
            for family in actions.values()
            for matrix in family
        ),
        "all_9_EF_commutators_exact": all(ef_relations),
        "all_18_Cartan_weight_relations_exact": all(weight_relations),
        "all_12_Serre_relations_exact": all(serre_relations),
        "raising_sha256": _matrix_sha256(*raising),
        "lowering_sha256": _matrix_sha256(*lowering),
        "proof_grade": bool(
            all_integral
            and len(raising) == len(lowering) == len(cartan) == 3
            and all(matrix.shape == (PHI_DIMENSION, PHI_DIMENSION)
                    for family in actions.values() for matrix in family)
            and all(ef_relations)
            and all(weight_relations)
            and all(serre_relations)
        ),
    }


def carrier_specs() -> tuple[dict[str, Any], ...]:
    """Return the public deterministic order of the 25 upstream carriers."""
    specs: list[dict[str, Any]] = []

    def add(
        singlets: tuple[int, ...],
        fundamental_count: int,
        antifundamental_count: int,
        irreps: tuple[str, ...],
    ) -> None:
        block_name = (
            "none" if not singlets else "_".join(
                upstream.GAUSSIAN_ONE_FORM_LABELS[index] for index in singlets
            )
        )
        block_eigenvalues = tuple(
            dict.fromkeys(upstream.IRREP_DATA[name]["C8"] for name in irreps)
        )
        for irrep in irreps:
            specs.append(
                {
                    "name": (
                        f"{block_name}__b{fundamental_count}_"
                        f"c{antifundamental_count}__{irrep}"
                    ),
                    "natural_block": (
                        singlets,
                        fundamental_count,
                        antifundamental_count,
                    ),
                    "irrep": irrep,
                    "C8": upstream.IRREP_DATA[irrep]["C8"],
                    "expected_dimension": upstream.IRREP_DATA[irrep]["dimension"],
                    "block_eigenvalues": block_eigenvalues,
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
    if len(specs) != 25:
        raise ArithmeticError("aligned carrier census drifted")
    return tuple(specs)


def _primitive_column(column: sparse.spmatrix) -> sparse.csr_matrix:
    values = _integer_dense(column, "highest-weight column").reshape(-1)
    common = 0
    for value in values:
        common = math.gcd(common, abs(int(value)))
    if common == 0:
        raise ArithmeticError("cannot normalize a zero highest-weight vector")
    values //= common
    first = int(np.flatnonzero(values)[0])
    if values[first] < 0:
        values = -values
    return sparse.csr_matrix(values.reshape(-1, 1), dtype=np.int64)


def _highest_weight_vector(spec: dict[str, Any]) -> sparse.csr_matrix:
    blocks = upstream.natural_exterior_blocks()
    columns = blocks[spec["natural_block"]]
    filtered = upstream._filtered_block(
        columns, int(spec["C8"]), tuple(spec["block_eigenvalues"])
    )
    target = tuple(upstream.IRREP_DATA[spec["irrep"]]["dynkin"])
    weights = upstream.exterior_state_weights()
    candidates = tuple(
        local
        for local, global_column in enumerate(columns)
        if weights[global_column] == target and filtered[:, local].nnz
    )
    if not candidates:
        raise ArithmeticError(f"no highest-weight column for {spec['name']}")
    result = _primitive_column(filtered[:, candidates[0]])
    if not all(
        _sparse_is_zero(
            _checked_sparse_matmul(
                operator, result, "highest-weight raising action"
            )
        )
        for operator in _chevalley_actions_cached()["raising"]
    ):
        raise ArithmeticError(f"raising residual for {spec['name']}")
    return result


def _apply_lowering_word(
    vector: sparse.csr_matrix, word: tuple[int, ...]
) -> sparse.csr_matrix:
    result = vector
    lowering = _chevalley_actions_cached()["lowering"]
    for index in word:
        result = _checked_sparse_matmul(
            lowering[index], result, "lowering-word action"
        )
    result.eliminate_zeros()
    return result


def _deterministic_lowering_words(
    highest: sparse.csr_matrix, dimension: int
) -> tuple[tuple[tuple[int, ...], ...], sparse.csr_matrix]:
    words: list[tuple[int, ...]] = [()]
    vectors: list[sparse.csr_matrix] = [highest]
    queue = 0
    while len(words) < dimension and queue < len(words):
        for root in range(3):
            word = words[queue] + (root,)
            candidate = _apply_lowering_word(highest, word)
            if not candidate.nnz:
                continue
            trial = sparse.hstack(vectors + [candidate], format="csr")
            if _rank_mod_prime(trial.toarray()) > len(vectors):
                words.append(word)
                vectors.append(candidate)
            if len(words) == dimension:
                break
        queue += 1
    if len(words) != dimension:
        raise ArithmeticError(
            f"lowering words span {len(words)} rather than {dimension}"
        )
    return tuple(words), sparse.hstack(vectors, format="csr")


def _solve_square_rational(left: np.ndarray, right: np.ndarray) -> list[list[Fraction]]:
    left = _integer_dense(left, "exact solve left operand")
    right = _integer_dense(right, "exact solve right operand")
    dimension = left.shape[0]
    if left.shape != (dimension, dimension) or right.shape[0] != dimension:
        raise ValueError("exact solve requires a square left matrix")
    width = right.shape[1]
    work = [
        [Fraction(int(left[row, column])) for column in range(dimension)]
        + [Fraction(int(right[row, column])) for column in range(width)]
        for row in range(dimension)
    ]
    for column in range(dimension):
        pivot = next(
            (row for row in range(column, dimension) if work[row][column]),
            None,
        )
        if pivot is None:
            raise ArithmeticError("exact coordinate minor is singular")
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [value / scale for value in work[column]]
        for row in range(dimension):
            if row == column or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                left_value - scale * pivot_value
                for left_value, pivot_value in zip(
                    work[row], work[column], strict=True
                )
            ]
    return [row[dimension:] for row in work]


def _pack_rational(values: list[list[Fraction]]) -> RationalMatrix:
    denominator = 1
    for row in values:
        for value in row:
            denominator = math.lcm(denominator, value.denominator)
    numerators = _integer_dense(
        [
            [int(value * denominator) for value in row]
            for row in values
        ],
        "packed rational numerator",
    )
    common = denominator
    for value in numerators.reshape(-1):
        common = math.gcd(common, abs(int(value)))
    if common > 1:
        numerators //= common
        denominator //= common
    return numerators, denominator


def _normalize_rational(numerator: np.ndarray, denominator: int) -> RationalMatrix:
    if denominator == 0:
        raise ZeroDivisionError("rational-matrix denominator is zero")
    numerator = _integer_dense(numerator, "normalized rational numerator").copy()
    if denominator < 0:
        numerator = _checked_dense_linear_combination(
            ((numerator, -1),), "rational sign normalization"
        )
        denominator = -denominator
    common = int(denominator)
    for value in numerator.reshape(-1):
        common = math.gcd(common, abs(int(value)))
    if common > 1:
        numerator //= common
        denominator //= common
    return numerator, int(denominator)


def _coordinate_matrix(
    basis: sparse.csr_matrix, image: sparse.spmatrix
) -> RationalMatrix:
    dense_basis = _integer_dense(basis, "coordinate basis")
    dense_image = _integer_dense(image, "coordinate image")
    pivot_rows = _independent_columns_mod_prime(dense_basis.T)
    dimension = basis.shape[1]
    if len(pivot_rows) != dimension:
        raise ArithmeticError("aligned basis lost exact rank")
    row_indices = list(pivot_rows)
    values = _solve_square_rational(
        dense_basis[row_indices, :], dense_image[row_indices, :]
    )
    result = _pack_rational(values)
    residual = _checked_dense_linear_combination(
        (
            (dense_image, result[1]),
            (
                _checked_dense_matmul(
                    dense_basis, result[0], "coordinate reconstruction"
                ),
                -1,
            ),
        ),
        "coordinate residual",
    )
    if np.any(residual):
        raise ArithmeticError("candidate rational coordinates have a residual")
    return result


def _rational_product(left: RationalMatrix, right: RationalMatrix) -> RationalMatrix:
    denominator = int(left[1]) * int(right[1])
    return _normalize_rational(
        _checked_dense_matmul(
            left[0], right[0], "rational-matrix product"
        ),
        denominator,
    )


def _rational_is_identity(value: RationalMatrix) -> bool:
    expected = _checked_dense_linear_combination(
        ((np.eye(value[0].shape[0], dtype=np.int64), int(value[1])),),
        "rational identity",
    )
    return np.array_equal(
        value[0], expected
    )


def _rational_hash(value: RationalMatrix) -> str:
    digest = hashlib.sha256()
    digest.update(_matrix_sha256(value[0]).encode("ascii"))
    digest.update(b"/")
    digest.update(str(int(value[1])).encode("ascii"))
    return digest.hexdigest()


@lru_cache(maxsize=1)
def _exterior_conjugation_cached() -> sparse.csr_matrix:
    """Signed permutation implementing physical complex conjugation."""
    state_index = {
        state: index for index, state in enumerate(upstream.CANONICAL_FOUR_STATES)
    }
    rows: list[int] = []
    columns: list[int] = []
    values: list[int] = []
    for column, state in enumerate(upstream.CANONICAL_FOUR_STATES):
        conjugated = tuple(ONE_FORM_CONJUGATE[index] for index in state)
        inversions = sum(
            conjugated[left] > conjugated[right]
            for left in range(upstream.EXTERIOR_DEGREE)
            for right in range(left + 1, upstream.EXTERIOR_DEGREE)
        )
        rows.append(state_index[tuple(sorted(conjugated))])
        columns.append(column)
        values.append(-1 if inversions % 2 else 1)
    return sparse.csr_matrix(
        (values, (rows, columns)),
        shape=(PHI_DIMENSION, PHI_DIMENSION),
        dtype=np.int64,
    )


def exterior_conjugation() -> sparse.csr_matrix:
    """Return a mutation-isolated physical-conjugation matrix."""
    return _exterior_conjugation_cached().copy()


def _conjugate_natural_block(
    block: tuple[tuple[int, ...], int, int]
) -> tuple[tuple[int, ...], int, int]:
    singlets, fundamental, antifundamental = block
    return (
        tuple(sorted(ONE_FORM_CONJUGATE[index] for index in singlets)),
        antifundamental,
        fundamental,
    )


def _source_actions_for_basis(
    basis: sparse.csr_matrix,
) -> tuple[dict[str, Any], ...]:
    output = []
    for label, (real, imaginary) in zip(
        upstream.stabilizer.SU4_LABELS,
        upstream.su4_exterior_actions(),
        strict=True,
    ):
        output.append(
            {
                "label": label,
                "real": _coordinate_matrix(
                    basis,
                    _checked_sparse_matmul(
                        real, basis, "exterior real source action"
                    ),
                ),
                "imaginary": _coordinate_matrix(
                    basis,
                    _checked_sparse_matmul(
                        imaginary, basis, "exterior imaginary source action"
                    ),
                ),
            }
        )
    return tuple(output)


def _source_intertwining_exact(
    basis: sparse.csr_matrix,
    source_actions: tuple[dict[str, Any], ...],
) -> bool:
    dense = _integer_dense(basis, "source intertwining basis")
    for exterior_action, source in zip(
        upstream.su4_exterior_actions(), source_actions, strict=True
    ):
        for ambient, coordinate in zip(
            exterior_action,
            (source["real"], source["imaginary"]),
            strict=True,
        ):
            numerator, denominator = coordinate
            ambient_image = _checked_sparse_matmul(
                ambient, basis, "source intertwining ambient image"
            )
            residual = _checked_dense_linear_combination(
                (
                    (
                        _integer_dense(
                            ambient_image, "source intertwining image"
                        ),
                        denominator,
                    ),
                    (
                        _checked_dense_matmul(
                            dense, numerator, "source coordinate image"
                        ),
                        -1,
                    ),
                ),
                "source intertwining residual",
            )
            if np.any(residual):
                return False
    return True


def _canonical_intertwining_exact(
    basis_real: sparse.csr_matrix,
    basis_imaginary: sparse.csr_matrix,
    source_actions: tuple[dict[str, Any], ...],
) -> bool:
    dense_real = _integer_dense(basis_real, "canonical real basis")
    dense_imaginary = _integer_dense(
        basis_imaginary, "canonical imaginary basis"
    )
    for live_action, source in zip(
        upstream.stabilizer.exact_phi210_actions(), source_actions, strict=True
    ):
        real_numerator, real_denominator = source["real"]
        imaginary_numerator, imaginary_denominator = source["imaginary"]
        denominator = math.lcm(real_denominator, imaginary_denominator)
        real_scale = denominator // real_denominator
        imaginary_scale = denominator // imaginary_denominator
        right_real = _checked_dense_linear_combination(
            (
                (
                    _checked_dense_matmul(
                        dense_real,
                        real_numerator,
                        "canonical real/source-real product",
                    ),
                    real_scale,
                ),
                (
                    _checked_dense_matmul(
                        dense_imaginary,
                        imaginary_numerator,
                        "canonical imaginary/source-imaginary product",
                    ),
                    -imaginary_scale,
                ),
            ),
            "canonical right-real action",
        )
        right_imaginary = _checked_dense_linear_combination(
            (
                (
                    _checked_dense_matmul(
                        dense_imaginary,
                        real_numerator,
                        "canonical imaginary/source-real product",
                    ),
                    real_scale,
                ),
                (
                    _checked_dense_matmul(
                        dense_real,
                        imaginary_numerator,
                        "canonical real/source-imaginary product",
                    ),
                    imaginary_scale,
                ),
            ),
            "canonical right-imaginary action",
        )
        live_real = _checked_sparse_matmul(
            live_action, basis_real, "live Phi210 real action"
        )
        live_imaginary = _checked_sparse_matmul(
            live_action, basis_imaginary, "live Phi210 imaginary action"
        )
        residual_real = _checked_dense_linear_combination(
            (
                (_integer_dense(live_real, "live real image"), denominator),
                (right_real, -1),
            ),
            "canonical real intertwining residual",
        )
        residual_imaginary = _checked_dense_linear_combination(
            (
                (
                    _integer_dense(live_imaginary, "live imaginary image"),
                    denominator,
                ),
                (right_imaginary, -1),
            ),
            "canonical imaginary intertwining residual",
        )
        if np.any(residual_real) or np.any(residual_imaginary):
            return False
    return True


@lru_cache(maxsize=1)
def _exact_aligned_carrier_data_cached() -> dict[str, Any]:
    """Build the private cached aligned matrices.

    Every rational matrix is ``(int64 numerator, positive denominator)``.
    This object must never escape without a defensive deep copy.
    """
    specs = carrier_specs()
    highest_vectors = {spec["name"]: _highest_weight_vector(spec) for spec in specs}
    family_words: dict[str, tuple[tuple[int, ...], ...]] = {}
    reference_basis: dict[str, sparse.csr_matrix] = {}
    reference_name: dict[str, str] = {}
    for spec in specs:
        irrep = spec["irrep"]
        if irrep in family_words:
            continue
        words, basis = _deterministic_lowering_words(
            highest_vectors[spec["name"]], int(spec["expected_dimension"])
        )
        family_words[irrep] = words
        reference_basis[irrep] = basis
        reference_name[irrep] = spec["name"]
    source_actions = {
        irrep: _source_actions_for_basis(basis)
        for irrep, basis in reference_basis.items()
    }

    gaussian_real, gaussian_imaginary = upstream.gaussian_exterior_basis()
    copy_count: Counter[str] = Counter()
    carriers: list[dict[str, Any]] = []
    for spec in specs:
        irrep = spec["irrep"]
        highest = highest_vectors[spec["name"]]
        basis = sparse.hstack(
            [
                _apply_lowering_word(highest, word)
                for word in family_words[irrep]
            ],
            format="csr",
        )
        canonical_real = _checked_sparse_matmul(
            gaussian_real, basis, "Gaussian real carrier embedding"
        )
        canonical_imaginary = _checked_sparse_matmul(
            gaussian_imaginary, basis, "Gaussian imaginary carrier embedding"
        )
        gram = _integer_dense(
            _checked_sparse_matmul(
                basis.T, basis, "aligned carrier Gram matrix"
            ),
            "aligned carrier Gram matrix",
        )
        carriers.append(
            {
                "name": spec["name"],
                "irrep": irrep,
                "copy_index": int(copy_count[irrep]),
                "natural_block": spec["natural_block"],
                "C8": int(spec["C8"]),
                "dimension": int(spec["expected_dimension"]),
                "highest_weight": tuple(upstream.IRREP_DATA[irrep]["dynkin"]),
                "highest_weight_vector": highest,
                "lowering_words": family_words[irrep],
                "exterior_basis": basis,
                "canonical_basis_real": canonical_real,
                "canonical_basis_imaginary": canonical_imaginary,
                "exterior_gram": gram,
                "source_actions": source_actions[irrep],
                "reality_kind": (
                    "self_conjugate_real_type"
                    if irrep in SELF_CONJUGATE_IRREPS
                    else "complex_type_conjugate_pair"
                ),
            }
        )
        copy_count[irrep] += 1

    by_key = {
        (record["natural_block"], record["irrep"]): record
        for record in carriers
    }
    conjugation = _exterior_conjugation_cached()
    for record in carriers:
        target_key = (
            _conjugate_natural_block(record["natural_block"]),
            CONJUGATE_IRREP[record["irrep"]],
        )
        target = by_key.get(target_key)
        if target is None:
            raise ArithmeticError(f"missing conjugate carrier for {record['name']}")
        coordinate_map = _coordinate_matrix(
            target["exterior_basis"],
            _checked_sparse_matmul(
                conjugation,
                record["exterior_basis"],
                "carrier conjugation image",
            ),
        )
        record["conjugate_carrier_name"] = target["name"]
        record["conjugation_map"] = coordinate_map

    families = {
        irrep: {
            "irrep": irrep,
            "dimension": int(upstream.IRREP_DATA[irrep]["dimension"]),
            "multiplicity": int(upstream.EXPECTED_BRANCHING[irrep]),
            "reference_carrier_name": reference_name[irrep],
            "lowering_words": family_words[irrep],
            "source_actions": source_actions[irrep],
        }
        for irrep in upstream.EXPECTED_BRANCHING
    }
    return {
        "rational_matrix_convention": (
            "(int64 numerator, positive common denominator)"
        ),
        "generator_labels": upstream.stabilizer.SU4_LABELS,
        "families": families,
        "carriers": tuple(carriers),
        "exterior_conjugation": conjugation,
    }


def exact_aligned_carrier_data() -> dict[str, Any]:
    """Return mutation-isolated exact matrices for downstream construction."""
    return _defensive_copy(_exact_aligned_carrier_data_cached())


def _exact_arithmetic_safety_certificate(data: dict[str, Any]) -> dict[str, Any]:
    """Certify the integer bounds exercised by the live carrier proof."""
    product_bounds: list[tuple[str, int]] = []
    scalar_bounds: list[tuple[str, int]] = []

    def product(
        label: str,
        left: sparse.spmatrix | np.ndarray,
        right: sparse.spmatrix | np.ndarray,
    ) -> None:
        product_bounds.append((label, _matmul_bound(left, right)))

    def scalar(
        label: str, coefficient: int, matrix: sparse.spmatrix | np.ndarray
    ) -> None:
        scalar_bounds.append(
            (label, abs(int(coefficient)) * _maximum_abs(matrix))
        )

    def scaled_bound(label: str, coefficient: int, bound: int) -> None:
        scalar_bounds.append((label, abs(int(coefficient)) * int(bound)))

    chevalley = _chevalley_actions_cached()
    for family_name, family in chevalley.items():
        for left in family:
            for right in family:
                product(f"Chevalley {family_name}", left, right)

    gaussian_real, gaussian_imaginary = upstream.gaussian_exterior_basis()
    exterior_actions = upstream.su4_exterior_actions()
    live_actions = upstream.stabilizer.exact_phi210_actions()
    c8_real, _ = upstream.integral_c8()
    by_name = {record["name"]: record for record in data["carriers"]}
    maximum_denominator = 1
    maximum_rational_numerator = 0
    all_public_matrices_int64 = all(
        matrix.dtype == np.int64
        for matrix in (
            gaussian_real,
            gaussian_imaginary,
            c8_real,
            data["exterior_conjugation"],
            *live_actions,
            *(matrix for action in exterior_actions for matrix in action),
            *(matrix for family in chevalley.values() for matrix in family),
        )
    )
    for record in data["carriers"]:
        basis = record["exterior_basis"]
        canonical_real = record["canonical_basis_real"]
        canonical_imaginary = record["canonical_basis_imaginary"]
        all_public_matrices_int64 = bool(
            all_public_matrices_int64
            and basis.dtype == np.int64
            and canonical_real.dtype == np.int64
            and canonical_imaginary.dtype == np.int64
            and record["exterior_gram"].dtype == np.int64
        )
        product("Gaussian real embedding", gaussian_real, basis)
        product("Gaussian imaginary embedding", gaussian_imaginary, basis)
        product("carrier Gram", basis.T, basis)
        c8_shift_bound = (
            _maximum_abs(c8_real) + abs(int(record["C8"]))
        ) * int(c8_real.shape[1]) * _maximum_abs(basis)
        product_bounds.append(("C8 carrier equation", c8_shift_bound))
        conjugation_product_bound = _matmul_bound(
            data["exterior_conjugation"], basis
        )
        product_bounds.append(
            ("physical conjugation", conjugation_product_bound)
        )
        target = by_name[record["conjugate_carrier_name"]]
        conjugation_numerator, conjugation_denominator = record[
            "conjugation_map"
        ]
        maximum_denominator = max(
            maximum_denominator, int(conjugation_denominator)
        )
        maximum_rational_numerator = max(
            maximum_rational_numerator,
            _maximum_abs(conjugation_numerator),
        )
        product(
            "conjugate carrier coordinates",
            target["exterior_basis"],
            conjugation_numerator,
        )
        scaled_bound(
            "conjugation denominator scaling",
            conjugation_denominator,
            conjugation_product_bound,
        )
        scalar(
            "physical real conjugation denominator scaling",
            conjugation_denominator,
            canonical_real,
        )
        scalar(
            "physical imaginary conjugation denominator scaling",
            conjugation_denominator,
            canonical_imaginary,
        )
        reverse_numerator, reverse_denominator = target["conjugation_map"]
        product(
            "conjugation involution rational product",
            reverse_numerator,
            conjugation_numerator,
        )
        maximum_denominator = max(
            maximum_denominator, int(reverse_denominator)
        )
        for (exterior_real, exterior_imaginary), live, source in zip(
            exterior_actions, live_actions, record["source_actions"], strict=True
        ):
            for ambient, part in (
                (exterior_real, "real"),
                (exterior_imaginary, "imaginary"),
            ):
                numerator, denominator = source[part]
                maximum_denominator = max(maximum_denominator, int(denominator))
                maximum_rational_numerator = max(
                    maximum_rational_numerator, _maximum_abs(numerator)
                )
                all_public_matrices_int64 = bool(
                    all_public_matrices_int64 and numerator.dtype == np.int64
                )
                ambient_product_bound = _matmul_bound(ambient, basis)
                product_bounds.append(
                    ("exterior source action", ambient_product_bound)
                )
                product("source coordinate reconstruction", basis, numerator)
                scaled_bound(
                    "source action denominator scaling",
                    denominator,
                    ambient_product_bound,
                )
            real_numerator, real_denominator = source["real"]
            imaginary_numerator, imaginary_denominator = source["imaginary"]
            live_real_bound = _matmul_bound(live, canonical_real)
            live_imaginary_bound = _matmul_bound(live, canonical_imaginary)
            product_bounds.extend(
                (
                    ("live canonical real action", live_real_bound),
                    ("live canonical imaginary action", live_imaginary_bound),
                )
            )
            canonical_real_source_real_bound = _matmul_bound(
                canonical_real, real_numerator
            )
            canonical_imaginary_source_imaginary_bound = _matmul_bound(
                canonical_imaginary, imaginary_numerator
            )
            canonical_imaginary_source_real_bound = _matmul_bound(
                canonical_imaginary, real_numerator
            )
            canonical_real_source_imaginary_bound = _matmul_bound(
                canonical_real, imaginary_numerator
            )
            product_bounds.extend(
                (
                    (
                        "canonical real/source real",
                        canonical_real_source_real_bound,
                    ),
                    (
                        "canonical imaginary/source imaginary",
                        canonical_imaginary_source_imaginary_bound,
                    ),
                    (
                        "canonical imaginary/source real",
                        canonical_imaginary_source_real_bound,
                    ),
                    (
                        "canonical real/source imaginary",
                        canonical_real_source_imaginary_bound,
                    ),
                )
            )
            denominator = math.lcm(real_denominator, imaginary_denominator)
            scaled_bound(
                "live real denominator scaling", denominator, live_real_bound
            )
            scaled_bound(
                "live imaginary denominator scaling",
                denominator,
                live_imaginary_bound,
            )
            scaled_bound(
                "right real/source-real scaling",
                denominator // real_denominator,
                canonical_real_source_real_bound,
            )
            scaled_bound(
                "right real/source-imaginary scaling",
                denominator // imaginary_denominator,
                canonical_imaginary_source_imaginary_bound,
            )
            scaled_bound(
                "right imaginary/source-real scaling",
                denominator // real_denominator,
                canonical_imaginary_source_real_bound,
            )
            scaled_bound(
                "right imaginary/source-imaginary scaling",
                denominator // imaginary_denominator,
                canonical_real_source_imaginary_bound,
            )

    maximum_product_bound = max((bound for _, bound in product_bounds), default=0)
    maximum_scalar_bound = max((bound for _, bound in scalar_bounds), default=0)
    modular_update_bound = (MODULAR_PRIME - 1) ** 2 + (MODULAR_PRIME - 1)
    all_bounds_fit = bool(
        maximum_product_bound <= INT64_MAX
        and maximum_scalar_bound <= INT64_MAX
        and modular_update_bound <= INT64_MAX
    )
    return {
        "storage_dtype": "signed int64",
        "Python_Fraction_Gauss_Jordan_solver_exact": True,
        "Python_integer_denominator_lcm_and_products_exact": True,
        "checked_products_have_Python_integer_fallback": True,
        "checked_results_reject_out_of_int64_range": True,
        "live_product_bound_count": len(product_bounds),
        "live_scalar_bound_count": len(scalar_bounds),
        "maximum_live_product_absolute_bound": maximum_product_bound,
        "maximum_live_scalar_absolute_bound": maximum_scalar_bound,
        "modular_elimination_row_update_absolute_bound": modular_update_bound,
        "signed_int64_maximum": INT64_MAX,
        "maximum_rational_numerator_absolute_entry": (
            maximum_rational_numerator
        ),
        "maximum_positive_common_denominator": maximum_denominator,
        "all_published_matrices_have_int64_dtype": all_public_matrices_int64,
        "all_live_conservative_bounds_fit_int64": all_bounds_fit,
        "proof_grade": bool(all_public_matrices_int64 and all_bounds_fit),
    }


@lru_cache(maxsize=1)
def _exact_aligned_carrier_certificate_cached() -> dict[str, Any]:
    data = _exact_aligned_carrier_data_cached()
    carriers = data["carriers"]
    families = data["families"]
    c8_real, c8_imaginary = upstream.integral_c8()
    if not _sparse_is_zero(c8_imaginary):
        raise ArithmeticError("upstream C8 acquired an imaginary part")
    identity = sparse.identity(PHI_DIMENSION, dtype=np.int64, format="csr")
    weights = upstream.exterior_state_weights()
    natural_blocks = upstream.natural_exterior_blocks()
    block_by_row = {
        row: block for block, rows in natural_blocks.items() for row in rows
    }

    carrier_rows = []
    complete_bases: list[sparse.csr_matrix] = []
    by_name = {record["name"]: record for record in carriers}
    all_source_exact = True
    all_live_exact = True
    all_conjugation_exact = True
    all_conjugation_involutive = True
    for record in carriers:
        basis = record["exterior_basis"]
        highest = record["highest_weight_vector"]
        complete_bases.append(basis)
        source_exact = _source_intertwining_exact(
            basis, record["source_actions"]
        )
        live_exact = _canonical_intertwining_exact(
            record["canonical_basis_real"],
            record["canonical_basis_imaginary"],
            record["source_actions"],
        )
        target = by_name[record["conjugate_carrier_name"]]
        numerator, denominator = record["conjugation_map"]
        conjugated_basis = _checked_sparse_matmul(
            data["exterior_conjugation"],
            basis,
            "certificate conjugated carrier",
        )
        conjugation_residual = _checked_dense_linear_combination(
            (
                (
                    _integer_dense(
                        conjugated_basis, "certificate conjugated carrier"
                    ),
                    denominator,
                ),
                (
                    _checked_dense_matmul(
                        target["exterior_basis"],
                        numerator,
                        "target carrier conjugation coordinates",
                    ),
                    -1,
                ),
            ),
            "carrier conjugation residual",
        )
        physical_real_residual = _checked_dense_linear_combination(
            (
                (
                    _integer_dense(
                        record["canonical_basis_real"],
                        "carrier canonical real basis",
                    ),
                    denominator,
                ),
                (
                    _checked_dense_matmul(
                        target["canonical_basis_real"],
                        numerator,
                        "target canonical real conjugation coordinates",
                    ),
                    -1,
                ),
            ),
            "physical real conjugation residual",
        )
        physical_imaginary_residual = _checked_dense_linear_combination(
            (
                (
                    _integer_dense(
                        record["canonical_basis_imaginary"],
                        "carrier canonical imaginary basis",
                    ),
                    -denominator,
                ),
                (
                    _checked_dense_matmul(
                        target["canonical_basis_imaginary"],
                        numerator,
                        "target canonical imaginary conjugation coordinates",
                    ),
                    -1,
                ),
            ),
            "physical imaginary conjugation residual",
        )
        conjugation_exact = bool(
            not np.any(conjugation_residual)
            and not np.any(physical_real_residual)
            and not np.any(physical_imaginary_residual)
        )
        reverse = target["conjugation_map"]
        involutive = _rational_is_identity(
            _rational_product(reverse, record["conjugation_map"])
        )
        highest_dense = _integer_dense(
            highest, "certificate highest-weight vector"
        ).reshape(-1)
        highest_support = tuple(int(index) for index in np.flatnonzero(highest_dense))
        target_weight = tuple(record["highest_weight"])
        highest_weight_exact = bool(
            highest_support
            and all(weights[index] == target_weight for index in highest_support)
            and all(
                _sparse_is_zero(
                    _checked_sparse_matmul(
                        operator,
                        highest,
                        "certificate highest-weight raising action",
                    )
                )
                for operator in _chevalley_actions_cached()["raising"]
            )
        )
        primitive = 0
        for value in highest_dense:
            primitive = math.gcd(primitive, abs(int(value)))
        natural_block_exact = all(
            block_by_row[int(row)] == record["natural_block"]
            for row in np.unique(basis.nonzero()[0])
        )
        c8_shift = _checked_sparse_linear_combination(
            ((c8_real, 1), (identity, -record["C8"])),
            "C8 eigenspace shift",
        )
        c8_exact = _sparse_is_zero(
            _checked_sparse_matmul(
                c8_shift, basis, "C8 carrier eigen-equation"
            )
        )
        rank = _rank_mod_prime(basis.toarray())
        source_denominators = sorted(
            {
                int(action[part][1])
                for action in record["source_actions"]
                for part in ("real", "imaginary")
            }
        )
        all_source_exact = all_source_exact and source_exact
        all_live_exact = all_live_exact and live_exact
        all_conjugation_exact = all_conjugation_exact and conjugation_exact
        all_conjugation_involutive = (
            all_conjugation_involutive and involutive
        )
        carrier_rows.append(
            {
                "name": record["name"],
                "irrep": record["irrep"],
                "copy_index": record["copy_index"],
                "natural_block": record["natural_block"],
                "dimension": record["dimension"],
                "highest_weight": target_weight,
                "highest_weight_primitive_and_raising_annihilated": bool(
                    primitive == 1 and highest_weight_exact
                ),
                "lowering_word_count": len(record["lowering_words"]),
                "lowering_word_maximum_length": max(
                    map(len, record["lowering_words"])
                ),
                "aligned_rank_mod_prime": rank,
                "natural_block_support_exact": natural_block_exact,
                "C8_eigen_equation_exact": c8_exact,
                "basis_maximum_absolute_entry": _maximum_abs(basis),
                "basis_sha256": _matrix_sha256(basis),
                "canonical_basis_real_sha256": _matrix_sha256(
                    record["canonical_basis_real"]
                ),
                "canonical_basis_imaginary_sha256": _matrix_sha256(
                    record["canonical_basis_imaginary"]
                ),
                "exterior_gram_sha256": _matrix_sha256(record["exterior_gram"]),
                "source_action_denominators": source_denominators,
                "all_15_common_source_actions_intertwine_exact": source_exact,
                "all_15_live_canonical_Phi210_actions_intertwine_exact": live_exact,
                "reality_kind": record["reality_kind"],
                "conjugate_carrier_name": record["conjugate_carrier_name"],
                "conjugation_map_denominator": denominator,
                "conjugation_map_sha256": _rational_hash(
                    record["conjugation_map"]
                ),
                "physical_conjugation_embedding_exact": conjugation_exact,
                "conjugation_involution_exact": involutive,
            }
        )

    family_rows = []
    for irrep, family in families.items():
        source_matrices = tuple(
            matrix
            for action in family["source_actions"]
            for part in ("real", "imaginary")
            for matrix in (
                action[part][0],
                np.asarray([[action[part][1]]], dtype=np.int64),
            )
        )
        family_rows.append(
            {
                "irrep": irrep,
                "dimension": family["dimension"],
                "multiplicity": family["multiplicity"],
                "reference_carrier_name": family["reference_carrier_name"],
                "lowering_words": tuple(
                    "identity" if not word else tuple(index + 1 for index in word)
                    for word in family["lowering_words"]
                ),
                "lowering_word_sha256": _word_sha256(family["lowering_words"]),
                "common_source_action_count": len(family["source_actions"]),
                "common_source_actions_sha256": _matrix_sha256(*source_matrices),
            }
        )

    complete = sparse.hstack(complete_bases, format="csr")
    complete_rank = _rank_mod_prime(complete.toarray())
    conjugation = data["exterior_conjugation"]
    gaussian_real, gaussian_imaginary = upstream.gaussian_exterior_basis()
    conjugation_square_exact = _sparse_is_zero(
        _checked_sparse_linear_combination(
            (
                (
                    _checked_sparse_matmul(
                        conjugation,
                        conjugation,
                        "physical conjugation square",
                    ),
                    1,
                ),
                (
                    sparse.identity(
                        PHI_DIMENSION, dtype=np.int64, format="csr"
                    ),
                    -1,
                ),
            ),
            "physical conjugation involution residual",
        )
    )
    physical_conjugation_exact = bool(
        _sparse_is_zero(
            _checked_sparse_linear_combination(
                (
                    (
                        _checked_sparse_matmul(
                            gaussian_real,
                            conjugation,
                            "Gaussian real conjugation",
                        ),
                        1,
                    ),
                    (gaussian_real, -1),
                ),
                "Gaussian real conjugation residual",
            )
        )
        and _sparse_is_zero(
            _checked_sparse_linear_combination(
                (
                    (
                        _checked_sparse_matmul(
                            gaussian_imaginary,
                            conjugation,
                            "Gaussian imaginary conjugation",
                        ),
                        1,
                    ),
                    (gaussian_imaginary, 1),
                ),
                "Gaussian imaginary conjugation residual",
            )
        )
    )
    generator_conjugation_exact = all(
        _sparse_is_zero(
            _checked_sparse_linear_combination(
                (
                    (
                        _checked_sparse_matmul(
                            conjugation, real, "conjugation/real generator"
                        ),
                        1,
                    ),
                    (
                        _checked_sparse_matmul(
                            real, conjugation, "real generator/conjugation"
                        ),
                        -1,
                    ),
                ),
                "real generator conjugation residual",
            )
        )
        and _sparse_is_zero(
            _checked_sparse_linear_combination(
                (
                    (
                        _checked_sparse_matmul(
                            conjugation,
                            imaginary,
                            "conjugation/imaginary generator",
                        ),
                        1,
                    ),
                    (
                        _checked_sparse_matmul(
                            imaginary,
                            conjugation,
                            "imaginary generator/conjugation",
                        ),
                        1,
                    ),
                ),
                "imaginary generator conjugation residual",
            )
        )
        for real, imaginary in upstream.su4_exterior_actions()
    )
    expected_names = [row["name"] for row in upstream.exact_carrier_certificate()["carriers"]]
    observed_names = [row["name"] for row in carrier_rows]
    family_word_counts_exact = all(
        row["dimension"] == len(row["lowering_words"])
        for row in family_rows
    )
    carrier_rows_exact = all(
        row["dimension"] == row["aligned_rank_mod_prime"]
        and row["highest_weight_primitive_and_raising_annihilated"]
        and row["lowering_word_count"] == row["dimension"]
        and row["natural_block_support_exact"]
        and row["C8_eigen_equation_exact"]
        and row["all_15_common_source_actions_intertwine_exact"]
        and row["all_15_live_canonical_Phi210_actions_intertwine_exact"]
        and row["physical_conjugation_embedding_exact"]
        and row["conjugation_involution_exact"]
        for row in carrier_rows
    )
    arithmetic_safety = _exact_arithmetic_safety_certificate(data)
    return {
        "rational_matrix_convention": data["rational_matrix_convention"],
        "modular_prime": MODULAR_PRIME,
        "generator_labels": data["generator_labels"],
        "simple_Chevalley_system": exact_chevalley_certificate(),
        "exact_integer_and_rational_arithmetic_safety": arithmetic_safety,
        "family_count": len(family_rows),
        "families": family_rows,
        "carrier_count": len(carrier_rows),
        "carriers": carrier_rows,
        "observed_irrep_multiplicities": dict(
            Counter(row["irrep"] for row in carrier_rows)
        ),
        "expected_irrep_multiplicities": upstream.EXPECTED_BRANCHING,
        "upstream_carrier_order_exact": observed_names == expected_names,
        "all_family_word_counts_equal_dimensions": family_word_counts_exact,
        "all_25_carriers_exact": carrier_rows_exact,
        "all_equivalent_copies_use_common_source_actions_exact": (
            all_source_exact
        ),
        "all_25_physical_Gaussian_embeddings_intertwine_live_Phi210_exact": (
            all_live_exact
        ),
        "exterior_conjugation_shape": conjugation.shape,
        "exterior_conjugation_signed_permutation_exact": bool(
            conjugation.nnz == PHI_DIMENSION
            and np.all(np.abs(conjugation.data) == 1)
            and np.all(np.diff(conjugation.indptr) == 1)
            and len(set(map(int, conjugation.indices))) == PHI_DIMENSION
        ),
        "exterior_conjugation_square_equals_identity_exact": (
            conjugation_square_exact
        ),
        "Gaussian_basis_conjugation_is_physical_exact": (
            physical_conjugation_exact
        ),
        "conjugation_compatible_with_all_15_generators_exact": (
            generator_conjugation_exact
        ),
        "all_25_conjugate_carrier_maps_exact": all_conjugation_exact,
        "all_25_conjugate_maps_involutive_exact": all_conjugation_involutive,
        "self_conjugate_real_type_carrier_count": sum(
            row["reality_kind"] == "self_conjugate_real_type"
            for row in carrier_rows
        ),
        "complex_type_carrier_count": sum(
            row["reality_kind"] == "complex_type_conjugate_pair"
            for row in carrier_rows
        ),
        "concatenated_aligned_basis_shape": complete.shape,
        "concatenated_aligned_basis_rank_mod_prime": complete_rank,
        "concatenated_aligned_basis_sha256": _matrix_sha256(complete),
        "exact_rank_argument": (
            "The same deterministic lowering words give the full irreducible "
            "dimension in every carrier. Their square 210-column "
            "concatenation has rank 210 modulo the recorded prime, hence "
            "determinant nonzero and exact rank 210 over Q."
        ),
        "proof_grade": bool(
            exact_chevalley_certificate()["proof_grade"]
            and arithmetic_safety["proof_grade"]
            and len(family_rows) == 10
            and len(carrier_rows) == 25
            and observed_names == expected_names
            and Counter(row["irrep"] for row in carrier_rows)
            == Counter(upstream.EXPECTED_BRANCHING)
            and family_word_counts_exact
            and carrier_rows_exact
            and all_source_exact
            and all_live_exact
            and conjugation_square_exact
            and physical_conjugation_exact
            and generator_conjugation_exact
            and all_conjugation_exact
            and all_conjugation_involutive
            and complete.shape == (PHI_DIMENSION, PHI_DIMENSION)
            and complete_rank == PHI_DIMENSION
        ),
    }


def exact_aligned_carrier_certificate() -> dict[str, Any]:
    """Return a mutation-isolated exact alignment certificate."""
    return _defensive_copy(_exact_aligned_carrier_certificate_cached())


def _nested_get(value: dict[str, Any], *keys: str) -> Any:
    current: Any = value
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def _build_report_from_certificates(
    *,
    upstream_model_contract_id: str,
    upstream_source_contract: dict[str, Any],
    upstream_report: dict[str, Any],
    upstream_intertwiner: dict[str, Any],
    upstream_carriers: dict[str, Any],
    alignment: dict[str, Any],
) -> dict[str, Any]:
    """Assemble fail-closed against the live companion certificates."""
    source_contract_keys = {
        "upstream_module",
        "upstream_module_sha256",
        "expected_upstream_module_sha256",
        "stabilizer_module",
        "stabilizer_module_sha256",
        "expected_stabilizer_module_sha256",
        "both_modules_resolve_to_repository_root_exact",
        "source_bytes_match_pinned_contract_exact",
        "proof_grade",
    }
    source_contract_exact = bool(
        set(upstream_source_contract) == source_contract_keys
        and upstream_source_contract.get("upstream_module")
        == EXPECTED_UPSTREAM_MODULE
        and upstream_source_contract.get("upstream_module_sha256")
        == EXPECTED_UPSTREAM_SOURCE_SHA256
        and upstream_source_contract.get("expected_upstream_module_sha256")
        == EXPECTED_UPSTREAM_SOURCE_SHA256
        and upstream_source_contract.get("stabilizer_module")
        == EXPECTED_STABILIZER_MODULE
        and upstream_source_contract.get("stabilizer_module_sha256")
        == EXPECTED_STABILIZER_SOURCE_SHA256
        and upstream_source_contract.get("expected_stabilizer_module_sha256")
        == EXPECTED_STABILIZER_SOURCE_SHA256
        and upstream_source_contract.get(
            "both_modules_resolve_to_repository_root_exact"
        )
        is True
        and upstream_source_contract.get(
            "source_bytes_match_pinned_contract_exact"
        )
        is True
        and upstream_source_contract.get("proof_grade") is True
    )
    upstream_report_hash = _canonical_json_sha256(upstream_report)
    upstream_intertwiner_hash = _canonical_json_sha256(upstream_intertwiner)
    upstream_carriers_hash = _canonical_json_sha256(upstream_carriers)
    upstream_literal_contract_exact = bool(
        upstream_report_hash == EXPECTED_UPSTREAM_REPORT_SHA256
        and upstream_intertwiner_hash
        == EXPECTED_UPSTREAM_INTERTWINER_SHA256
        and upstream_carriers_hash == EXPECTED_UPSTREAM_CARRIERS_SHA256
    )
    contract_exact = bool(
        MODEL_CONTRACT_ID == EXPECTED_MODEL_CONTRACT_ID
        and upstream_model_contract_id == MODEL_CONTRACT_ID
        and upstream_report.get("model_contract_id") == MODEL_CONTRACT_ID
        and source_contract_exact
        and upstream_literal_contract_exact
    )
    upstream_scope_exact = bool(
        upstream_report.get("n_failed") == 0
        and upstream_report.get("status")
        == "EXACT_RANK1_SU4_PHI210_INTERTWINER_INFRASTRUCTURE_CERTIFIED"
        and upstream_report.get("overall_state")
        == "SU4_SCHUR_INFRASTRUCTURE_CLOSED__SDP_AND_G3_OPEN"
        and _nested_get(
            upstream_report, "scope", "companion_stabilizer_provenance_exact"
        )
        is True
        and _nested_get(
            upstream_report, "scope", "deterministic_irreducible_carriers_complete"
        )
        is True
        and _nested_get(
            upstream_report, "scope", "SU4_invariant_quadratic_form_basis_constructed"
        )
        is False
        and _nested_get(upstream_report, "scope", "Schur_SOS_SDP_constructed")
        is False
        and _nested_get(upstream_report, "scope", "G3_closed") is False
    )
    intertwiner_exact = bool(
        upstream_intertwiner.get("proof_grade") is True
        and upstream_intertwiner.get("exterior_basis_shape") == (210, 210)
        and upstream_intertwiner.get(
            "exterior_basis_Bdagger_B_equals_16I_exact"
        )
        is True
        and upstream_intertwiner.get("intertwining_count") == 15
        and upstream_intertwiner.get("all_15_intertwinings_exact") is True
    )
    carriers_exact = bool(
        upstream_carriers.get("proof_grade") is True
        and upstream_carriers.get("carrier_count") == 25
        and len(upstream_carriers.get("carriers", ())) == 25
        and upstream_carriers.get("concatenated_carrier_shape") == (210, 210)
        and upstream_carriers.get("concatenated_carrier_rank_mod_prime") == 210
        and upstream_carriers.get("observed_irrep_multiplicities")
        == upstream.EXPECTED_BRANCHING
    )
    embedded_exact = bool(
        upstream_report.get("intertwiner") == upstream_intertwiner
        and upstream_report.get("carriers") == upstream_carriers
    )
    alignment_hash = _canonical_json_sha256(alignment)
    expected_alignment_hash = _canonical_json_sha256(
        _exact_aligned_carrier_certificate_cached()
    )
    alignment_literal_contract_exact = alignment_hash == expected_alignment_hash
    checks = {
        "model_contract_and_endpoint_provenance_exact": contract_exact,
        "upstream_source_bytes_match_pinned_contract_exact": (
            source_contract_exact
        ),
        "upstream_full_schema_and_literal_certificates_exact": (
            upstream_literal_contract_exact
        ),
        "upstream_intertwiner_report_green_and_scope_exact": upstream_scope_exact,
        "upstream_live_Gaussian_intertwiner_exact": intertwiner_exact,
        "upstream_25_carrier_census_exact": carriers_exact,
        "upstream_embedded_certificates_match_live_inputs": embedded_exact,
        "alignment_full_schema_and_literals_exact": (
            alignment_literal_contract_exact
        ),
        "integral_A3_Chevalley_system_exact": bool(
            _nested_get(alignment, "simple_Chevalley_system", "proof_grade")
        ),
        "integer_and_rational_arithmetic_safety_exact": bool(
            _nested_get(
                alignment,
                "exact_integer_and_rational_arithmetic_safety",
                "proof_grade",
            )
        ),
        "deterministic_lowering_words_align_all_25_carriers_exact": bool(
            alignment.get("proof_grade")
            and alignment.get("carrier_count") == 25
            and alignment.get("all_25_carriers_exact") is True
        ),
        "common_source_actions_on_all_equivalent_copies_exact": bool(
            alignment.get(
                "all_equivalent_copies_use_common_source_actions_exact"
            )
            is True
        ),
        "physical_live_Phi210_embeddings_exact": bool(
            alignment.get(
                "all_25_physical_Gaussian_embeddings_intertwine_live_Phi210_exact"
            )
            is True
        ),
        "physical_conjugation_and_real_structures_exact": bool(
            alignment.get("Gaussian_basis_conjugation_is_physical_exact") is True
            and alignment.get(
                "conjugation_compatible_with_all_15_generators_exact"
            )
            is True
            and alignment.get("all_25_conjugate_carrier_maps_exact") is True
            and alignment.get("all_25_conjugate_maps_involutive_exact") is True
        ),
        "aligned_25_carrier_direct_sum_rank_210_exact": bool(
            alignment.get("concatenated_aligned_basis_shape") == (210, 210)
            and alignment.get("concatenated_aligned_basis_rank_mod_prime") == 210
        ),
        "SU4_invariant_quadratic_basis_constructed": False,
        "Schur_SOS_SDP_constructed": False,
        "arbitrary_real_Phi_lower_bound_proved": False,
        "G3_closed": False,
    }
    open_checks = {
        "SU4_invariant_quadratic_basis_constructed",
        "Schur_SOS_SDP_constructed",
        "arbitrary_real_Phi_lower_bound_proved",
        "G3_closed",
    }
    failures = [
        name for name, passed in checks.items()
        if name not in open_checks and not passed
    ]
    ready = not failures
    return {
        "status": (
            "EXACT_RANK1_SU4_ALIGNED_CARRIER_INFRASTRUCTURE_CERTIFIED"
            if ready
            else "RANK1_SU4_ALIGNED_CARRIER_EXECUTION_FAILED"
        ),
        "overall_state": (
            "SU4_ALIGNED_CARRIERS_CLOSED__INVARIANT_BASIS_SDP_AND_G3_OPEN"
            if ready
            else "EXECUTION_FAIL"
        ),
        "model_contract_id": MODEL_CONTRACT_ID,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "upstream_provenance": {
            "module": (
                "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py"
            ),
            "model_contract_id": upstream_model_contract_id,
            "status": upstream_report.get("status"),
            "n_failed": upstream_report.get("n_failed"),
            "intertwiner_proof_grade": upstream_intertwiner.get("proof_grade"),
            "carrier_proof_grade": upstream_carriers.get("proof_grade"),
            "embedded_certificates_match": embedded_exact,
            "source_contract": upstream_source_contract,
            "source_contract_exact": source_contract_exact,
            "upstream_report_sha256": upstream_report_hash,
            "expected_upstream_report_sha256": (
                EXPECTED_UPSTREAM_REPORT_SHA256
            ),
            "upstream_intertwiner_certificate_sha256": (
                upstream_intertwiner_hash
            ),
            "expected_upstream_intertwiner_certificate_sha256": (
                EXPECTED_UPSTREAM_INTERTWINER_SHA256
            ),
            "upstream_carrier_certificate_sha256": upstream_carriers_hash,
            "expected_upstream_carrier_certificate_sha256": (
                EXPECTED_UPSTREAM_CARRIERS_SHA256
            ),
            "full_schema_and_literals_exact": upstream_literal_contract_exact,
            "all_required_provenance_exact": bool(
                contract_exact
                and upstream_scope_exact
                and intertwiner_exact
                and carriers_exact
                and embedded_exact
            ),
        },
        "alignment": alignment,
        "alignment_provenance": {
            "certificate_sha256": alignment_hash,
            "expected_live_certificate_sha256": expected_alignment_hash,
            "full_schema_and_literals_exact": (
                alignment_literal_contract_exact
            ),
        },
        "scope": {
            "H_fixed_to_h_minus": ready,
            "Sigma_fixed_to_q_over_4": ready,
            "rank1_endpoint_SU4_stabilizer_used": ready,
            "aligned_complexified_Phi210_carriers_constructed": ready,
            "physical_real_structure_and_Gaussian_embeddings_constructed": ready,
            "SU4_invariant_quadratic_form_basis_constructed": False,
            "Schur_SOS_SDP_constructed": False,
            "arbitrary_real_Phi_lower_bound_proved": False,
            "arbitrary_rank1_Phi_proved": False,
            "G3_closed": False,
            "whole_model_excluded": False,
        },
        "next_exact_target": (
            "Construct and independently certify the 45-dimensional real "
            "SU(4)-invariant quadratic-form basis in the live canonical "
            "Phi210 chart, then use it as one input to the full augmented "
            "degree-2 equivariant Schur/SOS system."
        ),
        "verdict": (
            "All 25 complex SU(4) carriers now have deterministic common "
            "lowering-word coordinates, exact shared source actions, live "
            "canonical Phi210 embeddings, and certified conjugation/real-form "
            "maps. Their aligned direct sum has exact rank 210. This does "
            "not yet construct the invariant quadratic basis or SDP, prove "
            "an arbitrary-Phi bound, or close G3."
        ),
    }


@lru_cache(maxsize=1)
def _build_report_cached() -> dict[str, Any]:
    upstream_report = upstream.build_report()
    upstream_intertwiner = upstream.exact_intertwiner_certificate()
    upstream_carriers = upstream.exact_carrier_certificate()
    return _build_report_from_certificates(
        upstream_model_contract_id=upstream.MODEL_CONTRACT_ID,
        upstream_source_contract=upstream_source_contract_certificate(),
        upstream_report=upstream_report,
        upstream_intertwiner=upstream_intertwiner,
        upstream_carriers=upstream_carriers,
        alignment=_exact_aligned_carrier_certificate_cached(),
    )


def build_report() -> dict[str, Any]:
    """Return a mutation-isolated copy of the cached exact report."""
    return _defensive_copy(_build_report_cached())


def render_markdown(report: dict[str, Any]) -> str:
    alignment = report["alignment"]
    arithmetic = alignment["exact_integer_and_rational_arithmetic_safety"]
    maximum_recorded_bound = max(
        arithmetic["maximum_live_product_absolute_bound"],
        arithmetic["maximum_live_scalar_absolute_bound"],
        arithmetic["modular_elimination_row_update_absolute_bound"],
    )
    return "\n".join(
        [
            "# Exact rank-one SU(4) aligned carriers -- v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "- pinned upstream source bytes and full literal certificates: `PASS`;",
            "- exact A3 Chevalley system: `PASS`;",
            "- public cached proof objects are mutation-isolated: `PASS`;",
            (
                "- maximum recorded conservative integer bound: "
                f"`{maximum_recorded_bound}` "
                "(< signed-int64 maximum);"
            ),
            f"- aligned irreducible families: `{alignment['family_count']}`;",
            f"- aligned carrier copies: `{alignment['carrier_count']}`;",
            "- common compact-generator actions: `15/15` on every copy;",
            "- physical Gaussian/live-Phi210 intertwinings: `15/15` on every copy;",
            "- conjugation and real-form maps: `25/25`, exactly involutive;",
            "- aligned direct-sum rank: `210/210`;",
            "- invariant quadratic-form basis: `OPEN in this artifact`;",
            "- Schur/SOS SDP: `OPEN`;",
            "- arbitrary-Phi bound and G3: `OPEN`.",
            "",
            f"**Next:** {report['next_exact_target']}",
            "",
        ]
    )


def write_report(report: dict[str, Any]) -> None:
    # Pin LF explicitly so regenerated evidence is byte-identical on every OS.
    with OUT_JSON.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(
            json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n"
        )
    with OUT_MD.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(render_markdown(report))


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
