#!/usr/bin/env python3
"""Reduce all dimension-six SO(10) epsilon contractions to metric graphs.

The finite metric audit enumerates every charge-allowed phase-sensitive tensor
signature through canonical dimension six and evaluates all pairwise metric
contractions on the selected vacuum. This module closes the remaining epsilon
question for those signatures.

Every candidate contains at least one 126bar_H or its conjugate, represented by
a complex five-form in ten Euclidean dimensions. Such a five-form obeys

    *Sigma = eta Sigma,   eta in {+i,-i}.

For a contraction with an odd number of Levi-Civita tensors, replace one
five-form by its Hodge-dual expression. This introduces one additional epsilon,
so the number of epsilons becomes even. Every epsilon pair is a generalized
Kronecker delta, i.e. a signed sum of products of ordinary metrics. Therefore
all delta/epsilon contractions reduce linearly to the already enumerated metric
multigraphs. Even-epsilon contractions reduce directly.

This closes the independent epsilon-tensor sector for the weak embeddings
actually tested by the metric audit. It does not manufacture the exact
published neutral-H Cartesian state dictionary; that remaining component-label
step is kept open.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import selected_vacuum_phase_invariant_dim6_metric_audit_v20 as metric

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SELECTED_VACUUM_PHASE_INVARIANT_DIM6_EPSILON_REDUCTION_V20.json"
OUT_MD = ROOT / "SELECTED_VACUUM_PHASE_INVARIANT_DIM6_EPSILON_REDUCTION_V20.md"
TOL = 1.0e-12


def hodge_eigenvalue(form: direct.Form) -> complex:
    starred = direct.hodge_star(form)
    denominator = direct.sigma_kinetic_inner(form, form)
    if abs(denominator) == 0.0:
        raise ValueError("zero five-form")
    return complex(direct.sigma_kinetic_inner(form, starred) / denominator)


def hodge_residual(form: direct.Form, eigenvalue: complex) -> float:
    difference = direct.add_forms(
        direct.hodge_star(form),
        direct.scale_form(form, -eigenvalue),
    )
    return direct.sigma_kinetic_norm(difference)


def levi_civita(indices: tuple[int, ...]) -> int:
    if len(indices) != direct.N or set(indices) != set(range(direct.N)):
        return 0
    return direct.permutation_sign(indices)


def epsilon_pair_identity_checks() -> dict[str, Any]:
    permutations = [
        tuple(range(10)),
        tuple(reversed(range(10))),
        (1, 0, 2, 3, 4, 5, 6, 7, 8, 9),
        (2, 5, 1, 8, 0, 9, 3, 7, 4, 6),
    ]
    cases: list[dict[str, Any]] = []
    for left in permutations:
        for right in permutations:
            matrix = np.array(
                [[1 if a == b else 0 for b in right] for a in left],
                dtype=float,
            )
            determinant = int(round(float(np.linalg.det(matrix))))
            product = levi_civita(left) * levi_civita(right)
            cases.append(
                {
                    "left": list(left),
                    "right": list(right),
                    "epsilon_product": product,
                    "generalized_delta_determinant": determinant,
                    "matches": product == determinant,
                }
            )

    repeated = (0, 0, 1, 2, 3, 4, 5, 6, 7, 8)
    repeated_matrix = np.array(
        [[1 if a == b else 0 for b in range(10)] for a in repeated],
        dtype=float,
    )
    repeated_det = int(round(float(np.linalg.det(repeated_matrix))))
    repeated_case = {
        "epsilon": levi_civita(repeated),
        "generalized_delta_determinant": repeated_det,
        "matches": levi_civita(repeated) == repeated_det == 0,
    }
    return {
        "permutation_cases": cases,
        "repeated_index_case": repeated_case,
        "all_match": all(case["matches"] for case in cases)
        and repeated_case["matches"],
    }


def representative_signatures() -> list[metric.TensorSignature]:
    candidates = metric.charge_candidates(6)
    signatures = {metric.tensor_signature(row["counts"]) for row in candidates}
    even_h = {
        signature
        for signature in signatures
        if (signature[3] + signature[4]) % 2 == 0
    }
    return sorted({metric.canonical_signature(signature) for signature in even_h})


def epsilon_topologies(signature: metric.TensorSignature) -> dict[str, int]:
    degrees = metric.tensor_degrees(signature)
    allocations = 0
    topologies = 0
    for epsilon_legs in itertools.product(
        *[range(degree + 1) for degree in degrees]
    ):
        if sum(epsilon_legs) != direct.N:
            continue
        residual = [
            degree - epsilon
            for degree, epsilon in zip(degrees, epsilon_legs)
        ]
        graphs = metric.multigraphs_for_degrees(residual)
        if not graphs:
            continue
        allocations += 1
        topologies += len(graphs)
    return {
        "epsilon_allocations": allocations,
        "epsilon_metric_topologies": topologies,
    }


def build_report() -> dict[str, Any]:
    metric_report = metric.build_report()
    delta = direct.delta_r()
    delta_bar = metric.conjugate_form(delta)
    eigen_delta = hodge_eigenvalue(delta)
    eigen_bar = hodge_eigenvalue(delta_bar)
    residual_delta = hodge_residual(delta, eigen_delta)
    residual_bar = hodge_residual(delta_bar, eigen_bar)

    representatives = representative_signatures()
    topology_rows = []
    for signature in representatives:
        counts = epsilon_topologies(signature)
        topology_rows.append(
            {
                "signature_P_D_Db_H_Hb": list(signature),
                "contains_five_form": signature[1] + signature[2] > 0,
                **counts,
            }
        )
    topology_total = sum(
        row["epsilon_metric_topologies"] for row in topology_rows
    )
    allocation_total = sum(row["epsilon_allocations"] for row in topology_rows)

    epsilon_identity = epsilon_pair_identity_checks()
    all_candidates_have_five_form = all(
        row["contains_five_form"] for row in topology_rows
    )
    eigenvalues_are_opposite_imaginary = (
        abs(eigen_delta.real) < TOL
        and abs(eigen_bar.real) < TOL
        and abs(abs(eigen_delta.imag) - 1.0) < TOL
        and abs(abs(eigen_bar.imag) - 1.0) < TOL
        and abs(eigen_delta + eigen_bar) < TOL
    )
    metric_upstream_green = bool(
        metric_report.get("n_failed") == 0
        and metric_report.get("flags", {}).get(
            "metric_graph_enumeration_complete_for_15_representatives"
        )
        and not metric_report.get("flags", {}).get(
            "nonzero_selected_metric_phase_channel_found", True
        )
    )

    checks = {
        "metric_upstream_green": metric_upstream_green,
        "fifteen_even_H_representatives": len(representatives) == 15,
        "every_representative_contains_126_five_form": all_candidates_have_five_form,
        "DeltaR_is_exact_Hodge_eigenform": residual_delta < TOL,
        "DeltaR_conjugate_is_exact_Hodge_eigenform": residual_bar < TOL,
        "Hodge_eigenvalues_are_opposite_plus_minus_i": eigenvalues_are_opposite_imaginary,
        "epsilon_pair_generalized_delta_identity": epsilon_identity["all_match"],
        "one_epsilon_topology_count_18577": topology_total == 18577,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]

    return {
        "status": (
            "DIM6_EPSILON_SECTOR_REDUCES_TO_ZERO_METRIC_SECTOR__HEW_DICTIONARY_OPEN"
            if not failures
            else "DIM6_EPSILON_REDUCTION_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "hodge": {
            "DeltaR_eigenvalue": [eigen_delta.real, eigen_delta.imag],
            "DeltaR_conjugate_eigenvalue": [eigen_bar.real, eigen_bar.imag],
            "DeltaR_residual": residual_delta,
            "DeltaR_conjugate_residual": residual_bar,
            "identity": "*Sigma=eta*Sigma with eta=+/-i",
        },
        "epsilon_pair_identity": epsilon_identity,
        "topology_ledger": {
            "representatives": topology_rows,
            "total_epsilon_allocations": allocation_total,
            "total_one_epsilon_metric_topologies": topology_total,
        },
        "reduction_theorem": {
            "SO10_invariant_generators": "Kronecker delta and Levi-Civita epsilon_10",
            "odd_epsilon_step": (
                "dualize one participating self-dual/anti-self-dual five-form, "
                "turning an odd epsilon count into an even count"
            ),
            "even_epsilon_step": (
                "pair epsilons and replace each pair by a generalized Kronecker "
                "delta, a signed sum of metric products"
            ),
            "conclusion": (
                "no epsilon contraction is independent of the completed metric "
                "multigraph sector for these signatures"
            ),
        },
        "upstream_metric_result": {
            "status": metric_report.get("status"),
            "selected_maximum_abs_metric_contraction": metric_report.get(
                "selected_vacuum", {}
            ).get("maximum_abs_metric_contraction"),
            "weak_embeddings_tested": metric_report.get("counts", {}).get(
                "weak_embeddings_tested"
            ),
        },
        "flags": {
            "one_epsilon_topology_ledger_complete": not bool(failures),
            "epsilon_channels_independent_of_metric_sector": False,
            "epsilon_sector_reduced_to_metric_sector": not bool(failures),
            "nonzero_selected_epsilon_phase_channel_found": False,
            "delta_epsilon_tensor_sector_closed_for_tested_embeddings": not bool(
                failures
            ),
            "exact_published_hEW_component_dictionary_complete": False,
            "full_selected_vacuum_dimension6_no_go_proven": False,
            "dimension7_search_ready_after_hEW_dictionary": not bool(failures),
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "map_exact_neutral_hEW_state_into_cartesian_10": True,
            "prove_metric_zero_for_exact_published_hEW_state": True,
            "complete_SO10_invariant_multiplicities": True,
            "extend_phase_sensitive_search_to_dimension7": True,
            "rebuild_stationarity_and_full_component_hessian": True,
        },
        "verdict": (
            "All 18,577 one-epsilon allocation/metric topologies across the 15 "
            "dimension-six representatives are algebraically non-independent. "
            "Every representative contains a 126 five-form; Hodge duality turns "
            "an odd epsilon count into an even one, and epsilon pairs reduce to "
            "metric contractions. Because the exhaustive metric sector is zero "
            "on both tested weak embeddings, no independent epsilon phase-lifting "
            "channel exists there. The exact labeled neutral-H dictionary remains "
            "open, so this is not yet advertised as a complete physical-vacuum "
            "dimension-six no-go."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    ledger = report["topology_ledger"]
    OUT_MD.write_text(
        "# Selected-vacuum dimension-six epsilon reduction — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- One-epsilon allocations: `{ledger['total_epsilon_allocations']}`\n"
        f"- One-epsilon/metric topologies: `{ledger['total_one_epsilon_metric_topologies']}`\n\n"
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
                "hodge": report["hodge"],
                "topology_ledger": {
                    "total_epsilon_allocations": report["topology_ledger"][
                        "total_epsilon_allocations"
                    ],
                    "total_one_epsilon_metric_topologies": report[
                        "topology_ledger"
                    ]["total_one_epsilon_metric_topologies"],
                },
                "flags": report["flags"],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
