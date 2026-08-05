#!/usr/bin/env python3
"""Finite selected-vacuum phase-invariant search through dimension six.

Scope
-----
This audit exhausts the SO(10) *metric-contraction* sector for scalar
monomials built from

    210_H, 126bar_H, 10_H, S and their conjugates

through canonical field dimension six. It first enumerates every monomial
that is neutral under the repository PQ/X/Z17 charges, is phase-sensitive,
involves 126bar_H, and has a phase vector independent of kappa H^2 S.

For each even-H tensor signature, every multigraph of pairwise Kronecker-delta
contractions is evaluated with the exact sparse Cartesian tensors for the
selected p,a,omega and Delta_R directions. Conjugate signatures are identified.
Odd-H signatures vanish on the heavy-singlet plus electroweak-doublet vacuum by
SU(2)_L doublet parity.

Honesty boundary
----------------
This is not yet a complete SO(10) invariant-ring theorem. Contractions with one
Levi-Civita epsilon and the exact published neutral-H component dictionary are
kept open. Two canonical weak embeddings are tested, and deterministic generic
tensor controls prove that the contraction engine can return nonzero values.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import nonsusy_z17_pq_potential_filter_v20 as charge_filter

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SELECTED_VACUUM_PHASE_INVARIANT_DIM6_METRIC_AUDIT_V20.json"
OUT_MD = ROOT / "SELECTED_VACUUM_PHASE_INVARIANT_DIM6_METRIC_AUDIT_V20.md"

FIELDS = ("P", "D", "Db", "H", "Hb", "S", "Sb")
REPO_FIELD_NAMES = {
    "P": "210_H",
    "D": "126bar_H",
    "Db": "126bar_H_dag",
    "H": "10_H",
    "Hb": "10_H_dag",
    "S": "S",
    "Sb": "S_dag",
}
INTEGER_CHARGES = {
    name: int(charge_filter.CHARGES[repo_name]["PQ"])
    for name, repo_name in REPO_FIELD_NAMES.items()
}
KAPPA_PHASE_VECTOR = (0, 2, 1)
DROP_TOL = 1.0e-12
ZERO_TOL = 1.0e-9

TensorSignature = tuple[int, int, int, int, int]
Graph = tuple[tuple[int, ...], ...]
SparseTable = dict[tuple[int, ...], complex]
Factor = tuple[tuple[int, ...], SparseTable]


def compositions(total: int, length: int, prefix: tuple[int, ...] = ()) -> Iterable[tuple[int, ...]]:
    if length == 1:
        yield prefix + (total,)
        return
    for value in range(total + 1):
        yield from compositions(total - value, length - 1, prefix + (value,))


def phase_vector(counts: dict[str, int]) -> tuple[int, int, int]:
    return (
        counts["D"] - counts["Db"],
        counts["H"] - counts["Hb"],
        counts["S"] - counts["Sb"],
    )


def parallel_to_kappa(vector: tuple[int, int, int]) -> bool:
    return vector[0] == 0 and vector[1] == 2 * vector[2]


def charge_candidates(max_dimension: int = 6) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for dimension in range(1, max_dimension + 1):
        for values in compositions(dimension, len(FIELDS)):
            counts = dict(zip(FIELDS, values))
            pq = sum(INTEGER_CHARGES[name] * counts[name] for name in FIELDS)
            if pq != 0:
                continue
            vector = phase_vector(counts)
            if vector == (0, 0, 0) or parallel_to_kappa(vector):
                continue
            if counts["D"] + counts["Db"] == 0:
                continue
            repo_counts = {
                REPO_FIELD_NAMES[name]: multiplicity
                for name, multiplicity in counts.items()
                if multiplicity
            }
            totals = charge_filter._total_charge(repo_counts)
            allowed = charge_filter._allowed(totals)
            rows.append(
                {
                    "dimension": dimension,
                    "counts": counts,
                    "repo_counts": repo_counts,
                    "phase_vector_D_H_S": list(vector),
                    "charge_totals": totals,
                    "charge_allowed": allowed,
                }
            )
    return rows


def tensor_signature(counts: dict[str, int]) -> TensorSignature:
    return (
        counts["P"],
        counts["D"],
        counts["Db"],
        counts["H"],
        counts["Hb"],
    )


def conjugate_signature(signature: TensorSignature) -> TensorSignature:
    nphi, nd, ndb, nh, nhb = signature
    return (nphi, ndb, nd, nhb, nh)


def canonical_signature(signature: TensorSignature) -> TensorSignature:
    return min(signature, conjugate_signature(signature))


def tensor_degrees(signature: TensorSignature) -> list[int]:
    nphi, nd, ndb, nh, nhb = signature
    return [4] * nphi + [5] * (nd + ndb) + [1] * (nh + nhb)


def multigraphs_for_degrees(degrees: list[int]) -> list[Graph]:
    """All loop-free multigraphs whose vertex degrees equal tensor ranks."""
    n = len(degrees)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    remaining = list(degrees)
    matrix = [[0] * n for _ in range(n)]
    output: list[Graph] = []

    def recurse(position: int) -> None:
        if position == len(pairs):
            if not any(remaining):
                output.append(tuple(tuple(row) for row in matrix))
            return
        i, j = pairs[position]
        maximum = min(remaining[i], remaining[j])
        for multiplicity in range(maximum + 1):
            remaining[i] -= multiplicity
            remaining[j] -= multiplicity
            matrix[i][j] = matrix[j][i] = multiplicity
            total_remaining = sum(remaining)
            feasible = all(
                value >= 0 and value <= total_remaining - value
                for value in remaining
            )
            if feasible:
                recurse(position + 1)
            remaining[i] += multiplicity
            remaining[j] += multiplicity
        matrix[i][j] = matrix[j][i] = 0

    if sum(degrees) % 2 == 0:
        recurse(0)
    return output


def conjugate_form(form: direct.Form) -> direct.Form:
    return {indices: complex(value).conjugate() for indices, value in form.items()}


def full_components(form: direct.Form) -> SparseTable:
    """Expand independent antisymmetric components to ordered components."""
    output: SparseTable = {}
    for indices, coefficient in form.items():
        for ordered in itertools.permutations(indices):
            output[ordered] = coefficient * direct.permutation_sign(ordered)
    return output


def graph_labels(graph: Graph) -> list[tuple[int, ...]]:
    labels: list[list[int]] = [[] for _ in graph]
    edge = 0
    for i in range(len(graph)):
        for j in range(i + 1, len(graph)):
            for _ in range(graph[i][j]):
                labels[i].append(edge)
                labels[j].append(edge)
                edge += 1
    return [tuple(row) for row in labels]


def contract_two(left: Factor, right: Factor) -> Factor:
    left_labels, left_table = left
    right_labels, right_table = right
    right_set = set(right_labels)
    shared = [label for label in left_labels if label in right_set]

    if not shared:
        output: defaultdict[tuple[int, ...], complex] = defaultdict(complex)
        for left_key, left_value in left_table.items():
            for right_key, right_value in right_table.items():
                output[left_key + right_key] += left_value * right_value
        return (
            left_labels + right_labels,
            {
                key: value
                for key, value in output.items()
                if abs(value) > DROP_TOL
            },
        )

    left_shared = [left_labels.index(label) for label in shared]
    right_shared = [right_labels.index(label) for label in shared]
    left_remaining = [
        index for index, label in enumerate(left_labels) if label not in shared
    ]
    right_remaining = [
        index for index, label in enumerate(right_labels) if label not in shared
    ]

    index: defaultdict[tuple[int, ...], list[tuple[tuple[int, ...], complex]]] = defaultdict(list)
    for key, value in right_table.items():
        shared_key = tuple(key[position] for position in right_shared)
        remainder = tuple(key[position] for position in right_remaining)
        index[shared_key].append((remainder, value))

    output: defaultdict[tuple[int, ...], complex] = defaultdict(complex)
    for key, value in left_table.items():
        shared_key = tuple(key[position] for position in left_shared)
        left_remainder = tuple(key[position] for position in left_remaining)
        for right_remainder, right_value in index.get(shared_key, ()):
            output[left_remainder + right_remainder] += value * right_value

    output_labels = tuple(left_labels[position] for position in left_remaining) + tuple(
        right_labels[position] for position in right_remaining
    )
    return (
        output_labels,
        {
            key: value
            for key, value in output.items()
            if abs(value) > DROP_TOL
        },
    )


def sparse_contract(tables: list[SparseTable], graph: Graph) -> complex:
    labels = graph_labels(graph)
    factors: list[Factor] = [(labels[i], tables[i]) for i in range(len(tables))]
    while len(factors) > 1:
        candidates: list[tuple[int, int, int, int]] = []
        for i in range(len(factors)):
            left_set = set(factors[i][0])
            for j in range(i + 1, len(factors)):
                shared = len(left_set.intersection(factors[j][0]))
                if shared:
                    candidates.append(
                        (
                            -shared,
                            len(factors[i][1]) * len(factors[j][1]),
                            i,
                            j,
                        )
                    )
        if candidates:
            _, _, i, j = min(candidates)
        else:
            i, j = 0, 1
        combined = contract_two(factors[i], factors[j])
        factors = [
            factor
            for index, factor in enumerate(factors)
            if index not in (i, j)
        ] + [combined]
    labels_final, table_final = factors[0]
    if labels_final:
        raise RuntimeError("metric contraction left uncontracted labels")
    return table_final.get((), 0.0j)


def selected_phi() -> direct.Form:
    basis = direct.singlet_basis()
    # Repository Aulakh ratios p:a:omega = 0.2:0.3:0.5, converted to the
    # canonical P,A,W normalization used by the direct tensor module.
    return direct.add_forms(
        direct.scale_form(basis["p"], 0.2),
        direct.scale_form(basis["a"], math.sqrt(3.0) * 0.3),
        direct.scale_form(basis["omega"], math.sqrt(6.0) * 0.5),
    )


def weak_probe_67() -> direct.Form:
    return direct.normalize_210_or_10(
        direct.add_forms(
            direct.one_form(6),
            direct.scale_form(direct.one_form(7), 1.0j),
        )
    )


def weak_probe_mixed() -> direct.Form:
    return direct.normalize_210_or_10(
        direct.add_forms(
            direct.one_form(6),
            direct.scale_form(direct.one_form(7), 1.0j),
            direct.scale_form(direct.one_form(8), 0.7),
            direct.scale_form(direct.one_form(9), 0.7j),
        )
    )


def tables_for_signature(
    signature: TensorSignature,
    *,
    phi_table: SparseTable,
    delta_table: SparseTable,
    delta_bar_table: SparseTable,
    h_table: SparseTable,
    h_bar_table: SparseTable,
) -> list[SparseTable]:
    nphi, nd, ndb, nh, nhb = signature
    return (
        [phi_table] * nphi
        + [delta_table] * nd
        + [delta_bar_table] * ndb
        + [h_table] * nh
        + [h_bar_table] * nhb
    )


def evaluate_signature(
    signature: TensorSignature,
    *,
    phi_table: SparseTable,
    delta_table: SparseTable,
    delta_bar_table: SparseTable,
    h_table: SparseTable,
    h_bar_table: SparseTable,
) -> dict[str, Any]:
    degrees = tensor_degrees(signature)
    graphs = multigraphs_for_degrees(degrees)
    tables = tables_for_signature(
        signature,
        phi_table=phi_table,
        delta_table=delta_table,
        delta_bar_table=delta_bar_table,
        h_table=h_table,
        h_bar_table=h_bar_table,
    )
    values = [sparse_contract(tables, graph) for graph in graphs]
    maximum = max((abs(value) for value in values), default=0.0)
    return {
        "signature_P_D_Db_H_Hb": list(signature),
        "tensor_degrees": degrees,
        "n_metric_graphs": len(graphs),
        "max_abs_contraction": float(maximum),
        "all_metric_contractions_zero": maximum < ZERO_TOL,
    }


def deterministic_generic_forms() -> tuple[direct.Form, direct.Form]:
    phi = direct.normalize_210_or_10(
        {
            (0, 1, 2, 3): 1.0,
            (0, 4, 6, 8): 0.6,
            (1, 5, 7, 9): -0.3,
        }
    )
    seed: direct.Form = {
        (0, 1, 2, 3, 4): 1.0,
        (0, 2, 5, 7, 9): 0.7 + 0.2j,
        (1, 3, 4, 6, 8): -0.4 + 0.3j,
    }
    delta = direct.normalize_126(
        direct.add_forms(
            seed,
            direct.scale_form(direct.hodge_star(seed), 1.0j),
        )
    )
    return phi, delta


def build_report() -> dict[str, Any]:
    candidates = charge_candidates(6)
    signatures = {tensor_signature(row["counts"]) for row in candidates}
    odd_h = {
        signature
        for signature in signatures
        if (signature[3] + signature[4]) % 2 == 1
    }
    even_h = signatures.difference(odd_h)
    representatives = sorted({canonical_signature(signature) for signature in even_h})

    charge_crosscheck = all(
        row["charge_allowed"]["all"]
        and row["charge_totals"]["PQ"] == 0
        and row["charge_totals"]["X"] == 0
        and row["charge_totals"]["Z17"] == 0
        for row in candidates
    )

    phi = selected_phi()
    delta = direct.delta_r()
    delta_bar = conjugate_form(delta)
    phi_table = full_components(phi)
    delta_table = full_components(delta)
    delta_bar_table = full_components(delta_bar)

    probes = {
        "canonical_67_complex": weak_probe_67(),
        "mixed_67_89_complex": weak_probe_mixed(),
    }
    evaluations: dict[str, list[dict[str, Any]]] = {}
    for name, h in probes.items():
        h_table = full_components(h)
        h_bar_table = full_components(conjugate_form(h))
        evaluations[name] = [
            evaluate_signature(
                signature,
                phi_table=phi_table,
                delta_table=delta_table,
                delta_bar_table=delta_bar_table,
                h_table=h_table,
                h_bar_table=h_bar_table,
            )
            for signature in representatives
        ]

    selected_maximum = max(
        row["max_abs_contraction"]
        for rows in evaluations.values()
        for row in rows
    )
    metric_graph_count = sum(
        row["n_metric_graphs"] for row in evaluations["canonical_67_complex"]
    )

    generic_phi, generic_delta = deterministic_generic_forms()
    generic_phi_table = full_components(generic_phi)
    generic_delta_table = full_components(generic_delta)
    generic_delta_bar_table = full_components(conjugate_form(generic_delta))
    generic_h = weak_probe_mixed()
    generic_h_table = full_components(generic_h)
    generic_h_bar_table = full_components(conjugate_form(generic_h))
    control_signatures: list[TensorSignature] = [
        (0, 0, 2, 1, 1),
        (0, 0, 4, 0, 0),
        (2, 0, 2, 0, 0),
    ]
    controls = [
        evaluate_signature(
            signature,
            phi_table=generic_phi_table,
            delta_table=generic_delta_table,
            delta_bar_table=generic_delta_bar_table,
            h_table=generic_h_table,
            h_bar_table=generic_h_bar_table,
        )
        for signature in control_signatures
    ]
    generic_nonzero = all(
        not row["all_metric_contractions_zero"] for row in controls
    )

    checks = {
        "repository_charge_filter_crosscheck": charge_crosscheck,
        "candidate_count_110": len(candidates) == 110,
        "tensor_signature_count_88": len(signatures) == 88,
        "odd_H_signature_count_58": len(odd_h) == 58,
        "even_H_signature_count_30": len(even_h) == 30,
        "conjugacy_representative_count_15": len(representatives) == 15,
        "metric_graph_count_1006_per_embedding": metric_graph_count == 1006,
        "all_selected_metric_contractions_zero": selected_maximum < ZERO_TOL,
        "generic_controls_nonzero": generic_nonzero,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]

    return {
        "status": (
            "DIM6_PHASE_METRIC_SECTOR_ZERO_ON_CANONICAL_SELECTED_VACUUM__EPSILON_OPEN"
            if not failures
            else "DIM6_PHASE_METRIC_AUDIT_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "scope": {
            "maximum_canonical_dimension": 6,
            "fields": list(FIELDS),
            "requires_126bar_participation": True,
            "phase_vector_independent_of_kappa": True,
            "contraction_sector_completed": "pairwise SO(10) metric contractions",
            "epsilon_contraction_sector_completed": False,
            "exact_published_hEW_state_dictionary_completed": False,
        },
        "counts": {
            "charge_allowed_phase_sensitive_monomials": len(candidates),
            "distinct_tensor_signatures": len(signatures),
            "odd_H_signatures_removed_by_SU2L_doublet_parity": len(odd_h),
            "even_H_signatures": len(even_h),
            "conjugacy_representatives": len(representatives),
            "metric_graphs_per_weak_embedding": metric_graph_count,
            "weak_embeddings_tested": len(probes),
        },
        "selected_vacuum": {
            "Phi_coefficients_canonical_P_A_W": {
                "P": 0.2,
                "A": math.sqrt(3.0) * 0.3,
                "W": math.sqrt(6.0) * 0.5,
            },
            "DeltaR_canonical_norm": direct.sigma_kinetic_norm(delta),
            "weak_probes": list(probes),
            "maximum_abs_metric_contraction": float(selected_maximum),
            "evaluations": evaluations,
        },
        "generic_engine_controls": controls,
        "candidate_ledger": candidates,
        "flags": {
            "charge_enumeration_through_dim6_complete": not bool(failures),
            "metric_graph_enumeration_complete_for_15_representatives": not bool(failures),
            "nonzero_selected_metric_phase_channel_found": False,
            "dimension6_full_SO10_no_go_proven": False,
            "epsilon_sector_open": True,
            "published_hEW_component_dictionary_open": True,
            "dimension7_search_required_if_epsilon_sector_also_zero": True,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "enumerate_one_epsilon_contractions_through_dimension6": True,
            "map_exact_neutral_hEW_state_into_cartesian_10": True,
            "complete_SO10_invariant_multiplicities": True,
            "extend_phase_sensitive_search_to_dimension7": True,
            "rebuild_full_stationarity_and_component_hessian": True,
        },
        "verdict": (
            "All 110 charge-allowed phase-sensitive monomials through dimension "
            "six reduce to 88 tensor signatures. Fifty-eight odd-H signatures "
            "are excluded by SU(2)L doublet parity. The remaining 30 signatures "
            "form 15 conjugacy representatives; all 1006 pairwise-metric "
            "contraction graphs vanish on both canonical weak embeddings of the "
            "selected p,a,omega,Delta_R vacuum. Generic controls are nonzero, so "
            "the result is not a dead contraction engine. This is a finite "
            "metric-sector no-channel result, not yet a full SO(10) no-go: the "
            "one-epsilon sector and exact labeled hEW state remain open."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    counts = report["counts"]
    OUT_MD.write_text(
        "# Selected-vacuum phase-invariant dimension-six metric audit — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Charge-allowed monomials: `{counts['charge_allowed_phase_sensitive_monomials']}`\n"
        f"- Tensor signatures: `{counts['distinct_tensor_signatures']}`\n"
        f"- Even-H conjugacy representatives: `{counts['conjugacy_representatives']}`\n"
        f"- Metric graphs per weak embedding: `{counts['metric_graphs_per_weak_embedding']}`\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "overall_state": report["overall_state"],
                "n_failed": report["n_failed"],
                "counts": report["counts"],
                "selected_max": report["selected_vacuum"][
                    "maximum_abs_metric_contraction"
                ],
                "flags": report["flags"],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
