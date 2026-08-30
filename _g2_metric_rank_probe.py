#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations, permutations
import argparse
import json
from pathlib import Path
import random
import time

from _g2_contraction_graphs import RANKS, sector_candidates

ROOT = Path(__file__).resolve().parent
PRIME = 1009


def parity(values: tuple[int, ...]) -> int:
    return -1 if sum(values[i] > values[j] for i in range(len(values)) for j in range(i + 1, len(values))) % 2 else 1


@lru_cache(maxsize=None)
def signed_permutations(values: tuple[int, ...]):
    result = []
    for item in permutations(values):
        result.append((item, parity(item)))
    return tuple(result)


def complement(values: tuple[int, ...]):
    chosen = set(values)
    return tuple(i for i in range(10) if i not in chosen)


def wedge_join_sign(left: tuple[int, ...], right: tuple[int, ...]):
    return parity(left + right)


FIVE_REPRESENTATIVES = tuple(
    item for item in combinations(range(10), 5) if item < complement(item)
)


def random_terms(
    rank: int,
    support: int,
    rng: random.Random,
    chirality: int | None = None,
    selected_five: tuple[tuple[int, ...], ...] | None = None,
):
    if chirality is None:
        pool = tuple(combinations(range(10), rank))
        selected = rng.sample(pool, min(support, len(pool)))
        return tuple((item, rng.randrange(1, PRIME)) for item in selected)
    sqrt_minus_one = next(value for value in range(2, PRIME) if value * value % PRIME == PRIME - 1)
    selected = (
        selected_five
        if selected_five is not None
        else tuple(rng.sample(FIVE_REPRESENTATIVES, min(support, len(FIVE_REPRESENTATIVES))))
    )
    result = []
    for item in selected:
        coefficient = rng.randrange(1, PRIME)
        other = complement(item)
        sign = wedge_join_sign(item, other)
        # * e_I = sign e_Ic and the eigenvalue is chirality*i.
        partner = (-chirality * sign * sqrt_minus_one * coefficient) % PRIME
        result.extend(((item, coefficient), (other, partner)))
    return tuple(result)


def antisymmetric_tensor(terms):
    data = {}
    for item, coefficient in terms:
        for ordered, sign in signed_permutations(item):
            data[ordered] = (data.get(ordered, 0) + sign * coefficient) % PRIME
    return {key: value for key, value in data.items() if value}


@dataclass
class SparseTensor:
    labels: tuple[int, ...]
    data: dict[tuple[int, ...], int]


def contract_pair(left: SparseTensor, right: SparseTensor):
    common = tuple(sorted(set(left.labels) & set(right.labels)))
    if not common:
        raise ArithmeticError("disconnected contraction path")
    lp_common = tuple(left.labels.index(label) for label in common)
    rp_common = tuple(right.labels.index(label) for label in common)
    lp_free = tuple(i for i, label in enumerate(left.labels) if label not in common)
    rp_free = tuple(i for i, label in enumerate(right.labels) if label not in common)
    buckets = {}
    for key, value in right.data.items():
        shared = tuple(key[i] for i in rp_common)
        buckets.setdefault(shared, []).append((tuple(key[i] for i in rp_free), value))
    output = {}
    for key, value in left.data.items():
        shared = tuple(key[i] for i in lp_common)
        left_free = tuple(key[i] for i in lp_free)
        for right_free, other in buckets.get(shared, ()): 
            out_key = left_free + right_free
            output[out_key] = (output.get(out_key, 0) + value * other) % PRIME
    output = {key: value for key, value in output.items() if value}
    labels = tuple(left.labels[i] for i in lp_free) + tuple(right.labels[i] for i in rp_free)
    return SparseTensor(labels, output)


def graph_labels(n: int, flat_edges: tuple[int, ...]):
    pairs = tuple((i, j) for i in range(n) for j in range(i + 1, n))
    labels = [[] for _ in range(n)]
    edge_id = 0
    for (i, j), multiplicity in zip(pairs, flat_edges):
        for _ in range(multiplicity):
            labels[i].append(edge_id)
            labels[j].append(edge_id)
            edge_id += 1
    return tuple(tuple(item) for item in labels)


def epsilon_graph_labels(n: int, epsilon_legs: tuple[int, ...], flat_edges: tuple[int, ...]):
    labels = [list(item) for item in graph_labels(n, flat_edges)]
    epsilon_position = 0
    for vertex, count in enumerate(epsilon_legs):
        for _ in range(count):
            labels[vertex].append(10_000 + epsilon_position)
            epsilon_position += 1
    if epsilon_position != 10:
        raise ArithmeticError("epsilon graph does not have ten oriented legs")
    return tuple(tuple(item) for item in labels)


def evaluate_metric_graph(species: tuple[int, ...], flat_edges: tuple[int, ...], field_data):
    labels = graph_labels(len(species), flat_edges)
    states = [SparseTensor(labels[i], field_data[species[i]]) for i in range(len(species))]
    scalar = 1
    while len(states) > 1:
        scalar_states = [state for state in states if not state.labels]
        if scalar_states:
            for state in scalar_states:
                scalar = scalar * state.data.get((), 0) % PRIME
            states = [state for state in states if state.labels]
            if not states:
                return scalar
            if len(states) == 1:
                break
        choices = []
        for i in range(len(states)):
            for j in range(i + 1, len(states)):
                common = len(set(states[i].labels) & set(states[j].labels))
                if common:
                    choices.append((-common, len(states[i].data) * len(states[j].data), i, j))
        if not choices:
            raise ArithmeticError("metric graph is disconnected")
        _, _, i, j = min(choices)
        merged = contract_pair(states[i], states[j])
        states = [state for index, state in enumerate(states) if index not in (i, j)] + [merged]
    final = states[0]
    if final.labels:
        raise ArithmeticError("uncontracted metric labels")
    return scalar * final.data.get((), 0) % PRIME


def evaluate_epsilon_graph(species: tuple[int, ...], epsilon_legs: tuple[int, ...], flat_edges: tuple[int, ...], field_data):
    labels = epsilon_graph_labels(len(species), epsilon_legs, flat_edges)
    states = [SparseTensor(labels[i], field_data[species[i]]) for i in range(len(species))]
    scalar = 1
    # Contract every metric-connected component, leaving only epsilon axes.
    while True:
        choices = []
        for i in range(len(states)):
            for j in range(i + 1, len(states)):
                common_labels = set(states[i].labels) & set(states[j].labels)
                common = sum(label < 10_000 for label in common_labels)
                if common:
                    choices.append((-common, len(states[i].data) * len(states[j].data), i, j))
        if not choices:
            break
        _, _, i, j = min(choices)
        merged = contract_pair(states[i], states[j])
        states = [state for index, state in enumerate(states) if index not in (i, j)] + [merged]
    components = []
    for state in states:
        epsilon_positions = tuple(sorted(label - 10_000 for label in state.labels if label >= 10_000))
        if len(epsilon_positions) != len(state.labels):
            raise ArithmeticError("uncontracted metric edge in epsilon component")
        if not epsilon_positions:
            scalar = scalar * state.data.get((), 0) % PRIME
            continue
        order = tuple(state.labels.index(10_000 + position) for position in epsilon_positions)
        exterior = {}
        for key, value in state.data.items():
            values = tuple(key[index] for index in order)
            if len(set(values)) != len(values):
                continue
            canonical = tuple(sorted(values))
            exterior[canonical] = (exterior.get(canonical, 0) + parity(values) * value) % PRIME
        components.append((epsilon_positions, {key: value for key, value in exterior.items() if value}))
    components.sort(key=lambda item: item[0])
    total = 0

    def combine(index: int, used: int, assignment: list[int], coefficient: int):
        nonlocal total
        if index == len(components):
            if used == (1 << 10) - 1:
                total = (total + coefficient * parity(tuple(assignment))) % PRIME
            return
        positions, exterior = components[index]
        for colors, value in exterior.items():
            mask = sum(1 << color for color in colors)
            if used & mask:
                continue
            updated = list(assignment)
            for position, color in zip(positions, colors):
                updated[position] = color
            combine(index + 1, used | mask, updated, coefficient * value % PRIME)

    combine(0, 0, [-1] * 10, scalar)
    return total


def sample_fields(counts: tuple[int, ...], support: int, seed: int):
    rng = random.Random(seed)
    data = {}
    selected_five: dict[int, tuple[tuple[int, ...], ...]] = {}
    if counts[3] and counts[4]:
        common = rng.choice(FIVE_REPRESENTATIVES)
        residual_pool = tuple(item for item in FIVE_REPRESENTATIVES if item != common)
        for species in (3, 4):
            selected_five[species] = (common,) + tuple(
                rng.sample(residual_pool, min(max(support - 1, 0), len(residual_pool)))
            )
    for species, count in enumerate(counts):
        if not count:
            continue
        rank = RANKS[species]
        chirality = 1 if species == 3 else -1 if species == 4 else None
        data[species] = antisymmetric_tensor(
            random_terms(rank, support, rng, chirality, selected_five.get(species))
        )
    return data


def modular_rank_add(vector, basis):
    row = list(vector)
    for pivot in sorted(basis):
        factor = row[pivot]
        if factor:
            reference = basis[pivot]
            row = [(left - factor * right) % PRIME for left, right in zip(row, reference)]
    pivot = next((index for index, value in enumerate(row) if value), None)
    if pivot is None:
        return None
    inverse = pow(row[pivot], -1, PRIME)
    row = [value * inverse % PRIME for value in row]
    # Keep a reduced basis so later pivot ordering cannot matter.
    for old_pivot, reference in list(basis.items()):
        factor = reference[pivot]
        if factor:
            basis[old_pivot] = [(left - factor * right) % PRIME for left, right in zip(reference, row)]
    basis[pivot] = row
    return pivot


def determinant_mod(matrix):
    work = [list(row) for row in matrix]
    determinant = 1
    for column in range(len(work)):
        pivot = next((row for row in range(column, len(work)) if work[row][column]), None)
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            determinant = -determinant
        value = work[column][column] % PRIME
        determinant = determinant * value % PRIME
        inverse = pow(value, -1, PRIME)
        for row in range(column + 1, len(work)):
            factor = work[row][column] * inverse % PRIME
            if factor:
                for index in range(column, len(work)):
                    work[row][index] = (work[row][index] - factor * work[column][index]) % PRIME
    return determinant % PRIME


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--counts", default="2,0,0,2,2")
    parser.add_argument("--support", type=int, default=2)
    parser.add_argument("--supports")
    parser.add_argument("--samples", type=int, default=1)
    parser.add_argument("--rank-target", type=int)
    parser.add_argument("--candidate-limit", type=int)
    parser.add_argument("--metric-indices")
    parser.add_argument("--epsilon-limit", type=int, default=0)
    parser.add_argument("--epsilon-offset", type=int, default=0)
    parser.add_argument("--epsilon-indices")
    args = parser.parse_args()
    counts = tuple(map(int, args.counts.split(",")))
    species = tuple(index for index, count in enumerate(counts) for _ in range(count))
    metric, epsilon = sector_candidates(counts)
    if args.metric_indices:
        selected_metric_indices = tuple(map(int, args.metric_indices.split(",")))
        metric = tuple(metric[index] for index in selected_metric_indices)
    elif args.candidate_limit is not None:
        metric = metric[: args.candidate_limit]
    if args.epsilon_indices:
        selected_epsilon_indices = tuple(map(int, args.epsilon_indices.split(",")))
        epsilon = tuple(epsilon[index] for index in selected_epsilon_indices)
    else:
        epsilon = epsilon[args.epsilon_offset : args.epsilon_offset + args.epsilon_limit]
    supports = tuple(map(int, args.supports.split(","))) if args.supports else (args.support,)
    candidates = tuple(("metric", graph) for graph in metric) + tuple(("epsilon", graph) for graph in epsilon)
    print(json.dumps({"counts": counts, "metric_candidates": len(metric), "epsilon_candidates": len(epsilon), "supports": supports}))
    basis = {}
    selected_rows = []
    selected_samples = []
    all_started = time.monotonic()
    for sample in range(args.samples):
        support = supports[sample % len(supports)]
        fields = sample_fields(counts, support, 20260814 + sample)
        started = time.monotonic()
        values = []
        sizes = []
        for index, (kind, graph) in enumerate(candidates):
            if kind == "metric":
                _, edges = graph
                values.append(evaluate_metric_graph(species, edges, fields))
            else:
                epsilon_legs, edges = graph
                values.append(evaluate_epsilon_graph(species, epsilon_legs, edges, fields))
            if args.samples <= 2 and (index + 1) % 100 == 0:
                print(json.dumps({"sample": sample, "done": index + 1, "seconds": time.monotonic() - started}), flush=True)
        print(json.dumps({"sample": sample, "support": support, "seconds": time.monotonic() - started,
            "nonzero": sum(value != 0 for value in values),
            "nonzero_indices": [index for index, value in enumerate(values) if value] if args.samples <= 2 else None,
            "values_sha256": __import__('hashlib').sha256(json.dumps(values).encode()).hexdigest()}), flush=True)
        if args.rank_target is not None:
            pivot = modular_rank_add(values, basis)
            if pivot is not None:
                selected_rows.append(values)
                selected_samples.append(sample)
            print(json.dumps({"sample": sample, "rank": len(basis), "pivot": pivot}), flush=True)
            if len(basis) >= args.rank_target:
                columns = sorted(basis)
                minor = [[row[column] for column in columns] for row in selected_rows]
                determinant = determinant_mod(minor)
                payload = {
                    "counts": counts,
                    "target": args.rank_target,
                    "rank": len(basis),
                    "prime": PRIME,
                    "support_schedule": supports,
                    "selected_samples": selected_samples,
                    "pivot_columns": columns,
                    "minor_determinant_mod_prime": determinant,
                    "minor_sha256": __import__('hashlib').sha256(json.dumps(minor, separators=(",", ":")).encode()).hexdigest(),
                    "wall_seconds": time.monotonic() - all_started,
                }
                print(json.dumps({"certificate": payload}, sort_keys=True), flush=True)
                return
    if args.rank_target is not None:
        print(json.dumps({"incomplete_rank": len(basis), "target": args.rank_target,
            "samples": args.samples, "wall_seconds": time.monotonic() - all_started}), flush=True)


if __name__ == "__main__":
    main()
