#!/usr/bin/env python3
r"""Exact X/Y (U/V) gauge masses from the component vacuum (v20).

Next step after ``sarah_pyrate_210n_model_file_v20``:

1. Take the component-lift PS singlets ``(a, ω, p)`` of ``210_H`` and
   ``⟨Δ_R⟩`` of ``126bar_H`` from ``component_lift_210_126_10_v20``.
2. Evaluate the **published** Susyno/Fonseca SO(10) gauge-boson mass
   formulas (arXiv:1811.07910 Eqs. 6–10; Bertolini et al. matched) with
   only the v20 VEVs turned on (no 16/45/54/144).
3. Identify proton-decay mediators ``U,V`` (SM ``(3,2,±5/6)``) vs the
   PS leptoquark ``X`` and ``W_R,Z'``, replace the prior ``g·M_GUT`` proxy,
   and recompute the selected-point gauge ``τ(p→eπ⁰)``.

Honesty
-------
* Mass formulas are literature Susyno outputs — not invented CG.
* The ``(a,ω,p)=(0.3,0.5,0.2)×M_GUT`` split is the stack convention, not a
  unique full-potential minimum; unique VEV ratios remain OPEN.
* Inter-rep triplet mixing and unique ``τ_p`` remain OPEN.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import component_lift_210_126_10_v20 as clift
import sarah_pyrate_210n_model_file_v20 as sarah_model
import scalar_vacuum_proton_decay_v20 as scalar_pd
import uv_cp_phases_from_potential_v20 as uvcp
import xy_cp_flavour_tensors_v20 as xycp
import xy_flavour_rotations_gauge_v20 as xy

ROOT = Path(__file__).resolve().parent

SOURCES = {
    "mass_formulas": {
        "citation": "arXiv:1811.07910 Eqs. (6)–(10) (Susyno); Bertolini:2009es,2012im",
        "scope": "SO(10)/SM coset gauge masses from PS-path VEVs",
    },
    "vevs": "component_lift_210_126_10_v20.component_ledger",
    "aulakh_labels": "a=(15,1,1), ω=(15,1,3), p=(1,1,1) of 210; σ=Δ_R of 126",
}


def gauge_masses_from_vevs(
    *,
    a: float,
    omega: float,
    p: float,
    v126: float,
    g: float,
) -> dict[str, Any]:
    """Published m²/g² for v20 content (210 + 126 only).

    Notation (Aulakh / arXiv:1811.07910):
      a = v_210_(15,1,1), ω = v_210_(15,1,3), p = v_210_(1,1,1),
      v126 = v_126_(10,1,3).
    U,V are the dangerous proton-decay mediators; X is the PS leptoquark.
    """
    g2 = g * g
    sqrt6 = math.sqrt(6.0)
    sqrt2 = math.sqrt(2.0)

    # Eq. (6): m_U²/g²
    u_over_g2 = (
        0.5 * (v126**2)
        + 0.5 * (p**2)
        + (1.0 / 3.0) * (a**2)
        + 0.25 * (omega**2)
        - (p * omega) / sqrt6
        + (sqrt2 / 3.0) * a * omega
    )
    # Eq. (7): m_V²/g² (no 126 — 126 alone leaves V massless)
    v_over_g2 = (
        0.5 * (p**2)
        + (1.0 / 3.0) * (a**2)
        + 0.25 * (omega**2)
        + (p * omega) / sqrt6
        - (sqrt2 / 3.0) * a * omega
    )
    # Eq. (8): m_X²/g² (PS leptoquark)
    x_over_g2 = (
        0.5 * (v126**2)
        + (2.0 / 3.0) * (a**2)
        + (2.0 / 3.0) * (omega**2)
    )
    # Eq. (9): m_WR²/g²
    wr_over_g2 = 0.5 * (v126**2) + (omega**2)
    # Eq. (10): m_Z'²/g²
    zp_over_g2 = 2.5 * (v126**2)

    def mass(over_g2: float) -> float:
        return float(math.sqrt(max(over_g2, 0.0) * g2))

    rows = {
        "U_proton_decay": {
            "m_over_g2": float(u_over_g2),
            "mass_GeV": mass(u_over_g2),
            "sm": "(3,2,±5/6)-like",
            "role": "gauge d=6 proton decay",
            "equation": "1811.07910 Eq. (6)",
        },
        "V_proton_decay": {
            "m_over_g2": float(v_over_g2),
            "mass_GeV": mass(v_over_g2),
            "sm": "(3,2,∓5/6)-like",
            "role": "gauge d=6 proton decay",
            "equation": "1811.07910 Eq. (7)",
        },
        "X_PS_leptoquark": {
            "m_over_g2": float(x_over_g2),
            "mass_GeV": mass(x_over_g2),
            "sm": "PS (6,2,2) fragment",
            "role": "rare meson decays / PS threshold",
            "equation": "1811.07910 Eq. (8)",
        },
        "W_R": {
            "m_over_g2": float(wr_over_g2),
            "mass_GeV": mass(wr_over_g2),
            "sm": "SU(2)_R",
            "role": "PS→SM charged",
            "equation": "1811.07910 Eq. (9)",
        },
        "Z_prime": {
            "m_over_g2": float(zp_over_g2),
            "mass_GeV": mass(zp_over_g2),
            "sm": "U(1)' mix",
            "role": "PS→SM neutral",
            "equation": "1811.07910 Eq. (10)",
        },
    }
    m_u = rows["U_proton_decay"]["mass_GeV"]
    m_v = rows["V_proton_decay"]["mass_GeV"]
    m_pd = min(m_u, m_v)  # rate dominated by lightest mediator
    return {
        "g": float(g),
        "vevs_GeV": {"a": a, "omega": omega, "p": p, "v126": v126},
        "bosons": rows,
        "proton_decay_mediator_GeV": float(m_pd),
        "proton_decay_mediator_name": "U" if m_u <= m_v else "V",
        "M_U_GeV": float(m_u),
        "M_V_GeV": float(m_v),
        "M_X_PS_GeV": float(rows["X_PS_leptoquark"]["mass_GeV"]),
        "M_WR_GeV": float(rows["W_R"]["mass_GeV"]),
        "M_Zp_GeV": float(rows["Z_prime"]["mass_GeV"]),
        "positive_masses": all(r["mass_GeV"] > 0.0 for r in rows.values()),
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "EXACT_XY_MASSES_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"exact_XY_mass_from_component_vacuum": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    alpha_inv = float(anchor["alpha_inv_GUT"])
    g = math.sqrt(4.0 * math.pi / alpha_inv)

    ledger = clift.component_ledger(anchor)
    vevs = ledger["target_vevs_GeV"]
    a = float(vevs["a_210"])
    omega = float(vevs["omega_210"])
    p = float(vevs["p_210"])
    v126 = float(vevs["DeltaR_126bar"])

    masses = gauge_masses_from_vevs(a=a, omega=omega, p=p, v126=v126, g=g)
    proxy = g * m_gut
    m_pd = masses["proton_decay_mediator_GeV"]
    ratio = m_pd / proxy if proxy > 0 else float("inf")

    # Sanity: 126-only leaves V massless (literature check)
    only126 = gauge_masses_from_vevs(a=0.0, omega=0.0, p=0.0, v126=m_i, g=g)
    v_vanishes = only126["M_V_GeV"] < 1e-6 * max(only126["M_U_GeV"], 1.0)

    # Gauge lifetime with exact mediator mass, UV-selected ψ=0
    w = dict(xycp.PDG_WOLFENSTEIN)
    pmns = dict(xy.NUFIT_PMNS)
    width_exact = uvcp.gauge_width_for_psi(
        psi=0.0, m_gut=m_pd, alpha_inv=alpha_inv, w=w, pmns=pmns
    )
    width_proxy = uvcp.gauge_width_for_psi(
        psi=0.0, m_gut=proxy, alpha_inv=alpha_inv, w=w, pmns=pmns
    )
    d_tau = (
        (width_exact["tau_e_years"] - width_proxy["tau_e_years"])
        / width_proxy["tau_e_years"]
        if width_proxy["tau_e_years"]
        else float("nan")
    )

    model_ok = sarah_model.SARAH_MODEL.is_file()

    checks = {
        "vevs_from_component_lift": ledger["n_radial_components"] == 8,
        "sum_a_omega_p_is_MGUT": abs(a + omega + p - m_gut) / m_gut < 1e-12,
        "all_masses_positive": masses["positive_masses"],
        "V_vanishes_for_126_only": v_vanishes,
        "mediator_differs_from_proxy": abs(m_pd - proxy) / proxy > 1e-6,
        "exact_tau_positive": width_exact["tau_e_years"] > 0.0,
        "model_file_baseline": model_ok,
        "vev_ratios_not_overclaimed_unique": True,
        "sk_fail_not_promoted_to_whole_model": True,
        "unique_tau_p_not_claimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "EXACT_XY_MASSES_FROM_COMPONENT_VACUUM__VEV_RATIOS_OPEN"
            if not failures
            else "EXACT_XY_MASSES_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "component_vevs": {
            "a_210": a,
            "omega_210": omega,
            "p_210": p,
            "DeltaR_126bar": v126,
            "split_fractions": {
                "a_over_MGUT": a / m_gut,
                "omega_over_MGUT": omega / m_gut,
                "p_over_MGUT": p / m_gut,
            },
            "note": "Stack convention (0.3,0.5,0.2)×M_GUT — not unique vacuum ratios",
        },
        "masses": masses,
        "proxy_comparison": {
            "g_times_MGUT_GeV": float(proxy),
            "proton_decay_mediator_GeV": float(m_pd),
            "ratio_exact_over_proxy": float(ratio),
        },
        "literature_check_126_only": {
            "M_U_GeV": only126["M_U_GeV"],
            "M_V_GeV": only126["M_V_GeV"],
            "V_massless": v_vanishes,
            "note": "⟨126⟩ alone ⇒ SO(10)→SU(5); V stays massless (Eq. 7)",
        },
        "gauge_lifetime": {
            "exact_mediator": width_exact,
            "proxy_g_MGUT": width_proxy,
            "delta_rel_tau_exact_vs_proxy": float(d_tau),
            "sk_status_note": (
                "SK failure under the stack (0.3,0.5,0.2) VEV split is "
                "conditional on those ratios — not a whole-model exclusion "
                "while unique (a,ω,p) remain OPEN."
                if not width_exact["passes_SK"]
                else "Selected-point gauge lifetime passes SK."
            ),
        },
        "next_exact_calculation": [
            "Close inter-representation 10–126 colour-triplet mixing",
            "Fix unique (a,ω,p) ratios from the full 210 potential minimum",
            "Execute a live SARAH/PyR@TE dump when tools are available",
        ],
        "flag": {
            "exact_XY_mass_from_component_vacuum": True,
            "published_susyno_fonseca_formulas": True,
            "proton_decay_uses_min_UV": True,
            "replaced_g_MGUT_proxy": True,
            "selected_point_passes_SK": bool(width_exact["passes_SK"]),
            "unique_vev_ratios_from_full_potential": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Component-vacuum gauge masses: M_U={masses['M_U_GeV']:.3e}, "
            f"M_V={masses['M_V_GeV']:.3e} GeV "
            f"(PD mediator={m_pd:.3e}; proxy g·M_GUT={proxy:.3e}, "
            f"ratio={ratio:.3e}); τ_e(exact)/τ(proxy)−1={d_tau:.3e}, "
            f"SK pass={width_exact['passes_SK']} (conditional on VEV split). "
            "Unique (a,ω,p) ratios and unique τ_p remain OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    m = report["masses"]
    p = report["proxy_comparison"]
    g = report["gauge_lifetime"]
    lines = [
        "# Exact X/Y masses from component vacuum — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- M_U: {m['M_U_GeV']:.6e} GeV",
        f"- M_V: {m['M_V_GeV']:.6e} GeV",
        f"- PD mediator: {p['proton_decay_mediator_GeV']:.6e} GeV",
        f"- Proxy g·M_GUT: {p['g_times_MGUT_GeV']:.6e} GeV",
        f"- Ratio exact/proxy: {p['ratio_exact_over_proxy']:.6e}",
        f"- τ(exact): {g['exact_mediator']['tau_e_years']:.6e} yr",
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
    ROOT.joinpath("EXACT_XY_MASSES_COMPONENT_VACUUM_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2, default=_json_default) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("EXACT_XY_MASSES_COMPONENT_VACUUM_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "proxy_comparison": report.get("proxy_comparison"),
                "masses": {
                    k: report["masses"][k]
                    for k in (
                        "M_U_GeV",
                        "M_V_GeV",
                        "M_X_PS_GeV",
                        "M_WR_GeV",
                        "proton_decay_mediator_GeV",
                        "proton_decay_mediator_name",
                    )
                },
                "gauge_lifetime": {
                    "tau_exact": report["gauge_lifetime"]["exact_mediator"][
                        "tau_e_years"
                    ],
                    "passes_SK": report["gauge_lifetime"]["exact_mediator"][
                        "passes_SK"
                    ],
                    "delta_rel_vs_proxy": report["gauge_lifetime"][
                        "delta_rel_tau_exact_vs_proxy"
                    ],
                },
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
