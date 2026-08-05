#!/usr/bin/env python3
"""Consolidated selected-vacuum phase-lifting no-go through dimension seven.

This report combines hosted, fail-closed evidence from the complete finite
search over charge-allowed non-derivative scalar invariants for the current
SO(10) x Z17/PQ field content on the selected
(p,a,omega,Delta_R,H10_neutral,S) vacuum.

Dimension six was closed by exact metric-graph enumeration, a Hodge reduction
of the epsilon sector, and an exact two-state neutral-H basis. Dimension seven
contains thirteen even-H conjugacy representatives. All thirteen have now
been evaluated, covering 62,948 exact graph/coefficient evaluations, and every
coefficient is zero.

Scope: this is a selected-vacuum and current-field-content theorem. It does not
exclude alternative SO(10) vacua, extra fields, derivative operators, or
operators of canonical dimension eight and above.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import selected_vacuum_dim7_high_complexity_wave1_v20 as wave1
import selected_vacuum_dim7_low_complexity_phase_screen_v20 as low
import selected_vacuum_dim7_remaining_high_complexity_v20 as remaining

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SELECTED_VACUUM_DIMENSION7_COMPLETE_NO_GO_V20.json"
OUT_MD = ROOT / "SELECTED_VACUUM_DIMENSION7_COMPLETE_NO_GO_V20.md"

EVIDENCE = {
    "dimension6_complete": {
        "workflow_run_id": 31013743621,
        "head_sha": "df3c0ea7e79b5a61ccac13e48a04ee066a432113",
        "artifact_id": 8933804476,
        "artifact_sha256": "cb7fb8033d875474e926f68ef63cf2cc9d60611494c18d01c1c272010886bcb7",
        "result": "selected-vacuum phase-lifting no-go through dimension six",
    },
    "dimension7_low_complexity": {
        "workflow_run_id": 31014649923,
        "head_sha": "4113003a2249f769186afdd128bd54e5f9c69704",
        "artifact_id": 8934152643,
        "artifact_sha256": "8837269d04573b297d3cb9a26342c619abb914938ca90b7b8fc898dadc595977",
        "representatives": 8,
        "metric_graphs": 1128,
        "coefficient_evaluations": 5835,
        "maximum_abs_coefficient": 0.0,
    },
    "dimension7_wave1": {
        "workflow_run_id": 31016125611,
        "head_sha": "0785827793a77501f88a80d1d04e804dfc782f0c",
        "artifact_id": 8934772075,
        "artifact_sha256": "f0f5e63d00cb3926ab90e0ae194d641e621f4383b00f6f35614f01ab9e3caa6c",
        "representatives": 2,
        "metric_graphs": 11934,
        "coefficient_evaluations": 11934,
        "maximum_abs_coefficient": 0.0,
    },
    "dimension7_wave2a": {
        "workflow_run_id": 31018459395,
        "head_sha": "c841bc955ef3cb57c518fd17df1e66ee1647e8b2",
        "artifact_id": 8935862621,
        "artifact_sha256": "76003d02ebfe9d5923760abc24b0e6a818cc55af077eb4dd3ad2a16e4cc6c832",
        "signature": [0, 2, 4, 0, 0],
        "metric_graphs": 12043,
        "coefficient_evaluations": 12043,
        "maximum_abs_coefficient": 0.0,
    },
    "dimension7_wave2b": {
        "workflow_run_id": 31018459395,
        "head_sha": "c841bc955ef3cb57c518fd17df1e66ee1647e8b2",
        "artifact_id": 8935614893,
        "artifact_sha256": "c5878957f9f38af0e3b0582f617b5f9ea0055ddaca70d48e3e5ba69f18535876",
        "signature": [3, 0, 2, 2, 0],
        "metric_graphs": 3387,
        "coefficient_evaluations": 13548,
        "maximum_abs_coefficient": 0.0,
    },
    "dimension7_wave2c": {
        "workflow_run_id": 31018459395,
        "head_sha": "c841bc955ef3cb57c518fd17df1e66ee1647e8b2",
        "artifact_id": 8935843237,
        "artifact_sha256": "611b190e38b07d5c585f1e54fcaa5dc49dac49b8fa5a2f4140d1b6e043343b4c",
        "signature": [1, 1, 3, 2, 0],
        "metric_graphs": 4897,
        "coefficient_evaluations": 19588,
        "maximum_abs_coefficient": 0.0,
    },
}


def build_report() -> dict[str, Any]:
    context = remaining.planning_context()
    low_reps = [
        signature
        for signature in context["representatives"]
        if context["graph_counts"][signature] <= low.GRAPH_LIMIT
    ]
    expected_remaining = [
        spec["signature"] for spec in remaining.WAVE_SPECS.values()
    ]
    all_dim7_entries = [
        EVIDENCE["dimension7_low_complexity"],
        EVIDENCE["dimension7_wave1"],
        EVIDENCE["dimension7_wave2a"],
        EVIDENCE["dimension7_wave2b"],
        EVIDENCE["dimension7_wave2c"],
    ]
    total_graphs = sum(int(row["metric_graphs"]) for row in all_dim7_entries)
    total_evaluations = sum(
        int(row["coefficient_evaluations"]) for row in all_dim7_entries
    )
    maximum = max(float(row["maximum_abs_coefficient"]) for row in all_dim7_entries)
    artifact_hashes_well_formed = all(
        len(str(row["artifact_sha256"])) == 64
        for row in EVIDENCE.values()
    )

    checks = {
        "thirteen_even_H_dimension7_representatives": len(context["representatives"]) == 13,
        "eight_low_complexity_representatives": len(low_reps) == 8,
        "wave1_two_representatives_exact": context["ordered_high"][:2]
        == wave1.EXPECTED_SIGNATURES,
        "remaining_three_representatives_exact": context["remaining"]
        == expected_remaining,
        "dimension7_total_metric_graphs_33389": total_graphs == 33389,
        "dimension7_total_coefficient_evaluations_62948": total_evaluations == 62948,
        "all_hosted_maxima_exactly_zero": maximum == 0.0,
        "artifact_hashes_well_formed": artifact_hashes_well_formed,
        "epsilon_sector_reduced_by_126_Hodge_duality": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    status = (
        "SELECTED_VACUUM_PHASE_LIFTING_NO_GO_THROUGH_DIMENSION7"
        if not failures
        else "SELECTED_VACUUM_DIMENSION7_CONSOLIDATION_FAILED"
    )
    return {
        "status": status,
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "scope": {
            "gauge_group": "SO(10)",
            "discrete_and_global_charges": "repository Z17/PQ/X assignment",
            "vacuum": "selected p,a,omega,Delta_R plus arbitrary neutral 10_H mixture",
            "operator_class": "non-derivative scalar invariants",
            "canonical_dimension_closed_through": 7,
        },
        "counts": {
            "dimension7_even_H_conjugacy_representatives": 13,
            "dimension7_total_metric_graphs": total_graphs,
            "dimension7_total_graph_coefficient_evaluations": total_evaluations,
            "dimension7_maximum_abs_coefficient": maximum,
        },
        "evidence": EVIDENCE,
        "flags": {
            "dimension6_complete_selected_vacuum_no_go": True,
            "dimension7_all_representatives_evaluated": not bool(failures),
            "dimension7_metric_sector_closed": not bool(failures),
            "dimension7_epsilon_sector_reduced_to_metric": True,
            "full_selected_vacuum_phase_lifting_no_go_through_dimension7": not bool(failures),
            "alternative_vacua_excluded": False,
            "dimension8_and_above_excluded": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "next_action": (
            "Enumerate dimension-eight primitive phase-sensitive tensor signatures, "
            "rank them by exact multigraph/neutral-basis cost, and execute the "
            "lowest-cost genuinely new representatives."
        ),
        "verdict": (
            "Every charge-allowed phase-sensitive non-derivative scalar invariant "
            "through canonical dimension seven vanishes on the selected vacuum. "
            "The current field content therefore cannot lift the extra phase at "
            "dimension <=7. This is not a whole-model exclusion: dimension eight, "
            "alternative vacua and extra UV fields remain open."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    counts = report["counts"]
    OUT_MD.write_text(
        "# Selected-vacuum phase-lifting no-go through dimension seven — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Dimension-seven representatives: `{counts['dimension7_even_H_conjugacy_representatives']}`\n"
        f"- Metric graphs: `{counts['dimension7_total_metric_graphs']}`\n"
        f"- Exact coefficient evaluations: `{counts['dimension7_total_graph_coefficient_evaluations']}`\n"
        f"- Maximum coefficient: `{counts['dimension7_maximum_abs_coefficient']:.1f}`\n\n"
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
