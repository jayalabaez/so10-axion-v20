#!/usr/bin/env python3
"""Integrate the exact direct-portal mass-squared result into the gap ledger.

This report closes only the lambda4*vS*T_Phi off-diagonal mass-squared block,
its real-Hessian embedding, and the exact Schur positivity theorem.  It keeps
the full diagonal component Hessian, stationarity, Goldstone projection, and
global vacuum explicitly open.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import direct_portal_mass2_schur_gate_v20 as schur

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "DIRECT_PORTAL_MASS2_INTEGRATION_V20.json"
OUT_MD = ROOT / "DIRECT_PORTAL_MASS2_INTEGRATION_V20.md"


def build_report() -> dict[str, Any]:
    portal = schur.build_report()
    flags = portal.get("flags", {})
    exact_closed = bool(
        portal.get("n_failed") == 0
        and portal.get("overall_state") == "BLOCKED"
        and flags.get("direct_portal_mass2_block_constructed")
        and flags.get("real_scalar_hessian_embedding_constructed")
        and flags.get("exact_schur_positivity_gate_derived")
        and portal.get("mass2_interpretation", {}).get("B_shape") == [10, 126]
        and portal.get("mass2_interpretation", {}).get("real_hessian_shape")
        == [272, 272]
    )
    fail_closed = bool(
        not flags.get("full_nonsusy_diagonal_component_hessian_supplied", True)
        and not flags.get("full_component_hessian_complete", True)
        and not flags.get("global_vacuum_complete", True)
        and not flags.get("whole_model_validated", True)
        and not flags.get("whole_model_excluded", True)
    )
    conditional = portal.get(
        "historical_lambda4_conditional_doublet_gate", {}
    )
    alignment = conditional.get("alignment_tolerances", {})
    plus_ratio = alignment.get("plus", {}).get(
        "max_abs_combination_over_MGUT"
    )
    minus_ratio = alignment.get("minus", {}).get(
        "max_abs_combination_over_MGUT"
    )
    conditional_result_recorded = bool(
        conditional.get(
            "generic_probe_both_doublet_branches_fail_on_assumption"
        )
        and isinstance(plus_ratio, (int, float))
        and isinstance(minus_ratio, (int, float))
        and plus_ratio > 0.0
        and minus_ratio > 0.0
    )

    checks = {
        "direct_portal_offdiagonal_mass2_closed": exact_closed,
        "real_272_mode_embedding_closed": exact_closed,
        "exact_schur_positivity_theorem_closed": exact_closed,
        "conditional_historical_alignment_result_recorded": (
            conditional_result_recorded
        ),
        "full_diagonal_hessian_remains_open": fail_closed,
        "whole_model_not_overclaimed": fail_closed,
    }
    failures = [name for name, passed in checks.items() if not passed]

    still_open = {
        "complete_nonsusy_invariant_ring": True,
        "derive_H10_diagonal_component_mass_squared": True,
        "derive_Sigmabar126_diagonal_component_mass_squared": True,
        "identify_physical_light_doublet_branch": True,
        "solve_full_stationarity_at_hEW_174_GeV": True,
        "remove_exactly_33_goldstones_from_complete_hessian": True,
        "all_non_goldstone_mass_squared_positive": True,
        "global_boundedness_and_competing_extrema": True,
        "physical_threshold_spectrum": True,
        "unique_proton_lifetime": True,
    }

    return {
        "status": (
            "DIRECT_PORTAL_MASS2_INTEGRATED__FULL_DIAGONAL_HESSIAN_OPEN"
            if not failures
            else "DIRECT_PORTAL_MASS2_INTEGRATION_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "new_exact_closures": {
            "lambda4_vS_TPhi_offdiagonal_mass2_block": exact_closed,
            "real_272_mode_H10_Sigmabar_hessian_embedding": exact_closed,
            "schur_complement_positivity_criterion": exact_closed,
            "isotropic_exact_eigenvalue_spectrum": bool(
                flags.get("exact_isotropic_spectrum_derived")
            ),
            "doublet_and_triplet_rank_loss_surfaces": bool(
                flags.get("doublet_alignment_escape_surfaces_identified")
            ),
        },
        "conditional_historical_diagnostic": {
            "assumption": conditional.get("assumption"),
            "generic_probe_both_doublet_branches_fail_on_assumption": (
                conditional.get(
                    "generic_probe_both_doublet_branches_fail_on_assumption"
                )
            ),
            "max_abs_a_plus_omega_over_MGUT": plus_ratio,
            "max_abs_a_minus_omega_over_MGUT": minus_ratio,
            "interpretation": conditional.get("interpretation"),
            "full_model_exclusion": False,
        },
        "still_open": still_open,
        "upstream_status": portal.get("status"),
        "flags": {
            "direct_portal_component_mass_squared_insertion_closed": (
                exact_closed
            ),
            "direct_nonsusy_offdiagonal_component_mass_squared_closed": (
                exact_closed
            ),
            "full_nonsusy_diagonal_component_hessian_supplied": False,
            "full_component_hessian_complete": False,
            "global_vacuum_complete": False,
            "historical_lambda4_full_model_excluded": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The direct lambda4*vS*T_Phi off-diagonal mass-squared block, its "
            "272-real-mode embedding, and the exact Schur positivity theorem "
            "are now closed. Under the explicitly conditional M_Sigma=M_GUT "
            "diagnostic, the historical lambda4 benchmark requires near "
            "a=±omega alignment or larger diagonal masses. The complete scalar "
            "theory remains BLOCKED until the diagonal component Hessian and "
            "global vacuum are derived."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    OUT_MD.write_text(
        "# Direct portal mass-squared integration — v20\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    report = build_report()
    write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
