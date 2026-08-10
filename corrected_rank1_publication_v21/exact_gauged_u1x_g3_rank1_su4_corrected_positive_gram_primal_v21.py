#!/usr/bin/env python3
"""HERE-only loader for the corrected v21 exact positive-Gram primal.

Ordinary validation reads only two byte-pinned files beside this module: a
canonical corrected map/RHS sparse system and the exact rational primal.  It
does not import the generation tree, consult environment paths, or regenerate
the 19,594 map columns.  Heavy source reconstruction is a separate explicit
audit step.
"""
from __future__ import annotations

import argparse
import copy
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from scipy import sparse


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / (
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_POSITIVE_GRAM_PRIMAL_V21.json"
)
SYSTEM = HERE / (
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_POSITIVE_GRAM_SYSTEM_V21.npz"
)

EXPECTED_CERTIFICATE_RAW_SHA256 = (
    "dd40a508a08c219117ddefaf574652a24f0e1f868d011e05f558ecafc9600e03"
)
EXPECTED_SYSTEM_RAW_SHA256 = (
    "25ec946b1e9bca50cfe4e31ac9bb58f5d8d0f4a24b83dc11fdeec0d68a80c6f3"
)
EXPECTED_MAP_NUMERATOR_CSR_SHA256 = (
    "1834c8439fa3e44459f7ba871420a4351cd0b4de194dec6f5c4a84c1f39d3a16"
)
EXPECTED_TARGET_NUMERATOR_SHA256 = (
    "14debcfaf02d4b8c20d1d43a2e1f82d6a7390e28428fc63dd21a9c5f90aec0cf"
)
EXPECTED_COORDINATE_SHA256 = (
    "7a36b579821e135fb7283d02e696153cc78907048e73ca5dce0dd260abdc3147"
)
EXPECTED_LDL_PIVOT_SHA256 = (
    "bc8626c201d626aa33a97f707bfa963ae887fe9abb64a0fab728343825a430c2"
)
EXPECTED_SCHEMA = "so10-g3-corrected-positive-gram-exact-primal-v2-hold-only"
EXPECTED_SYSTEM_KEYS = {
    "map_data",
    "map_indices",
    "map_indptr",
    "map_shape",
    "map_denominator",
    "target_numerator",
    "target_denominator",
}


def raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def int64_array_sha256(value: np.ndarray) -> str:
    array = np.ascontiguousarray(value, dtype=np.int64)
    shape = np.asarray(array.shape, dtype="<i8")
    return hashlib.sha256(shape.tobytes() + array.astype("<i8").tobytes()).hexdigest()


def sparse_sha256(value: sparse.spmatrix) -> str:
    matrix = value.tocsr().astype(np.int64)
    matrix.sum_duplicates()
    matrix.sort_indices()
    digest = hashlib.sha256()
    digest.update(np.asarray(matrix.shape, dtype="<i8").tobytes())
    digest.update(np.asarray(matrix.indptr, dtype="<i8").tobytes())
    digest.update(np.asarray(matrix.indices, dtype="<i8").tobytes())
    digest.update(np.asarray(matrix.data, dtype="<i8").tobytes())
    return digest.hexdigest()


def _require_here(path: Path) -> None:
    if path.resolve().parent != HERE.resolve():
        raise ArithmeticError(f"publication input escaped HERE: {path}")


def load_system() -> tuple[sparse.csr_matrix, int, np.ndarray, int]:
    """Load a fresh corrected sparse system after byte and logical checks."""
    _require_here(SYSTEM)
    if raw_sha256(SYSTEM) != EXPECTED_SYSTEM_RAW_SHA256:
        raise ArithmeticError("corrected v21 system bytes drifted")
    with np.load(SYSTEM, allow_pickle=False) as archive:
        if set(archive.files) != EXPECTED_SYSTEM_KEYS:
            raise ArithmeticError("corrected v21 system member inventory drifted")
        shape_raw = np.asarray(archive["map_shape"])
        denominator_raw = np.asarray(archive["map_denominator"])
        target_denominator_raw = np.asarray(archive["target_denominator"])
        data = np.asarray(archive["map_data"])
        indices = np.asarray(archive["map_indices"])
        indptr = np.asarray(archive["map_indptr"])
        target = np.asarray(archive["target_numerator"])
    if (
        shape_raw.dtype != np.dtype("int64")
        or denominator_raw.dtype != np.dtype("int64")
        or target_denominator_raw.dtype != np.dtype("int64")
        or data.dtype != np.dtype("int64")
        or indices.dtype != np.dtype("int32")
        or indptr.dtype != np.dtype("int32")
        or target.dtype != np.dtype("int64")
    ):
        raise ArithmeticError("corrected v21 system dtype drifted")
    shape = tuple(int(value) for value in shape_raw)
    if shape != (6_585, 19_594):
        raise ArithmeticError("corrected v21 system shape drifted")
    matrix = sparse.csr_matrix((data, indices, indptr), shape=shape)
    matrix.check_format(full_check=True)
    if matrix.nnz != 138_550 or not matrix.has_sorted_indices:
        raise ArithmeticError("corrected v21 map sparse structure drifted")
    map_denominator = int(denominator_raw)
    target_denominator = int(target_denominator_raw)
    if map_denominator != 256 or target_denominator != 576_000:
        raise ArithmeticError("corrected v21 system denominator drifted")
    if target.shape != (6_585,):
        raise ArithmeticError("corrected v21 RHS shape drifted")
    if sparse_sha256(matrix) != EXPECTED_MAP_NUMERATOR_CSR_SHA256:
        raise ArithmeticError("corrected v21 map logical fingerprint drifted")
    if int64_array_sha256(target) != EXPECTED_TARGET_NUMERATOR_SHA256:
        raise ArithmeticError("corrected v21 target logical fingerprint drifted")
    return matrix, map_denominator, target.copy(), target_denominator


def validate_certificate(certificate: Mapping[str, Any]) -> None:
    """Reject stale or mutated certificate echoes before returning payload data."""
    expected_top = {
        "claim_boundary",
        "construction",
        "corrected_system",
        "exact_primal_coordinates_fraction_pairs",
        "exact_primal_coordinates_sha256",
        "exact_verification",
        "grade_correction_reconstruction_records",
        "location_boundary",
        "schema",
        "status",
    }
    if set(certificate) != expected_top:
        raise ArithmeticError("corrected primal top-level inventory drifted")
    if certificate.get("schema") != EXPECTED_SCHEMA:
        raise ArithmeticError("corrected primal schema drifted")
    expected_system = certificate.get("corrected_system", {})
    if not (
        expected_system.get("map_shape") == [6_585, 19_594]
        and expected_system.get("map_common_denominator") == 256
        and expected_system.get("map_numerator_csr_sha256")
        == EXPECTED_MAP_NUMERATOR_CSR_SHA256
        and expected_system.get("target_common_denominator") == 576_000
        and expected_system.get("target_numerator_int64_sha256")
        == EXPECTED_TARGET_NUMERATOR_SHA256
        and expected_system.get("numerical_system_raw_sha256")
        == EXPECTED_SYSTEM_RAW_SHA256
    ):
        raise ArithmeticError("corrected primal system echo drifted")
    pairs = certificate.get("exact_primal_coordinates_fraction_pairs")
    if not isinstance(pairs, list) or len(pairs) != 19_594:
        raise ArithmeticError("corrected primal coordinate census drifted")
    if canonical_sha256(pairs) != EXPECTED_COORDINATE_SHA256:
        raise ArithmeticError("corrected primal coordinate digest drifted")
    if certificate.get("exact_primal_coordinates_sha256") != EXPECTED_COORDINATE_SHA256:
        raise ArithmeticError("corrected primal coordinate echo drifted")
    verification = certificate.get("exact_verification", {})
    blocks = verification.get("block_exact_LDL_diagnostics")
    if not (
        verification.get("all_6585_coefficient_equalities_hold") is True
        and verification.get("all_exact_LDL_pivots_strictly_positive") is True
        and verification.get("strict_PSD_block_count") == 22
        and verification.get("exact_LDL_pivot_count") == 824
        and verification.get("all_exact_LDL_pivots_sha256")
        == EXPECTED_LDL_PIVOT_SHA256
        and isinstance(blocks, list)
        and len(blocks) == 22
        and sum(int(row.get("exact_LDL_pivot_count", -1)) for row in blocks) == 824
        and all(row.get("all_exact_LDL_pivots_strictly_positive") is True for row in blocks)
    ):
        raise ArithmeticError("corrected primal exact-verification echo drifted")
    boundary = certificate.get("claim_boundary", {})
    if not (
        boundary.get("corrected_map_and_RHS_pinned") is True
        and boundary.get("exact_affine_equalities_proved") is True
        and boundary.get("exact_strict_PSD_primal_certificate_constructed") is True
        and boundary.get("arbitrary_Phi_endpoint_proved") is False
        and boundary.get("G3_closed") is False
    ):
        raise ArithmeticError("constructor claim boundary drifted")


def load_certificate() -> dict[str, Any]:
    """Return a fresh deep copy of the pinned constructor certificate."""
    _require_here(CERTIFICATE)
    if raw_sha256(CERTIFICATE) != EXPECTED_CERTIFICATE_RAW_SHA256:
        raise ArithmeticError("corrected v21 exact-primal bytes drifted")
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    validate_certificate(certificate)
    return copy.deepcopy(certificate)


@dataclass(frozen=True)
class RuntimeVariable:
    global_index: int
    left_standard_index: int
    right_standard_index: int
    component: str


@dataclass(frozen=True)
class RuntimeBlock:
    block_index: int
    representative: tuple[int, int, int]
    multiplicity: int
    self_conjugate: bool
    variables: tuple[RuntimeVariable, ...]


def runtime_blocks(certificate: Mapping[str, Any]) -> tuple[RuntimeBlock, ...]:
    """Reconstruct the canonical standard-coordinate block layout compactly."""
    validate_certificate(certificate)
    diagnostics = certificate["exact_verification"]["block_exact_LDL_diagnostics"]
    output: list[RuntimeBlock] = []
    global_index = 0
    for expected_index, row in enumerate(diagnostics):
        if int(row["block_index"]) != expected_index:
            raise ArithmeticError("corrected primal block ordering drifted")
        multiplicity = int(row["Gram_order"])
        self_conjugate = row["kind"] == "real_symmetric"
        if not self_conjugate and row["kind"] != "complex_Hermitian":
            raise ArithmeticError("corrected primal block kind drifted")
        expected_realified = multiplicity if self_conjugate else 2 * multiplicity
        if int(row["realified_order"]) != expected_realified:
            raise ArithmeticError("corrected primal realification order drifted")
        variables: list[RuntimeVariable] = []
        for left in range(multiplicity):
            variables.append(RuntimeVariable(global_index, left, left, "diagonal"))
            global_index += 1
            for right in range(left + 1, multiplicity):
                variables.append(
                    RuntimeVariable(global_index, left, right, "real_off_diagonal")
                )
                global_index += 1
                if not self_conjugate:
                    variables.append(
                        RuntimeVariable(
                            global_index, left, right, "imaginary_off_diagonal"
                        )
                    )
                    global_index += 1
        expected_count = (
            multiplicity * (multiplicity + 1) // 2
            if self_conjugate
            else multiplicity * multiplicity
        )
        if len(variables) != expected_count:
            raise ArithmeticError("corrected primal block coordinate count drifted")
        output.append(
            RuntimeBlock(
                block_index=expected_index,
                representative=tuple(int(value) for value in row["representative_dynkin"]),
                multiplicity=multiplicity,
                self_conjugate=self_conjugate,
                variables=tuple(variables),
            )
        )
    if global_index != 19_594:
        raise ArithmeticError("corrected primal global coordinate count drifted")
    return tuple(output)


def build_report() -> dict[str, Any]:
    certificate = load_certificate()
    matrix, map_denominator, target, target_denominator = load_system()
    blocks = runtime_blocks(certificate)
    return {
        "status": "EXACT_RANK1_SU4_CORRECTED_POSITIVE_GRAM_PRIMAL_V21_BYTES_PASS",
        "certificate_raw_sha256": EXPECTED_CERTIFICATE_RAW_SHA256,
        "system_raw_sha256": EXPECTED_SYSTEM_RAW_SHA256,
        "map_shape": list(matrix.shape),
        "map_common_denominator": map_denominator,
        "map_nnz": int(matrix.nnz),
        "map_numerator_csr_sha256": sparse_sha256(matrix),
        "target_common_denominator": target_denominator,
        "target_numerator_sha256": int64_array_sha256(target),
        "exact_coordinate_sha256": certificate["exact_primal_coordinates_sha256"],
        "exact_LDL_pivot_sha256": certificate["exact_verification"][
            "all_exact_LDL_pivots_sha256"
        ],
        "standard_block_count": len(blocks),
        "standard_coordinate_count": sum(len(block.variables) for block in blocks),
        "claim_boundary": {
            "fixed_H": "h_-=(e0-i e1)/sqrt(2)",
            "fixed_Sigma": "q/4",
            "constructor_alone_proves_arbitrary_real_Phi": False,
            "global_Sigma_proved": False,
            "general_H_proved": False,
            "full_Hessian_proved": False,
            "G3_closed": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("use --check")
    print(json.dumps(build_report(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
