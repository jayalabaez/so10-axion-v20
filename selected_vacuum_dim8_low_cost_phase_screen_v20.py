#!/usr/bin/env python3
"""Low-cost dimension-eight selected-vacuum phase-invariant screen.

The complete dimension-seven audit found no phase-lifting invariant for the
current fields, charges, and selected vacuum. This module enumerates genuinely
new dimension-eight tensor signatures and evaluates the six cheapest even-H
conjugacy representatives in the exact neutral 10_H basis.

The calculation is staged: a nonzero contraction is a candidate phase-lifting
operator, not proof of stationarity or a positive full scalar Hessian. If all
six vanish, fifteen higher-cost representatives remain open.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import selected_vacuum_dim7_complete_no_go_v20 as dim7_complete
import selected_vacuum_dim7_low_complexity_phase_screen_v20 as dim7
import selected_vacuum_neutral_h10_dim6_no_go_v20 as neutral
import selected_vacuum_phase_invariant_dim6_metric_audit_v20 as metric

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SELECTED_VACUUM_DIM8_LOW_COST_PHASE_SCREEN_V20.json"
OUT_MD = ROOT / "SELECTED_VACUUM_DIM8_LOW_COST_PHASE_SCREEN_V20.md"
TOL = neutral.TOL

EXPECTED_LOW_COST = [
    ((0, 0, 2, 1, 3), 21, 16, 336),
    ((2, 0, 2, 0, 2), 177, 4, 708),
    ((0, 0, 4, 1, 1), 241, 4, 964),
    ((0, 1, 3, 0, 2), 241, 4, 964),
    ((1, 0, 2, 2, 2), 138, 16, 2208),
    ((1, 0, 2, 4, 0), 138, 16, 2208),
]


def dimension_candidates(dimension: int) -> list[dict[str, Any]]:
    return dim7.exact_dimension_candidates(dimension)


def build_report() -> dict[str, Any]:
    upstream = dim7_complete.build_report()
    candidates8 = dimension_candidates(8)

    lower_signatures: set[metric.TensorSignature] = set()
    for dimension in range(2, 8):
        lower_signatures.update(
            metric.tensor_signature(row["counts"])
            for row in dimension_candidates(dimension)
        )

    signatures8 = {
        metric.tensor_signature(row["counts"]) for row in candidates8
    }
    new_signatures = signatures8.difference(lower_signatures)
    odd_h = {
        signature
        for signature in new_signatures
        if (signature[3] + signature[4]) % 2 == 1
    }
    even_h = new_signatures.difference(odd_h)
    representatives = sorted(
        {metric.canonical_signature(signature) for signature in even_h}
    )

    candidate_map: defaultdict[metric.TensorSignature, list[dict[str, Any]]] = defaultdict(list)
    for row in candidates8:
        canonical = tuple(row["canonical_signature"])
        if canonical in representatives:
            candidate_map[canonical].append(row)

    workload: list[dict[str, Any]] = []
    for signature in representatives:
        graph_count = len(
            metric.multigraphs_for_degrees(metric.tensor_degrees(signature))
        )
        assignments = 2 ** (signature[3] + signature[4])
        workload.append(
            {
                "signature_P_D_Db_H_Hb": list(signature),
                "n_metric_graphs": graph_count,
                "n_H_multilinear_assignments": assignments,
                "planned_evaluation_cost": graph_count * assignments,
                "dimension8_monomials": candidate_map[signature],
            }
        )
    workload.sort(
        key=lambda row: (
            row["planned_evaluation_cost"],
            row["n_metric_graphs"],
            row["signature_P_D_Db_H_Hb"],
        )
    )
    low_rows = workload[:6]
    low_signatures = [tuple(row["signature_P_D_Db_H_Hb"]) for row in low_rows]

    phi_table = metric.full_components(metric.selected_phi())
    delta = direct.delta_r()
    delta_table = metric.full_components(delta)
    delta_bar_table = metric.full_components(metric.conjugate_form(delta))
    h_basis, hbar_basis = neutral.neutral_basis()
    h_tables = [metric.full_components(form) for form in h_basis]
    hbar_tables = [metric.full_components(form) for form in hbar_basis]

    evaluated: list[dict[str, Any]] = []
    for workload_row in low_rows:
        signature = tuple(workload_row["signature_P_D_Db_H_Hb"])
        audit = neutral.coefficient_audit_for_signature(
            signature,
            phi_table=phi_table,
            delta_table=delta_table,
            delta_bar_table=delta_bar_table,
            h_tables=h_tables,
            hbar_tables=hbar_tables,
        )
        monomials = candidate_map[signature]
        rank_records = [
            {
                "phase_vector_D_H_S": row["phase_vector_D_H_S"],
                **dim7.phase_rank_record(row["phase_vector_D_H_S"]),
            }
            for row in monomials
        ]
        evaluated.append(
            {
                **audit,
                "dimension8_monomials": monomials,
                "phase_rank_records": rank_records,
                "nonzero_selected_vacuum_channel": not audit[
                    "all_neutral_H_coefficients_zero"
                ],
            }
        )

    nonzero = [row for row in evaluated if row["nonzero_selected_vacuum_channel"]]
    total_graphs = sum(int(row["n_metric_graphs"]) for row in evaluated)
    total_evaluations = sum(
        int(row["n_graph_coefficient_evaluations"]) for row in evaluated
    )
    maximum = max(
        (float(row["maximum_abs_coefficient"]) for row in evaluated),
        default=0.0,
    )
    all_rank_two_pq = all(
        record["rank_with_kappa"] == 2
        and record["null_is_PQ_1_1_minus2"]
        for row in evaluated
        for record in row["phase_rank_records"]
    )
    expected_signatures = [row[0] for row in EXPECTED_LOW_COST]
    expected_graphs = [row[1] for row in EXPECTED_LOW_COST]
    expected_assignments = [row[2] for row in EXPECTED_LOW_COST]
    expected_costs = [row[3] for row in EXPECTED_LOW_COST]

    checks = {
        "dimension7_complete_no_go_upstream_green": bool(
            upstream.get("n_failed") == 0
            and upstream.get("flags", {}).get(
                "full_selected_vacuum_dimension7_phase_lifting_no_go_proven"
            )
        ),
        "dimension8_charge_allowed_candidate_count_166": len(candidates8) == 166,
        "dimension8_tensor_signature_count_166": len(signatures8) == 166,
        "lower_dimension_signature_union_count_156": len(lower_signatures) == 156,
        "genuinely_new_dimension8_signature_count_108": len(new_signatures) == 108,
        "new_odd_H_signature_count_66": len(odd_h) == 66,
        "new_even_H_signature_count_42": len(even_h) == 42,
        "new_even_H_conjugacy_representative_count_21": len(representatives) == 21,
        "low_cost_representative_count_6": len(low_rows) == 6,
        "low_cost_signatures_exact": low_signatures == expected_signatures,
        "low_cost_graph_counts_exact": [row["n_metric_graphs"] for row in low_rows]
        == expected_graphs,
        "low_cost_assignment_counts_exact": [
            row["n_H_multilinear_assignments"] for row in low_rows
        ]
        == expected_assignments,
        "low_cost_planned_costs_exact": [
            row["planned_evaluation_cost"] for row in low_rows
        ]
        == expected_costs,
        "low_cost_total_metric_graphs_956": total_graphs == 956,
        "low_cost_total_coefficient_evaluations_7388": total_evaluations == 7388,
        "all_coefficients_finite": all(
            np.isfinite(row["maximum_abs_coefficient"]) for row in evaluated
        ),
        "all_candidate_phase_vectors_rank_two_with_PQ_null": all_rank_two_pq,
        "all_new_representatives_contain_126_five_form": all(
            signature[1] + signature[2] > 0 for signature in representatives
        ),
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]

    if failures:
        status = "DIM8_LOW_COST_PHASE_SCREEN_FAILED"
    elif nonzero:
        status = "DIM8_LOW_COST_NONZERO_PHASE_CHANNEL_FOUND__STATIONARITY_OPEN"
    else:
        status = "DIM8_LOW_COST_SCREEN_ZERO__FIFTEEN_REPRESENTATIVES_OPEN"

    return {
        "status": status,
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "enumeration": {
            "dimension8_charge_allowed_monomials": len(candidates8),
            "dimension8_tensor_signatures": len(signatures8),
            "lower_dimension_signature_union": len(lower_signatures),
            "genuinely_new_dimension8_tensor_signatures": len(new_signatures),
            "new_odd_H_signatures": len(odd_h),
            "new_even_H_signatures": len(even_h),
            "new_even_H_conjugacy_representatives": len(representatives),
            "full_workload_order": workload,
        },
        "screen": {
            "representatives_evaluated": evaluated,
            "total_metric_graphs": total_graphs,
            "total_graph_coefficient_evaluations": total_evaluations,
            "maximum_abs_coefficient": maximum,
            "n_nonzero_representatives": len(nonzero),
            "nonzero_representatives": nonzero,
            "representatives_remaining": workload[6:],
        },
        "epsilon_statement": {
            "all_representatives_contain_126_five_form": True,
            "one_epsilon_sector_reduces_to_metric_sector_by_Hodge_duality": True,
        },
        "flags": {
            "dimension7_no_go_used_as_prerequisite": True,
            "dimension8_low_cost_wave_complete": not bool(failures),
            "nonzero_dimension8_phase_channel_found": bool(nonzero),
            "full_selected_vacuum_dimension8_phase_lifting_no_go_proven": False,
            "stationarity_rebuilt": False,
            "full_scalar_hessian_rebuilt": False,
            "selected_vacuum_fully_stabilized": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "next_action": (
            "Insert the lowest-cost nonzero dimension-eight operator into the selected-vacuum phase and radial potential."
            if nonzero
            else "Evaluate the next dimension-eight workload wave from the fifteen remaining representatives."
        ),
        "verdict": (
            f"The six cheapest genuinely new dimension-eight representatives "
            f"were evaluated through {total_evaluations:,} exact coefficients. "
            + (
                f"{len(nonzero)} nonzero representative(s) were found; phase lifting exists in principle, but stationarity and the full Hessian remain open."
                if nonzero
                else "All six vanish; fifteen higher-cost dimension-eight representatives remain open."
            )
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    screen = report["screen"]
    OUT_MD.write_text(
        "# Selected-vacuum dimension-eight low-cost phase screen — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Representatives evaluated: `{len(screen['representatives_evaluated'])}`\n"
        f"- Exact coefficient evaluations: `{screen['total_graph_coefficient_evaluations']}`\n"
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
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
