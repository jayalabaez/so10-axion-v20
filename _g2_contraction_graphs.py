#!/usr/bin/env python3
from __future__ import annotations

from functools import lru_cache
from itertools import permutations, product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RANKS = (4, 1, 1, 5, 5)


@lru_cache(maxsize=None)
def labelled_multigraphs(degrees: tuple[int, ...]):
    n = len(degrees)
    pairs = tuple((i, j) for i in range(n) for j in range(i + 1, n))
    remaining = list(degrees)
    edges = [0] * len(pairs)

    output = []
    last_incident = tuple(max(k for k, pair in enumerate(pairs) if i in pair) for i in range(n))

    def rec(position: int):
        if position == len(pairs):
            if all(value == 0 for value in remaining):
                output.append(tuple(edges))
            return
        i, j = pairs[position]
        # Once this is the last edge incident to i, its multiplicity is forced.
        values = (remaining[i],) if last_incident[i] == position else range(min(remaining[i], remaining[j]) + 1)
        for value in values:
            if value > remaining[j]:
                continue
            remaining[i] -= value
            remaining[j] -= value
            edges[position] = value
            # Every residual vertex degree must fit in the sum of the others.
            feasible = all(remaining[k] <= sum(remaining) - remaining[k] for k in range(n))
            if feasible:
                rec(position + 1)
            remaining[i] += value
            remaining[j] += value
        edges[position] = 0

    rec(0)
    return tuple(output)


@lru_cache(maxsize=None)
def color_permutations(species: tuple[int, ...]):
    n = len(species)
    groups = []
    for color in sorted(set(species)):
        groups.append(tuple(i for i, value in enumerate(species) if value == color))
    result = []
    for choices in product(*(permutations(group) for group in groups)):
        mapping = list(range(n))
        for old_group, new_group in zip(groups, choices):
            for old, new in zip(old_group, new_group):
                mapping[old] = new
        result.append(tuple(mapping))
    return tuple(result)


def canonical_graph(species: tuple[int, ...], epsilon_legs: tuple[int, ...], edges: tuple[int, ...]):
    n = len(species)
    pairs = tuple((i, j) for i in range(n) for j in range(i + 1, n))
    edge_map = {pair: edges[index] for index, pair in enumerate(pairs)}
    candidates = []
    for mapping in color_permutations(species):
        eps = [0] * n
        adjacency = [[0] * n for _ in range(n)]
        for old, new in enumerate(mapping):
            eps[new] = epsilon_legs[old]
        for (i, j), value in edge_map.items():
            a, b = sorted((mapping[i], mapping[j]))
            adjacency[a][b] = adjacency[b][a] = value
        flat = tuple(adjacency[i][j] for i in range(n) for j in range(i + 1, n))
        candidates.append((tuple(eps), flat))
    return min(candidates)


def sector_candidates(counts: tuple[int, ...]):
    species = tuple(index for index, count in enumerate(counts) for _ in range(count))
    degrees = tuple(RANKS[index] for index in species)
    if not species:
        return (((), ()),), ()
    metric = {
        canonical_graph(species, (0,) * len(species), edges)
        for edges in labelled_multigraphs(degrees)
    }
    epsilon = set()
    ranges = tuple(range(rank + 1) for rank in degrees)
    for legs in product(*ranges):
        if sum(legs) != 10:
            continue
        # One representative of each identical-field orbit is sufficient;
        # the graph enumeration below still covers every compatible adjacency.
        if any(
            tuple(legs[i] for i, value in enumerate(species) if value == color)
            != tuple(sorted(legs[i] for i, value in enumerate(species) if value == color))
            for color in set(species)
        ):
            continue
        residual = tuple(rank - used for rank, used in zip(degrees, legs))
        if sum(residual) % 2:
            continue
        for edges in labelled_multigraphs(residual):
            epsilon.add(canonical_graph(species, legs, edges))
    return tuple(sorted(metric)), tuple(sorted(epsilon))


def main():
    rows = json.loads((ROOT / "CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json").read_text())["rows"]
    unique = {}
    for row in rows:
        key = tuple(row["count_tuple"][:5])
        unique.setdefault(key, row)
    totals = [0, 0]
    deficient = []
    for key, row in sorted(unique.items(), key=lambda item: (sum(item[0]), item[0])):
        metric, epsilon = sector_candidates(key)
        target = row["constructive_channel_count"]
        totals[0] += len(metric)
        totals[1] += len(epsilon)
        record = {
            "counts": key,
            "target": target,
            "metric": len(metric),
            "one_epsilon": len(epsilon),
            "total_candidates": len(metric) + len(epsilon),
        }
        if len(metric) < target:
            deficient.append(record)
        print(json.dumps(record, sort_keys=True), flush=True)
    print(json.dumps({"totals": totals, "metric_deficient_sectors": deficient}, sort_keys=True))


if __name__ == "__main__":
    main()
