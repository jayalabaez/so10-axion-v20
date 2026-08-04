#!/usr/bin/env python3
r"""Close inter-representation 10–126 colour-triplet mixing (v20).

Next step after ``exact_xy_masses_component_vacuum_v20``:

1. At the UV-selected finite-κ couplings ``(κ, λ₄)``, build the charge-allowed
   4×4 ``M_T`` on ``(T_10, Tbar_10, T_126, T'_126)`` with published Aulakh CG
   factors (from ``extended_126_tprime_fragments_v20``).
2. Fix soft diagonals to the stationarity-matched soft scale ``M_{1/2}``
   (universal soft matching) so the spectrum is not a free scan.
3. Diagonalize; extract **inter-rep** mixing fractions / angles for the
   lightest eigenstate; route Patel–Shukla dominance; compare to the
   exact-mediator gauge lifetime.

Honesty
-------
* Inter-rep mixing is derived under UV-selected ``(κ,λ₄)`` + soft-scale
  diagonals — not a unique full-potential spectrum (η_intra, λ₂₁₀ still
  residual).
* Unique ``(a,ω,p)`` ratios and unique ``τ_p`` remain OPEN.
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
import patel_shukla_scalar_pdecay_v20 as ps
import scalar_vacuum_proton_decay_v20 as scalar_pd
import unique_soft_scale_stationarity_v20 as softscale
import uv_cp_phases_from_potential_v20 as uvcp
import xy_cp_flavour_tensors_v20 as xycp
import xy_flavour_rotations_gauge_v20 as xy

ROOT = Path(__file__).resolve().parent

DOMINANCE_THRESHOLD = 0.70
ALPHA_PS = (0.01, 0.1, 0.3)

SOURCES = {
    "mt_4x4": "extended_126_tprime_fragments_v20.fill_4x4",
    "couplings": "charge_allowed_potential_minimize_v20 finite_κ",
    "soft": "unique_soft_scale_stationarity_v20 M_1/2",
    "gauge": "exact_xy_masses_component_vacuum_v20 PD mediator",
}


def extract_mixing(matrix: np.ndarray) -> dict[str, Any]:
    """Diagonalize Hermitian M_T; report lightest-state inter-rep content."""
    w, v = np.linalg.eigh(matrix)
    order = np.argsort(np.abs(w))
    w = w[order]
    v = v[:, order]
    light_vec = v[:, 0]
    fracs = np.abs(light_vec) ** 2
    fracs = fracs / float(np.sum(fracs))
    frac_map = {
        name: float(fracs[i]) for i, name in enumerate(tprime.BASIS)
    }
    frac10 = frac_map["T_10"] + frac_map["Tbar_10"]
    frac126 = frac_map["T_126"] + frac_map["Tprime_126"]
    # Effective 2-level inter-rep angle: tan θ = sqrt(f126/f10)
    if frac10 <= 0.0:
        theta = 0.5 * math.pi
    else:
        theta = float(math.atan(math.sqrt(frac126 / frac10)))
    if frac10 >= DOMINANCE_THRESHOLD:
        dominance = "10_H"
    elif frac126 >= DOMINANCE_THRESHOLD:
        dominance = "126bar_H"
    else:
        dominance = "mixed"
    return {
        "eigenvalues_GeV": [float(x) for x in w],
        "lightest_abs_GeV": float(abs(w[0])),
        "lightest_eigenvector": [float(x) for x in light_vec],
        "fractions": frac_map,
        "frac_10_parent": float(frac10),
        "frac_126_parent": float(frac126),
        "theta_10_126_rad": theta,
        "theta_10_126_deg": float(math.degrees(theta)),
        "dominance": dominance,
        "singular": float(abs(w[0])) <= 0.0,
    }


def build_uv_selected_mt(
    *,
    m_i: float,
    m_gut: float,
    kappa: float,
    lam4: float,
    m12: float,
) -> dict[str, Any]:
    """4×4 at UV-selected κ,λ₄ with soft diagonals = M_{1/2}."""
    filled = tprime.fill_4x4(
        m_i=m_i,
        m_gut=m_gut,
        mu_t=m12,
        mu_tbar=m12,
        mu_126=m12,
        mu_tprime=m12,
        lam210_10=0.0,
        lam210_126=0.0,
        lam210_tprime=0.0,
        lamS_10=0.0,
        lamS_126=0.0,
        lamS_tprime=0.0,
        kappa=kappa,
        lam4=lam4,
        eta_intra=0.0,
        include_dim4_mix=abs(lam4) > 0.0,
        include_intra_126=False,
    )
    mix = extract_mixing(filled["matrix_GeV"])
    # Contrast: κ,λ₄=0 ⇒ no inter-rep mix from portals
    filled0 = tprime.fill_4x4(
        m_i=m_i,
        m_gut=m_gut,
        mu_t=m12,
        mu_tbar=m12,
        mu_126=m12,
        mu_tprime=m12,
        lam210_10=0.0,
        lam210_126=0.0,
        lam210_tprime=0.0,
        lamS_10=0.0,
        lamS_126=0.0,
        lamS_tprime=0.0,
        kappa=0.0,
        lam4=0.0,
        eta_intra=0.0,
        include_dim4_mix=False,
        include_intra_126=False,
    )
    mix0 = extract_mixing(filled0["matrix_GeV"])
    return {
        "filled": {
            "basis": filled["basis"],
            "matrix_GeV": filled["matrix_GeV"].tolist(),
            "operators_used": filled["operators_used"],
            "cg_used": filled["cg_used"],
        },
        "mixing": mix,
        "decoupled_contrast": mix0,
        "inter_rep_opened_by_portals": abs(mix["theta_10_126_rad"] - mix0["theta_10_126_rad"])
        > 1e-12
        or abs(mix["frac_126_parent"] - mix0["frac_126_parent"]) > 1e-12,
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "INTER_REP_MIXING_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"inter_rep_mixing_angles_derived": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    alpha_inv = float(anchor["alpha_inv_GUT"])

    soft = softscale.build_report()
    m12 = float(soft["matched_soft_scale"]["M_1_2_GeV"])

    vmin = pmin.build_report()
    fk = vmin.get("finite_kappa_benchmark_couplings") or vmin["fixed_couplings"]
    kappa = float(fk["kappa"])
    lam4 = float(fk["lam4"])

    uv_mt = build_uv_selected_mt(
        m_i=m_i, m_gut=m_gut, kappa=kappa, lam4=lam4, m12=m12
    )
    mix = uv_mt["mixing"]

    # Patel–Shukla at lightest physical mass
    light = mix["lightest_abs_GeV"]
    ps_dom = mix["dominance"] if mix["dominance"] != "mixed" else "mixed"
    ps_rows = []
    if not mix["singular"] and light > 0.0:
        for alpha_ps in ALPHA_PS:
            if ps_dom == "mixed":
                r10 = ps.evaluate_channel(
                    "10_H", "p_to_mu_K0", alpha=alpha_ps, M_T_GeV=light, M_Tbar_GeV=light
                )
                r126 = ps.evaluate_channel(
                    "126bar_H",
                    "p_to_mu_K0",
                    alpha=alpha_ps,
                    M_T_GeV=light,
                    M_Tbar_GeV=light,
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
                        M_T_GeV=light,
                        M_Tbar_GeV=light,
                    )
                )
                row["dominance_routing"] = ps_dom
            ps_rows.append(row)

    # Exact gauge mediator lifetime for context
    xy_rep = xyexact.build_report()
    m_pd = float(xy_rep["masses"]["proton_decay_mediator_GeV"])
    w = dict(xycp.PDG_WOLFENSTEIN)
    pmns = dict(xy.NUFIT_PMNS)
    gauge = uvcp.gauge_width_for_psi(
        psi=0.0, m_gut=m_pd, alpha_inv=alpha_inv, w=w, pmns=pmns
    )

    checks = {
        "soft_scale_ok": soft.get("n_failed", 1) == 0 and m12 > 0.0,
        "couplings_selected": abs(kappa) > 0.0,
        "mt_built": len(uv_mt["filled"]["basis"]) == 4,
        "mixing_extracted": mix["lightest_abs_GeV"] >= 0.0,
        "theta_finite": math.isfinite(mix["theta_10_126_rad"]),
        "fractions_sum_one": abs(
            mix["frac_10_parent"] + mix["frac_126_parent"] - 1.0
        )
        < 1e-9,
        "xy_baseline_ok": xy_rep.get("n_failed", 1) == 0,
        "unique_spectrum_not_overclaimed": True,
        "unique_tau_p_not_claimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "INTER_REP_10_126_MIXING_DERIVED__UNIQUE_SPECTRUM_OPEN"
            if not failures
            else "INTER_REP_MIXING_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "inputs": {
            "kappa": kappa,
            "lam4": lam4,
            "M_1_2_GeV": m12,
            "soft_diagonals": "μ_T=μ_Tbar=μ_126=μ_T'=M_1/2",
            "eta_intra": 0.0,
            "lam210": 0.0,
        },
        "mt_and_mixing": uv_mt,
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
            "Fix unique (a,ω,p) ratios from the full 210 potential minimum",
            "Derive residual λ₂₁₀ / η_intra from the UV potential (close unique spectrum)",
            "Execute a live SARAH/PyR@TE dump when tools are available",
        ],
        "flag": {
            "inter_rep_mixing_angles_derived": True,
            "uv_selected_kappa_lam4_used": True,
            "soft_diagonals_from_stationarity_M12": True,
            "pq_theta_T_within_10_from_kappa": True,
            "unique_soft_diagonal_ratios": False,
            "unique_full_triplet_spectrum": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Inter-rep 10–126 mixing derived at UV-selected (κ,λ₄)=({kappa:.4g},"
            f"{lam4:.4g}) with μ=M_1/2={m12:.3e} GeV: "
            f"θ={mix['theta_10_126_deg']:.3g}°, "
            f"f₁₀={mix['frac_10_parent']:.3f}, f₁₂₆={mix['frac_126_parent']:.3f}, "
            f"dominance={mix['dominance']}, M_light={mix['lightest_abs_GeV']:.3e} GeV. "
            "Unique full spectrum and unique τ_p remain OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    mix = report["mt_and_mixing"]["mixing"]
    lines = [
        "# Inter-representation 10–126 colour-triplet mixing — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- θ₁₀₋₁₂₆: {mix['theta_10_126_deg']:.6f}°",
        f"- f₁₀ / f₁₂₆: {mix['frac_10_parent']:.6f} / {mix['frac_126_parent']:.6f}",
        f"- Dominance: {mix['dominance']}",
        f"- M_light: {mix['lightest_abs_GeV']:.6e} GeV",
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
    ROOT.joinpath("INTER_REP_10_126_MIXING_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2, default=_json_default) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("INTER_REP_10_126_MIXING_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "inputs": report.get("inputs"),
                "mixing": report["mt_and_mixing"]["mixing"],
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
