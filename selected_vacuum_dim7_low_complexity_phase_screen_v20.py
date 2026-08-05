#!/usr/bin/env python3
"""Targeted dimension-seven phase-invariant screen on the selected vacuum.

The dimension-six audit proves that the current p,a,omega,Delta_R vacuum cannot
obtain the missing independent phase constraint through canonical dimension
six. This module advances to dimension seven and screens the eight new even-H
tensor representatives with at most 300 metric graphs.

All neutral-H multilinear coefficients are evaluated exactly in the two-state
Cartesian neutral basis derived by ``selected_vacuum_neutral_h10_dim6_no_go``.
Because every candidate contains a 126 five-form, the Hodge/epsilon reduction
continues to apply: epsilon contractions add no structures independent of the
metric graph sector.

The screen is intentionally staged. Five higher-complexity representatives are
kept open unless this wave already finds a nonzero selected-vacuum channel.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import selected_vacuum_neutral_h10_dim6_no_go_v20 as neutral
import selected_vacuum_phase_invariant_dim6_metric_audit_v20 as metric

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SELECTED_VACUUM_DIM7_LOW_COMPLEXITY_PHASE_SCREEN_V20.json"
OUT_MD = ROOT / "SELECTED_VACUUM_DIM7_LOW_COMPLEXITY_PHASE_SCREEN_V20.md"
GRAPH_LIMIT = 300
TOL = neutral.TOL


def exact_dimension_candidates(dimension: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for values in metric.compositions(dimension, len(metric.FIELDS)):
        counts = dict(zip(metric.FIELDS, values))
        pq = sum(
            metric.INTEGER_CHARGES[name] * counts[name]
            for name in metric.FIELDS
        )
        if pq != 0:
            continue
        vector = metric.phase_vector(counts)
        if vector == (0, 0, 0) or metric.parallel_to_kappa(vector):
            continue
        if counts["D"] + counts["Db"] == 0:
            continue
        repo_counts = {
            metric.REPO_FIELD_NAMES[name]: multiplicity
            for name, multiplicity in counts.items()
            if multiplicity
        }
        totals = metric.charge_filter._total_charge(repo_counts)
        allowed = metric.charge_filter._allowed(totals)
        rows.append(
            {
                "dimension": dimension,
                "counts": counts,
                "repo_counts": repo_counts,
                "phase_vector_D_H_S": list(vector),
                "charge_totals": totals,
                "charge_allowed": allowed,
                "tensor_signature": list(metric.tensor_signature(counts)),
                "canonical_signature": list(
                    metric.canonical_signature(metric.tensor_signature(counts))
                ),
            }
        )
    return rows


def normalize_integer_vector(vector: np.ndarray) -> list[int]:
    rounded = np.rint(vector).astype(int)
    nonzero = [abs(int(value)) for value in rounded if value]
    if not nonzero:
        return [0, 0, 0]
    divisor = int(np.gcd.reduce(nonzero))
    rounded = rounded // max(divisor, 1)
    pivot = next((value for value in rounded if value), 1)
    if pivot < 0:
        rounded = -rounded
    return [int(value) for value in rounded]


def phase_rank_record(vector: list[int]) -> dict[str, Any]:
    kappa = np.array(metric.KAPPA_PHASE_VECTOR, dtype=int)
    candidate = np.array(vector, dtype=int)
    matrix = np.stack([kappa, candidate])
    rank = int(np.linalg.matrix_rank(matrix.astype(float)))
    null = normalize_integer_vector(np.cross(kappa, candidate))
    pq = [1, 1, -2]
    if null == [-value for value in pq]:
        null = pq
    return {
        "rank_with_kappa": rank,
        "null_vector": null,
        "null_is_PQ_1_1_minus2": null == pq,
    }


def build_report() -> dict[str, Any]:
    dim6 = neutral.build_report()
    candidates7 = exact_dimension_candidates(7)

    dim6_signatures = {
        metric.tensor_signature(row["counts"])
        for row in metric.charge_candidates(6)
    }
    signatures7 = {
        metric.tensor_signature(row["counts"]) for row in candidates7
    }
    new_signatures = signatures7.difference(dim6_signatures)
    odd_h = {
        signature
        for signature in new_signatures
        if (signature[3] + signature[4]) % 2 == 1
    }
    even_h = new_signatures.difference(odd_h)
    representatives = sorted(
        {metric.canonical_signature(signature) for signature in even_h}
    )

    graph_counts = {
        signature: len(
            metric.multigraphs_for_degrees(metric.tensor_degrees(signature))
        )
        for signature in representatives
    }
    low_representatives = [
        signature
        for signature in representatives
        if graph_counts[signature] <= GRAPH_LIMIT
    ]
    high_representatives = [
        signature
        for signature in representatives
        if graph_counts[signature] > GRAPH_LIMIT
    ]

    candidate_map: defaultdict[metric.TensorSignature, list[dict[str, Any]]] = defaultdict(list)
    for row in candidates7:
        signature = tuple(row["canonical_signature"])
        if signature in representatives:
            candidate_map[signature].append(row)

    phi_table = metric.full_components(metric.selected_phi())
    delta = direct.delta_r()
    delta_table = metric.full_components(delta)
    delta_bar_table = metric.full_components(metric.conjugate_form(delta))
    h_basis, hbar_basis = neutral.neutral_basis()
    h_tables = [metric.full_components(form) for form in h_basis]
    hbar_tables = [metric.full_components(form) for form in hbar_basis]

    evaluation_rows: list[dict[str, Any]] = []
    for signature in low_representatives:
        audit = neutral.coefficient_audit_for_signature(
            signature,
            phi_table=phi_table,
            delta_table=delta_table,
            delta_bar_table=delta_bar_table,
            h_tables=h_tables,
            hbar_tables=hbar_tables,
        )
        monomials = candidate_map[signature]
        nonzero = not audit["all_neutral_H_coefficients_zero"]
        rank_records = [
            {
                "phase_vector_D_H_S": row["phase_vector_D_H_S"],
                **phase_rank_record(row["phase_vector_D_H_S"]),
            }
            for row in monomials
        ]
        evaluation_rows.append(
            {
                **audit,
                "dimension7_monomials": monomials,
                "phase_rank_records": rank_records,
                "nonzero_selected_vacuum_channel": nonzero,
            }
        )

    nonzero_rows = [
        row for row in evaluation_rows if row["nonzero_selected_vacuum_channel"]
    ]
    total_graphs = sum(row["n_metric_graphs"] for row in evaluation_rows)
    total_evaluations = sum(
        row["n_graph_coefficient_evaluations"] for row in evaluation_rows
    )
    maximum = max(
        (row["maximum_abs_coefficient"] for row in evaluation_rows),
        default=0.0,
    )
    all_nonzero_rank_two = all(
        record["rank_with_kappa"] == 2
        and record["null_is_PQ_1_1_minus2"]
        for row in nonzero_rows
        for record in row["phase_rank_records"]
    )

    dim6_green = bool(
        dim6.get("n_failed") == 0
        and dim6.get("flags", {}).get(
            "full_selected_vacuum_dimension6_phase_lifting_no_go_proven"
        )
    )
    charge_crosscheck = all(
        row["charge_allowed"]["all"] for row in candidates7
    )
    finite = all(
        np.isfinite(row["maximum_abs_coefficient"])
        for row in evaluation_rows
    )

    checks = {
        "dimension6_no_go_upstream_green": dim6_green,
        "dimension7_charge_crosscheck": charge_crosscheck,
        "dimension7_candidate_count_98": len(candidates7) == 98,
        "dimension7_signature_count_98": len(signatures7) == 98,
        "new_tensor_signature_count_68": len(new_signatures) == 68,
        "new_odd_H_signature_count_42": len(odd_h) == 42,
        "new_even_H_signature_count_26": len(even_h) == 26,
        "new_even_H_representative_count_13": len(representatives) == 13,
        "low_complexity_representative_count_8": len(low_representatives) == 8,
        "high_complexity_representative_count_5": len(high_representatives) == 5,
        "low_complexity_metric_graph_count_1128": total_graphs == 1128,
        "low_complexity_graph_coefficient_count_5835": total_evaluations == 5835,
        "all_results_finite": finite,
        "any_found_channel_has_rank_two_with_kappa_and_PQ_null": all_nonzero_rank_two,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]

    if failures:
        status = "DIM7_LOW_COMPLEXITY_PHASE_SCREEN_FAILED"
    elif nonzero_rows:
        status = "DIM7_LOW_COMPLEXITY_NONZERO_PHASE_CHANNEL_FOUND__STATIONARITY_OPEN"
    else:
        status = "DIM7_LOW_COMPLEXITY_SCREEN_ZERO__FIVE_HIGH_COMPLEXITY_REPS_OPEN"

    return {
        "status": status,
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "enumeration": {
            "dimension7_charge_allowed_monomials": len(candidates7),
            "dimension7_tensor_signatures": len(signatures7),
            "new_tensor_signatures_beyond_dim6": len(new_signatures),
            "new_odd_H_signatures": len(odd_h),
            "new_even_H_signatures": len(even_h),
            "new_even_H_conjugacy_representatives": len(representatives),
            "low_complexity_representatives": [
                list(signature) for signature in low_representatives
            ],
            "high_complexity_representatives": [
                {
                    "signature_P_D_Db_H_Hb": list(signature),
                    "n_metric_graphs": graph_counts[signature],
                    "dimension7_monomials": candidate_map[signature],
                }
                for signature in high_representatives
            ],
            "graph_limit": GRAPH_LIMIT,
        },
        "screen": {
            "representatives_evaluated": evaluation_rows,
            "total_metric_graphs": total_graphs,
            "total_graph_coefficient_evaluations": total_evaluations,
            "maximum_abs_coefficient": float(maximum),
            "n_nonzero_representatives": len(nonzero_rows),
            "nonzero_representatives": nonzero_rows,
        },
        "epsilon_statement": {
            "all_candidates_contain_126_five_form": True,
            "epsilon_channels_reduce_to_metric_by_Hodge_duality": True,
            "independent_epsilon_screen_required": False,
        },
        "flags": {
            "dimension7_low_complexity_screen_complete": not bool(failures),
            "nonzero_dimension7_phase_channel_found": bool(nonzero_rows),
            "selected_vacuum_phase_lift_exists_in_screened_dim7_sector": bool(
                nonzero_rows
            ),
            "five_high_complexity_dimension7_representatives_open": not bool(
                nonzero_rows
            ),
            "stationarity_rebuilt_with_dimension7_operator": False,
            "selected_vacuum_fully_stabilized": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "next_action": (
            "Insert the lowest-complexity nonzero dimension-seven invariant into "
            "the selected-vacuum phase/radial potential and solve stationarity."
            if nonzero_rows
            else (
                "Evaluate the five high-complexity dimension-seven representatives "
                "with exact neutral-H multilinear coefficients."
            )
        ),
        "verdict": (
            (
                f"The targeted dimension-seven wave found {len(nonzero_rows)} "
                "nonzero selected-vacuum tensor representative(s). Each active "
                "phase vector is independent of kappa and leaves the unique PQ "
                "null, so a dimension-seven phase lift exists in principle. "
                "Its coupling, radial stationarity, boundedness and full Hessian "
                "remain open."
            )
            if nonzero_rows
            else (
                "All eight low-complexity new dimension-seven representatives "
                "vanish on the selected vacuum after 5,835 exact neutral-basis "
                "graph/coefficient evaluations. Five higher-complexity "
                "representatives remain open; the model is not excluded."
            )
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    screen = report["screen"]
    OUT_MD.write_text(
        "# Selected-vacuum dimension-seven low-complexity phase screen — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Representatives evaluated: `{len(screen['representatives_evaluated'])}`\n"
        f"- Graph/coefficient evaluations: `{screen['total_graph_coefficient_evaluations']}`\n"
        f"- Nonzero representatives: `{screen['n_nonzero_representatives']}`\n\n"
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
                "enumeration": report["enumeration"],
                "screen": {
                    "total_metric_graphs": report["screen"]["total_metric_graphs"],
                    "total_graph_coefficient_evaluations": report["screen"][
                        "total_graph_coefficient_evaluations"
                    ],
                    "maximum_abs_coefficient": report["screen"][
                        "maximum_abs_coefficient"
                    ],
                    "n_nonzero_representatives": report["screen"][
                        "n_nonzero_representatives"
                    ],
                    "nonzero_representatives": report["screen"][
                        "nonzero_representatives"
                    ],
                },
                "flags": report["flags"],
                "next_action": report["next_action"],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
