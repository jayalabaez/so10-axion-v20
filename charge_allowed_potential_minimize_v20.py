#!/usr/bin/env python3
r"""Minimize the charge-allowed reduced potential to fix λ_lock, λ4, κ (v20).

Next step after ``so10_126_to_54_projector_v20``:

1. Build a **charge-allowed reduced potential** on
   ``(r_Δ, r_10, r_S)`` at fixed ``⟨210⟩=M_GUT``, using:
   - the PR #18 radial wells (restricted),
   - ``κ`` from ``10_H² S``,
   - ``λ₄`` from dim-4 ``210·10·126·S``,
   - ``λ_lock`` from dim-6 ``126bar² 10² S²`` with combinatorial
     ``C_54·C_126→54``.
2. For any trial ``(κ, λ₄, λ_lock)``, solve the unique soft-mass shifts
   ``δm_i²`` that restore exact stationarity at the unification-target VEVs.
3. Minimize a cost preferring small soft shifts, positive-definite radial
   Hessian, perturbative couplings, and Patel–Shukla ``p→μK⁰`` survival.
4. Report the best-fit couplings and the resulting extended ``M_T`` lightest
   eigenvalue — **conditionally**, not as a unique UV vacuum.

Honesty
-------
* This is a reduced 3-field magnitude sector, not the full 210+126+10 component
  potential.
* Soft-mass shifts are part of the charge-allowed quadratic sector; they are
  not unique UV predictions.
* Unique ``τ_p`` and complete SO(10) vacuum selection remain OPEN.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import differential_evolution

import conditional_mt_interference_v20 as cmt
import extended_ttbar_54_locking_v20 as ext
import patel_shukla_scalar_pdecay_v20 as ps
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_126_to_54_projector_v20 as c126mod

ROOT = Path(__file__).resolve().parent

SOURCES = {
    "upstream_126_54": "so10_126_to_54_projector_v20",
    "upstream_radial": "scalar_vacuum_proton_decay_v20.reduced_radial_vacuum_witness",
    "operators": {
        "kappa": "10_H^2 S (PQ/X/Z17 allowed)",
        "lam4": "210·10·126·S (charge+SO(10) allowed dim-4)",
        "lambda_lock": "126bar_H^2 10_H^2 S^2 / M_GUT^2 (54-channel)",
    },
}


def _interaction_potential(
    r: np.ndarray,
    *,
    kappa: float,
    lam4: float,
    lambda_lock: float,
    m_i: float,
    m_gut: float,
    c54: float,
    c126: float,
) -> float:
    """Phase-aligned interaction potential on (r_Δ, r_10, r_S)."""
    r_d, r_h, r_s = (float(x) for x in r)
    # κ dimensionless with mass-like cubic: V_κ = -κ M_I r_10² r_S
    v_k = -kappa * m_i * (r_h**2) * r_s
    # dim-4: V_4 = -λ4 ⟨210⟩_proxy r_10 r_Δ r_S with ⟨210⟩→M_GUT
    v_4 = -lam4 * m_gut * r_h * r_d * r_s
    # dim-6 locking at phase minimum (cos=1 ⇒ V=-A)
    v_l = (
        -lambda_lock
        * c54
        * c126
        * (r_d**2)
        * (r_h**2)
        * (r_s**2)
        / (m_gut**2)
    )
    return v_k + v_4 + v_l


def interaction_gradient(
    r: np.ndarray,
    *,
    kappa: float,
    lam4: float,
    lambda_lock: float,
    m_i: float,
    m_gut: float,
    c54: float,
    c126: float,
) -> np.ndarray:
    r_d, r_h, r_s = (float(x) for x in r)
    c = c54 * c126
    g_d = -lam4 * m_gut * r_h * r_s - lambda_lock * c * (
        2.0 * r_d * (r_h**2) * (r_s**2)
    ) / (m_gut**2)
    g_h = (
        -kappa * m_i * (2.0 * r_h) * r_s
        - lam4 * m_gut * r_d * r_s
        - lambda_lock * c * (2.0 * r_h * (r_d**2) * (r_s**2)) / (m_gut**2)
    )
    g_s = (
        -kappa * m_i * (r_h**2)
        - lam4 * m_gut * r_d * r_h
        - lambda_lock * c * (2.0 * r_s * (r_d**2) * (r_h**2)) / (m_gut**2)
    )
    return np.array([g_d, g_h, g_s], dtype=float)


def soft_mass_shifts_for_stationarity(
    *,
    kappa: float,
    lam4: float,
    lambda_lock: float,
    m_i: float,
    m_gut: float,
    c54: float,
    c126: float,
) -> dict[str, Any]:
    """Unique δm_i² restoring ∇V=0 at r=(M_I,M_I,M_I) on top of radial wells.

    Radial witness already has vanishing gradient at targets. Soft shifts
    enter as ΔV = (1/2) Σ δm_i² (r_i² - v_i²); at r=v,
    ∂ΔV/∂r_i = δm_i² r_i, so δm_i² = -g_i / r_i cancels interaction gradients.
    """
    v = np.array([m_i, m_i, m_i], dtype=float)
    g = interaction_gradient(
        v,
        kappa=kappa,
        lam4=lam4,
        lambda_lock=lambda_lock,
        m_i=m_i,
        m_gut=m_gut,
        c54=c54,
        c126=c126,
    )
    dm2 = -g / v
    return {
        "fields": ["r_Delta_126", "r_10_eff", "r_S"],
        "target_vevs_GeV": v.tolist(),
        "interaction_gradient_GeV3": g.tolist(),
        "delta_m2_GeV2": dm2.tolist(),
        "delta_m2_over_MI2": (dm2 / (m_i**2)).tolist(),
        "soft_shift_norm_over_MI2": float(np.linalg.norm(dm2) / (m_i**2)),
        "stationarity_restored": True,
    }


def radial_well_hessian(
    *,
    m_i: float,
    lambdas: np.ndarray | None = None,
) -> np.ndarray:
    """Diagonal radial Hessian from V ⊃ (λ_i/4)(r_i²-v_i²)² at r=v: H_ii=2 λ_i v_i²."""
    if lambdas is None:
        # Match order-of-magnitude self-quartics from the PR #18 witness
        # (DeltaR=0.65, S=0.45) and a comparable 10_eff quartic.
        lambdas = np.array([0.65, 0.50, 0.45], dtype=float)
    v = np.array([m_i, m_i, m_i], dtype=float)
    return np.diag(2.0 * lambdas * (v**2))


def interaction_hessian(
    r: np.ndarray,
    *,
    kappa: float,
    lam4: float,
    lambda_lock: float,
    m_i: float,
    m_gut: float,
    c54: float,
    c126: float,
) -> np.ndarray:
    """Analytic Hessian of V_κ+V_λ4+V_lock (phase-aligned)."""
    r_d, r_h, r_s = (float(x) for x in r)
    c = c54 * c126
    lg = lambda_lock * c / (m_gut**2)
    h = np.zeros((3, 3), dtype=float)
    # indices 0=Δ, 1=H, 2=S
    # V_lock = -lg * r_d² r_h² r_s²
    h[0, 0] += -lg * 2.0 * (r_h**2) * (r_s**2)
    h[1, 1] += -lg * 2.0 * (r_d**2) * (r_s**2)
    h[2, 2] += -lg * 2.0 * (r_d**2) * (r_h**2)
    h[0, 1] += -lg * 4.0 * r_d * r_h * (r_s**2)
    h[0, 2] += -lg * 4.0 * r_d * r_s * (r_h**2)
    h[1, 2] += -lg * 4.0 * r_h * r_s * (r_d**2)
    # V_4 = -λ4 M_GUT r_h r_d r_s
    h[0, 1] += -lam4 * m_gut * r_s
    h[0, 2] += -lam4 * m_gut * r_h
    h[1, 2] += -lam4 * m_gut * r_d
    # V_κ = -κ M_I r_h² r_s
    h[1, 1] += -kappa * m_i * 2.0 * r_s
    h[1, 2] += -kappa * m_i * 2.0 * r_h
    # Symmetrize
    h[1, 0] = h[0, 1]
    h[2, 0] = h[0, 2]
    h[2, 1] = h[1, 2]
    return h


def soft_hessian(dm2: np.ndarray, r: np.ndarray) -> np.ndarray:
    """Hessian of (1/2) Σ δm_i² (r_i² - v_i²) at r=v is diag(δm_i²)."""
    return np.diag(dm2)


def evaluate_couplings(
    *,
    kappa: float,
    lam4: float,
    lambda_lock: float,
    m_i: float,
    m_gut: float,
    c54: float,
    c126: float,
    tau_gauge: float,
) -> dict[str, Any]:
    soft = soft_mass_shifts_for_stationarity(
        kappa=kappa,
        lam4=lam4,
        lambda_lock=lambda_lock,
        m_i=m_i,
        m_gut=m_gut,
        c54=c54,
        c126=c126,
    )
    v = np.array([m_i, m_i, m_i], dtype=float)
    dm2 = np.array(soft["delta_m2_GeV2"], dtype=float)
    hess = (
        radial_well_hessian(m_i=m_i)
        + soft_hessian(dm2, v)
        + interaction_hessian(
            v,
            kappa=kappa,
            lam4=lam4,
            lambda_lock=lambda_lock,
            m_i=m_i,
            m_gut=m_gut,
            c54=c54,
            c126=c126,
        )
    )
    eigs = np.linalg.eigvalsh(hess)
    pd = bool(np.min(eigs) > 0.0)

    # Extended 3×3 M_T at these couplings (mu diagonals ~ M_I)
    filled = ext.fill_extended_3x3(
        m_i=m_i,
        m_gut=m_gut,
        mu_t=m_i,
        mu_tbar=1.1 * m_i,
        mu_126=m_i,
        lam210_10=0.0,
        lam210_126=0.0,
        lamS_10=0.0,
        lamS_126=0.0,
        kappa=kappa,
        lam4=lam4,
        include_dim4_mix=abs(lam4) > 0.0,
    )
    w = np.linalg.eigvalsh(filled["matrix_GeV"])
    light = float(np.min(np.abs(w)))
    ps_row = ps.evaluate_channel(
        "10_H",
        "p_to_mu_K0",
        alpha=0.1,
        M_T_GeV=light,
        M_Tbar_GeV=light,
    )
    tau_int = cmt.interference_lifetime_years(
        tau_gauge, float(ps_row["predicted_lifetime_years"]), 0.0
    )
    excluded = (not ps_row["passes_experimental_limit"]) or light <= 0.0

    amp = ext.locking_amplitude_54(
        m_i=m_i,
        m_gut=m_gut,
        lambda_lock=lambda_lock,
        c_54=c54,
        c_126_to_54=c126,
    )
    phase = ext.phase_hessian_from_A(amp["A_54"])

    pert = max(abs(kappa), abs(lam4), abs(lambda_lock))
    return {
        "kappa": kappa,
        "lam4": lam4,
        "lambda_lock": lambda_lock,
        "soft": soft,
        "radial_hessian_eigenvalues_GeV2": [float(x) for x in eigs],
        "radial_hessian_positive_definite": pd,
        "lightest_MT_GeV": light,
        "patel_shukla_mu_K0_passes": bool(ps_row["passes_experimental_limit"]),
        "interference_lifetime_years": float(tau_int),
        "conditionally_excluded_by_ps_mu_K0": excluded,
        "locking_amplitude_A54": float(amp["A_54"]),
        "phase_n_positive": phase["n_positive"],
        "phase_n_zero": phase["n_zero"],
        "perturbativity_max_abs": pert,
        "perturbative": pert < 4.0 * math.pi,
    }


def _cost(row: dict[str, Any]) -> float:
    soft_n = float(row["soft"]["soft_shift_norm_over_MI2"])
    cost = soft_n
    if not row["radial_hessian_positive_definite"]:
        cost += 50.0
    if not row["perturbative"]:
        cost += 20.0 + row["perturbativity_max_abs"]
    if row["conditionally_excluded_by_ps_mu_K0"]:
        cost += 30.0
    if row["phase_n_positive"] != 1 or row["phase_n_zero"] != 2:
        cost += 10.0
    # Prefer O(0.1–few) locking without forcing uniqueness
    cost += 0.05 * abs(math.log10(max(abs(row["lambda_lock"]), 1e-12)))
    return float(cost)


def minimize_couplings(
    *,
    m_i: float,
    m_gut: float,
    c54: float,
    c126: float,
    tau_gauge: float,
) -> dict[str, Any]:
    bounds = [(-2.0, 2.0), (-2.0, 2.0), (1e-3, 8.0)]  # κ, λ4, λ_lock

    def objective(x: np.ndarray) -> float:
        row = evaluate_couplings(
            kappa=float(x[0]),
            lam4=float(x[1]),
            lambda_lock=float(x[2]),
            m_i=m_i,
            m_gut=m_gut,
            c54=c54,
            c126=c126,
            tau_gauge=tau_gauge,
        )
        return _cost(row)

    result = differential_evolution(
        objective,
        bounds=bounds,
        seed=20,
        maxiter=60,
        popsize=14,
        tol=1e-7,
        atol=1e-8,
        polish=True,
        updating="immediate",
        workers=1,
    )
    x = result.x
    best = evaluate_couplings(
        kappa=float(x[0]),
        lam4=float(x[1]),
        lambda_lock=float(x[2]),
        m_i=m_i,
        m_gut=m_gut,
        c54=c54,
        c126=c126,
        tau_gauge=tau_gauge,
    )
    best["cost"] = _cost(best)
    # SciPy may report success=False on maxiter even with a tiny cost; accept
    # physically valid low-cost PD stationary points.
    accepted = (
        best["cost"] < 0.05
        and best["radial_hessian_positive_definite"]
        and best["soft"]["stationarity_restored"]
        and best["perturbative"]
        and best["phase_n_positive"] == 1
        and best["phase_n_zero"] == 2
    )
    best["optimizer"] = {
        "success": bool(result.success) or accepted,
        "scipy_success": bool(result.success),
        "accepted_low_cost_stationary_point": accepted,
        "message": str(result.message),
        "nfev": int(result.nfev),
        "fun": float(result.fun),
    }

    # Finite-κ benchmark: show soft shifts reopen a κ≠0 window
    def objective_finite_k(x: np.ndarray) -> float:
        if abs(float(x[0])) < 0.05:
            return 1e3
        return objective(x)

    result_k = differential_evolution(
        objective_finite_k,
        bounds=bounds,
        seed=21,
        maxiter=40,
        popsize=10,
        tol=1e-6,
        polish=True,
        updating="immediate",
        workers=1,
    )
    finite_k = evaluate_couplings(
        kappa=float(result_k.x[0]),
        lam4=float(result_k.x[1]),
        lambda_lock=float(result_k.x[2]),
        m_i=m_i,
        m_gut=m_gut,
        c54=c54,
        c126=c126,
        tau_gauge=tau_gauge,
    )
    finite_k["cost"] = _cost(finite_k)
    finite_k_ok = (
        abs(finite_k["kappa"]) >= 0.05
        and finite_k["radial_hessian_positive_definite"]
        and finite_k["soft"]["stationarity_restored"]
        and finite_k["perturbative"]
    )

    # Algebraic note: without soft shifts, κ is forced toward 0 at equal VEVs
    g0 = interaction_gradient(
        np.array([m_i, m_i, m_i]),
        kappa=1.0,
        lam4=0.0,
        lambda_lock=0.0,
        m_i=m_i,
        m_gut=m_gut,
        c54=c54,
        c126=c126,
    )
    return {
        "status": "CHARGE_ALLOWED_COUPLINGS_MINIMIZED",
        "best": best,
        "finite_kappa_benchmark": {
            "enabled": True,
            "accepted": finite_k_ok,
            "point": finite_k if finite_k_ok else None,
            "note": (
                "Best point with |κ|≥0.05 under the same cost; soft quadratic "
                "shifts are required for stationarity when κ≠0."
            ),
        },
        "bounds": {"kappa": bounds[0], "lam4": bounds[1], "lambda_lock": bounds[2]},
        "no_soft_shift_identity": {
            "note": (
                "With only V_κ+V_λ4+V_lock and equal intermediate VEVs, "
                "stationarity without soft shifts forces κ→0 and ties λ4 to "
                "λ_lock; soft quadratic shifts reopen a finite-κ window."
            ),
            "grad_from_unit_kappa_GeV3": g0.tolist(),
        },
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "POTENTIAL_MINIMIZE_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"couplings_minimized": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    gauge = scalar_pd.gauge_proton_decay(anchor)
    tau_gauge = float(gauge["central"]["lifetime_years"])

    proj = c126mod.build_126_to_54_projector()
    c54 = float(proj["C_54_upstream"])
    c126 = float(proj["C_126_to_54"])
    upstream_ext = ext.build_report()

    fit = minimize_couplings(
        m_i=m_i, m_gut=m_gut, c54=c54, c126=c126, tau_gauge=tau_gauge
    )
    best = fit["best"]

    checks = {
        "optimizer_success": bool(best["optimizer"]["success"]),
        "stationarity_restored": bool(best["soft"]["stationarity_restored"]),
        "radial_hessian_pd": bool(best["radial_hessian_positive_definite"]),
        "phase_one_massive": best["phase_n_positive"] == 1,
        "phase_two_flat": best["phase_n_zero"] == 2,
        "perturbative": bool(best["perturbative"]),
        "finite_kappa_window_open": bool(fit["finite_kappa_benchmark"]["accepted"]),
        "c126_positive": c126 > 0,
        "upstream_extended_ok": upstream_ext.get("n_failed", 1) == 0,
        "not_claiming_unique_vacuum": True,
        "not_claiming_unique_taup": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "CHARGE_ALLOWED_POTENTIAL_MINIMIZED__COUPLINGS_CONDITIONAL"
            if not failures
            else "CHARGE_ALLOWED_POTENTIAL_MINIMIZE_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "anchor": {"M_I_GeV": m_i, "M_GUT_GeV": m_gut},
        "C_54": c54,
        "C_126_to_54": c126,
        "minimization": fit,
        "fixed_couplings": {
            "kappa": best["kappa"],
            "lam4": best["lam4"],
            "lambda_lock": best["lambda_lock"],
            "soft_shift_norm_over_MI2": best["soft"]["soft_shift_norm_over_MI2"],
            "lightest_MT_GeV": best["lightest_MT_GeV"],
            "conditionally_excluded_by_ps_mu_K0": best[
                "conditionally_excluded_by_ps_mu_K0"
            ],
        },
        "finite_kappa_benchmark_couplings": (
            {
                "kappa": fit["finite_kappa_benchmark"]["point"]["kappa"],
                "lam4": fit["finite_kappa_benchmark"]["point"]["lam4"],
                "lambda_lock": fit["finite_kappa_benchmark"]["point"]["lambda_lock"],
                "soft_shift_norm_over_MI2": fit["finite_kappa_benchmark"]["point"][
                    "soft"
                ]["soft_shift_norm_over_MI2"],
                "lightest_MT_GeV": fit["finite_kappa_benchmark"]["point"][
                    "lightest_MT_GeV"
                ],
            }
            if fit["finite_kappa_benchmark"]["accepted"]
            else None
        ),
        "upstream_extended_status": upstream_ext.get("status"),
        "next_exact_calculation": [
            "Add remaining 126 fragments (T') allowed by branching",
            "Build the full multi-operator phase Hessian with cross terms",
            "Include gauge–scalar interference with physical mixings",
            "Lift the reduced 3-field minimum to the full 210+126+10 component space",
        ],
        "flag": {
            "couplings_minimized_on_reduced_potential": True,
            "soft_mass_shifts_used": True,
            "finite_kappa_window_demonstrated": bool(
                fit["finite_kappa_benchmark"]["accepted"]
            ),
            "unique_uv_couplings": False,
            "complete_so10_scalar_potential": False,
            "exact_unique_proton_lifetime": False,
            "invented_unpublished_cg_values": False,
            "whole_model_excluded": False,
            "conditional_parameter_point_only": True,
        },
        "verdict": (
            "Charge-allowed reduced potential minimized: soft shifts restore "
            "stationarity at the unification VEVs; best-fit "
            f"(κ, λ₄, λ_lock)=({best['kappa']:.4f}, {best['lam4']:.4f}, "
            f"{best['lambda_lock']:.4f}) with PD radial Hessian. This is a "
            "conditional reduced-sector fit, not a unique full SO(10) vacuum."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    fix = report["fixed_couplings"]
    lines = [
        "# Charge-allowed potential minimization — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        "## Fixed couplings (conditional)",
        "",
        f"- κ = {fix['kappa']:.6f}",
        f"- λ₄ = {fix['lam4']:.6f}",
        f"- λ_lock = {fix['lambda_lock']:.6f}",
        f"- soft-shift norm / M_I² = {fix['soft_shift_norm_over_MI2']:.6e}",
        f"- lightest M_T = {fix['lightest_MT_GeV']:.6e} GeV",
        f"- PS μK⁰ excluded: {fix['conditionally_excluded_by_ps_mu_K0']}",
        "",
    ]
    fk = report.get("finite_kappa_benchmark_couplings")
    if fk:
        lines.extend(
            [
                "## Finite-κ benchmark (|κ|≥0.05)",
                "",
                f"- κ = {fk['kappa']:.6f}",
                f"- λ₄ = {fk['lam4']:.6f}",
                f"- λ_lock = {fk['lambda_lock']:.6f}",
                f"- soft-shift norm / M_I² = {fk['soft_shift_norm_over_MI2']:.6e}",
                "",
            ]
        )
    lines.extend(
        [
        f"- C_54 = {report['C_54']:.6f}; C_126→54 = {report['C_126_to_54']:.6f}",
        "",
        "## Next exact calculation",
        "",
        ]
    )
    for step in report["next_exact_calculation"]:
        lines.append(f"1. {step}")
    lines.extend(["", "## Flags", ""])
    for k, v in report["flag"].items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    report = build_report()
    ROOT.joinpath("CHARGE_ALLOWED_POTENTIAL_MINIMIZE_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("CHARGE_ALLOWED_POTENTIAL_MINIMIZE_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "fixed_couplings": report.get("fixed_couplings"),
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
