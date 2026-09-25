#!/usr/bin/env python3
"""Independent torus-quadrature cross-check of the exact G1 scalar census.

``g1_exact_declared_symmetry_character_census_v20`` counts the SO(10)
invariants of every charge-neutral scalar multidegree of total degree <= 4
from explicit weight multisets and a Racah-Speiser (Weyl alternating-sum)
singlet extractor.  This module recomputes every one of its numbers by a
different route: numerical Weyl integration over the maximal torus of SO(10).

Characters
    On the maximal torus the vector 10 has eigenvalues x_i and 1/x_i, with
    x_i = exp(i theta_i), i = 1..5.  Characters come from generating functions
    of these eigenvalues, never from weight lists:

        10      sum_i (x_i + 1/x_i)
        210     e_4 of the ten eigenvalues (Lambda^4 10)
        126     (e_5 + prod_i (x_i - 1/x_i)) / 2     contains the weight (1,1,1,1,1)
        126bar  (e_5 - prod_i (x_i - 1/x_i)) / 2
        16      (prod_i (y_i + 1/y_i) + prod_i (y_i - 1/y_i)) / 2,   y_i = x_i^(1/2)

    The e_k are the coefficients of prod_i (1 + x_i t)(1 + t/x_i).  The 16
    (weights (+-1/2)^5 with an even number of minus signs) enters only the
    sanity checks, where Sym^2 16 = 10 + 126 ties it to the 126 convention.
    Symmetric powers use the cycle-index (plethysm) formula
    h_n = sum_{lambda |- n} p_lambda / z_lambda with p_k(theta) = chi(k theta).

Invariants
    dim Inv = (1/|W|) int_T chi |Delta|^2 dtheta/(2 pi)^5 with |W(D5)| = 1920
    and |Delta|^2 = prod_{alpha>0} |e^{i alpha.theta/2} - e^{-i alpha.theta/2}|^2
    over the 20 positive roots e_i +- e_j; this equals
    prod_{i<j} (2 cos theta_i - 2 cos theta_j)^2.

Exact quadrature
    The integrand is a trigonometric polynomial.  Its mean over the uniform
    grid theta_i = 2 pi k_i / M collects every Fourier coefficient whose
    frequency vector lies in (M Z)^5.  It therefore equals the integral as soon
    as M exceeds the largest frequency per angle, K.  Every weight of 10, 210,
    126 and 126bar has components in {-1, 0, 1}, so a character of total field
    degree d <= 4 has per-angle frequency <= 4 (singlets add nothing).  Each
    angle lies in 2(5 - 1) = 8 positive roots, and each root contributes a
    factor 2 - 2 cos(alpha.theta) of frequency one, so |Delta|^2 adds 8.  Hence
    K = 12, and M = 13 is exact (13^5 = 371293 nodes).  The module asserts the
    bound, measures it with 1-D FFTs, recomputes every integral on M + 2 = 15,
    and shows the bound is sharp: on M = 12 the grid aliases and Sym^4 210
    comes out as the wrong integer 7 instead of 4.  Integrality alone is
    therefore no certificate; the frequency bound is.  Every value must also
    lie within 1e-6 of a nonnegative integer, otherwise the report fails.

Independence
    Only the standard library and numpy are imported.  No weight multiset,
    dominant-weight bookkeeping, Racah-Speiser reflection or census code is
    used.  The only shared input is the declared model contract (fields,
    charges, conjugation and SO(10) content), which is restated below; the test
    compares it against the census.  This is a cross-check only and closes no
    gate.
"""
from __future__ import annotations

import argparse
import functools
import itertools
import json
import math
import operator
from collections import Counter
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G1_INDEPENDENT_TORUS_QUADRATURE_CENSUS_V20.json"
OUT_MD = ROOT / "G1_INDEPENDENT_TORUS_QUADRATURE_CENSUS_V20.md"

MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
STATUS_REPRODUCED = "G1_INDEPENDENT_TORUS_QUADRATURE_CENSUS_REPRODUCED__CROSS_CHECK_ONLY"
STATUS_FAILED = "G1_INDEPENDENT_TORUS_QUADRATURE_CENSUS_FAILED"

# Maximal torus of SO(10) = D5, and the aliasing bound derived in the docstring.
RANK = 5
WEYL_GROUP_ORDER = 2 ** (RANK - 1) * math.factorial(RANK)  # |W(D5)| = 1920
POSITIVE_ROOTS = tuple(
    (i, j, sign) for i, j in itertools.combinations(range(RANK), 2) for sign in (1, -1)
)  # alpha = e_i + sign * e_j
MAX_DEGREE = 4
FIELD_FREQUENCY = 1  # weights of 10, 210, 126, 126bar have components in {-1, 0, 1}
WEYL_DENSITY_FREQUENCY = 2 * (RANK - 1)  # each angle lies in 8 positive roots
MAX_FREQUENCY = MAX_DEGREE * FIELD_FREQUENCY + WEYL_DENSITY_FREQUENCY  # K = 12
GRID_SIZE = MAX_FREQUENCY + 1  # M = 13, the smallest exact uniform grid
REFINED_GRID_SIZE = GRID_SIZE + 2  # 15
UNDER_RESOLVED_GRID_SIZE = MAX_FREQUENCY  # M = K violates M > K: negative control
INTEGER_TOLERANCE = 1e-6
FFT_LENGTH = 64  # resolves per-angle frequencies up to 31 without wrap-around
FFT_BASE_POINT = (0.37, 1.21, 2.03, 2.89, 4.11)  # generic torus point for FFT slices

# Declared model contract, restated from the census (not imported):
# (PQ, X, Z17) charges, Hermitian conjugation and SO(10) content.
FIELDS = ("P", "H", "Hb", "D", "Db", "S", "Sb", "X", "Xb")
LABEL = {
    "P": "210_H", "H": "10_H", "Hb": "10_H^dag", "D": "126bar_H", "Db": "126bar_H^dag",
    "S": "S", "Sb": "S^dag", "X": "Phi17", "Xb": "Phi17^dag",
}
CHARGE = {
    "P": (0, 0, 0), "H": (-2, -2, 15), "Hb": (2, 2, 2), "D": (-2, -2, 15), "Db": (2, 2, 2),
    "S": (4, 4, 4), "Sb": (-4, -4, 13), "X": (0, 17, 0), "Xb": (0, -17, 0),
}
Z17_ORDER = 17
CONJUGATE = {
    "P": "P", "H": "Hb", "Hb": "H", "D": "Db", "Db": "D",
    "S": "Sb", "Sb": "S", "X": "Xb", "Xb": "X",
}
# Census convention: D = 126bar_H, and Db = 126bar_H^dag transforms as a 126.
SO10_REP = {
    "P": "210", "H": "10", "Hb": "10", "D": "126bar", "Db": "126",
    "S": "1", "Sb": "1", "X": "1", "Xb": "1",
}
# The outer automorphism of D5 swaps 126 <-> 126bar and fixes 10 and 210.
SO10_REP_OUTER = {**SO10_REP, "D": "126", "Db": "126bar"}

TUPLE_KEYS = (
    "multidegrees",
    "conjugacy_orbits",
    "complex_invariant_multiplicity",
    "potential_orbit_multiplicity",
    "real_parameters",
)
EXPECTED_GAUGED = (34, 28, 51, 44, 51)
EXPECTED_GAUGED_COMPLEX_BY_DEGREE = {1: 0, 2: 5, 3: 6, 4: 40}
EXPECTED_GAUGED_ORBIT_BY_DEGREE = {1: 0, 2: 5, 3: 4, 4: 35}
EXPECTED_OPTION_C = (74, 48, 91, 64, 91)
# name -> (multidegree, expected multiplicity, also read from the gauged rows as in the census)
ANCHORS: dict[str, tuple[dict[str, int], int, bool]] = {
    "Sym2_10": ({"H": 2}, 1, False),
    "Sym4_10": ({"H": 4}, 1, False),
    "Sym2_210": ({"P": 2}, 1, False),
    "Sym3_210": ({"P": 3}, 1, False),
    "Sym4_210": ({"P": 4}, 4, False),
    "Sym2_126_pair": ({"D": 2, "Db": 2}, 4, True),
    "P2_H_126dag": ({"P": 2, "H": 1, "Db": 1}, 2, True),
    "P2_126bar_126": ({"P": 2, "D": 1, "Db": 1}, 6, True),
    "P2_H_Hdag": ({"P": 2, "H": 1, "Hb": 1}, 3, True),
    "H_Hdag_126bar_126": ({"H": 1, "Hb": 1, "D": 1, "Db": 1}, 2, True),
    "H2_Hdag2": ({"H": 2, "Hb": 2}, 2, True),
}
# name -> (forbidden fields, expected tuple in TUPLE_KEYS order)
SECTORS: dict[str, tuple[tuple[str, ...], tuple[int, ...]]] = {
    "singlet_only": (("P", "H", "Hb", "D", "Db"), (5, 5, 5, 5, 5)),
    "H10_S_Phi17": (("P", "D", "Db"), (11, 10, 12, 11, 12)),
}
EXPECTED_DIMENSIONS = {"10": 10, "16": 16, "126": 126, "126bar": 126, "210": 210}
EXPECTED_TEXTBOOK = {
    "inv_10_10": 1,
    "inv_10_10_10_10": 3,  # the three Brauer pairings
    "inv_210_210": 1,
    "inv_126_126bar": 1,
    "inv_126_126": 0,
    "inv_16_16bar": 1,
    "inv_16_16": 0,
    "inv_16_16_10": 1,  # the 16 16 10 Yukawa
    "inv_16_16_126bar": 1,  # the 16 16 126bar Yukawa
    "inv_16_16_126": 0,
}


# --------------------------------------------------------------------------- characters


def torus_characters(theta: np.ndarray) -> dict[str, np.ndarray]:
    """Characters of 10, 210, 126 and 126bar at torus angles ``theta[..., 5]``."""
    x = np.exp(1j * theta)
    shape = theta.shape[:-1]
    # prod_i (1 + x_i t)(1 + t/x_i) = prod_i (1 + (x_i + 1/x_i) t + t^2) = sum_k e_k t^k
    pair_trace = (x + 1 / x).real
    e = [np.ones(shape)] + [np.zeros(shape) for _ in range(5)]
    for i in range(RANK):
        for k in range(5, 0, -1):
            e[k] = e[k] + pair_trace[..., i] * e[k - 1] + (e[k - 2] if k >= 2 else 0.0)
    chirality = np.prod(x - 1 / x, axis=-1)  # splits Lambda^5 10 = 126 + 126bar
    return {
        "10": np.sum(x + 1 / x, axis=-1).real,
        "210": e[4],
        "126": (e[5] + chirality) / 2,
        "126bar": (e[5] - chirality) / 2,
    }


def spinor16_character(theta: np.ndarray) -> np.ndarray:
    """Chiral spinor 16, weights (+-1/2)^5 with an even number of minus signs (Spin(10))."""
    y = np.exp(0.5j * theta)
    return (np.prod(y + 1 / y, axis=-1) + np.prod(y - 1 / y, axis=-1)) / 2


def weyl_density(theta: np.ndarray) -> np.ndarray:
    """|Delta|^2 = prod_{alpha>0} |e^{i alpha.theta/2} - e^{-i alpha.theta/2}|^2."""
    density = np.ones(theta.shape[:-1])
    for i, j, sign in POSITIVE_ROOTS:
        density = density * 4.0 * np.sin(0.5 * (theta[..., i] + sign * theta[..., j])) ** 2
    return density


def weyl_density_cosine_form(theta: np.ndarray) -> np.ndarray:
    """The equivalent form prod_{i<j} (2 cos theta_i - 2 cos theta_j)^2."""
    trace = 2.0 * np.cos(theta)
    density = np.ones(theta.shape[:-1])
    for i, j in itertools.combinations(range(RANK), 2):
        density = density * (trace[..., i] - trace[..., j]) ** 2
    return density


def partitions(n: int, largest: int | None = None) -> Iterator[tuple[int, ...]]:
    """Partitions of n with parts <= largest, parts in decreasing order."""
    largest = n if largest is None else largest
    if n == 0:
        yield ()
        return
    for first in range(min(n, largest), 0, -1):
        for rest in partitions(n - first, first):
            yield (first, *rest)


def centralizer_order(partition: tuple[int, ...]) -> int:
    """z_lambda = prod_k k^{m_k} m_k!, the centralizer order of cycle type lambda."""
    return math.prod(k**m * math.factorial(m) for k, m in Counter(partition).items())


def symmetric_power(power_sum: Callable[[int], np.ndarray], n: int) -> np.ndarray:
    """Sym^n character h_n = sum_{lambda |- n} p_lambda / z_lambda (n >= 1)."""
    terms = (
        functools.reduce(operator.mul, (power_sum(k) for k in lam)) / centralizer_order(lam)
        for lam in partitions(n)
    )
    return functools.reduce(operator.add, terms)


# --------------------------------------------------------------------------- quadrature


class TorusGrid:
    """Uniform ``size**5`` grid on the torus; exact for per-angle frequency < size."""

    def __init__(self, size: int, enforce_bound: bool = True) -> None:
        self.size = size
        self.enforce_bound = enforce_bound
        axis = 2.0 * np.pi * np.arange(size) / size
        grid = np.meshgrid(*[axis] * RANK, indexing="ij")
        self.theta = np.stack(grid, axis=-1).reshape(-1, RANK)
        self.measure = weyl_density(self.theta) / WEYL_GROUP_ORDER
        self._power_sums: dict[int, dict[str, np.ndarray]] = {}
        self._sym: dict[tuple[str, int], np.ndarray] = {}
        self.values: dict[tuple[tuple[str, int], ...], complex] = {}

    def require_resolved(self, character_frequency: int) -> None:
        """Fail closed unless size > character frequency + Weyl-density frequency."""
        needed = character_frequency + WEYL_DENSITY_FREQUENCY
        if self.enforce_bound and self.size <= needed:
            raise ValueError(
                f"grid M={self.size} aliases an integrand of per-angle frequency {needed};"
                f" exactness needs M > {needed}"
            )

    def power_sum(self, rep: str, k: int) -> np.ndarray:
        """p_k = chi_rep(k theta), cached per k for all representations."""
        if k not in self._power_sums:
            self._power_sums[k] = torus_characters(k * self.theta)
        return self._power_sums[k][rep]

    def sym(self, rep: str, n: int) -> np.ndarray:
        """Sym^n character of ``rep`` on the grid, cached per (rep, n)."""
        if (rep, n) not in self._sym:
            self._sym[rep, n] = symmetric_power(lambda k: self.power_sum(rep, k), n)
        return self._sym[rep, n]

    def weyl_average(self, values: np.ndarray, character_frequency: int) -> complex:
        """(1/|W|) int_T chi |Delta|^2 dtheta/(2 pi)^5, evaluated as the grid mean."""
        self.require_resolved(character_frequency)
        return complex(np.mean(values * self.measure))

    def invariant_value(self, factors: tuple[tuple[str, int], ...]) -> complex:
        """Quadrature value of dim Inv(tensor over (rep, n) of Sym^n rep)."""
        if factors not in self.values:
            frequency = FIELD_FREQUENCY * sum(n for _, n in factors)
            self.require_resolved(frequency)
            chi = functools.reduce(
                operator.mul,
                (self.sym(rep, n) for rep, n in factors),
                np.ones(len(self.theta)),
            )
            self.values[factors] = self.weyl_average(chi, frequency)
        return self.values[factors]


def nearest_count(value: complex) -> tuple[int, float, bool]:
    """Nearest integer, its distance, and whether ``value`` certifies a count >= 0."""
    count = round(value.real)
    distance = abs(value.real - count)
    certified = (
        count >= 0 and distance <= INTEGER_TOLERANCE and abs(value.imag) <= INTEGER_TOLERANCE
    )
    return count, distance, certified


def stable(x: float) -> float:
    """Round for byte-stable JSON across BLAS builds (and map -0.0 to 0.0)."""
    return round(float(x), 9) + 0.0


# --------------------------------------------------------------------------- census


def multidegrees(max_degree: int = MAX_DEGREE) -> Iterator[tuple[int, ...]]:
    """Every count vector over FIELDS with total degree 1..max_degree."""
    for degree in range(1, max_degree + 1):
        for chosen in itertools.combinations_with_replacement(range(len(FIELDS)), degree):
            yield tuple(chosen.count(i) for i in range(len(FIELDS)))


def as_counts(fields: dict[str, int]) -> tuple[int, ...]:
    return tuple(fields.get(field, 0) for field in FIELDS)


def charge(counts: tuple[int, ...]) -> dict[str, int]:
    pq, x, z = (
        sum(n * CHARGE[field][slot] for field, n in zip(FIELDS, counts)) for slot in range(3)
    )
    return {"PQ": pq, "X": x, "Z17": z % Z17_ORDER}


def is_neutral(counts: tuple[int, ...], require_x: bool) -> bool:
    q = charge(counts)
    return q["PQ"] == 0 and q["Z17"] == 0 and (q["X"] == 0 or not require_x)


def conjugate(counts: tuple[int, ...]) -> tuple[int, ...]:
    by_field = dict(zip(FIELDS, counts))
    return tuple(by_field[CONJUGATE[field]] for field in FIELDS)


def monomial(counts: tuple[int, ...]) -> str:
    parts = (
        LABEL[field] if n == 1 else f"{LABEL[field]}^{n}" for field, n in zip(FIELDS, counts) if n
    )
    return " ".join(parts) or "1"


def character_factors(
    counts: tuple[int, ...], rep_map: dict[str, str] = SO10_REP
) -> tuple[tuple[str, int], ...]:
    """(representation, power) per non-singlet field; singlets have character 1."""
    return tuple(
        (rep_map[field], n) for field, n in zip(FIELDS, counts) if n and rep_map[field] != "1"
    )


def quadrature_census(
    grid: TorusGrid, require_x: bool, rep_map: dict[str, str] = SO10_REP
) -> list[dict[str, Any]]:
    """Rows with nonzero multiplicity among all charge-neutral multidegrees of degree <= 4."""
    rows = []
    for counts in multidegrees():
        if not is_neutral(counts, require_x):
            continue
        value = grid.invariant_value(character_factors(counts, rep_map))
        multiplicity, distance, _ = nearest_count(value)
        if multiplicity == 0:
            continue
        conj = conjugate(counts)
        rows.append(
            {
                "count_tuple": list(counts),
                "counts": dict(zip(FIELDS, counts)),
                "degree": sum(counts),
                "monomial": monomial(counts),
                "charge": charge(counts),
                "so10_singlet_multiplicity": multiplicity,
                "quadrature_value": stable(value.real),
                "quadrature_imaginary_part": stable(value.imag),
                "distance_to_nearest_integer": stable(distance),
                "conjugate_count_tuple": list(conj),
                "conjugate_monomial": monomial(conj),
                "self_conjugate": counts == conj,
                "conjugacy_orbit_key": list(min(counts, conj)),
            }
        )
    return sorted(rows, key=lambda row: (row["degree"], row["count_tuple"]))


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "count_tuple",
        "monomial",
        "so10_singlet_multiplicity",
        "quadrature_value",
        "quadrature_imaginary_part",
        "distance_to_nearest_integer",
    )
    return {key: row[key] for key in keys} | {"x_charge": row["charge"]["X"]}


def conjugacy_orbits(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Hermitian-conjugacy orbits {c, c^dag}; m real parameters if self-conjugate, else 2m."""
    groups: dict[tuple[int, ...], list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(tuple(row["conjugacy_orbit_key"]), []).append(row)
    orbits = []
    for key, group in sorted(groups.items(), key=lambda item: (sum(item[0]), item[0])):
        self_conjugate = key == conjugate(key)
        multiplicities = {row["so10_singlet_multiplicity"] for row in group}
        m = max(multiplicities)
        orbits.append(
            {
                "orbit_key": list(key),
                "representative": monomial(key),
                "degree": sum(key),
                "self_conjugate": self_conjugate,
                "so10_singlet_multiplicity": m,
                "real_parameter_count": m if self_conjugate else 2 * m,
                "members": [row["monomial"] for row in group],
                "conjugates_present_with_equal_multiplicity": (
                    len(group) == (1 if self_conjugate else 2) and len(multiplicities) == 1
                ),
            }
        )
    return orbits


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Count block with the same keys as the exact census."""
    orbits = conjugacy_orbits(rows)
    degrees = range(1, MAX_DEGREE + 1)
    complex_by_degree = {
        d: sum(r["so10_singlet_multiplicity"] for r in rows if r["degree"] == d) for d in degrees
    }
    orbit_by_degree = {
        d: sum(o["so10_singlet_multiplicity"] for o in orbits if o["degree"] == d) for d in degrees
    }
    return {
        "charge_and_so10_allowed_multidegrees": len(rows),
        "hermitian_conjugacy_orbits": len(orbits),
        "complex_invariant_multiplicity_by_degree": complex_by_degree,
        "potential_orbit_multiplicity_by_degree": orbit_by_degree,
        "total_complex_invariant_multiplicity": sum(complex_by_degree.values()),
        "total_potential_orbit_multiplicity": sum(orbit_by_degree.values()),
        "total_real_potential_parameters": sum(o["real_parameter_count"] for o in orbits),
    }


def five_numbers(summary: dict[str, Any]) -> tuple[int, ...]:
    """(multidegrees, orbits, complex multiplicity, orbit multiplicity, real parameters)."""
    return (
        summary["charge_and_so10_allowed_multidegrees"],
        summary["hermitian_conjugacy_orbits"],
        summary["total_complex_invariant_multiplicity"],
        summary["total_potential_orbit_multiplicity"],
        summary["total_real_potential_parameters"],
    )


def sector(rows: list[dict[str, Any]], forbidden: tuple[str, ...]) -> dict[str, int]:
    kept = [r for r in rows if all(r["counts"][field] == 0 for field in forbidden)]
    return dict(zip(TUPLE_KEYS, five_numbers(summarize(kept))))


# --------------------------------------------------------------------------- sanity checks


def character_dimensions() -> dict[str, complex]:
    origin = np.zeros((1, RANK))
    dims = {rep: complex(chi[0]) for rep, chi in torus_characters(origin).items()}
    dims["16"] = complex(spinor16_character(origin)[0])
    return dims


def textbook_values(grid: TorusGrid) -> dict[str, complex]:
    """Invariant counts with textbook answers (EXPECTED_TEXTBOOK)."""
    chi = {rep: grid.power_sum(rep, 1) for rep in ("10", "210", "126", "126bar")}
    s16 = spinor16_character(grid.theta)
    s16_squared = s16 * s16  # integer weights, so periodic on the SO(10) torus
    integrands = {  # name -> (character, per-angle character frequency)
        "inv_10_10": (chi["10"] ** 2, 2),
        "inv_10_10_10_10": (chi["10"] ** 4, 4),
        "inv_210_210": (chi["210"] ** 2, 2),
        "inv_126_126bar": (chi["126"] * chi["126bar"], 2),
        "inv_126_126": (chi["126"] ** 2, 2),
        "inv_16_16bar": (s16 * s16.conj(), 1),
        "inv_16_16": (s16_squared, 1),
        "inv_16_16_10": (s16_squared * chi["10"], 2),
        "inv_16_16_126bar": (s16_squared * chi["126bar"], 2),
        "inv_16_16_126": (s16_squared * chi["126"], 2),
    }
    return {name: grid.weyl_average(v, freq) for name, (v, freq) in integrands.items()}


def weight_multiplicity(grid: TorusGrid, chi: np.ndarray, weight: tuple[int, ...]) -> complex:
    """Fourier coefficient of exp(i weight.theta) in chi (exact: frequency 2 < M)."""
    phase = np.exp(-1j * (grid.theta @ np.asarray(weight, dtype=float)))
    return complex(np.mean(chi * phase))


def convention_checks(grid: TorusGrid) -> dict[str, bool]:
    chi = {rep: grid.power_sum(rep, 1) for rep in ("10", "210", "126", "126bar")}
    s16 = spinor16_character(grid.theta)
    sym2_16 = (s16 * s16 + spinor16_character(2.0 * grid.theta)) / 2
    top, bottom = (1,) * RANK, (-1,) * RANK
    reflected = torus_characters(grid.theta * np.array([1.0, 1.0, 1.0, 1.0, -1.0]))
    outer_image = {"10": "10", "210": "210", "126": "126bar", "126bar": "126"}
    density_gap = np.max(np.abs(weyl_density(grid.theta) - weyl_density_cosine_form(grid.theta)))
    return {
        "sym2_16_equals_10_plus_126": bool(
            np.max(np.abs(sym2_16 - chi["10"] - chi["126"])) < 1e-9
        ),
        "convention_126_contains_weight_plus_11111": bool(
            abs(weight_multiplicity(grid, chi["126"], top) - 1) < 1e-9
            and abs(weight_multiplicity(grid, chi["126"], bottom)) < 1e-9
        ),
        "convention_126bar_contains_weight_minus_11111": bool(
            abs(weight_multiplicity(grid, chi["126bar"], bottom) - 1) < 1e-9
            and abs(weight_multiplicity(grid, chi["126bar"], top)) < 1e-9
        ),
        "outer_automorphism_character_identity": all(
            bool(np.max(np.abs(reflected[rep] - chi[image])) < 1e-9)
            for rep, image in outer_image.items()
        ),
        "weyl_density_root_and_cosine_forms_agree": bool(
            density_gap < 1e-9 * max(1.0, float(np.max(grid.measure)) * WEYL_GROUP_ORDER)
        ),
    }


def measured_frequency(function: Callable[[np.ndarray], np.ndarray]) -> int:
    """Largest per-angle frequency of a trigonometric polynomial, from 1-D FFT slices."""
    steps = 2.0 * np.pi * np.arange(FFT_LENGTH) / FFT_LENGTH
    frequencies = np.abs(np.fft.fftfreq(FFT_LENGTH, d=1.0 / FFT_LENGTH)).round().astype(int)
    largest = 0
    for axis in range(RANK):
        theta = np.tile(np.array(FFT_BASE_POINT), (FFT_LENGTH, 1))
        theta[:, axis] = steps
        magnitude = np.abs(np.fft.fft(function(theta)))
        largest = max(largest, int(frequencies[magnitude > 1e-9 * magnitude.max()].max()))
    return largest


def frequency_support() -> dict[str, int]:
    """Measured per-angle frequencies of the density, the characters and worst integrands."""

    def sym(rep: str, n: int, theta: np.ndarray) -> np.ndarray:
        return symmetric_power(lambda k: torus_characters(k * theta)[rep], n)

    support = {"weyl_density": measured_frequency(weyl_density)}
    for rep in ("10", "210", "126", "126bar"):
        support[f"chi_{rep}"] = measured_frequency(lambda t, rep=rep: torus_characters(t)[rep])
    worst = {
        "sym4_10_times_density": lambda t: sym("10", 4, t) * weyl_density(t),
        "sym4_210_times_density": lambda t: sym("210", 4, t) * weyl_density(t),
        "sym2_126bar_sym2_126_times_density": (
            lambda t: sym("126bar", 2, t) * sym("126", 2, t) * weyl_density(t)
        ),
    }
    for name, function in worst.items():
        support[name] = measured_frequency(function)
    return support


# --------------------------------------------------------------------------- report


def refined_grid_check(grid: TorusGrid) -> dict[str, Any]:
    """Recompute every integral of ``grid`` on the larger exact grid M + 2."""
    refined = TorusGrid(REFINED_GRID_SIZE)
    identical = True
    largest_difference = 0.0
    for factors, value in grid.values.items():
        other = refined.invariant_value(factors)
        count, _, certified = nearest_count(value)
        other_count, _, other_certified = nearest_count(other)
        identical = identical and certified and other_certified and count == other_count
        largest_difference = max(largest_difference, abs(value - other))
    return {
        "grid_size": REFINED_GRID_SIZE,
        "grid_points": REFINED_GRID_SIZE**RANK,
        "integrals_recomputed": len(grid.values),
        "identical_certified_integers": identical,
        "max_abs_value_difference": stable(largest_difference),
    }


def negative_control(resolved_value: complex) -> dict[str, Any]:
    """Sym^4 210 on the under-resolved grid M = K = 12."""
    factors = (("210", 4),)
    try:
        TorusGrid(UNDER_RESOLVED_GRID_SIZE).invariant_value(factors)
        refused = False
    except ValueError:
        refused = True
    aliased = TorusGrid(UNDER_RESOLVED_GRID_SIZE, enforce_bound=False).invariant_value(factors)
    count, _, certified = nearest_count(aliased)
    resolved_count = nearest_count(resolved_value)[0]
    return {
        "grid_size": UNDER_RESOLVED_GRID_SIZE,
        "integrand": "Sym^4 210 (210_H^4)",
        "resolved_count": resolved_count,
        "aliased_quadrature_value": stable(aliased.real),
        "aliased_nearest_integer": count,
        "aliased_value_is_certified_integer": certified,
        "aliasing_detected": (not certified) or count != resolved_count,
        "guard_refuses_under_resolved_grid": refused,
        "lesson": "M = K aliases into a wrong integer; integrality alone is no certificate,"
        " the frequency bound M > K is.",
    }


METHOD = {
    "summary": "Numerical Weyl integration over the maximal torus of SO(10) on a uniform"
    " grid that is exact for the trigonometric-polynomial integrand.",
    "characters": "Generating functions of the vector eigenvalues x_i^(+-1):"
    " 10 = sum(x_i + 1/x_i), 210 = e_4, 126/126bar = (e_5 +- prod(x_i - 1/x_i))/2;"
    " 16 only in sanity checks.",
    "symmetric_powers": "Cycle-index (plethysm) formula"
    " h_n = sum_{lambda |- n} p_lambda/z_lambda with p_k(theta) = chi(k theta).",
    "invariant_count": "dim Inv = (1/1920) x grid mean of chi |Delta|^2, with |Delta|^2 the"
    " product over the 20 positive roots e_i +- e_j of"
    " |e^{i alpha.theta/2} - e^{-i alpha.theta/2}|^2.",
    "exactness": "Per-angle frequency <= 4 (characters, degree <= 4) + 8 (Weyl density) = 12"
    " < M = 13; every value must lie within 1e-6 of a nonnegative integer.",
    "independence": "Imports only the standard library and numpy; no weight multisets,"
    " Racah-Speiser reflections or census code. Shared input: the declared field, charge,"
    " conjugation and SO(10) contract.",
}


def build_report() -> dict[str, Any]:
    grid = TorusGrid(GRID_SIZE)
    normalization = grid.invariant_value(())
    gauged_rows = quadrature_census(grid, require_x=True)
    option_c_rows = quadrature_census(grid, require_x=False)
    swapped_rows = quadrature_census(grid, require_x=False, rep_map=SO10_REP_OUTER)
    gauged = summarize(gauged_rows)
    option_c = summarize(option_c_rows)
    gauged_orbits = conjugacy_orbits(gauged_rows)
    option_c_orbits = conjugacy_orbits(option_c_rows)
    gauged_lookup = {tuple(r["count_tuple"]): r["so10_singlet_multiplicity"] for r in gauged_rows}
    option_c_lookup = {
        tuple(r["count_tuple"]): r["so10_singlet_multiplicity"] for r in option_c_rows
    }

    anchors = {
        name: nearest_count(grid.invariant_value(character_factors(as_counts(fields))))[0]
        for name, (fields, _, _) in ANCHORS.items()
    }
    sectors = {name: sector(gauged_rows, forbidden) for name, (forbidden, _) in SECTORS.items()}
    dimensions = character_dimensions()
    textbook = textbook_values(grid)
    conventions = convention_checks(grid)
    support = frequency_support()
    refined = refined_grid_check(grid)
    control = negative_control(grid.invariant_value((("210", 4),)))

    certified_values = list(grid.values.values()) + list(textbook.values())
    distances = [nearest_count(v)[1] for v in certified_values]
    imaginary = [abs(v.imag) for v in certified_values]

    checks: dict[str, bool] = {}
    for rep, expected in EXPECTED_DIMENSIONS.items():
        checks[f"character_dimension_{rep}"] = abs(dimensions[rep] - expected) < 1e-9
    checks["weyl_normalization_trivial_rep_is_1"] = abs(normalization - 1) < INTEGER_TOLERANCE
    for name, expected in EXPECTED_TEXTBOOK.items():
        count, _, certified = nearest_count(textbook[name])
        checks[f"textbook_{name}"] = certified and count == expected
    checks.update(conventions)
    checks["aliasing_bound_grid_exceeds_max_frequency"] = GRID_SIZE > MAX_FREQUENCY
    checks["measured_weyl_density_frequency_equals_derived"] = (
        support["weyl_density"] == WEYL_DENSITY_FREQUENCY
    )
    checks["measured_character_frequencies_equal_derived"] = all(
        support[f"chi_{rep}"] == FIELD_FREQUENCY for rep in ("10", "210", "126", "126bar")
    )
    checks["measured_integrand_frequencies_within_bound"] = all(
        value <= MAX_FREQUENCY for name, value in support.items() if name.endswith("density")
    )
    checks["all_quadrature_values_certified_nonnegative_integers"] = all(
        nearest_count(v)[2] for v in certified_values
    )
    checks["refined_grid_reproduces_identical_integers"] = refined["identical_certified_integers"]
    checks["negative_control_under_resolved_grid_detected"] = control["aliasing_detected"]
    checks["negative_control_guard_refuses_under_resolved_grid"] = control[
        "guard_refuses_under_resolved_grid"
    ]
    checks["outer_automorphism_census_invariant"] = [
        (r["count_tuple"], r["so10_singlet_multiplicity"]) for r in swapped_rows
    ] == [(r["count_tuple"], r["so10_singlet_multiplicity"]) for r in option_c_rows]
    checks["conjugate_pairs_present_with_equal_multiplicity"] = all(
        o["conjugates_present_with_equal_multiplicity"] for o in gauged_orbits + option_c_orbits
    )
    checks["gauged_rows_pq_x_z17_neutral"] = all(
        r["charge"] == {"PQ": 0, "X": 0, "Z17": 0} for r in gauged_rows
    )
    for label, observed, expected in (
        ("gauged", five_numbers(gauged), EXPECTED_GAUGED),
        ("option_c", five_numbers(option_c), EXPECTED_OPTION_C),
    ):
        for key, got, want in zip(TUPLE_KEYS, observed, expected):
            checks[f"{label}_{key}"] = got == want
    checks["gauged_complex_multiplicity_by_degree"] = (
        gauged["complex_invariant_multiplicity_by_degree"] == EXPECTED_GAUGED_COMPLEX_BY_DEGREE
    )
    checks["gauged_orbit_multiplicity_by_degree"] = (
        gauged["potential_orbit_multiplicity_by_degree"] == EXPECTED_GAUGED_ORBIT_BY_DEGREE
    )
    checks["gauged_rows_in_option_c_with_same_multiplicity"] = all(
        option_c_lookup.get(key) == m for key, m in gauged_lookup.items()
    )
    for name, (fields, expected, from_rows) in ANCHORS.items():
        in_rows = gauged_lookup.get(as_counts(fields), 0) == anchors[name]
        checks[f"anchor_{name}"] = anchors[name] == expected and (in_rows or not from_rows)
    for name, (_, expected) in SECTORS.items():
        for key, want in zip(TUPLE_KEYS, expected):
            checks[f"sector_{name}_{key}"] = sectors[name][key] == want
    checks["no_gate_closure_claim"] = True
    checks = {name: bool(ok) for name, ok in checks.items()}

    failures = [name for name, ok in checks.items() if not ok]
    passed = not failures
    return {
        "model_contract_id": MODEL_CONTRACT_ID,
        "status": STATUS_REPRODUCED if passed else STATUS_FAILED,
        "overall_state": "PARTIAL" if passed else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "method": METHOD,
        "quadrature": {
            "grid_size": GRID_SIZE,
            "grid_points": GRID_SIZE**RANK,
            "weyl_group_order": WEYL_GROUP_ORDER,
            "positive_roots": len(POSITIVE_ROOTS),
            "character_max_frequency_per_angle": MAX_DEGREE * FIELD_FREQUENCY,
            "weyl_density_max_frequency_per_angle": WEYL_DENSITY_FREQUENCY,
            "integrand_max_frequency_per_angle": MAX_FREQUENCY,
            "aliasing_condition": f"M > {MAX_FREQUENCY}",
            "aliasing_bound_satisfied": GRID_SIZE > MAX_FREQUENCY,
            "measured_frequency_support": support,
            "fft_slice_length": FFT_LENGTH,
            "integer_tolerance": INTEGER_TOLERANCE,
            "integrals_evaluated": len(certified_values),
            "max_distance_to_nearest_integer": stable(max(distances)),
            "max_abs_imaginary_part": stable(max(imaginary)),
        },
        "character_dimensions": {
            rep: round(value.real) for rep, value in sorted(dimensions.items())
        },
        "textbook_invariants": {name: nearest_count(v)[0] for name, v in textbook.items()},
        "counts": gauged,
        "historical_option_c_no_x_comparison": {
            "counts": option_c,
            "multidegrees": [compact_row(row) for row in option_c_rows],
            "interpretation": "Counterfactual without the U(1)_X selection rule, reproduced"
            " only to match the census comparison; not authoritative.",
        },
        "anchors": anchors,
        "sectors": sectors,
        "multidegrees": gauged_rows,
        "potential_orbits": gauged_orbits,
        "outer_automorphism": {
            "swap": "D -> 126, Db -> 126bar (theta_5 -> -theta_5)",
            "multidegrees_compared": len(option_c_rows),
            "invariant": checks["outer_automorphism_census_invariant"],
        },
        "refined_grid": refined,
        "negative_control": control,
        "expected": {
            "tuple_order": list(TUPLE_KEYS),
            "gauged": list(EXPECTED_GAUGED),
            "gauged_complex_multiplicity_by_degree": EXPECTED_GAUGED_COMPLEX_BY_DEGREE,
            "gauged_orbit_multiplicity_by_degree": EXPECTED_GAUGED_ORBIT_BY_DEGREE,
            "option_c": list(EXPECTED_OPTION_C),
            "anchors": {name: expected for name, (_, expected, _) in ANCHORS.items()},
            "sectors": {name: list(expected) for name, (_, expected) in SECTORS.items()},
        },
        "flags": {
            "independent_reproduction_of_exact_g1_census": passed,
            "cross_check_only": True,
            "g1_closed_by_this_module": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "scope": "Cross-check of the degree <= 4 multiplicity census only; it closes no gate"
        " and makes no whole-model validation or exclusion claim.",
        "verdict": (
            "Torus quadrature independently reproduces the exact G1 census: gauged"
            f" SO(10) x U(1)_X {five_numbers(gauged)}, historical Option-C"
            f" {five_numbers(option_c)}, all anchors and sectors. Cross-check only; no gate is"
            " closed."
            if passed
            else f"Torus quadrature did not reproduce the exact G1 census; failed: {failures}."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    checks, quad = report["checks"], report["quadrature"]
    control, refined = report["negative_control"], report["refined_grid"]
    gauged = report["counts"]
    option_c = report["historical_option_c_no_x_comparison"]["counts"]
    # (quantity, quadrature value, expected value, checks that must pass)
    table: list[tuple[str, Any, Any, list[str]]] = [
        ("gauged SO(10) x U(1)_X", five_numbers(gauged), EXPECTED_GAUGED,
         [f"gauged_{key}" for key in TUPLE_KEYS]),
        ("gauged complex multiplicity by degree",
         gauged["complex_invariant_multiplicity_by_degree"], EXPECTED_GAUGED_COMPLEX_BY_DEGREE,
         ["gauged_complex_multiplicity_by_degree"]),
        ("gauged orbit multiplicity by degree",
         gauged["potential_orbit_multiplicity_by_degree"], EXPECTED_GAUGED_ORBIT_BY_DEGREE,
         ["gauged_orbit_multiplicity_by_degree"]),
        ("historical Option-C (no X)", five_numbers(option_c), EXPECTED_OPTION_C,
         [f"option_c_{key}" for key in TUPLE_KEYS]),
    ]
    table += [
        (f"anchor {name}", report["anchors"][name], expected, [f"anchor_{name}"])
        for name, (_, expected, _) in ANCHORS.items()
    ]
    table += [
        (f"sector {name}", tuple(report["sectors"][name][key] for key in TUPLE_KEYS), expected,
         [f"sector_{name}_{key}" for key in TUPLE_KEYS])
        for name, (_, expected) in SECTORS.items()
    ]
    return "\n".join(
        [
            "# G1 independent torus-quadrature census (cross-check)",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "## Method",
            "",
            f"- dim Inv = (1/{quad['weyl_group_order']}) x mean of chi |Delta|^2 over a uniform"
            f" `{quad['grid_size']}^5` torus grid ({quad['grid_points']} nodes).",
            "- Aliasing bound: per-angle frequency"
            f" <= {quad['character_max_frequency_per_angle']} (characters, degree <= 4)"
            f" + {quad['weyl_density_max_frequency_per_angle']} (Weyl density)"
            f" = {quad['integrand_max_frequency_per_angle']} < M = {quad['grid_size']};"
            " 1-D FFT slices confirm the frequencies.",
            f"- Refined grid M = {refined['grid_size']}: all"
            f" {refined['integrals_recomputed']} integrals give identical integers.",
            f"- Negative control, M = {control['grid_size']}: Sym^4 210 aliases to"
            f" {control['aliased_nearest_integer']} instead of {control['resolved_count']}, a"
            " wrong integer; the guard refuses this grid.",
            "- Characters come from eigenvalue generating functions and Sym^n from the"
            " cycle-index formula. No weight lists, Racah-Speiser code or census imports are"
            " used.",
            "",
            "## Reproduced numbers",
            "",
            "Tuples: (multidegrees, conjugacy orbits, complex invariant multiplicity,"
            " potential-orbit multiplicity, real parameters).",
            "",
            "| quantity | quadrature | expected | check |",
            "|---|---|---|---|",
            *(
                f"| {quantity} | `{got}` | `{want}` |"
                f" {'PASS' if all(checks[name] for name in names) else 'FAIL'} |"
                for quantity, got, want, names in table
            ),
            "",
            f"All {report['n_checks']} checks: {report['n_checks'] - report['n_failed']} passed,"
            f" {report['n_failed']} failed.",
            "",
            "## Scope",
            "",
            "Cross-check only. It reproduces the multiplicity census; it does not close G1 or"
            " any other gate and makes no whole-model validation or exclusion claim.",
            "",
        ]
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")


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
