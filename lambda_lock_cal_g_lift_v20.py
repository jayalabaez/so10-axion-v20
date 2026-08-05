#!/usr/bin/env python3
"""Withdraw the claimed lambda-lock lift of a physical cal-G scalar mode.

The former result raised |lambda_lock| until a singular value of Aulakh cal G
crossed a numerical tolerance. cal G is a SUSY chiral/gaugino fermion matrix,
so that operation cannot establish a non-supersymmetric scalar mass or vacuum
stability. The coupling-arithmetic helper is retained, but the physical lift
claim is fail-closed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
LOCK_CRIT_MARGIN = 1.001


def raised_lambda_lock(selected: float, crit_abs: float) -> dict[str, Any]:
    sign = 1.0 if selected >= 0.0 else -1.0
    target_abs = max(abs(selected), float(crit_abs) * LOCK_CRIT_MARGIN)
    return {
        "lambda_lock_selected": float(selected),
        "lambda_lock_crit_abs": float(crit_abs),
        "lambda_lock_raised": float(sign * target_abs),
        "raise_factor": float(target_abs / max(abs(selected), 1e-30)),
        "margin": LOCK_CRIT_MARGIN,
        "physical_lift_proven": False,
    }


def evaluate_cal_g_at_lock(**kwargs: Any) -> dict[str, Any]:
    return {
        "lambda_lock": kwargs.get("lambda_lock"),
        "withdrawn": True,
        "clears_null_tol": False,
        "reason": "cal G is not a non-SUSY scalar mass-squared matrix",
        "with_lambda_lock_embed": {
            "above_null_tol": False,
            "chiral_5x5_null_ok": False,
            "physical_scalar_interpretation_allowed": False,
        },
    }


def spoilage_compare(
    baseline: dict[str, Any], raised: dict[str, Any]
) -> dict[str, Any]:
    return {
        "not_spoiled": False,
        "withdrawn": True,
        "reason": (
            "no physical lambda-lock scalar lift has been derived, so a "
            "selected-point spoilage comparison cannot close the theory"
        ),
    }


def build_report() -> dict[str, Any]:
    checks = {
        "cal_G_target_identified_as_susy_fermion_gaugino_matrix": True,
        "old_lambda_lock_threshold_withdrawn": True,
        "selected_point_no_spoilage_claim_withdrawn": True,
        "direct_nonsusy_hessian_required": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "LAMBDA_LOCK_CAL_G_LIFT_WITHDRAWN__NONSUSY_HESSIAN_OPEN"
            if not failures
            else "LAMBDA_LOCK_WITHDRAWAL_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "couplings": {
            "kappa_fixed": None,
            "lam4_fixed": None,
            "lambda_lock_selected": None,
            "lambda_lock_crit_abs": None,
            "lambda_lock_raised": None,
            "raise_factor": None,
            "withdrawn": True,
        },
        "cal_G": {
            "at_selected_lambda_lock": evaluate_cal_g_at_lock(
                lambda_lock=None
            ),
            "at_raised_lambda_lock": evaluate_cal_g_at_lock(
                lambda_lock=None
            ),
        },
        "point_evaluation": {
            "withdrawn": True,
            "spoilage": spoilage_compare({}, {}),
        },
        "certificate": {
            "selected_lambda_lock_raised_to_cal_G_lift": False,
            "residual_still_open": {
                "direct_nonsusy_singlet_mass_squared_matrix": True,
                "lambda_lock_component_projection": True,
                "physical_EW_vacuum_reminimization": True,
            },
            "interpretation": (
                "No physical cal-G scalar lift is certified. The old threshold "
                "was obtained by deforming a SUSY fermion/gaugino matrix."
            ),
        },
        "flag": {
            "selected_lambda_lock_raised_to_cal_G_lift": False,
            "cal_G_soft_mode_cleared_at_raised_lock": False,
            "selected_point_not_spoiled_by_lock_raise": False,
            "old_lambda_lock_lift_claim_valid": False,
            "cal_G_susy_gaugino_target_withdrawn": True,
            "selected_lam4_still_below_gut_null_tol": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
            "whole_model_validated": False,
        },
        "verdict": (
            "The lambda-lock cal-G lift and selected-point no-spoilage claims "
            "are withdrawn pending a direct non-SUSY scalar Hessian."
        ),
    }


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    report = build_report()
    ROOT.joinpath("LAMBDA_LOCK_CAL_G_LIFT_V20.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("LAMBDA_LOCK_CAL_G_LIFT_V20.md").write_text(
        "# lambda-lock cal G correction — v20\n\n" + report["verdict"] + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
