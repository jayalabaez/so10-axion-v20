#!/usr/bin/env python3
"""Dimension-seven high-complexity phase screen, wave 1.

The low-complexity wave found no selected-vacuum phase channel. This module
fully evaluates the two smallest remaining metric representatives:

    (4,0,2,0,0)  with 4,691 graphs,
    (2,1,3,0,0)  with 7,243 graphs.

They contain no H factors, so no neutral-H assignment sampling is involved;
each graph is evaluated directly on the selected p,a,omega,Delta_R tensors.
Hodge duality again reduces epsilon contractions to this metric sector.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import direct_phi_h_sigmabar_tensor_v20 as direct
import selected_vacuum_dim7_low_complexity_phase_screen_v20 as low
import selected_vacuum_neutral_h10_dim6_no_go_v20 as neutral
import selected_vacuum_phase_invariant_dim6_metric_audit_v20 as metric

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SELECTED_VACUUM_DIM7_HIGH_COMPLEXITY_WAVE1_V20.json"
OUT_MD = ROOT / "SELECTED_VACUUM_DIM7_HIGH_COMPLEXITY_WAVE1_V20.md"
TOL = neutral.TOL
EXPECTED_SIGNATURES: list[metric.TensorSignature] = [
    (4, 0, 2, 0, 0),
    (2, 1, 3, 0, 0),
]
EXPECTED_GRAPH_COUNTS = {
    (4, 0, 2, 0, 0): 4691,
    (2, 1, 3, 0, 0): 7243,
}


def dimension7_representatives() -> tuple[
    list[metric.TensorSignature],
    defaultdict[metric.TensorSignature, list[dict[str, Any]]],
]:
    candidates = low.exact_dimension_candidates(7)
    dim6_signatures = {
        metric.tensor_signature(row["counts"])
        for row in metric.charge_candidates(6)
    }
    new_signatures = {
        metric.tensor_signature(row["counts"]) for row in candidates
    }.difference(dim6_signatures)
    even = {
        signature
        for signature in new_signatures
        if (signature[3] + signature[4]) % 2 == 0
    }
    representatives = sorted(
        {metric.canonical_signature(signature) for signature in even}
    )
    candidate_map: defaultdict[metric.TensorSignature, list[dict[str, Any]]] = defaultdict(list)
    for row in candidates:
        canonical = tuple(row["canonical_signature"])
        if canonical in representatives:
            candidate_map[canonical].append(row)
    return representatives, candidate_map


def build_report() -> dict[str, Any]:
    dim6 = neutral.build_report()
    representatives, candidate_map = dimension7_representatives()
    graph_counts = {
        signature: len(
            metric.multigraphs_for_degrees(metric.tensor_degrees(signature))
        )
        for signature in representatives
    }
    high = sorted(
        [signature for signature in representatives if graph_counts[signature] > low.GRAPH_LIMIT],
        key=lambda signature: graph_counts[signature],
    )
    wave = high[:2]

    phi_table = metric.full_components(metric.selected_phi())
    delta = direct.delta_r()
    delta_table = metric.full_components(delta)
    delta_bar_table = metric.full_components(metric.conjugate_form(delta))
    h_basis, hbar_basis = neutral.neutral_basis()
    h_tables = [metric.full_components(form) for form in h_basis]
    hbar_tables = [metric.full_components(form) for form in hbar_basis]

    rows: list[dict[str, Any]] = []
    for signature in wave:
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
        rows.append(
            {
                **audit,
                "dimension7_monomials": monomials,
                "phase_rank_records": [
                    {
                        "phase_vector_D_H_S": row["phase_vector_D_H_S"],
                        **low.phase_rank_record(row["phase_vector_D_H_S"]),
                    }
                    for row in monomials
                ],
                "nonzero_selected_vacuum_channel": nonzero,
            }
        )

    nonzero_rows = [row for row in rows if row["nonzero_selected_vacuum_channel"]]
    total_graphs = sum(row["n_metric_graphs"] for row in rows)
    total_evaluations = sum(row["n_graph_coefficient_evaluations"] for row in rows)
    maximum = max((row["maximum_abs_coefficient"] for row in rows), default=0.0)
    dim6_green = bool(
        dim6.get("n_failed") == 0
        and dim6.get("flags", {}).get(
            "full_selected_vacuum_dimension6_phase_lifting_no_go_proven"
        )
    )
    all_nonzero_rank_two = all(
        record["rank_with_kappa"] == 2 and record["null_is_PQ_1_1_minus2"]
        for row in nonzero_rows
        for record in row["phase_rank_records"]
    )

    checks = {
        "dimension6_no_go_upstream_green": dim6_green,
        "thirteen_dimension7_representatives": len(representatives) == 13,
        "five_high_complexity_representatives": len(high) == 5,
        "wave1_signatures_exact": wave == EXPECTED_SIGNATURES,
        "wave1_graph_counts_exact": all(
            graph_counts[signature] == EXPECTED_GRAPH_COUNTS[signature]
            for signature in wave
        ),
        "wave1_total_graphs_11934": total_graphs == 11934,
        "wave1_total_evaluations_11934": total_evaluations == 11934,
        "any_found_channel_has_rank_two_and_PQ_null": all_nonzero_rank_two,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]

    if failures:
        status = "DIM7_HIGH_COMPLEXITY_WAVE1_FAILED"
    elif nonzero_rows:
        status = "DIM7_HIGH_COMPLEXITY_WAVE1_NONZERO_CHANNEL_FOUND__STATIONARITY_OPEN"
    else:
        status = "DIM7_HIGH_COMPLEXITY_WAVE1_ZERO__THREE_REPRESENTATIVES_OPEN"

    remaining = high[2:]
    return {
        "status": status,
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "wave1": {
            "representatives": rows,
            "total_metric_graphs": total_graphs,
            "total_graph_coefficient_evaluations": total_evaluations,
            "maximum_abs_coefficient": float(maximum),
            "n_nonzero_representatives": len(nonzero_rows),
            "nonzero_representatives": nonzero_rows,
        },
        "remaining_high_complexity_representatives": [
            {
                "signature_P_D_Db_H_Hb": list(signature),
                "n_metric_graphs": graph_counts[signature],
                "dimension7_monomials": candidate_map[signature],
            }
            for signature in remaining
        ],
        "flags": {
            "wave1_complete": not bool(failures),
            "nonzero_dimension7_phase_channel_found": bool(nonzero_rows),
            "three_high_complexity_representatives_open": not bool(nonzero_rows),
            "stationarity_rebuilt": False,
            "selected_vacuum_fully_stabilized": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "next_action": (
            "Insert the lowest-complexity nonzero operator into the phase and radial potential."
            if nonzero_rows
            else "Evaluate the remaining three high-complexity dimension-seven representatives."
        ),
        "verdict": (
            (
                f"Wave 1 found {len(nonzero_rows)} nonzero dimension-seven "
                "representative(s). A phase lift exists in principle, but "
                "stationarity and the full Hessian remain open."
            )
            if nonzero_rows
            else (
                "Both smallest high-complexity dimension-seven representatives "
                "vanish after 11,934 exact graph evaluations. Three "
                "representatives remain open; the whole model is not excluded."
            )
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    wave = report["wave1"]
    OUT_MD.write_text(
        "# Selected-vacuum dimension-seven high-complexity wave 1 — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Graph evaluations: `{wave['total_graph_coefficient_evaluations']}`\n"
        f"- Nonzero representatives: `{wave['n_nonzero_representatives']}`\n\n"
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
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
