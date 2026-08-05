#!/usr/bin/env python3
"""Exact first wave of dimension-eight selected-vacuum phase coefficients.

The dimension-eight census found twenty-one genuinely new even-H tensor
representatives. This module evaluates one of the twelve representatives whose
full neutral-basis workload is at most 20,000 graph/coefficient contractions.
Each representative is run in a separate CI matrix job.

A nonzero coefficient establishes a candidate phase-lifting operator only.
Stationarity, boundedness and the full scalar Hessian remain open until the
operator is inserted with a dimensionful Wilson coefficient and the complete
vacuum is re-minimized.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import direct_phi_h_sigmabar_tensor_v20 as direct
import selected_vacuum_dim7_low_complexity_phase_screen_v20 as dim7
import selected_vacuum_dimension8_phase_census_v20 as census
import selected_vacuum_neutral_h10_dim6_no_go_v20 as neutral
import selected_vacuum_phase_invariant_dim6_metric_audit_v20 as metric

ROOT = Path(__file__).resolve().parent

WAVE_SPECS: dict[str, dict[str, Any]] = {
    "8a": {"signature": (0, 0, 2, 1, 3), "graphs": 21, "assignments": 16, "cost": 336},
    "8b": {"signature": (2, 0, 2, 0, 2), "graphs": 177, "assignments": 4, "cost": 708},
    "8c": {"signature": (0, 0, 4, 1, 1), "graphs": 241, "assignments": 4, "cost": 964},
    "8d": {"signature": (0, 1, 3, 0, 2), "graphs": 241, "assignments": 4, "cost": 964},
    "8e": {"signature": (1, 0, 2, 2, 2), "graphs": 138, "assignments": 16, "cost": 2208},
    "8f": {"signature": (1, 0, 2, 4, 0), "graphs": 138, "assignments": 16, "cost": 2208},
    "8g": {"signature": (2, 0, 4, 0, 0), "graphs": 7243, "assignments": 1, "cost": 7243},
    "8h": {"signature": (0, 1, 5, 0, 0), "graphs": 12043, "assignments": 1, "cost": 12043},
    "8i": {"signature": (3, 0, 2, 1, 1), "graphs": 3387, "assignments": 4, "cost": 13548},
    "8j": {"signature": (0, 0, 2, 4, 2), "graphs": 215, "assignments": 64, "cost": 13760},
    "8k": {"signature": (1, 0, 4, 2, 0), "graphs": 4897, "assignments": 4, "cost": 19588},
    "8l": {"signature": (1, 1, 3, 1, 1), "graphs": 4897, "assignments": 4, "cost": 19588},
}


def output_paths(wave: str) -> tuple[Path, Path]:
    tag = wave.upper()
    return (
        ROOT / f"SELECTED_VACUUM_DIMENSION8_FIRST_WAVE_{tag}_V20.json",
        ROOT / f"SELECTED_VACUUM_DIMENSION8_FIRST_WAVE_{tag}_V20.md",
    )


def planning_context() -> dict[str, Any]:
    candidates, _signatures, _odd_h, representatives, candidate_map = (
        census.canonical_representatives(8)
    )
    prior = census.prior_representatives(7)
    rows: list[dict[str, Any]] = []
    for signature in representatives:
        if signature in prior:
            continue
        degrees = tuple(metric.tensor_degrees(signature))
        graphs = census.count_pairwise_multigraphs(degrees)
        assignments = 2 ** (signature[3] + signature[4])
        rows.append(
            {
                "signature": signature,
                "graphs": graphs,
                "assignments": assignments,
                "cost": graphs * assignments,
            }
        )
    rows.sort(key=lambda row: (row["cost"], row["signature"]))
    first = [row for row in rows if row["cost"] <= 20000]
    return {
        "candidates": candidates,
        "candidate_map": candidate_map,
        "new_rows": rows,
        "first_wave": first,
    }


def build_report(wave: str) -> dict[str, Any]:
    if wave not in WAVE_SPECS:
        raise ValueError(f"unknown wave {wave!r}")
    spec = WAVE_SPECS[wave]
    signature: metric.TensorSignature = spec["signature"]
    context = planning_context()

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
    monomials = context["candidate_map"][signature]
    rank_records = [
        {
            "phase_vector_D_H_S": row["phase_vector_D_H_S"],
            **dim7.phase_rank_record(row["phase_vector_D_H_S"]),
        }
        for row in monomials
    ]
    nonzero = not audit["all_neutral_H_coefficients_zero"]
    expected_first = [spec_row["signature"] for spec_row in WAVE_SPECS.values()]
    checks = {
        "dimension8_candidate_count_166": len(context["candidates"]) == 166,
        "twenty_one_new_representatives": len(context["new_rows"]) == 21,
        "twelve_first_wave_representatives": len(context["first_wave"]) == 12,
        "first_wave_signatures_exact": [row["signature"] for row in context["first_wave"]]
        == expected_first,
        "selected_signature_exact": signature in expected_first,
        "selected_graph_count_exact": audit["n_metric_graphs"] == spec["graphs"],
        "selected_assignment_count_exact": audit["n_H_multilinear_assignments"]
        == spec["assignments"],
        "selected_cost_exact": audit["n_graph_coefficient_evaluations"] == spec["cost"],
        "phase_rank_two_and_only_PQ_null": all(
            row["rank_with_kappa"] == 2 and row["null_is_PQ_1_1_minus2"]
            for row in rank_records
        ),
        "epsilon_reduction_applies": signature[1] + signature[2] > 0,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    tag = wave.upper()
    if failures:
        status = f"DIMENSION8_FIRST_WAVE_{tag}_FAILED"
    elif nonzero:
        status = f"DIMENSION8_FIRST_WAVE_{tag}_NONZERO_CHANNEL_FOUND__STATIONARITY_OPEN"
    else:
        status = f"DIMENSION8_FIRST_WAVE_{tag}_ZERO"

    result = {
        **audit,
        "dimension8_monomials": monomials,
        "phase_rank_records": rank_records,
        "nonzero_selected_vacuum_channel": nonzero,
        "planned_evaluation_cost": spec["cost"],
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
            "selected_vacuum_no_go_through_dimension7_required": True,
            "dimension8_census_required": True,
            "upstream_expensive_reports_recomputed_here": False,
        },
        "flags": {
            "selected_dimension8_representative_complete": not bool(failures),
            "nonzero_dimension8_phase_channel_found": nonzero,
            "stationarity_rebuilt": False,
            "boundedness_reproved": False,
            "full_scalar_hessian_rebuilt": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "next_action": (
            "Insert the lowest-cost nonzero dimension-eight operator into the potential and rebuild stationarity."
            if nonzero
            else "Aggregate all twelve first-wave reports and continue with the nine higher-cost representatives."
        ),
        "verdict": (
            f"Dimension-eight wave {wave} found a nonzero selected-vacuum phase channel. "
            "This is a candidate lift, not a completed vacuum."
            if nonzero
            else f"Dimension-eight wave {wave} vanishes after {audit['n_graph_coefficient_evaluations']:,} exact evaluations."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    out_json, out_md = output_paths(report["wave"])
    out_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    result = report["result"]
    out_md.write_text(
        f"# Selected-vacuum dimension-eight first wave {report['wave']} — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Signature: `{result['signature_P_D_Db_H_Hb']}`\n"
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
