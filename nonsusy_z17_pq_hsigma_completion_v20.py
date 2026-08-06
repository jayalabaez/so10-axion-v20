#!/usr/bin/env python3
"""Canonical declared-symmetry catalogue overlay for the closed H--Sigma families.

The historical base filter is preserved for provenance.  This module appends
exactly once the three renormalizable classes proved by
``exact_hsigma_holomorphic_charge_dressed_completion_v20`` and exposes the
completed catalogue for downstream G2 work.
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


def operator_catalogue(*, require_x: bool = False) -> list[dict[str, Any]]:
    rows = [dict(row) for row in base.operator_catalogue(require_x=require_x)]
    names = {row["name"] for row in rows}
    for addition in closure.ADDITIONS:
        if addition["name"] not in names:
            rows.append(_completed_entry(addition, require_x=require_x))
            names.add(addition["name"])
    return rows


def build_report() -> dict[str, Any]:
    exact = closure.build_report()
    declared = operator_catalogue(require_x=False)
    historical = operator_catalogue(require_x=True)
    base_names = {row["name"] for row in base.operator_catalogue(require_x=False)}
    by_name = {row["name"]: row for row in declared}
    historical_by_name = {row["name"]: row for row in historical}
    added = [row for row in declared if row["name"] not in base_names]

    checks = {
        "exact_closure_executes": exact["n_failed"] == 0,
        "three_classes_appended": len(added) == 3,
        "all_three_present_once": all(
            sum(row["name"] == name for row in declared) == 1
            for name in (closure.O54, closure.OPLUS, closure.OMINUS)
        ),
        "all_three_declared_allowed": all(
            by_name[name]["status"] == "ALLOWED"
            for name in (closure.O54, closure.OPLUS, closure.OMINUS)
        ),
        "O54_historical_X_allowed": (
            historical_by_name[closure.O54]["status"] == "ALLOWED"
        ),
        "dressed_terms_historical_X_forbidden": (
            historical_by_name[closure.OPLUS]["status"] == "CHARGE_FORBIDDEN"
            and historical_by_name[closure.OMINUS]["status"] == "CHARGE_FORBIDDEN"
        ),
        "full_ring_not_claimed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "DECLARED_HSIGMA_CATALOGUE_COMPLETION_READY__FULL_RING_OPEN"
            if not failures
            else "DECLARED_HSIGMA_CATALOGUE_COMPLETION_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "base_count": len(base_names),
        "completed_count": len(declared),
        "appended": added,
        "operator_names": [row["name"] for row in declared],
        "flags": {
            "canonical_hsigma_completion_overlay_emitted": not failures,
            "three_closed_families_registered": not failures,
            "historical_base_preserved_for_provenance": True,
            "complete_mixed_invariant_ring": False,
            "complete_component_potential": False,
            "whole_model_validated": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "The declared-symmetry catalogue is completed for the remaining "
            "renormalizable H10--126bar holomorphic and Phi17-dressed classes. "
            "The historical base ledger is preserved; downstream work should "
            "use this overlay. Full G1 remains open."
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
            "# Declared H–Sigma catalogue completion\n\n"
            f"**Status:** `{report['status']}`\n\n"
            + report["verdict"]
            + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
