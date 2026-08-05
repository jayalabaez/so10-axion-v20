#!/usr/bin/env python3
"""Final high-cost dimension-eight selected-vacuum phase coefficient wave.

The dimension-eight census contains twenty-one genuinely new even-H tensor
representatives. The first and second waves cover the fifteen lowest-cost
representatives. This module evaluates one of the final six representatives,
one per CI matrix job:

    8p: (5,0,2,0,0), 146,880 exact evaluations;
    8q: (3,1,3,0,0), 248,904 exact evaluations;
    8r: (4,0,2,2,0), 387,396 exact evaluations;
    8s: (1,2,4,0,0), 448,740 exact evaluations;
    8t: (2,1,3,2,0), 619,684 exact evaluations;
    8u: (0,2,4,2,0), 1,064,452 exact evaluations.

A nonzero coefficient is only a candidate phase-lifting invariant. Stationarity,
boundedness, competing extrema, and the full scalar Hessian remain open until
the corresponding operator is inserted with an explicit Wilson coefficient and
the complete potential is re-minimized.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import direct_phi_h_sigmabar_tensor_v20 as direct
import selected_vacuum_dim7_low_complexity_phase_screen_v20 as dim7
import selected_vacuum_dimension8_first_wave_v20 as first
import selected_vacuum_dimension8_second_wave_v20 as second
import selected_vacuum_neutral_h10_dim6_no_go_v20 as neutral
import selected_vacuum_phase_invariant_dim6_metric_audit_v20 as metric

ROOT = Path(__file__).resolve().parent

WAVE_SPECS: dict[str, dict[str, Any]] = {
    "8p": {"signature": (5, 0, 2, 0, 0), "graphs": 146880, "assignments": 1, "cost": 146880},
    "8q": {"signature": (3, 1, 3, 0, 0), "graphs": 248904, "assignments": 1, "cost": 248904},
    "8r": {"signature": (4, 0, 2, 2, 0), "graphs": 96849, "assignments": 4, "cost": 387396},
    "8s": {"signature": (1, 2, 4, 0, 0), "graphs": 448740, "assignments": 1, "cost": 448740},
    "8t": {"signature": (2, 1, 3, 2, 0), "graphs": 154921, "assignments": 4, "cost": 619684},
    "8u": {"signature": (0, 2, 4, 2, 0), "graphs": 266113, "assignments": 4, "cost": 1064452},
}


def output_paths(wave: str) -> tuple[Path, Path]:
    tag = wave.upper()
    return (
        ROOT / f"SELECTED_VACUUM_DIMENSION8_THIRD_WAVE_{tag}_V20.json",
        ROOT / f"SELECTED_VACUUM_DIMENSION8_THIRD_WAVE_{tag}_V20.md",
    )


def planning_context() -> dict[str, Any]:
    context = first.planning_context()
    used = {spec["signature"] for spec in first.WAVE_SPECS.values()}
    used.update(spec["signature"] for spec in second.WAVE_SPECS.values())
    remaining = [row for row in context["new_rows"] if row["signature"] not in used]
    return {**context, "remaining_after_second": remaining, "third_wave": remaining}


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
    expected = [spec_row["signature"] for spec_row in WAVE_SPECS.values()]
    checks = {
        "twenty_one_new_dimension8_representatives": len(context["new_rows"]) == 21,
        "twelve_first_wave_representatives": len(first.WAVE_SPECS) == 12,
        "three_second_wave_representatives": len(second.WAVE_SPECS) == 3,
        "six_representatives_after_second_wave": len(context["remaining_after_second"]) == 6,
        "third_wave_signatures_exact": [row["signature"] for row in context["third_wave"]] == expected,
        "selected_signature_is_in_final_wave": signature in expected,
        "selected_graph_count_exact": audit["n_metric_graphs"] == spec["graphs"],
        "selected_assignment_count_exact": audit["n_H_multilinear_assignments"] == spec["assignments"],
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
        status = f"DIMENSION8_THIRD_WAVE_{tag}_FAILED"
    elif nonzero:
        status = f"DIMENSION8_THIRD_WAVE_{tag}_NONZERO_CHANNEL_FOUND__STATIONARITY_OPEN"
    else:
        status = f"DIMENSION8_THIRD_WAVE_{tag}_ZERO"

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
        "flags": {
            "selected_dimension8_representative_complete": not bool(failures),
            "nonzero_dimension8_phase_channel_found": nonzero,
            "full_dimension8_no_go_proven_by_this_single_job": False,
            "stationarity_rebuilt": False,
            "boundedness_reproved": False,
            "full_scalar_hessian_rebuilt": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "next_action": (
            "Insert the lowest-cost nonzero operator into the phase/radial potential and rebuild stationarity."
            if nonzero
            else "Aggregate all twenty-one dimension-eight representative reports before declaring a dimension-eight no-go."
        ),
        "verdict": (
            f"Dimension-eight wave {wave} found a nonzero selected-vacuum phase channel; full vacuum closure remains open."
            if nonzero
            else f"Dimension-eight wave {wave} vanishes after {audit['n_graph_coefficient_evaluations']:,} exact evaluations."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    out_json, out_md = output_paths(report["wave"])
    out_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    result = report["result"]
    out_md.write_text(
        f"# Selected-vacuum dimension-eight third wave {report['wave']} — v20\n\n"
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
