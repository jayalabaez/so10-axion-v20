#!/usr/bin/env python3
"""Exact global degree-eight conductor identity for the Phi self-zero locus.

For ``Phi in Lambda^4(R^10)`` put

    N = ||Phi||^2,
    B = *(Phi wedge Phi),
    delta = 9 N^2 - 5 ||B||^2,
    D = delta/5.

This certificate proves over Q that ``delta^2`` is a linear combination of
115 contractions ``tr(q_r q_a q_b q_c)``, each containing
``r=54`` or ``r=4125``.  Hence

    q_54(Phi)=q_4125(Phi)=0  ==>  delta^2=25 D^2=0  ==>  D=0.

The proof uses the separately frozen exact count
``dim Sym^8(Lambda^4(C^10))^O(10)=117``.  The 115 residual trace
contractions, together with ``N^2 delta`` and ``N^4``, have a 117 by 117
evaluation matrix of full rank.  They are therefore a basis of the complete
orientation-even degree-eight invariant space.  An entrywise CRT
reconstruction under an explicit height bound gives the exact integer
evaluation table.  A fraction-free solve over ZZ has zero coordinates on
both complement columns, and its residual is checked entrywise exactly.

The table target is ``delta^2=25D^2`` and the first complement is
``N^2 delta=5N^2D``; these factors are intentional.  This theorem proves the
conductor identity and D=0 on the common residual zero set.  The subsequent
S=0/stabilizer orbit classification and quantitative distance estimates are
separate statements.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE
for source in (HERE, REPO):
    if str(source) not in sys.path:
        sys.path.insert(0, str(source))

import exact_210_self_invariant_basis_v20 as invariants
import exact_gauged_u1x_g3_su5_phi_su3_slice_v20 as covariants
import exact_phisigma_casimir_projectors_v20 as projectors
import exact_phi_zero_o10_degree8_invariant_split_v20 as invariant_split


STATUS = "EXACT_GLOBAL_PHI_ZERO_DEGREE8_CONDUCTOR__ORBIT_RIGIDITY_SEPARATE"
EXPECTED_CORE_SHA256 = "3763506628c0aac91fc54fdd1b49f6cdb12114707a13f2359ba3acc2b4836142"
TABLE = HERE / "EXACT_PHI_ZERO_DEGREE8_CONDUCTOR_EVALUATION_TABLE.json"
SOLUTION = HERE / "EXACT_PHI_ZERO_DEGREE8_CONDUCTOR_SOLUTION.json"
EXPECTED_SHA256 = {
    TABLE: "beab3649ca03c3ee3c6fc2ab700efedfe614328a6da52f2234d3b9610f3c167c",
    SOLUTION: "c49833b4f90b0b5a6604d4d5aded36ea00944dd198d2ceefd8def8213174dcfa",
    HERE / "exact_phi_zero_o10_degree8_invariant_split_v20.py": (
        "6a80a8f95efc1f4515b8b8e9120c4011df5d378ebeb38f59f6119c73308daa90"
    ),
    HERE / "reconstruct_exact_phi_zero_degree8_conductor_table_v20.py": (
        "968c4f63bbc4a1eb213a335d10ee465e8f27621b79c9ce860ca187702f49bbc9"
    ),
    HERE / "reconstruct_exact_phi_zero_degree8_radical_v20.py": (
        "8c835c5df2bce72d263117061fde770d53bb7d607cd305cc4a6a039466529133"
    ),
    HERE / "EXACT_PHI_ZERO_DEGREE8_CONDUCTOR_RECONSTRUCTION_CHECKPOINT.json": (
        "0afad3c1a1de58243d27fd07fe550c90ca516e1c5483c027bcbd8e752e892179"
    ),
    HERE / "solve_exact_phi_zero_degree8_conductor_identity_v20.py": (
        "3679695424452230c1583088b83291a7671348cfa90deb872cba51f2a07eceb0"
    ),
    REPO / "exact_210_self_invariant_basis_v20.py": (
        "e905911f3589a78fb0c510060ca0ff6997d0963305c48f91f7a37cccbcfb4772"
    ),
    REPO / "exact_phisigma_casimir_projectors_v20.py": (
        "f4b7b6eea2bb0c4423ff52bc8b4abb082ad77eaba524a1de0a345c9eae1e2400"
    ),
    REPO / "exact_gauged_u1x_g3_su5_phi_su3_slice_v20.py": (
        "dd4eef8d455601b3527e0dbe46b10cf09ab9224282e73b65a0e98a289fefd0a8"
    ),
}

CHANNELS = tuple(projectors.SPECTRAL_EIGENVALUES)
TRIPLES = tuple(itertools.combinations_with_replacement(range(8), 3))
SAMPLE_SEED = 20_260_810
SAMPLE_COORDINATE_BOUND = 3
SAMPLE_COUNT = 117


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def _rank_mod(matrix: list[list[int]] | np.ndarray, prime: int) -> int:
    work = np.asarray(
        [[int(value) % prime for value in row] for row in matrix], dtype=np.int64
    )
    row = 0
    for column in range(work.shape[1]):
        candidates = np.flatnonzero(work[row:, column])
        if not candidates.size:
            continue
        pivot = row + int(candidates[0])
        work[[row, pivot]] = work[[pivot, row]]
        work[row] = work[row] * pow(int(work[row, column]), -1, prime) % prime
        for target in range(work.shape[0]):
            if target == row or not work[target, column]:
                continue
            work[target] = (
                work[target] - work[target, column] * work[row]
            ) % prime
        row += 1
        if row == work.shape[0]:
            break
    return row


def _projector_denominators() -> tuple[int, ...]:
    output = []
    for eigenvalue in projectors.SPECTRAL_EIGENVALUES.values():
        denominator = 1
        for coefficient in projectors.projector_polynomial(eigenvalue):
            denominator = math.lcm(denominator, coefficient.denominator)
        output.append(denominator)
    return tuple(output)


def _trace_scale(index: int, denominators: tuple[int, ...]) -> int:
    residual = 2 if index < len(TRIPLES) else 5
    left, middle, right = TRIPLES[index % len(TRIPLES)]
    return (
        denominators[residual]
        * denominators[left]
        * denominators[middle]
        * denominators[right]
    )


def _exact_payload() -> tuple[dict[str, Any], dict[str, Any]]:
    for path, expected in EXPECTED_SHA256.items():
        observed = _sha256(path)
        if observed != expected:
            raise ArithmeticError(f"dependency hash drift: {path.name}: {observed}")
    table = json.loads(TABLE.read_text(encoding="utf-8"))
    solution = json.loads(SOLUTION.read_text(encoding="utf-8"))
    if solution["source_sha256"] != EXPECTED_SHA256[TABLE]:
        raise ArithmeticError("solution/table linkage drift")
    return table, solution


def _verify_height_and_basis(table: dict[str, Any]) -> tuple[list[list[int]], int]:
    primes = tuple(int(value) for value in table["primes"])
    modulus = int(table["modulus"])
    if modulus != math.prod(primes):
        raise ArithmeticError("CRT modulus drift")
    denominators = _projector_denominators()
    trace_pivots = [int(value) for value in table["trace_pivots"]]
    trace_scales = tuple(_trace_scale(index, denominators) for index in trace_pivots)
    if [str(value) for value in trace_scales] != table["trace_scales"]:
        raise ArithmeticError("trace scale drift")
    nmax = 210 * SAMPLE_COORDINATE_BOUND**2
    entry_bound = max(trace_scales) * nmax**4
    if int(table["entry_bound"]) != entry_bound or modulus <= 2 * entry_bound:
        raise ArithmeticError("entrywise CRT height certificate drift")

    # Elementary direct bound for delta columns and target.
    coefficient_sums = [0] * 45
    for _left, _right, target, coefficient in covariants._disjoint_four_form_pairs():
        coefficient_sums[target] += abs(coefficient)
    b_entry_bound = SAMPLE_COORDINATE_BOUND**2 * max(coefficient_sums)
    b2_bound = 45 * b_entry_bound**2
    delta_bound = 9 * nmax**2 + 5 * b2_bound
    if max(delta_bound**2, nmax**2 * delta_bound, nmax**4) > entry_bound:
        raise ArithmeticError("delta-column height no longer dominated")

    augmented = [
        [int(value) for value in row]
        for row in table["selected_exact_augmented_entries"]
    ]
    if (len(augmented), len(augmented[0])) != (117, 118):
        raise ArithmeticError("evaluation table shape drift")
    if max(abs(value) for row in augmented for value in row) > entry_bound:
        raise ArithmeticError("centered entry exceeds certified bound")
    if table["sample_pivots"] != list(range(117)):
        raise ArithmeticError("sample pivot drift")
    rank = _rank_mod([row[:-1] for row in augmented], primes[0])
    if rank != 117:
        raise ArithmeticError(("unisolvent rank", rank))
    return augmented, rank


def _verify_exact_solution(
    augmented: list[list[int]], solution: dict[str, Any]
) -> tuple[list[Fraction], int]:
    row_gcds = [int(value) for value in solution["row_gcds"]]
    column_gcds = [int(value) for value in solution["column_gcds"]]
    denominator = int(solution["solve_denominator"])
    numerators = [int(value) for value in solution["solve_numerators"]]
    if not (len(row_gcds) == len(column_gcds) == len(numerators) == 117):
        raise ArithmeticError("fraction-free solution shape drift")
    if numerators[-2:] != [0, 0]:
        raise ArithmeticError(("quotient numerators", numerators[-2:]))

    for row_index, original_row in enumerate(augmented):
        common = math.gcd(*(abs(value) for value in original_row)) or 1
        if common != row_gcds[row_index]:
            raise ArithmeticError("row gcd drift")
    reduced_matrix = []
    reduced_rhs = []
    for row, row_gcd in zip(augmented, row_gcds, strict=True):
        reduced_matrix.append(
            [
                value // row_gcd // column_gcd
                for value, column_gcd in zip(row[:-1], column_gcds, strict=True)
            ]
        )
        reduced_rhs.append(row[-1] // row_gcd)
    for column, stored_gcd in enumerate(column_gcds):
        observed = math.gcd(
            *(abs(row[column] * stored_gcd) for row in reduced_matrix)
        ) or 1
        if observed != stored_gcd:
            raise ArithmeticError("column gcd drift")
    for row, rhs in zip(reduced_matrix, reduced_rhs, strict=True):
        if sum(value * numerator for value, numerator in zip(row, numerators, strict=True)) != denominator * rhs:
            raise ArithmeticError("exact fraction-free residual")

    coefficients = [
        Fraction(numerator, denominator * column_gcd)
        for numerator, column_gcd in zip(numerators, column_gcds, strict=True)
    ]
    if [str(value) for value in coefficients] != solution["original_basis_coefficients"]:
        raise ArithmeticError("stored rational coordinate drift")
    if coefficients[-2:] != [Fraction(0), Fraction(0)]:
        raise ArithmeticError("nonzero complement coordinate")
    return coefficients, len(str(abs(denominator)))


def _modular_channels(vector: np.ndarray, prime: int) -> list[np.ndarray]:
    pair = np.outer(vector, vector) % prime
    powers = [pair]
    for _ in range(7):
        powers.append(invariants.integer_pair_casimir(powers[-1]) % prime)
    output = []
    for eigenvalue in projectors.SPECTRAL_EIGENVALUES.values():
        q = np.zeros_like(pair)
        for coefficient, power in zip(
            projectors.projector_polynomial(eigenvalue), powers, strict=True
        ):
            modular = (
                coefficient.numerator
                * pow(coefficient.denominator % prime, -1, prime)
                % prime
            )
            q = (q + modular * power) % prime
        output.append(q)
    return output


def _modular_wedge(vector: np.ndarray, prime: int) -> np.ndarray:
    output = np.zeros(45, dtype=np.int64)
    for left, right, target, coefficient in covariants._disjoint_four_form_pairs():
        output[target] = (
            output[target] + coefficient * vector[left] * vector[right]
        ) % prime
    return output


def verify_live_prime(table: dict[str, Any], prime_index: int) -> None:
    prime = int(table["primes"][prime_index])
    pivots = [int(value) for value in table["trace_pivots"]]
    scales = [int(value) % prime for value in table["trace_scales"]]
    exact = table["selected_exact_augmented_entries"]
    rng = np.random.default_rng(SAMPLE_SEED)
    for sample in range(SAMPLE_COUNT):
        vector = rng.integers(
            -SAMPLE_COORDINATE_BOUND,
            SAMPLE_COORDINATE_BOUND + 1,
            size=210,
            dtype=np.int64,
        ) % prime
        qs = _modular_channels(vector, prime)
        left_cache: dict[tuple[int, int], np.ndarray] = {}
        right_cache: dict[tuple[int, int], np.ndarray] = {}
        trace_values = []
        for pivot, scale in zip(pivots, scales, strict=True):
            residual = 2 if pivot < len(TRIPLES) else 5
            left, middle, right = TRIPLES[pivot % len(TRIPLES)]
            left_key = (residual, left)
            if left_key not in left_cache:
                left_cache[left_key] = qs[residual] @ qs[left] % prime
            left_product = left_cache[left_key]
            right_key = (middle, right)
            if right_key not in right_cache:
                right_cache[right_key] = qs[middle] @ qs[right] % prime
            right_product = right_cache[right_key]
            value = int(
                np.sum(left_product * right_product.T, dtype=np.int64) % prime
            )
            trace_values.append(value * scale % prime)
        norm = int(vector @ vector % prime)
        wedge = _modular_wedge(vector, prime)
        delta = (9 * norm**2 - 5 * int(wedge @ wedge % prime)) % prime
        observed = trace_values + [norm**2 * delta % prime, norm**4 % prime, delta**2 % prime]
        expected = [int(value) % prime for value in exact[sample]]
        if observed != expected:
            raise ArithmeticError(("live table mismatch", prime, sample))


@lru_cache(maxsize=None)
def certificate(live_primes: int = 0) -> dict[str, Any]:
    table, solution = _exact_payload()
    split = invariant_split.certificate()
    if split["core_sha256"] != invariant_split.EXPECTED_CORE_SHA256:
        raise ArithmeticError("O-even dimension certificate drift")
    if split["O10_invariant_dimension"] != 117:
        raise ArithmeticError("O-even dimension is not 117")
    augmented, rank = _verify_height_and_basis(table)
    coefficients, denominator_digits = _verify_exact_solution(augmented, solution)
    if not 0 <= live_primes <= len(table["primes"]):
        raise ValueError("live_primes out of range")
    for prime_index in range(live_primes):
        verify_live_prime(table, prime_index)

    trace_coefficients = [
        coefficient * int(scale) / 25
        for coefficient, scale in zip(
            coefficients[:115], table["trace_scales"], strict=True
        )
    ]
    payload = {
        "status": STATUS,
        "O_even_degree8_dimension": 117,
        "residual_trace_count": 115,
        "complement_basis": ["N^2 delta", "N^4"],
        "table_target": "delta^2=25D^2",
        "delta_definition": "delta=9N^2-5||*(Phi wedge Phi)||^2=5D",
        "unisolvent_rank": rank,
        "crt_prime_count": len(table["primes"]),
        "crt_modulus": table["modulus"],
        "entry_bound": table["entry_bound"],
        "fraction_free_denominator_digits": denominator_digits,
        "complement_solution_coordinates": [str(value) for value in coefficients[-2:]],
        "trace_coefficient_sha256_for_D2": _canonical_sha256(
            [str(value) for value in trace_coefficients]
        ),
        "table_sha256": EXPECTED_SHA256[TABLE],
        "solution_sha256": EXPECTED_SHA256[SOLUTION],
        "live_primes_recomputed": live_primes,
        "conclusion": "q54=q4125=0 implies D^2=0 and hence D=0 over Q/R/C",
        "scope": (
            "global degree-eight conductor only; orbit rigidity and quantitative "
            "distance/positivity integration are separate"
        ),
    }
    payload["core_sha256"] = _canonical_sha256(
        {key: value for key, value in payload.items() if key != "live_primes_recomputed"}
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live-primes", type=int, default=0)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--allow-unfrozen", action="store_true")
    arguments = parser.parse_args()
    payload = certificate(arguments.live_primes)
    if not arguments.allow_unfrozen and payload["core_sha256"] != EXPECTED_CORE_SHA256:
        raise ArithmeticError(
            f"core hash drift: {payload['core_sha256']} != {EXPECTED_CORE_SHA256}"
        )
    if arguments.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(STATUS)
        print("unisolvent rank", payload["unisolvent_rank"])
        print("complement coordinates", payload["complement_solution_coordinates"])
        print("core_sha256", payload["core_sha256"])


if __name__ == "__main__":
    main()
