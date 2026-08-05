#!/usr/bin/env python3
"""Withdraw the lambda-lock cal-G portal decision pending a non-SUSY Hessian.

The former decision embedded an effective scalar soft mass into Aulakh cal G,
a SUSY chiral/gaugino fermion matrix. That deformation cannot establish that a
charge-allowed scalar operator lifts a physical non-SUSY singlet mode.

The dimension-analysis helpers are retained, but no portal is declared
sufficient or insufficient until the direct component scalar mass-squared
matrix is derived.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent
NULL_TOL_OVER_MGUT = 1e-8


def goldstone_and_orthogonal(
    sigma: complex, sigma_bar: complex
) -> tuple[np.ndarray, np.ndarray]:
    gdir = np.array(
        [0.0, 0.0, 0.0, sigma, sigma_bar, 0.0], dtype=complex
    )
    gdir = gdir / (np.linalg.norm(gdir) + 1e-30)
    orth = np.array(
        [0.0, 0.0, 0.0, -np.conj(sigma_bar), np.conj(sigma), 0.0],
        dtype=complex,
    )
    orth = orth / (np.linalg.norm(orth) + 1e-30)
    return gdir, orth


def deform_cal_g(mat: np.ndarray, orth: np.ndarray, mu: float) -> np.ndarray:
    """Algebraic compatibility helper; not a physical scalar deformation."""
    return mat + float(mu) * np.outer(orth, np.conj(orth))


def spectrum_with_goldstone_check(
    mat: np.ndarray,
    *,
    sigma: complex,
    sigma_bar: complex,
    null_tol_GeV: float,
) -> dict[str, Any]:
    svals = np.linalg.svd(mat, compute_uv=False)
    lightest = float(min(svals))
    return {
        "lightest_GeV": lightest,
        "singular_values_GeV": [float(x) for x in sorted(svals)],
        "above_null_tol": lightest > null_tol_GeV,
        "chiral_5x5_null_ok": False,
        "physical_scalar_interpretation_allowed": False,
    }


def critical_orthogonal_soft(
    mat: np.ndarray,
    orth: np.ndarray,
    *,
    sigma: complex,
    sigma_bar: complex,
    null_tol_GeV: float,
) -> dict[str, Any]:
    return {
        "found": False,
        "mu_crit_GeV": None,
        "already_above_tol": False,
        "withdrawn": True,
        "reason": "cal G is not a non-SUSY scalar mass-squared matrix",
    }


def lambda_lock_soft_mass_GeV(
    lambda_lock: float, *, m_i: float, m_gut: float
) -> float:
    """Dimensional estimate only: sqrt(2|lambda_lock|) M_I^2/M_GUT."""
    return float(
        math.sqrt(2.0 * abs(lambda_lock)) * (m_i**2) / m_gut
    )


def lambda_lock_for_soft_mass(
    mu_GeV: float, *, m_i: float, m_gut: float
) -> float:
    ratio = mu_GeV * m_gut / (m_i**2)
    return float(0.5 * ratio * ratio)


def portal_scale_ledger(
    *,
    kappa: float,
    lam4: float,
    lambda_lock: float,
    m_i: float,
    m_gut: float,
    mu_crit_GeV: float,
) -> dict[str, Any]:
    return {
        "kappa": {"value": kappa, "physical_lift_proven": False},
        "lam4": {"value": lam4, "physical_lift_proven": False},
        "lambda_lock": {
            "value": lambda_lock,
            "soft_mass_estimate_GeV": lambda_lock_soft_mass_GeV(
                lambda_lock, m_i=m_i, m_gut=m_gut
            ),
            "lambda_lock_crit_abs": None,
            "physical_lift_proven": False,
        },
        "withdrawn_target_mu_crit_GeV": mu_crit_GeV,
    }


def build_report() -> dict[str, Any]:
    checks = {
        "cal_G_identified_as_susy_chiral_gaugino_matrix": True,
        "effective_projector_not_used_as_scalar_proof": True,
        "lambda_lock_sufficiency_claim_withdrawn": True,
        "dimensional_helpers_labeled_nonclosing": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "CAL_G_PORTAL_DECISION_WITHDRAWN__NONSUSY_SINGLET_HESSIAN_OPEN"
            if not failures
            else "CAL_G_PORTAL_WITHDRAWAL_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "decision": {
            "label": "undetermined_until_direct_nonsusy_singlet_hessian",
            "extra_new_portal_required": None,
            "existing_lambda_lock_sufficient_in_principle": False,
            "selected_lambda_lock_clears": False,
            "mu_crit_GeV": None,
            "lambda_lock_crit_abs": None,
            "withdrawn": True,
        },
        "soft_mode": {
            "classification_label": (
                "withdrawn_susy_fermion_gaugino_diagnostic"
            ),
            "overlap_goldstone_dir": None,
            "overlap_orthogonal_dir": None,
            "physical_scalar_mode_identified": False,
        },
        "portals": {
            "kappa": {"physical_lift_proven": False},
            "lam4": {"physical_lift_proven": False},
            "lambda_lock": {
                "physical_lift_proven": False,
                "perturbative_O1_window": None,
            },
        },
        "embeddings": {
            "at_lambda_lock_crit": {
                "above_null_tol": False,
                "chiral_5x5_null_ok": False,
                "withdrawn": True,
            }
        },
        "remaining_blockers": {
            "direct_nonsusy_singlet_mass_squared_matrix": True,
            "operator_to_component_projection": True,
            "gauge_projected_full_hessian": True,
        },
        "flag": {
            "cal_G_portal_decision_resolved": False,
            "existing_lambda_lock_sufficient_in_principle": False,
            "extra_new_portal_required": False,
            "old_lambda_lock_lift_claim_valid": False,
            "cal_G_susy_gaugino_target_withdrawn": True,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
            "whole_model_validated": False,
        },
        "verdict": (
            "The cal G portal decision is withdrawn. A lambda-lock projector "
            "inserted into a SUSY fermion/gaugino matrix cannot prove a physical "
            "non-SUSY scalar lift."
        ),
    }


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    report = build_report()
    ROOT.joinpath("CAL_G_PORTAL_DECISION_V20.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("CAL_G_PORTAL_DECISION_V20.md").write_text(
        "# cal G portal source correction — v20\n\n" + report["verdict"] + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
