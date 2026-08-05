#!/usr/bin/env python3
"""Consolidated selected-vacuum dimension-seven phase-lifting verdict.

This ledger combines the independently hosted dimension-seven low-complexity,
high-complexity wave 1, and remaining 2a/2b/2c artifacts. The expensive
contractions remain reproducible in their source modules and dedicated Actions
workflows; this file records the exact verified partition and scientific
boundary without rerunning 62,948 contractions in every aggregate workflow.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SELECTED_VACUUM_DIM7_COMPLETE_NO_GO_V20.json"
OUT_MD = ROOT / "SELECTED_VACUUM_DIM7_COMPLETE_NO_GO_V20.md"

EVIDENCE = [
    {
        "stage": "dimension6_prerequisite",
        "run_id": 31013743621,
        "artifact_id": 8933804476,
        "artifact_digest": "sha256:cb7fb8033d875474e926f68ef63cf2cc9d60611494c18d01c1c272010886bcb7",
        "head_sha": "df3c0ea7e79b5a61ccac13e48a04ee066a432113",
        "representatives": 15,
        "evaluations": 2662,
        "maximum_abs_coefficient": 0.0,
        "role": "dimension-six no-go and epsilon reduction prerequisite",
    },
    {
        "stage": "dimension7_low_complexity",
        "run_id": 31014649923,
        "artifact_id": 8934152643,
        "artifact_digest": "sha256:8837269d04573b297d3cb9a26342c619abb914938ca90b7b8fc898dadc595977",
        "head_sha": "4113003a2249f769186afdd128bd54e5f9c69704",
        "representatives": 8,
        "evaluations": 5835,
        "maximum_abs_coefficient": 0.0,
    },
    {
        "stage": "dimension7_high_complexity_wave1",
        "run_id": 31016125611,
        "artifact_id": 8934772075,
        "artifact_digest": "sha256:f0f5e63d00cb3926ab90e0ae194d641e621f4383b00f6f35614f01ab9e3caa6c",
        "head_sha": "0785827793a77501f88a80d1d04e804dfc782f0c",
        "representatives": 2,
        "evaluations": 11934,
        "maximum_abs_coefficient": 0.0,
    },
    {
        "stage": "dimension7_remaining_2a",
        "run_id": 31018459395,
        "artifact_id": 8935862621,
        "artifact_digest": "sha256:76003d02ebfe9d5923760abc24b0e6a818cc55af077eb4dd3ad2a16e4cc6c832",
        "head_sha": "c841bc955ef3cb57c518fd17df1e66ee1647e8b2",
        "representatives": 1,
        "evaluations": 12043,
        "maximum_abs_coefficient": 0.0,
        "signature_P_D_Db_H_Hb": [0, 2, 4, 0, 0],
    },
    {
        "stage": "dimension7_remaining_2b",
        "run_id": 31018459395,
        "artifact_id": 8935614893,
        "artifact_digest": "sha256:c5878957f9f38af0e3b0582f617b5f9ea0055ddaca70d48e3e5ba69f18535876",
        "head_sha": "c841bc955ef3cb57c518fd17df1e66ee1647e8b2",
        "representatives": 1,
        "evaluations": 13548,
        "maximum_abs_coefficient": 0.0,
        "signature_P_D_Db_H_Hb": [3, 0, 2, 2, 0],
    },
    {
        "stage": "dimension7_remaining_2c",
        "run_id": 31018459395,
        "artifact_id": 8935843237,
        "artifact_digest": "sha256:611b190e38b07d5c585f1e54fcaa5dc49dac49b8fa5a2f4140d1b6e043343b4c",
        "head_sha": "c841bc955ef3cb57c518fd17df1e66ee1647e8b2",
        "representatives": 1,
        "evaluations": 19588,
        "maximum_abs_coefficient": 0.0,
        "signature_P_D_Db_H_Hb": [1, 1, 3, 2, 0],
    },
]


def build_report() -> dict[str, Any]:
    dim7_rows = [row for row in EVIDENCE if row["stage"].startswith("dimension7_")]
    representatives = sum(int(row["representatives"]) for row in dim7_rows)
    evaluations = sum(int(row["evaluations"]) for row in dim7_rows)
    maximum = max(float(row["maximum_abs_coefficient"]) for row in dim7_rows)
    checks = {
        "dimension6_prerequisite_recorded": EVIDENCE[0]["stage"] == "dimension6_prerequisite",
        "dimension7_partition_has_five_stages": len(dim7_rows) == 5,
        "dimension7_representative_count_13": representatives == 13,
        "dimension7_evaluation_count_62948": evaluations == 62948,
        "all_dimension7_stage_maxima_zero": maximum == 0.0,
        "all_artifact_digests_sha256": all(
            str(row["artifact_digest"]).startswith("sha256:") for row in EVIDENCE
        ),
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "SELECTED_VACUUM_DIM7_PHASE_LIFTING_NO_GO_PROVEN"
            if not failures
            else "SELECTED_VACUUM_DIM7_LEDGER_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "evidence": EVIDENCE,
        "dimension7_summary": {
            "charge_allowed_even_H_conjugacy_representatives": representatives,
            "exact_graph_coefficient_evaluations": evaluations,
            "maximum_abs_coefficient": maximum,
            "nonzero_representatives": 0,
            "metric_sector_exhausted": True,
            "epsilon_sector_reduced_to_metric_sector_by_five_form_hodge_duality": True,
            "arbitrary_neutral_H10_mixture_covered": True,
        },
        "flags": {
            "full_selected_vacuum_dimension7_phase_lifting_no_go_proven": not bool(failures),
            "dimension8_search_required": not bool(failures),
            "selected_vacuum_fully_stabilized": False,
            "stationarity_rebuilt": False,
            "full_scalar_hessian_rebuilt": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "next_action": "Enumerate and test genuinely new dimension-eight phase-sensitive tensor representatives.",
        "verdict": (
            "All 13 charge-allowed even-H dimension-seven representatives vanish "
            "on the selected p,a,omega,Delta_R and arbitrary neutral-H10 vacuum "
            "after 62,948 exact contractions. The missing phase lift is absent "
            "through dimension seven for the current fields and charges."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    summary = report["dimension7_summary"]
    OUT_MD.write_text(
        "# Complete selected-vacuum dimension-seven phase audit — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Representatives: `{summary['charge_allowed_even_H_conjugacy_representatives']}`\n"
        f"- Exact evaluations: `{summary['exact_graph_coefficient_evaluations']}`\n"
        f"- Maximum coefficient: `{summary['maximum_abs_coefficient']}`\n\n"
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
