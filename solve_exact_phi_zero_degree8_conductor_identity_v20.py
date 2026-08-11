#!/usr/bin/env python3
"""One exact fraction-free solve of the reconstructed degree-eight table."""
from __future__ import annotations

import hashlib
import json
import math
import time
from fractions import Fraction
from pathlib import Path

from sympy import ZZ
from sympy.polys.matrices import DomainMatrix


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "EXACT_PHI_ZERO_DEGREE8_CONDUCTOR_EVALUATION_TABLE.json"
DESTINATION = HERE / "EXACT_PHI_ZERO_DEGREE8_CONDUCTOR_SOLUTION.json"


def rank_mod(matrix: list[list[int]], prime: int) -> int:
    work = [[value % prime for value in row] for row in matrix]
    row = 0
    for column in range(len(work[0])):
        pivot = next(
            (candidate for candidate in range(row, len(work)) if work[candidate][column]),
            None,
        )
        if pivot is None:
            continue
        work[row], work[pivot] = work[pivot], work[row]
        inverse = pow(work[row][column], -1, prime)
        work[row] = [value * inverse % prime for value in work[row]]
        for target in range(len(work)):
            if target == row or not work[target][column]:
                continue
            coefficient = work[target][column]
            work[target] = [
                (left - coefficient * right) % prime
                for left, right in zip(work[target], work[row], strict=True)
            ]
        row += 1
        if row == len(work):
            break
    return row


def main() -> None:
    start = time.time()
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    augmented = [
        [int(value) for value in row]
        for row in payload["selected_exact_augmented_entries"]
    ]
    if (len(augmented), len(augmented[0])) != (117, 118):
        raise ArithmeticError("unexpected augmented shape")

    row_gcds = []
    for index, row in enumerate(augmented):
        common = math.gcd(*(abs(value) for value in row))
        if not common:
            common = 1
        row_gcds.append(common)
        augmented[index] = [value // common for value in row]
    matrix = [row[:-1] for row in augmented]
    rhs = [[row[-1]] for row in augmented]

    column_gcds = []
    for column in range(117):
        common = math.gcd(*(abs(row[column]) for row in matrix))
        if not common:
            common = 1
        column_gcds.append(common)
        for row in matrix:
            row[column] //= common

    modular_rank = rank_mod(matrix, 10_000_019)
    if modular_rank != 117:
        raise ArithmeticError(("scaled basis rank", modular_rank))
    print(
        "scaled exact table",
        "row_gcd_digits",
        (min(len(str(value)) for value in row_gcds), max(len(str(value)) for value in row_gcds)),
        "column_gcd_digits",
        (
            min(len(str(value)) for value in column_gcds),
            max(len(str(value)) for value in column_gcds),
        ),
        "elapsed",
        f"{time.time()-start:.2f}s",
        flush=True,
    )

    domain_matrix = DomainMatrix.from_list(matrix, ZZ)
    domain_rhs = DomainMatrix.from_list(rhs, ZZ)
    numerator, denominator = domain_matrix.solve_den(domain_rhs, method="rref")
    if domain_matrix * numerator != denominator * domain_rhs:
        raise ArithmeticError("fraction-free solve residual")
    numerator_values = [int(row[0]) for row in numerator.to_list()]
    denominator_value = int(denominator)
    if numerator_values[-2:] != [0, 0]:
        raise ArithmeticError(("nonzero quotient numerators", numerator_values[-2:]))
    coefficients = [
        Fraction(value, denominator_value * column_gcd)
        for value, column_gcd in zip(numerator_values, column_gcds, strict=True)
    ]

    # Recheck the original centered table over Q.
    original = [
        [int(value) for value in row]
        for row in payload["selected_exact_augmented_entries"]
    ]
    for row in original:
        if sum(
            coefficient * value
            for coefficient, value in zip(coefficients, row[:-1], strict=True)
        ) != row[-1]:
            raise ArithmeticError("original-table rational residual")

    output = {
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "modular_full_basis_rank": modular_rank,
        "row_gcds": [str(value) for value in row_gcds],
        "column_gcds": [str(value) for value in column_gcds],
        "solve_denominator": str(denominator_value),
        "solve_numerators": [str(value) for value in numerator_values],
        "original_basis_coefficients": [str(value) for value in coefficients],
        "quotient_coefficients_N2D_N4": [str(value) for value in coefficients[-2:]],
        "exact_original_table_residual": True,
        "elapsed_seconds": time.time() - start,
    }
    DESTINATION.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(
        "EXACT_SOLVE_PASS",
        "last_numerators",
        numerator_values[-2:],
        "denominator_digits",
        len(str(abs(denominator_value))),
        "elapsed",
        f"{time.time()-start:.2f}s",
        flush=True,
    )


if __name__ == "__main__":
    main()
