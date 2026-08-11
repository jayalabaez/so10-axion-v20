#!/usr/bin/env python3
"""Exact-entry CRT reconstruction of the degree-eight D^2 conductor identity."""
from __future__ import annotations

import importlib.util
import itertools
import json
import math
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "reconstruct_exact_phi_zero_degree8_radical_v20.py"
saved_argv = sys.argv
sys.argv = [str(SOURCE), "10007", "125", "reconstruct"]
spec = importlib.util.spec_from_file_location("degree8", SOURCE)
assert spec is not None and spec.loader is not None
degree8 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(degree8)
sys.argv = saved_argv

PRIMES = (
    10_000_019,
    10_000_079,
    10_000_103,
    10_000_121,
    10_000_139,
    10_000_141,
    10_000_169,
    10_000_189,
)
SAMPLE_COUNT = 125
RNG_SEED = 20_260_810
TRIPLES = tuple(itertools.combinations_with_replacement(range(8), 3))


def rational_reconstruct(value: int, modulus: int) -> Fraction | None:
    value %= modulus
    bound = math.isqrt(modulus // 2)
    old_r, r = modulus, value
    old_t, t = 0, 1
    while r > bound:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_t, t = t, old_t - quotient * t
    if t < 0:
        r, t = -r, -t
    if not t or abs(r) > bound or t > bound or math.gcd(r, t) != 1:
        return None
    if (r - value * t) % modulus:
        return None
    return Fraction(r, t)


def configure(prime: int) -> None:
    degree8.P = prime
    degree8.COEFFICIENTS = {
        name: tuple(
            value.numerator % prime
            * pow(value.denominator % prime, -1, prime)
            % prime
            for value in degree8.projectors.projector_polynomial(eigenvalue)
        )
        for name, eigenvalue in degree8.projectors.SPECTRAL_EIGENVALUES.items()
    }


def projector_denominators() -> tuple[int, ...]:
    output = []
    for eigenvalue in degree8.projectors.SPECTRAL_EIGENVALUES.values():
        denominator = 1
        for coefficient in degree8.projectors.projector_polynomial(eigenvalue):
            denominator = math.lcm(denominator, coefficient.denominator)
        output.append(denominator)
    return tuple(output)


def trace_column_scale(index: int, denominators: tuple[int, ...]) -> int:
    residual = 2 if index < len(TRIPLES) else 5
    left, middle, right = TRIPLES[index % len(TRIPLES)]
    return (
        denominators[residual]
        * denominators[left]
        * denominators[middle]
        * denominators[right]
    )


def row_pivots_mod(matrix: np.ndarray, prime: int) -> list[int]:
    work = np.asarray(matrix, dtype=np.int64).T.copy() % prime
    row = 0
    pivots = []
    for column in range(work.shape[1]):
        candidates = np.flatnonzero(work[row:, column])
        if not candidates.size:
            continue
        pivot = row + int(candidates[0])
        work[[row, pivot]] = work[[pivot, row]]
        work[row] = work[row] * pow(int(work[row, column]), -1, prime) % prime
        for target in range(work.shape[0]):
            if target != row and work[target, column]:
                work[target] = (
                    work[target] - work[target, column] * work[row]
                ) % prime
        pivots.append(column)
        row += 1
        if row == work.shape[0]:
            break
    return pivots


def modular_rows(prime: int, trace_pivots: list[int] | None):
    configure(prime)
    denominators = projector_denominators()
    rng = np.random.default_rng(RNG_SEED)
    all_trace_rows = []
    auxiliary_rows = []
    targets = []
    for _sample in range(SAMPLE_COUNT):
        vector = rng.integers(-3, 4, size=210, dtype=np.int64) % prime
        features, _unused_target = degree8.evaluate(vector)
        all_trace_rows.append(features[: 2 * len(TRIPLES)])
        norm = int(vector @ vector % prime)
        wedge = degree8.hodge_square(vector)
        delta = (9 * norm**2 - 5 * int(wedge @ wedge % prime)) % prime
        auxiliary_rows.append((norm**2 * delta % prime, norm**4 % prime))
        targets.append(delta**2 % prime)

    all_trace = np.asarray(all_trace_rows, dtype=np.int64)
    if trace_pivots is None:
        _solution, trace_pivots = degree8.solve_mod(
            all_trace, np.asarray(targets, dtype=np.int64)
        )
        if len(trace_pivots) != 115:
            raise ArithmeticError(("trace rank", len(trace_pivots)))
    scales = np.asarray(
        [trace_column_scale(index, denominators) % prime for index in trace_pivots],
        dtype=np.int64,
    )
    scaled_trace = all_trace[:, trace_pivots] * scales[None, :] % prime
    basis = np.column_stack(
        [scaled_trace, np.asarray(auxiliary_rows, dtype=np.int64)]
    )
    return basis, np.asarray(targets, dtype=np.int64), trace_pivots


def crt_update(combined: list[int], residues: np.ndarray, modulus: int, prime: int):
    inverse = pow(modulus % prime, -1, prime)
    flat = residues.ravel()
    if not combined:
        combined.extend(int(value) for value in flat)
        return
    for index, residue in enumerate(flat):
        correction = (int(residue) - combined[index]) % prime * inverse % prime
        combined[index] += modulus * correction


def main() -> None:
    start = time.time()
    checkpoint_path = (
        HERE / "EXACT_PHI_ZERO_DEGREE8_CONDUCTOR_RECONSTRUCTION_CHECKPOINT.json"
    )
    if checkpoint_path.exists():
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        processed = int(checkpoint["processed"])
        trace_pivots = [int(value) for value in checkpoint["trace_pivots"]]
        sample_pivots = [int(value) for value in checkpoint["sample_pivots"]]
        combined_entries = [int(value) for value in checkpoint["combined_entries"]]
        combined_solution = [int(value) for value in checkpoint["combined_solution"]]
        modulus = int(checkpoint["modulus"])
        print("resuming", processed, "primes", "digits", len(str(modulus)), flush=True)
    else:
        processed = 0
        trace_pivots = None
        sample_pivots = None
        combined_entries: list[int] = []
        combined_solution: list[int] = []
        modulus = 1
    selected_shape = (117, 118)
    denominators = projector_denominators()
    trace_scales = (
        tuple(trace_column_scale(index, denominators) for index in trace_pivots)
        if trace_pivots is not None
        else None
    )

    for prime_index, prime in enumerate(PRIMES[processed:], start=processed):
        basis, targets, observed_trace_pivots = modular_rows(prime, trace_pivots)
        if trace_pivots is None:
            trace_pivots = observed_trace_pivots
            trace_scales = tuple(
                trace_column_scale(index, denominators) for index in trace_pivots
            )
            sample_pivots = row_pivots_mod(basis, prime)
            if len(sample_pivots) != 117:
                raise ArithmeticError(("basis rank", len(sample_pivots)))
        elif observed_trace_pivots != trace_pivots:
            raise ArithmeticError("trace pivots drifted")
        assert sample_pivots is not None
        selected_basis = basis[sample_pivots]
        selected_targets = targets[sample_pivots]
        selected_shape = (len(sample_pivots), basis.shape[1] + 1)
        augmented = np.column_stack([selected_basis, selected_targets])
        solution, solution_pivots = degree8.solve_mod(
            selected_basis, selected_targets
        )
        if len(solution_pivots) != 117:
            raise ArithmeticError("selected basis singular")
        crt_update(combined_entries, augmented, modulus, prime)
        crt_update(combined_solution, solution, modulus, prime)
        modulus *= prime
        checkpoint_path.write_text(
            json.dumps(
                {
                    "processed": prime_index + 1,
                    "trace_pivots": trace_pivots,
                    "sample_pivots": sample_pivots,
                    "combined_entries": [str(value) for value in combined_entries],
                    "combined_solution": [str(value) for value in combined_solution],
                    "modulus": str(modulus),
                }
            ),
            encoding="utf-8",
        )
        reconstructed = [
            rational_reconstruct(value, modulus) for value in combined_solution
        ]
        print(
            "prime",
            prime,
            "digits",
            len(str(modulus)),
            "coefficients",
            sum(value is not None for value in reconstructed),
            "last",
            reconstructed[-2:],
            "elapsed",
            f"{time.time()-start:.1f}s",
            flush=True,
        )

    assert trace_pivots is not None and sample_pivots is not None
    assert trace_scales is not None and selected_shape is not None
    nmax = 210 * 3**2
    entry_bound = max(trace_scales) * nmax**4
    # The trace bound dominates the elementary N,D columns by many orders.
    if modulus <= 2 * entry_bound:
        raise ArithmeticError(("CRT modulus too small", modulus, entry_bound))
    centered = [value if value <= modulus // 2 else value - modulus for value in combined_entries]
    if max(abs(value) for value in centered) > entry_bound:
        raise ArithmeticError("entry height bound failed")
    exact_augmented = np.asarray(centered, dtype=object).reshape(selected_shape)
    reconstructed = [
        rational_reconstruct(value, modulus) for value in combined_solution
    ]
    coefficients = reconstructed
    if coefficients[-2:] != [Fraction(0), Fraction(0)]:
        raise ArithmeticError(("quotient coefficients", coefficients[-2:]))
    exact_identity_verified = False
    if all(value is not None for value in coefficients):
        exact_coefficients = [value for value in coefficients if value is not None]
        for row in exact_augmented:
            lhs = sum(
                coefficient * int(value)
                for coefficient, value in zip(exact_coefficients, row[:-1], strict=True)
            )
            if lhs != int(row[-1]):
                raise ArithmeticError("exact reconstructed-entry identity failed")
        exact_identity_verified = True

    output = {
        "primes": PRIMES,
        "modulus": str(modulus),
        "entry_bound": str(entry_bound),
        "trace_pivots": trace_pivots,
        "sample_pivots": sample_pivots,
        "trace_scales": [str(value) for value in trace_scales],
        "coefficients": [str(value) if value is not None else None for value in coefficients],
        "reconstructed_coefficient_count": sum(value is not None for value in coefficients),
        "quotient_coefficients_N2D_N4": [str(value) for value in coefficients[-2:]],
        "exact_identity_verified_from_reconstructed_coefficients": exact_identity_verified,
        "selected_exact_augmented_entries": [
            [str(value) for value in row] for row in exact_augmented
        ],
        "elapsed_seconds": time.time() - start,
    }
    destination = HERE / "EXACT_PHI_ZERO_DEGREE8_CONDUCTOR_EVALUATION_TABLE.json"
    destination.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(
        "ENTRY_TABLE_PASS",
        destination,
        "coefficient_count",
        output["reconstructed_coefficient_count"],
        "elapsed",
        f"{time.time()-start:.1f}s",
    )


if __name__ == "__main__":
    main()
