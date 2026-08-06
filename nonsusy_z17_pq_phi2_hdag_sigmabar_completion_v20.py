#!/usr/bin/env python3
"""Canonical catalogue overlay for the exact 210^2 Hdag 126bar family."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import exact_phi2_hdag_sigmabar_two_channel_family_v20 as closure
import nonsusy_z17_pq_phi17_dressing_completion_v20 as base
import nonsusy_z17_pq_potential_filter_v20 as filter_core

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "NONSUSY_Z17_PQ_PHI2_HDAG_SIGMABAR_COMPLETION_V20.json"
OUT_MD = ROOT / "NONSUSY_Z17_PQ_PHI2_HDAG_SIGMABAR_COMPLETION_V20.md"


def operator_catalogue(*, require_x: bool = False) -> list[dict[str, Any]]:
    rows = [dict(row) for row in base.operator_catalogue(require_x=require_x)]
    names = {row["name"] for row in rows}
    if closure.OPERATOR not in names:
        totals = filter_core._total_charge(closure.COUNTS)
        rows.append(
            filter_core._entry(
                closure.OPERATOR,
                dict(closure.COUNTS),
                4,
                True,
                feeds_triplet_mass=True,
                note=(
                    "exact multiplicity-two 210/1050bar family with explicit "
                    "factorial-reduced channel-A and channel-B tensors"
                ),
                require_x=require_x,
            )
            | {
                "multiplicity": 2,
                "channel_names": ["A_210", "B_1050bar_basis"],
                "completion_source": (
                    "exact_phi2_hdag_sigmabar_two_channel_family_v20"
                ),
                "selected_vacuum_HPhi_ranks": [3, 4],
            }
        )
    return rows


def build_report() -> dict[str, Any]:
    exact = closure.build_report()
    rows = operator_catalogue(require_x=False)
    historical = operator_catalogue(require_x=True)
    matches = [row for row in rows if row["name"] == closure.OPERATOR]
    historical_match = next(
        row for row in historical if row["name"] == closure.OPERATOR
    )
    checks = {
        "exact_family_executes": exact["n_failed"] == 0,
        "operator_registered_once": len(matches) == 1,
        "multiplicity_two_preserved": (
            len(matches) == 1 and matches[0].get("multiplicity") == 2
        ),
        "two_coefficients_named": (
            len(matches) == 1 and len(matches[0].get("channel_names", [])) == 2
        ),
        "declared_contract_allowed": (
            len(matches) == 1 and matches[0]["status"] == "ALLOWED"
        ),
        "historical_X_also_allowed": historical_match["status"] == "ALLOWED",
        "selected_HPhi_ranks_recorded": (
            len(matches) == 1
            and matches[0]["selected_vacuum_HPhi_ranks"] == [3, 4]
        ),
        "complete_tensor_G1_not_claimed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "PHI2_HDAG_SIGMABAR_MULTIPLICITY_TWO_REGISTERED__G1_OPEN"
            if not failures
            else "PHI2_HDAG_SIGMABAR_CATALOGUE_COMPLETION_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "operator_entry": matches[0] if len(matches) == 1 else None,
        "completed_catalogue_count": len(rows),
        "flags": {
            "multiplicity_two_operator_registered": not failures,
            "two_independent_coefficients_preserved": not failures,
            "selected_HPhi_blocks_propagated": not failures,
            "complete_mixed_tensor_basis": False,
            "complete_component_potential": False,
            "full_multifield_vacuum": False,
            "whole_model_validated": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "The exact 210^2 Hdag 126bar multidegree is registered once with "
            "multiplicity two and two independent coefficients. Downstream G2 "
            "must retain both rank-3/rank-4 H--210 mixed blocks."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        OUT_MD.write_text(
            "# 210² H† 126bar catalogue completion\n\n"
            f"**Status:** `{report['status']}`\n\n"
            + report["verdict"]
            + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
