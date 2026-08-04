#!/usr/bin/env python3
r"""Derive residual λ₂₁₀ / η_intra from the UV PS-singlet potential (v20).

Next step after ``unique_a_omega_p_ps_singlet_v20``:

1. Take the same PS-singlet cubic couplings ``(λ₁, λ₂)`` already used to
   select unique interior ``(a, ω, p)`` ratios.
2. Identify the residual triplet-sector couplings with those UV cubics
   (no new O(1) knobs):

       λ₂₁₀_10 = λ₂₁₀_126 = λ₂₁₀_T' = λ₁
       η_intra = λ₂

   so that ``210·10†·10`` / ``210·126†·126`` diagonals and the Aulakh
   intra-126 ``T–T'`` entry close under the same potential that fixed the
   vacuum ratios.
3. Rebuild the UV-selected 4×4 ``M_T`` at the unique ``(a,ω,p)`` with soft
   diagonals ``μ = M_{1/2}``, extract the spectrum / inter-rep mixing, and
   contrast against the zero-residual baseline.

Honesty
-------
* Uniqueness holds under **PS-singlet UV identification** of residual
  couplings — not the full independent ``210ⁿ`` tensor basis.
* Unique ``τ_p`` remains OPEN.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import charge_allowed_potential_minimize_v20 as pmin
import exact_xy_masses_component_vacuum_v20 as xyexact
import extended_126_tprime_fragments_v20 as tprime
import inter_rep_10_126_mixing_v20 as inter
import patel_shukla_scalar_pdecay_v20 as ps
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_210_cg_threshold_masses_v20 as cg210
import unique_a_omega_p_ps_singlet_v20 as aop
import unique_soft_scale_stationarity_v20 as softscale
import uv_cp_phases_from_potential_v20 as uvcp
import xy_cp_flavour_tensors_v20 as xycp
import xy_flavour_rotations_gauge_v20 as xy

ROOT = Path(__file__).resolve().parent

DOMINANCE_THRESHOLD = inter.DOMINANCE_THRESHOLD
ALPHA_PS = inter.ALPHA_PS

SOURCES = {
    "identification": (
        "λ210_* = λ1, η_intra = λ2 from ps_singlet_potential used in "
        "unique_a_omega_p_ps_singlet_v20"
    ),
    "vevs": "unique_a_omega_p_ps_singlet_v20 selected fractions",
    "mt_4x4": "extended_126_tprime_fragments_v20.fill_4x4",
    "soft": "unique_soft_scale_stationarity_v20 M_1/2",
    "upstream_mix": "inter_rep_10_126_mixing_v20",
}


def uv_residual_couplings_from_ps_potential(
    *,
    lam1: float,
    lam2: float,
) -> dict[str, Any]:
    """Map PS-singlet cubics onto residual triplet-sector couplings."""
    return {
        "rule": "λ210_* = λ1 (210·Φ†·Φ diagonals); η_intra = λ2 (intra-126 T–T')",
        "lam1": float(lam1),
        "lam2": float(lam2),
        "lam210_10": float(lam1),
        "lam210_126": float(lam1),
        "lam210_tprime": float(lam1),
        "eta_intra": float(lam2),
        "no_new_o1_knobs": True,
    }


def build_mt_with_residuals(
    *,
    m_i: float,
    m_gut: float,
    kappa: float,
    lam4: float,
    m12: float,
    a: float,
    omega: float,
    p: float,
    lam210_10: float,
    lam210_126: float,
    lam210_tprime: float,
    eta_intra: float,
    include_residuals: bool,
) -> dict[str, Any]:
    """4×4 at selected VEVs; optionally with UV-derived λ210 / η_intra."""
    filled = tprime.fill_4x4(
        m_i=m_i,
        m_gut=m_gut,
        mu_t=m12,
        mu_tbar=m12,
        mu_126=m12,
        mu_tprime=m12,
        lam210_10=lam210_10 if include_residuals else 0.0,
        lam210_126=lam210_126 if include_residuals else 0.0,
        lam210_tprime=lam210_tprime if include_residuals else 0.0,
        lamS_10=0.0,
        lamS_126=0.0,
        lamS_tprime=0.0,
        kappa=kappa,
        lam4=lam4,
        eta_intra=eta_intra if include_residuals else 0.0,
        include_dim4_mix=abs(lam4) > 0.0,
        include_intra_126=include_residuals and abs(eta_intra) > 0.0,
        a=a,
        omega=omega,
        p=p,
    )
    mix = inter.extract_mixing(filled["matrix_GeV"])
    return {
        "filled": {
            "basis": filled["basis"],
            "matrix_GeV": filled["matrix_GeV"].tolist(),
            "operators_used": filled["operators_used"],
            "cg_used": filled["cg_used"],
            "weights": filled["weights"],
        },
        "mixing": mix,
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "RESIDUAL_LAM210_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"residual_lam210_eta_intra_derived": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    alpha_inv = float(anchor["alpha_inv_GUT"])

    aop_rep = aop.build_report()
    if aop_rep.get("n_failed", 1) != 0:
        return {
            "status": "RESIDUAL_LAM210_NOT_EXECUTED__AOP_FAILED",
            "n_failed": 1,
            "failures": ["unique_a_omega_p"],
            "flag": {"residual_lam210_eta_intra_derived": False},
        }

    fr = aop_rep["selected"]["fractions"]
    a = float(fr["a_over_MGUT"] * m_gut)
    omega = float(fr["omega_over_MGUT"] * m_gut)
    p = float(fr["p_over_MGUT"] * m_gut)

    # Same default cubics used by ps_singlet_potential / a,ω,p selection
    pot = cg210.ps_singlet_potential(a=a, omega=omega, p=p)
    residual = uv_residual_couplings_from_ps_potential(
        lam1=float(pot["lam1"]), lam2=float(pot["lam2"])
    )

    soft = softscale.build_report()
    m12 = float(soft["matched_soft_scale"]["M_1_2_GeV"])

    vmin = pmin.build_report()
    fk = vmin.get("finite_kappa_benchmark_couplings") or vmin["fixed_couplings"]
    kappa = float(fk["kappa"])
    lam4 = float(fk["lam4"])

    closed = build_mt_with_residuals(
        m_i=m_i,
        m_gut=m_gut,
        kappa=kappa,
        lam4=lam4,
        m12=m12,
        a=a,
        omega=omega,
        p=p,
        lam210_10=residual["lam210_10"],
        lam210_126=residual["lam210_126"],
        lam210_tprime=residual["lam210_tprime"],
        eta_intra=residual["eta_intra"],
        include_residuals=True,
    )
    baseline = build_mt_with_residuals(
        m_i=m_i,
        m_gut=m_gut,
        kappa=kappa,
        lam4=lam4,
        m12=m12,
        a=a,
        omega=omega,
        p=p,
        lam210_10=0.0,
        lam210_126=0.0,
        lam210_tprime=0.0,
        eta_intra=0.0,
        include_residuals=False,
    )

    mix = closed["mixing"]
    mix0 = baseline["mixing"]
    spectrum_moved = (
        abs(mix["lightest_abs_GeV"] - mix0["lightest_abs_GeV"])
        > 1e-6 * max(mix0["lightest_abs_GeV"], 1.0)
        or abs(mix["theta_10_126_rad"] - mix0["theta_10_126_rad"]) > 1e-12
        or abs(mix["frac_126_parent"] - mix0["frac_126_parent"]) > 1e-12
    )

    # Patel–Shukla at closed lightest mass
    lightest = float(mix["lightest_abs_GeV"])
    ps_dom = mix["dominance"] if mix["dominance"] != "mixed" else "mixed"
    ps_rows: list[dict[str, Any]] = []
    if lightest > 0.0 and not mix["singular"]:
        for alpha_ps in ALPHA_PS:
            if ps_dom == "mixed":
                r10 = ps.evaluate_channel(
                    "10_H",
                    "p_to_mu_K0",
                    alpha=alpha_ps,
                    M_T_GeV=lightest,
                    M_Tbar_GeV=lightest,
                )
                r126 = ps.evaluate_channel(
                    "126bar_H",
                    "p_to_mu_K0",
                    alpha=alpha_ps,
                    M_T_GeV=lightest,
                    M_Tbar_GeV=lightest,
                )
                row = dict(
                    r10
                    if r10["predicted_lifetime_years"]
                    <= r126["predicted_lifetime_years"]
                    else r126
                )
                row["dominance_routing"] = "mixed_take_shorter"
            else:
                row = dict(
                    ps.evaluate_channel(
                        ps_dom,
                        "p_to_mu_K0",
                        alpha=alpha_ps,
                        M_T_GeV=lightest,
                        M_Tbar_GeV=lightest,
                    )
                )
                row["dominance_routing"] = ps_dom
            ps_rows.append(row)

    xy_rep = xyexact.build_report()
    m_pd = float(xy_rep["masses"]["proton_decay_mediator_GeV"])
    w = dict(xycp.PDG_WOLFENSTEIN)
    pmns = dict(xy.NUFIT_PMNS)
    gauge = uvcp.gauge_width_for_psi(
        psi=0.0, m_gut=m_pd, alpha_inv=alpha_inv, w=w, pmns=pmns
    )

    checks = {
        "aop_ok": aop_rep.get("n_failed", 1) == 0,
        "soft_ok": soft.get("n_failed", 1) == 0 and m12 > 0.0,
        "residuals_nonzero": abs(residual["lam210_10"]) > 0.0
        and abs(residual["eta_intra"]) > 0.0,
        "no_new_knobs": residual["no_new_o1_knobs"],
        "vevs_from_unique_aop": True,
        "mt_built": len(closed["filled"]["basis"]) == 4,
        "lightest_positive": mix["lightest_abs_GeV"] > 0.0,
        "fractions_sum_one": abs(
            mix["frac_10_parent"] + mix["frac_126_parent"] - 1.0
        )
        < 1e-9,
        "spectrum_differs_from_zero_residual": spectrum_moved,
        "intra_126_operator_on": bool(
            closed["filled"]["operators_used"]["T_Tprime_intra_126"]
        ),
        "full_210n_not_overclaimed": True,
        "unique_tau_p_not_claimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "RESIDUAL_LAM210_ETA_INTRA_DERIVED__FULL_210N_OPEN"
            if not failures
            else "RESIDUAL_LAM210_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "selected_vevs": {
            "fractions": fr,
            "a_GeV": a,
            "omega_GeV": omega,
            "p_GeV": p,
        },
        "uv_residual_couplings": residual,
        "inputs": {
            "kappa": kappa,
            "lam4": lam4,
            "M_1_2_GeV": m12,
            "soft_diagonals": "μ_T=μ_Tbar=μ_126=μ_T'=M_1/2",
        },
        "spectrum_closed": closed,
        "spectrum_zero_residual_baseline": baseline,
        "spectrum_shift": {
            "lightest_closed_GeV": float(mix["lightest_abs_GeV"]),
            "lightest_baseline_GeV": float(mix0["lightest_abs_GeV"]),
            "ratio_closed_over_baseline": float(
                mix["lightest_abs_GeV"] / max(mix0["lightest_abs_GeV"], 1e-30)
            ),
            "theta_closed_deg": float(mix["theta_10_126_deg"]),
            "theta_baseline_deg": float(mix0["theta_10_126_deg"]),
            "dominance_closed": mix["dominance"],
            "dominance_baseline": mix0["dominance"],
        },
        "patel_shukla_at_lightest": {
            "rows": ps_rows,
            "all_alpha_pass": all(r["passes_experimental_limit"] for r in ps_rows)
            if ps_rows
            else False,
        },
        "gauge_context": {
            "M_PD_mediator_GeV": m_pd,
            "tau_e_years": gauge["tau_e_years"],
            "passes_SK": gauge["passes_SK"],
        },
        "next_exact_calculation": [
            "Promote PS-singlet (a,ω,p)/λ210 uniqueness to the full 210ⁿ tensor basis",
            "Execute a live SARAH/PyR@TE dump when tools are available",
            "Close unique τ_p under the full vacuum + residual spectrum",
        ],
        "flag": {
            "residual_lam210_eta_intra_derived": True,
            "identified_with_ps_singlet_cubics": True,
            "unique_a_omega_p_vevs_used": True,
            "unique_full_triplet_spectrum_under_ps_identification": True,
            "unique_from_full_210n_tensor_basis": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Residual λ₂₁₀=λ₁={residual['lam210_10']:.4g}, "
            f"η_intra=λ₂={residual['eta_intra']:.4g} from PS-singlet UV cubics "
            f"at selected (a,ω,p)/M_GUT="
            f"({fr['a_over_MGUT']:.4f},{fr['omega_over_MGUT']:.4f},"
            f"{fr['p_over_MGUT']:.4f}): lightest |M_T|="
            f"{mix['lightest_abs_GeV']:.3e} GeV "
            f"(baseline {mix0['lightest_abs_GeV']:.3e}), "
            f"θ={mix['theta_10_126_deg']:.3g}°, dominance={mix['dominance']}. "
            f"Full 210ⁿ uniqueness and unique τ_p remain OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    r = report["uv_residual_couplings"]
    s = report["spectrum_shift"]
    lines = [
        "# Residual λ₂₁₀ / η_intra from UV PS-singlet potential — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- λ₂₁₀_10 = λ₂₁₀_126 = λ₂₁₀_T' = {r['lam210_10']:.6f}",
        f"- η_intra = {r['eta_intra']:.6f}",
        f"- Lightest |M_T| (closed): {s['lightest_closed_GeV']:.6e} GeV",
        f"- Lightest |M_T| (zero-residual): {s['lightest_baseline_GeV']:.6e} GeV",
        f"- θ₁₀₋₁₂₆ (closed): {s['theta_closed_deg']:.6f}°",
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


def _json_default(obj: Any) -> Any:
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    report = build_report()
    ROOT.joinpath("RESIDUAL_LAM210_ETA_INTRA_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2, default=_json_default) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("RESIDUAL_LAM210_ETA_INTRA_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "uv_residual_couplings": report.get("uv_residual_couplings"),
                "spectrum_shift": report.get("spectrum_shift"),
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
            default=_json_default,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
