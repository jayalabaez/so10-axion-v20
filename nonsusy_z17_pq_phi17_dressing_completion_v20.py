#!/usr/bin/env python3
"""Historical Option-C/no-X overlay for Phi17 dressing families.

All added holomorphic Phi17 dressings are forbidden by the manuscript's
gauged U(1)_X. This module preserves the archived no-X inventory only and is
not an authoritative catalogue for the live theory.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import exact_phi17_neutral_dressing_completion_v20 as closure
import nonsusy_z17_pq_hsigma_completion_v20 as base
import nonsusy_z17_pq_potential_filter_v20 as filter_core

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "NONSUSY_Z17_PQ_PHI17_DRESSING_COMPLETION_V20.json"
OUT_MD = ROOT / "NONSUSY_Z17_PQ_PHI17_DRESSING_COMPLETION_V20.md"
MODEL_CONTRACT_ID = "historical_option_c_no_x_v20"


def _entry(row: dict[str, Any], *, require_x: bool) -> dict[str, Any]:
    return filter_core._entry(
        row["name"],
        dict(row["counts"]),
        int(row["dim"]),
        True,
        feeds_triplet_mass=True,
        note=(
            row["role"]
            + "; exact neutral-Phi17 dressing theorem; no new SO(10) Clebsch"
        ),
        require_x=require_x,
    ) | {
        "multiplicity": int(row["multiplicity"]),
        "core": row["core"],
        "completion_source": "exact_phi17_neutral_dressing_completion_v20",
    }


def operator_catalogue(*, require_x: bool) -> list[dict[str, Any]]:
    """Build the overlay under an explicitly selected X-charge policy."""
    rows = [dict(row) for row in base.operator_catalogue(require_x=require_x)]
    names = {row["name"] for row in rows}
    for addition in closure.ADDITIONS:
        if addition["name"] not in names:
            rows.append(_entry(addition, require_x=require_x))
            names.add(addition["name"])
    return rows


def build_report() -> dict[str, Any]:
    exact = closure.build_report()
    option_c = operator_catalogue(require_x=False)
    manuscript = operator_catalogue(require_x=True)
    base_names = {row["name"] for row in base.operator_catalogue(require_x=False)}
    option_c_by_name = {row["name"]: row for row in option_c}
    manuscript_by_name = {row["name"]: row for row in manuscript}
    additions = [row for row in option_c if row["name"] not in base_names]
    expected = {row["name"] for row in closure.ADDITIONS}

    checks = {
        "exact_theorem_executes": exact["n_failed"] == 0,
        "seven_classes_appended": len(additions) == 7,
        "appended_names_exact": {row["name"] for row in additions} == expected,
        "every_required_dressing_present_once": all(
            sum(row["name"] == name for row in option_c) == 1
            for name in closure.required_dressing_names()
        ),
        "all_new_classes_option_c_no_x_allowed": all(
            option_c_by_name[name]["status"] == "ALLOWED" for name in expected
        ),
        "all_new_classes_manuscript_u1x_forbidden": all(
            manuscript_by_name[name]["status"] == "CHARGE_FORBIDDEN"
            for name in expected
        ),
        "full_ring_not_claimed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "model_contract_id": MODEL_CONTRACT_ID,
        "authoritative_for_manuscript": False,
        "model_wide_no_go_certified": False,
        "status": (
            "HISTORICAL_OPTION_C_PHI17_OVERLAY_REPRODUCED__NONAUTHORITATIVE"
            if not failures
            else "HISTORICAL_OPTION_C_PHI17_OVERLAY_REPRODUCTION_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "base_count": len(base_names),
        "completed_count": len(option_c),
        "appended": additions,
        "required_dressing_names": sorted(closure.required_dressing_names()),
        "effective_coefficient_map": exact["effective_coefficient_map"],
        "flags": {
            "historical_option_c_Phi17_overlay_reproduced": not failures,
            "historical_all_fifteen_dressings_registered": not failures,
            "historical_seven_missing_classes_appended": not failures,
            "historical_no_new_SO10_Clebsches": not failures,
            "phi17_dressings_allowed_by_manuscript_u1x": False,
            "authoritative_for_manuscript": False,
            "model_wide_no_go_certified": False,
            "complete_mixed_invariant_ring": False,
            "complete_component_potential": False,
            "full_multifield_vacuum": False,
            "whole_model_validated": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "This overlay reproduces all 15 historical Option-C/no-X Phi17 "
            "dressings and appends the seven missing entries exactly once. "
            "The added holomorphic dressings are forbidden by the manuscript's "
            "gauged U(1)_X, so this is not a live G1 catalogue or closure."
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
            "# Historical Option-C Phi17 dressing catalogue overlay\n\n"
            f"**Status:** `{report['status']}`\n\n"
            + report["verdict"]
            + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
