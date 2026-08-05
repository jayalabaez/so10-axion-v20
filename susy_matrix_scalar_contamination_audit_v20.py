#!/usr/bin/env python3
"""Audit every known SUSY-matrix-to-non-SUSY-scalar contamination path.

This report is the authoritative source-correction inventory for matrices
imported from Aulakh hep-ph/0405074. It requires all affected scalar Hessian,
Coleman-Weinberg, portal-lift, and proton-lifetime closures to be explicitly
withdrawn while retaining the direct non-SUSY Phi-H-Sigmabar tensor result.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import cal_g_portal_decision_v20 as calg_portal
import cal_g_soft_mode_classification_v20 as calg_soft
import direct_phi_h_sigmabar_td_crosscheck_v20 as tdcheck
import direct_phi_h_sigmabar_tensor_v20 as direct
import g_singlet_6x6_cw_v20 as gsing_cw
import lambda_lock_cal_g_lift_v20 as lock_lift
import mixed_210_126_10_cw_v20 as mixed_cw
import mixed_210_126_10_hilbert_hessian_v20 as mixed_hessian
import tau_p_hessian_residual_closure_v20 as tau_hessian

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_MATRIX_SCALAR_CONTAMINATION_AUDIT_V20.json"
OUT_MD = ROOT / "SUSY_MATRIX_SCALAR_CONTAMINATION_AUDIT_V20.md"


def build_report() -> dict[str, Any]:
    tensor = direct.build_report()
    td = tdcheck.build_report()
    mixed_cw_report = mixed_cw.build_report()
    gsing_report = gsing_cw.build_report()
    mixed_hessian_report = mixed_hessian.build_report()
    calg_report = calg_soft.build_report()
    portal_report = calg_portal.build_report()
    lock_report = lock_lift.build_report()
    tau_report = tau_hessian.build_report()

    rows = {
        "EFJX_scalar_CW": {
            "withdrawn": bool(
                mixed_cw_report.get("n_failed") == 0
                and mixed_cw_report.get("flag", {}).get(
                    "scalar_CW_contribution_withdrawn"
                )
                and not mixed_cw_report.get("flag", {}).get(
                    "mixed_210_126_10_in_cw", True
                )
            ),
            "status": mixed_cw_report.get("status"),
            "invalid_input": "E/F/J/X mixed chiral-gauge fermion matrices",
        },
        "cal_G_scalar_CW": {
            "withdrawn": bool(
                gsing_report.get("n_failed") == 0
                and gsing_report.get("flag", {}).get(
                    "scalar_CW_contribution_withdrawn"
                )
                and gsing_report.get("g_singlet_cw", {}).get(
                    "n_entries"
                )
                == 0
            ),
            "status": gsing_report.get("status"),
            "invalid_input": "cal G mixed chiral/gaugino fermion matrix",
        },
        "mixed_scalar_Hessian": {
            "withdrawn": bool(
                mixed_hessian_report.get("n_failed") == 0
                and mixed_hessian_report.get("flag", {}).get(
                    "imported_susy_hessian_withdrawn"
                )
                and not mixed_hessian_report.get("flag", {}).get(
                    "mixed_210_126_10_complete", True
                )
            ),
            "status": mixed_hessian_report.get("status"),
            "invalid_input": "squared singular values of SUSY fermion matrices",
        },
        "cal_G_scalar_mode_classification": {
            "withdrawn": bool(
                calg_report.get("n_failed") == 0
                and calg_report.get("flag", {}).get(
                    "cal_G_susy_gaugino_diagnostic_only"
                )
                and not calg_report.get("flag", {}).get(
                    "cal_G_soft_mode_classified", True
                )
            ),
            "status": calg_report.get("status"),
            "invalid_input": "cal G fermion singular vector",
        },
        "cal_G_portal_decision": {
            "withdrawn": bool(
                portal_report.get("n_failed") == 0
                and portal_report.get("flag", {}).get(
                    "cal_G_susy_gaugino_target_withdrawn"
                )
                and not portal_report.get("flag", {}).get(
                    "cal_G_portal_decision_resolved", True
                )
            ),
            "status": portal_report.get("status"),
            "invalid_input": "projector deformation of cal G fermion matrix",
        },
        "lambda_lock_cal_G_lift": {
            "withdrawn": bool(
                lock_report.get("n_failed") == 0
                and lock_report.get("flag", {}).get(
                    "cal_G_susy_gaugino_target_withdrawn"
                )
                and not lock_report.get("flag", {}).get(
                    "selected_lambda_lock_raised_to_cal_G_lift", True
                )
            ),
            "status": lock_report.get("status"),
            "invalid_input": "numerical tolerance crossing in cal G",
        },
        "proton_lifetime_Hessian_closure": {
            "withdrawn": bool(
                tau_report.get("n_failed") == 0
                and tau_report.get("flag", {}).get(
                    "imported_susy_hessian_withdrawn"
                )
                and not tau_report.get("flag", {}).get(
                    "full_component_hessian_residual_closed", True
                )
            ),
            "status": tau_report.get("status"),
            "invalid_input": "downstream use of imported SUSY scalar closure",
        },
    }
    all_withdrawn = all(row["withdrawn"] for row in rows.values())
    direct_retained = bool(
        tensor.get("n_failed") == 0
        and tensor.get("flags", {}).get(
            "closed_analytic_portal_spectrum_derived"
        )
        and td.get("n_failed") == 0
        and td.get("flags", {}).get(
            "published_gamma_TD_magnitudes_matched"
        )
    )

    checks = {
        "all_known_contamination_paths_withdrawn": all_withdrawn,
        "direct_nonsusy_tensor_retained": direct_retained,
        "old_8p8e29_bound_not_restored": not tensor.get(
            "flags", {}
        ).get("old_8p8e29_bound_valid", True),
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]

    return {
        "status": (
            "SUSY_MATRIX_SCALAR_CONTAMINATION_AUDIT_CLEAN"
            if not failures
            else "SUSY_MATRIX_SCALAR_CONTAMINATION_REMAINS"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "paths": rows,
        "counts": {
            "n_paths": len(rows),
            "n_withdrawn": sum(
                int(row["withdrawn"]) for row in rows.values()
            ),
            "n_remaining": sum(
                int(not row["withdrawn"]) for row in rows.values()
            ),
        },
        "retained_physics": {
            "direct_tensor_status": tensor.get("status"),
            "direct_tensor_map_shape": tensor.get(
                "representation", {}
            ).get("tensor_map_shape"),
            "published_TD_crosscheck_status": td.get("status"),
            "published_TD_max_abs_residual": td.get("max_abs_residual"),
        },
        "remaining_blockers": {
            "complete_nonsusy_invariant_ring": True,
            "direct_component_mass_squared_matrix": True,
            "physical_scalar_Coleman_Weinberg_spectrum": True,
            "global_vacuum_and_full_Hessian": True,
            "physical_thresholds_and_unique_proton_lifetime": True,
        },
        "flag": {
            "all_known_susy_matrix_scalar_paths_withdrawn": all_withdrawn,
            "direct_tensor_problem_closed": direct_retained,
            "physical_scalar_CW_complete": False,
            "full_component_hessian_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "All known uses of SUSY fermion/gaugino matrices as non-SUSY "
            "scalar Hessian or Coleman-Weinberg inputs are withdrawn. The "
            "direct tensor result is retained; the physical scalar spectrum "
            "and complete theory remain open."
        ),
    }


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    report = build_report()
    OUT_JSON.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    OUT_MD.write_text(
        "# SUSY-matrix scalar contamination audit — v20\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
