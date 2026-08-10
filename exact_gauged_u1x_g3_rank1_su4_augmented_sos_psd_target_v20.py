#!/usr/bin/env python3
"""Legacy structural PSD-route API; the v20 physical RHS is rejected.

Only the private exact congruence and lower-grade construction helpers remain
available as byte-pinned generation inputs for the corrected v21 publication.
The old raw-Schur physical target is invalid and superseded.  Public report,
render, validation, artifact-writing, and command-line entrypoints fail closed
so this source cannot regenerate or certify the rejected payload.

The corrected theorem is restricted to ``H=h_-`` and ``Sigma=q/4`` with
arbitrary real ``Phi``.  It does not close G3 or vary H or Sigma.
"""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
from scipy import sparse
import sympy as sp


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20 as aligned
import exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20 as census
import exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20 as cubic
import exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20 as quartic
import exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20 as intertwiners
import exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20 as quadratics
import exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20 as rank1
import exact_phisigma_casimir_projectors_v20 as projectors
import exact_gauged_u1x_g3_pd_rank_certificate_v20 as rank_source


FIRST_PRIME = 1_000_003
SECOND_PRIME = 1_000_033
PHI_DIMENSION = 210
PAIR_DIMENSION = PHI_DIMENSION * PHI_DIMENSION
LINEAR_DENOMINATOR = 2_560
QUADRATIC_DENOMINATOR = 25_600
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
SPECTRAL_BATCH_SIZE = 24
INT64_MAX = int(np.iinfo(np.int64).max)

STATUS = "REJECTED_V20_PHYSICAL_TARGET__STRUCTURAL_PSD_ROUTES_ONLY"
OVERALL_STATE = (
    "STRUCTURAL_PSD_ROUTES_RETAINED__V20_PHYSICAL_TARGET_REJECTED__"
    "SUPERSEDED_BY_V21"
)
JSON_NAME = "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.json"
MARKDOWN_NAME = "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.md"

EXPECTED_DEPENDENCY_HASHES = {
    "exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py": "5671857444bda7d53db45393e28a3b9ac0784d0f2a63aa1e541eb5e356d23ccc",
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py": "3e0d7f2eac73eec950960f1ffd78c9584a4b15d070c84889080cf4c67d5a4d63",
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py": "589952b9b0a0b6af1543b87c89b0f3626a4bfb9c4219821a915fe04fab8af690",
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py": "28633a2dba4d70f019a3e63ca87e8224ca11630a9e7c53bc963aedc6824208c1",
    "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py": "76fa77c99b8d6e963e8694acf74280de29ced4c7a7623bffa991aead77329f49",
    "exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py": "4eec63ba40b888de736c84f607019ba0f21915028b423578502893744bab1060",
    "exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20.py": "6b2cfe46503833d8ac81dae385bef1bfa192bc0d4aa1dce392f2513b270aa14b",
    "exact_phisigma_casimir_projectors_v20.py": "372401c9b760e7b4e2224d4b6b2151611e68e7ba786ec735ebbd8baeb0103355",
    "exact_gauged_u1x_g3_pd_rank_certificate_v20.py": "e2499baf3f7a572df7647ca02f109666a549c9e2c1989110c682ee584e0483c6",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.json": "505f846291320e0671ff1208dc34339d0c2302f24ab80e9569b73d6479b2db8a",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.json": "056e1a90c028f0aaca8fb17f2f53dfb02d5e7a33230ec3675537d2778755266a",
}

IMPORTED_SOURCE_MODULES = {
    "exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py": aligned,
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py": census,
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py": cubic,
    "exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py": quartic,
    "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py": intertwiners,
    "exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py": quadratics,
    "exact_gauged_u1x_g3_su5_max_negative_rank1_su3_slice_v20.py": rank1,
    "exact_phisigma_casimir_projectors_v20.py": projectors,
    "exact_gauged_u1x_g3_pd_rank_certificate_v20.py": rank_source,
}

ARTIFACT_DEPENDENCIES = (
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.json",
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.json",
)

for _dependency_name, _dependency_module in IMPORTED_SOURCE_MODULES.items():
    _raw_module_path = getattr(_dependency_module, "__file__", None)
    if not _raw_module_path:
        raise ImportError(
            f"repository-local dependency {_dependency_module.__name__} has no __file__"
        )
    _module_path = Path(_raw_module_path).resolve()
    if _module_path.name != _dependency_name or _module_path.parent != HERE:
        raise ImportError(
            f"repository-local import contract failed for {_dependency_name}: "
            f"loaded {_module_path}, required parent {HERE}"
        )

EXPECTED_SCOPE = {
    "all_nine_real_type_standard_PSD_congruences_constructed": True,
    "all_thirteen_complex_blocks_in_standard_Hermitian_coordinates": True,
    "all_22_standard_PSD_coordinate_routes_constructed": True,
    "physical_target_formula_all_five_grades_constructed": False,
    "physical_target_full_6585_row_vector_constructed": False,
    "legacy_physical_target_rejected": True,
    "structural_PSD_routes_retained_for_v21_generation": True,
    "coefficient_map_reparameterized_in_standard_PSD_coordinates": False,
    "semidefinite_feasibility_solved": False,
    "exact_primal_PSD_certificate_constructed": False,
    "exact_dual_Farkas_certificate_constructed": False,
    "arbitrary_Phi_lower_bound_proved": False,
    "equality_orbit_classification_proved": False,
    "full_486_field_Hessian_classification_proved": False,
    "G3_closed": False,
}

EXPECTED_CLAIM_BOUNDARY = {
    "proved_here": (
        "exact standard-cone coordinate routes for all 22 augmented blocks",
    ),
    "not_proved_here": (
        "a valid physical target in the 6,585-row graded chart",
        "standard-coordinate coefficient matrix",
        "semidefinite feasibility",
        "primal PSD or dual Farkas certificate",
        "arbitrary-Phi lower bound",
        "equality orbit classification",
        "full 486-field Hessian classification",
        "G3",
    ),
}


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        _jsonable(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def _int64_array_sha256(value: np.ndarray) -> str:
    array = np.ascontiguousarray(value, dtype="<i8")
    digest = hashlib.sha256()
    digest.update(np.asarray(array.shape, dtype="<i8").tobytes())
    digest.update(array.tobytes())
    return digest.hexdigest()


def _portable_file_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _require_repository_local_file(path: Path, name: str, kind: str) -> Path:
    resolved = path.resolve(strict=True)
    if resolved.name != name:
        raise ArithmeticError(
            f"{kind} basename drifted: expected {name}, got {resolved.name}"
        )
    if resolved.parent != HERE:
        raise ArithmeticError(
            f"{kind} must be repository-local beside this module: "
            f"expected parent {HERE}, got {resolved.parent}"
        )
    return resolved


def _artifact_dependency_path(name: str) -> Path:
    if name not in ARTIFACT_DEPENDENCIES:
        raise KeyError(f"{name} is not an artifact dependency")
    path = _require_repository_local_file(HERE / name, name, "artifact dependency")
    actual_hash = _portable_file_sha256(path)
    if actual_hash != EXPECTED_DEPENDENCY_HASHES[name]:
        raise ArithmeticError(
            f"repository-local artifact hash drifted for {name}: {actual_hash}"
        )
    return path


def _imported_module_dependency_path(name: str) -> Path:
    module = IMPORTED_SOURCE_MODULES[name]
    raw_path = getattr(module, "__file__", None)
    if not raw_path:
        raise FileNotFoundError(f"imported module {module.__name__} has no __file__")
    path = _require_repository_local_file(
        Path(raw_path), name, f"imported module {module.__name__}"
    )
    actual_hash = _portable_file_sha256(path)
    if actual_hash != EXPECTED_DEPENDENCY_HASHES[name]:
        raise ArithmeticError(
            f"repository-local imported-module hash drifted for {name}: {actual_hash}"
        )
    return path


def dependency_binding_records() -> dict[str, dict[str, str]]:
    records: dict[str, dict[str, str]] = {}
    for name, module in IMPORTED_SOURCE_MODULES.items():
        path = _imported_module_dependency_path(name)
        records[name] = {
            "binding_kind": "Path(imported_module.__file__).resolve()",
            "module_name": module.__name__,
            "imported_file_basename": path.name,
            "repository_local_path": name,
            "required_parent": ".",
            "portable_sha256": _portable_file_sha256(path),
        }
    for name in ARTIFACT_DEPENDENCIES:
        path = _artifact_dependency_path(name)
        records[name] = {
            "binding_kind": "exact_predecessor_artifact",
            "module_name": "",
            "imported_file_basename": path.name,
            "repository_local_path": name,
            "required_parent": ".",
            "portable_sha256": _portable_file_sha256(path),
        }
    return records


def dependency_hashes() -> dict[str, str]:
    records = dependency_binding_records()
    return {name: records[name]["portable_sha256"] for name in EXPECTED_DEPENDENCY_HASHES}


def _require_int64(value: int, context: str) -> int:
    integer = int(value)
    if abs(integer) > INT64_MAX:
        raise OverflowError(f"{context} exceeds signed int64")
    return integer


def _pivot_rows_mod_prime(matrix: sparse.spmatrix, prime: int) -> tuple[int, ...]:
    value = matrix.tocsr()
    width = value.shape[1]
    pivots: dict[int, dict[int, int]] = {}
    selected: list[int] = []
    for row in range(value.shape[0]):
        work = {
            int(value.indices[pointer]): int(value.data[pointer]) % prime
            for pointer in range(value.indptr[row], value.indptr[row + 1])
            if int(value.data[pointer]) % prime
        }
        while work:
            lead = min(work)
            if lead not in pivots:
                inverse = pow(work[lead], prime - 2, prime)
                pivots[lead] = {
                    column: coefficient * inverse % prime
                    for column, coefficient in work.items()
                    if coefficient * inverse % prime
                }
                selected.append(row)
                break
            scale = work[lead]
            for column, coefficient in pivots[lead].items():
                updated = (work.get(column, 0) - scale * coefficient) % prime
                if updated:
                    work[column] = updated
                else:
                    work.pop(column, None)
        if len(selected) == width:
            return tuple(selected)
    raise ArithmeticError("matrix lacks a full-column-rank row minor")


def _rank_and_pivot_rows(matrix: np.ndarray, prime: int) -> tuple[int, tuple[int, ...]]:
    source = np.asarray(matrix, dtype=np.int64)
    rows, columns = source.shape
    pivots: dict[int, dict[int, int]] = {}
    selected: list[int] = []
    for row in range(rows):
        work = {
            column: int(source[row, column]) % prime
            for column in range(columns)
            if int(source[row, column]) % prime
        }
        while work:
            lead = min(work)
            if lead not in pivots:
                inverse = pow(work[lead], prime - 2, prime)
                pivots[lead] = {
                    column: coefficient * inverse % prime
                    for column, coefficient in work.items()
                    if coefficient * inverse % prime
                }
                selected.append(row)
                break
            scale = work[lead]
            for column, coefficient in pivots[lead].items():
                updated = (work.get(column, 0) - scale * coefficient) % prime
                if updated:
                    work[column] = updated
                else:
                    work.pop(column, None)
    return len(selected), tuple(selected)


def _matrix_rank_mod_prime(numerator: np.ndarray, prime: int) -> int:
    work = np.asarray(numerator, dtype=object)
    rows, columns = work.shape
    dense = [[int(work[r, c]) % prime for c in range(columns)] for r in range(rows)]
    rank = 0
    for column in range(columns):
        pivot = next((row for row in range(rank, rows) if dense[row][column]), None)
        if pivot is None:
            continue
        dense[rank], dense[pivot] = dense[pivot], dense[rank]
        inverse = pow(dense[rank][column], prime - 2, prime)
        dense[rank] = [value * inverse % prime for value in dense[rank]]
        for row in range(rows):
            if row == rank or not dense[row][column]:
                continue
            scale = dense[row][column]
            dense[row] = [
                (left - scale * right) % prime
                for left, right in zip(dense[row], dense[rank], strict=True)
            ]
        rank += 1
        if rank == rows:
            break
    return rank


def _sympy_fraction_matrix(matrix: sp.Matrix) -> tuple[np.ndarray, int]:
    denominator = 1
    for entry in matrix:
        denominator = math.lcm(denominator, int(sp.denom(entry)))
    numerator = np.asarray(
        [int(entry * denominator) for entry in matrix], dtype=object
    ).reshape(matrix.rows, matrix.cols)
    content = denominator
    for entry in numerator.reshape(-1):
        content = math.gcd(content, abs(int(entry)))
    if content > 1:
        numerator //= content
        denominator //= content
    return numerator, denominator


def _primitive_integer_nullspace(matrix: sp.Matrix) -> tuple[np.ndarray, ...]:
    output: list[np.ndarray] = []
    for vector in matrix.nullspace():
        denominator = math.lcm(*(int(sp.denom(entry)) for entry in vector))
        values = [int(entry * denominator) for entry in vector]
        content = 0
        for value in values:
            content = math.gcd(content, abs(value))
        values = [value // content for value in values]
        first = next(value for value in values if value)
        if first < 0:
            values = [-value for value in values]
        output.append(np.asarray(values, dtype=object))
    return tuple(output)


def _solve_rational_columns(
    matrix: np.ndarray, target_numerator: np.ndarray, target_denominator: int
) -> tuple[tuple[Fraction, ...], tuple[int, ...]]:
    source = np.asarray(matrix, dtype=np.int64)
    target = np.asarray(target_numerator, dtype=np.int64).reshape(-1)
    rank, pivot_rows = _rank_and_pivot_rows(source, FIRST_PRIME)
    if rank != source.shape[1]:
        raise ArithmeticError("candidate invariant basis is rank deficient")
    selected = pivot_rows[: source.shape[1]]
    left = sp.Matrix(source[list(selected), :].tolist())
    right = sp.Matrix([[int(target[row])] for row in selected]) / target_denominator
    solution = left.inv() * right
    coefficients = tuple(
        Fraction(int(sp.numer(value)), int(sp.denom(value))) for value in solution
    )
    denominator = math.lcm(*(value.denominator for value in coefficients))
    integers = np.asarray(
        [value.numerator * (denominator // value.denominator) for value in coefficients],
        dtype=np.int64,
    )
    residual = source @ integers * target_denominator - target * denominator
    if np.any(residual):
        raise ArithmeticError("exact invariant-coordinate reconstruction failed")
    return coefficients, selected


def _primitive_vector(values: np.ndarray) -> np.ndarray:
    vector = np.asarray(values, dtype=np.int64).reshape(-1).copy()
    content = 0
    for value in vector:
        content = math.gcd(content, abs(int(value)))
    if not content:
        raise ArithmeticError("zero vector cannot be normalized")
    vector //= content
    if int(vector[np.flatnonzero(vector)[0]]) < 0:
        vector = -vector
    return vector


def _extract_real_structure(
    copies: Sequence[sparse.csr_matrix],
    conjugation: sparse.csr_matrix,
    weights: Sequence[tuple[int, int, int]],
    representative: tuple[int, int, int],
) -> dict[str, Any]:
    lowest_weight = (-representative[2], -representative[1], -representative[0])
    lowest_indices = [index for index, weight in enumerate(weights) if weight == lowest_weight]
    if len(lowest_indices) != 1:
        raise ArithmeticError(f"{representative}: non-unique extremal component")
    lowest_index = lowest_indices[0]
    highest = sparse.hstack([copy[:, 0] for copy in copies], format="csr")
    lowest = sparse.hstack([copy[:, lowest_index] for copy in copies], format="csr")
    conjugated = conjugation @ highest
    selected_rows = _pivot_rows_mod_prime(lowest, FIRST_PRIME)
    left = sp.Matrix(lowest[list(selected_rows), :].toarray().tolist())
    right = sp.Matrix(conjugated[list(selected_rows), :].toarray().tolist())
    numerator, denominator = _sympy_fraction_matrix(left.inv() * right)
    maximum = max((abs(int(value)) for value in numerator.reshape(-1)), default=0)
    _require_int64(maximum, f"{representative} real structure")
    integer = np.asarray(numerator, dtype=np.int64)
    residual = quartic._safe_sparse_matmul(
        lowest, sparse.csr_matrix(integer), "physical multiplicity real structure"
    ) - conjugated * denominator
    residual.eliminate_zeros()
    if residual.nnz:
        raise ArithmeticError(f"{representative}: full real-structure residual")
    if not np.array_equal(integer @ integer, np.eye(len(copies), dtype=np.int64)):
        raise ArithmeticError(f"{representative}: primitive structure is not involutive")
    return {
        "matrix": integer,
        "component_scale_denominator": denominator,
        "selected_evaluation_rows": selected_rows,
        "selected_minor_determinant": int(left.det()),
        "lowest_component_index": lowest_index,
        "full_coordinate_residual_nnz": int(residual.nnz),
        "maximum_absolute_entry": maximum,
    }


@lru_cache(maxsize=None)
def _phi2_real_structure(representative: tuple[int, int, int]) -> dict[str, Any]:
    family = quartic._carrier_family_data_cached()[representative]
    copies = tuple(copy.tocsr() for copy in family["copies"])
    return _extract_real_structure(
        copies,
        quartic._sym2_conjugation_cached(),
        tuple(family["lowering_word_weights"]),
        representative,
    )


def _build_congruences() -> dict[str, Any]:
    aligned_data = aligned.exact_aligned_carrier_data()
    target_carriers = cubic._target_carrier_data_cached()
    phi_conjugation = aligned.exterior_conjugation()
    sym2_conjugation = quartic._sym2_conjugation_cached()
    real_rows: list[dict[str, Any]] = []
    for block in census.exact_augmented_isotypic_blocks():
        if not block["self_conjugate"]:
            continue
        representative = tuple(block["representative_dynkin"])
        grades = tuple(int(value) for value in block["graded_multiplicities_t2_tPhi_Phi2"])
        phi2 = _phi2_real_structure(representative)
        grade_rows: list[tuple[str, np.ndarray, int, dict[str, Any]]] = []
        if grades[0]:
            grade_rows.append(("t2", np.eye(1, dtype=np.int64), 1, {}))
        if grades[1]:
            irrep = next(
                name
                for name, record in intertwiners.IRREP_DATA.items()
                if tuple(record["dynkin"]) == representative
            )
            words = tuple(aligned_data["families"][irrep]["lowering_words"])
            weights = cubic._word_weights(irrep, words)
            source_copies = tuple(
                carrier["exterior_basis"].tocsr()
                for carrier in aligned_data["carriers"]
                if carrier["irrep"] == irrep
            )
            tphi = _extract_real_structure(
                source_copies, phi_conjugation, weights, representative
            )
            target_phi2 = _extract_real_structure(
                tuple(copy.tocsr() for copy in target_carriers[irrep]["copies"]),
                sym2_conjugation,
                weights,
                representative,
            )
            if not np.array_equal(target_phi2["matrix"], phi2["matrix"]):
                raise ArithmeticError("aligned cubic and quartic Phi2 structures differ")
            grade_rows.append(
                ("tPhi", tphi["matrix"], tphi["component_scale_denominator"], tphi)
            )
            grade_rows.append(
                (
                    "Phi2",
                    target_phi2["matrix"],
                    target_phi2["component_scale_denominator"],
                    target_phi2,
                )
            )
        else:
            grade_rows.append(
                (
                    "Phi2",
                    phi2["matrix"],
                    phi2["component_scale_denominator"],
                    phi2,
                )
            )
        denominators = {denominator for _, _, denominator, _ in grade_rows}
        if len(denominators) != 1:
            raise ArithmeticError(f"{representative}: inconsistent component normalizations")
        augmented = sparse.block_diag(
            [matrix for _, matrix, _, _ in grade_rows], format="csr", dtype=np.int64
        ).toarray()
        multiplicity = sum(grades)
        if augmented.shape != (multiplicity, multiplicity):
            raise ArithmeticError(f"{representative}: augmented size drifted")
        if not np.array_equal(augmented @ augmented, np.eye(multiplicity, dtype=np.int64)):
            raise ArithmeticError(f"{representative}: augmented structure is not involutive")
        sympy_augmented = sp.Matrix(augmented.tolist())
        plus = _primitive_integer_nullspace(sympy_augmented - sp.eye(multiplicity))
        minus = _primitive_integer_nullspace(sympy_augmented + sp.eye(multiplicity))
        p = np.column_stack(plus) if plus else np.zeros((multiplicity, 0), dtype=object)
        q = np.column_stack(minus) if minus else np.zeros((multiplicity, 0), dtype=object)
        fixed = np.column_stack((p, q))
        first_rank = _matrix_rank_mod_prime(fixed, FIRST_PRIME)
        second_rank = _matrix_rank_mod_prime(fixed, SECOND_PRIME)
        plus_residual = np.asarray(augmented, dtype=object) @ p - p
        minus_residual = np.asarray(augmented, dtype=object) @ q + q
        naive_residual = (
            np.asarray(augmented, dtype=object) @ np.asarray(augmented.T, dtype=object)
            - np.eye(multiplicity, dtype=object)
        )
        row_proof = bool(
            len(plus) + len(minus) == multiplicity
            and first_rank == second_rank == multiplicity
            and not np.any(plus_residual)
            and not np.any(minus_residual)
        )
        real_rows.append(
            {
                "representative_dynkin": representative,
                "graded_multiplicities_t2_tPhi_Phi2": grades,
                "augmented_multiplicity": multiplicity,
                "PSD_cone": block["PSD_cone"],
                "common_component_scale_denominator": next(iter(denominators)),
                "grade_real_structures": tuple(
                    {
                        "grade": label,
                        "multiplicity": int(matrix.shape[0]),
                        "matrix": matrix,
                        "component_scale_denominator": denominator,
                        "matrix_sha256": _canonical_sha256(matrix),
                        "full_coordinate_residual_nnz": int(
                            metadata.get("full_coordinate_residual_nnz", 0)
                        ),
                    }
                    for label, matrix, denominator, metadata in grade_rows
                ),
                "augmented_real_structure": augmented,
                "augmented_real_structure_sha256": _canonical_sha256(augmented),
                "plus_eigenspace_dimension": len(plus),
                "minus_eigenspace_dimension": len(minus),
                "fixed_basis_real_numerator": p,
                "fixed_basis_imaginary_numerator": q,
                "fixed_basis_sha256": _canonical_sha256({"P": p, "Q": q}),
                "fixed_basis_maximum_absolute_entry": max(
                    (abs(int(value)) for value in fixed.reshape(-1)), default=0
                ),
                "fixed_basis_rank_at_first_prime": first_rank,
                "fixed_basis_rank_at_second_prime": second_rank,
                "B_Fbar_equals_F_residual_maximum_absolute_entry": max(
                    [abs(int(value)) for value in plus_residual.reshape(-1)]
                    + [abs(int(value)) for value in minus_residual.reshape(-1)]
                    + [0]
                ),
                "naive_original_coordinate_identity_is_tau_fixed": bool(
                    not np.any(naive_residual)
                ),
                "naive_identity_tau_residual_nnz": int(np.count_nonzero(naive_residual)),
                "naive_identity_tau_residual_maximum_absolute_entry": max(
                    (abs(int(value)) for value in naive_residual.reshape(-1)), default=0
                ),
                "standard_PSD_congruence": (
                    "F=[P | iQ]; H=F*A*F^dagger with A in S_+^m(R)"
                ),
                "cone_equivalence": (
                    "B*conjugate(F)=F and F is invertible, hence A real symmetric PSD "
                    "iff H=F*A*F^dagger is Hermitian PSD and tau-fixed."
                ),
                "proof_grade": row_proof,
            }
        )
    complex_rows = tuple(
        {
            "representative_dynkin": tuple(block["representative_dynkin"]),
            "graded_multiplicities_t2_tPhi_Phi2": tuple(
                int(value) for value in block["graded_multiplicities_t2_tPhi_Phi2"]
            ),
            "augmented_multiplicity": sum(block["graded_multiplicities_t2_tPhi_Phi2"]),
            "PSD_cone": block["PSD_cone"],
            "coordinate_convention": (
                "real diagonal, real off-diagonal, imaginary off-diagonal; "
                "standard Herm_+^m(C)"
            ),
        }
        for block in census.exact_augmented_isotypic_blocks()
        if not block["self_conjugate"]
    )
    real_parameter_count = sum(
        int(row["augmented_multiplicity"])
        * (int(row["augmented_multiplicity"]) + 1)
        // 2
        for row in real_rows
    )
    complex_parameter_count = sum(
        int(row["augmented_multiplicity"]) ** 2 for row in complex_rows
    )
    failing = tuple(
        row["representative_dynkin"]
        for row in real_rows
        if not row["naive_original_coordinate_identity_is_tau_fixed"]
    )
    return {
        "real_type_block_count": len(real_rows),
        "real_type_rows": real_rows,
        "complex_Hermitian_block_count": len(complex_rows),
        "complex_Hermitian_rows": complex_rows,
        "standard_real_parameter_count": real_parameter_count,
        "standard_complex_parameter_count": complex_parameter_count,
        "standard_total_parameter_count": real_parameter_count + complex_parameter_count,
        "naive_coordinate_counterexample": {
            "statement": (
                "H=I in raw carrier-copy coordinates is not tau-fixed whenever B*B^T != I; "
                "therefore raw coordinates cannot be declared standard PSD coordinates."
            ),
            "failing_block_count": len(failing),
            "failing_representatives": failing,
        },
        "all_22_cones_have_standard_coordinate_routes": bool(
            len(real_rows) == 9
            and len(complex_rows) == 13
            and all(row["proof_grade"] for row in real_rows)
            and real_parameter_count + complex_parameter_count == 19_594
        ),
    }


def _linear_basis_and_coordinates(linear_numerator: np.ndarray) -> dict[str, Any]:
    data = aligned.exact_aligned_carrier_data()
    candidates: list[np.ndarray] = []
    origins: list[dict[str, Any]] = []
    for carrier in data["carriers"]:
        if int(carrier["dimension"]) != 1:
            continue
        for component, matrix in (
            ("real", carrier["canonical_basis_real"]),
            ("imaginary", carrier["canonical_basis_imaginary"]),
        ):
            if not matrix.nnz:
                continue
            candidates.append(_primitive_vector(matrix.toarray()[:, 0]))
            origins.append({"carrier": carrier["name"], "component": component})
    candidate_matrix = np.column_stack(candidates)
    row_rank, _ = _rank_and_pivot_rows(candidate_matrix, FIRST_PRIME)
    column_rank, selected_columns = _rank_and_pivot_rows(candidate_matrix.T, FIRST_PRIME)
    if row_rank != column_rank or row_rank != 4:
        raise ArithmeticError("trivial-carrier invariant dimension drifted")
    selected_columns = selected_columns[:4]
    basis = candidate_matrix[:, list(selected_columns)]
    coefficients, selected_rows = _solve_rational_columns(
        basis, linear_numerator, LINEAR_DENOMINATOR
    )
    second_rank, _ = _rank_and_pivot_rows(basis, SECOND_PRIME)
    return {
        "candidate_count": len(candidates),
        "selected_candidate_indices": selected_columns,
        "selected_origins": tuple(origins[index] for index in selected_columns),
        "basis_sha256": _canonical_sha256(basis),
        "rank_at_first_prime": row_rank,
        "rank_at_second_prime": second_rank,
        "target_coordinates": coefficients,
        "target_coordinate_sha256": _canonical_sha256(coefficients),
        "selected_evaluation_rows": selected_rows,
        "proof_grade": bool(row_rank == second_rank == 4),
    }


def _quadratic_basis_coordinates(quadratic_numerator: np.ndarray) -> dict[str, Any]:
    matrices = quadratics.exact_invariant_quadratic_basis()
    upper_rows, upper_columns = np.triu_indices(PHI_DIMENSION)
    columns = np.column_stack(
        [matrix.toarray()[upper_rows, upper_columns] for matrix in matrices]
    ).astype(np.int64)
    target = quadratic_numerator[upper_rows, upper_columns]
    coefficients, selected_rows = _solve_rational_columns(
        columns, target, QUADRATIC_DENOMINATOR
    )
    second_rank, _ = _rank_and_pivot_rows(columns, SECOND_PRIME)
    return {
        "ordered_basis_dimension": len(matrices),
        "ordered_basis_sha256": quadratics.build_report()["quadratic_basis"][
            "basis_sha256"
        ],
        "rank_at_first_prime": len(selected_rows),
        "rank_at_second_prime": second_rank,
        "target_coordinates": coefficients,
        "target_coordinate_nonzero_count": sum(bool(value) for value in coefficients),
        "target_coordinate_sha256": _canonical_sha256(coefficients),
        "selected_upper_triangle_rows": selected_rows,
        "proof_grade": bool(len(selected_rows) == second_rank == 45),
    }


def _build_lower_target() -> dict[str, Any]:
    source = rank1.exact_rank1_residual_source()
    mixed = np.asarray(source["mixed"], dtype=np.int64)
    target = np.asarray(source["target"], dtype=np.int64)
    chiral = np.asarray(source["chiral"], dtype=np.int64)
    linear_numerator = -(mixed.T @ target)
    quadratic_numerator = (
        -5_120 * np.eye(PHI_DIMENSION, dtype=np.int64)
        + 576 * (chiral.T @ chiral)
        + 5 * (mixed.T @ mixed)
    )
    constant = Fraction(1) + Fraction(int(target @ target), 5_120) - Fraction(3, 200)
    linear_basis = _linear_basis_and_coordinates(linear_numerator)
    quadratic_basis = _quadratic_basis_coordinates(quadratic_numerator)
    basis_real, basis_imaginary = intertwiners.gaussian_exterior_basis()
    br = basis_real.toarray().astype(np.int64)
    bi = basis_imaginary.toarray().astype(np.int64)
    gaussian_linear_real = br.T @ linear_numerator
    gaussian_linear_imaginary = bi.T @ linear_numerator
    gaussian_quadratic_real = (
        br.T @ quadratic_numerator @ br - bi.T @ quadratic_numerator @ bi
    )
    gaussian_quadratic_imaginary = (
        br.T @ quadratic_numerator @ bi + bi.T @ quadratic_numerator @ br
    )
    conjugation = aligned.exterior_conjugation()
    linear_conjugation_residual = conjugation @ gaussian_linear_real - gaussian_linear_real
    quadratic_conjugation_residual = (
        conjugation @ sparse.csr_matrix(gaussian_quadratic_real) @ conjugation.T
        - sparse.csr_matrix(gaussian_quadratic_real)
    )
    quadratic_conjugation_residual.eliminate_zeros()
    checks = {
        "rank1_residual_source_exact": bool(source["source_binding_exact"]),
        "constant_237_over_200_exact": constant == Fraction(237, 200),
        "linear_10_nonzero_each_minus_1_over_10_exact": bool(
            np.count_nonzero(linear_numerator) == 10
            and set(int(value) for value in linear_numerator if value) == {-256}
        ),
        "quadratic_numerator_symmetric_exact": bool(
            np.array_equal(quadratic_numerator, quadratic_numerator.T)
        ),
        "quadratic_numerator_1460_nnz_max_4960_exact": bool(
            np.count_nonzero(quadratic_numerator) == 1_460
            and int(np.max(np.abs(quadratic_numerator))) == 4_960
        ),
        "linear_SU4_invariant_coordinates_exact": bool(linear_basis["proof_grade"]),
        "quadratic_SU4_invariant_coordinates_exact": bool(quadratic_basis["proof_grade"]),
        "Gaussian_lower_coefficients_purely_real_exact": bool(
            not np.any(gaussian_linear_imaginary)
            and not np.any(gaussian_quadratic_imaginary)
        ),
        "Gaussian_linear_physical_conjugation_exact": bool(
            not np.any(linear_conjugation_residual)
        ),
        "Gaussian_quadratic_physical_conjugation_exact": bool(
            not quadratic_conjugation_residual.nnz
        ),
        "cubic_target_zero_by_explicit_graded_formula_exact": True,
    }
    return {
        "normalization": {
            "variable": "z=sqrt(10)Phi",
            "anchor": (
                "A=(N_Phi-1)^2+I54+I4125+9||Cz||^2/400+||Mz-b||^2/5120"
            ),
            "physical_target": "p=A-3/200",
        },
        "source_shapes": {
            "M": mixed.shape,
            "C": chiral.shape,
            "b": target.shape,
            "b_norm_squared": int(target @ target),
        },
        "constant": constant,
        "linear": {
            "formula": "-(M^T b)/2560",
            "live_denominator": LINEAR_DENOMINATOR,
            "live_numerator_nonzero_count": int(np.count_nonzero(linear_numerator)),
            "live_numerator_sha256": _canonical_sha256(linear_numerator),
            "SU4_invariant_basis": linear_basis,
            "Gaussian_numerator_sha256": _canonical_sha256(
                {"real": gaussian_linear_real, "imaginary": gaussian_linear_imaginary}
            ),
        },
        "quadratic": {
            "formula": "-I/5+(9/400)C^T C+(1/5120)M^T M",
            "live_common_denominator": QUADRATIC_DENOMINATOR,
            "live_numerator_nonzero_count": int(np.count_nonzero(quadratic_numerator)),
            "live_numerator_maximum_absolute_entry": int(
                np.max(np.abs(quadratic_numerator))
            ),
            "live_numerator_sha256": _canonical_sha256(quadratic_numerator),
            "SU4_invariant_basis": quadratic_basis,
            "Gaussian_numerator_sha256": _canonical_sha256(
                {
                    "real": gaussian_quadratic_real,
                    "imaginary": gaussian_quadratic_imaginary,
                }
            ),
        },
        "cubic": {
            "formula": "0",
            "row_count": 478,
            "all_target_rows_zero_exact": True,
        },
        "checks": checks,
        "proof_grade": all(checks.values()),
    }


@lru_cache(maxsize=None)
def _gaussian_column(column: int) -> tuple[tuple[int, int, int], ...]:
    real, imaginary = intertwiners.gaussian_exterior_basis()
    real_column = real.getcol(column).tocoo()
    imaginary_column = imaginary.getcol(column).tocoo()
    values: dict[int, list[int]] = {}
    for row, value in zip(real_column.row, real_column.data, strict=True):
        values.setdefault(int(row), [0, 0])[0] += int(value)
    for row, value in zip(imaginary_column.row, imaginary_column.data, strict=True):
        values.setdefault(int(row), [0, 0])[1] += int(value)
    return tuple(
        (row, value[0], value[1])
        for row, value in sorted(values.items())
        if value[0] or value[1]
    )


@lru_cache(maxsize=None)
def _ordered_pair_column(pair_coordinate: int) -> tuple[dict[int, int], dict[int, int]]:
    left, right = cubic._quadratic_pairs_cached()[pair_coordinate]
    first = _gaussian_column(left)
    second = _gaussian_column(right)
    real: dict[int, int] = {}
    imaginary: dict[int, int] = {}

    def add_outer(
        one: tuple[tuple[int, int, int], ...],
        two: tuple[tuple[int, int, int], ...],
    ) -> None:
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


def _column_matrix(
    coordinates: tuple[int, ...]
) -> tuple[sparse.csc_matrix, sparse.csc_matrix]:
    rows_real: list[int] = []
    columns_real: list[int] = []
    values_real: list[int] = []
    rows_imaginary: list[int] = []
    columns_imaginary: list[int] = []
    values_imaginary: list[int] = []
    for column, coordinate in enumerate(coordinates):
        real, imaginary = _ordered_pair_column(coordinate)
        for row, value in real.items():
            rows_real.append(row)
            columns_real.append(column)
            values_real.append(_require_int64(value, "Gaussian real pair column"))
        for row, value in imaginary.items():
            rows_imaginary.append(row)
            columns_imaginary.append(column)
            values_imaginary.append(_require_int64(value, "Gaussian imaginary pair column"))
    shape = (PAIR_DIMENSION, len(coordinates))
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


def _extremal_minors() -> tuple[dict[str, Any], ...]:
    rows: list[dict[str, Any]] = []
    conjugation = quartic._sym2_conjugation_cached()
    for representative, family in quartic._carrier_family_data_cached().items():
        copies = tuple(copy.tocsr() for copy in family["copies"])
        highest = sparse.hstack([copy[:, 0] for copy in copies], format="csr")
        conjugate_highest = conjugation @ highest
        left_rows = _pivot_rows_mod_prime(highest, FIRST_PRIME)
        right_rows = _pivot_rows_mod_prime(conjugate_highest, FIRST_PRIME)
        rows.append(
            {
                "representative_dynkin": representative,
                "multiplicity": len(copies),
                "left_rows": left_rows,
                "right_rows": right_rows,
                "left_minor": highest[list(left_rows), :].toarray().astype(np.int64),
                "right_minor": conjugate_highest[list(right_rows), :]
                .toarray()
                .astype(np.int64),
            }
        )
    return tuple(rows)


def _spectral_restrictions(
    minors: tuple[dict[str, Any], ...]
) -> tuple[tuple[dict[str, Any], ...], dict[str, Any]]:
    left_coordinates = tuple(
        sorted({coordinate for row in minors for coordinate in row["left_rows"]})
    )
    right_coordinates = tuple(
        sorted({coordinate for row in minors for coordinate in row["right_rows"]})
    )
    left_index = {coordinate: index for index, coordinate in enumerate(left_coordinates)}
    right_index = {coordinate: index for index, coordinate in enumerate(right_coordinates)}
    left_real, left_imaginary = _column_matrix(left_coordinates)
    right_real, right_imaginary = _column_matrix(right_coordinates)
    operator = rank_source._phi_pair_casimir_integer().tocsr()
    real_values = np.zeros((len(left_coordinates), len(right_coordinates)), dtype=np.int64)
    imaginary_values = np.zeros_like(real_values)
    observed_power_maximum = 0
    observed_response_maximum = 0
    maximum_batch_response_nnz = 0
    for start in range(0, len(right_coordinates), SPECTRAL_BATCH_SIZE):
        stop = min(start + SPECTRAL_BATCH_SIZE, len(right_coordinates))
        current_real = right_real[:, start:stop].tocsr()
        current_imaginary = right_imaginary[:, start:stop].tocsr()
        response_real = current_real * SPECTRAL_NUMERATORS[0]
        response_imaginary = current_imaginary * SPECTRAL_NUMERATORS[0]
        for numerator in SPECTRAL_NUMERATORS[1:]:
            current_real = quartic._safe_sparse_matmul(
                operator, current_real, "spectral target real power"
            )
            current_imaginary = quartic._safe_sparse_matmul(
                operator, current_imaginary, "spectral target imaginary power"
            )
            observed_power_maximum = max(
                observed_power_maximum,
                max((abs(int(value)) for value in current_real.data), default=0),
                max((abs(int(value)) for value in current_imaginary.data), default=0),
            )
            response_real = (response_real + current_real * numerator).tocsr()
            response_imaginary = (response_imaginary + current_imaginary * numerator).tocsr()
            response_real.eliminate_zeros()
            response_imaginary.eliminate_zeros()
        observed_response_maximum = max(
            observed_response_maximum,
            max((abs(int(value)) for value in response_real.data), default=0),
            max((abs(int(value)) for value in response_imaginary.data), default=0),
        )
        maximum_batch_response_nnz = max(
            maximum_batch_response_nnz, response_real.nnz + response_imaginary.nnz
        )
        rr = quartic._safe_sparse_matmul(
            left_real.T, response_real, "spectral target real-real restriction"
        ) - quartic._safe_sparse_matmul(
            left_imaginary.T,
            response_imaginary,
            "spectral target imaginary-imaginary restriction",
        )
        ri = quartic._safe_sparse_matmul(
            left_real.T, response_imaginary, "spectral target real-imaginary restriction"
        ) + quartic._safe_sparse_matmul(
            left_imaginary.T, response_real, "spectral target imaginary-real restriction"
        )
        real_values[:, start:stop] = rr.toarray()
        imaginary_values[:, start:stop] = ri.toarray()
    output: list[dict[str, Any]] = []
    for row in minors:
        left = [left_index[coordinate] for coordinate in row["left_rows"]]
        right = [right_index[coordinate] for coordinate in row["right_rows"]]
        output.append(
            {
                **row,
                "spectral_restriction_real_numerator": real_values[np.ix_(left, right)],
                "spectral_restriction_imaginary_numerator": imaginary_values[
                    np.ix_(left, right)
                ],
            }
        )
    metadata = {
        "left_coordinate_count": len(left_coordinates),
        "right_coordinate_count": len(right_coordinates),
        "left_transform_shape": left_real.shape,
        "left_transform_real_nnz": left_real.nnz,
        "left_transform_imaginary_nnz": left_imaginary.nnz,
        "right_transform_shape": right_real.shape,
        "right_transform_real_nnz": right_real.nnz,
        "right_transform_imaginary_nnz": right_imaginary.nnz,
        "observed_power_maximum": observed_power_maximum,
        "observed_response_maximum": observed_response_maximum,
        "maximum_batch_response_nnz": maximum_batch_response_nnz,
        "spectral_denominator": SPECTRAL_DENOMINATOR,
    }
    return tuple(output), metadata


def _raw_schur_coefficients(
    restrictions: tuple[dict[str, Any], ...]
) -> tuple[tuple[dict[str, Any], ...], dict[str, Any]]:
    source_rows = {
        tuple(row["representative_dynkin"]): row for row in restrictions
    }
    rows: list[dict[str, Any]] = []
    for block in quartic._block_specs_cached():
        representative = tuple(block["representative_dynkin"])
        row = source_rows[representative]
        left = sp.Matrix(row["left_minor"])
        right = sp.Matrix(row["right_minor"])
        target = sp.Matrix(row["spectral_restriction_real_numerator"])
        pairing = quartic._pairing_data_cached()[representative]["pairing"]
        scale = int(pairing[0, 0]) * SPECTRAL_DENOMINATOR
        coefficient = left.inv() * target * right.T.inv() / scale
        numerator, denominator = _sympy_fraction_matrix(coefficient)
        maximum = max((abs(int(value)) for value in numerator.reshape(-1)), default=0)
        _require_int64(maximum, f"{representative} raw Schur coefficient")
        integer = np.asarray(numerator, dtype=np.int64)
        reconstruction = (
            left * sp.Matrix(integer.tolist()) * right.T * scale
            - target * denominator
        )
        if reconstruction != sp.zeros(*reconstruction.shape):
            raise ArithmeticError(f"{representative}: extremal Schur reconstruction failed")
        rows.append(
            {
                "block_index": int(block["block_index"]),
                "representative_dynkin": representative,
                "multiplicity": int(block["multiplicity"]),
                "coefficient_numerator": integer,
                "coefficient_denominator": denominator,
                "coefficient_nnz": int(np.count_nonzero(integer)),
                "coefficient_maximum_absolute_numerator": maximum,
                "coefficient_sha256": _canonical_sha256(
                    {"numerator": integer, "denominator": denominator}
                ),
                "extremal_reconstruction_residual_zero_exact": True,
            }
        )
    return tuple(rows), {
        "block_count": len(rows),
        "total_nonzero_raw_coefficients": sum(row["coefficient_nnz"] for row in rows),
        "all_extremal_reconstructions_zero_exact": all(
            row["extremal_reconstruction_residual_zero_exact"] for row in rows
        ),
    }


def _quartic_chart_target(
    coefficient_rows: tuple[dict[str, Any], ...]
) -> dict[str, Any]:
    quartic_artifact = json.loads(
        _artifact_dependency_path(
            "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.json"
        ).read_text(encoding="utf-8")
    )
    pivot_physical = tuple(
        quartic_artifact["coefficient_map_certificate"][
            "pivot_physical_quartic_coordinates"
        ]
    )
    expected_pivot_hash = quartic_artifact["coefficient_map_certificate"][
        "pivot_physical_quartic_coordinates_sha256"
    ]
    if _canonical_sha256(pivot_physical) != expected_pivot_hash:
        raise ArithmeticError("quartic pivot-coordinate hash drifted")
    rows_by_representative = {
        tuple(row["representative_dynkin"]): row for row in coefficient_rows
    }
    even_raw_coordinates = {
        coordinate // 2 for coordinate in pivot_physical if coordinate % 2 == 0
    }
    common_denominator = math.lcm(
        *(int(row["coefficient_denominator"]) for row in coefficient_rows)
    )
    accumulator = {coordinate: 0 for coordinate in even_raw_coordinates}
    multiplication_count = 0
    total_intermediate_image_nnz = 0
    maximum_intermediate_image_nnz = 0
    maximum_intermediate_image_coefficient = 0
    for block in quartic._block_specs_cached():
        representative = tuple(block["representative_dynkin"])
        row = rows_by_representative[representative]
        matrix = np.asarray(row["coefficient_numerator"], dtype=np.int64)
        denominator = int(row["coefficient_denominator"])
        scale = common_denominator // denominator
        multiplicity = int(block["multiplicity"])
        if matrix.shape != (multiplicity, multiplicity):
            raise ArithmeticError("raw Schur coefficient shape drifted")
        conjugates = tuple(
            quartic._conjugate_carrier(representative, index)
            for index in range(multiplicity)
        )
        block_accumulator: dict[int, int] = {}
        for left in range(multiplicity):
            nonzero = np.flatnonzero(matrix[left])
            if not nonzero.size:
                continue
            combined: sparse.csr_matrix | None = None
            for right in nonzero:
                term = conjugates[int(right)] * int(matrix[left, int(right)])
                combined = term.tocsr() if combined is None else (combined + term).tocsr()
            if combined is None:
                continue
            combined.sum_duplicates()
            combined.eliminate_zeros()
            if combined.data.size:
                _require_int64(
                    max(abs(int(value)) for value in combined.data),
                    "combined conjugate carrier",
                )
            tensor = quartic._safe_sparse_matmul(
                quartic._left_paired_carrier(representative, left),
                combined.T,
                "physical quartic target Schur block",
            )
            image = quartic._multiply_tensor_to_quartic(tensor)
            multiplication_count += 1
            total_intermediate_image_nnz += len(image)
            maximum_intermediate_image_nnz = max(
                maximum_intermediate_image_nnz, len(image)
            )
            maximum_intermediate_image_coefficient = max(
                maximum_intermediate_image_coefficient,
                max((abs(value) for value in image.values()), default=0),
            )
            for coordinate, value in image.items():
                if coordinate in even_raw_coordinates:
                    block_accumulator[coordinate] = (
                        block_accumulator.get(coordinate, 0) + int(value)
                    )
        for coordinate, value in block_accumulator.items():
            accumulator[coordinate] += scale * value
    target_numerator = np.asarray(
        [
            accumulator[coordinate // 2] if coordinate % 2 == 0 else 0
            for coordinate in pivot_physical
        ],
        dtype=np.int64,
    )
    content = common_denominator
    for value in target_numerator:
        content = math.gcd(content, abs(int(value)))
    if content > 1:
        target_numerator //= content
        common_denominator //= content
    odd_indices = np.asarray(
        [index for index, coordinate in enumerate(pivot_physical) if coordinate % 2],
        dtype=np.int64,
    )
    return {
        "formula": (
            "<z tensor z,[I+P54(K)+P4125(K)](z tensor z)>/100, z=sqrt(10)Phi"
        ),
        "spectral_operator_numerator_coefficients_K_degree_0_through_7": (
            SPECTRAL_NUMERATORS
        ),
        "spectral_operator_denominator": SPECTRAL_DENOMINATOR,
        "row_count": len(pivot_physical),
        "real_channel_row_count": sum(coordinate % 2 == 0 for coordinate in pivot_physical),
        "i_times_anti_real_channel_row_count": sum(
            coordinate % 2 == 1 for coordinate in pivot_physical
        ),
        "pivot_physical_quartic_coordinates_sha256": expected_pivot_hash,
        "common_denominator": common_denominator,
        "numerator": target_numerator,
        "numerator_sha256": _int64_array_sha256(target_numerator),
        "nonzero_count": int(np.count_nonzero(target_numerator)),
        "maximum_absolute_numerator": int(np.max(np.abs(target_numerator), initial=0)),
        "all_i_times_anti_real_rows_zero_exact": bool(
            not np.any(target_numerator[odd_indices])
        ),
        "stream": {
            "combined_tensor_multiplication_count": multiplication_count,
            "total_intermediate_image_nnz": total_intermediate_image_nnz,
            "maximum_intermediate_image_nnz": maximum_intermediate_image_nnz,
            "maximum_intermediate_image_absolute_coefficient": (
                maximum_intermediate_image_coefficient
            ),
        },
        "proof_grade": bool(
            len(pivot_physical) == 6_057
            and common_denominator == 3_375
            and int(np.count_nonzero(target_numerator)) == 825
            and not np.any(target_numerator[odd_indices])
        ),
    }


def _assemble_full_target(lower: dict[str, Any], quartic_target: dict[str, Any]) -> dict[str, Any]:
    linear = tuple(lower["linear"]["SU4_invariant_basis"]["target_coordinates"])
    quadratic = tuple(lower["quadratic"]["SU4_invariant_basis"]["target_coordinates"])
    denominators = [
        lower["constant"].denominator,
        *(value.denominator for value in linear),
        *(value.denominator for value in quadratic),
        int(quartic_target["common_denominator"]),
    ]
    common_denominator = math.lcm(*denominators)
    pieces = (
        np.asarray(
            [lower["constant"].numerator * (common_denominator // lower["constant"].denominator)],
            dtype=np.int64,
        ),
        np.asarray(
            [value.numerator * (common_denominator // value.denominator) for value in linear],
            dtype=np.int64,
        ),
        np.asarray(
            [
                value.numerator * (common_denominator // value.denominator)
                for value in quadratic
            ],
            dtype=np.int64,
        ),
        np.zeros(478, dtype=np.int64),
        np.asarray(quartic_target["numerator"], dtype=np.int64)
        * (common_denominator // int(quartic_target["common_denominator"])),
    )
    target = np.concatenate(pieces)
    content = common_denominator
    for value in target:
        content = math.gcd(content, abs(int(value)))
    offsets: dict[str, dict[str, int]] = {}
    start = 0
    names = ("constant", "linear", "quadratic", "cubic", "quartic")
    for name, piece in zip(names, pieces, strict=True):
        stop = start + int(piece.size)
        offsets[name] = {"start_inclusive": start, "stop_exclusive": stop}
        start = stop
    return {
        "grade_order": names,
        "grade_lengths": tuple(int(piece.size) for piece in pieces),
        "grade_offsets": offsets,
        "row_count": int(target.size),
        "common_denominator": common_denominator,
        "numerator": target,
        "numerator_sha256": _int64_array_sha256(target),
        "nonzero_count_by_grade": {
            name: int(np.count_nonzero(piece))
            for name, piece in zip(names, pieces, strict=True)
        },
        "total_nonzero_count": int(np.count_nonzero(target)),
        "maximum_absolute_numerator": int(np.max(np.abs(target), initial=0)),
        "primitive_common_fraction": content == 1,
        "proof_grade": bool(
            tuple(int(piece.size) for piece in pieces) == (1, 4, 45, 478, 6_057)
            and int(target.size) == 6_585
            and common_denominator == 1_728_000
            and content == 1
        ),
    }


def _compute_report() -> dict[str, Any]:
    dependency_bindings = dependency_binding_records()
    actual_dependencies = {
        name: dependency_bindings[name]["portable_sha256"]
        for name in EXPECTED_DEPENDENCY_HASHES
    }
    if actual_dependencies != EXPECTED_DEPENDENCY_HASHES:
        raise ArithmeticError("dependency provenance drifted")
    congruences = _build_congruences()
    lower = _build_lower_target()
    minors = _extremal_minors()
    restrictions, stream = _spectral_restrictions(minors)
    restrictions_purely_real = all(
        not np.any(row["spectral_restriction_imaginary_numerator"])
        for row in restrictions
    )
    coefficient_rows, schur = _raw_schur_coefficients(restrictions)
    quartic_target = _quartic_chart_target(coefficient_rows)
    full_target = _assemble_full_target(lower, quartic_target)
    exact_arithmetic_safety = {
        "storage_dtype": "signed int64",
        "signed_int64_maximum": INT64_MAX,
        "observed_spectral_power_maximum": stream["observed_power_maximum"],
        "observed_spectral_response_maximum": stream["observed_response_maximum"],
        "observed_quartic_image_maximum": quartic_target["stream"][
            "maximum_intermediate_image_absolute_coefficient"
        ],
        "full_target_maximum_absolute_numerator": full_target[
            "maximum_absolute_numerator"
        ],
        "all_recorded_bounds_fit_signed_int64": all(
            int(value) <= INT64_MAX
            for value in (
                stream["observed_power_maximum"],
                stream["observed_response_maximum"],
                quartic_target["stream"][
                    "maximum_intermediate_image_absolute_coefficient"
                ],
                full_target["maximum_absolute_numerator"],
            )
        ),
        "checked_sparse_products_reject_unsafe_int64_bounds": True,
    }
    report = {
        "status": STATUS,
        "overall_state": OVERALL_STATE,
        "model_contract_id": "gauged_u1x_phi17_v20",
        "provenance": {
            "dependency_hash_algorithm": "SHA256 of UTF-8 text after LF normalization",
            "repository_local_dependency_root": ".",
            "all_dependency_files_required_beside_this_module": True,
            "source_module_path_binding": (
                "Every Python source hash is read from "
                "Path(the_actually_imported_module.__file__).resolve(), whose parent "
                "must equal Path(this_module.__file__).resolve().parent. Artifacts obey "
                "the same parent contract; no external shadow can satisfy it."
            ),
            "expected_dependency_hashes": EXPECTED_DEPENDENCY_HASHES,
            "actual_dependency_hashes": actual_dependencies,
            "dependency_file_bindings": dependency_bindings,
            "all_dependency_hashes_match_exact": actual_dependencies
            == EXPECTED_DEPENDENCY_HASHES,
        },
        "scope": EXPECTED_SCOPE,
        "standard_PSD_coordinate_routes": congruences,
        "physical_target": {
            "normalization": lower["normalization"],
            "source_shapes": lower["source_shapes"],
            "constant": lower["constant"],
            "linear": lower["linear"],
            "quadratic": lower["quadratic"],
            "cubic": lower["cubic"],
            "quartic": quartic_target,
            "full_graded_chart": full_target,
            "lower_grade_checks": lower["checks"],
            "lower_grade_proof_grade": lower["proof_grade"],
            "quartic_extremal_family_count": len(restrictions),
            "quartic_extremal_restrictions_purely_real_exact": (
                restrictions_purely_real
            ),
            "quartic_extremal_stream": stream,
            "raw_Schur_reconstruction": schur,
        },
        "exact_arithmetic_safety": exact_arithmetic_safety,
        "claim_boundary": EXPECTED_CLAIM_BOUNDARY,
    }
    report["proof_grade"] = bool(
        congruences["all_22_cones_have_standard_coordinate_routes"]
        and lower["proof_grade"]
        and len(restrictions) == 35
        and restrictions_purely_real
        and schur["block_count"] == 22
        and schur["all_extremal_reconstructions_zero_exact"]
        and quartic_target["proof_grade"]
        and full_target["proof_grade"]
        and exact_arithmetic_safety["all_recorded_bounds_fit_signed_int64"]
        and not any(
            EXPECTED_SCOPE[key]
            for key in (
                "coefficient_map_reparameterized_in_standard_PSD_coordinates",
                "semidefinite_feasibility_solved",
                "exact_primal_PSD_certificate_constructed",
                "exact_dual_Farkas_certificate_constructed",
                "arbitrary_Phi_lower_bound_proved",
                "equality_orbit_classification_proved",
                "full_486_field_Hessian_classification_proved",
                "G3_closed",
            )
        )
    )
    return report


@lru_cache(maxsize=1)
def _cached_report_payload() -> str:
    """Cache only an immutable canonical payload, never a caller-mutable object."""
    return json.dumps(
        _jsonable(_compute_report()),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def build_report() -> dict[str, Any]:
    """Reject the superseded v20 physical-target report entrypoint."""
    raise ArithmeticError(
        "the v20 physical target is rejected and superseded by "
        "corrected_rank1_publication_v21; structural private APIs only"
    )


def build_report_cache_info() -> Any:
    return _cached_report_payload.cache_info()


def clear_build_report_cache() -> None:
    _cached_report_payload.cache_clear()


def validate_report(
    raw_report: Mapping[str, Any], *, check_live_dependencies: bool = False
) -> tuple[bool, tuple[str, ...]]:
    del raw_report, check_live_dependencies
    return False, (
        "the v20 physical target is rejected and superseded by "
        "corrected_rank1_publication_v21",
    )


def _validate_rejected_payload_never_called(
    raw_report: Mapping[str, Any], *, check_live_dependencies: bool = False
) -> tuple[bool, tuple[str, ...]]:
    """Historical validator body retained as unreachable forensic source."""
    report = _jsonable(dict(raw_report))
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(report.get("status") == STATUS, "status drifted")
    require(report.get("overall_state") == OVERALL_STATE, "overall_state drifted")
    require(report.get("model_contract_id") == "gauged_u1x_phi17_v20", "contract drifted")
    provenance = report.get("provenance", {})
    require(
        provenance.get("repository_local_dependency_root") == ".",
        "repository-local dependency root drifted",
    )
    require(
        provenance.get("all_dependency_files_required_beside_this_module") is True,
        "repository-local dependency-parent contract is false",
    )
    require(
        provenance.get("expected_dependency_hashes") == EXPECTED_DEPENDENCY_HASHES,
        "expected dependency hashes drifted",
    )
    require(
        provenance.get("actual_dependency_hashes") == EXPECTED_DEPENDENCY_HASHES,
        "recorded dependency hashes drifted",
    )
    require(
        provenance.get("all_dependency_hashes_match_exact") is True,
        "dependency-match flag is not exact",
    )
    recorded_bindings = provenance.get("dependency_file_bindings", {})
    require(
        set(recorded_bindings) == set(EXPECTED_DEPENDENCY_HASHES),
        "dependency file-binding keys drifted",
    )
    for name, expected_hash in EXPECTED_DEPENDENCY_HASHES.items():
        binding = recorded_bindings.get(name, {})
        if name in IMPORTED_SOURCE_MODULES:
            require(
                binding.get("binding_kind")
                == "Path(imported_module.__file__).resolve()",
                f"{name}: imported-module path binding drifted",
            )
            require(
                binding.get("module_name") == IMPORTED_SOURCE_MODULES[name].__name__,
                f"{name}: imported module name drifted",
            )
        else:
            require(
                binding.get("binding_kind") == "exact_predecessor_artifact",
                f"{name}: artifact binding drifted",
            )
            require(binding.get("module_name") == "", f"{name}: artifact module drifted")
        require(
            binding.get("imported_file_basename") == name,
            f"{name}: bound filename drifted",
        )
        require(
            binding.get("repository_local_path") == name,
            f"{name}: repository-local path drifted",
        )
        require(
            binding.get("required_parent") == ".",
            f"{name}: repository-local parent contract drifted",
        )
        require(
            binding.get("portable_sha256") == expected_hash,
            f"{name}: bound file hash drifted",
        )
    if check_live_dependencies:
        try:
            require(dependency_hashes() == EXPECTED_DEPENDENCY_HASHES, "live dependencies drifted")
            require(
                dependency_binding_records() == recorded_bindings,
                "live imported-module/artifact bindings drifted",
            )
        except (FileNotFoundError, UnicodeError, ArithmeticError, KeyError) as error:
            failures.append(f"live dependency validation failed: {error}")
    require(report.get("scope") == EXPECTED_SCOPE, "scope/claim boundary drifted")
    require(
        report.get("claim_boundary") == _jsonable(EXPECTED_CLAIM_BOUNDARY),
        "textual claim boundary drifted",
    )

    routes = report.get("standard_PSD_coordinate_routes", {})
    real_rows = routes.get("real_type_rows", [])
    complex_rows = routes.get("complex_Hermitian_rows", [])
    require(routes.get("real_type_block_count") == 9, "real-type block count drifted")
    require(len(real_rows) == 9, "real-type row count drifted")
    require(routes.get("complex_Hermitian_block_count") == 13, "complex block count drifted")
    require(len(complex_rows) == 13, "complex row count drifted")
    require(routes.get("standard_real_parameter_count") == 7_979, "real cone dimension drifted")
    require(routes.get("standard_complex_parameter_count") == 11_615, "complex cone dimension drifted")
    require(routes.get("standard_total_parameter_count") == 19_594, "total cone dimension drifted")
    require(
        routes.get("all_22_cones_have_standard_coordinate_routes") is True,
        "standard cone route certificate is false",
    )
    expected_real_shapes = {
        (0, 0, 0): (50, 35, 15, 1),
        (0, 1, 0): (66, 33, 33, 1),
        (0, 2, 0): (43, 26, 17, 4),
        (0, 3, 0): (6, 3, 3, 36),
        (0, 4, 0): (1, 1, 0, 576),
        (1, 0, 1): (71, 25, 46, 1),
        (1, 1, 1): (42, 21, 21, 1),
        (1, 2, 1): (6, 1, 5, 4),
        (2, 0, 2): (9, 8, 1, 16),
    }
    for index, row in enumerate(real_rows):
        representative = tuple(row.get("representative_dynkin", []))
        label = f"real row {index} {representative}"
        require(representative in expected_real_shapes, f"{label}: representative drifted")
        if representative not in expected_real_shapes:
            continue
        multiplicity, plus_dimension, minus_dimension, scale = expected_real_shapes[
            representative
        ]
        b = np.asarray(row.get("augmented_real_structure", []), dtype=object)
        p = np.asarray(row.get("fixed_basis_real_numerator", []), dtype=object)
        q = np.asarray(row.get("fixed_basis_imaginary_numerator", []), dtype=object)
        require(b.shape == (multiplicity, multiplicity), f"{label}: B shape drifted")
        require(p.shape == (multiplicity, plus_dimension), f"{label}: P shape drifted")
        require(q.shape == (multiplicity, minus_dimension), f"{label}: Q shape drifted")
        if b.shape == (multiplicity, multiplicity):
            require(
                np.array_equal(b @ b, np.eye(multiplicity, dtype=object)),
                f"{label}: B^2 != I",
            )
            require(
                row.get("augmented_real_structure_sha256") == _canonical_sha256(b),
                f"{label}: B hash drifted",
            )
        if p.shape == (multiplicity, plus_dimension):
            require(not np.any(b @ p - p), f"{label}: B*P != P")
        if q.shape == (multiplicity, minus_dimension):
            require(not np.any(b @ q + q), f"{label}: B*Q != -Q")
        if p.shape[0] == multiplicity and q.shape[0] == multiplicity:
            require(
                row.get("fixed_basis_sha256") == _canonical_sha256({"P": p, "Q": q}),
                f"{label}: fixed-basis hash drifted",
            )
        require(row.get("augmented_multiplicity") == multiplicity, f"{label}: m drifted")
        require(row.get("plus_eigenspace_dimension") == plus_dimension, f"{label}: plus drifted")
        require(row.get("minus_eigenspace_dimension") == minus_dimension, f"{label}: minus drifted")
        require(row.get("common_component_scale_denominator") == scale, f"{label}: scale drifted")
        require(row.get("fixed_basis_rank_at_first_prime") == multiplicity, f"{label}: rank1 drifted")
        require(row.get("fixed_basis_rank_at_second_prime") == multiplicity, f"{label}: rank2 drifted")
        require(row.get("B_Fbar_equals_F_residual_maximum_absolute_entry") == 0, f"{label}: fixed residual")
        require(row.get("proof_grade") is True, f"{label}: proof flag false")
    counterexample = routes.get("naive_coordinate_counterexample", {})
    require(counterexample.get("failing_block_count") == 4, "naive counterexample count drifted")
    require(
        tuple(tuple(value) for value in counterexample.get("failing_representatives", []))
        == ((0, 1, 0), (0, 2, 0), (1, 0, 1), (1, 1, 1)),
        "naive counterexample representatives drifted",
    )

    physical = report.get("physical_target", {})
    constant = physical.get("constant", {})
    require(constant == {"numerator": 237, "denominator": 200}, "constant target drifted")
    linear = physical.get("linear", {}).get("SU4_invariant_basis", {})
    quadratic = physical.get("quadratic", {}).get("SU4_invariant_basis", {})
    require(linear.get("basis_sha256") == "8b800fb7b46420d25aeb9a3040851ad40133361d030053f13731564f019ec7e9", "linear basis drifted")
    require(linear.get("target_coordinate_sha256") == "d78fe55c0b9e022777546f3e84212b09ac401bedf929170e6c252f4c41d315e6", "linear target drifted")
    require(
        linear.get("target_coordinates")
        == [
            {"numerator": 0, "denominator": 1},
            {"numerator": 0, "denominator": 1},
            {"numerator": -1, "denominator": 10},
            {"numerator": -1, "denominator": 10},
        ],
        "linear target coordinates drifted",
    )
    require(quadratic.get("ordered_basis_dimension") == 45, "quadratic basis dimension drifted")
    require(quadratic.get("ordered_basis_sha256") == "27c0649758c87aa2cbe39ae04596f4bd6df511ba3ca4004013bdcf936599b694", "quadratic basis drifted")
    require(quadratic.get("target_coordinate_nonzero_count") == 17, "quadratic target sparsity drifted")
    require(quadratic.get("target_coordinate_sha256") == "9348d7c109203e80d64dde3e63d006edb439109c70bf812daf2a4cda99a3e3fb", "quadratic target drifted")
    require(
        quadratic.get("target_coordinate_sha256")
        == _canonical_sha256(quadratic.get("target_coordinates", [])),
        "quadratic target-coordinate hash is inconsistent",
    )
    cubic_target = physical.get("cubic", {})
    require(cubic_target.get("row_count") == 478, "cubic target row count drifted")
    require(cubic_target.get("all_target_rows_zero_exact") is True, "cubic target is not zero")
    quartic_target = physical.get("quartic", {})
    quartic_numerator = np.asarray(quartic_target.get("numerator", []), dtype=np.int64)
    require(quartic_target.get("row_count") == 6_057, "quartic target row count drifted")
    require(quartic_numerator.shape == (6_057,), "quartic numerator shape drifted")
    require(quartic_target.get("common_denominator") == 3_375, "quartic denominator drifted")
    require(quartic_target.get("nonzero_count") == 825, "quartic sparsity drifted")
    require(quartic_target.get("all_i_times_anti_real_rows_zero_exact") is True, "quartic anti-real rows drifted")
    require(quartic_target.get("pivot_physical_quartic_coordinates_sha256") == "f33cb0163f3cdc4a3480cb55e09329888c8cf0641cc0acab4cb01f8075058ce4", "quartic chart binding drifted")
    if quartic_numerator.shape == (6_057,):
        require(quartic_target.get("numerator_sha256") == _int64_array_sha256(quartic_numerator), "quartic numerator hash inconsistent")
    require(quartic_target.get("numerator_sha256") == "38476cff340ef8702735d48d7dbdf644ed41f8dc4a359264d33d966f177145ad", "quartic target hash drifted")
    require(quartic_target.get("proof_grade") is True, "quartic target proof flag false")
    require(physical.get("quartic_extremal_family_count") == 35, "extremal family count drifted")
    require(physical.get("quartic_extremal_restrictions_purely_real_exact") is True, "extremal restrictions are not real")
    schur = physical.get("raw_Schur_reconstruction", {})
    require(schur.get("block_count") == 22, "Schur block count drifted")
    require(schur.get("total_nonzero_raw_coefficients") == 4_433, "Schur sparsity drifted")
    require(schur.get("all_extremal_reconstructions_zero_exact") is True, "Schur residual drifted")
    full = physical.get("full_graded_chart", {})
    full_numerator = np.asarray(full.get("numerator", []), dtype=np.int64)
    require(tuple(full.get("grade_lengths", [])) == (1, 4, 45, 478, 6_057), "graded lengths drifted")
    require(full.get("row_count") == 6_585, "full target row count drifted")
    require(full_numerator.shape == (6_585,), "full target shape drifted")
    require(full.get("common_denominator") == 1_728_000, "full target denominator drifted")
    require(full.get("total_nonzero_count") == 845, "full target sparsity drifted")
    require(full.get("primitive_common_fraction") is True, "full target is not primitive")
    if full_numerator.shape == (6_585,):
        require(full.get("numerator_sha256") == _int64_array_sha256(full_numerator), "full target hash inconsistent")
        require(not np.any(full_numerator[50:528]), "full cubic segment is nonzero")
    require(full.get("numerator_sha256") == "e2d9eec1b01b3eeefc4a54d404db93171aa6600ea9ef646a215ab0b5401f7630", "full target hash drifted")
    require(full.get("proof_grade") is True, "full target proof flag false")
    safety = report.get("exact_arithmetic_safety", {})
    require(safety.get("storage_dtype") == "signed int64", "storage dtype drifted")
    require(safety.get("signed_int64_maximum") == INT64_MAX, "int64 bound drifted")
    require(safety.get("all_recorded_bounds_fit_signed_int64") is True, "overflow safety flag false")
    for key in (
        "observed_spectral_power_maximum",
        "observed_spectral_response_maximum",
        "observed_quartic_image_maximum",
        "full_target_maximum_absolute_numerator",
    ):
        value = safety.get(key, INT64_MAX + 1)
        require(isinstance(value, int) and 0 <= value <= INT64_MAX, f"{key} is unsafe")
    require(report.get("proof_grade") is True, "top-level proof_grade is false")
    return not failures, tuple(failures)


def render_markdown(raw_report: Mapping[str, Any]) -> str:
    del raw_report
    raise ArithmeticError(
        "the v20 physical-target renderer is disabled; use the tracked "
        "rejection notice and corrected_rank1_publication_v21"
    )


def _render_rejected_payload_never_called(raw_report: Mapping[str, Any]) -> str:
    """Historical renderer retained as unreachable forensic source."""
    report = _jsonable(dict(raw_report))
    routes = report["standard_PSD_coordinate_routes"]
    target = report["physical_target"]
    full = target["full_graded_chart"]
    lines = [
        "# Exact rank-one SU(4) PSD routes and physical target",
        "",
        f"Status: `{report['status']}`",
        "",
        "This certificate constructs the exact standard-cone coordinate routes for all 22",
        "augmented isotypic blocks and the exact physical right-hand side in the 6,585-row",
        "graded invariant chart. It does not solve the SDP and does not close G3.",
        "",
        "## Standard PSD coordinate routes",
        "",
        "| SU(4) irrep | m | dim(+1) | dim(-1) | component scale | cone |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in routes["real_type_rows"]:
        representative = ",".join(str(value) for value in row["representative_dynkin"])
        lines.append(
            f"| ({representative}) | {row['augmented_multiplicity']} | "
            f"{row['plus_eigenspace_dimension']} | {row['minus_eigenspace_dimension']} | "
            f"{row['common_component_scale_denominator']} | `{row['PSD_cone']}` |"
        )
    lines.extend(
        [
            "",
            f"The 9 real blocks contribute {routes['standard_real_parameter_count']:,} real",
            f"symmetric parameters. The 13 complex blocks contribute",
            f"{routes['standard_complex_parameter_count']:,} Hermitian parameters; total",
            f"{routes['standard_total_parameter_count']:,}.",
            "",
            "For every real block the displayed integer matrices satisfy",
            "`B^2=I`, `B P=P`, `B Q=-Q`; with `F=[P | iQ]`,",
            "`H=F A F^dagger` is an exact cone equivalence from `S_+^m(R)` to the",
            "physical tau-fixed Hermitian cone.",
            "",
            "Raw carrier-copy coordinates are not standard PSD coordinates: `H=I` fails",
            "tau-fixedness in exactly four displayed blocks. This is an explicit",
            "counterexample to the naive coordinate identification.",
            "",
            "## Physical target",
            "",
            "The normalized polynomial is",
            "",
            "`p(z)=A(z)-3/200`, with `z=sqrt(10) Phi`,",
            "",
            "where `A=(N_Phi-1)^2+I54+I4125+9||Cz||^2/400+||Mz-b||^2/5120`.",
            "",
            "| grade | rows | nonzero RHS entries |",
            "|---|---:|---:|",
        ]
    )
    for grade, length in zip(full["grade_order"], full["grade_lengths"], strict=True):
        lines.append(
            f"| {grade} | {length} | {full['nonzero_count_by_grade'][grade]} |"
        )
    lines.extend(
        [
            "",
            f"The primitive full target has denominator `{full['common_denominator']}`,",
            f"{full['total_nonzero_count']} nonzero entries, and numerator SHA-256",
            f"`{full['numerator_sha256']}`.",
            "",
            "The quartic component is streamed exactly from the degree-seven SO(10)",
            "pair-Casimir projector polynomial into the frozen 6,057-row chart. It has",
            f"denominator `{target['quartic']['common_denominator']}`,",
            f"{target['quartic']['nonzero_count']} nonzero entries, and all",
            "i-times-anti-real chart rows vanish exactly. The 478-row cubic RHS is",
            "exactly zero because the explicit physical polynomial has no cubic term.",
            "",
            "## Claim boundary",
            "",
            "Still open: the coefficient matrix in these standard PSD coordinates, SDP",
            "feasibility or an exact dual obstruction, the arbitrary-Phi inequality,",
            "equality-orbit classification, the full 486-field Hessian classification,",
            "and G3 itself.",
            "",
            f"Top-level proof grade: `{str(report['proof_grade']).lower()}`.",
            "",
        ]
    )
    return "\n".join(lines)


def _write_artifacts(report: Mapping[str, Any], output: Path, markdown_output: Path) -> None:
    del report, output, markdown_output
    raise ArithmeticError(
        "writing the rejected v20 physical target is permanently disabled"
    )


def main(argv: list[str] | None = None) -> int:
    del argv
    print(
        "REJECTED: the v20 physical-target generator is disabled and superseded "
        "by corrected_rank1_publication_v21; no files were read or written.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
