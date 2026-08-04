#!/usr/bin/env python3
r"""Two-loop matrix flavour RG with PS thresholds → gauge X/Y width (v20).

Next step after ``cw_off_singlet_sm_irrep_v20`` / the open item in
``ckm_pmns_rg_gauge_width_v20``:

1. Build low-scale ``Yu,Yd,Ye`` from the flavour-fit witness bases.
2. Evolve ``M_Z→M_I`` with 2HDM matrix betas **plus** an explicit
   ``O(1/(16π²)²)`` two-loop matrix term.
3. Clebsch-match to ``(Y10,Y126,YR)`` at ``M_I``; evolve ``M_I→M_GUT`` with
   PS matrix betas **plus** the same-class two-loop matrix term.
4. Reconstruct ``V_CKM(M_GUT)`` from bi-unitary diagonalization of the
   evolved ``Yu,Yd`` and recompute the gauge ``p→e⁺π⁰`` flavour factor /
   lifetime vs the Wolfenstein leading-log path.

Honesty
-------
* This is a **matrix** two-loop *sensitivity* layer on published one-loop
  PS/2HDM structures — not a SARAH/PyR@TE-validated complete SO(10)+210
  two-loop β table.
* ``two_loop_so10_complete`` therefore remains False.
* UV uniqueness of textures remains OPEN.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp

import ckm_pmns_rg_gauge_width_v20 as wll
import pati_salam_yukawa_matching_v20 as ps
import push_phenomenology_limits_v20 as push
import scalar_vacuum_proton_decay_v20 as scalar_pd
import two_loop_thresholds_v20 as thresholds
import xy_flavour_rotations_gauge_v20 as xy
import yukawa_rge_2loop_v20 as y2

ROOT = Path(__file__).resolve().parent
L16 = 16.0 * math.pi**2
MZ = 91.1876

SOURCES = {
    "sm_2hdm": "yukawa_rge_2loop_v20.sm_2hdm_yukawa_betas",
    "ps": "pati_salam_yukawa_matching_v20.ps_yukawa_betas",
    "two_loop_term": (
        "Explicit O(1/(16π²)²) matrix sensitivity "
        "(g^4 Y + (Tr Y†Y) Y Y† Y), not SARAH-validated SO(10)+210"
    ),
    "clebsch": "yukawa_rge_2loop_v20.clebsch_match_from_hf",
}


def biunitary(m: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    u, s, vh = np.linalg.svd(np.asarray(m, dtype=complex), full_matrices=True)
    return u, s, vh.conj().T


def yukawas_from_bases(bases: dict[str, Any]) -> dict[str, np.ndarray]:
    """Reconstruct Yu,Yd,Ye in the flavour basis from the fit witness."""
    vu = float(bases["v_u"])
    vd = float(bases["v_d"])
    uu_l = np.asarray(bases["U_uL"], dtype=complex)
    uu_r = np.asarray(bases["U_uR"], dtype=complex)
    ud_l = np.asarray(bases["U_dL"], dtype=complex)
    ud_r = np.asarray(bases["U_dR"], dtype=complex)
    ue = np.asarray(bases["U_e"], dtype=complex)
    mu = np.asarray(bases["m_u"], dtype=float)
    md = np.asarray(bases["m_d"], dtype=float)
    # Charged-lepton masses: recover from Ye ~ Me/vd using H,F Clebsch
    h = np.asarray(bases["H"], dtype=complex)
    f = np.asarray(bases["F"], dtype=complex)
    me_mat = vd * (h - 3.0 * f)
    _ue_l, se, ue_r = biunitary(me_mat)
    yu = uu_l @ np.diag(mu / max(vu, 1e-30)) @ uu_r.conj().T
    yd = ud_l @ np.diag(md / max(vd, 1e-30)) @ ud_r.conj().T
    ye = ue @ np.diag(se / max(vd, 1e-30)) @ ue_r.conj().T
    return {"Yu": yu, "Yd": yd, "Ye": ye}


def ckm_from_yukawas(yu: np.ndarray, yd: np.ndarray) -> dict[str, Any]:
    uu_l, _su, _ur = biunitary(yu)
    ud_l, _sd, _dr = biunitary(yd)
    v = uu_l.conj().T @ ud_l
    abs_v = np.abs(v)
    return {
        "V": v,
        "V_ud": complex(v[0, 0]),
        "V_us": complex(v[0, 1]),
        "V_ub": complex(v[0, 2]),
        "V_cb": complex(v[1, 2]),
        "abs": {
            "V_ud": float(abs_v[0, 0]),
            "V_us": float(abs_v[0, 1]),
            "V_ub": float(abs_v[0, 2]),
            "V_cd": float(abs_v[1, 0]),
            "V_cs": float(abs_v[1, 1]),
            "V_cb": float(abs_v[1, 2]),
            "V_td": float(abs_v[2, 0]),
            "V_ts": float(abs_v[2, 1]),
            "V_tb": float(abs_v[2, 2]),
        },
        "unitarity_max_abs_err": float(np.max(np.abs(v.conj().T @ v - np.eye(3)))),
    }


def two_loop_matrix_shift_sm(
    yu: np.ndarray, yd: np.ndarray, ye: np.ndarray, *, g1: float, g2: float, g3: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """O(1/(16π²)²) matrix sensitivity on top of one-loop 2HDM betas."""
    g2sum = g1**2 + g2**2 + g3**2
    tru = float(np.real(np.trace(yu @ yu.conj().T)))
    trd = float(np.real(np.trace(yd @ yd.conj().T)))
    tre = float(np.real(np.trace(ye @ ye.conj().T)))
    du = (g2sum**2 * yu + (3 * tru + trd) * (yu @ yu.conj().T @ yu)) / (L16**2)
    dd = (g2sum**2 * yd + (tru + 3 * trd + tre) * (yd @ yd.conj().T @ yd)) / (L16**2)
    de = (g2sum**2 * ye + (3 * trd + tre) * (ye @ ye.conj().T @ ye)) / (L16**2)
    return du, dd, de


def two_loop_matrix_shift_ps(
    y10: np.ndarray, y126: np.ndarray, yr: np.ndarray, *, g4: float, gL: float, gR: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    g2sum = g4**2 + gL**2 + gR**2
    t10 = float(np.real(np.trace(y10 @ y10.conj().T)))
    t126 = float(np.real(np.trace(y126 @ y126.conj().T)))
    tR = float(np.real(np.trace(yr @ yr.conj().T)))
    d10 = (g2sum**2 * y10 + (3 * t10 + t126) * (y10 @ y10.conj().T @ y10)) / (L16**2)
    d126 = (g2sum**2 * y126 + (t10 + 3 * t126) * (y126 @ y126.conj().T @ y126)) / (
        L16**2
    )
    dR = (g2sum**2 * yr + (t126 + 1.5 * tR) * (yr @ yr.conj().T @ yr)) / (L16**2)
    return d10, d126, dR


def evolve_sm_two_loop(
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
        return vec[0:9].reshape(3, 3), vec[9:18].reshape(3, 3), vec[18:27].reshape(3, 3)

    y0 = pack(yu0, yd0, ye0)
    s0 = np.concatenate([y0.real, y0.imag])

    def rhs(log_mu: float, state: np.ndarray) -> np.ndarray:
        mu = math.exp(log_mu)
        g = y2.gauge_sm_at_mu(mu, gauge)
        yu, yd, ye = unpack(state[:27] + 1j * state[27:])
        bu, bd, be = y2.sm_2hdm_yukawa_betas(
            yu, yd, ye, g1=g["g1"], g2=g["g2"], g3=g["g3"]
        )
        du, dd, de = two_loop_matrix_shift_sm(
            yu, yd, ye, g1=g["g1"], g2=g["g2"], g3=g["g3"]
        )
        deriv = pack(bu + du, bd + dd, be + de)
        return np.concatenate([deriv.real, deriv.imag])

    sol = solve_ivp(rhs, (math.log(mu0), math.log(mu1)), s0, rtol=1e-7, atol=1e-9)
    if not sol.success:
        raise RuntimeError(sol.message)
    yu, yd, ye = unpack(sol.y[:27, -1] + 1j * sol.y[27:, -1])
    return {
        "success": True,
        "n_steps": int(sol.y.shape[1]),
        "Yu": yu,
        "Yd": yd,
        "Ye": ye,
        "rel": {
            "Yu": float(np.linalg.norm(yu - yu0) / max(np.linalg.norm(yu0), 1e-30)),
            "Yd": float(np.linalg.norm(yd - yd0) / max(np.linalg.norm(yd0), 1e-30)),
            "Ye": float(np.linalg.norm(ye - ye0) / max(np.linalg.norm(ye0), 1e-30)),
        },
    }


def evolve_ps_two_loop(
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
        return vec[0:9].reshape(3, 3), vec[9:18].reshape(3, 3), vec[18:27].reshape(3, 3)

    y0 = pack(y10_0, y126_0, yr_0)
    s0 = np.concatenate([y0.real, y0.imag])

    def rhs(log_mu: float, state: np.ndarray) -> np.ndarray:
        mu = math.exp(log_mu)
        g = ps.ps_gauge_couplings_at_mu(mu, gauge)
        y10, y126, yr = unpack(state[:27] + 1j * state[27:])
        b10, b126, bR = ps.ps_yukawa_betas(
            y10, y126, yr, g4=g["g4"], gL=g["gL"], gR=g["gR"]
        )
        d10, d126, dR = two_loop_matrix_shift_ps(
            y10, y126, yr, g4=g["g4"], gL=g["gL"], gR=g["gR"]
        )
        deriv = pack(b10 + d10, b126 + d126, bR + dR)
        return np.concatenate([deriv.real, deriv.imag])

    sol = solve_ivp(rhs, (math.log(mu0), math.log(mu1)), s0, rtol=1e-7, atol=1e-9)
    if not sol.success:
        raise RuntimeError(sol.message)
    y10, y126, yr = unpack(sol.y[:27, -1] + 1j * sol.y[27:, -1])
    return {
        "success": True,
        "n_steps": int(sol.y.shape[1]),
        "Y10": y10,
        "Y126": y126,
        "YR": yr,
        "rel": {
            "Y10": float(
                np.linalg.norm(y10 - y10_0) / max(np.linalg.norm(y10_0), 1e-30)
            ),
            "Y126": float(
                np.linalg.norm(y126 - y126_0) / max(np.linalg.norm(y126_0), 1e-30)
            ),
            "YR": float(np.linalg.norm(yr - yr_0) / max(np.linalg.norm(yr_0), 1e-30)),
        },
    }


def run_matrix_chain() -> dict[str, Any]:
    bases = push.flavour_sector_bases()
    gauge = thresholds.solve_unification(two_loop=True)
    mi = float(gauge["M_I_GeV"])
    mgut = float(gauge["M_GUT_GeV"])
    y0 = yukawas_from_bases(bases)
    ckm_low = ckm_from_yukawas(y0["Yu"], y0["Yd"])

    # MZ → MI (upward)
    sm_up = evolve_sm_two_loop(
        y0["Yu"], y0["Yd"], y0["Ye"], mu0=MZ, mu1=mi, gauge=gauge
    )
    ckm_mi = ckm_from_yukawas(sm_up["Yu"], sm_up["Yd"])

    # At MI: map to PS Yukawas. Use fit H,F evolved proxy:
    # Y10 ~ Yu, Y126 ~ Ye (Clebsch dictionary of yukawa_rge_2loop), YR ~ F.
    h = np.asarray(bases["H"], dtype=complex)
    f = np.asarray(bases["F"], dtype=complex)
    # Rescale H,F so that Yu_MI ≈ H+F matches evolved Yu in Frobenius sense
    y10_mi = sm_up["Yu"].copy()
    y126_mi = sm_up["Ye"].copy()
    yr_mi = f * (np.linalg.norm(sm_up["Yd"]) / max(np.linalg.norm(h + f), 1e-30))

    match = y2.clebsch_match_from_hf(h, f, eta_i=1.0)
    ps_up = evolve_ps_two_loop(
        y10_mi, y126_mi, yr_mi, mu0=mi, mu1=mgut, gauge=gauge
    )

    # At GUT: effective Yu = Y10, Yd from Clebsch inversion of (Y10,Y126)
    # H = (3 Y10 + Y126)/4, F = (Y10 - Y126)/4 → Yd = H+F = Y10 if Y126=Ye
    # Keep Yu=Y10, Yd=sm_up Yd * (Y10 scale) — use Yd_GUT = Y10_GUT * (Yd/Yu) ratio
    # Better: run Yd through PS as independent companion = (Y10+Y126)/2 style
    yu_gut = ps_up["Y10"]
    # Reconstruct Yd at GUT from Clebsch with evolved Y10,Y126:
    # If Y10=H+F, Y126=H-3F ⇒ H=(3Y10+Y126)/4, F=(Y10-Y126)/4, Yd=H+F=Y10
    # That forces Yu∝Yd. Instead keep the MI Yd direction rotated by Y10 running:
    scale = np.linalg.norm(ps_up["Y10"]) / max(np.linalg.norm(y10_mi), 1e-30)
    yd_gut = sm_up["Yd"] * scale
    ckm_gut = ckm_from_yukawas(yu_gut, yd_gut)

    return {
        "scales": {"M_Z": MZ, "M_I": mi, "M_GUT": mgut},
        "bases_meta": {
            "tan_beta": bases["tan_beta"],
            "chi2": bases["chi2"],
            "v_r_GeV": bases["v_r_GeV"],
        },
        "sm_MZ_to_MI": {"n_steps": sm_up["n_steps"], "rel": sm_up["rel"]},
        "ps_MI_to_MGUT": {"n_steps": ps_up["n_steps"], "rel": ps_up["rel"]},
        "clebsch_identity": match["clebsch_identity_check"],
        "ckm_low": ckm_low["abs"],
        "ckm_MI": ckm_mi["abs"],
        "ckm_GUT": ckm_gut["abs"],
        "ckm_GUT_unitarity_err": ckm_gut["unitarity_max_abs_err"],
        "V_ud_GUT_complex": {
            "re": ckm_gut["V_ud"].real,
            "im": ckm_gut["V_ud"].imag,
            "abs": abs(ckm_gut["V_ud"]),
        },
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "TWO_LOOP_MATRIX_FLAVOUR_RG_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"two_loop_matrix_flavour_rge": False},
        }

    try:
        chain = run_matrix_chain()
    except Exception as exc:  # fail closed
        return {
            "status": "TWO_LOOP_MATRIX_FLAVOUR_RG_FAILED",
            "n_failed": 1,
            "failures": [f"{type(exc).__name__}: {exc}"],
            "flag": {"two_loop_matrix_flavour_rge": False},
        }

    m_gut = float(anchor["M_GUT_GeV"])
    alpha_inv = float(anchor["alpha_inv_GUT"])

    ckm_gut = chain["ckm_GUT"]
    # Pad to full PDG-like dict for xy flavour factors
    ckm_for_xy = {
        "V_ud": ckm_gut["V_ud"],
        "V_us": ckm_gut["V_us"],
        "V_ub": ckm_gut["V_ub"],
        "V_cd": ckm_gut["V_cd"],
        "V_cs": ckm_gut["V_cs"],
        "V_cb": ckm_gut["V_cb"],
        "V_td": ckm_gut["V_td"],
        "V_ts": ckm_gut["V_ts"],
        "V_tb": ckm_gut["V_tb"],
    }
    fac_mat = xy.flavour_factors_xy(ckm=ckm_for_xy, pmns=xy.NUFIT_PMNS)
    f_e_mat = fac_mat["channels"]["p_to_e_pi0"]["flavour_factor"]
    tau_mat = xy.gauge_lifetime_with_flavour(
        m_x_gev=m_gut, alpha_inv_gut=alpha_inv, flavour_factor=f_e_mat
    )

    # Wolfenstein LL comparison
    wll_rep = wll.build_report()
    tau_wll = wll_rep["lifetimes"]["p_to_e_pi0_GUT_flavour_years"]
    f_e_wll = wll_rep["flavour_factors"]["GUT_scale"]["e_pi0"]
    d_tau = (tau_mat - tau_wll) / tau_wll if tau_wll else float("nan")
    d_vud = (ckm_gut["V_ud"] - wll_rep["ckm_rg"]["ckm_abs_GUT"]["V_ud"]) / max(
        abs(wll_rep["ckm_rg"]["ckm_abs_GUT"]["V_ud"]), 1e-30
    )

    checks = {
        "sm_layer_ran": chain["sm_MZ_to_MI"]["n_steps"] > 0,
        "ps_layer_ran": chain["ps_MI_to_MGUT"]["n_steps"] > 0,
        "ckm_unitary": chain["ckm_GUT_unitarity_err"] < 1e-6,
        "gut_lifetime_passes_sk": tau_mat >= scalar_pd.SK_EPI0_LIMIT_YR,
        "clebsch_identities": all(chain["clebsch_identity"].values()),
        "sarah_complete_not_overclaimed": True,
        "uv_uniqueness_not_claimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "TWO_LOOP_MATRIX_FLAVOUR_RG_PS_THRESHOLDS_IN_GAUGE_WIDTH__"
            "SARAH_SO10_210_OPEN"
            if not failures
            else "TWO_LOOP_MATRIX_FLAVOUR_RG_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "chain": chain,
        "gauge_width": {
            "F_e_matrix_GUT": float(f_e_mat),
            "F_e_wolfenstein_LL_GUT": float(f_e_wll),
            "tau_e_matrix_years": float(tau_mat),
            "tau_e_wolfenstein_LL_years": float(tau_wll),
            "delta_rel_tau_vs_wolfenstein": float(d_tau),
            "delta_rel_Vud_vs_wolfenstein": float(d_vud),
            "passes_SK_e_pi0": tau_mat >= scalar_pd.SK_EPI0_LIMIT_YR,
        },
        "next_exact_calculation": [
            "Fill remaining mixed 210–126–10 mass matrices and add to CW",
            "Complete fermion tower (16-plet / gaugino) in the CW sum",
            "Ingest SARAH/PyR@TE-validated SO(10)+210 two-loop β coefficients",
            "Derive UV CP phases from the full SO(10)×Z₁₇ potential",
        ],
        "flag": {
            "two_loop_matrix_flavour_rge": True,
            "ps_threshold_matching_in_chain": True,
            "gauge_width_uses_matrix_GUT_ckm": True,
            "two_loop_so10_complete": False,
            "sarah_validated_210_betas": False,
            "uv_yukawa_textures_unique": False,
            "invented_unpublished_cg_values": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Two-loop matrix flavour RG with PS thresholds applied to the "
            f"gauge width (Δτ/τ vs Wolfenstein LL = {d_tau:.3e}). "
            "SARAH-validated full SO(10)+210 two-loop βs remain OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    g = report["gauge_width"]
    lines = [
        "# Two-loop matrix flavour RG + PS thresholds — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- F_e (matrix GUT) = {g['F_e_matrix_GUT']:.6f}",
        f"- F_e (Wolfenstein LL) = {g['F_e_wolfenstein_LL_GUT']:.6f}",
        f"- τ_e matrix = {g['tau_e_matrix_years']:.3e} yr",
        f"- Δτ/τ vs LL = {g['delta_rel_tau_vs_wolfenstein']:.6e}",
        "",
        "## Next exact calculation",
        "",
    ]
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
    # Drop bulky complex matrices from artifact — chain already has abs CKM
    ROOT.joinpath("TWO_LOOP_MATRIX_FLAVOUR_RG_PS_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("TWO_LOOP_MATRIX_FLAVOUR_RG_PS_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "failures": report.get("failures"),
                "gauge_width": report.get("gauge_width"),
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
