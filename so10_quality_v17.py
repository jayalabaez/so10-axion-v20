#!/usr/bin/env python3
"""Axion-quality proof machinery for the Spin(10) x Z17 model (v17).

The catalogue generated here is intentionally an *over-catalogue*.  It
imposes only conditions that every Lorentz/SO(10) invariant must obey:

* an even number of Weyl fields;
* trivial Spin(10)-centre charge;
* Z17 invariance (and, optionally, spectator Z3 triality).

It allows contractions that need not exist.  Consequently, excluding a
low-order vacuum closure in this catalogue excludes it in the physical
operator set as well.  The companion :mod:`spin10_referee_audit` constructs
the explicit first-attainable contraction and verifies its Lorentz and Fermi
statistics.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import heapq
import math
from typing import Dict, Iterable, Iterator, Mapping, Sequence, Tuple


@dataclass(frozen=True)
class Field:
    name: str
    pq: int
    centre: int
    vector: int
    triality: int
    twice_dimension: int
    fermion: bool


# Hm/Hp stand for either charge -2 tensor scalar and its conjugate.
# Keeping only one representative per charge is conservative: 10_H and
# 126bar_H have the same PQ and Spin(10)-centre data.
FIELDS: Tuple[Field, ...] = (
    Field("F", +1, +1, 0, 0, 3, True),
    Field("Fd", -1, -1, 0, 0, 3, True),
    Field("s", +2, +1, +1, +1, 3, True),
    Field("sd", -2, -1, -1, -1, 3, True),
    Field("b", -6, -1, -1, -1, 3, True),
    Field("bd", +6, +1, +1, +1, 3, True),
    Field("S", +4, 0, 0, 0, 2, False),
    Field("Sd", -4, 0, 0, 0, 2, False),
    Field("Hm", -2, 2, 0, 0, 2, False),
    Field("Hp", +2, 2, 0, 0, 2, False),
)
FIELD_BY_NAME = {field.name: field for field in FIELDS}
FERMIONS = FIELDS[:6]
SCALARS = FIELDS[6:]


@dataclass(frozen=True)
class Monomial:
    dimension: int
    pq: int
    vector: int
    centre: int
    triality: int
    n_fermions: int
    counts: Tuple[int, ...]

    @property
    def m17(self) -> int:
        if self.pq % 17:
            raise ValueError("monomial is not Z17 invariant")
        return self.pq // 17

    @property
    def planck_power(self) -> int:
        return self.dimension - 4

    @property
    def label(self) -> str:
        pieces = []
        for field, count in zip(FIELDS, self.counts):
            if count == 1:
                pieces.append(field.name)
            elif count:
                pieces.append(f"{field.name}^{count}")
        return " ".join(pieces) if pieces else "1"

    def as_dict(self) -> dict:
        return {
            "label": self.label,
            "dimension": self.dimension,
            "pq": self.pq,
            "m17": self.m17 if self.pq % 17 == 0 else None,
            "spectator_vector": self.vector,
            "spin10_centre_mod4": self.centre % 4,
            "triality_mod3": self.triality % 3,
            "n_fermions": self.n_fermions,
            "planck_power": self.planck_power,
        }


@dataclass(frozen=True)
class Closure:
    planck_power: int
    m17: int
    vector: int
    operators: Tuple[Monomial, ...]

    @property
    def pq(self) -> int:
        return 17 * self.m17

    def multiplicities(self) -> list[dict]:
        counts = Counter(op.label for op in self.operators)
        by_label = {op.label: op for op in self.operators}
        return [
            {"multiplicity": counts[label], **by_label[label].as_dict()}
            for label in sorted(counts)
        ]


def weak_compositions(total: int, parts: int) -> Iterator[Tuple[int, ...]]:
    """Yield ordered non-negative integer tuples summing to ``total``."""
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in weak_compositions(total - first, parts - 1):
            yield (first,) + rest


def monomial_from_counts(counts: Mapping[str, int]) -> Monomial:
    vector = [int(counts.get(field.name, 0)) for field in FIELDS]
    if any(value < 0 for value in vector):
        raise ValueError("field multiplicities must be non-negative")
    n_fermions = sum(vector[: len(FERMIONS)])
    twice_dimension = sum(
        count * field.twice_dimension for count, field in zip(vector, FIELDS)
    )
    if twice_dimension % 2:
        raise ValueError("canonical dimension is half-integral")
    return Monomial(
        dimension=twice_dimension // 2,
        pq=sum(count * field.pq for count, field in zip(vector, FIELDS)),
        vector=sum(count * field.vector for count, field in zip(vector, FIELDS)),
        centre=sum(count * field.centre for count, field in zip(vector, FIELDS)) % 4,
        triality=sum(count * field.triality for count, field in zip(vector, FIELDS)) % 3,
        n_fermions=n_fermions,
        counts=tuple(vector),
    )


EXPLICIT_OPERATORS: Dict[str, Monomial] = {
    # (S dagger)^3 (16_F 16bar_s)_1
    "O6_portal": monomial_from_counts({"Sd": 3, "F": 1, "b": 1}),
    # (S dagger)^2 [(16_s 16_s)_10]^2
    "O8_vector_breaker": monomial_from_counts({"Sd": 2, "s": 4}),
    # The v15 one-sided Majorana insertion.
    "O9_one_sided": monomial_from_counts({"Sd": 5, "b": 2, "Hm": 1}),
    # Regression: omitted in v15's bilinear-only scan.
    "O10_six_fermion": monomial_from_counts({"b": 6, "Hp": 1}),
    # Regression: omitted in v15's bilinear-only scan.
    "O12_mixed": monomial_from_counts({"Sd": 6, "F": 1, "s": 3}),
    # Lowest optional-Z3, vector-neutral local spurion.
    "O19_dirac": monomial_from_counts({"Sd": 16, "s": 1, "b": 1}),
    # The dagger on Hp is essential in the equivalent S^16 FF Hp form.
    "O20_family": monomial_from_counts({"S": 16, "F": 2, "Hp": 1}),
}


def _fermion_summaries(max_dimension: int) -> list[tuple]:
    summaries = {}
    max_fermions = (2 * max_dimension) // 3
    for n_fermions in range(0, max_fermions + 1, 2):
        for counts in weak_compositions(n_fermions, len(FERMIONS)):
            pq = sum(n * field.pq for n, field in zip(counts, FERMIONS))
            centre = sum(n * field.centre for n, field in zip(counts, FERMIONS)) % 4
            vector = sum(n * field.vector for n, field in zip(counts, FERMIONS))
            triality = sum(n * field.triality for n, field in zip(counts, FERMIONS)) % 3
            key = (n_fermions, pq, centre, vector, triality)
            summaries.setdefault(key, counts)
    return [key + (counts,) for key, counts in summaries.items()]


def _scalar_summaries(max_dimension: int) -> list[tuple]:
    summaries = {}
    for n_scalars in range(max_dimension + 1):
        for counts in weak_compositions(n_scalars, len(SCALARS)):
            pq = sum(n * field.pq for n, field in zip(counts, SCALARS))
            centre = sum(n * field.centre for n, field in zip(counts, SCALARS)) % 4
            key = (n_scalars, pq, centre)
            summaries.setdefault(key, counts)
    return [key + (counts,) for key, counts in summaries.items()]


def enumerate_overcomplete_catalog(
    max_dimension: int = 20,
    require_triality: bool = False,
) -> Dict[Tuple[int, int], Monomial]:
    """Return the least-dimensional monomial for every (Q/17, V).

    Neutral insertions, derivatives, gauge strengths and 210_H are omitted:
    they change neither Q_PQ nor V and only increase the suppression.  The
    catalogue therefore remains complete for a minimum-suppression proof.
    """
    catalog: Dict[Tuple[int, int], Monomial] = {}
    fermion_data = _fermion_summaries(max_dimension)
    scalar_data = _scalar_summaries(max_dimension)
    for n_fermions, fq, fc, vector, triality, fcounts in fermion_data:
        fermion_dimension = 3 * n_fermions // 2
        for n_scalars, sq, sc, scounts in scalar_data:
            dimension = fermion_dimension + n_scalars
            if dimension > max_dimension or (fc + sc) % 4:
                continue
            pq = fq + sq
            if pq % 17 or (require_triality and triality % 3):
                continue
            if pq == 0 and vector == 0:
                continue
            counts = tuple(fcounts) + tuple(scounts)
            monomial = Monomial(
                dimension=dimension,
                pq=pq,
                vector=vector,
                centre=0,
                triality=triality,
                n_fermions=n_fermions,
                counts=counts,
            )
            key = (pq // 17, vector)
            previous = catalog.get(key)
            if previous is None or (dimension, monomial.label) < (
                previous.dimension,
                previous.label,
            ):
                catalog[key] = monomial
    return catalog


def minimum_local_pq_dimension(catalog: Mapping[Tuple[int, int], Monomial]) -> int:
    return min(op.dimension for op in catalog.values() if op.pq)


def minimum_q0_vector_breaking_dimension(
    catalog: Mapping[Tuple[int, int], Monomial],
) -> int:
    return min(op.dimension for op in catalog.values() if not op.pq and op.vector)


def renormalizable_vector_breakers(
    catalog: Mapping[Tuple[int, int], Monomial],
) -> list[Monomial]:
    return [
        op for op in catalog.values()
        if op.pq == 0 and op.vector != 0 and op.dimension <= 4
    ]


def minimum_vacuum_closure(
    catalog: Mapping[Tuple[int, int], Monomial],
    max_planck_power: int = 20,
) -> Closure | None:
    """Find the least P=sum(d_i-4) vacuum-sensitive spurion set.

    A vacuum amplitude must conserve the exact spectator vector number V.
    After its fermions are closed with PQ-conserving interactions, Spin(10)
    scalar parity requires Q_PQ=0 mod 4.  Since each Planck spurion has
    Q_PQ=17m, the target is V=0 and nonzero m=0 mod 4.
    """
    useful = sorted(
        (op for op in catalog.values() if op.planck_power > 0),
        key=lambda op: (op.planck_power, op.dimension, abs(op.m17), abs(op.vector), op.label),
    )
    start = (0, 0)
    best = {start: 0}
    previous: dict[tuple[int, int], tuple[tuple[int, int], Monomial]] = {}
    queue = [(0, 0, 0)]
    while queue:
        cost, m17, vector = heapq.heappop(queue)
        state = (m17, vector)
        if cost != best.get(state) or cost > max_planck_power:
            continue
        if state != start and vector == 0 and m17 != 0 and m17 % 4 == 0:
            path = []
            while state != start:
                old_state, op = previous[state]
                path.append(op)
                state = old_state
            path.reverse()
            return Closure(cost, m17, vector, tuple(path))
        for op in useful:
            new_cost = cost + op.planck_power
            if new_cost > max_planck_power:
                continue
            new_state = (m17 + op.m17, vector + op.vector)
            if new_cost < best.get(new_state, math.inf):
                best[new_state] = new_cost
                previous[new_state] = (state, op)
                heapq.heappush(queue, (new_cost, *new_state))
    return None


def explicit_p12_certificate() -> Closure:
    portal = EXPLICIT_OPERATORS["O6_portal"]
    vector_breaker = EXPLICIT_OPERATORS["O8_vector_breaker"]
    operators = (portal, portal, portal, portal, vector_breaker)
    return Closure(
        planck_power=sum(op.planck_power for op in operators),
        m17=sum(op.m17 for op in operators),
        vector=sum(op.vector for op in operators),
        operators=operators,
    )


def one_sided_mass_invariants(
    dirac_mass: float,
    majorana_mass: float,
    phases: Iterable[float],
) -> list[tuple[float, float]]:
    """Return tr(M^dagger M), det(M^dagger M) for each phase.

    M = [[0, M_D], [M_D, delta exp(i phi)]].  Both invariants, hence both
    singular values and the one-loop Coleman-Weinberg potential, are phase
    independent.  This invalidates v15's term linear in delta.
    """
    trace = 2.0 * dirac_mass**2 + majorana_mass**2
    determinant = dirac_mass**4
    return [(trace, determinant) for _ in phases]


def scalar_quality_numbers(
    v_s: float,
    chi_fourth_root: float = 75.5e-3,
    reduced_planck_mass: float = 2.435e18,
) -> dict:
    chi = chi_fourth_root**4
    s_vev = v_s / math.sqrt(2.0)
    scalar_delta = s_vev**17 / reduced_planck_mass**13 / chi
    d_min = next(
        dimension
        for dimension in range(5, 40)
        if s_vev**dimension
        / reduced_planck_mass ** (dimension - 4)
        / chi
        < 1.0e-10
    )
    ceiling = math.sqrt(2.0) * (
        1.0e-10 * chi * reduced_planck_mass**13
    ) ** (1.0 / 17.0)
    return {
        "leading_operator": "S^17/M_Pl^13",
        "leading_dimension": 17,
        "delta_theta_scalar": scalar_delta,
        "minimum_safe_dimension": d_min,
        "v_s_quality_ceiling_GeV": ceiling,
    }


def nda_vacuum_bound(
    matching_scale: float,
    planck_power: int,
    chi_fourth_root: float = 75.5e-3,
    reduced_planck_mass: float = 2.435e18,
) -> float:
    """Wilsonian NDA bound per unit effective Wilson coefficient."""
    chi = chi_fourth_root**4
    return (
        matching_scale**4
        * (matching_scale / reduced_planck_mass) ** planck_power
        / chi
    )


def combined_z51_anomalies() -> dict:
    """Optional Z3 diagnostic using the CRT lift to Z51.

    This is retained only as a regression/diagnostic.  The corrected model
    does not need Z3 and therefore avoids an exactly stable charged sector.
    """
    q_f, q_s, q_b = 18, 19, 11
    mixed = 3 * 2 * q_f + 5 * 2 * (q_s + q_b)
    gravitational = 3 * 16 * q_f + 5 * 16 * (q_s + q_b)
    cubic = 3 * 16 * q_f**3 + 5 * 16 * (q_s**3 + q_b**3)
    return {
        "crt_charges": {"F": q_f, "s": q_s, "b": q_b},
        "mixed": mixed,
        "gravitational": gravitational,
        "cubic": cubic,
        "quotients": [mixed // 51, gravitational // 51, cubic // 51],
        "all_divisible_by_51": all(value % 51 == 0 for value in (mixed, gravitational, cubic)),
    }


def build_quality_report(v_s: float, matching_scale: float) -> dict:
    catalog = enumerate_overcomplete_catalog(max_dimension=20)
    catalog_z3 = enumerate_overcomplete_catalog(max_dimension=20, require_triality=True)
    closure = minimum_vacuum_closure(catalog, max_planck_power=16)
    closure_z3 = minimum_vacuum_closure(catalog_z3, max_planck_power=18)
    certificate = explicit_p12_certificate()
    scalar = scalar_quality_numbers(v_s)
    bound = nda_vacuum_bound(matching_scale, certificate.planck_power)
    return {
        "status": "Z17 alone is sufficient under the stated Wilsonian-NDA assumptions",
        "method": {
            "catalogue": "Lorentz-parity and Spin(10)-centre necessary-condition superset",
            "vacuum_conditions": ["spectator vector V=0", "nonzero Q_PQ divisible by 68"],
            "suppression_exponent": "P = sum_i (d_i - 4)",
            "assumption": "all relevant Wilson coefficients are O(1) at M_Pl and all matching-scale vevs/masses are <= M_s",
        },
        "local_operator_minimum_dimension": minimum_local_pq_dimension(catalog),
        "pq_conserving_vector_breaker_minimum_dimension": minimum_q0_vector_breaking_dimension(catalog),
        "renormalizable_vector_breakers": [op.as_dict() for op in renormalizable_vector_breakers(catalog)],
        "explicit_operator_regressions": {
            name: operator.as_dict() for name, operator in EXPLICIT_OPERATORS.items()
        },
        "vacuum_closure_minimum": {
            "overcatalogue_result": None if closure is None else {
                "P": closure.planck_power,
                "Q_PQ": closure.pq,
                "V": closure.vector,
                "operators": closure.multiplicities(),
            },
            "explicit_SO10_certificate": {
                "P": certificate.planck_power,
                "Q_PQ": certificate.pq,
                "V": certificate.vector,
                "operators": certificate.multiplicities(),
                "closure": "four spectator s-b chirality flips and two ordinary-family 10_H-channel chirality flips",
            },
        },
        "delta_theta_NDA_per_Ceff": bound,
        "maximum_Ceff_at_1e-10": 1.0e-10 / bound,
        "scalar_only": scalar,
        "one_sided_majorana_result": "no phase-dependent one-insertion Coleman-Weinberg term",
        "optional_Z3_diagnostic_only": {
            "local_minimum_dimension": minimum_local_pq_dimension(catalog_z3),
            "vacuum_closure_minimum_P": None if closure_z3 is None else closure_z3.planck_power,
            "z51_anomalies": combined_z51_anomalies(),
            "model_choice": "not imposed; unnecessary and would make the lightest spectator-triality state exactly stable",
        },
    }


__all__ = [
    "Closure",
    "EXPLICIT_OPERATORS",
    "FIELDS",
    "Monomial",
    "build_quality_report",
    "combined_z51_anomalies",
    "enumerate_overcomplete_catalog",
    "explicit_p12_certificate",
    "minimum_local_pq_dimension",
    "minimum_q0_vector_breaking_dimension",
    "minimum_vacuum_closure",
    "monomial_from_counts",
    "nda_vacuum_bound",
    "one_sided_mass_invariants",
    "renormalizable_vector_breakers",
    "scalar_quality_numbers",
]
