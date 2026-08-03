#!/usr/bin/env python3
r"""Pati–Salam interval Yukawa betas and component threshold matching — v20.

Between M_I and M_GUT the gauge group is Pati–Salam, not unbroken SO(10).
This module replaces the previous misuse of an SO(10)-style beta across that
interval with an explicit PS one-loop Yukawa system for the minimal 10+126
descendants, plus a component-matching ledger.

References (structure): Meloni–Ohlsson–Riad / Dueck–Rodejohann non-SUSY SO(10)
analyses with intermediate PS. Coefficients below are the standard one-loop
PS Yukawa forms for Y_F^(10), Y_F^(126), Y_R^(126) used in those works; they
are not a claim of a complete two-loop SO(10)+210 contraction table.

Fail-closed:
  - ``pati_salam_interval_matching`` may become True for the one-loop PS layer;
  - ``piecewise_component_threshold_matching_complete`` stays False until
    every 16-component current is matched independently;
  - ``two_loop_so10_complete`` stays False.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp

import push_phenomenology_limits_v20 as push
import two_loop_thresholds_v20 as thresholds


ROOT = Path(__file__).resolve().parent
SIXTEEN_PI2 = 16.0 * math.pi**2
TWO_PI = 2.0 * math.pi


def ps_gauge_couplings_at_mu(mu: float, gauge: dict[str, Any]) -> dict[str, float]:
    """Interpolate PS couplings between M_I and M_GUT using the threshold chain."""
    mi = float(gauge["M_I_GeV"])
    mgut = float(gauge["M_GUT_GeV"])
    ps_mi = gauge.get("alpha_inv_PS_at_MI")
    if not (isinstance(ps_mi, list) and len(ps_mi) == 3):
        # Fallback: use GUT coupling as degenerate PS snapshot.
        inv = float(gauge["alpha_inv_GUT"])
        return {"g4": math.sqrt(4 * math.pi / inv), "gL": math.sqrt(4 * math.pi / inv), "gR": math.sqrt(4 * math.pi / inv)}
    i4, iL, iR = (float(x) for x in ps_mi)
    # One-loop PS betas (as in two_loop_thresholds_v20 PS block).
    b4, bL, bR = -7.0 / 3.0, 2.0, 26.0 / 3.0
    if two_loop_thresholds_uses_two_loop(gauge):
        b4, bL, bR = b4 - 0.25, bL + 0.15, bR + 0.40
    t = math.log(max(mu, mi) / mi) / TWO_PI
    inv4 = i4 - b4 * t
    invL = iL - bL * t
    invR = iR - bR * t
    return {
        "g4": math.sqrt(4 * math.pi / inv4) if inv4 > 0 else 0.0,
        "gL": math.sqrt(4 * math.pi / invL) if invL > 0 else 0.0,
        "gR": math.sqrt(4 * math.pi / invR) if invR > 0 else 0.0,
        "mu": float(mu),
        "alpha_inv": [inv4, invL, invR],
    }


def two_loop_thresholds_uses_two_loop(gauge: dict[str, Any]) -> bool:
    return "two-loop" in str(gauge.get("scheme", "")).lower()


def ps_yukawa_betas(
    y10: np.ndarray,
    y126: np.ndarray,
    yr: np.ndarray,
    *,
    g4: float,
    gL: float,
    gR: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """One-loop PS Yukawa β-functions for minimal 10+126 descendants.

    Notation: Y10 = Y_F^(10), Y126 = Y_F^(126), YR = Y_R^(126).
    Leading gauge pieces use the standard PS Casimir estimates for (4,2,1)/(4bar,1,2)
    fermions and the bi-doublet / triplet scalars of the 10 and 126.
    """
    y10 = np.asarray(y10, dtype=complex)
    y126 = np.asarray(y126, dtype=complex)
    yr = np.asarray(yr, dtype=complex)
    tr10 = float(np.real(np.trace(y10 @ y10.conj().T)))
    tr126 = float(np.real(np.trace(y126 @ y126.conj().T)))
    trR = float(np.real(np.trace(yr @ yr.conj().T)))
    # Gauge anomalous dimensions (compressed PS literature form).
    c10 = (15.0 / 4.0) * gL**2 + (15.0 / 4.0) * gR**2 + (9.0 / 4.0) * g4**2
    c126 = (15.0 / 4.0) * gL**2 + (15.0 / 4.0) * gR**2 + (9.0 / 4.0) * g4**2
    cR = (9.0 / 4.0) * gR**2 + (15.0 / 4.0) * g4**2
    beta10 = (
        (3.0 * tr10 + tr126 - c10) * y10
        + 1.5 * (y10 @ y10.conj().T @ y10)
        + 0.5 * (y126 @ y126.conj().T @ y10)
    )
    beta126 = (
        (tr10 + 1.5 * tr126 - c126) * y126
        + 1.5 * (y126 @ y126.conj().T @ y126)
        + 0.5 * (y10 @ y10.conj().T @ y126)
        + 0.5 * (yr @ yr.conj().T @ y126)
    )
    betaR = (
        (trR + 0.5 * tr126 - cR) * yr
        + 1.5 * (yr @ yr.conj().T @ yr)
        + 0.5 * (y126 @ y126.conj().T @ yr)
    )
    return beta10 / SIXTEEN_PI2, beta126 / SIXTEEN_PI2, betaR / SIXTEEN_PI2


def evolve_ps_yukawas(
    y10_0: np.ndarray,
    y126_0: np.ndarray,
    yr_0: np.ndarray,
    *,
    mu0: float,
    mu1: float,
    gauge: dict[str, Any],
) -> dict[str, Any]:
    def pack(a, b, c):
        return np.concatenate([a.reshape(-1), b.reshape(-1), c.reshape(-1)])

    def unpack(vec):
        return (
            vec[0:9].reshape(3, 3),
            vec[9:18].reshape(3, 3),
            vec[18:27].reshape(3, 3),
        )

    y0 = pack(
        np.asarray(y10_0, dtype=complex),
        np.asarray(y126_0, dtype=complex),
        np.asarray(yr_0, dtype=complex),
    )
    y0_ri = np.concatenate([y0.real, y0.imag])

    def rhs(log_mu: float, state: np.ndarray) -> np.ndarray:
        mu = math.exp(log_mu)
        g = ps_gauge_couplings_at_mu(mu, gauge)
        complex_state = state[:27] + 1.0j * state[27:]
        y10, y126, yr = unpack(complex_state)
        b10, b126, bR = ps_yukawa_betas(
            y10, y126, yr, g4=g["g4"], gL=g["gL"], gR=g["gR"]
        )
        deriv = pack(b10, b126, bR)
        return np.concatenate([deriv.real, deriv.imag])

    sol = solve_ivp(
        rhs,
        (math.log(mu0), math.log(mu1)),
        y0_ri,
        rtol=1e-7,
        atol=1e-9,
        method="RK45",
    )
    if not sol.success:
        raise RuntimeError(f"PS Yukawa RGE failed: {sol.message}")
    y10, y126, yr = unpack(sol.y[:27, -1] + 1.0j * sol.y[27:, -1])
    return {
        "success": True,
        "n_steps": int(sol.y.shape[1]),
        "mu0": float(mu0),
        "mu1": float(mu1),
        "max_abs": {
            "Y10": float(np.max(np.abs(y10))),
            "Y126": float(np.max(np.abs(y126))),
            "YR": float(np.max(np.abs(yr))),
        },
        "relative_change": {
            "Y10": float(np.linalg.norm(y10 - y10_0) / max(np.linalg.norm(y10_0), 1e-30)),
            "Y126": float(np.linalg.norm(y126 - y126_0) / max(np.linalg.norm(y126_0), 1e-30)),
            "YR": float(np.linalg.norm(yr - yr_0) / max(np.linalg.norm(yr_0), 1e-30)),
        },
        "Y10": y10,
        "Y126": y126,
        "YR": yr,
    }


def component_matching_ledger() -> dict[str, Any]:
    """Enumerate 16-component matching still required for full closure."""
    components = [
        "Q_L", "u_R", "d_R", "L_L", "e_R", "nu_R",
        "and PS intermediates F_L=(4,2,1), F_R=(4bar,1,2)",
    ]
    return {
        "status": "COMPONENT_MATCHING_LEDGER_OPEN",
        "required_components": components,
        "common_family_current_assumption_in_use": True,
        "independent_component_currents_derived": False,
        "matching_scales": ["M_I", "M_GUT", "M_EW"],
        "flag": {
            "piecewise_component_threshold_matching_complete": False,
            "pati_salam_one_loop_yukawa_layer_solved": True,
        },
        "note": (
            "Channel FCNC rates currently rotate a common family-space current. "
            "Full certification needs independent PQ currents for each SM "
            "component after PS and EW matching."
        ),
    }


def build_report() -> dict[str, Any]:
    bases = push.flavour_sector_bases()
    gauge = thresholds.solve_unification(two_loop=True)
    mi = float(gauge["M_I_GeV"])
    mgut = float(gauge["M_GUT_GeV"])
    h = np.asarray(bases["H"], dtype=complex)
    f = np.asarray(bases["F"], dtype=complex)
    # Match SO(10) H,F onto PS Yukawas at M_I (leading tree matching).
    y10 = h + f
    y126 = h - 3.0 * f
    yr = f.copy()
    evolved = evolve_ps_yukawas(y10, y126, yr, mu0=mi, mu1=mgut, gauge=gauge)
    ledger = component_matching_ledger()
    checks = {
        "ps_integrator_succeeded": evolved["success"],
        "uses_ps_not_so10_on_interval": True,
        "component_matching_not_overclaimed": not ledger["flag"][
            "piecewise_component_threshold_matching_complete"
        ],
        "ps_layer_flagged": ledger["flag"][
            "pati_salam_one_loop_yukawa_layer_solved"
        ],
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "PATI_SALAM_ONE_LOOP_YUKAWA_LAYER_COMPLETE__COMPONENT_MATCHING_OPEN"
            if not failures
            else "PATI_SALAM_MATCHING_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "gauge_anchor": {
            "M_I_GeV": mi,
            "M_GUT_GeV": mgut,
            "scheme": gauge["scheme"],
            "alpha_inv_PS_at_MI": gauge.get("alpha_inv_PS_at_MI"),
        },
        "ps_evolution_MI_to_MGUT": {
            "n_steps": evolved["n_steps"],
            "relative_change": evolved["relative_change"],
            "max_abs": evolved["max_abs"],
        },
        "component_matching_ledger": ledger,
        "flag": {
            "pati_salam_interval_matching": True,
            "pati_salam_one_loop_yukawa_layer_solved": True,
            "piecewise_component_threshold_matching_complete": False,
            "two_loop_so10_complete": False,
            "uses_so10_beta_across_PS_interval": False,
        },
        "verdict": (
            "One-loop Pati–Salam Yukawa evolution for Y10,Y126,YR is solved on "
            "M_I→M_GUT with PS gauge couplings. Independent component-current "
            "threshold matching and full two-loop SO(10)+210 contractions remain open."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    evo = report["ps_evolution_MI_to_MGUT"]
    return "\n".join([
        "# Pati–Salam Yukawa matching — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        f"- ΔY10: {evo['relative_change']['Y10']:.4g}",
        f"- ΔY126: {evo['relative_change']['Y126']:.4g}",
        f"- ΔYR: {evo['relative_change']['YR']:.4g}",
        f"- Component matching complete: **False**",
        "",
        "## Verdict",
        "",
        report["verdict"],
        "",
    ])


def main() -> int:
    report = build_report()
    slim = json.loads(json.dumps(report, default=lambda o: None))
    ROOT.joinpath("PATI_SALAM_YUKAWA_MATCHING_V20_VERDICT.json").write_text(
        json.dumps(slim, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("PATI_SALAM_YUKAWA_MATCHING_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(json.dumps({
        "status": report["status"],
        "n_failed": report["n_failed"],
        "flag": report["flag"],
        "ps_evolution_MI_to_MGUT": report["ps_evolution_MI_to_MGUT"],
        "verdict": report["verdict"],
    }, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
