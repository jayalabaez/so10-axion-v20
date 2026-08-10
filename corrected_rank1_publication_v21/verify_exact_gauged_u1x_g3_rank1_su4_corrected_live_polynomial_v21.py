#!/usr/bin/env python3
"""Direct Python-integer live-polynomial regression for the v21 primal.

At the pinned rational SU(3) field this evaluates the exact primal as an
actual sum of positive carrier norms, split by homogeneous grade, using Python
integers from the first physical contraction.  It compares that result to the
live anchor polynomial, not to any assembled target payload.  This is an
explicit generation-time regression; its compact output is frozen beside the
separately relocatable runtime publication.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any, Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT.parent / "so10-axion-v20-reaudit"
PUBLICATION = HERE
os.environ.setdefault("SO10_PUBLISHED_API_ROOT", str(REPO))
for source in (PUBLICATION, HERE, ROOT, REPO):
    if str(source) not in sys.path:
        sys.path.insert(0, str(source))

import exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_map_v21 as corrected
import exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_primal_v21 as primal
import prototype_rank1_su3_q0_8d as su3


CERTIFICATE = HERE / "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_POSITIVE_GRAM_PRIMAL_V21.json"
OUTPUT = HERE / "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_LIVE_POLYNOMIAL_V21.json"
EXPECTED_CERTIFICATE_RAW_SHA256: str | None = (
    "dd40a508a08c219117ddefaf574652a24f0e1f868d011e05f558ecafc9600e03"
)
EXPECTED_DEPENDENCY_RAW_SHA256 = {
    "exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_map_v21.py": (
        "a7fe300ccf69dcb2520f2b3f18bf994fb8ab7ad90c5be866b34143b69c971259"
    ),
    "prototype_rank1_su3_q0_8d.py": (
        "e3b448d3cd8b8a2f0bf63aaae19f1744f0c7af296d2e29bf0fe0db117dfa7900"
    ),
}
WITNESS = (-639, 1160, 1023, -909, 0, 0, 0, 0)
WITNESS_DENOMINATOR = 1000
FEATURE_DENOMINATOR = 256
EXPECTED_TARGET_BY_GRADE = (
    Fraction(237, 200),
    Fraction(-3183, 10000),
    Fraction(-753023067, 400000000),
    Fraction(0),
    Fraction(3063315748321207, 3000000000000000),
)
EXPECTED_TARGET_TOTAL = Fraction(15742745821207, 3000000000000000)
EXPECTED_RAW_ANCHOR_TOTAL = Fraction(60742745821207, 3000000000000000)
STATUS = "EXACT_RANK1_SU4_CORRECTED_LIVE_POLYNOMIAL_V21_PASS"


def raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fraction_pair(value: Fraction) -> list[str]:
    return [str(value.numerator), str(value.denominator)]


def parse_fraction_pair(raw: Sequence[str]) -> Fraction:
    if len(raw) != 2:
        raise ArithmeticError("coordinate is not a fraction pair")
    numerator, denominator = int(raw[0]), int(raw[1])
    if denominator <= 0 or math.gcd(abs(numerator), denominator) != 1:
        raise ArithmeticError("coordinate is not canonically reduced")
    value = Fraction(numerator, denominator)
    if fraction_pair(value) != list(raw):
        raise ArithmeticError("coordinate text is noncanonical")
    return value


def evaluate_sparse_polynomial_by_degree(polynomial, values):
    output = [Fraction(0) for _ in range(5)]
    for exponent, coefficient in polynomial.items():
        value = Fraction(coefficient)
        for index, power in enumerate(exponent):
            value *= values[index] ** power
        output[sum(exponent)] += value
    return tuple(output)


def exact_sparse_matvec(matrix, vector: np.ndarray) -> np.ndarray:
    values = [int(value) for value in np.asarray(vector).reshape(-1)]
    if hasattr(matrix, "tocsr"):
        matrix = matrix.tocsr()
    else:
        dense = np.asarray(matrix, dtype=object)
        if dense.ndim != 2 or dense.shape[1] != len(values):
            raise ArithmeticError("dense physical contraction shape drifted")
        output = np.empty(dense.shape[0], dtype=object)
        for row in range(dense.shape[0]):
            output[row] = sum(
                int(dense[row, column]) * values[column]
                for column in range(dense.shape[1])
            )
        return output
    output = np.empty(matrix.shape[0], dtype=object)
    for row in range(matrix.shape[0]):
        total = 0
        for cursor in range(matrix.indptr[row], matrix.indptr[row + 1]):
            total += int(matrix.data[cursor]) * values[int(matrix.indices[cursor])]
        output[row] = total
    return output


def raw_copy_weights(block, vector_real, vector_imaginary):
    """Apply F=[P|iQ] with object integers; no fixed-width contraction."""
    f_real = np.asarray(block.f_real, dtype=object)
    f_imaginary = np.asarray(block.f_imaginary, dtype=object)
    vector_real = np.asarray(vector_real, dtype=object)
    vector_imaginary = np.asarray(vector_imaginary, dtype=object)
    return (
        f_real @ vector_real - f_imaginary @ vector_imaginary,
        f_real @ vector_imaginary + f_imaginary @ vector_real,
    )


def homogeneous_field() -> dict[str, Any]:
    coordinates = np.asarray(WITNESS, dtype=object)
    z = exact_sparse_matvec(su3.basis(), coordinates)
    br, bi = corrected.gaussian_embedding()
    x_real = exact_sparse_matvec(br.T, z)
    x_imaginary = -exact_sparse_matvec(bi.T, z)
    pairs = corrected.cubic._quadratic_pairs_cached()
    pair_real = np.asarray(
        [
            int(x_real[left]) * int(x_real[right])
            - int(x_imaginary[left]) * int(x_imaginary[right])
            for left, right in pairs
        ],
        dtype=object,
    )
    pair_imaginary = np.asarray(
        [
            int(x_real[left]) * int(x_imaginary[right])
            + int(x_imaginary[left]) * int(x_real[right])
            for left, right in pairs
        ],
        dtype=object,
    )
    return {
        "t": WITNESS_DENOMINATOR,
        "z": z,
        "x_real_numerator": x_real,
        "x_imaginary_numerator": x_imaginary,
        "pair_real_numerator": pair_real,
        "pair_imaginary_numerator": pair_imaginary,
        "homogeneous_denominator": WITNESS_DENOMINATOR**4,
    }


def exact_carrier_feature_sums(block, raw_real, raw_imaginary, field):
    dimension = corrected.positive_pairing(block.representative).shape[0]
    output = [
        (np.zeros(dimension, dtype=object), np.zeros(dimension, dtype=object))
        for _ in range(3)
    ]
    offsets = block.grade_offsets
    t = int(field["t"])
    x_real = np.asarray(field["x_real_numerator"], dtype=object)
    x_imaginary = np.asarray(field["x_imaginary_numerator"], dtype=object)
    pair_real = np.asarray(field["pair_real_numerator"], dtype=object)
    pair_imaginary = np.asarray(field["pair_imaginary_numerator"], dtype=object)
    for raw in range(block.multiplicity):
        grade = int(block.raw_grade[raw])
        local = raw - offsets[grade]
        if grade == 0:
            feature_real = np.asarray([t * t * FEATURE_DENOMINATOR], dtype=object)
            feature_imaginary = np.zeros(1, dtype=object)
        elif grade == 1:
            carrier = corrected.tphi_carriers(block.representative)[local][
                "exterior_basis"
            ].T.tocsr()
            feature_real = exact_sparse_matvec(carrier, 16 * t * x_real)
            feature_imaginary = exact_sparse_matvec(carrier, 16 * t * x_imaginary)
        elif grade == 2:
            carrier = corrected.quartic._carrier_family_data_cached()[
                block.representative
            ]["copies"][local].T.tocsr()
            feature_real = exact_sparse_matvec(carrier, pair_real)
            feature_imaginary = exact_sparse_matvec(carrier, pair_imaginary)
        else:
            raise ArithmeticError("invalid carrier grade")
        wr, wi = int(raw_real[raw]), int(raw_imaginary[raw])
        output[grade][0][:] += wr * feature_real - wi * feature_imaginary
        output[grade][1][:] += wr * feature_imaginary + wi * feature_real
    return tuple(output)


def standard_feature_matrices(block, field):
    dimension = corrected.positive_pairing(block.representative).shape[0]
    real = [
        np.zeros((dimension, block.multiplicity), dtype=object) for _ in range(3)
    ]
    imaginary = [np.zeros_like(value) for value in real]
    for standard in range(block.multiplicity):
        vector_real = np.zeros(block.multiplicity, dtype=np.int64)
        vector_imaginary = np.zeros_like(vector_real)
        vector_real[standard] = 1
        raw_real, raw_imaginary = raw_copy_weights(
            block, vector_real, vector_imaginary
        )
        grades = exact_carrier_feature_sums(
            block, raw_real, raw_imaginary, field
        )
        for grade, (feature_real, feature_imaginary) in enumerate(grades):
            real[grade][:, standard] = np.asarray(feature_real, dtype=object).reshape(-1)
            imaginary[grade][:, standard] = np.asarray(
                feature_imaginary, dtype=object
            ).reshape(-1)
    return tuple(zip(real, imaginary, strict=True))


def degree_kernel_matrices(block, features):
    pairing = corrected.positive_pairing(block.representative).toarray().astype(object)
    real = [
        np.zeros((block.multiplicity, block.multiplicity), dtype=object)
        for _ in range(5)
    ]
    imaginary = [np.zeros_like(value) for value in real]
    for left_grade, (left_real, left_imaginary) in enumerate(features):
        for right_grade, (right_real, right_imaginary) in enumerate(features):
            degree = left_grade + right_grade
            real[degree] += (
                left_real.T @ pairing @ right_real
                + left_imaginary.T @ pairing @ right_imaginary
            )
            imaginary[degree] += (
                left_real.T @ pairing @ right_imaginary
                - left_imaginary.T @ pairing @ right_real
            )
    return tuple(zip(real, imaginary, strict=True))


def contract_standard_coordinate(variable, kernel) -> int:
    real, imaginary = kernel
    left = variable.left_standard_index
    right = variable.right_standard_index
    if variable.component == "diagonal":
        if imaginary[left, left]:
            raise ArithmeticError("Hermitian kernel acquired imaginary diagonal")
        return int(real[left, left])
    if variable.component == "real_off_diagonal":
        return int(real[left, right] + real[right, left])
    if variable.component == "imaginary_off_diagonal":
        return int(imaginary[left, right] - imaginary[right, left])
    raise ArithmeticError("unknown standard coordinate component")


def maximum_integer_bit_length(*values) -> int:
    maximum = 0
    for value in values:
        for item in np.asarray(value, dtype=object).reshape(-1):
            maximum = max(maximum, abs(int(item)).bit_length())
    return maximum


def exact_primal_carrier_values(blocks, coordinates, field):
    common_denominator = FEATURE_DENOMINATOR**2 * int(
        field["homogeneous_denominator"]
    )
    totals = [Fraction(0) for _ in range(5)]
    block_rows = []
    maximum_physical_integer_bits = maximum_integer_bit_length(
        field["z"],
        field["x_real_numerator"],
        field["x_imaginary_numerator"],
        field["pair_real_numerator"],
        field["pair_imaginary_numerator"],
    )
    for block in blocks:
        features = standard_feature_matrices(block, field)
        degree_kernels = degree_kernel_matrices(block, features)
        maximum_physical_integer_bits = max(
            maximum_physical_integer_bits,
            maximum_integer_bit_length(
                *(part for pair in features for part in pair),
                *(part for pair in degree_kernels for part in pair),
            ),
        )
        values = [Fraction(0) for _ in range(5)]
        for variable in block.variables:
            coordinate = coordinates[variable.global_index]
            if coordinate:
                contraction = contract_standard_coordinate(
                    variable, degree_kernels[variable.phi_degree]
                )
                maximum_physical_integer_bits = max(
                    maximum_physical_integer_bits,
                    abs(int(contraction)).bit_length(),
                )
                values[variable.phi_degree] += coordinate * Fraction(
                    contraction,
                    common_denominator,
                )
        for degree, value in enumerate(values):
            totals[degree] += value
        block_rows.append(
            {
                "block_index": block.block_index,
                "representative_dynkin": list(block.representative),
                "values_by_grade": [str(value) for value in values],
            }
        )
    return tuple(totals), block_rows, {
        "physical_contraction_arithmetic": "Python int/object",
        "maximum_physical_integer_bit_length": maximum_physical_integer_bits,
        "signed_int64_value_bit_capacity": 63,
        "physical_path_exceeds_signed_int64": maximum_physical_integer_bits > 63,
        "fixed_width_physical_contraction_used": False,
    }


def main() -> int:
    if EXPECTED_CERTIFICATE_RAW_SHA256 is None:
        raise ArithmeticError(
            "certificate fingerprint is intentionally unset; generate, review, and pin it first"
        )
    observed_dependencies = {
        name: raw_sha256(
            Path(
                {
                    "exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_map_v21.py": corrected.__file__,
                    "prototype_rank1_su3_q0_8d.py": su3.__file__,
                }[name]
            ).resolve()
        )
        for name in EXPECTED_DEPENDENCY_RAW_SHA256
    }
    if observed_dependencies != EXPECTED_DEPENDENCY_RAW_SHA256:
        raise ArithmeticError("live-polynomial dependency provenance drifted")
    if raw_sha256(CERTIFICATE) != EXPECTED_CERTIFICATE_RAW_SHA256:
        raise ArithmeticError("corrected exact certificate bytes drifted")
    certificate = primal.load_certificate()
    coordinates = [
        parse_fraction_pair(pair)
        for pair in certificate["exact_primal_coordinates_fraction_pairs"]
    ]
    if len(coordinates) != 19_594:
        raise ArithmeticError("exact primal coordinate census drifted")
    report = corrected.load_certificate()
    blocks = corrected.build_standard_blocks(report)
    field = homogeneous_field()
    carrier, block_rows, arithmetic_safety = exact_primal_carrier_values(
        blocks, coordinates, field
    )
    slice_values = [Fraction(value, WITNESS_DENOMINATOR) for value in WITNESS]
    raw_anchor = evaluate_sparse_polynomial_by_degree(
        su3.anchor_polynomial(), slice_values
    )
    target = (raw_anchor[0] - Fraction(3, 200), *raw_anchor[1:])
    if raw_anchor[0] - target[0] != Fraction(3, 200):
        raise ArithmeticError("grade-zero reserve subtraction drifted")
    if target[1:] != raw_anchor[1:]:
        raise ArithmeticError("reserve subtraction altered a nonzero grade")
    if sum(raw_anchor) != EXPECTED_RAW_ANCHOR_TOTAL:
        raise ArithmeticError("raw live anchor polynomial regression drifted")
    if target != EXPECTED_TARGET_BY_GRADE or sum(target) != EXPECTED_TARGET_TOTAL:
        raise ArithmeticError("live endpoint target A-3/200 regression drifted")
    if carrier != target:
        residual = tuple(carrier[i] - target[i] for i in range(5))
        raise ArithmeticError(f"exact primal carrier/live mismatch by grade: {residual}")
    payload = {
        "status": STATUS,
        "source_raw_sha256": raw_sha256(Path(__file__).resolve()),
        "generation_boundary": {
            "generation_time_external_structural_APIs_required": True,
            "runtime_relocation_claimed_by_this_source": False,
            "target_payload_read": False,
            "physical_contraction_arithmetic": "Python int/object",
        },
        "certificate_raw_sha256": EXPECTED_CERTIFICATE_RAW_SHA256,
        "dependency_raw_sha256": observed_dependencies,
        "SU3_witness_coordinates_over_1000": list(WITNESS),
        "raw_live_anchor_A_by_grade": [str(value) for value in raw_anchor],
        "reserve_subtracted_from_grade_zero": "3/200",
        "reserve_changes_only_grade_zero_exact": True,
        "live_endpoint_target_A_minus_3_over_200_by_grade": [
            str(value) for value in target
        ],
        "direct_positive_carrier_norm_by_grade": [str(value) for value in carrier],
        "exact_residual_by_grade": ["0", "0", "0", "0", "0"],
        "raw_live_anchor_total": str(sum(raw_anchor)),
        "target_and_carrier_total": str(sum(target)),
        "block_contributions": block_rows,
        "exact_arithmetic_safety": arithmetic_safety,
        "claim_boundary": {
            "pinned_live_SU3_polynomial_consistency_verified": True,
            "complete_polynomial_identity_proved_by_this_regression": False,
            "complete_chart_identity_requires_separate_map_RHS_reconstruction": True,
            "arbitrary_Phi_polynomial_identity_proved": False,
            "arbitrary_Phi_endpoint_proved": False,
            "global_Sigma_proved": False,
            "general_H_proved": False,
            "full_Hessian_proved": False,
            "G3_closed": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": STATUS,
                "target_and_carrier_total": payload["target_and_carrier_total"],
                "G3_closed": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
