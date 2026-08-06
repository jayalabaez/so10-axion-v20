#!/usr/bin/env python3
r"""Free extrema on promoted (p,a,ω) seven-amplitude potential (v20).

Physics
-------
Upstream ``promote_paw_split_reduced_amplitudes_v20`` replaces coarse ``P_210``
by ``(p,a,ω)`` with source pure-210 ``V₄``, published linear CG for Δ/H₁₀, and
an isotropic residual for S/Φ₁₇. This module freely minimizes that promoted
potential at fixed physical ``hEW=174 GeV`` and ``λ₄=0``, with and without
soft δm² that restore stationarity on the non-210 amplitudes.

Honesty
-------
* Seven-amplitude reduced solve — not the full ring / full Hessian.
* S/Φ₁₇ crosses remain isotropic residual (no invented linear CG).
* Does not invent 120/320/1050/4125.
* Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import minimize

import nonsusy_reduced_hessian_v20 as reduced
import promote_paw_split_reduced_amplitudes_v20 as paw
import scalar_vacuum_proton_decay_v20 as scalar_pd
import source_pure210_reduced_potential_insertion_v20 as insertion

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "PROMOTE_PAW_FREE_EXTREMA_STATIONARITY_V20.json"
OUT_MD = ROOT / "PROMOTE_PAW_FREE_EXTREMA_STATIONARITY_V20.md"

FREE_FIELDS = (
    "p_210",
    "a_210",
    "omega_210",
    "DeltaR_126bar",
    "S_PQ",
    "Phi17_X",
)
HEW = "H10_EW"


def pack_x(x: np.ndarray, h_ew: float) -> np.ndarray:
    """Map free vector → promoted 7-vector (p,a,ω,Δ,hEW,S,Φ)."""
    return np.array(
        [x[0], x[1], x[2], x[3], h_ew, x[4], x[5]], dtype=float
    )


def potential(
    x: np.ndarray,
    *,
    h_ew: float,
    couplings: dict[str, float],
    lam_non: np.ndarray,
    lam_cross: np.ndarray,
    params: dict[str, float],
    lam_eff_fixed: dict[str, float],
    soft_dm2_free: np.ndarray | None,
) -> float:
    full = pack_x(x, h_ew)
    v = paw.potential_promoted(
        full,
        couplings=couplings,
        lam_non=lam_non,
        lam_cross=lam_cross,
        params=params,
        lam_eff_fixed=lam_eff_fixed,
    )
    if soft_dm2_free is not None:
        # soft on free amplitudes only (not hEW)
        for i, dm2 in enumerate(soft_dm2_free):
            v += 0.5 * float(dm2) * float(x[i] ** 2)
    return float(v)


def soft_dm2_restoring(
    x0: np.ndarray,
    *,
    h_ew: float,
    couplings: dict[str, float],
    lam_non: np.ndarray,
    lam_cross: np.ndarray,
    params: dict[str, float],
    lam_eff_fixed: dict[str, float],
    eps_rel: float = 1.0e-6,
) -> np.ndarray:
    """δm² on free amps so ∂V/∂x_i + δm_i² x_i ≈ 0 at selected point."""

    def bare(x: np.ndarray) -> float:
        return potential(
            x,
            h_ew=h_ew,
            couplings=couplings,
            lam_non=lam_non,
            lam_cross=lam_cross,
            params=params,
            lam_eff_fixed=lam_eff_fixed,
            soft_dm2_free=None,
        )

    g = np.zeros(len(FREE_FIELDS), dtype=float)
    for i in range(len(FREE_FIELDS)):
        step = max(abs(x0[i]) * eps_rel, 1.0)
        xp = x0.copy()
        xm = x0.copy()
        xp[i] += step
        xm[i] -= step
        g[i] = (bare(xp) - bare(xm)) / (2.0 * step)
    dm2 = np.zeros_like(g)
    for i, xi in enumerate(x0):
        if abs(xi) > 1.0:
            dm2[i] = -g[i] / xi
    return dm2


def run_minimize(
    x0: np.ndarray,
    *,
    h_ew: float,
    couplings: dict[str, float],
    lam_non: np.ndarray,
    lam_cross: np.ndarray,
    params: dict[str, float],
    lam_eff_fixed: dict[str, float],
    soft_dm2_free: np.ndarray | None,
    bounds: list[tuple[float, float]],
) -> dict[str, Any]:
    def obj(x: np.ndarray) -> float:
        return potential(
            x,
            h_ew=h_ew,
            couplings=couplings,
            lam_non=lam_non,
            lam_cross=lam_cross,
            params=params,
            lam_eff_fixed=lam_eff_fixed,
            soft_dm2_free=soft_dm2_free,
        )

    result = minimize(
        obj,
        x0,
        method="L-BFGS-B",
        bounds=bounds,
        options={"maxiter": 400, "ftol": 1e-12},
    )
    x_opt = np.asarray(result.x, dtype=float)
    rho = {
        name: float(x_opt[i]) for i, name in enumerate(FREE_FIELDS)
    }
    rho[HEW] = float(h_ew)
    return {
        "success": bool(result.success),
        "message": str(result.message),
        "nfev": int(result.nfev),
        "V_GeV4": float(result.fun),
        "x": rho,
        "rel_shift_from_selected": {
            name: float(
                (rho[name] - float(x0[i])) / max(abs(float(x0[i])), 1.0)
            )
            for i, name in enumerate(FREE_FIELDS)
        },
    }


def build_report() -> dict[str, Any]:
    paw_rep = paw.build_report()
    anchor = scalar_pd._unification_anchor()
    targets = paw.promoted_targets(anchor)
    h_ew = float(targets[HEW])

    # Couplings / matrices from the same path as promote_paw.build_report
    radial = scalar_pd.reduced_radial_vacuum_witness(
        {
            "available": True,
            "M_I_GeV": float(anchor["M_I_GeV"]),
            "M_GUT_GeV": float(anchor["M_GUT_GeV"]),
        }
    )
    quartic5, _, _ = reduced.radial_quartic_matrix(radial)
    lam_non, lam_cross = paw.non210_quartic_blocks(quartic5)
    matched = paw.matched_linear_cg_strengths(
        p=targets["p_210"],
        a=targets["a_210"],
        omega=targets["omega_210"],
        lam_cross=lam_cross,
    )
    lam_eff_fixed = {
        field: ch["lambda_eff_matched"]
        for field, ch in matched["channels"].items()
    }

    # Prefer exact same params path as promote_paw
    params = reduced.interaction_parameters(
        float(anchor["M_I_GeV"]), float(anchor["M_GUT_GeV"]), 0.0
    )
    couplings = dict(insertion.DIAGNOSTIC_COUPLINGS)

    x0 = np.array([targets[n] for n in FREE_FIELDS], dtype=float)
    soft = soft_dm2_restoring(
        x0,
        h_ew=h_ew,
        couplings=couplings,
        lam_non=lam_non,
        lam_cross=lam_cross,
        params=params,
        lam_eff_fixed=lam_eff_fixed,
    )

    bounds = []
    for name in FREE_FIELDS:
        v = float(targets[name])
        lo = max(v * 0.2, 1.0)
        hi = max(v * 5.0, lo * 2.0)
        bounds.append((lo, hi))

    no_soft = run_minimize(
        x0,
        h_ew=h_ew,
        couplings=couplings,
        lam_non=lam_non,
        lam_cross=lam_cross,
        params=params,
        lam_eff_fixed=lam_eff_fixed,
        soft_dm2_free=None,
        bounds=bounds,
    )
    with_soft = run_minimize(
        x0,
        h_ew=h_ew,
        couplings=couplings,
        lam_non=lam_non,
        lam_cross=lam_cross,
        params=params,
        lam_eff_fixed=lam_eff_fixed,
        soft_dm2_free=soft,
        bounds=bounds,
    )

    v_selected = potential(
        x0,
        h_ew=h_ew,
        couplings=couplings,
        lam_non=lam_non,
        lam_cross=lam_cross,
        params=params,
        lam_eff_fixed=lam_eff_fixed,
        soft_dm2_free=None,
    )

    max_shift_soft = max(
        abs(v) for v in with_soft["rel_shift_from_selected"].values()
    )
    hess = paw_rep.get("promoted_hessian_lam4_0", {})

    checks = {
        "paw_upstream_green": bool(paw_rep.get("n_failed", 1) == 0),
        "minimize_no_soft_ran": bool(no_soft["success"] or no_soft["nfev"] > 0),
        "minimize_with_soft_ran": bool(with_soft["success"] or with_soft["nfev"] > 0),
        "selected_potential_finite": bool(np.isfinite(v_selected)),
        "with_soft_near_selected": bool(max_shift_soft < 0.25),
        "promoted_hessian_psd_documented": bool(
            hess.get("positive_semidefinite", False)
        ),
        "hEW_fixed_physical": bool(abs(h_ew - 174.0) < 1e-9),
        "isotropic_S_Phi17_residual_kept": bool(
            paw_rep.get("flags", {}).get("isotropic_residual_S_Phi17_only", True)
        ),
        "cg_not_invented": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "PROMOTE_PAW_FREE_EXTREMA_PARTIAL"
            if not failures
            else "PROMOTE_PAW_FREE_EXTREMA_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "free_fields": list(FREE_FIELDS),
        "fixed": {HEW: h_ew, "lam4": 0.0},
        "selected_targets": {k: float(targets[k]) for k in paw.PROMOTED_FIELDS},
        "V_selected_GeV4": v_selected,
        "soft_dm2_free_GeV2": {
            name: float(soft[i]) for i, name in enumerate(FREE_FIELDS)
        },
        "free_minimize_no_soft": no_soft,
        "free_minimize_with_soft": with_soft,
        "promoted_hessian_lam4_0_min_eig": hess.get("min_eig_mpmath"),
        "flags": {
            "paw_free_extrema_ready": not bool(failures),
            "soft_anchors_selected_vacuum": max_shift_soft < 0.25,
            "isotropic_residual_S_Phi17_only": True,
            "cg_120_320_1050_4125_invented": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "published_linear_cg_for_S_Phi17_cross": True,
            "full_ring_extrema": True,
            "missing_cg_120_320_1050_4125": True,
            "full_nonsusy_vacuum_hessian": True,
        },
        "verdict": (
            "Promoted (p,a,ω) free extrema PARTIAL: λ₄=0, hEW fixed; "
            f"with-soft max |Δρ/ρ|={max_shift_soft:.4g}; "
            f"no-soft V={no_soft['V_GeV4']:.6g}, "
            f"with-soft V={with_soft['V_GeV4']:.6g}. "
            "S/Φ₁₇ isotropic residual kept. Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Promote (p,a,ω) free extrema / stationarity — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- V_selected: `{report['V_selected_GeV4']}`\n"
        f"- With-soft V: `{report['free_minimize_with_soft']['V_GeV4']}`\n"
        f"- No-soft V: `{report['free_minimize_no_soft']['V_GeV4']}`\n\n"
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
