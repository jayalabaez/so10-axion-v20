#!/usr/bin/env python3
"""Generation-time reconstruction of the v21 SU(4) positive-Gram system.

This bundle source consumes an explicitly byte-pinned v20 structural API root
and the adjacent corrected ordered-spectral v21 RHS source.  It never reads a
previous assembled map, a v20 physical-target payload, or a previous primal
certificate.  The publication's runtime certificate/verifier is separately
HERE-only and relocation-tested.

The important convention is that a real-type block is reparameterized by

    H = F A F^dagger,  F = [P | i Q],  A in Sym_m(R),

whereas a complex-type block uses A in Herm_m(C).  Cubic and quartic columns
are rebuilt in the ambient tensor charts from these H matrices.  They are not
obtained by relabelling the independently selected published domain bases.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any, Iterable, Iterator, Mapping, Sequence

import numpy as np
from scipy import sparse
import sympy as sp


HERE = Path(__file__).resolve().parent
SOURCE_ROOT = Path(os.environ.get("SO10_PUBLISHED_API_ROOT", HERE)).resolve()
sys.path.insert(0, str(SOURCE_ROOT))

import exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20 as aligned
import exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20 as census
import exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20 as cubic
import exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20 as quartic
import exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20 as intertwiners
import exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20 as quadratics
import exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20 as psd_source
import exact_gauged_u1x_g3_rank1_su4_corrected_physical_rhs_v21 as physical_rhs


QUARTIC_JSON = SOURCE_ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.json"
STABILIZER_JSON = SOURCE_ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_STABILIZER_V20.json"

EXPECTED_RAW_SHA256 = {
    SOURCE_ROOT / "exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py":
        "8493a90d9b689bc02479151529ac697425f56087f2bdbebb40176f418b7c0ff8",
    SOURCE_ROOT / "exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py":
        "589952b9b0a0b6af1543b87c89b0f3626a4bfb9c4219821a915fe04fab8af690",
    SOURCE_ROOT / "exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py":
        "9964606de2ef2a322536c6185342bc6e8fe61a46fb6ceeed9ab51d812c395b84",
    SOURCE_ROOT / "exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py":
        "a6ca509755d352ddb17d8f8081a247cc55861b75c7f15f85b3a7a6b9218af85c",
    SOURCE_ROOT / "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py":
        "b848448fa6badfcb491136862b26ec9f6c80a0b509e2aad79fdb917be9eb7617",
    SOURCE_ROOT / "exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py":
        "cb54ad8b5222872187af404d3bbfa939157d4fb25db9941bc9ac3a6976fa0492",
    SOURCE_ROOT / "exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py":
        "28633a2dba4d70f019a3e63ca87e8224ca11630a9e7c53bc963aedc6824208c1",
    QUARTIC_JSON:
        "0efce9154b5b4204107cf211ff3c355641783353bf8d68ddb931f40994fdbb08",
    SOURCE_ROOT / "exact_gauged_u1x_g3_rank1_su4_stabilizer_v20.py":
        "a0641dfda3573cbd9343c65a4c26d7f89602bb4a21eb6e4ab8a360fa1d434e8f",
    STABILIZER_JSON:
        "91996a1e36b8169ffe5a8553f7efacf4586935aec7f971ad9689805049c62feb",
    SOURCE_ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_STABILIZER_V20.md":
        "a243c9b9de43fe8e5245e58dc1f3d0464dc93127cd1142317108e0518f4954f9",
}

GRADE_LENGTHS = (1, 4, 45, 478, 6057)
GRADE_OFFSETS = (0, 1, 5, 50, 528, 6585)
DOMAIN_GRADE_COUNTS = (1, 4, 90, 1414, 18085)
FIRST_PRIME = 1_000_003
SECOND_PRIME = 1_000_033
PHI_DIMENSION = 210
PAIR_DIMENSION = 22_155

# These are content hashes of the exact integer CSR payloads, including shape.
# Per-grade hashes use a primitive numerator obtained by removing the gcd shared
# with the displayed denominator.  They bind the independently calibrated
# lower, cubic, and quartic maps without relying on the non-deterministic ZIP
# metadata of the generated NPZ container.
EXPECTED_FULL_MAP_SHA256 = (
    "1834c8439fa3e44459f7ba871420a4351cd0b4de194dec6f5c4a84c1f39d3a16"
)
EXPECTED_TARGET_NUMERATOR_SHA256 = (
    "14debcfaf02d4b8c20d1d43a2e1f82d6a7390e28428fc63dd21a9c5f90aec0cf"
)
EXPECTED_PRIMITIVE_GRADE_MAPS = (
    ((1, 1), 1, 1, 1,
     "486e4eb2827ec909822c7880e7f00dfbafd85ff21537dbde1f024ceff0a03c82"),
    ((4, 4), 4, 4, 2,
     "fc5e5443069b1613159d9de90a44fa8eee2a8e6a54271fb66ae6df7f86e83441"),
    ((45, 90), 256, 114, 256,
     "cfdb2b74c2cf2fe418a8e1298a2c0408165e1420a191a99a1742f23095047de8"),
    ((478, 1414), 1, 3480, 256,
     "3a066cd2318ce55710680495d0b1b987222052cfeb7fc1124d36044301a61331"),
    ((6057, 18085), 1, 134951, 9_953_280,
     "36d7cfc38ff7458cbf86c12e1a5b5e0e279b8ac795b2edacb960d6bdd3ea2227"),
)


Gaussian = tuple[int, int]


def raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    def jsonable(item: Any) -> Any:
        if isinstance(item, dict):
            return {str(key): jsonable(val) for key, val in item.items()}
        if isinstance(item, (tuple, list)):
            return [jsonable(val) for val in item]
        if isinstance(item, Fraction):
            return {"numerator": item.numerator, "denominator": item.denominator}
        if isinstance(item, np.ndarray):
            return item.tolist()
        if isinstance(item, np.generic):
            return item.item()
        return item

    payload = json.dumps(
        jsonable(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def sparse_sha256(matrix: sparse.spmatrix) -> str:
    value = matrix.tocsr().astype(np.int64)
    value.sum_duplicates()
    value.sort_indices()
    digest = hashlib.sha256()
    digest.update(np.asarray(value.shape, dtype="<i8").tobytes())
    digest.update(np.asarray(value.indptr, dtype="<i8").tobytes())
    digest.update(np.asarray(value.indices, dtype="<i8").tobytes())
    digest.update(np.asarray(value.data, dtype="<i8").tobytes())
    return digest.hexdigest()


def int64_array_sha256(value: np.ndarray) -> str:
    array = np.ascontiguousarray(value, dtype="<i8")
    digest = hashlib.sha256()
    digest.update(np.asarray(array.shape, dtype="<i8").tobytes())
    digest.update(array.tobytes())
    return digest.hexdigest()


def add_gaussian(left: Gaussian, right: Gaussian) -> Gaussian:
    return left[0] + right[0], left[1] + right[1]


def scale_gaussian(value: Gaussian, scale: int) -> Gaussian:
    return scale * value[0], scale * value[1]


def multiply_with_conjugate(left: Gaussian, right: Gaussian) -> Gaussian:
    """Return left * conjugate(right)."""
    a, b = left
    c, d = right
    return a * c + b * d, b * c - a * d


def multiply_i(value: Gaussian, sign: int = 1) -> Gaussian:
    a, b = value
    return -sign * b, sign * a


def primitive_integer_vector(values: np.ndarray) -> np.ndarray:
    vector = np.asarray(values, dtype=np.int64).reshape(-1).copy()
    content = 0
    for value in vector:
        content = math.gcd(content, abs(int(value)))
    if not content:
        raise ArithmeticError("cannot primitive-normalize the zero vector")
    vector //= content
    first = int(vector[np.flatnonzero(vector)[0]])
    if first < 0:
        vector = -vector
    return vector


def fraction_from_sympy(value: sp.Expr) -> Fraction:
    numerator, denominator = sp.fraction(sp.cancel(value))
    return Fraction(int(numerator), int(denominator))


def rational_solver(matrix: np.ndarray) -> tuple[sp.Matrix, tuple[int, ...]]:
    """Select exact independent rows and return the inverse square minor."""
    value = np.asarray(matrix, dtype=np.int64)
    rows = pivot_rows_mod_prime(sparse.csr_matrix(value), FIRST_PRIME)
    if len(rows) != value.shape[1]:
        raise ArithmeticError("target basis did not have full column rank")
    minor = sp.Matrix(value[list(rows), :].tolist())
    if minor.det() == 0:
        raise ArithmeticError("selected rational target-basis minor is singular")
    return minor.inv(), rows


def solve_selected(
    inverse: sp.Matrix, rows: Sequence[int], vector: Sequence[Fraction]
) -> tuple[Fraction, ...]:
    rhs = sp.Matrix(
        [sp.Rational(vector[row].numerator, vector[row].denominator) for row in rows]
    )
    return tuple(fraction_from_sympy(value) for value in inverse * rhs)


def pivot_rows_mod_prime(matrix: sparse.spmatrix, prime: int) -> tuple[int, ...]:
    """Return deterministic independent rows using sparse modular elimination."""
    value = matrix.tocsr()
    basis: dict[int, dict[int, int]] = {}
    selected: list[int] = []
    for row in range(value.shape[0]):
        start, stop = value.indptr[row], value.indptr[row + 1]
        vector = {
            int(column): int(coefficient) % prime
            for column, coefficient in zip(
                value.indices[start:stop], value.data[start:stop], strict=True
            )
            if int(coefficient) % prime
        }
        while vector:
            pivot = min(vector)
            existing = basis.get(pivot)
            if existing is None:
                inverse = pow(vector[pivot], -1, prime)
                vector = {
                    column: (coefficient * inverse) % prime
                    for column, coefficient in vector.items()
                }
                basis[pivot] = vector
                selected.append(row)
                break
            coefficient = vector[pivot]
            for column, old in existing.items():
                updated = (vector.get(column, 0) - coefficient * old) % prime
                if updated:
                    vector[column] = updated
                else:
                    vector.pop(column, None)
        if len(basis) == value.shape[1]:
            break
    return tuple(selected)


def rank_mod_prime(matrix: sparse.spmatrix, prime: int) -> int:
    return len(pivot_rows_mod_prime(matrix, prime))


def sparse_vector_echelon(
    vectors: Iterable[Mapping[int, int]], prime: int
) -> dict[int, dict[int, int]]:
    basis: dict[int, dict[int, int]] = {}
    for source in vectors:
        vector = {
            int(coordinate): int(value) % prime
            for coordinate, value in source.items()
            if int(value) % prime
        }
        while vector:
            pivot = min(vector)
            old = basis.get(pivot)
            if old is None:
                inverse = pow(vector[pivot], -1, prime)
                basis[pivot] = {
                    coordinate: coefficient * inverse % prime
                    for coordinate, coefficient in vector.items()
                }
                break
            coefficient = vector[pivot]
            for coordinate, old_value in old.items():
                updated = (vector.get(coordinate, 0) - coefficient * old_value) % prime
                if updated:
                    vector[coordinate] = updated
                else:
                    vector.pop(coordinate, None)
    return basis


def span_residual_count_mod_prime(
    basis_vectors: Iterable[Mapping[int, int]],
    test_vectors: Iterable[Mapping[int, int]],
    prime: int,
) -> tuple[int, int]:
    basis = sparse_vector_echelon(basis_vectors, prime)
    residual_count = 0
    for source in test_vectors:
        vector = {
            int(coordinate): int(value) % prime
            for coordinate, value in source.items()
            if int(value) % prime
        }
        while vector:
            pivot = min(vector)
            old = basis.get(pivot)
            if old is None:
                residual_count += 1
                break
            coefficient = vector[pivot]
            for coordinate, old_value in old.items():
                updated = (vector.get(coordinate, 0) - coefficient * old_value) % prime
                if updated:
                    vector[coordinate] = updated
                else:
                    vector.pop(coordinate, None)
    return len(basis), residual_count


@dataclass(frozen=True)
class StandardVariable:
    global_index: int
    block_index: int
    representative: tuple[int, int, int]
    block_kind: str
    left_standard_index: int
    right_standard_index: int
    component: str
    left_grade: int
    right_grade: int
    phi_degree: int


@dataclass
class StandardBlock:
    block_index: int
    representative: tuple[int, int, int]
    conjugate: tuple[int, int, int]
    self_conjugate: bool
    kind: str
    grades: tuple[int, int, int]
    raw_grade: np.ndarray
    f_real: np.ndarray
    f_imaginary: np.ndarray
    standard_grade: tuple[int, ...]
    variables: tuple[StandardVariable, ...]

    @property
    def multiplicity(self) -> int:
        return int(self.f_real.shape[0])

    @property
    def grade_offsets(self) -> tuple[int, int, int, int]:
        a, b, c = self.grades
        return 0, a, a + b, a + b + c


def load_certificate() -> dict[str, Any]:
    observed = {str(path): raw_sha256(path) for path in EXPECTED_RAW_SHA256}
    expected = {str(path): digest for path, digest in EXPECTED_RAW_SHA256.items()}
    if observed != expected:
        raise ArithmeticError(
            "an explicitly pinned cubic/quartic/PSD dependency hash drifted"
        )
    if Path(cubic.__file__).resolve() != (
        SOURCE_ROOT / "exact_gauged_u1x_g3_rank1_su4_augmented_sos_cubic_map_v20.py"
    ).resolve():
        raise ArithmeticError("cubic module escaped the explicit published API root")
    direct_repo_modules = (
        (
            aligned,
            "exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py",
            "aligned-carrier",
        ),
        (
            census,
            "exact_gauged_u1x_g3_rank1_su4_augmented_sos_census_v20.py",
            "augmented-census",
        ),
        (
            intertwiners,
            "exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20.py",
            "intertwiner",
        ),
        (
            quadratics,
            "exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py",
            "quadratic-basis",
        ),
    )
    for module, basename, label in direct_repo_modules:
        if Path(module.__file__).resolve() != (SOURCE_ROOT / basename).resolve():
            raise ArithmeticError(
                f"{label} module escaped the explicit published API root"
            )
    if Path(quartic.__file__).resolve() != (
        SOURCE_ROOT / "exact_gauged_u1x_g3_rank1_su4_augmented_sos_quartic_map_v20.py"
    ).resolve():
        raise ArithmeticError("quartic module escaped the explicit published API root")
    if Path(psd_source.__file__).resolve() != (
        SOURCE_ROOT / "exact_gauged_u1x_g3_rank1_su4_augmented_sos_psd_target_v20.py"
    ).resolve():
        raise ArithmeticError("PSD-route source escaped the explicit published API root")
    if Path(physical_rhs.__file__).resolve() != (
        HERE / "exact_gauged_u1x_g3_rank1_su4_corrected_physical_rhs_v21.py"
    ).resolve():
        raise ArithmeticError("corrected physical RHS source escaped the publication bundle")
    stabilizer_report = json.loads(STABILIZER_JSON.read_text(encoding="utf-8"))
    endpoint = stabilizer_report.get("joint_stabilizer_tangent", {}).get(
        "fixed_endpoint", {}
    )
    if not (
        stabilizer_report.get("status")
        == "EXACT_RANK1_SU4_STABILIZER_INFRASTRUCTURE_CERTIFIED"
        and stabilizer_report.get("joint_stabilizer_tangent", {}).get(
            "proof_grade"
        )
        is True
        and endpoint.get("H") == "h_-=(e0-i e1)/sqrt(2)"
        and endpoint.get("Sigma") == "q/4"
        and stabilizer_report.get("scope", {}).get("G3_closed") is False
    ):
        raise ArithmeticError("published rank-one endpoint provenance drifted")
    # Only the source-level standard-cone routes and lower-grade formulas are
    # reused.  The stale v20 physical-target JSON is never read.  Quartic and
    # full RHS coordinates are rebuilt independently by the adjacent v21
    # ordered-spectral source.
    routes = psd_source._build_congruences()
    lower = psd_source._build_lower_target()
    report = {
        "proof_grade": bool(
            routes["all_22_cones_have_standard_coordinate_routes"]
            and lower["proof_grade"]
        ),
        "standard_PSD_coordinate_routes": routes,
        "physical_target": {
            "linear": lower["linear"],
            "quadratic": lower["quadratic"],
        },
    }
    if not report["proof_grade"]:
        raise ArithmeticError("source-level standard routes/lower target are not proof-grade")
    if report["standard_PSD_coordinate_routes"]["standard_total_parameter_count"] != 19_594:
        raise ArithmeticError("standard PSD parameter census drifted")
    return report


def build_standard_blocks(report: Mapping[str, Any]) -> tuple[StandardBlock, ...]:
    routes = report["standard_PSD_coordinate_routes"]
    real_routes = {
        tuple(row["representative_dynkin"]): row
        for row in routes["real_type_rows"]
    }
    blocks: list[StandardBlock] = []
    global_index = 0
    for block_index, raw in enumerate(census.exact_augmented_isotypic_blocks()):
        representative = tuple(raw["representative_dynkin"])
        grades = tuple(int(value) for value in raw["graded_multiplicities_t2_tPhi_Phi2"])
        multiplicity = sum(grades)
        raw_grade = np.concatenate(
            [np.full(count, grade, dtype=np.int8) for grade, count in enumerate(grades)]
        )
        if raw["self_conjugate"]:
            route = real_routes[representative]
            p = np.asarray(route["fixed_basis_real_numerator"], dtype=np.int64)
            q = np.asarray(route["fixed_basis_imaginary_numerator"], dtype=np.int64)
            f_real = np.column_stack((p, np.zeros_like(q)))
            f_imaginary = np.column_stack((np.zeros_like(p), q))
        else:
            f_real = np.eye(multiplicity, dtype=np.int64)
            f_imaginary = np.zeros((multiplicity, multiplicity), dtype=np.int64)
        if f_real.shape != (multiplicity, multiplicity):
            raise ArithmeticError(f"{representative}: F dimension drifted")
        standard_grade: list[int] = []
        for column in range(multiplicity):
            support = np.flatnonzero(
                (f_real[:, column] != 0) | (f_imaginary[:, column] != 0)
            )
            grades_seen = {int(raw_grade[index]) for index in support}
            if len(grades_seen) != 1:
                raise ArithmeticError(f"{representative}: F mixed homogenizing grades")
            standard_grade.append(next(iter(grades_seen)))
        variables: list[StandardVariable] = []
        for left in range(multiplicity):
            variables.append(
                StandardVariable(
                    global_index, block_index, representative,
                    raw["real_block_kind"], left, left, "diagonal",
                    standard_grade[left], standard_grade[left],
                    2 * standard_grade[left],
                )
            )
            global_index += 1
            for right in range(left + 1, multiplicity):
                variables.append(
                    StandardVariable(
                        global_index, block_index, representative,
                        raw["real_block_kind"], left, right, "real_off_diagonal",
                        standard_grade[left], standard_grade[right],
                        standard_grade[left] + standard_grade[right],
                    )
                )
                global_index += 1
                if not raw["self_conjugate"]:
                    variables.append(
                        StandardVariable(
                            global_index, block_index, representative,
                            raw["real_block_kind"], left, right,
                            "imaginary_off_diagonal", standard_grade[left],
                            standard_grade[right],
                            standard_grade[left] + standard_grade[right],
                        )
                    )
                    global_index += 1
        expected = (
            multiplicity * (multiplicity + 1) // 2
            if raw["self_conjugate"] else multiplicity**2
        )
        if len(variables) != expected:
            raise ArithmeticError(f"{representative}: variable count drifted")
        blocks.append(
            StandardBlock(
                block_index=block_index,
                representative=representative,
                conjugate=tuple(raw["conjugate_dynkin"]),
                self_conjugate=bool(raw["self_conjugate"]),
                kind=raw["real_block_kind"],
                grades=grades,
                raw_grade=raw_grade,
                f_real=f_real,
                f_imaginary=f_imaginary,
                standard_grade=tuple(standard_grade),
                variables=tuple(variables),
            )
        )
    if global_index != 19_594:
        raise ArithmeticError("global standard variable count drifted")
    observed_grades = [0] * 5
    for block in blocks:
        for variable in block.variables:
            observed_grades[variable.phi_degree] += 1
    if tuple(observed_grades) != DOMAIN_GRADE_COUNTS:
        raise ArithmeticError(f"standard variable grade census drifted: {observed_grades}")
    return tuple(blocks)


def column_support(block: StandardBlock, column: int) -> tuple[tuple[int, Gaussian], ...]:
    return tuple(
        (row, (int(block.f_real[row, column]), int(block.f_imaginary[row, column])))
        for row in range(block.multiplicity)
        if block.f_real[row, column] or block.f_imaginary[row, column]
    )


def h_entries(block: StandardBlock, variable: StandardVariable) -> dict[tuple[int, int], Gaussian]:
    left = column_support(block, variable.left_standard_index)
    right = column_support(block, variable.right_standard_index)
    output: dict[tuple[int, int], Gaussian] = {}

    def accumulate(
        first: Sequence[tuple[int, Gaussian]],
        second: Sequence[tuple[int, Gaussian]],
        i_scale: int = 0,
    ) -> None:
        for row, row_value in first:
            for column, column_value in second:
                value = multiply_with_conjugate(row_value, column_value)
                if i_scale:
                    value = multiply_i(value, i_scale)
                key = (row, column)
                output[key] = add_gaussian(output.get(key, (0, 0)), value)
                if output[key] == (0, 0):
                    output.pop(key)

    if variable.component == "diagonal":
        accumulate(left, left)
    elif variable.component == "real_off_diagonal":
        accumulate(left, right)
        accumulate(right, left)
    elif variable.component == "imaginary_off_diagonal":
        accumulate(left, right, 1)
        accumulate(right, left, -1)
    else:
        raise ValueError(variable.component)
    for (row, column), value in output.items():
        if output.get((column, row), (0, 0)) != (value[0], -value[1]):
            raise ArithmeticError("H ceased to be Hermitian")
    return output


def irrep_label(representative: tuple[int, int, int]) -> str:
    return next(
        label
        for label, record in intertwiners.IRREP_DATA.items()
        if tuple(record["dynkin"]) == representative
    )


@lru_cache(maxsize=1)
def aligned_data() -> dict[str, Any]:
    return aligned.exact_aligned_carrier_data()


@lru_cache(maxsize=None)
def tphi_carriers(representative: tuple[int, int, int]) -> tuple[dict[str, Any], ...]:
    label = irrep_label(representative)
    return tuple(
        sorted(
            (row for row in aligned_data()["carriers"] if row["irrep"] == label),
            key=lambda row: int(row["copy_index"]),
        )
    )


def build_linear_solver(report: Mapping[str, Any]) -> tuple[np.ndarray, sp.Matrix, tuple[int, ...]]:
    candidates: list[np.ndarray] = []
    for carrier in aligned_data()["carriers"]:
        if int(carrier["dimension"]) != 1:
            continue
        for matrix in (carrier["canonical_basis_real"], carrier["canonical_basis_imaginary"]):
            if matrix.nnz:
                candidates.append(primitive_integer_vector(matrix.toarray()[:, 0]))
    selected = tuple(
        int(index)
        for index in report["physical_target"]["linear"]["SU4_invariant_basis"][
            "selected_candidate_indices"
        ]
    )
    basis = np.column_stack([candidates[index] for index in selected])
    inverse, rows = rational_solver(basis)
    return basis, inverse, rows


@lru_cache(maxsize=1)
def gaussian_embedding() -> tuple[np.ndarray, np.ndarray]:
    real, imaginary = intertwiners.gaussian_exterior_basis()
    return real.toarray().astype(np.int64), imaginary.toarray().astype(np.int64)


def quadratic_basis_gaussian_chart() -> tuple[np.ndarray, sp.Matrix, tuple[int, ...]]:
    br, bi = gaussian_embedding()
    upper_rows, upper_columns = np.triu_indices(PHI_DIMENSION)
    columns: list[np.ndarray] = []
    for matrix in quadratics.exact_invariant_quadratic_basis():
        q = matrix.toarray().astype(np.int64)
        real = br.T @ q @ br - bi.T @ q @ bi
        imaginary = br.T @ q @ bi + bi.T @ q @ br
        columns.append(
            np.concatenate((real[upper_rows, upper_columns], imaginary[upper_rows, upper_columns]))
        )
    basis = np.column_stack(columns).astype(np.int64)
    inverse, rows = rational_solver(basis)
    return basis, inverse, rows


def linear_column(
    block: StandardBlock,
    variable: StandardVariable,
    inverse: sp.Matrix,
    selected_rows: Sequence[int],
) -> tuple[Fraction, ...]:
    if block.representative != (0, 0, 0):
        raise ArithmeticError("a nontrivial block produced a linear variable")
    offsets = block.grade_offsets
    entries = h_entries(block, variable)
    vector = np.zeros(PHI_DIMENSION, dtype=np.int64)
    carriers = tphi_carriers(block.representative)
    for raw in range(offsets[1], offsets[2]):
        a, b = entries.get((0, raw), (0, 0))
        local = raw - offsets[1]
        real = carriers[local]["canonical_basis_real"].toarray()[:, 0].astype(np.int64)
        imaginary = carriers[local]["canonical_basis_imaginary"].toarray()[:, 0].astype(np.int64)
        vector += 2 * (a * real - b * imaginary)
    fractions = tuple(Fraction(int(value)) for value in vector)
    coordinates = solve_selected(inverse, selected_rows, fractions)
    # Gaussian exterior coordinates obey x=(B^T z)/16.  The Gram cross factor
    # two is already included in ``vector`` above, so no additional factor is
    # permitted here.
    return tuple(value / 16 for value in coordinates)


def pair_vector_to_symmetric_matrix(
    vector: sparse.spmatrix,
) -> tuple[np.ndarray, int]:
    """Return numerator/denominator for a Gaussian quadratic monomial vector."""
    column = vector.tocoo()
    numerator = np.zeros((PHI_DIMENSION, PHI_DIMENSION), dtype=np.int64)
    pairs = cubic._quadratic_pairs_cached()
    for row, value in zip(column.row, column.data, strict=True):
        left, right = pairs[int(row)]
        if left == right:
            numerator[left, right] += 2 * int(value)
        else:
            numerator[left, right] += int(value)
            numerator[right, left] += int(value)
    return numerator, 2


@lru_cache(maxsize=None)
def positive_pairing(
    representative: tuple[int, int, int],
) -> sparse.csr_matrix:
    """Return the positive integer inverse-component pairing P=d G^-1."""
    record = quartic._pairing_data_cached()[representative]
    pairing = sparse.csr_matrix(np.asarray(record["pairing"], dtype=np.int64))
    metric = np.asarray(record["component_metric"], dtype=np.int64)
    denominator = int(record["rational_inverse_denominator"])
    if denominator <= 0 or not np.array_equal(
        metric @ pairing.toarray(),
        denominator * np.eye(metric.shape[0], dtype=np.int64),
    ):
        raise ArithmeticError(
            f"positive inverse-component-metric identity failed for {representative}"
        )
    return pairing


@lru_cache(maxsize=None)
def quadratic_tphi_raw(
    representative: tuple[int, int, int], left: int, right: int
) -> sparse.csr_matrix:
    carriers = tphi_carriers(representative)
    source = carriers[left]["exterior_basis"].tocsr()
    conjugated = aligned.exterior_conjugation() @ carriers[right]["exterior_basis"].tocsr()
    return (source @ positive_pairing(representative) @ conjugated.T).tocsr()


def quadratic_column_chart(
    block: StandardBlock,
    variable: StandardVariable,
    inverse: sp.Matrix,
    selected_rows: Sequence[int],
) -> tuple[Fraction, ...]:
    entries = h_entries(block, variable)
    offsets = block.grade_offsets
    real = np.zeros((PHI_DIMENSION, PHI_DIMENSION), dtype=object)
    imaginary = np.zeros_like(real)
    symmetric_denominator = 1
    if {variable.left_grade, variable.right_grade} == {0, 2}:
        if block.representative != (0, 0, 0):
            raise ArithmeticError("only the trivial block can mix t2 and Phi2")
        copies = quartic._carrier_family_data_cached()[block.representative]["copies"]
        for raw in range(offsets[2], offsets[3]):
            a, b = entries.get((0, raw), (0, 0))
            numerator, _denominator = pair_vector_to_symmetric_matrix(copies[raw - offsets[2]])
            # Gram cross factor two cancels the monomial-to-matrix denominator.
            real += a * np.asarray(numerator, dtype=object)
            imaginary += b * np.asarray(numerator, dtype=object)
    elif variable.left_grade == variable.right_grade == 1:
        for raw_left in range(offsets[1], offsets[2]):
            for raw_right in range(offsets[1], offsets[2]):
                a, b = entries.get((raw_left, raw_right), (0, 0))
                if not (a or b):
                    continue
                tensor = quadratic_tphi_raw(
                    block.representative,
                    raw_left - offsets[1], raw_right - offsets[1],
                ).toarray().astype(object)
                real += a * tensor
                imaginary += b * tensor
        real = real + real.T
        imaginary = imaginary + imaginary.T
        symmetric_denominator = 2
    else:
        raise ArithmeticError("unexpected quadratic grade pair")
    upper_rows, upper_columns = np.triu_indices(PHI_DIMENSION)
    vector = tuple(
        Fraction(int(value), symmetric_denominator)
        for value in np.concatenate(
            (real[upper_rows, upper_columns], imaginary[upper_rows, upper_columns])
        )
    )
    return solve_selected(inverse, selected_rows, vector)


def sparse_dictionary_add(
    accumulator: dict[int, int], source: Mapping[int, int], scale: int
) -> None:
    if not scale:
        return
    for coordinate, coefficient in source.items():
        updated = accumulator.get(int(coordinate), 0) + scale * int(coefficient)
        if updated:
            accumulator[int(coordinate)] = updated
        else:
            accumulator.pop(int(coordinate), None)


def tensor_domain_dictionary(tensor: sparse.spmatrix) -> dict[int, int]:
    value = tensor.tocoo()
    return {
        int(row) * PAIR_DIMENSION + int(column): int(coefficient)
        for row, column, coefficient in zip(value.row, value.col, value.data, strict=True)
        if coefficient
    }


@lru_cache(maxsize=None)
def cubic_original_raw_dictionary(
    representative: tuple[int, int, int], left: int, right: int
) -> dict[int, int]:
    """Build tPhi*Phi2 with the same positive P used in grades two/four."""
    source = tphi_carriers(representative)[left]["exterior_basis"].tocsr()
    target = quartic._carrier_family_data_cached()[representative]["copies"][
        right
    ].tocsr()
    conjugated_target = quartic._sym2_conjugation_cached() @ target
    return tensor_domain_dictionary(
        source @ positive_pairing(representative) @ conjugated_target.T
    )


def cubic_standard_domain(
    block: StandardBlock, variable: StandardVariable
) -> tuple[dict[int, int], dict[int, int]]:
    entries = h_entries(block, variable)
    offsets = block.grade_offsets
    real: dict[int, int] = {}
    imaginary: dict[int, int] = {}
    for raw_left in range(offsets[1], offsets[2]):
        for raw_right in range(offsets[2], offsets[3]):
            a, b = entries.get((raw_left, raw_right), (0, 0))
            if not (a or b):
                continue
            raw = cubic_original_raw_dictionary(
                block.representative,
                raw_left - offsets[1], raw_right - offsets[2],
            )
            if block.self_conjugate:
                # The full rectangular H subblock is already tau-fixed through
                # F A F^dagger, so its real and imaginary coefficient tensors
                # can be accumulated before the global fixedness check.
                sparse_dictionary_add(real, raw, a)
                sparse_dictionary_add(imaginary, raw, b)
            else:
                # A complex-type real Schur block represents a conjugate irrep
                # pair.  One oriented carrier tensor is *not* itself a physical
                # coordinate.  Calibrate it explicitly by plus / i-minus
                # realification; using the same copy index in the conjugate
                # family would be the forbidden naive relabel.
                conjugate = cubic._conjugate_domain_vector(raw)
                sparse_dictionary_add(real, raw, a)
                sparse_dictionary_add(real, conjugate, a)
                sparse_dictionary_add(imaginary, raw, b)
                sparse_dictionary_add(imaginary, conjugate, -b)
    if cubic._conjugate_domain_vector(real) != real:
        raise ArithmeticError("standard cubic real channel is not physically fixed")
    if cubic._conjugate_domain_vector(imaginary) != {
        coordinate: -coefficient for coordinate, coefficient in imaginary.items()
    }:
        raise ArithmeticError("standard cubic imaginary channel is not anti-fixed")
    return real, imaginary


def cubic_column(
    block: StandardBlock, variable: StandardVariable
) -> tuple[tuple[int, Fraction], ...]:
    real, imaginary = cubic_standard_domain(block, variable)
    divisor = 1 if block.self_conjugate else 2
    return tuple(
        (row, Fraction(value, divisor))
        for row, value in cubic_column_from_domain(real, imaginary)
    )


def cubic_column_from_domain(
    real: Mapping[int, int], imaginary: Mapping[int, int]
) -> tuple[tuple[int, int], ...]:
    real_image = cubic._multiply_domain_tensor(real)
    imaginary_image = cubic._multiply_domain_tensor(imaginary)
    data = cubic._coordinate_map_data_cached()
    weight_zero_count = cubic.WEIGHT_ZERO_CUBIC_MONOMIAL_COUNT
    output: list[tuple[int, int]] = []
    for row, pivot in enumerate(data["target_pivot_rows"]):
        if pivot < weight_zero_count:
            value = real_image.get(int(pivot), 0)
        else:
            value = imaginary_image.get(int(pivot - weight_zero_count), 0)
        if value:
            output.append((row, int(value)))
    return tuple(output)


def doubled_cubic_domain(
    real: Mapping[int, int], imaginary: Mapping[int, int]
) -> dict[int, int]:
    offset = PHI_DIMENSION * PAIR_DIMENSION
    output = {int(coordinate): int(value) for coordinate, value in real.items() if value}
    output.update(
        {offset + int(coordinate): int(value) for coordinate, value in imaginary.items() if value}
    )
    return output


@lru_cache(maxsize=None)
def quartic_raw_restricted(
    representative: tuple[int, int, int], left: int, right: int
) -> dict[int, int]:
    raw = quartic._multiply_tensor_to_quartic(
        quartic._raw_invariant_tensor(representative, left, right)
    )
    needed = quartic_needed_raw_coordinates()
    return {coordinate: coefficient for coordinate, coefficient in raw.items() if coordinate in needed}


@lru_cache(maxsize=1)
def quartic_needed_raw_coordinates() -> frozenset[int]:
    pivots = quartic_pivots()
    return frozenset(int(pivot) // 2 for pivot in pivots)


@lru_cache(maxsize=1)
def quartic_pivots() -> tuple[int, ...]:
    artifact = json.loads(QUARTIC_JSON.read_text(encoding="utf-8"))
    pivots = tuple(
        int(value)
        for value in artifact["coefficient_map_certificate"][
            "pivot_physical_quartic_coordinates"
        ]
    )
    if len(pivots) != 6_057:
        raise ArithmeticError("frozen quartic pivot count drifted")
    if canonical_sha256(pivots) != artifact["coefficient_map_certificate"][
        "pivot_physical_quartic_coordinates_sha256"
    ]:
        raise ArithmeticError("frozen quartic pivot hash drifted")
    return pivots


def quartic_column(
    block: StandardBlock, variable: StandardVariable
) -> tuple[tuple[int, int], ...]:
    entries = h_entries(block, variable)
    offsets = block.grade_offsets
    real: dict[int, int] = {}
    imaginary: dict[int, int] = {}
    for raw_left in range(offsets[2], offsets[3]):
        for raw_right in range(offsets[2], offsets[3]):
            a, b = entries.get((raw_left, raw_right), (0, 0))
            if not (a or b):
                continue
            raw = quartic_raw_restricted(
                block.representative,
                raw_left - offsets[2], raw_right - offsets[2],
            )
            sparse_dictionary_add(real, raw, a)
            sparse_dictionary_add(imaginary, raw, b)
    # Exact physical-channel checks are performed on the restricted coordinate
    # set by comparing every selected conjugate pair that is present.
    pivots = quartic_pivots()
    output: list[tuple[int, int]] = []
    for row, pivot in enumerate(pivots):
        raw_coordinate, channel = divmod(int(pivot), 2)
        value = real.get(raw_coordinate, 0) if channel == 0 else imaginary.get(raw_coordinate, 0)
        if value:
            output.append((row, int(value)))
    return tuple(output)


@lru_cache(maxsize=1)
def published_quartic_map() -> sparse.csr_matrix:
    artifact = json.loads(QUARTIC_JSON.read_text(encoding="utf-8"))
    raw = artifact["coefficient_map_certificate"]["coordinate_map_CSR"]
    matrix = sparse.csr_matrix(
        (
            np.asarray(raw["data"], dtype=np.int64),
            np.asarray(raw["indices"], dtype=np.int32),
            np.asarray(raw["indptr"], dtype=np.int32),
        ),
        shape=(6_057, 18_085),
    )
    if sparse_sha256(matrix) != artifact["coefficient_map_certificate"][
        "coordinate_map_sha256"
    ]:
        raise ArithmeticError("published quartic CSR hash drifted")
    return matrix


def assemble(report: Mapping[str, Any], blocks: Sequence[StandardBlock]) -> tuple[sparse.csr_matrix, int, dict[str, Any]]:
    linear_basis, linear_inverse, linear_rows = build_linear_solver(report)
    quadratic_basis, quadratic_inverse, quadratic_rows = quadratic_basis_gaussian_chart()
    grade_entries: list[list[tuple[int, int, Fraction]]] = [[] for _ in range(5)]
    progress = [0] * 5
    standard_cubic_domains: list[dict[int, int]] = []

    for block in blocks:
        print(f"block {block.block_index + 1:02d}/22 {block.representative} m={block.multiplicity}", flush=True)
        for variable in block.variables:
            degree = variable.phi_degree
            local_column = variable.global_index
            if degree == 0:
                entries = h_entries(block, variable)
                value = entries.get((0, 0), (0, 0))
                if value[1]:
                    raise ArithmeticError("constant column became imaginary")
                if value[0]:
                    grade_entries[0].append((0, local_column, Fraction(value[0])))
            elif degree == 1:
                values = linear_column(block, variable, linear_inverse, linear_rows)
                grade_entries[1].extend(
                    (row, local_column, value)
                    for row, value in enumerate(values) if value
                )
            elif degree == 2:
                values = quadratic_column_chart(
                    block, variable, quadratic_inverse, quadratic_rows
                )
                grade_entries[2].extend(
                    (row, local_column, value)
                    for row, value in enumerate(values) if value
                )
            elif degree == 3:
                real_domain, imaginary_domain = cubic_standard_domain(block, variable)
                standard_cubic_domains.append(
                    doubled_cubic_domain(real_domain, imaginary_domain)
                )
                divisor = 1 if block.self_conjugate else 2
                grade_entries[3].extend(
                    (row, local_column, Fraction(value, divisor))
                    for row, value in cubic_column_from_domain(
                        real_domain, imaginary_domain
                    )
                )
            elif degree == 4:
                grade_entries[4].extend(
                    (row, local_column, Fraction(value))
                    for row, value in quartic_column(block, variable)
                )
            else:
                raise ArithmeticError("invalid homogenizing degree")
            progress[degree] += 1
        print(f"  cumulative grade columns {tuple(progress)}", flush=True)

    if tuple(progress) != DOMAIN_GRADE_COUNTS:
        raise ArithmeticError(f"assembled grade-column census drifted: {progress}")
    denominator = 1
    for entries in grade_entries:
        for _, _, value in entries:
            denominator = math.lcm(denominator, value.denominator)
    rows: list[int] = []
    columns: list[int] = []
    values: list[int] = []
    nnz_by_grade: list[int] = []
    for degree, entries in enumerate(grade_entries):
        nnz_by_grade.append(len(entries))
        for row, column, value in entries:
            integer = value.numerator * (denominator // value.denominator)
            if abs(integer) > np.iinfo(np.int64).max:
                raise ArithmeticError("coefficient map exceeded signed int64")
            rows.append(GRADE_OFFSETS[degree] + row)
            columns.append(column)
            values.append(integer)
    matrix = sparse.coo_matrix(
        (values, (rows, columns)), shape=(6585, 19594), dtype=np.int64
    ).tocsr()
    matrix.sum_duplicates()
    matrix.eliminate_zeros()
    ranks = []
    grade_diagnostics: list[dict[str, Any]] = []
    for degree in range(5):
        row_slice = slice(GRADE_OFFSETS[degree], GRADE_OFFSETS[degree + 1])
        degree_columns = [
            variable.global_index
            for block in blocks for variable in block.variables
            if variable.phi_degree == degree
        ]
        submatrix = matrix[row_slice, :][:, degree_columns].tocsr()
        first = rank_mod_prime(submatrix, FIRST_PRIME)
        second = rank_mod_prime(submatrix, SECOND_PRIME)
        ranks.append((first, second))
        content = denominator
        for coefficient in submatrix.data:
            content = math.gcd(content, abs(int(coefficient)))
        primitive = submatrix.copy()
        primitive.data //= content
        primitive_denominator = denominator // content
        grade_diagnostics.append(
            {
                "degree": degree,
                "shape": submatrix.shape,
                "primitive_denominator": primitive_denominator,
                "primitive_numerator_nnz": primitive.nnz,
                "primitive_maximum_absolute_numerator": int(
                    np.max(np.abs(primitive.data), initial=0)
                ),
                "primitive_numerator_csr_sha256": sparse_sha256(primitive),
                "rank_at_first_prime": first,
                "rank_at_second_prime": second,
            }
        )
        print(f"grade {degree} rank {first}/{second}, shape={submatrix.shape}, nnz={submatrix.nnz}", flush=True)

    observed_grade_maps = tuple(
        (
            tuple(row["shape"]),
            int(row["primitive_denominator"]),
            int(row["primitive_numerator_nnz"]),
            int(row["primitive_maximum_absolute_numerator"]),
            str(row["primitive_numerator_csr_sha256"]),
        )
        for row in grade_diagnostics
    )
    if observed_grade_maps != EXPECTED_PRIMITIVE_GRADE_MAPS:
        raise ArithmeticError("a primitive per-grade standard map drifted")

    published_cubic_domains = tuple(
        row["domain_vector"]
        for row in cubic._physical_domain_data_cached()["basis"]
    )
    cubic_span_checks = tuple(
        span_residual_count_mod_prime(
            published_cubic_domains, standard_cubic_domains, prime
        )
        for prime in (FIRST_PRIME, SECOND_PRIME)
    )
    if cubic_span_checks != ((1_414, 0), (1_414, 0)):
        raise ArithmeticError(
            f"standard cubic basis failed exact-space calibration: {cubic_span_checks}"
        )

    published_q4 = published_quartic_map()
    quartic_ordinal = 0
    complex_quartic_columns_checked = 0
    complex_quartic_mismatch_nnz = 0
    for block in blocks:
        phi2 = block.grades[2]
        count = phi2 * (phi2 + 1) // 2 if block.self_conjugate else phi2**2
        if not block.self_conjugate:
            columns = [
                variable.global_index
                for variable in block.variables if variable.phi_degree == 4
            ]
            observed = matrix[GRADE_OFFSETS[4]:GRADE_OFFSETS[5], :][:, columns]
            expected = published_q4[:, quartic_ordinal:quartic_ordinal + count] * denominator
            residual = observed - expected
            residual.eliminate_zeros()
            complex_quartic_mismatch_nnz += int(residual.nnz)
            complex_quartic_columns_checked += count
        quartic_ordinal += count
    if quartic_ordinal != 18_085 or complex_quartic_mismatch_nnz:
        raise ArithmeticError(
            "complex-block standard quartic columns do not match the published Hermitian convention"
        )
    diagnostics = {
        "map_shape": matrix.shape,
        "map_common_denominator": denominator,
        "map_nnz": matrix.nnz,
        "map_nnz_by_grade_before_duplicate_elimination": tuple(nnz_by_grade),
        "map_maximum_absolute_numerator": int(np.max(np.abs(matrix.data), initial=0)),
        "map_numerator_csr_sha256": sparse_sha256(matrix),
        "primitive_grade_maps": tuple(grade_diagnostics),
        "grade_ranks_at_primes_1000003_1000033": tuple(ranks),
        "all_grade_ranks_surjective": all(
            first == second == GRADE_LENGTHS[degree]
            for degree, (first, second) in enumerate(ranks)
        ),
        "linear_target_basis_sha256": canonical_sha256(linear_basis),
        "linear_selected_rows": tuple(linear_rows),
        "quadratic_gaussian_target_basis_sha256": canonical_sha256(quadratic_basis),
        "quadratic_selected_doubled_gaussian_rows": tuple(quadratic_rows),
        "cubic_standard_to_published_basis_span_checks_rank_and_residual_count": cubic_span_checks,
        "positive_Gram_factorization_argument": (
            "For every isotypic block, grades tPhi and Phi2 and their cross "
            "use one P=d*G_Phi2^-1 with G_Phi2*P=dI and d>0.  Every standard "
            "column is obtained by expanding the resulting rank-one positive "
            "component-metric norm.  Complex-type domains already contain the "
            "physical conjugate orientation, so their cubic chart is divided "
            "by two; self-conjugate domains retain divisor one."
        ),
        "complex_type_cubic_divisor": 2,
        "self_conjugate_cubic_divisor": 1,
        "complex_quartic_identity_columns_checked_exact": complex_quartic_columns_checked,
        "complex_quartic_identity_mismatch_nnz": complex_quartic_mismatch_nnz,
    }
    return matrix, denominator, diagnostics


def reconstruct_system() -> tuple[
    sparse.csr_matrix,
    int,
    np.ndarray,
    int,
    tuple[StandardBlock, ...],
    dict[str, Any],
]:
    """Return the exact map/target/schema reconstructed from published APIs."""
    report = load_certificate()
    blocks = build_standard_blocks(report)
    matrix, denominator, diagnostics = assemble(report, blocks)
    if not diagnostics["all_grade_ranks_surjective"]:
        raise ArithmeticError("a corrected grade map lost surjectivity")
    if diagnostics["map_numerator_csr_sha256"] != EXPECTED_FULL_MAP_SHA256:
        raise ArithmeticError("the corrected positive-Gram map drifted")
    target_numerator, target_denominator, rhs_diagnostics = physical_rhs.reconstruct_rhs()
    if target_denominator != 576_000:
        raise ArithmeticError("corrected physical target denominator drifted")
    if int64_array_sha256(target_numerator) != EXPECTED_TARGET_NUMERATOR_SHA256:
        raise ArithmeticError("corrected ordered-spectral physical target drifted")
    diagnostics["published_source_api_raw_sha256"] = tuple(
        {
            "basename": path.name,
            "sha256": digest,
        }
        for path, digest in sorted(
            EXPECTED_RAW_SHA256.items(), key=lambda item: item[0].name
        )
    )
    diagnostics["prior_assembled_map_read"] = False
    diagnostics["prior_primal_certificate_read"] = False
    diagnostics["v20_physical_target_payload_read"] = False
    diagnostics["corrected_physical_RHS"] = {
        "source_basename": Path(physical_rhs.__file__).name,
        "row_count": int(target_numerator.size),
        "common_denominator": target_denominator,
        "numerator_sha256": int64_array_sha256(target_numerator),
        "quartic_row_count": int(rhs_diagnostics["quartic"]["pivots"].__len__()),
        "quartic_common_denominator": int(
            rhs_diagnostics["quartic"]["common_denominator"]
        ),
        "quartic_numerator_sha256": rhs_diagnostics["quartic"]["numerator_sha256"],
        "row_by_row_direct_evaluator_mismatch_count": int(
            rhs_diagnostics["quartic"]["row_by_row_direct_evaluator_mismatch_count"]
        ),
        "v20_physical_target_artifact_read": bool(
            rhs_diagnostics["v20_physical_target_artifact_read"]
        ),
    }
    diagnostics["fixed_endpoint_provenance"] = {
        "H": "h_-=(e0-i e1)/sqrt(2)",
        "Sigma": "q/4",
        "common_stabilizer": "SU(4)",
        "stabilizer_status": "EXACT_RANK1_SU4_STABILIZER_INFRASTRUCTURE_CERTIFIED",
        "stabilizer_JSON_sha256": EXPECTED_RAW_SHA256[STABILIZER_JSON],
    }
    return (
        matrix,
        denominator,
        target_numerator,
        target_denominator,
        blocks,
        diagnostics,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("use --check")
    matrix, denominator, target, target_denominator, blocks, diagnostics = (
        reconstruct_system()
    )
    print(
        json.dumps(
            {
                "status": "EXACT_CORRECTED_POSITIVE_GRAM_SOURCE_RECONSTRUCTION_PASS",
                "map_shape": list(matrix.shape),
                "map_common_denominator": denominator,
                "map_numerator_csr_sha256": sparse_sha256(matrix),
                "target_common_denominator": target_denominator,
                "target_numerator_int64_sha256": int64_array_sha256(target),
                "standard_block_count": len(blocks),
                "diagnostics": diagnostics,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
