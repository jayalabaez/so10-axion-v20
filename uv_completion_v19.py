#!/usr/bin/env python3
"""Continuous UV completion and heavy-threshold audit for v19.

The module embeds the low-energy :math:`Z_{17}` in an anomaly-free
``U(1)_X``.  A charge-17 scalar ``Phi`` breaks the continuous gauge group,
while carrying no accidental PQ charge.  The heavy anomaly-cancelling
fermions are included explicitly in an intentionally over-complete operator
search.  As in v17, the search imposes necessary (not sufficient)
Spin(10)/Lorentz conditions, so a non-existence result is conservative.

All charges are primitive integers.  ``T(16)=2`` and ``dim(16)=16`` are
used for the mixed, gravitational and cubic anomaly coefficients.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
import heapq
import math
from typing import Iterable, Iterator, Mapping, Sequence


Vector = tuple[int, int, int, int]
ZERO_VECTOR: Vector = (0, 0, 0, 0)


@dataclass(frozen=True)
class AnomalySpecies:
    name: str
    multiplicity: int
    spin10_dimension: int
    spin10_index: int
    x: int

    @property
    def mixed_spin10(self) -> int:
        return self.multiplicity * self.spin10_index * self.x

    @property
    def gravitational(self) -> int:
        return self.multiplicity * self.spin10_dimension * self.x

    @property
    def cubic(self) -> int:
        return self.multiplicity * self.spin10_dimension * self.x**3


LIGHT_ANOMALY_SPECIES: tuple[AnomalySpecies, ...] = (
    AnomalySpecies("3 x 16_F", 3, 16, 2, +1),
    AnomalySpecies("5 x 16_s", 5, 16, 2, +2),
    AnomalySpecies("5 x 16bar_s", 5, 16, 2, -6),
)

HEAVY_SPIN10_SPECIES: tuple[AnomalySpecies, ...] = (
    AnomalySpecies("Psi_16", 1, 16, 2, +7),
    AnomalySpecies("PsiBar_16bar", 1, 16, 2, +10),
)

HEAVY_SINGLET_SPECIES: tuple[AnomalySpecies, ...] = (
    AnomalySpecies("n_-6", 1, 1, 0, -6),
    AnomalySpecies("n_23", 1, 1, 0, +23),
    AnomalySpecies("n_-26", 1, 1, 0, -26),
    AnomalySpecies("n_9", 1, 1, 0, +9),
)


def anomaly_tuple(species: Iterable[AnomalySpecies]) -> tuple[int, int, int]:
    data = tuple(species)
    return (
        sum(item.mixed_spin10 for item in data),
        sum(item.gravitational for item in data),
        sum(item.cubic for item in data),
    )


def anomaly_report() -> dict:
    light = anomaly_tuple(LIGHT_ANOMALY_SPECIES)
    spin = anomaly_tuple(HEAVY_SPIN10_SPECIES)
    singlets = anomaly_tuple(HEAVY_SINGLET_SPECIES)
    total = tuple(a + b + c for a, b, c in zip(light, spin, singlets))
    return {
        "convention": "(A[Spin(10)^2 U(1)_X], A[grav^2 U(1)_X], A[U(1)_X^3])",
        "light": light,
        "heavy_spin10_pair": spin,
        "heavy_singlets": singlets,
        "total": total,
        "all_continuous_anomalies_cancel": total == (0, 0, 0),
        "mass_terms": {
            "spin10_pair": "Phi_dagger Psi_7 PsiBar_10",
            "singlet_pair_A": "Phi_dagger n_-6 n_23",
            "singlet_pair_B": "Phi n_-26 n_9",
        },
    }


def completion_solutions(max_abs_charge: int) -> list[tuple[int, ...]]:
    """Enumerate a bounded one-pair/two-singlet-pair completion ansatz.

    The Spin(10) pair has charges ``(x,17-x)`` and a ``Phi_dagger`` mass.
    One singlet pair has sum ``+17`` and one has sum ``-17``.  This is a
    bounded statement about this ansatz, not a theorem about arbitrary UV
    completions.
    """
    solutions: set[tuple[int, ...]] = set()
    bound = int(max_abs_charge)
    for x in range(-bound, bound + 1):
        y = 17 - x
        if abs(y) > bound:
            continue
        for a in range(-bound, bound + 1):
            b = 17 - a
            if abs(b) > bound:
                continue
            for c in range(-bound, bound + 1):
                d = -17 - c
                values = (x, y, a, b, c, d)
                if abs(d) > bound:
                    continue
                cubic = -16592 + 16 * (x**3 + y**3)
                cubic += a**3 + b**3 + c**3 + d**3
                if cubic == 0:
                    solutions.add(values)
    return sorted(solutions)


def minimality_within_ansatz() -> dict:
    below = completion_solutions(25)
    at = completion_solutions(26)
    canonical = (7, 10, -6, 23, -26, 9)
    return {
        "ansatz": "one 16+16bar pair with X-sum +17, plus singlet pairs with sums +17 and -17",
        "solutions_with_max_abs_charge_at_most_25": len(below),
        "solutions_with_max_abs_charge_at_most_26": len(at),
        "canonical_solution_present": canonical in at,
        "minimum_max_abs_charge_in_this_ansatz": 26 if not below and at else None,
        "canonical_charges": canonical,
    }


@dataclass(frozen=True)
class Field:
    name: str
    x: int
    pq: int
    centre: int
    vector: Vector
    twice_dimension: int
    fermion: bool


def _neg(v: Vector) -> Vector:
    return tuple(-item for item in v)  # type: ignore[return-value]


def _add(a: Vector, b: Vector) -> Vector:
    return tuple(x + y for x, y in zip(a, b))  # type: ignore[return-value]


# Vector entries are, in order, the light spectator number, the heavy
# Spin(10)-pair number, and the two heavy singlet-pair numbers.  Each is an
# exact symmetry of the complete renormalizable Lagrangian.
FERMIONS: tuple[Field, ...] = (
    Field("F", +1, +1, +1, ZERO_VECTOR, 3, True),
    Field("Fd", -1, -1, -1, ZERO_VECTOR, 3, True),
    Field("s", +2, +2, +1, (+1, 0, 0, 0), 3, True),
    Field("sd", -2, -2, -1, (-1, 0, 0, 0), 3, True),
    Field("b", -6, -6, -1, (-1, 0, 0, 0), 3, True),
    Field("bd", +6, +6, +1, (+1, 0, 0, 0), 3, True),
    Field("Psi", +7, 0, +1, (0, +1, 0, 0), 3, True),
    Field("Psid", -7, 0, -1, (0, -1, 0, 0), 3, True),
    Field("Bpsi", +10, 0, -1, (0, -1, 0, 0), 3, True),
    Field("Bpsid", -10, 0, +1, (0, +1, 0, 0), 3, True),
    Field("n6m", -6, 0, 0, (0, 0, +1, 0), 3, True),
    Field("n6md", +6, 0, 0, (0, 0, -1, 0), 3, True),
    Field("n23", +23, 0, 0, (0, 0, -1, 0), 3, True),
    Field("n23d", -23, 0, 0, (0, 0, +1, 0), 3, True),
    Field("n26m", -26, 0, 0, (0, 0, 0, +1), 3, True),
    Field("n26md", +26, 0, 0, (0, 0, 0, -1), 3, True),
    Field("n9", +9, 0, 0, (0, 0, 0, -1), 3, True),
    Field("n9d", -9, 0, 0, (0, 0, 0, +1), 3, True),
)

SCALARS: tuple[Field, ...] = (
    Field("S", +4, +4, 0, ZERO_VECTOR, 2, False),
    Field("Sd", -4, -4, 0, ZERO_VECTOR, 2, False),
    Field("Hm", -2, -2, 2, ZERO_VECTOR, 2, False),
    Field("Hp", +2, +2, 2, ZERO_VECTOR, 2, False),
    Field("Phi", +17, 0, 0, ZERO_VECTOR, 2, False),
    Field("Phid", -17, 0, 0, ZERO_VECTOR, 2, False),
)

ALL_FIELDS = FERMIONS + SCALARS


@dataclass(frozen=True)
class Operator:
    dimension: int
    x: int
    pq: int
    centre: int
    vector: Vector
    n_fermions: int
    labels: tuple[str, ...]

    @property
    def planck_power(self) -> int:
        return self.dimension - 4

    @property
    def label(self) -> str:
        counts = Counter(self.labels)
        return " ".join(
            name if count == 1 else f"{name}^{count}"
            for name, count in sorted(counts.items())
        )

    def as_dict(self) -> dict:
        return {
            "label": self.label,
            "dimension": self.dimension,
            "planck_power": self.planck_power,
            "X": self.x,
            "Q_PQ": self.pq,
            "spin10_centre_mod4": self.centre % 4,
            "vector": self.vector,
            "n_fermions": self.n_fermions,
        }


@dataclass(frozen=True)
class Closure:
    planck_power: int
    pq: int
    vector: Vector
    operators: tuple[Operator, ...]

    def as_dict(self) -> dict:
        counts = Counter(op.label for op in self.operators)
        by_label = {op.label: op for op in self.operators}
        return {
            "P": self.planck_power,
            "Q_PQ": self.pq,
            "vector": self.vector,
            "operators": [
                {"multiplicity": counts[label], **by_label[label].as_dict()}
                for label in sorted(counts)
            ],
        }


def _layers(fields: Sequence[Field], max_number: int) -> tuple[dict, ...]:
    """Dynamic charge summaries, retaining one monomial per exact state."""
    start = {(0, 0, 0, ZERO_VECTOR): ()}
    layers: list[dict] = [start]
    for _ in range(max_number):
        new: dict[tuple[int, int, int, Vector], tuple[str, ...]] = {}
        for (x, pq, centre, vector), labels in layers[-1].items():
            for field in fields:
                key = (
                    x + field.x,
                    pq + field.pq,
                    (centre + field.centre) % 4,
                    _add(vector, field.vector),
                )
                candidate = tuple(sorted(labels + (field.name,)))
                if key not in new or candidate < new[key]:
                    new[key] = candidate
        layers.append(new)
    return tuple(layers)


@lru_cache(maxsize=None)
def operator_frontier(max_dimension: int = 16) -> dict[tuple[int, Vector], Operator]:
    """Least-dimensional ``U(1)_X``-invariant necessary-condition frontier."""
    max_fermions = 2 * max_dimension // 3
    fermion_layers = _layers(FERMIONS, max_fermions)
    scalar_layers = _layers(SCALARS, max_dimension)
    scalar_index: list[dict[tuple[int, int], list[tuple[int, tuple[str, ...]]]]] = []
    for layer in scalar_layers:
        index: dict[tuple[int, int], list[tuple[int, tuple[str, ...]]]] = defaultdict(list)
        for (x, pq, centre, _vector), labels in layer.items():
            index[(x, centre)].append((pq, labels))
        scalar_index.append(index)

    frontier: dict[tuple[int, Vector], Operator] = {}
    for n_fermions in range(0, max_fermions + 1, 2):
        fermion_dimension = 3 * n_fermions // 2
        for n_scalars in range(max_dimension - fermion_dimension + 1):
            dimension = fermion_dimension + n_scalars
            if dimension < 5:
                continue
            for (fx, fpq, fcentre, vector), flabels in fermion_layers[n_fermions].items():
                needed = (-fx, (-fcentre) % 4)
                for spq, slabels in scalar_index[n_scalars].get(needed, ()):
                    pq = fpq + spq
                    if pq == 0 and vector == ZERO_VECTOR:
                        continue
                    operator = Operator(
                        dimension=dimension,
                        x=0,
                        pq=pq,
                        centre=0,
                        vector=vector,
                        n_fermions=n_fermions,
                        labels=flabels + slabels,
                    )
                    key = (pq, vector)
                    old = frontier.get(key)
                    if old is None or (operator.dimension, operator.label) < (
                        old.dimension,
                        old.label,
                    ):
                        frontier[key] = operator
    return frontier


def renormalizable_accidental_symmetry_audit() -> dict:
    """Search a conservative superset of all dimension <=4 monomials."""
    fermion_layers = _layers(FERMIONS, 2)
    scalar_layers = _layers(SCALARS, 4)
    dangerous: list[Operator] = []
    for n_fermions in (0, 2):
        fermion_dimension = 3 * n_fermions // 2
        for n_scalars in range(5 - fermion_dimension):
            dimension = fermion_dimension + n_scalars
            if dimension == 0 or dimension > 4:
                continue
            for (fx, fpq, fc, fv), flabels in fermion_layers[n_fermions].items():
                for (sx, spq, sc, _), slabels in scalar_layers[n_scalars].items():
                    if fx + sx or (fc + sc) % 4:
                        continue
                    pq = fpq + spq
                    if pq == 0 and fv == ZERO_VECTOR:
                        continue
                    dangerous.append(
                        Operator(dimension, 0, pq, 0, fv, n_fermions, flabels + slabels)
                    )
    unique = {(op.dimension, op.label): op for op in dangerous}
    ordered = [unique[key].as_dict() for key in sorted(unique)]
    return {
        "catalogue": "Lorentz parity + Spin(10)-centre necessary-condition superset",
        "pq_or_vector_breaking_candidates": ordered,
        "accidental_PQ_and_four_vector_numbers_exact_at_d_le_4": not ordered,
    }


def minimum_vacuum_closure(
    frontier: Mapping[tuple[int, Vector], Operator],
    max_planck_power: int = 16,
) -> Closure | None:
    """Dijkstra search for a PQ-sensitive, vector-neutral vacuum closure."""
    useful = sorted(
        (op for op in frontier.values() if op.planck_power > 0),
        key=lambda op: (
            op.planck_power,
            abs(op.pq),
            sum(abs(v) for v in op.vector),
            op.label,
        ),
    )
    start = (0, ZERO_VECTOR)
    best: dict[tuple[int, Vector], int] = {start: 0}
    previous: dict[tuple[int, Vector], tuple[tuple[int, Vector], Operator]] = {}
    queue: list[tuple[int, int, Vector]] = [(0, 0, ZERO_VECTOR)]
    while queue:
        cost, pq, vector = heapq.heappop(queue)
        state = (pq, vector)
        if cost != best.get(state) or cost > max_planck_power:
            continue
        if state != start and pq and pq % 4 == 0 and vector == ZERO_VECTOR:
            path: list[Operator] = []
            while state != start:
                old, operator = previous[state]
                path.append(operator)
                state = old
            path.reverse()
            return Closure(cost, pq, vector, tuple(path))
        for operator in useful:
            new_cost = cost + operator.planck_power
            if new_cost > max_planck_power:
                continue
            new_state = (pq + operator.pq, _add(vector, operator.vector))
            if new_cost < best.get(new_state, math.inf):
                best[new_state] = new_cost
                previous[new_state] = (state, operator)
                heapq.heappush(queue, (new_cost, *new_state))
    return None


def explicit_p13_certificate() -> Closure:
    by_labels = {
        (operator.dimension, operator.label): operator
        for operator in operator_frontier(16).values()
    }
    requested = (
        (6, "Bpsi S^0 Sd^3 s"),  # compatibility placeholder, replaced below
    )
    del requested

    def find(dimension: int, required: Counter[str]) -> Operator:
        for operator in by_labels.values():
            if operator.dimension == dimension and Counter(operator.labels) == required:
                return operator
        raise RuntimeError(f"explicit certificate operator not found: {required}")

    portal = find(6, Counter({"Bpsi": 1, "s": 1, "Sd": 3}))
    light = find(7, Counter({"F": 1, "b": 1, "Phi": 1, "Sd": 3}))
    heavy = find(7, Counter({"Psi": 2, "Hm": 1, "Sd": 3}))
    operators = (portal, portal, light, light, heavy)
    return Closure(
        planck_power=sum(op.planck_power for op in operators),
        pq=sum(op.pq for op in operators),
        vector=tuple(sum(op.vector[i] for op in operators) for i in range(4)),  # type: ignore[arg-type]
        operators=operators,
    )


def axion_mixing(v_s: float, v_phi: float) -> dict:
    """Project the accidental-PQ phase orthogonal to the heavy gauge boson."""
    norm = math.hypot(17.0 * v_phi, 4.0 * v_s)
    physical_shift = 68.0 * v_s * v_phi / norm
    f_a = physical_shift / 68.0
    limiting = v_s / 17.0
    return {
        "gauge_direction_in_(aPhi,aS)": (17.0 * v_phi, 4.0 * v_s),
        "physical_axion_direction_in_(aPhi,aS)": (-4.0 * v_s / norm, 17.0 * v_phi / norm),
        "physical_PQ_shift_coefficient": physical_shift,
        "f_a_exact_GeV": f_a,
        "f_a_large_vPhi_limit_GeV": limiting,
        "relative_correction_to_vS_over_17": f_a / limiting - 1.0,
    }


def abelian_beta_and_landau_bound(v_phi: float, cutoff: float = 2.435e18) -> dict:
    """One-loop U(1)_X beta coefficient and perturbative cutoff bound."""
    fermion_q2 = 6954  # sum over Weyl fields including Spin(10) dimensions
    scalar_q2 = 16 + 10 * 4 + 126 * 4 + 17**2
    beta = (2.0 / 3.0) * fermion_q2 + (1.0 / 3.0) * scalar_q2
    logarithm = math.log(cutoff / v_phi)
    g_max = math.sqrt(8.0 * math.pi**2 / (beta * logarithm))
    return {
        "sum_Weyl_dimR_X2": fermion_q2,
        "sum_complex_scalar_dimR_X2": scalar_q2,
        "b_X_one_loop": beta,
        "cutoff_GeV": cutoff,
        "v_phi_GeV": v_phi,
        "maximum_gX_for_landau_pole_above_cutoff": g_max,
        "example_gX": 0.05,
        "example_landau_pole_GeV": v_phi
        * math.exp(8.0 * math.pi**2 / (beta * 0.05**2)),
    }


def build_uv_report(v_s: float = 6.313855e11, v_phi: float = 1.0e17) -> dict:
    frontier = operator_frontier(16)
    closure = minimum_vacuum_closure(frontier, 16)
    certificate = explicit_p13_certificate()
    return {
        "status": "explicit anomaly-free U(1)_X -> Z17 completion; heavy-threshold closure audited",
        "charges": {
            "Phi": {"Spin10": "1", "X": 17, "PQ": 0},
            "Psi": {"Spin10": "16", "X": 7, "PQ": 0},
            "PsiBar": {"Spin10": "16bar", "X": 10, "PQ": 0},
            "singlet_Weyl": [-6, 23, -26, 9],
        },
        "anomalies": anomaly_report(),
        "minimality": minimality_within_ansatz(),
        "renormalizable_audit": renormalizable_accidental_symmetry_audit(),
        "quality_overcatalogue": {
            "maximum_local_dimension": 16,
            "frontier_states": len(frontier),
            "no_vacuum_closure_through_P12": closure is not None and closure.planck_power == 13,
            "minimum": None if closure is None else closure.as_dict(),
            "explicit_spin10_certificate": certificate.as_dict(),
            "explicit_graph": {
                "operators": "2 (Sd)^3(s PsiBar) + 2 Phi(Sd)^3(F b) + (Sd)^3(Psi Psi)_10 Hm",
                "topology": "connected one-loop five-propagator polygon",
                "resulting_phase": "Phi^4 (Sd)^17 (Hm Hp)",
                "Q_PQ": -68,
            },
        },
        "axion_mixing": axion_mixing(v_s, v_phi),
        "u1_running": abelian_beta_and_landau_bound(v_phi),
        "declared_limitations": [
            "minimality is only within the one-Spin(10)-pair/two-singlet-pair ansatz",
            "the hierarchy vPhi >> vS requires a small Higgs portal or another stabilization mechanism",
            "the listed heavy anomalons have no renormalizable decay portal to ordinary matter; cosmology requires reheating below their masses or an added decay mechanism",
            "unknown Planck-scale Wilson tensors are parameterized, not predicted",
            "cosmic strings of U(1)_X are not simulated",
        ],
    }


__all__ = [
    "Closure",
    "FERMIONS",
    "SCALARS",
    "ZERO_VECTOR",
    "abelian_beta_and_landau_bound",
    "anomaly_report",
    "axion_mixing",
    "build_uv_report",
    "completion_solutions",
    "explicit_p13_certificate",
    "minimality_within_ansatz",
    "minimum_vacuum_closure",
    "operator_frontier",
    "renormalizable_accidental_symmetry_audit",
]


if __name__ == "__main__":
    import json

    print(json.dumps(build_uv_report(), indent=2))
