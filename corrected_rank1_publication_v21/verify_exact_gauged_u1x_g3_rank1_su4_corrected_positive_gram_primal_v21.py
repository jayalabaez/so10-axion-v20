#!/usr/bin/env python3
"""HERE-only independent Fraction/Bareiss verifier for the v21 primal."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Sequence

import numpy as np
from scipy import sparse

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_primal_v21 as primal
if Path(primal.__file__).resolve() != (
    HERE / "exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_primal_v21.py"
).resolve():
    raise ImportError("runtime primal module escaped HERE")


OUTPUT = HERE / (
    "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_POSITIVE_GRAM_VERIFY_V21.json"
)
STATUS = "EXACT_RANK1_SU4_CORRECTED_POSITIVE_GRAM_PRIMAL_V21_INDEPENDENT_VERIFY_PASS"


def raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "ascii"
        )
    ).hexdigest()


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


def exact_row_dot(
    matrix: sparse.csr_matrix, row: int, coordinates: Sequence[Fraction]
) -> Fraction:
    start, stop = matrix.indptr[row], matrix.indptr[row + 1]
    return sum(
        (
            int(value) * coordinates[int(column)]
            for column, value in zip(
                matrix.indices[start:stop], matrix.data[start:stop], strict=True
            )
        ),
        Fraction(0),
    )


def realified_block(coordinates: Sequence[Fraction], block):
    order = block.multiplicity
    real = [[Fraction(0) for _ in range(order)] for _ in range(order)]
    imaginary = [[Fraction(0) for _ in range(order)] for _ in range(order)]
    for variable in block.variables:
        value = coordinates[variable.global_index]
        left, right = variable.left_standard_index, variable.right_standard_index
        if variable.component == "diagonal":
            real[left][left] = value
        elif variable.component == "real_off_diagonal":
            real[left][right] = real[right][left] = value
        elif variable.component == "imaginary_off_diagonal":
            imaginary[left][right] = value
            imaginary[right][left] = -value
        else:
            raise ArithmeticError("unknown standard block coordinate")
    if block.self_conjugate:
        return real
    output = [[Fraction(0) for _ in range(2 * order)] for _ in range(2 * order)]
    for row in range(order):
        for column in range(order):
            output[row][column] = real[row][column]
            output[row][order + column] = -imaginary[row][column]
            output[order + row][column] = imaginary[row][column]
            output[order + row][order + column] = real[row][column]
    return output


def fraction_free_positive_leading_minors(matrix):
    order = len(matrix)
    common_denominator = 1
    for row in matrix:
        for value in row:
            common_denominator = math.lcm(common_denominator, value.denominator)
    lower = [
        [int(matrix[row][column] * common_denominator) for column in range(row + 1)]
        for row in range(order)
    ]
    previous = 1
    minors = []
    for pivot_index in range(order):
        pivot = lower[pivot_index][pivot_index]
        if pivot <= 0:
            raise ArithmeticError(
                f"nonpositive leading principal minor {pivot_index}: {pivot}"
            )
        minors.append(pivot)
        for left in range(pivot_index + 1, order):
            left_entry = lower[left][pivot_index]
            for right in range(left, order):
                numerator = (
                    lower[right][left] * pivot
                    - left_entry * lower[right][pivot_index]
                )
                quotient, remainder = divmod(numerator, previous)
                if remainder:
                    raise ArithmeticError("Bareiss division was inexact")
                lower[right][left] = quotient
        previous = pivot
    return minors, common_denominator


def verify() -> dict:
    certificate = primal.load_certificate()
    raw_map, map_denominator, target, target_denominator = primal.load_system()
    blocks = primal.runtime_blocks(certificate)
    expected_system = certificate["corrected_system"]
    if not (
        expected_system["map_shape"] == list(raw_map.shape)
        and expected_system["map_common_denominator"] == map_denominator
        and expected_system["map_numerator_csr_sha256"] == primal.sparse_sha256(raw_map)
        and expected_system["target_common_denominator"] == target_denominator
        and expected_system["target_numerator_int64_sha256"]
        == primal.int64_array_sha256(target)
        and expected_system["numerical_system_raw_sha256"]
        == primal.EXPECTED_SYSTEM_RAW_SHA256
    ):
        raise ArithmeticError("corrected certificate system binding drifted")

    raw_pairs = certificate["exact_primal_coordinates_fraction_pairs"]
    coordinates = [parse_fraction_pair(pair) for pair in raw_pairs]
    if len(coordinates) != raw_map.shape[1]:
        raise ArithmeticError("coordinate census drifted")
    if canonical_sha256(raw_pairs) != certificate["exact_primal_coordinates_sha256"]:
        raise ArithmeticError("coordinate digest drifted")
    if target_denominator % map_denominator:
        raise ArithmeticError("target/map denominator ratio is not integral")
    multiplier = target_denominator // map_denominator
    for row in range(raw_map.shape[0]):
        if multiplier * exact_row_dot(raw_map, row, coordinates) != int(target[row]):
            raise ArithmeticError(f"exact equality failed at row {row}")

    all_ldl_pairs = []
    block_rows = []
    for block in blocks:
        matrix = realified_block(coordinates, block)
        minors, denominator = fraction_free_positive_leading_minors(matrix)
        previous = 1
        pivots = []
        for minor in minors:
            pivots.append(Fraction(minor, denominator * previous))
            previous = minor
        if not all(value > 0 for value in pivots):
            raise ArithmeticError("positive minors produced nonpositive pivot")
        pairs = [fraction_pair(value) for value in pivots]
        all_ldl_pairs.extend(pairs)
        constructor = certificate["exact_verification"][
            "block_exact_LDL_diagnostics"
        ][block.block_index]
        if canonical_sha256(pairs) != constructor["LDL_pivot_pairs_sha256"]:
            raise ArithmeticError(
                f"independent pivot digest mismatch in block {block.block_index}"
            )
        block_rows.append(
            {
                "block_index": block.block_index,
                "representative_dynkin": list(block.representative),
                "realified_order": len(matrix),
                "positive_leading_principal_minor_count": len(minors),
                "cleared_denominator_height_bits": denominator.bit_length(),
                "all_leading_principal_minors_strictly_positive": True,
                "derived_LDL_pivot_pairs_sha256": canonical_sha256(pairs),
            }
        )
    ldl_sha = canonical_sha256(all_ldl_pairs)
    if ldl_sha != certificate["exact_verification"]["all_exact_LDL_pivots_sha256"]:
        raise ArithmeticError("all-block independent LDL digest mismatch")
    payload = {
        "status": STATUS,
        "certificate_raw_sha256": primal.EXPECTED_CERTIFICATE_RAW_SHA256,
        "corrected_system_raw_sha256": primal.EXPECTED_SYSTEM_RAW_SHA256,
        "coefficient_map_numerator_csr_sha256": primal.sparse_sha256(raw_map),
        "target_numerator_int64_sha256": primal.int64_array_sha256(target),
        "exact_coordinate_sha256": certificate["exact_primal_coordinates_sha256"],
        "exact_LDL_pivot_sha256": ldl_sha,
        "exact_coefficient_equalities_verified": raw_map.shape[0],
        "exact_rational_coordinates_verified": len(coordinates),
        "strictly_positive_Gram_blocks_verified": len(blocks),
        "independent_method": (
            "canonical Fraction equalities plus denominator-cleared "
            "fraction-free Bareiss/Sylvester leading principal minors"
        ),
        "block_diagnostics": block_rows,
        "claim_boundary": {
            "exact_affine_equalities_proved": True,
            "exact_strict_PSD_primal_independently_verified": True,
            "physical_carrier_endpoint_identity_proved_separately": False,
            "arbitrary_Phi_endpoint_proved": False,
            "global_Sigma_proved": False,
            "general_H_proved": False,
            "full_Hessian_proved": False,
            "G3_closed": False,
        },
    }
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args(argv)
    payload = verify()
    if args.write_report:
        if OUTPUT.resolve().parent != HERE.resolve():
            raise ArithmeticError("independent verifier output escaped HERE")
        OUTPUT.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "exact_coefficient_equalities_verified": payload[
                    "exact_coefficient_equalities_verified"
                ],
                "strictly_positive_Gram_blocks_verified": payload[
                    "strictly_positive_Gram_blocks_verified"
                ],
                "exact_LDL_pivot_sha256": payload["exact_LDL_pivot_sha256"],
                "G3_closed": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
