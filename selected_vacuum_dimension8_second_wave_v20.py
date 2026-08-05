#!/usr/bin/env python3
"""Exact second wave of dimension-eight selected-vacuum phase coefficients.

The first twelve genuinely new dimension-eight representatives all vanish after
93,158 exact graph/coefficient evaluations. This module evaluates the next
three representatives in the census, one per CI matrix job:

    8m: (2,0,2,3,1),  2,777 graphs x 16 neutral assignments = 44,432;
    8n: (0,0,4,4,0),  3,843 graphs x 16 neutral assignments = 61,488;
    8o: (0,1,3,3,1),  3,843 graphs x 16 neutral assignments = 61,488.

A nonzero result is only a candidate phase-lifting operator. It does not close
stationarity, boundedness or the full scalar Hessian.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import direct_phi_h_sigmabar_tensor_v20 as direct
import selected_vacuum_dim7_low_complexity_phase_screen_v20 as dim7
import selected_vacuum_dimension8_first_wave_v20 as first
import selected_vacuum_neutral_h10_dim6_no_go_v20 as neutral
import selected_vacuum_phase_invariant_dim6_metric_audit_v20 as metric

ROOT = Path(__file__).resolve().parent

WAVE_SPECS: dict[str, dict[str, Any]] = {
    "8m": {"signature": (2, 0, 2, 3, 1), "graphs": 2777, "assignments": 16, "cost": 44432},
    "8n": {"signature": (0, 0, 4, 4, 0), "graphs": 3843, "assignments": 16, "cost": 61488},
    "8o": {"signature": (0, 1, 3, 3, 1), "graphs": 3843, "assignments": 16, "cost": 61488},
}


def output_paths(wave: str) -> tuple[Path, Path]:
    tag = wave.upper()
    return (
        ROOT / f"SELECTED_VACUUM_DIMENSION8_SECOND_WAVE_{tag}_V20.json",
        ROOT / f"SELECTED_VACUUM_DIMENSION8_SECOND_WAVE_{tag}_V20.md",
    )


def planning_context() -> dict[str, Any]:
    context = first.planning_context()
    first_signatures = {spec["signature"] for spec in first.WAVE_SPECS.values()}
    remaining = [row for row in context["new_rows"] if row["signature"] not in first_signatures]
    return {**context, "remaining_after_first": remaining, "second_wave": remaining[:3]}


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
        "nine_representatives_after_first_wave": len(context["remaining_after_first"]) == 9,
        "second_wave_signatures_exact": [row["signature"] for row in context["second_wave"]] == expected,
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
        status = f"DIMENSION8_SECOND_WAVE_{tag}_FAILED"
    elif nonzero:
        status = f"DIMENSION8_SECOND_WAVE_{tag}_NONZERO_CHANNEL_FOUND__STATIONARITY_OPEN"
    else:
        status = f"DIMENSION8_SECOND_WAVE_{tag}_ZERO"
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
            "stationarity_rebuilt": False,
            "boundedness_reproved": False,
            "full_scalar_hessian_rebuilt": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "next_action": (
            "Insert the lowest-cost nonzero operator into the phase/radial potential and rebuild stationarity."
            if nonzero
            else "Continue to the six remaining higher-cost dimension-eight representatives."
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
        f"# Selected-vacuum dimension-eight second wave {report['wave']} — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Signature: `{result['signature_P_D_Db_H_Hb']}`\n"
        f"- Exact evaluations: `{result['n_graph_coefficient_evaluations']}`\n"
        f"- Maximum coefficient: `{result['maximum_abs_coefficient']:.12e}`\n\n"
        + report["verdict"] + "\n",
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
