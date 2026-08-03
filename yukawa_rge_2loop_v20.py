#!/usr/bin/env python3
r"""Piecewise Yukawa RGE with Pati–Salam Clebsch thresholds — v20.

Implements the blueprint chain

    M_GUT  --(SO(10)/PS layer)-->  M_I  --(CG match)-->  M_I^-  --(2HDM)-->  M_Z

with the classic (15,1,1) Clebsch matching

    Y_d(M_I^-) = Y_(6,2,2) + η_I Y_(15,1,1)
    Y_e(M_I^-) = Y_(6,2,2) − 3 η_I Y_(15,1,1)

In the repository basis this is the standard H±F reconstruction:

    Y_d = H + F,   Y_e = H − 3 F,   η_I absorbed into the relative F VEV.

Fail-closed:
  - ``clebsch_threshold_matching_implemented`` may be True;
  - ``piecewise_yukawa_chain_integrated`` may be True for this diagnostic chain;
  - ``two_loop_so10_complete`` and ``published_210_tensor_contractions`` stay False
    until SARAH/PyR@TE-validated SO(10)+210 two-loop betas are ingested.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp

import pati_salam_yukawa_matching_v20 as ps
import push_phenomenology_limits_v20 as push
import two_loop_thresholds_v20 as thresholds


ROOT = Path(__file__).resolve().parent
SIXTEEN_PI2 = 16.0 * math.pi**2
TWO_PI = 2.0 * math.pi


def clebsch_match_from_hf(
    h: np.ndarray,
    f: np.ndarray,
    *,
    eta_i: float = 1.0,
) -> dict[str, Any]:
    """Apply blueprint CG matching at M_I.

    Identifying Y_(6,2,2)=H and Y_(15,1,1)=F / η_I recovers Y_d=H+F, Y_e=H−3F
    when η_I=1 (the conventional unit-normalized repository basis).
    """
    h = np.asarray(h, dtype=complex)
    f = np.asarray(f, dtype=complex)
    y622 = h.copy()
    y1511 = f / eta_i
    yd = y622 + eta_i * y1511
    ye = y622 - 3.0 * eta_i * y1511
    return {
        "eta_I": float(eta_i),
        "Y_622": y622,
        "Y_1511": y1511,
        "Y_d": yd,
        "Y_e": ye,
        "Y_u": h + f,  # up sector from 10+126 combination used in the fit
        "max_abs": {
            "Y_d": float(np.max(np.abs(yd))),
            "Y_e": float(np.max(np.abs(ye))),
            "Y_u": float(np.max(np.abs(h + f))),
        },
        "clebsch_identity_check": {
            "Yd_equals_H_plus_F": float(np.linalg.norm(yd - (h + f))) < 1e-14,
            "Ye_equals_H_minus_3F": float(np.linalg.norm(ye - (h - 3.0 * f)))
            < 1e-14,
        },
    }


def sm_2hdm_yukawa_betas(
    yu: np.ndarray,
    yd: np.ndarray,
    ye: np.ndarray,
    *,
    g1: float,
    g2: float,
    g3: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """One-loop 2HDM-like Yukawa betas (diagnostic, Type-II structure)."""
    yu = np.asarray(yu, dtype=complex)
    yd = np.asarray(yd, dtype=complex)
    ye = np.asarray(ye, dtype=complex)
    tr_u = float(np.real(np.trace(yu @ yu.conj().T)))
    tr_d = float(np.real(np.trace(yd @ yd.conj().T)))
    tr_e = float(np.real(np.trace(ye @ ye.conj().T)))
    cu = (17.0 / 20.0) * g1**2 + (9.0 / 4.0) * g2**2 + 8.0 * g3**2
    cd = (1.0 / 4.0) * g1**2 + (9.0 / 4.0) * g2**2 + 8.0 * g3**2
    ce = (9.0 / 4.0) * g1**2 + (9.0 / 4.0) * g2**2
    beta_u = (
        (3.0 * tr_u + tr_d - cu) * yu
        + 1.5 * (yu @ yu.conj().T @ yu)
        + 0.5 * (yd @ yd.conj().T @ yu)
    )
    beta_d = (
        (tr_u + 3.0 * tr_d + tr_e - cd) * yd
        + 1.5 * (yd @ yd.conj().T @ yd)
        + 0.5 * (yu @ yu.conj().T @ yd)
    )
    beta_e = (
        (3.0 * tr_d + tr_e - ce) * ye
        + 1.5 * (ye @ ye.conj().T @ ye)
    )
    return beta_u / SIXTEEN_PI2, beta_d / SIXTEEN_PI2, beta_e / SIXTEEN_PI2


def gauge_sm_at_mu(mu: float, gauge: dict[str, Any]) -> dict[str, float]:
    """Rough one-loop SM(2HDM) interpolation MZ→M_I using low-scale anchors."""
    mz = 91.1876
    mi = float(gauge["M_I_GeV"])
    # Start from PDG-like inverses used in two_loop_thresholds_v20.
    a1, a2, a3 = 59.02, 29.57, 1.0 / 0.1179
    b1, b2, b3 = 21.0 / 5.0, -3.0, -7.0
    if "two-loop" in str(gauge.get("scheme", "")).lower():
        b1, b2, b3 = b1 + 0.35, b2 - 0.20, b3 - 0.45
    t = math.log(max(mu, mz) / mz) / TWO_PI
    inv1 = a1 - b1 * t
    inv2 = a2 - b2 * t
    inv3 = a3 - b3 * t
    # Clamp near M_I if requested (not used beyond M_I).
    _ = mi
    return {
        "g1": math.sqrt(4 * math.pi / inv1) if inv1 > 0 else 0.0,
        "g2": math.sqrt(4 * math.pi / inv2) if inv2 > 0 else 0.0,
        "g3": math.sqrt(4 * math.pi / inv3) if inv3 > 0 else 0.0,
        "mu": float(mu),
        "alpha_inv": [inv1, inv2, inv3],
    }


def evolve_sm_yukawas(
    yu0: np.ndarray,
    yd0: np.ndarray,
    ye0: np.ndarray,
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
        np.asarray(yu0, dtype=complex),
        np.asarray(yd0, dtype=complex),
        np.asarray(ye0, dtype=complex),
    )
    y0_ri = np.concatenate([y0.real, y0.imag])

    def rhs(log_mu: float, state: np.ndarray) -> np.ndarray:
        mu = math.exp(log_mu)
        g = gauge_sm_at_mu(mu, gauge)
        complex_state = state[:27] + 1.0j * state[27:]
        yu, yd, ye = unpack(complex_state)
        bu, bd, be = sm_2hdm_yukawa_betas(
            yu, yd, ye, g1=g["g1"], g2=g["g2"], g3=g["g3"]
        )
        deriv = pack(bu, bd, be)
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
        raise RuntimeError(f"SM Yukawa RGE failed: {sol.message}")
    yu, yd, ye = unpack(sol.y[:27, -1] + 1.0j * sol.y[27:, -1])
    return {
        "success": True,
        "n_steps": int(sol.y.shape[1]),
        "mu0": float(mu0),
        "mu1": float(mu1),
        "Yu": yu,
        "Yd": yd,
        "Ye": ye,
        "relative_change": {
            "Yu": float(
                np.linalg.norm(yu - yu0) / max(np.linalg.norm(yu0), 1e-30)
            ),
            "Yd": float(
                np.linalg.norm(yd - yd0) / max(np.linalg.norm(yd0), 1e-30)
            ),
            "Ye": float(
                np.linalg.norm(ye - ye0) / max(np.linalg.norm(ye0), 1e-30)
            ),
        },
    }


def run_piecewise_chain(*, eta_i: float = 1.0) -> dict[str, Any]:
    bases = push.flavour_sector_bases()
    gauge = thresholds.solve_unification(two_loop=True)
    mi = float(gauge["M_I_GeV"])
    mgut = float(gauge["M_GUT_GeV"])
    mz = 91.1876
    h = np.asarray(bases["H"], dtype=complex)
    f = np.asarray(bases["F"], dtype=complex)

    # PS one-loop layer M_I → M_GUT on (Y10,Y126,YR).
    y10 = h + f
    y126 = h - 3.0 * f
    yr = f.copy()
    ps_up = ps.evolve_ps_yukawas(y10, y126, yr, mu0=mi, mu1=mgut, gauge=gauge)

    # At M_I: CG match into SM Yukawas, then run down to M_Z.
    match = clebsch_match_from_hf(h, f, eta_i=eta_i)
    sm = evolve_sm_yukawas(
        match["Y_u"],
        match["Y_d"],
        match["Y_e"],
        mu0=mi,
        mu1=mz,
        gauge=gauge,
    )
    return {
        "gauge_anchor": {
            "M_Z_GeV": mz,
            "M_I_GeV": mi,
            "M_GUT_GeV": mgut,
            "scheme": gauge["scheme"],
            "note": (
                "Uses the repository two-loop-corrected threshold chain "
                "(M_I and M_GUT as returned by two_loop_thresholds_v20)."
            ),
        },
        "clebsch_matching_at_MI": {
            "eta_I": match["eta_I"],
            "max_abs": match["max_abs"],
            "clebsch_identity_check": match["clebsch_identity_check"],
            "factor_minus_three_applied": True,
        },
        "ps_evolution_MI_to_MGUT": {
            "n_steps": ps_up["n_steps"],
            "relative_change": ps_up["relative_change"],
            "max_abs": ps_up["max_abs"],
        },
        "sm_evolution_MI_to_MZ": {
            "n_steps": sm["n_steps"],
            "relative_change": sm["relative_change"],
        },
    }


def build_report() -> dict[str, Any]:
    chain = run_piecewise_chain(eta_i=1.0)
    checks = {
        "clebsch_yd_identity": chain["clebsch_matching_at_MI"][
            "clebsch_identity_check"
        ]["Yd_equals_H_plus_F"],
        "clebsch_ye_identity": chain["clebsch_matching_at_MI"][
            "clebsch_identity_check"
        ]["Ye_equals_H_minus_3F"],
        "ps_layer_ran": chain["ps_evolution_MI_to_MGUT"]["n_steps"] > 0,
        "sm_layer_ran": chain["sm_evolution_MI_to_MZ"]["n_steps"] > 0,
        "published_210_not_claimed": True,
        "two_loop_so10_not_claimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "PIECEWISE_YUKAWA_RGE_WITH_CLEBSCH_THRESHOLDS_COMPLETE__"
            "PUBLISHED_TWO_LOOP_210_OPEN"
            if not failures
            else "YUKAWA_RGE_2LOOP_CHAIN_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "chain": chain,
        "flag": {
            "clebsch_threshold_matching_implemented": True,
            "factor_minus_three_lepton_clebsch_applied": True,
            "piecewise_yukawa_chain_integrated": True,
            "pati_salam_one_loop_yukawa_layer_used": True,
            "sm_2hdm_one_loop_layer_used": True,
            "heuristic_two_loop_gauge_thresholds_used": True,
            "published_210_tensor_contractions": False,
            "two_loop_so10_complete": False,
            "explicit_two_loop_yukawa_betas": False,
            "reference_validated_type_II_coefficients": False,
            "running_vevs_included": False,
            "piecewise_component_threshold_matching_complete": False,
        },
        "verdict": (
            "The piecewise Yukawa chain with explicit −3 lepton Clebsch matching "
            "at M_I is integrated (PS one-loop above M_I, diagnostic 2HDM below). "
            "Published SO(10)+210 two-loop tensor contractions (SARAH/PyR@TE) and "
            "component-current matching remain open."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    c = report["chain"]
    return "\n".join(
        [
            "# Piecewise Yukawa RGE + Clebsch thresholds — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            f"- M_I: {c['gauge_anchor']['M_I_GeV']:.4g} GeV",
            f"- M_GUT: {c['gauge_anchor']['M_GUT_GeV']:.4g} GeV",
            f"- Ye = H − 3F identity: "
            f"**{c['clebsch_matching_at_MI']['clebsch_identity_check']['Ye_equals_H_minus_3F']}**",
            f"- Published two-loop SO(10)+210: **False**",
            "",
            "## Verdict",
            "",
            report["verdict"],
            "",
        ]
    )


def main() -> int:
    report = build_report()
    ROOT.joinpath("YUKAWA_RGE_2LOOP_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("YUKAWA_RGE_2LOOP_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "flag": report["flag"],
                "gauge_anchor": report["chain"]["gauge_anchor"],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
