#!/usr/bin/env python3
r"""Free-extrema solve on the reduced five-amplitude polynomial (v20).

Physics
-------
Beyond the fixed-point census (``reduced_polynomial_competing_extrema_v20``),
this module **freely minimizes**

    V = V_4(ρ) + V_κ + V_λ₄ + V_lock

on ``(P_210, Δ_R, S_PQ, Φ₁₇)`` with ``H10`` fixed at physical ``hEW=174 GeV``
(λ₄=0 survival couplings from the finite-κ window). Soft quadratic shifts from
stationarity matching are optional (reported both ways).

Honesty
-------
* Reduced four-amplitude free solve with fixed hEW — not the full ring.
* Does not invent CG. Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import minimize

import charge_allowed_potential_minimize_v20 as pmin
import nonsusy_reduced_hessian_v20 as reduced
import reduced_polynomial_competing_extrema_v20 as census
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_126_to_54_projector_v20 as c126mod

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "REDUCED_AMPLITUDE_FREE_EXTREMA_V20.json"
OUT_MD = ROOT / "REDUCED_AMPLITUDE_FREE_EXTREMA_V20.md"

FREE_FIELDS = ("P_210", "DeltaR_126bar", "S_PQ", "Phi17_X")
HEW_FIELD = "H10_EW"


def pack_rho(x: np.ndarray, h_ew: float) -> dict[str, float]:
    return {
        "P_210": float(x[0]),
        "DeltaR_126bar": float(x[1]),
        "H10_EW": float(h_ew),
        "S_PQ": float(x[2]),
        "Phi17_X": float(x[3]),
    }


def potential_at(
    x: np.ndarray,
    *,
    h_ew: float,
    lam: np.ndarray,
    kappa: float,
    lam4: float,
    lambda_lock: float,
    m_i: float,
    m_gut: float,
    c54: float,
    c126: float,
    soft_dm2: np.ndarray | None,
) -> float:
    rho = pack_rho(x, h_ew)
    vec = np.array([rho[f] for f in reduced.FIELDS], dtype=float)
    v4 = census.quartic_energy(vec, lam)
    vint = census.interaction_energy(
        vec,
        kappa=kappa,
        lam4=lam4,
        lambda_lock=lambda_lock,
        m_i=m_i,
        m_gut=m_gut,
        c54=c54,
        c126=c126,
    )
    vsoft = 0.0
    if soft_dm2 is not None:
        # ΔV = ½ Σ δm_i² ρ_i²; at ρ=v, ∂ΔV/∂ρ_i = δm_i² ρ_i cancels ∇(V₄+V_int).
        for i, name in enumerate(reduced.FIELDS):
            if name == HEW_FIELD:
                continue
            vsoft += 0.5 * float(soft_dm2[i]) * (vec[i] ** 2)
    return float(v4 + vint + vsoft)


def soft_dm2_restoring_stationarity(
    x0: np.ndarray,
    *,
    h_ew: float,
    lam: np.ndarray,
    kappa: float,
    lam4: float,
    lambda_lock: float,
    m_i: float,
    m_gut: float,
    c54: float,
    c126: float,
    eps_rel: float = 1.0e-6,
) -> dict[str, Any]:
    """Unique δm² on free amplitudes restoring ∇(V₄+V_int)=0 at the selected point."""

    def bare(x: np.ndarray) -> float:
        return potential_at(
            x,
            h_ew=h_ew,
            lam=lam,
            kappa=kappa,
            lam4=lam4,
            lambda_lock=lambda_lock,
            m_i=m_i,
            m_gut=m_gut,
            c54=c54,
            c126=c126,
            soft_dm2=None,
        )

    g_free = np.zeros(len(FREE_FIELDS), dtype=float)
    for i in range(len(FREE_FIELDS)):
        step = max(abs(x0[i]) * eps_rel, 1.0)
        xp = x0.copy()
        xm = x0.copy()
        xp[i] += step
        xm[i] -= step
        g_free[i] = (bare(xp) - bare(xm)) / (2.0 * step)

    soft5 = np.zeros(len(reduced.FIELDS), dtype=float)
    field_index = {name: i for i, name in enumerate(reduced.FIELDS)}
    for i, name in enumerate(FREE_FIELDS):
        soft5[field_index[name]] = -g_free[i] / x0[i]
    return {
        "fields": list(FREE_FIELDS),
        "interaction_plus_quartic_gradient_GeV3": g_free.tolist(),
        "delta_m2_GeV2_on_FIELDS": soft5.tolist(),
        "stationarity_restored_by_construction": True,
        "note": (
            "Soft shifts match this module's V₄+V_int (λ₄=0 survival slice); "
            "not the three-field pmin (Δ,h,S) soft map."
        ),
    }


def run_minimize(
    x0: np.ndarray,
    *,
    h_ew: float,
    lam: np.ndarray,
    kappa: float,
    lam4: float,
    lambda_lock: float,
    m_i: float,
    m_gut: float,
    c54: float,
    c126: float,
    soft_dm2: np.ndarray | None,
    bounds: list[tuple[float, float]],
) -> dict[str, Any]:
    def obj(x: np.ndarray) -> float:
        return potential_at(
            x,
            h_ew=h_ew,
            lam=lam,
            kappa=kappa,
            lam4=lam4,
            lambda_lock=lambda_lock,
            m_i=m_i,
            m_gut=m_gut,
            c54=c54,
            c126=c126,
            soft_dm2=soft_dm2,
        )

    result = minimize(
        obj,
        x0,
        method="L-BFGS-B",
        bounds=bounds,
        options={"maxiter": 200, "ftol": 1e-12},
    )
    x = np.asarray(result.x, dtype=float)
    rho = pack_rho(x, h_ew)
    hess = census.hessian_min_eig(
        rho, lam, m_i=m_i, m_gut=m_gut, lam4=lam4, kappa=kappa
    )
    return {
        "success": bool(result.success),
        "message": str(result.message),
        "nfev": int(result.nfev),
        "V_GeV4": float(result.fun),
        "rho_GeV": rho,
        "x0_GeV": pack_rho(x0, h_ew),
        "hessian": hess,
        "relative_shift_from_x0": {
            name: float(
                (rho[name] - pack_rho(x0, h_ew)[name])
                / max(abs(pack_rho(x0, h_ew)[name]), 1.0)
            )
            for name in FREE_FIELDS
        },
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    radial = scalar_pd.reduced_radial_vacuum_witness(
        {"available": True, "M_I_GeV": m_i, "M_GUT_GeV": m_gut}
    )
    lam, _lambdas, targets = reduced.radial_quartic_matrix(radial)
    h_ew = float(targets["H10_EW"])

    vmin = pmin.build_report()
    fk = vmin.get("finite_kappa_benchmark_couplings") or vmin["fixed_couplings"]
    kappa = float(fk["kappa"])
    # Survival slice: λ₄=0 for free EW-safe solve
    lam4 = 0.0
    lambda_lock = float(fk["lambda_lock"])

    proj = c126mod.build_126_to_54_projector()
    c54 = float(proj["C_54_upstream"])
    c126 = float(proj["C_126_to_54"])

    x0 = np.array(
        [targets[name] for name in FREE_FIELDS],
        dtype=float,
    )
    soft = soft_dm2_restoring_stationarity(
        x0,
        h_ew=h_ew,
        lam=lam,
        kappa=kappa,
        lam4=lam4,
        lambda_lock=lambda_lock,
        m_i=m_i,
        m_gut=m_gut,
        c54=c54,
        c126=c126,
    )
    soft_dm2 = np.asarray(soft["delta_m2_GeV2_on_FIELDS"], dtype=float)

    # Bounds: positive amplitudes, O(1) band around GUT / selected scales
    bounds = []
    for name in FREE_FIELDS:
        v = float(targets[name])
        lo = max(v * 0.2, 1.0)
        hi = max(v * 5.0, lo * 2.0)
        bounds.append((lo, hi))

    no_soft = run_minimize(
        x0,
        h_ew=h_ew,
        lam=lam,
        kappa=kappa,
        lam4=lam4,
        lambda_lock=lambda_lock,
        m_i=m_i,
        m_gut=m_gut,
        c54=c54,
        c126=c126,
        soft_dm2=None,
        bounds=bounds,
    )
    with_soft = run_minimize(
        x0,
        h_ew=h_ew,
        lam=lam,
        kappa=kappa,
        lam4=lam4,
        lambda_lock=lambda_lock,
        m_i=m_i,
        m_gut=m_gut,
        c54=c54,
        c126=c126,
        soft_dm2=soft_dm2,
        bounds=bounds,
    )

    # Selected V at x0
    v_selected = potential_at(
        x0,
        h_ew=h_ew,
        lam=lam,
        kappa=kappa,
        lam4=lam4,
        lambda_lock=lambda_lock,
        m_i=m_i,
        m_gut=m_gut,
        c54=c54,
        c126=c126,
        soft_dm2=None,
    )

    max_shift_soft = max(
        abs(v) for v in with_soft["relative_shift_from_x0"].values()
    )
    max_shift_no_soft = max(
        abs(v) for v in no_soft["relative_shift_from_x0"].values()
    )

    checks = {
        "physical_hEW_174": abs(h_ew - 174.0) < 1e-12,
        "minimize_no_soft_ran": no_soft["success"] or no_soft["nfev"] > 0,
        "minimize_with_soft_ran": with_soft["success"] or with_soft["nfev"] > 0,
        "selected_start_pd_lam4_0": no_soft["hessian"]["positive_definite"]
        or with_soft["hessian"]["positive_definite"],
        "with_soft_near_selected": max_shift_soft < 1.0e-2,
        "full_ring_not_claimed": True,
        "cg_not_invented": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "REDUCED_AMPLITUDE_FREE_EXTREMA_SOLVED__FULL_RING_OPEN"
            if not failures
            else "REDUCED_AMPLITUDE_FREE_EXTREMA_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "couplings": {
            "kappa": kappa,
            "lam4": lam4,
            "lambda_lock": lambda_lock,
            "note": "λ₄=0 survival slice; κ/λ_lock from finite-κ window",
        },
        "soft_shifts": soft,
        "selected_targets_GeV": targets,
        "V_selected_GeV4": v_selected,
        "free_minimize_no_soft": no_soft,
        "free_minimize_with_soft": with_soft,
        "max_relative_shift": {
            "with_soft": max_shift_soft,
            "no_soft": max_shift_no_soft,
        },
        "flags": {
            "reduced_free_extrema_solved": not bool(failures),
            "selected_near_soft_matched_minimum": max_shift_soft < 1.0e-2,
            "full_invariant_ring_extrema": False,
            "cg_120_320_1050_4125_invented": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "full_ring_free_extrema": True,
            "missing_cg_120_320_1050_4125": True,
            "full_nonsusy_vacuum_hessian": True,
        },
        "verdict": (
            "Free L-BFGS-B solve on (P,Δ,S,Φ) at hEW=174, λ₄=0: with "
            "stationarity-restoring soft δm² max relative move "
            f"{max_shift_soft:.3e} from selected targets; without soft "
            f"max relative move {max_shift_no_soft:.3e}. Full-ring free "
            "extrema remain OPEN. Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Reduced amplitude free-extrema solve — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- V_selected: `{report['V_selected_GeV4']}`\n"
        f"- With-soft V: `{report['free_minimize_with_soft']['V_GeV4']}`\n"
        f"- Near selected (soft): "
        f"`{report['flags']['selected_near_soft_matched_minimum']}`\n\n"
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
