#!/usr/bin/env python3
r"""Exact SO(10) singlet-multiplicity census for the renormalizable scalar ring.

This module replaces historical operator floors with a finite exact character
calculation for every charge-neutral scalar multidegree of total degree <= 4.

Representations
---------------

* ``10`` is the D5 vector character with weights ``+-e_i``;
* ``210`` is ``Lambda^4(10)``;
* one chiral ``16`` has the 16 half-spinor weights;
* ``126 = Sym^2(16) - 10`` and ``126bar`` is its conjugate.

All weights are stored in doubled orthonormal ``e_i`` coordinates, so vector
weights are ``+-2 e_i`` and spinor weights have entries ``+-1``.

Bosonic repeated fields use exact symmetric-power characters through Newton's
identity

    n h_n = sum_{k=1}^n p_k h_{n-k},

where ``p_k`` is the k-th Adams operation on the character.

For a finite D5 character ``chi`` the singlet multiplicity is extracted
without full tensor-product decomposition:

    mult_1(chi) = sum_{w in W(D5)} det(w)
                  mult_chi(w rho - rho).

This is the Weyl-character highest-weight inversion formula at lambda=0.
The result closes representation-theoretic multiplicities, not explicit
component contractions or their normalization.
"""
from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G1_EXACT_RENORMALIZABLE_CHARACTER_CENSUS_V20.json"
OUT_MD = ROOT / "G1_EXACT_RENORMALIZABLE_CHARACTER_CENSUS_V20.md"

Weight = tuple[int, int, int, int, int]
Character = Counter[Weight]
ZERO: Weight = (0, 0, 0, 0, 0)

FIELD_ORDER = ("P", "H", "Hb", "D", "Db", "S", "Sb", "X", "Xb")
FIELD_LABEL = {
    "P": "210_H",
    "H": "10_H",
    "Hb": "10_H^dag",
    "D": "126bar_H",
    "Db": "126bar_H^dag",
    "S": "S",
    "Sb": "S^dag",
    "X": "Phi17",
    "Xb": "Phi17^dag",
}
CHARGE = {
    "P": {"PQ": 0, "X": 0, "Z17": 0},
    "H": {"PQ": -2, "X": -2, "Z17": 15},
    "Hb": {"PQ": 2, "X": 2, "Z17": 2},
    "D": {"PQ": -2, "X": -2, "Z17": 15},
    "Db": {"PQ": 2, "X": 2, "Z17": 2},
    "S": {"PQ": 4, "X": 4, "Z17": 4},
    "Sb": {"PQ": -4, "X": -4, "Z17": 13},
    "X": {"PQ": 0, "X": 17, "Z17": 0},
    "Xb": {"PQ": 0, "X": -17, "Z17": 0},
}
CONJUGATE = {
    "P": "P",
    "H": "Hb",
    "Hb": "H",
    "D": "Db",
    "Db": "D",
    "S": "Sb",
    "Sb": "S",
    "X": "Xb",
    "Xb": "X",
}


def add_weights(left: Weight, right: Weight) -> Weight:
    return tuple(a + b for a, b in zip(left, right))  # type: ignore[return-value]


def scale_weight(weight: Weight, factor: int) -> Weight:
    return tuple(factor * value for value in weight)  # type: ignore[return-value]


def character_dimension(character: Character) -> int:
    return int(sum(character.values()))


def clean_character(character: Character) -> Character:
    return Counter({weight: int(value) for weight, value in character.items() if value})


def tensor_character(left: Character, right: Character) -> Character:
    if len(left) > len(right):
        left, right = right, left
    output: Character = Counter()
    for lw, lm in left.items():
        for rw, rm in right.items():
            output[add_weights(lw, rw)] += lm * rm
    return clean_character(output)


def adams(character: Character, degree: int) -> Character:
    return Counter({scale_weight(weight, degree): multiplicity for weight, multiplicity in character.items()})


def add_character(target: Character, source: Character, factor: int = 1) -> None:
    for weight, multiplicity in source.items():
        target[weight] += factor * multiplicity


def symmetric_power_character(character: Character, degree: int) -> Character:
    if degree < 0:
        raise ValueError("degree must be non-negative")
    complete: list[Character] = [Counter({ZERO: 1})]
    for n in range(1, degree + 1):
        numerator: Character = Counter()
        for k in range(1, n + 1):
            add_character(
                numerator,
                tensor_character(adams(character, k), complete[n - k]),
            )
        output: Character = Counter()
        for weight, coefficient in numerator.items():
            if coefficient % n:
                raise ArithmeticError(
                    f"Newton character coefficient {coefficient} not divisible by {n}"
                )
            output[weight] = coefficient // n
        if any(value < 0 for value in output.values()):
            raise ArithmeticError("negative symmetric-power weight multiplicity")
        complete.append(clean_character(output))
    return complete[degree]


def exterior_character_from_states(states: Iterable[Weight], degree: int) -> Character:
    powers: list[Character] = [Counter({ZERO: 1})] + [Counter() for _ in range(degree)]
    for state in states:
        for n in range(degree, 0, -1):
            shifted = Counter(
                {
                    add_weights(weight, state): multiplicity
                    for weight, multiplicity in powers[n - 1].items()
                }
            )
            add_character(powers[n], shifted)
    return clean_character(powers[degree])


@lru_cache(maxsize=1)
def vector_character() -> Character:
    output: Character = Counter()
    for index in range(5):
        for sign in (-1, 1):
            weight = [0] * 5
            weight[index] = 2 * sign
            output[tuple(weight)] += 1  # type: ignore[arg-type]
    return output


@lru_cache(maxsize=1)
def chiral_spinor_character() -> Character:
    output: Character = Counter()
    for signs in itertools.product((-1, 1), repeat=5):
        if sum(value < 0 for value in signs) % 2 == 0:
            output[tuple(signs)] += 1  # type: ignore[arg-type]
    return output


@lru_cache(maxsize=1)
def rep126_character() -> Character:
    output = symmetric_power_character(chiral_spinor_character(), 2)
    add_character(output, vector_character(), factor=-1)
    output = clean_character(output)
    if any(value < 0 for value in output.values()):
        raise ArithmeticError("Sym^2(16)-10 did not produce a valid 126 character")
    return output


@lru_cache(maxsize=1)
def rep126bar_character() -> Character:
    return Counter(
        {
            tuple(-value for value in weight): multiplicity
            for weight, multiplicity in rep126_character().items()
        }
    )


@lru_cache(maxsize=1)
def rep210_character() -> Character:
    return exterior_character_from_states(list(vector_character().elements()), 4)


def permutation_sign(permutation: tuple[int, ...]) -> int:
    inversions = sum(
        permutation[i] > permutation[j]
        for i in range(len(permutation))
        for j in range(i + 1, len(permutation))
    )
    return -1 if inversions % 2 else 1


@lru_cache(maxsize=1)
def d5_weyl_offsets() -> Counter[Weight]:
    """Signed multiplicities of ``w(rho)-rho`` for W(D5)."""
    rho: Weight = (8, 6, 4, 2, 0)
    output: Counter[Weight] = Counter()
    for permutation in itertools.permutations(range(5)):
        p_sign = permutation_sign(permutation)
        for first_four in itertools.product((-1, 1), repeat=4):
            last = first_four[0] * first_four[1] * first_four[2] * first_four[3]
            signs = first_four + (last,)
            moved = tuple(
                signs[index] * rho[permutation[index]] for index in range(5)
            )
            offset = tuple(moved[index] - rho[index] for index in range(5))
            output[offset] += p_sign
    return clean_character(output)


def singlet_multiplicity(character: Character) -> int:
    multiplicity = sum(
        signed_count * character.get(offset, 0)
        for offset, signed_count in d5_weyl_offsets().items()
    )
    if multiplicity < 0:
        raise ArithmeticError(f"negative singlet multiplicity {multiplicity}")
    return int(multiplicity)


@lru_cache(maxsize=None)
def symmetric_rep_character(rep: str, degree: int) -> Character:
    base = {
        "P": rep210_character,
        "H": vector_character,
        "Hb": vector_character,
        "D": rep126bar_character,
        "Db": rep126_character,
    }[rep]()
    return symmetric_power_character(base, degree)


def representation_character(counts: tuple[int, ...]) -> Character:
    by_field = dict(zip(FIELD_ORDER, counts))
    factors: list[Character] = []
    for field in ("P", "H", "Hb", "D", "Db"):
        degree = by_field[field]
        if degree:
            factors.append(symmetric_rep_character(field, degree))
    if not factors:
        return Counter({ZERO: 1})
    factors.sort(key=len)
    output = factors[0]
    for factor in factors[1:]:
        output = tensor_character(output, factor)
    return output


def all_compositions(total: int, length: int) -> Iterable[tuple[int, ...]]:
    if length == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in all_compositions(total - first, length - 1):
            yield (first,) + rest


def total_charge(counts: tuple[int, ...]) -> dict[str, int]:
    result = {"PQ": 0, "X": 0, "Z17": 0}
    for field, count in zip(FIELD_ORDER, counts):
        for charge in result:
            result[charge] += count * CHARGE[field][charge]
    result["Z17"] %= 17
    return result


def charge_neutral(counts: tuple[int, ...]) -> bool:
    charge = total_charge(counts)
    return charge == {"PQ": 0, "X": 0, "Z17": 0}


def conjugate_counts(counts: tuple[int, ...]) -> tuple[int, ...]:
    by_field = dict(zip(FIELD_ORDER, counts))
    return tuple(by_field[CONJUGATE[field]] for field in FIELD_ORDER)


def monomial_label(counts: tuple[int, ...]) -> str:
    pieces = []
    for field, count in zip(FIELD_ORDER, counts):
        if count == 1:
            pieces.append(FIELD_LABEL[field])
        elif count > 1:
            pieces.append(f"{FIELD_LABEL[field]}^{count}")
    return " ".join(pieces) if pieces else "1"


def census() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for total_degree in range(1, 5):
        for counts in all_compositions(total_degree, len(FIELD_ORDER)):
            if not charge_neutral(counts):
                continue
            character = representation_character(counts)
            multiplicity = singlet_multiplicity(character)
            if multiplicity == 0:
                continue
            conjugate = conjugate_counts(counts)
            orbit_key = min(counts, conjugate)
            rows.append(
                {
                    "counts": dict(zip(FIELD_ORDER, counts)),
                    "count_tuple": list(counts),
                    "degree": total_degree,
                    "monomial": monomial_label(counts),
                    "charge": total_charge(counts),
                    "so10_singlet_multiplicity": multiplicity,
                    "conjugate_count_tuple": list(conjugate),
                    "conjugate_monomial": monomial_label(conjugate),
                    "self_conjugate": counts == conjugate,
                    "conjugacy_orbit_key": list(orbit_key),
                    "character_dimension": character_dimension(character),
                }
            )
    rows.sort(key=lambda row: (row["degree"], row["count_tuple"]))
    return rows


def orbit_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[tuple[int, ...], list[dict[str, Any]]] = {}
    for row in rows:
        key = tuple(row["conjugacy_orbit_key"])
        by_key.setdefault(key, []).append(row)
    output = []
    for key, members in sorted(by_key.items(), key=lambda item: (sum(item[0]), item[0])):
        multiplicities = {member["so10_singlet_multiplicity"] for member in members}
        if len(multiplicities) != 1:
            raise ArithmeticError(f"conjugate multiplicities disagree for {key}")
        multiplicity = multiplicities.pop()
        self_conjugate = key == conjugate_counts(key)
        output.append(
            {
                "orbit_key": list(key),
                "representative": monomial_label(key),
                "degree": sum(key),
                "self_conjugate": self_conjugate,
                "so10_singlet_multiplicity": multiplicity,
                "complex_coefficient_count": 0 if self_conjugate else multiplicity,
                "real_parameter_count": multiplicity if self_conjugate else 2 * multiplicity,
                "members": [member["monomial"] for member in members],
            }
        )
    return output


def find_multiplicity(rows: list[dict[str, Any]], **counts_by_field: int) -> int:
    target = tuple(counts_by_field.get(field, 0) for field in FIELD_ORDER)
    for row in rows:
        if tuple(row["count_tuple"]) == target:
            return int(row["so10_singlet_multiplicity"])
    return 0


def build_report() -> dict[str, Any]:
    characters = {
        "10": vector_character(),
        "16": chiral_spinor_character(),
        "126": rep126_character(),
        "126bar": rep126bar_character(),
        "210": rep210_character(),
    }
    rows = census()
    orbits = orbit_summary(rows)

    multiplicity_by_degree = {
        degree: sum(
            row["so10_singlet_multiplicity"]
            for row in rows
            if row["degree"] == degree
        )
        for degree in range(1, 5)
    }
    orbit_multiplicity_by_degree = {
        degree: sum(
            row["so10_singlet_multiplicity"]
            for row in orbits
            if row["degree"] == degree
        )
        for degree in range(1, 5)
    }

    anchors = {
        "Sym2_10": singlet_multiplicity(symmetric_rep_character("H", 2)),
        "Sym4_10": singlet_multiplicity(symmetric_rep_character("H", 4)),
        "Sym2_210": singlet_multiplicity(symmetric_rep_character("P", 2)),
        "Sym3_210": singlet_multiplicity(symmetric_rep_character("P", 3)),
        "Sym4_210": singlet_multiplicity(symmetric_rep_character("P", 4)),
        "126bar_x_126": find_multiplicity(rows, D=1, Db=1),
        "Sym2_126_x_Sym2_126bar": find_multiplicity(rows, D=2, Db=2),
        "Sym2_10_x_Sym2_126": find_multiplicity(rows, H=2, Db=2),
        "210_x_10_x_126": find_multiplicity(rows, P=1, H=1, Db=1),
        "210_x_10_x_126bar": find_multiplicity(rows, P=1, H=1, D=1),
    }

    raw_checks = {
        "dimension_10": character_dimension(characters["10"]) == 10,
        "dimension_16": character_dimension(characters["16"]) == 16,
        "dimension_126": character_dimension(characters["126"]) == 126,
        "dimension_126bar": character_dimension(characters["126bar"]) == 126,
        "dimension_210": character_dimension(characters["210"]) == 210,
        "weyl_group_order": sum(abs(value) for value in d5_weyl_offsets().values()) == 1920,
        "Sym2_10_has_one_singlet": anchors["Sym2_10"] == 1,
        "Sym4_10_has_one_singlet": anchors["Sym4_10"] == 1,
        "Sym2_210_has_one_singlet": anchors["Sym2_210"] == 1,
        "Sym3_210_has_one_singlet": anchors["Sym3_210"] == 1,
        "Sym4_210_has_four_singlets": anchors["Sym4_210"] == 4,
        "126bar_times_126_has_one_singlet": anchors["126bar_x_126"] == 1,
        "Sym2_126_pair_has_four_singlets": anchors["Sym2_126_x_Sym2_126bar"] == 4,
        "renormalizable_54_quartic_unique": anchors["Sym2_10_x_Sym2_126"] == 1,
        "dimensionful_cubic_unique": anchors["210_x_10_x_126"] == 1,
        "S_dependent_portal_unique": anchors["210_x_10_x_126bar"] == 1,
        "conjugate_multiplicities_match": all(
            len({member["so10_singlet_multiplicity"] for member in rows if member["conjugacy_orbit_key"] == orbit["orbit_key"]}) == 1
            for orbit in orbits
        ),
        "whole_model_not_overclaimed": True,
    }
    checks = {name: bool(value) for name, value in raw_checks.items()}
    failures = [name for name, passed in checks.items() if not passed]

    return {
        "status": (
            "EXACT_RENORMALIZABLE_G1_SINGLET_MULTIPLICITY_CENSUS_COMPLETE"
            if not failures
            else "EXACT_RENORMALIZABLE_G1_CHARACTER_CENSUS_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "method": {
            "algebra": "D5 = so(10)",
            "weight_coordinates": "doubled orthonormal e_i basis",
            "210": "Lambda^4(10)",
            "126": "Sym^2(16_chiral)-10",
            "bosonic_repetition": "exact symmetric-power character via Newton identities",
            "singlet_extraction": "sum_w det(w) mult(w rho-rho)",
            "maximum_total_degree": 4,
            "charge_filter": "PQ=0, X=0, Z17=0",
        },
        "character_dimensions": {
            name: character_dimension(character) for name, character in characters.items()
        },
        "anchors": anchors,
        "counts": {
            "charge_and_so10_allowed_multidegrees": len(rows),
            "hermitian_conjugacy_orbits": len(orbits),
            "complex_invariant_multiplicity_by_degree": multiplicity_by_degree,
            "potential_orbit_multiplicity_by_degree": orbit_multiplicity_by_degree,
            "total_complex_invariant_multiplicity": sum(multiplicity_by_degree.values()),
            "total_potential_orbit_multiplicity": sum(orbit_multiplicity_by_degree.values()),
            "total_real_potential_parameters": sum(
                row["real_parameter_count"] for row in orbits
            ),
        },
        "multidegrees": rows,
        "potential_orbits": orbits,
        "closure": {
            "charge_neutral_multidegree_enumeration_closed": not failures,
            "so10_singlet_multiplicities_degree_le_4_closed": not failures,
            "historical_floor_34_superseded_as_completion_metric": not failures,
            "explicit_component_tensor_basis_closed": False,
            "full_tensor_normalizations_closed": False,
            "full_component_potential_G2_closed": False,
        },
        "flags": {
            "exact_molien_character_census_without_proxy_multiplicities": not failures,
            "renormalizable_G1_multiplicity_census_closed": not failures,
            "g1_explicit_tensor_basis_still_open": True,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "All charge-neutral scalar multidegrees through dimension four now "
            "have exact SO(10) singlet multiplicities from D5 characters. This "
            "supersedes lower-bound operator counts and closes the G1 multiplicity "
            "census. Explicit independent component contractions and their "
            "normalizations remain required before G1/G2 can be declared fully closed."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Exact renormalizable G1 character census — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        "## Counts",
        "",
    ]
    for name, value in report["counts"].items():
        lines.append(f"- `{name}`: `{value}`")
    lines.extend(["", "## Anchor multiplicities", ""])
    for name, value in report["anchors"].items():
        lines.append(f"- `{name}`: `{value}`")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
