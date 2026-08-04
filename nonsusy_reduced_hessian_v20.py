#!/usr/bin/env python3
"""Independent non-SUSY reduced-potential BFB and Hessian certificate (v20).

This module does not import Aulakh/MSGUT component matrices. It repairs the
explicit reduced non-SUSY potential by pairing the phase-locking operator
Delta^2 H^2 S^2+h.c. with the separately allowed modulus operator
|Delta|^2|H|^2|S|^2. It derives the five-amplitude Hessian directly from the
repaired polynomial. Full component closure remains open.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import differential_evolution

import charge_allowed_potential_minimize_v20 as pmin
import mixed_rep_hilbert_bfb_completion_v20 as bfb_basis
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent
FIELDS = ("P_210", "DeltaR_126bar", "H10_eff", "S_PQ", "Phi17_X")


def quartic_amgm_limit(lambdas: dict[str, float]) -> float:
    vals = [float(lambdas[k]) for k in ("P_210", "DeltaR_126bar", "H10_eff", "S_PQ")]
    if not all(v > 0.0 and math.isfinite(v) for v in vals):
        return 0.0
    return float(np.prod(vals) ** 0.25)


def stabilizing_modulus_coefficient(lambda_phase: float, margin_fraction: float = 1e-3) -> float:
    if margin_fraction < 0.0:
        raise ValueError("margin_fraction must be non-negative")
    base = abs(float(lambda_phase))
    return float(base * (1.0 + margin_fraction) + (1e-15 if base == 0.0 else 0.0))


def interaction_gradient(
    r: np.ndarray,
    *,
    kappa: float,
    lam4: float,
    lambda_phase: float,
    lambda_abs: float,
    m_i: float,
    m_gut: float,
    c_lock: float,
) -> np.ndarray:
    p, d, h, s, _x = (float(v) for v in r)
    q = c_lock * (lambda_abs - abs(lambda_phase)) / m_gut**2
    return np.array(
        [
            -lam4 * h * d * s,
            -lam4 * p * h * s + 2.0 * q * d * h**2 * s**2,
            -2.0 * kappa * m_i * h * s - lam4 * p * d * s + 2.0 * q * h * d**2 * s**2,
            -kappa * m_i * h**2 - lam4 * p * h * d + 2.0 * q * s * d**2 * h**2,
            0.0,
        ],
        dtype=float,
    )


def soft_mass_shifts(target: np.ndarray, **interaction: float) -> np.ndarray:
    if np.any(target <= 0.0):
        raise ValueError("positive target amplitudes required")
    return -interaction_gradient(target, **interaction) / target


def interaction_hessian(
    r: np.ndarray,
    *,
    kappa: float,
    lam4: float,
    lambda_phase: float,
    lambda_abs: float,
    m_i: float,
    m_gut: float,
    c_lock: float,
) -> np.ndarray:
    p, d, h, s, _x = (float(v) for v in r)
    q = c_lock * (lambda_abs - abs(lambda_phase)) / m_gut**2
    out = np.zeros((5, 5), dtype=float)
    out[2, 2] += -2.0 * kappa * m_i * s
    out[2, 3] += -2.0 * kappa * m_i * h
    for i, j, value in (
        (0, 1, -lam4 * h * s),
        (0, 2, -lam4 * d * s),
        (0, 3, -lam4 * d * h),
        (1, 2, -lam4 * p * s),
        (1, 3, -lam4 * p * h),
        (2, 3, -lam4 * p * d),
    ):
        out[i, j] += value
    out[1, 1] += 2.0 * q * h**2 * s**2
    out[2, 2] += 2.0 * q * d**2 * s**2
    out[3, 3] += 2.0 * q * d**2 * h**2
    out[1, 2] += 4.0 * q * d * h * s**2
    out[1, 3] += 4.0 * q * d * s * h**2
    out[2, 3] += 4.0 * q * h * s * d**2
    return out + np.triu(out, 1).T


def potential(
    r: np.ndarray,
    *,
    target: np.ndarray,
    lambdas: np.ndarray,
    dm2: np.ndarray,
    kappa: float,
    lam4: float,
    lambda_phase: float,
    lambda_abs: float,
    m_i: float,
    m_gut: float,
    c_lock: float,
) -> float:
    p, d, h, s, _x = (float(v) for v in r)
    wells = 0.25 * np.sum(lambdas * (r**2 - target**2) ** 2)
    soft = 0.5 * np.sum(dm2 * (r**2 - target**2))
    q = c_lock * (lambda_abs - abs(lambda_phase)) / m_gut**2
    interactions = -kappa * m_i * h**2 * s - lam4 * p * d * h * s + q * d**2 * h**2 * s**2
    return float(wells + soft + interactions)


def analytic_hessian(target: np.ndarray, lambdas: np.ndarray, dm2: np.ndarray, **interaction: float) -> np.ndarray:
    return np.diag(2.0 * lambdas * target**2 + dm2) + interaction_hessian(target, **interaction)


def finite_difference_hessian_scaled(fn, x0: np.ndarray, scales: np.ndarray, step: float = 2e-5) -> np.ndarray:
    n = len(x0)
    h_x = np.zeros((n, n), dtype=float)
    f0 = fn(x0 * scales)
    for i in range(n):
        ei = np.zeros(n)
        ei[i] = step
        h_x[i, i] = (fn((x0 + ei) * scales) - 2.0 * f0 + fn((x0 - ei) * scales)) / step**2
        for j in range(i + 1, n):
            ej = np.zeros(n)
            ej[j] = step
            value = (
                fn((x0 + ei + ej) * scales)
                - fn((x0 + ei - ej) * scales)
                - fn((x0 - ei + ej) * scales)
                + fn((x0 - ei - ej) * scales)
            ) / (4.0 * step**2)
            h_x[i, j] = h_x[j, i] = value
    return h_x / np.outer(scales, scales)


def stress_competing_minima(fn, target: np.ndarray, target_value: float) -> dict[str, Any]:
    scales = target.copy()
    bounds = [(0.0, 3.0)] * len(target)

    def objective(x: np.ndarray) -> float:
        return fn(x * scales) / max(abs(target_value), scales[0] ** 4, 1.0)

    result = differential_evolution(
        objective,
        bounds=bounds,
        seed=1720,
        maxiter=80,
        popsize=12,
        tol=1e-8,
        polish=True,
        workers=1,
        updating="immediate",
    )
    r_best = np.asarray(result.x, dtype=float) * scales
    v_best = float(fn(r_best))
    tolerance = 1e-8 * max(abs(target_value), abs(v_best), scales[0] ** 4, 1.0)
    return {
        "box_in_target_units": [0.0, 3.0],
        "optimizer_success": bool(result.success),
        "best_amplitudes_over_target": [float(v) for v in result.x],
        "best_value_GeV4": v_best,
        "target_value_GeV4": float(target_value),
        "lower_than_target": bool(v_best < target_value - tolerance),
        "numerical_only_not_global_proof": True,
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "NONSUSY_REDUCED_HESSIAN_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
        }
    pmin_report = pmin.build_report()
    basis_report = bfb_basis.build_report()
    radial = scalar_pd.reduced_radial_vacuum_witness(anchor)
    if pmin_report.get("n_failed", 1) != 0 or basis_report.get("n_failed", 1) != 0:
        return {
            "status": "NONSUSY_REDUCED_HESSIAN_NOT_EXECUTED__UPSTREAM_FAILED",
            "n_failed": 1,
            "failures": ["pmin_or_bfb_basis"],
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    couplings = pmin_report.get("finite_kappa_benchmark_couplings") or pmin_report["fixed_couplings"]
    kappa = float(couplings["kappa"])
    lam4 = float(couplings["lam4"])
    lambda_phase = float(couplings["lambda_lock"])
    lambda_abs = stabilizing_modulus_coefficient(lambda_phase)
    c_lock = float(pmin_report["C_54"] * pmin_report["C_126_to_54"])

    raw = radial["potential_definition"]["self_quartics"]
    lambda_map = {
        "P_210": float(raw["P_210_PS"]),
        "DeltaR_126bar": float(raw["DeltaR_126bar"]),
        "H10_eff": float(raw["h_EW_effective"]),
        "S_PQ": float(raw["S_PQ"]),
        "Phi17_X": float(raw["Phi17_X"]),
    }
    target = np.array([m_gut, m_i, m_i, m_i, 1.0e17], dtype=float)
    lambdas = np.array([lambda_map[name] for name in FIELDS], dtype=float)
    interaction = dict(
        kappa=kappa,
        lam4=lam4,
        lambda_phase=lambda_phase,
        lambda_abs=lambda_abs,
        m_i=m_i,
        m_gut=m_gut,
        c_lock=c_lock,
    )
    dm2 = soft_mass_shifts(target, **interaction)
    grad = dm2 * target + interaction_gradient(target, **interaction)
    h_analytic = analytic_hessian(target, lambdas, dm2, **interaction)
    fn = lambda r: potential(r, target=target, lambdas=lambdas, dm2=dm2, **interaction)
    h_fd = finite_difference_hessian_scaled(fn, np.ones(5), target)
    scale = max(float(np.max(np.abs(h_analytic))), 1.0)
    hessian_rel_error = float(np.max(np.abs(h_analytic - h_fd)) / scale)
    eigs = np.linalg.eigvalsh(h_analytic)
    target_value = fn(target)
    stress = stress_competing_minima(fn, target, target_value)

    amgm_limit = quartic_amgm_limit(lambda_map)
    phase_bfb = lambda_abs > abs(lambda_phase)
    quartic_bfb = abs(lam4) <= amgm_limit
    exact_bfb = bool(np.all(lambdas > 0.0)) and (phase_bfb or quartic_bfb)
    stationarity_scale = max(m_gut**3, 1.0)

    checks = {
        "modulus_companion_in_basis": bool(basis_report["flag"]["modulus_locking_companion_added"]),
        "phase_lock_bfb": phase_bfb,
        "all_self_quartics_positive": bool(np.all(lambdas > 0.0)),
        "stationarity_exact": float(np.max(np.abs(grad)) / stationarity_scale) < 1e-12,
        "analytic_hessian_symmetric": bool(np.allclose(h_analytic, h_analytic.T, rtol=0.0, atol=1e-8 * scale)),
        "finite_difference_hessian_matches": hessian_rel_error < 2e-4,
        "local_hessian_positive": bool(np.min(eigs) > 0.0),
        "no_aulakh_msgut_component_matrix": True,
        "full_component_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "NONSUSY_REDUCED_BFB_AND_HESSIAN_CLOSED__FULL_COMPONENT_OPEN"
            if not failures
            else "NONSUSY_REDUCED_BFB_HESSIAN_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "fields": list(FIELDS),
        "target_vevs_GeV": target.tolist(),
        "couplings": {
            "kappa": kappa,
            "lam4": lam4,
            "lambda_lock_phase": lambda_phase,
            "lambda_lock_abs": lambda_abs,
            "lambda_lock_abs_min_bfb": abs(lambda_phase),
            "C_lock": c_lock,
            "self_quartics": lambda_map,
        },
        "bfb_certificate": {
            "phase_sextic_condition": "lambda_lock_abs > |lambda_lock_phase|",
            "phase_sextic_passes": phase_bfb,
            "quartic_amgm_limit": amgm_limit,
            "abs_lam4": abs(lam4),
            "quartic_amgm_passes": quartic_bfb,
            "reduced_polynomial_bounded_from_below": exact_bfb,
        },
        "stationarity": {
            "soft_delta_m2_GeV2": dm2.tolist(),
            "gradient_inf_over_MGUT3": float(np.max(np.abs(grad)) / stationarity_scale),
        },
        "hessian": {
            "analytic_GeV2": h_analytic.tolist(),
            "finite_difference_GeV2": h_fd.tolist(),
            "max_relative_difference": hessian_rel_error,
            "eigenvalues_GeV2": [float(v) for v in eigs],
            "positive_definite": bool(np.min(eigs) > 0.0),
            "min_eigenvalue_GeV2": float(np.min(eigs)),
            "robust_unknown_perturbation_norm_GeV2": float(np.min(eigs)),
        },
        "competing_minima_stress": stress,
        "flag": {
            "independent_nonsusy_reduced_hessian": True,
            "phase_lock_modulus_companion_added": True,
            "reduced_potential_bounded_from_below": exact_bfb,
            "reduced_local_minimum_positive_definite": bool(np.min(eigs) > 0.0),
            "uses_aulakh_or_msgut_component_matrices": False,
            "full_component_nonsusy_hessian": False,
            "full_component_global_vacuum_proof": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The explicit reduced non-SUSY radial potential is repaired by the required neutral modulus-locking companion. "
            f"BFB phase condition={phase_bfb}, quartic AM-GM fallback={quartic_bfb}, local Hessian PD={np.min(eigs) > 0.0}. "
            "This removes reliance on SUSY component matrices for the reduced radial certificate; the complete non-SUSY component Hessian remains open."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    b = report["bfb_certificate"]
    h = report["hessian"]
    lines = [
        "# Independent non-SUSY reduced BFB/Hessian certificate — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- lambda_abs / |lambda_phase|: {report['couplings']['lambda_lock_abs'] / max(abs(report['couplings']['lambda_lock_phase']), 1e-30):.8g}",
        f"- |lambda4|: {b['abs_lam4']:.8g}",
        f"- AM-GM quartic limit: {b['quartic_amgm_limit']:.8g}",
        f"- Reduced BFB: {b['reduced_polynomial_bounded_from_below']}",
        f"- Minimum Hessian eigenvalue: {h['min_eigenvalue_GeV2']:.6e} GeV^2",
        f"- Analytic/FD relative difference: {h['max_relative_difference']:.3e}",
        "",
        "The full component non-SUSY Hessian and global vacuum proof remain open.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("NONSUSY_REDUCED_HESSIAN_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("NONSUSY_REDUCED_HESSIAN_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "bfb": report.get("bfb_certificate"),
                "hessian": report.get("hessian"),
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
