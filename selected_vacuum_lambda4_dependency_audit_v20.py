#!/usr/bin/env python3
"""Inventory consumers of the invalid selected-vacuum lambda4 radial proxy.

The exact direct tensor result gives T_Phi Delta_R=0 for all p,a,omega
singlet combinations. Thus lambda4 remains a valid fluctuation mixing block
but does not generate a selected-vacuum monomial proportional to
p*Delta_R*h*S. Modules that use that monomial for stationarity, phase
curvature, tachyons or vacuum selection require revalidation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import selected_vacuum_lambda4_portal_null_audit_v20 as exact_null

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SELECTED_VACUUM_LAMBDA4_DEPENDENCY_AUDIT_V20.json"
OUT_MD = ROOT / "SELECTED_VACUUM_LAMBDA4_DEPENDENCY_AUDIT_V20.md"

REVALIDATE: dict[str, list[str]] = {
    "nonsusy_reduced_hessian_v20.py": ["lam4", "p * delta"],
    "ew_portal_rescue_bound_v20.py": ["historical_lam4"],
    "current_main_repair_closure_v20.py": ["historical_lam4"],
    "final_scalar_theory_gate_v20.py": ["historical_lam4"],
    "scalar_proton_falsification_gate_v20.py": ["historical_lam4"],
    "latest_main_residual_integration_v20.py": ["historical_tachyon"],
    "direct_phi_h_sigmabar_portal_m2_block_v20.py": ["high_precision_hessian", "lam4"],
    "diagonal_h10_sigmabar_m2_isotropic_54_slots_v20.py": ["historical_lam4"],
    "charge_allowed_potential_minimize_v20.py": ["lam4"],
    "multi_operator_phase_hessian_v20.py": ["lam4"],
    "hilbert_mixed_8comp_hessian_v20.py": ["lam4"],
    "unique_soft_scale_stationarity_v20.py": ["lam4"],
    "uv_cp_phases_from_potential_v20.py": ["lam4"],
    "tau_p_uv_vacuum_selection_v20.py": ["lam4"],
    "coleman_weinberg_lifted_vacuum_v20.py": ["lam4"],
}

RETAINED_FLUCTUATION_ONLY: dict[str, list[str]] = {
    "direct_phi_h_sigmabar_tensor_v20.py": ["contraction_matrix"],
    "direct_portal_mass2_schur_gate_v20.py": ["portal_mass2_matrix"],
    "direct_phi_h_sigmabar_td_crosscheck_v20.py": ["published_td_gamma_singular_values"],
}


def _row(path: str, tokens: list[str], status: str) -> dict[str, Any]:
    file_path = ROOT / path
    text = file_path.read_text(encoding="utf-8") if file_path.is_file() else ""
    presence = {token: token in text for token in tokens}
    return {
        "path": path,
        "file_exists": file_path.is_file(),
        "token_presence": presence,
        "dependency_detected": file_path.is_file() and any(presence.values()),
        "scientific_status": status,
    }


def build_report() -> dict[str, Any]:
    exact = exact_null.build_report()
    upstream_ok = bool(
        exact.get("n_failed") == 0
        and exact.get("flags", {}).get("selected_DeltaR_is_portal_null_vector")
        and exact.get("flags", {}).get("full_fluctuation_portal_map_nonzero")
        and not exact.get("flags", {}).get(
            "historical_reduced_lambda4_vacuum_term_physical", True
        )
    )
    revalidate = [
        _row(path, tokens, "REVALIDATION_REQUIRED")
        for path, tokens in REVALIDATE.items()
    ]
    retained = [
        _row(path, tokens, "RETAINED_FLUCTUATION_RESULT")
        for path, tokens in RETAINED_FLUCTUATION_ONLY.items()
    ]
    rows = revalidate + retained
    missing = [row["path"] for row in rows if not row["file_exists"]]
    undetected = [row["path"] for row in rows if not row["dependency_detected"]]

    checks = {
        "exact_selected_vacuum_null_upstream_green": upstream_ok,
        "all_files_present": not missing,
        "all_dependencies_detected": not undetected,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "SELECTED_VACUUM_LAMBDA4_DEPENDENCY_CHAIN_IDENTIFIED__REVALIDATION_OPEN"
            if not failures
            else "SELECTED_VACUUM_LAMBDA4_DEPENDENCY_AUDIT_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "authoritative_upstream": {
            "status": exact.get("status"),
            "selected_image_norm": exact.get("vacuum_contraction", {}).get(
                "selected_image_norm"
            ),
            "full_map_rank": exact.get("fluctuation_map", {}).get("rank"),
        },
        "counts": {
            "n_revalidation_required": len(revalidate),
            "n_retained_fluctuation_results": len(retained),
            "n_revalidated": 0,
            "n_missing_files": len(missing),
            "n_undetected_dependencies": len(undetected),
        },
        "revalidation_required": revalidate,
        "retained_fluctuation_results": retained,
        "withdrawn_selected_vacuum_claims": {
            "minus_lambda4_p_Delta_h_S_radial_term": True,
            "historical_lambda4_radial_tachyon": True,
            "EW_naturalness_bound_from_that_radial_term": True,
            "lambda4_selected_vacuum_phase_curvature": True,
            "stationarity_and_vacuum_selection_using_that_term": True,
        },
        "retained_claims": {
            "full_10x126_tensor_map": True,
            "T_D_Clebsch_spectrum": True,
            "lambda4_vS_TPhi_fluctuation_mass_block": True,
            "Schur_positivity_theorem": True,
        },
        "flags": {
            "all_known_selected_vacuum_consumers_identified": not bool(failures),
            "all_selected_vacuum_consumers_revalidated": False,
            "fluctuation_portal_results_retained": True,
            "historical_lambda4_tachyon_valid": False,
            "repository_ready_for_release": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "next_actions": [
            "Rebuild the reduced vacuum potential with no lambda4 radial monomial.",
            "Retain lambda4 only in the full component fluctuation mass matrix.",
            "Recompute phase rank, stationarity, competing extrema and loop vacuum.",
            "Revalidate every proton-decay and threshold result that selected this vacuum.",
        ],
        "verdict": (
            f"The selected-vacuum lambda4 proxy contaminates {len(revalidate)} "
            "known modules, while three exact fluctuation-level portal results "
            "remain valid. None of the vacuum consumers has yet been revalidated. "
            "The historical radial tachyon is withdrawn and the repository is "
            "not release-ready."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Selected-vacuum lambda4 dependency audit — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Revalidation required: `{report['counts']['n_revalidation_required']}`\n"
        f"- Retained fluctuation results: `{report['counts']['n_retained_fluctuation_results']}`\n"
        f"- Release ready: `{report['flags']['repository_ready_for_release']}`\n\n"
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
