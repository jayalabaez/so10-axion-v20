#!/usr/bin/env python3
"""Charge-independent minimality audit for the Z17 spectator sector.

Every spectator pair is massed by ``S`` and therefore has residues
``(a_i, 13-a_i)``.  The mixed Spin(10)^2-Z17 anomaly depends only on the
pair sum, so the lower bound on the number of pairs does not require the
identical-pair ansatz.  Residue uniqueness does require that ansatz.
"""

from __future__ import annotations

import itertools
import json


N = 17
PAIR_SUM = 13


def mixed_class(k: int) -> int:
    """Mixed anomaly residue for ``k`` arbitrary S-massed pairs."""
    return (6 + 2 * PAIR_SUM * k) % N


def gravitational_class(k: int) -> int:
    return (48 + 16 * PAIR_SUM * k) % N


def cubic_class(charges: tuple[int, ...]) -> int:
    return (
        48
        + 16
        * sum(a**3 + (PAIR_SUM - a) ** 3 for a in charges)
    ) % N


def allowed_pair_counts(limit: int = N) -> list[int]:
    return [k for k in range(1, limit + 1) if mixed_class(k) == 0]


def exhaustive_solutions(k: int) -> list[tuple[int, ...]]:
    """Ordered residue tuples satisfying all three anomaly classes."""
    if mixed_class(k) or gravitational_class(k):
        return []
    return [
        charges
        for charges in itertools.product(range(N), repeat=k)
        if cubic_class(charges) == 0
    ]


def count_cubic_solutions(k: int) -> int:
    """Count ordered solutions by exact cyclic convolution."""
    one_pair = [0] * N
    for a in range(N):
        one_pair[(a**3 + (PAIR_SUM - a) ** 3) % N] += 1

    distribution = [0] * N
    distribution[0] = 1
    for _ in range(k):
        updated = [0] * N
        for old_residue, old_count in enumerate(distribution):
            for pair_residue, pair_count in enumerate(one_pair):
                updated[(old_residue + pair_residue) % N] += old_count * pair_count
        distribution = updated

    inverse_16 = pow(16, -1, N)
    target = (-48 * inverse_16) % N
    return distribution[target] if not mixed_class(k) and not gravitational_class(k) else 0


def identical_pair_solutions(k: int = 5) -> list[tuple[int, int]]:
    """Unordered residue pairs for the identical-pair restriction."""
    solutions = set()
    for a in range(N):
        b = (PAIR_SUM - a) % N
        charges = (a,) * k
        if not mixed_class(k) and not gravitational_class(k) and not cubic_class(charges):
            solutions.add(tuple(sorted((a, b))))
    return sorted(solutions)


def build_report() -> dict:
    no_small = {str(k): len(exhaustive_solutions(k)) for k in range(1, 5)}
    return {
        "modulus": N,
        "pair_sum_mod_17": PAIR_SUM,
        "mixed_class_formula": "6 + 2*13*k = 6 + 9*k (mod 17)",
        "allowed_k_1_through_17": allowed_pair_counts(),
        "solutions_k_1_through_4": no_small,
        "general_minimum_k": 5,
        "ordered_general_solutions_at_k5": count_cubic_solutions(5),
        "ordered_tuples_at_k5": N**5,
        "general_cubic_formula": "48 + 16*sum_i[a_i^3+(13-a_i)^3] (mod 17)",
        "alternate_formula_correction": (
            "the supplied alternate engine used 80 times the per-pair sum; "
            "16 is the per-pair multiplicity and 80 applies only after five identical pairs. "
            "The corrected cyclic convolution happens to give the same count, 83232."
        ),
        "identical_pair_residue_solutions_at_k5": identical_pair_solutions(),
        "scope": (
            "five-pair minimality is charge-independent; residue uniqueness "
            "is only an identical-pair statement"
        ),
    }


if __name__ == "__main__":
    print(json.dumps(build_report(), indent=2))
