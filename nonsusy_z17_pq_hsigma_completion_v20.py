#!/usr/bin/env python3
"""Historical Option-C/no-X catalogue overlay for H--Sigma families.

The historical base filter is preserved for provenance. This module appends
exactly once the three renormalizable classes proved by
``exact_hsigma_holomorphic_charge_dressed_completion_v20`` and exposes the
counterfactual catalogue used by archived no-X calculations. Two appended
Phi17 dressings are forbidden by the manuscript's gauged U(1)_X, so this is
not a live catalogue and must not be used for authoritative G1/G2 work.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import exact_hsigma_holomorphic_charge_dressed_completion_v20 as closure
import nonsusy_z17_pq_potential_filter_v20 as base

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "NONSUSY_Z17_PQ_HSIGMA_COMPLETION_V20.json"
OUT_MD = ROOT / "NONSUSY_Z17_PQ_HSIGMA_COMPLETION_V20.md"
MODEL_CONTRACT_ID = "historical_option_c_no_x_v20"


def _completed_entry(row: dict[str, Any], *, require_x: bool) -> dict[str, Any]:
    return base._entry(
        row["name"],
        dict(row["counts"]),
        int(row["dim"]),
        True,
        feeds_triplet_mass=True,
        note=(
            row["so10"]
            + "; exact tensor and selected-vacuum audit in "
            "exact_hsigma_holomorphic_charge_dressed_completion_v20"
        ),
        require_x=require_x,
    ) | {
        "multiplicity": int(row["multiplicity"]),
        "coefficient": row["coefficient"],
        "completion_source": "exact_hsigma_holomorphic_charge_dressed_completion_v20",
    }


def operator_catalogue(*, require_x: bool) -> list[dict[str, Any]]:
    """Build the overlay under an explicitly selected X-charge policy."""
    rows = [dict(row) for row in base.operator_catalogue(require_x=require_x)]
    names = {row["name"] for row in rows}
    for addition in closure.ADDITIONS:
        if addition["name"] not in names:
            rows.append(_completed_entry(addition, require_x=require_x))
            names.add(addition["name"])
    return rows


def build_report() -> dict[str, Any]:
    exact = closure.build_report()
    option_c = operator_catalogue(require_x=False)
    manuscript = operator_catalogue(require_x=True)
    base_names = {row["name"] for row in base.operator_catalogue(require_x=False)}
    option_c_by_name = {row["name"]: row for row in option_c}
    manuscript_by_name = {row["name"]: row for row in manuscript}
    added = [row for row in option_c if row["name"] not in base_names]

    checks = {
        "exact_closure_executes": exact["n_failed"] == 0,
        "three_classes_appended": len(added) == 3,
        "all_three_present_once": all(
            sum(row["name"] == name for row in option_c) == 1
            for name in (closure.O54, closure.OPLUS, closure.OMINUS)
        ),
        "all_three_option_c_no_x_allowed": all(
            option_c_by_name[name]["status"] == "ALLOWED"
            for name in (closure.O54, closure.OPLUS, closure.OMINUS)
        ),
        "O54_manuscript_u1x_allowed": (
            manuscript_by_name[closure.O54]["status"] == "ALLOWED"
        ),
        "dressed_terms_manuscript_u1x_forbidden": (
            manuscript_by_name[closure.OPLUS]["status"] == "CHARGE_FORBIDDEN"
            and manuscript_by_name[closure.OMINUS]["status"] == "CHARGE_FORBIDDEN"
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
            "HISTORICAL_OPTION_C_HSIGMA_OVERLAY_REPRODUCED__NONAUTHORITATIVE"
            if not failures
            else "HISTORICAL_OPTION_C_HSIGMA_OVERLAY_REPRODUCTION_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "base_count": len(base_names),
        "completed_count": len(option_c),
        "appended": added,
        "operator_names": [row["name"] for row in option_c],
        "flags": {
            "historical_option_c_hsigma_overlay_reproduced": not failures,
            "historical_three_families_registered": not failures,
            "phi17_dressed_families_allowed_by_manuscript_u1x": False,
            "authoritative_for_manuscript": False,
            "model_wide_no_go_certified": False,
            "historical_base_preserved_for_provenance": True,
            "complete_mixed_invariant_ring": False,
            "complete_component_potential": False,
            "whole_model_validated": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "This overlay reproduces the historical Option-C/no-X catalogue. "
            "Its U(1)_X-neutral O54 entry remains mathematically reusable, but "
            "both Phi17-dressed entries are gauge-forbidden in the manuscript. "
            "The overlay is non-authoritative and must not close live G1 or G2."
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
            "# Historical Option-C H–Sigma catalogue overlay\n\n"
            f"**Status:** `{report['status']}`\n\n"
            + report["verdict"]
            + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
