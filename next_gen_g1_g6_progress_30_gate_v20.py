#!/usr/bin/env python3
"""Consolidated 30-subproblem extension of the v20 G1/G6 progress gate.

This layer preserves the authoritative 26-subproblem certificate and adds the
exact portal norm-square contraction and its Nambu insertion. The complete
invariant census closes G1 while G6 remains PARTIAL.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import numpy as np

import exact_portal_norm_square_triplet_channel_v20 as exact_c
import next_gen_g1_g6_progress_gate_v20 as base_gate
import next_gen_triplet_portal_norm_square_gate_v20 as insertion

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "NEXT_GEN_G1_G6_PROGRESS_30_GATE_V20.json"
OUT_MD = ROOT / "NEXT_GEN_G1_G6_PROGRESS_30_GATE_V20.md"


def build_report() -> dict[str, Any]:
    base = base_gate.build_report()
    exact = exact_c.build_report()
    inserted = insertion.build_report()
    execution_failures = []
    for name, report in (("base26", base), ("exact_contract", exact), ("insertion", inserted)):
        if report.get("n_failed", 1) != 0:
            execution_failures.append(f"{name}: {report.get('failures')}")

    closed = dict(base["closed_subproblems"])
    closed.update(
        {
            "exact_CPhi_dagger_CPhi_triplet_block": exact["newly_closed_subproblem"][
                "exact_CPhi_dagger_CPhi_triplet_block"
            ],
            "exact_t2bar_t4bar_quartic_mixing": exact["newly_closed_subproblem"][
                "exact_t2bar_t4bar_quartic_mixing"
            ],
            "positive_semidefinite_rank_structure": exact["newly_closed_subproblem"][
                "positive_semidefinite_rank_structure"
            ],
            "CCdag_CdagC_spectrum_match": exact["newly_closed_subproblem"][
                "CCdag_CdagC_spectrum_match"
            ],
        }
    )
    structure = copy.deepcopy(base["authoritative_triplet_structure"])
    structure["exact_portal_norm_square"] = {
        "operator": "lambda_PhiSigma_C ||C_Phi Sigma||^2",
        "x_minus": "p-a/sqrt(3)",
        "x_plus": "p+a/sqrt(3)",
        "y": "2omega/sqrt(3)",
        "t2_shift": "lambda_C x_minus^2",
        "t2bar_t4bar_block": (
            "lambda_C [[x_plus^2,x_plus*y],[x_plus*y,y^2]]"
        ),
        "positive_sector_rank": 1,
        "positive_semidefinite_for_lambda_C_nonnegative": True,
    }
    blockers = dict(base["remaining_blockers"])
    blockers.pop("higher_210dag210_126bardag126bar_tensor_Clebsches", None)
    blockers["other_independent_PhiSigma_irrep_contractions"] = True

    checks = {
        "all_upstreams_execute": not execution_failures,
        "base_26_closed": base["n_closed_subproblems"] == 26,
        "all_30_recorded_subproblems_closed": len(closed) == 30 and all(closed.values()),
        "exact_contract_closed": exact["flag"]["exact_portal_norm_square_channel_closed"],
        "quartic_mixing_inserted": inserted["flag"][
            "exact_quartic_t2bar_t4bar_mixing_inserted"
        ],
        "rank_one_block": inserted["benchmark"]["exact_contribution"][
            "positive_sector_rank"
        ]
        == 1,
        "G1_closed": base["gate_states"]["G1"] == "CLOSED",
        "G6_still_partial": base["gate_states"]["G6"] == "PARTIAL",
        "physical_spectrum_still_open": not inserted["flag"][
            "physical_triplet_spectrum_complete"
        ],
        "unique_lifetime_still_open": not inserted["flag"][
            "exact_unique_proton_lifetime"
        ],
        "whole_model_not_validated": not inserted["flag"]["whole_model_validated"],
        "whole_model_not_excluded": not inserted["flag"]["whole_model_excluded"],
        "empirical_discovery_false": not inserted["flag"]["empirical_discovery"],
    }
    failures = execution_failures + [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "NEXT_GEN_G1_G6_PROGRESS_30_VERIFIED__FULL_THEORY_STILL_BLOCKED"
            if not failures
            else "NEXT_GEN_G1_G6_PROGRESS_30_GATE_FAILED"
        ),
        "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "gate_states": base["gate_states"],
        "closed_subproblems": closed,
        "n_closed_subproblems": len(closed),
        "remaining_blockers": blockers,
        "n_remaining_blockers": sum(bool(value) for value in blockers.values()),
        "authoritative_triplet_structure": structure,
        "upstream_status": {
            "base26": base["status"],
            "exact_contract": exact["status"],
            "insertion": inserted["status"],
        },
        "next_exact_target": (
            "Derive the remaining independent Phi-Sigma irrep contractions, "
            "project 10dag10·126bardag126bar around DeltaR and hEW, and build "
            "all mixing-relevant 210 component states."
        ),
        "flag": {
            "authoritative_next_gen_G1_G6_progress_30_gate": True,
            "all_recorded_exact_subproblems_closed": not failures,
            "exact_portal_norm_square_channel_closed": not failures,
            "exact_quartic_t2bar_t4bar_mixing_inserted": not failures,
            "G1_closed": base["gate_states"]["G1"] == "CLOSED",
            "G6_closed": False,
            "physical_triplet_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "Thirty triplet tensor/quadratic subproblems are now exact. The "
            "Hermitian Phi-H family 1+45+54 is complete, the Hermitian 126bar "
            "54 is absent, the 126bar 45 currents are exact, and the first "
            "higher Phi-Sigma contraction fixes a positive-semidefinite rank-one "
            "t2bar/t4bar quartic block. The invariant census closes G1; G6 "
            "remains unclosed pending the physical triplet spectrum."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join([
        "# Next-generation G1/G6 30-subproblem progress gate — v20", "",
        f"**Status:** `{report['status']}`", "", report["verdict"], "",
        f"- Exact subproblems closed: {report['n_closed_subproblems']}",
        f"- Remaining blockers: {report['n_remaining_blockers']}",
        f"- G1: `{report['gate_states']['G1']}`",
        f"- G6: `{report['gate_states']['G6']}`", "",
        f"**Next target:** {report['next_exact_target']}", "",
    ])


def _json_default(obj: Any) -> Any:
    if isinstance(obj, np.bool_): return bool(obj)
    if isinstance(obj, np.integer): return int(obj)
    if isinstance(obj, np.floating): return float(obj)
    if isinstance(obj, np.ndarray): return obj.tolist()
    if isinstance(obj, complex): return {"re": float(obj.real), "im": float(obj.imag)}
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    payload = json.dumps(report, indent=2, default=_json_default) + "\n"
    OUT_JSON.write_text(payload, encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(payload, end="")
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
