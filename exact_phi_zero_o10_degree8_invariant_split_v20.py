#!/usr/bin/env python3
"""Exact O(10)/SO(10) split of degree-eight four-form invariants.

Let ``V=Lambda^4(C^10)``.  This module proves

    dim Sym^8(V)^O(10)  = 117,
    dim Sym^8(V)^SO(10) = 137,

so the extra orientation-sensitive (single-epsilon) sector has dimension
20.  This closes an important bookkeeping gap in the real Phi self-zero
problem: every invariant built without the orientation tensor belongs to a
117-dimensional space, not the full 137-dimensional SO(10) space.

The calculation is exact.  The Frobenius character of ``Sym^8(Lambda^4)``
is ``h_8[e_4]``.  Littlewood restriction says that the O(10)-trivial terms
are the Schur terms indexed by even-row partitions of length at most ten;
the determinant terms are indexed by ten-row partitions whose rows are all
odd.  The stable even-row sum is evaluated by

    sum_{lambda even} s_lambda = h_16[h_2]

and the finite-rank exclusions and determinant terms are evaluated with an
independent Murnaghan--Nakayama implementation over exact rationals.

This is an invariant-dimension theorem only.  In particular, it does not by
itself prove that D^2 belongs to the q_54/q_4125 ideal, and it does not close
the global Phi zero-locus classification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from typing import Any, Iterable


STATUS = "EXACT_O10_DEGREE8_INVARIANT_SPLIT__CONDUCTOR_MEMBERSHIP_OPEN"
EXPECTED_CORE_SHA256 = "e02a41591528569de011cc83bc933a8422fd5253f17b6d59581eda0146d1ef63"

EXPECTED_EXCLUDED = (
    ((6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), 0),
    ((5, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1), 0),
    ((5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), 0),
    ((4, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1), 1),
    ((4, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1), 1),
    ((4, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), 0),
    ((4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), 0),
    ((3, 3, 2, 1, 1, 1, 1, 1, 1, 1, 1), 5),
    ((3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), 5),
    ((3, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1), 13),
    ((3, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1), 6),
    ((3, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), 2),
    ((3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), 0),
    ((2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1), 10),
    ((2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1), 15),
    ((2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), 7),
    ((2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), 6),
    ((2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), 1),
    ((1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), 2),
)

EXPECTED_DETERMINANT_TERMS = (
    ((7, 5, 5, 5, 3, 3, 1, 1, 1, 1), 3),
    ((7, 5, 5, 3, 3, 3, 3, 1, 1, 1), 4),
    ((7, 5, 3, 3, 3, 3, 3, 3, 1, 1), 2),
    ((5, 5, 5, 5, 3, 3, 3, 1, 1, 1), 5),
    ((5, 5, 5, 3, 3, 3, 3, 3, 1, 1), 4),
    ((5, 5, 3, 3, 3, 3, 3, 3, 3, 1), 2),
)


def partitions(total: int, maximum: int | None = None) -> Iterable[tuple[int, ...]]:
    if total == 0:
        yield ()
        return
    maximum = total if maximum is None else min(total, maximum)
    for first in range(maximum, 0, -1):
        for rest in partitions(total - first, first):
            yield (first,) + rest


def z_value(partition: tuple[int, ...]) -> int:
    counts = Counter(partition)
    value = 1
    for part, multiplicity in counts.items():
        value *= part**multiplicity * math.factorial(multiplicity)
    return value


def h_of_e4_power_coefficients(degree: int) -> dict[tuple[int, ...], Fraction]:
    """Return ``h_degree[e_4]`` in the power-sum basis."""
    exterior = tuple(
        (
            partition,
            Fraction((-1) ** (4 - len(partition)), z_value(partition)),
        )
        for partition in partitions(4)
    )
    output: defaultdict[tuple[int, ...], Fraction] = defaultdict(Fraction)
    for outer in partitions(degree):
        terms: dict[tuple[int, ...], Fraction] = {
            (): Fraction(1, z_value(outer))
        }
        for scale in outer:
            updated: defaultdict[tuple[int, ...], Fraction] = defaultdict(Fraction)
            for existing, coefficient in terms.items():
                for inner, inner_coefficient in exterior:
                    cycle_type = tuple(
                        sorted(
                            existing + tuple(scale * part for part in inner),
                            reverse=True,
                        )
                    )
                    updated[cycle_type] += coefficient * inner_coefficient
            terms = updated
        for cycle_type, coefficient in terms.items():
            output[cycle_type] += coefficient
    return dict(output)


def h_of_h2_power_coefficients(degree: int) -> dict[tuple[int, ...], Fraction]:
    """Return ``h_degree[h_2]`` in the power-sum basis."""
    output: defaultdict[tuple[int, ...], Fraction] = defaultdict(Fraction)
    for outer in partitions(degree):
        terms: dict[tuple[int, ...], Fraction] = {
            (): Fraction(1, z_value(outer))
        }
        for scale in outer:
            updated: defaultdict[tuple[int, ...], Fraction] = defaultdict(Fraction)
            for existing, coefficient in terms.items():
                # p_scale[h_2]=(p_scale^2+p_(2 scale))/2.
                updated[tuple(sorted(existing + (scale, scale), reverse=True))] += (
                    coefficient / 2
                )
                updated[tuple(sorted(existing + (2 * scale,), reverse=True))] += (
                    coefficient / 2
                )
            terms = updated
        for cycle_type, coefficient in terms.items():
            output[cycle_type] += coefficient
    return dict(output)


def hall_inner_product(
    left: dict[tuple[int, ...], Fraction],
    right: dict[tuple[int, ...], Fraction],
) -> Fraction:
    return sum(
        coefficient * right.get(cycle_type, 0) * z_value(cycle_type)
        for cycle_type, coefficient in left.items()
    )


def _subpartitions_of_size(
    partition: tuple[int, ...], target_size: int
) -> tuple[tuple[int, ...], ...]:
    output: list[tuple[int, ...]] = []

    def recurse(row: int, previous: int, remaining: int, values: list[int]) -> None:
        if row == len(partition):
            if remaining == 0:
                candidate = tuple(values)
                while candidate and candidate[-1] == 0:
                    candidate = candidate[:-1]
                output.append(candidate)
            return
        maximum = min(previous, partition[row], remaining)
        for value in range(maximum, -1, -1):
            recurse(row + 1, value, remaining - value, values + [value])

    recurse(0, partition[0] if partition else 0, target_size, [])
    return tuple(output)


@lru_cache(maxsize=None)
def rim_hook_removals(
    partition: tuple[int, ...], size: int
) -> tuple[tuple[tuple[int, ...], int], ...]:
    target = sum(partition) - size
    if target < 0:
        return ()
    output = []
    for smaller in _subpartitions_of_size(partition, target):
        cells = set()
        for row, length in enumerate(partition):
            retained = smaller[row] if row < len(smaller) else 0
            cells.update((row, column) for column in range(retained, length))
        if len(cells) != size or not cells:
            continue
        reached = {next(iter(cells))}
        frontier = list(reached)
        while frontier:
            row, column = frontier.pop()
            for neighbour in (
                (row - 1, column),
                (row + 1, column),
                (row, column - 1),
                (row, column + 1),
            ):
                if neighbour in cells and neighbour not in reached:
                    reached.add(neighbour)
                    frontier.append(neighbour)
        if reached != cells:
            continue
        if any(
            (row + 1, column) in cells
            and (row, column + 1) in cells
            and (row + 1, column + 1) in cells
            for row, column in cells
        ):
            continue
        height = len({row for row, _column in cells})
        output.append((smaller, -1 if (height - 1) & 1 else 1))
    return tuple(output)


@lru_cache(maxsize=None)
def symmetric_group_character(
    partition: tuple[int, ...], cycle_type: tuple[int, ...]
) -> int:
    if not cycle_type:
        return int(not partition)
    if sum(partition) != sum(cycle_type):
        return 0
    first = cycle_type[0]
    return sum(
        sign * symmetric_group_character(smaller, cycle_type[1:])
        for smaller, sign in rim_hook_removals(partition, first)
    )


def schur_coefficient(
    partition: tuple[int, ...],
    power_coefficients: dict[tuple[int, ...], Fraction],
) -> int:
    value = sum(
        coefficient * symmetric_group_character(partition, cycle_type)
        for cycle_type, coefficient in power_coefficients.items()
    )
    if value.denominator != 1:
        raise ArithmeticError((partition, value))
    return value.numerator


def _jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    return value


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(_jsonable(value), sort_keys=True, separators=(",", ":")).encode(
            "ascii"
        )
    ).hexdigest()


@lru_cache(maxsize=1)
def certificate() -> dict[str, Any]:
    plethysm = h_of_e4_power_coefficients(8)
    stable_even = hall_inner_product(plethysm, h_of_h2_power_coefficients(16))
    if stable_even.denominator != 1:
        raise ArithmeticError(stable_even)

    excluded = tuple(
        (
            partition,
            schur_coefficient(tuple(2 * part for part in partition), plethysm),
        )
        for partition in partitions(16)
        if len(partition) > 10
    )
    determinant_terms = []
    determinant_target_count = 0
    for partition in partitions(11):
        if len(partition) > 10:
            continue
        determinant_target_count += 1
        padded = partition + (0,) * (10 - len(partition))
        target = tuple(2 * part + 1 for part in padded)
        coefficient = schur_coefficient(target, plethysm)
        if coefficient:
            determinant_terms.append((target, coefficient))
    determinant_terms = tuple(determinant_terms)

    excluded_sum = sum(coefficient for _partition, coefficient in excluded)
    determinant_dimension = sum(
        coefficient for _partition, coefficient in determinant_terms
    )
    o_dimension = stable_even.numerator - excluded_sum
    so_dimension = o_dimension + determinant_dimension

    if excluded != EXPECTED_EXCLUDED:
        raise ArithmeticError("finite-rank even-row census drift")
    if determinant_terms != EXPECTED_DETERMINANT_TERMS:
        raise ArithmeticError("determinant-row census drift")
    if (stable_even, excluded_sum, o_dimension) != (Fraction(191), 74, 117):
        raise ArithmeticError("O(10) dimension drift")
    if (determinant_target_count, determinant_dimension, so_dimension) != (
        55,
        20,
        137,
    ):
        raise ArithmeticError("SO(10) dimension drift")

    payload = {
        "status": STATUS,
        "representation": "Sym^8(Lambda^4(C^10))",
        "frobenius_character": "h_8[e_4]",
        "stable_even_identity": "sum_{lambda even} s_lambda=h_16[h_2]",
        "stable_even_multiplicity": stable_even.numerator,
        "finite_rank_excluded_terms": excluded,
        "finite_rank_excluded_sum": excluded_sum,
        "O10_invariant_dimension": o_dimension,
        "determinant_target_count": determinant_target_count,
        "nonzero_determinant_terms": determinant_terms,
        "determinant_sector_dimension": determinant_dimension,
        "SO10_invariant_dimension": so_dimension,
        "scope": (
            "degree-eight invariant census only; D^2 ideal membership and "
            "global Phi-zero classification remain open"
        ),
    }
    payload["core_sha256"] = _canonical_sha256(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--allow-unfrozen", action="store_true")
    arguments = parser.parse_args()
    payload = certificate()
    if not arguments.allow_unfrozen and payload["core_sha256"] != EXPECTED_CORE_SHA256:
        raise ArithmeticError(
            f"core hash drift: {payload['core_sha256']} != {EXPECTED_CORE_SHA256}"
        )
    if arguments.json:
        print(json.dumps(_jsonable(payload), indent=2, sort_keys=True))
    else:
        print(STATUS)
        print("O(10) dimension", payload["O10_invariant_dimension"])
        print("determinant sector", payload["determinant_sector_dimension"])
        print("SO(10) dimension", payload["SO10_invariant_dimension"])
        print("core_sha256", payload["core_sha256"])


if __name__ == "__main__":
    main()
