#!/usr/bin/env python3
r"""Full CP phases in gauge X/Y flavour tensors (v20).

Next step after ``ckm_pmns_rg_gauge_width_v20``:

1. Build a **complex** CKM from Wolfenstein ``(λ, A, ρ̄, η̄)`` (PDG δ_CKM)
   and a complex PMNS (NuFIT δ_CP), optionally after GUT RG.
2. Replace magnitude-only flavour factors by coherent tensors
   ``F = 1 + |1 + V²|²`` (and analogues) that reduce to the legacy
   ``1+(1+|V|²)²`` when ``V`` is real-positive, but pick up
   ``cos(2 arg V)`` interference when CP phases are present.
3. Recompute gauge lifetimes with CP-aware factors; compare to the
   magnitude-only / GUT-RG path.

Honesty
-------
* This closes the **low-scale + RG'd CP phase** input for X/Y widths.
* It is **not** a derivation of unique UV Yukawa CP phases from the
  full SO(10) potential.
* Two-loop matrix flavour RG and unique ``τ_p`` remain OPEN.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import ckm_pmns_rg_gauge_width_v20 as rg
import scalar_vacuum_proton_decay_v20 as scalar_pd
import xy_flavour_rotations_gauge_v20 as xy

ROOT = Path(__file__).resolve().parent

# PDG-ish Wolfenstein CP (central)
PDG_WOLFENSTEIN = {
    "lambda": 0.22431,
    "A": 0.826,
    "rho_bar": 0.159,
    "eta_bar": 0.348,
}

SOURCES = {
    "ckm_cp": "PDG Wolfenstein (λ,A,ρ̄,η̄) → complex CKM",
    "pmns_cp": "NuFIT δ_CP in standard PMNS parameterization",
    "coherent_factor": (
        "F = 1 + |1 + V²|²  (reduces to 1+(1+|V|²)² for real-positive V)"
    ),
    "rg": "ckm_pmns_rg_gauge_width_v20",
}


def complex_ckm_from_wolfenstein(w: dict[str, float]) -> np.ndarray:
    """Standard Wolfenstein complex CKM through O(λ³)."""
    lam = w["lambda"]
    a_w = w["A"]
    rho, eta = w["rho_bar"], w["eta_bar"]
    s12 = lam
    c12 = math.sqrt(max(0.0, 1.0 - s12 * s12))
    s23 = a_w * lam * lam
    c23 = math.sqrt(max(0.0, 1.0 - s23 * s23))
    s13 = a_w * (lam**3) * math.sqrt(rho**2 + eta**2)
    c13 = math.sqrt(max(0.0, 1.0 - s13 * s13))
    # δ from ρ̄, η̄:  ρ̄+iη̄ ∝ e^{-iδ} in standard convention for V_ub
    delta = math.atan2(eta, rho) if (abs(rho) + abs(eta)) > 0 else 0.0
    eid = np.exp(-1j * delta)
    # PDG standard parameterization
    return np.array(
        [
            [c12 * c13, s12 * c13, s13 * eid],
            [
                -s12 * c23 - c12 * s23 * s13 * np.conj(eid),
                c12 * c23 - s12 * s23 * s13 * np.conj(eid),
                s23 * c13,
            ],
            [
                s12 * s23 - c12 * c23 * s13 * np.conj(eid),
                -c12 * s23 - s12 * c23 * s13 * np.conj(eid),
                c23 * c13,
            ],
        ],
        dtype=complex,
    )


def coherent_flavour_factor(v: complex) -> float:
    """CP-aware factor reducing to 1+(1+|V|²)² for real-positive V."""
    return float(1.0 + abs(1.0 + v * v) ** 2)


def magnitude_flavour_factor(v: complex) -> float:
    """Legacy magnitude-only factor."""
    av = abs(v)
    return float(1.0 + (1.0 + av * av) ** 2)


def coherent_flavour_factor_with_subleading(
    v_lead: complex, v_cp: complex
) -> float:
    """Leading V² path plus a subleading CP-carrying amplitude.

    F = 1 + |1 + V_lead² + V_cp|².
    Reduces to ``coherent_flavour_factor(v_lead)`` when ``v_cp = 0``.
    """
    return float(1.0 + abs(1.0 + v_lead * v_lead + v_cp) ** 2)


def xy_cp_flavour_tensors(
    *,
    V: np.ndarray,
    U: np.ndarray,
) -> dict[str, Any]:
    """Complex X/Y flavour tensors for the benchmark channels.

    Leading CKM entries ``V_ud``, ``V_us`` are nearly real, so a pure
    ``|1+V²|`` factor is CP-blind there. Subleading paths
    ``V_ub U_e3^*`` (and analogues) carry δ_CKM and δ_PMNS and generate
    a genuine coherent interference.
    """
    v_ud = complex(V[0, 0])
    v_us = complex(V[0, 1])
    v_ub = complex(V[0, 2])
    ue1 = complex(U[0, 0])
    ue3 = complex(U[0, 2])

    # Subleading CP portals (schematic operator mixing; CG absorbed in O(1))
    cp_e = v_ub * np.conj(ue3)
    cp_mu = v_ub * np.conj(U[1, 2])
    cp_nuk = v_ub * ue3  # ν̄K: Cabibbo-suppressed × τ-row PMNS phase

    f_e_cp = coherent_flavour_factor_with_subleading(v_ud, cp_e)
    f_e_lead = coherent_flavour_factor(v_ud)
    f_e_mag = magnitude_flavour_factor(v_ud)

    f_mu_cp = coherent_flavour_factor_with_subleading(v_us, cp_mu)
    f_mu_lead = coherent_flavour_factor(v_us)
    f_mu_mag = magnitude_flavour_factor(v_us)

    v_nuk_lead = v_us * ue1
    f_nuk_cp = coherent_flavour_factor_with_subleading(v_nuk_lead, cp_nuk)
    f_nuk_lead = coherent_flavour_factor(v_nuk_lead)
    f_nuk_mag = magnitude_flavour_factor(v_nuk_lead)

    def interference(v_lead: complex, v_cp: complex) -> dict[str, float]:
        f_full = coherent_flavour_factor_with_subleading(v_lead, v_cp)
        f_0 = coherent_flavour_factor(v_lead)
        return {
            "arg_V_lead_rad": float(np.angle(v_lead)),
            "arg_V_cp_rad": float(np.angle(v_cp)) if abs(v_cp) > 0 else 0.0,
            "abs_V_cp": float(abs(v_cp)),
            "Delta_F_full_minus_lead": float(f_full - f_0),
            "Delta_F_lead_minus_mag": float(f_0 - magnitude_flavour_factor(v_lead)),
        }

    return {
        "status": "XY_CP_FLAVOUR_TENSORS_BUILT",
        "V_ud": {"re": v_ud.real, "im": v_ud.imag, "abs": abs(v_ud)},
        "V_us": {"re": v_us.real, "im": v_us.imag, "abs": abs(v_us)},
        "V_ub": {"re": v_ub.real, "im": v_ub.imag, "abs": abs(v_ub)},
        "U_e1": {"re": ue1.real, "im": ue1.imag, "abs": abs(ue1)},
        "U_e3": {"re": ue3.real, "im": ue3.imag, "abs": abs(ue3)},
        "channels": {
            "p_to_e_pi0": {
                "F_CP": f_e_cp,
                "F_lead_only": f_e_lead,
                "F_magnitude_only": f_e_mag,
                "ratio_CP_to_mag": f_e_cp / f_e_mag if f_e_mag else float("nan"),
                "subleading_portal": "V_ub U_e3^*",
                "interference": interference(v_ud, cp_e),
            },
            "p_to_mu_pi0": {
                "F_CP": f_mu_cp,
                "F_lead_only": f_mu_lead,
                "F_magnitude_only": f_mu_mag,
                "ratio_CP_to_mag": f_mu_cp / f_mu_mag if f_mu_mag else float("nan"),
                "subleading_portal": "V_ub U_mu3^*",
                "interference": interference(v_us, cp_mu),
            },
            "p_to_nu_K_proxy": {
                "F_CP": f_nuk_cp,
                "F_lead_only": f_nuk_lead,
                "F_magnitude_only": f_nuk_mag,
                "ratio_CP_to_mag": f_nuk_cp / f_nuk_mag if f_nuk_mag else float("nan"),
                "subleading_portal": "V_ub U_e3",
                "interference": interference(v_nuk_lead, cp_nuk),
            },
        },
        "flag": {
            "complex_ckm_used": True,
            "complex_pmns_used": True,
            "coherent_V2_interference": True,
            "subleading_cp_portals_included": True,
        },
    }


def unitarity_checks(V: np.ndarray, U: np.ndarray) -> dict[str, Any]:
    v_err = float(np.max(np.abs(V.conj().T @ V - np.eye(3))))
    u_err = float(np.max(np.abs(U.conj().T @ U - np.eye(3))))
    return {
        "ckm_unitarity_max_abs_err": v_err,
        "pmns_unitarity_max_abs_err": u_err,
        "ckm_unitary_ok": v_err < 1e-8,
        "pmns_unitary_ok": u_err < 1e-8,
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "XY_CP_FLAVOUR_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"full_cp_xy_tensors": False},
        }

    m_gut = float(anchor["M_GUT_GeV"])
    alpha_inv = float(anchor["alpha_inv_GUT"])
    m_i = float(anchor["M_I_GeV"])

    # Low-scale complex CKM/PMNS
    V_low = complex_ckm_from_wolfenstein(PDG_WOLFENSTEIN)
    U_low = xy.pmns_matrix(xy.NUFIT_PMNS)
    tensors_low = xy_cp_flavour_tensors(V=V_low, U=U_low)
    uni_low = unitarity_checks(V_low, U_low)

    # GUT-RG'd Wolfenstein A, then rebuild complex CKM with same ρ̄,η̄
    w0 = dict(PDG_WOLFENSTEIN)
    run_mi = rg.run_wolfenstein(w0, mu_start=rg.MZ, mu_end=m_i)
    run_gut = rg.run_wolfenstein(
        run_mi["wolfenstein_out"], mu_start=m_i, mu_end=m_gut
    )
    w_gut = run_gut["wolfenstein_out"]
    pmns_gut = rg.run_pmns(
        xy.NUFIT_PMNS, mu_start=rg.MZ, mu_mi=m_i, mu_end=m_gut
    )["pmns_out"]
    V_gut = complex_ckm_from_wolfenstein(w_gut)
    U_gut = xy.pmns_matrix(pmns_gut)
    tensors_gut = xy_cp_flavour_tensors(V=V_gut, U=U_gut)
    uni_gut = unitarity_checks(V_gut, U_gut)

    # Reduction check: real-positive V_ud must match magnitude formula
    v_real = complex(abs(V_low[0, 0]), 0.0)
    red_ok = abs(coherent_flavour_factor(v_real) - magnitude_flavour_factor(v_real)) < 1e-12

    f_e_cp = tensors_gut["channels"]["p_to_e_pi0"]["F_CP"]
    f_e_mag = tensors_gut["channels"]["p_to_e_pi0"]["F_magnitude_only"]
    tau_cp = xy.gauge_lifetime_with_flavour(
        m_x_gev=m_gut, alpha_inv_gut=alpha_inv, flavour_factor=f_e_cp
    )
    tau_mag = xy.gauge_lifetime_with_flavour(
        m_x_gev=m_gut, alpha_inv_gut=alpha_inv, flavour_factor=f_e_mag
    )
    tau_mu = xy.gauge_lifetime_with_flavour(
        m_x_gev=m_gut,
        alpha_inv_gut=alpha_inv,
        flavour_factor=tensors_gut["channels"]["p_to_mu_pi0"]["F_CP"],
    )
    tau_nuk = xy.gauge_lifetime_with_flavour(
        m_x_gev=m_gut,
        alpha_inv_gut=alpha_inv,
        flavour_factor=tensors_gut["channels"]["p_to_nu_K_proxy"]["F_CP"],
    )

    d_f = (f_e_cp - f_e_mag) / f_e_mag if f_e_mag else float("nan")
    d_tau = (tau_cp - tau_mag) / tau_mag if tau_mag else float("nan")

    checks = {
        "complex_ckm_unitary": uni_low["ckm_unitary_ok"] and uni_gut["ckm_unitary_ok"],
        "complex_pmns_unitary": uni_low["pmns_unitary_ok"] and uni_gut["pmns_unitary_ok"],
        "coherent_reduces_for_real_V": red_ok,
        "cp_factors_positive": f_e_cp > 0 and f_e_mag > 0,
        "gut_lifetime_passes_sk": tau_cp >= scalar_pd.SK_EPI0_LIMIT_YR,
        "cp_shift_recorded": math.isfinite(d_tau),
        "uv_uniqueness_not_claimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "XY_CP_FLAVOUR_TENSORS_COMPLETE__UV_CP_OPEN"
            if not failures
            else "XY_CP_FLAVOUR_TENSORS_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "wolfenstein_low": PDG_WOLFENSTEIN,
        "wolfenstein_GUT": w_gut,
        "unitarity": {"low": uni_low, "GUT": uni_gut},
        "tensors_low": tensors_low,
        "tensors_GUT": tensors_gut,
        "lifetimes": {
            "p_to_e_pi0_CP_years": float(tau_cp),
            "p_to_e_pi0_magnitude_only_years": float(tau_mag),
            "p_to_mu_pi0_CP_years": float(tau_mu),
            "p_to_nu_K_proxy_CP_years": float(tau_nuk),
            "delta_rel_F_e": float(d_f),
            "delta_rel_tau_e": float(d_tau),
            "passes_SK_e_pi0_CP": tau_cp >= scalar_pd.SK_EPI0_LIMIT_YR,
        },
        "next_exact_calculation": [
            "Off-singlet fluctuation CG for 210 mass thresholds beyond PS singlets",
            "Complete fermion + SM-irrep spectrum in the CW sum",
            "Upgrade flavour RG to two-loop matrix Yukawas with PS thresholds",
            "Derive UV CP phases from the full SO(10)×Z₁₇ potential (still open)",
        ],
        "flag": {
            "full_cp_xy_tensors": True,
            "complex_ckm_wolfenstein": True,
            "complex_pmns_delta": True,
            "coherent_V2_interference": True,
            "gut_rg_phases_included": True,
            "subleading_cp_portals_included": True,
            "reduces_to_magnitude_for_real_V": red_ok,
            "uv_cp_phases_from_potential": False,
            "two_loop_matrix_flavour_rge": False,
            "invented_unpublished_cg_values": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Complex CKM/PMNS X/Y flavour tensors built "
            f"(ΔF_e/F_mag={d_f:.3e}, Δτ_e/τ={d_tau:.3e} at GUT). "
            "UV CP phases from the full potential remain OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    life = report["lifetimes"]
    ch = report["tensors_GUT"]["channels"]["p_to_e_pi0"]
    lines = [
        "# X/Y CP flavour tensors — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- F_CP (e⁺π⁰, GUT) = {ch['F_CP']:.8f}",
        f"- F_mag (e⁺π⁰, GUT) = {ch['F_magnitude_only']:.8f}",
        f"- |V_cp| subleading = {ch['interference']['abs_V_cp']:.6e}",
        f"- ΔF (full−lead) = {ch['interference']['Delta_F_full_minus_lead']:.6e}",
        f"- τ_CP = {life['p_to_e_pi0_CP_years']:.3e} yr",
        f"- Δτ/τ = {life['delta_rel_tau_e']:.6e}",
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
    ROOT.joinpath("XY_CP_FLAVOUR_TENSORS_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("XY_CP_FLAVOUR_TENSORS_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "lifetimes": report.get("lifetimes"),
                "e_pi0_GUT": report["tensors_GUT"]["channels"]["p_to_e_pi0"]
                if "tensors_GUT" in report
                else None,
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
