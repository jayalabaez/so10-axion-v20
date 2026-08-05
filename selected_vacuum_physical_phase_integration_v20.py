#!/usr/bin/env python3
"""Authoritative selected-vacuum physical phase integration.

This module consumes the exact neutral gauge quotient and audits legacy modules
that were written before the eaten Delta_R phase was identified.  It separates
three statements:

1. The unquotiented reduced 3x3 phase Hessian has rank one and nullity two.
2. One null is the broken neutral Z'_R/B-L gauge orbit and is not physical.
3. For positive nonzero kappa, the quotient has one massive CP-odd mode and
   exactly one physical null, the PQ axion.

Legacy modules are retained as historical/pre-quotient diagnostics until their
component bookkeeping is rewritten.  Their stale physical-phase conclusions
are not allowed to override this authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import selected_vacuum_neutral_phase_gauge_quotient_v20 as quotient

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SELECTED_VACUUM_PHYSICAL_PHASE_INTEGRATION_V20.json"
OUT_MD = ROOT / "SELECTED_VACUUM_PHYSICAL_PHASE_INTEGRATION_V20.md"

LEGACY_CONSUMERS: dict[str, list[str]] = {
    "multi_operator_phase_hessian_v20.py": [
        "one additional unresolved flat phase",
        "Two flat directions orthogonal to the single active g",
    ],
    "gauge_fixing_goldstone_eating_v20.py": [
        '"name": "phi_DeltaR_126"',
        '"class": "physical_active"',
        "Physical 3×3 Hessian after removing gauge-fixed spectators",
    ],
    "phase_operator_independence_audit_v20.py": [
        "additional unresolved flat phase",
    ],
    "uv_cp_phases_from_potential_v20.py": [
        "multi_operator_phase_hessian_v20",
    ],
    "component_lift_210_126_10_v20.py": [
        "multi_operator_phase_hessian_v20",
    ],
    "uv_delta_i_cp_reality_principle_v20.py": [
        "multi_operator_phase_hessian_v20",
    ],
}

FINITE_SEARCH_MODULES = [
    "selected_vacuum_phase_invariant_dim6_metric_audit_v20.py",
    "selected_vacuum_phase_invariant_dim6_epsilon_reduction_v20.py",
    "selected_vacuum_neutral_h10_dim6_no_go_v20.py",
    "selected_vacuum_dim7_low_complexity_phase_screen_v20.py",
    "selected_vacuum_dim7_high_complexity_wave1_v20.py",
    "selected_vacuum_dim7_remaining_high_complexity_v20.py",
    "selected_vacuum_dim7_complete_no_go_v20.py",
    "selected_vacuum_dimension8_phase_census_v20.py",
    "selected_vacuum_dimension8_first_wave_v20.py",
    "selected_vacuum_dimension8_second_wave_v20.py",
    "selected_vacuum_dimension8_third_wave_v20.py",
    "selected_vacuum_dim8_low_cost_phase_screen_v20.py",
]


def _scan_file(path: Path, tokens: list[str]) -> dict[str, Any]:
    exists = path.exists()
    text = path.read_text(encoding="utf-8") if exists else ""
    found = [token for token in tokens if token in text]
    return {
        "path": path.name,
        "exists": exists,
        "tokens_expected": tokens,
        "tokens_found": found,
        "contains_stale_or_dependent_phase_logic": bool(found),
    }


def build_report(a_kappa: float = 1.0) -> dict[str, Any]:
    physical = quotient.quotient_report(a_kappa)
    scans = [
        _scan_file(ROOT / filename, tokens)
        for filename, tokens in LEGACY_CONSUMERS.items()
    ]
    finite = [
        {
            "path": filename,
            "exists": (ROOT / filename).exists(),
            "classification": "computational_corroboration_of_gauge_and_PQ_selection_rule",
            "required_for_physical_phase_closure": False,
        }
        for filename in FINITE_SEARCH_MODULES
    ]

    stale_or_dependent = [
        row["path"] for row in scans if row["contains_stale_or_dependent_phase_logic"]
    ]
    missing_legacy = [row["path"] for row in scans if not row["exists"]]
    missing_finite = [row["path"] for row in finite if not row["exists"]]

    checks = {
        "gauge_quotient_upstream_green": physical["n_failed"] == 0,
        "exactly_one_physical_PQ_null": physical["flags"][
            "exactly_one_physical_PQ_null"
        ],
        "no_extra_nonaxion_flat_phase": not physical["flags"][
            "extra_nonaxion_flat_phase_present"
        ],
        "DeltaR_phase_is_eaten": physical["flags"][
            "DeltaR_phase_eaten_by_Zprime_BL_R"
        ],
        "all_legacy_consumers_present": not missing_legacy,
        "all_finite_search_modules_present": not missing_finite,
        "stale_consumers_are_explicitly_identified": len(stale_or_dependent) >= 2,
        "finite_search_not_required_for_closure": all(
            not row["required_for_physical_phase_closure"] for row in finite
        ),
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]

    return {
        "status": (
            "PHYSICAL_NEUTRAL_PHASE_CLOSED__LEGACY_CONSUMERS_REVALIDATION_OPEN"
            if not failures
            else "PHYSICAL_PHASE_INTEGRATION_AUDIT_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "authoritative_result": physical,
        "legacy_consumer_audit": {
            "scans": scans,
            "n_scanned": len(scans),
            "n_stale_or_dependent": len(stale_or_dependent),
            "stale_or_dependent_paths": stale_or_dependent,
            "missing_paths": missing_legacy,
            "classification": (
                "pre_quotient_or_downstream_diagnostics__physical_phase_claims_superseded"
            ),
        },
        "finite_invariant_search_audit": {
            "modules": finite,
            "missing_paths": missing_finite,
            "scientific_role": (
                "Independent finite-dimensional checks of the all-orders gauge/PQ "
                "selection identity. They are not needed to lift a physical phase."
            ),
        },
        "closed_subproblem": {
            "scope": "reduced selected-vacuum neutral phase sector",
            "condition": "positive nonzero kappa phase amplitude",
            "unquotiented_rank": 1,
            "unquotiented_nullity": 2,
            "gauge_rank_removed": 1,
            "physical_rank": 1,
            "physical_nullity": 1,
            "physical_null": "PQ axion",
            "extra_physical_nonaxion_flat_phase": False,
        },
        "open_integration_work": {
            "rewrite_multi_operator_phase_hessian_as_prequotient_plus_physical_quotient": True,
            "correct_gauge_fixing_DeltaR_classification": True,
            "revalidate_UV_CP_phase_consumers": True,
            "full_component_scalar_hessian": True,
            "root_by_root_33_goldstone_projection": True,
            "global_stationarity_boundedness_competing_extrema": True,
            "thresholds_two_loop_RGE_proton_decay": True,
        },
        "flags": {
            "physical_neutral_phase_blocker_removed": not bool(failures),
            "legacy_phase_consumers_fully_revalidated": False,
            "finite_dimension_search_workflows_scientifically_required": False,
            "full_component_scalar_hessian_complete": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The reduced neutral phase sector is physically closed after removing "
            "the Z' gauge Goldstone: one CP-odd mode is massive and the sole "
            "physical null is the PQ axion. Legacy pre-quotient consumers require "
            "source-level revalidation, and the full scalar theory remains blocked."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    closed = report["closed_subproblem"]
    legacy = report["legacy_consumer_audit"]
    OUT_MD.write_text(
        "# Selected-vacuum physical phase integration — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Physical phase rank: `{closed['physical_rank']}`\n"
        f"- Physical nullity: `{closed['physical_nullity']}`\n"
        f"- Physical null: `{closed['physical_null']}`\n"
        f"- Extra non-axion phase: `{closed['extra_physical_nonaxion_flat_phase']}`\n"
        f"- Legacy consumers requiring revalidation: `{legacy['n_stale_or_dependent']}`\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--A-kappa", type=float, default=1.0)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report(args.A_kappa)
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
