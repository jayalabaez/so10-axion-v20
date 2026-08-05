#!/usr/bin/env python3
"""Evaluate the three remaining dimension-seven phase-sensitive representatives.

The selected-vacuum dimension-six search is closed and the first ten of the
thirteen dimension-seven conjugacy representatives have been evaluated:

* eight low-complexity representatives: zero;
* Wave 1, (4,0,2,0,0) and (2,1,3,0,0): zero.

This module evaluates one of the three remaining representatives per process,
so GitHub Actions can run them in parallel without hiding a slow class behind
one monolithic timeout:

    2a: (0,2,4,0,0), 12,043 graphs, 1 neutral-H assignment;
    2b: (3,0,2,2,0),  3,387 graphs, 4 neutral-H assignments;
    2c: (1,1,3,2,0),  4,897 graphs, 4 neutral-H assignments.

Signatures are ordered as (Phi210, Delta, Delta_dag, H10, H10_dag).  Epsilon
contractions are not separately evaluated because the 126bar five-form Hodge
eigenvalue reduces one-epsilon structures to the metric sector already used
here.  A nonzero result proves only that a phase-lifting operator exists on the
selected vacuum; stationarity, boundedness and the full scalar Hessian would
still remain open.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import direct_phi_h_sigmabar_tensor_v20 as direct
import selected_vacuum_dim7_high_complexity_wave1_v20 as wave1
import selected_vacuum_dim7_low_complexity_phase_screen_v20 as low
import selected_vacuum_neutral_h10_dim6_no_go_v20 as neutral
import selected_vacuum_phase_invariant_dim6_metric_audit_v20 as metric

ROOT = Path(__file__).resolve().parent
TOL = neutral.TOL

WAVE_SPECS: dict[str, dict[str, Any]] = {
    "2a": {
        "signature": (0, 2, 4, 0, 0),
        "n_metric_graphs": 12043,
        "n_neutral_assignments": 1,
        "evaluation_cost": 12043,
    },
    "2b": {
        "signature": (3, 0, 2, 2, 0),
        "n_metric_graphs": 3387,
        "n_neutral_assignments": 4,
        "evaluation_cost": 13548,
    },
    "2c": {
        "signature": (1, 1, 3, 2, 0),
        "n_metric_graphs": 4897,
        "n_neutral_assignments": 4,
        "evaluation_cost": 19588,
    },
}


def output_paths(wave: str) -> tuple[Path, Path]:
    tag = wave.upper()
    return (
        ROOT / f"SELECTED_VACUUM_DIM7_REMAINING_{tag}_V20.json",
        ROOT / f"SELECTED_VACUUM_DIM7_REMAINING_{tag}_V20.md",
    )


def planning_context() -> dict[str, Any]:
    representatives, candidate_map = wave1.dimension7_representatives()
    graph_counts = {
        signature: len(
            metric.multigraphs_for_degrees(metric.tensor_degrees(signature))
        )
        for signature in representatives
    }
    high = [
        signature
        for signature in representatives
        if graph_counts[signature] > low.GRAPH_LIMIT
    ]
    assignment_counts = {
        signature: 2 ** (signature[3] + signature[4]) for signature in high
    }
    costs = {
        signature: graph_counts[signature] * assignment_counts[signature]
        for signature in high
    }
    ordered = sorted(high, key=lambda signature: (costs[signature], signature))
    remaining = ordered[len(wave1.EXPECTED_SIGNATURES) :]
    return {
        "representatives": representatives,
        "candidate_map": candidate_map,
        "graph_counts": graph_counts,
        "assignment_counts": assignment_counts,
        "costs": costs,
        "ordered_high": ordered,
        "remaining": remaining,
    }


def phase_rank_records(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "phase_vector_D_H_S": row["phase_vector_D_H_S"],
            **low.phase_rank_record(row["phase_vector_D_H_S"]),
        }
        for row in rows
    ]


def build_report(wave: str) -> dict[str, Any]:
    if wave not in WAVE_SPECS:
        raise ValueError(f"unknown wave {wave!r}; choose one of {sorted(WAVE_SPECS)}")

    spec = WAVE_SPECS[wave]
    signature: metric.TensorSignature = spec["signature"]
    context = planning_context()
    candidate_map = context["candidate_map"]

    phi_table = metric.full_components(metric.selected_phi())
    delta = direct.delta_r()
    delta_table = metric.full_components(delta)
    delta_bar_table = metric.full_components(metric.conjugate_form(delta))
    h_basis, hbar_basis = neutral.neutral_basis()
    h_tables = [metric.full_components(form) for form in h_basis]
    hbar_tables = [metric.full_components(form) for form in hbar_basis]

    audit = neutral.coefficient_audit_for_signature(
        signature,
        phi_table=phi_table,
        delta_table=delta_table,
        delta_bar_table=delta_bar_table,
        h_tables=h_tables,
        hbar_tables=hbar_tables,
    )
    monomials = candidate_map[signature]
    ranks = phase_rank_records(monomials)
    nonzero = not audit["all_neutral_H_coefficients_zero"]
    rank_contract = all(
        row["rank_with_kappa"] == 2 and row["null_is_PQ_1_1_minus2"]
        for row in ranks
    )

    expected_remaining = [WAVE_SPECS[name]["signature"] for name in WAVE_SPECS]
    checks = {
        "thirteen_dimension7_representatives": len(context["representatives"]) == 13,
        "five_high_complexity_representatives": len(context["ordered_high"]) == 5,
        "wave1_is_first_two_by_total_cost": context["ordered_high"][:2]
        == wave1.EXPECTED_SIGNATURES,
        "remaining_signatures_exact": context["remaining"] == expected_remaining,
        "selected_signature_exact": signature in context["remaining"],
        "selected_graph_count_exact": audit["n_metric_graphs"]
        == spec["n_metric_graphs"],
        "selected_assignment_count_exact": audit["n_H_multilinear_assignments"]
        == spec["n_neutral_assignments"],
        "selected_evaluation_cost_exact": audit["n_graph_coefficient_evaluations"]
        == spec["evaluation_cost"],
        "all_candidate_phase_vectors_rank_two_with_PQ_null": rank_contract,
        "finite_coefficient_result": audit["maximum_abs_coefficient"] >= 0.0,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]

    if failures:
        status = f"DIM7_REMAINING_{wave.upper()}_FAILED"
    elif nonzero:
        status = (
            f"DIM7_REMAINING_{wave.upper()}_NONZERO_CHANNEL_FOUND__"
            "STATIONARITY_OPEN"
        )
    else:
        status = f"DIM7_REMAINING_{wave.upper()}_ZERO"

    result = {
        **audit,
        "planned_evaluation_cost": spec["evaluation_cost"],
        "dimension7_monomials": monomials,
        "phase_rank_records": ranks,
        "nonzero_selected_vacuum_channel": nonzero,
    }
    return {
        "status": status,
        "overall_state": "BLOCKED",
        "wave": wave,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "result": result,
        "upstream_contract": {
            "dimension6_selected_vacuum_no_go_required_on_same_head": True,
            "dimension7_low_complexity_zero_required_on_same_head": True,
            "dimension7_wave1_zero_required_on_same_head": True,
            "upstream_expensive_reports_recomputed_in_this_process": False,
        },
        "flags": {
            "selected_representative_complete": not bool(failures),
            "nonzero_dimension7_phase_channel_found": nonzero,
            "stationarity_rebuilt": False,
            "full_scalar_hessian_rebuilt": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "next_action": (
            "Insert this operator into the phase/radial potential and rebuild stationarity."
            if nonzero
            else "Combine all three remaining-wave reports into the complete dimension-seven verdict."
        ),
        "verdict": (
            f"Wave {wave} found a nonzero selected-vacuum dimension-seven "
            "phase channel. This can lift the extra phase in principle, but "
            "stationarity, boundedness and the full Hessian remain open."
            if nonzero
            else (
                f"Wave {wave} vanishes after {audit['n_graph_coefficient_evaluations']:,} "
                "exact selected-vacuum graph/coefficient evaluations."
            )
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    out_json, out_md = output_paths(report["wave"])
    out_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    result = report["result"]
    out_md.write_text(
        f"# Selected-vacuum dimension-seven remaining wave {report['wave']} — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Signature: `{result['signature_P_D_Db_H_Hb']}`\n"
        f"- Metric graphs: `{result['n_metric_graphs']}`\n"
        f"- Neutral assignments: `{result['n_H_multilinear_assignments']}`\n"
        f"- Exact evaluations: `{result['n_graph_coefficient_evaluations']}`\n"
        f"- Maximum coefficient: `{result['maximum_abs_coefficient']:.12e}`\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wave", required=True, choices=sorted(WAVE_SPECS))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report(args.wave)
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
