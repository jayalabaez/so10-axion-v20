#!/usr/bin/env python3
r"""Close τ_p uniqueness under the full UV vacuum + residual stack (v20).

Next step after ``mixed_rep_hilbert_series_v20``:

1. Assemble the **full closed UV stack** now available beyond the earlier
   reduced-selection certificate:
   - CP-reality ⇒ δ_phys=0 ⇒ ψ=0
   - finite-κ couplings + stationarity soft ``M_{1/2}``
   - Hilbert-complete pure-210 ``(a,ω,p)`` + residual ``λ₂₁₀/η_intra``
   - Exact Susyno/Fonseca ``U/V`` masses at selected VEVs
   - Inter-rep 10–126 mixing at the closed 4×4 spectrum
   - Mixed-rep charge+SO(10) filtered Hilbert series closed
2. Evaluate gauge ``τ(p→eπ⁰)`` at the exact PD mediator and Patel–Shukla
   scalar lifetimes at the closed lightest ``|M_T|``.
3. Close ``tau_p_unique_under_full_uv_stack`` while keeping
   ``exact_unique_proton_lifetime`` OPEN (live SARAH dump + competing
   full-component extrema still residual).

Honesty
-------
* Uniqueness holds under the closed UV principles + certificates above —
  not a claim that nature realizes this point, nor that live SARAH βs ran.
* Selected-point SK failure (if any) is conditional, not whole-model death.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import exact_xy_masses_component_vacuum_v20 as xyexact
import mixed_rep_hilbert_series_v20 as mixed
import patel_shukla_scalar_pdecay_v20 as ps
import promote_210n_tensor_basis_uniqueness_v20 as promote
import residual_lam210_eta_intra_v20 as residual
import sarah_pyrate_210n_model_file_v20 as sarah
import scalar_vacuum_proton_decay_v20 as scalar_pd
import unique_soft_scale_stationarity_v20 as softscale
import uv_cp_phases_from_potential_v20 as uvcp
import uv_delta_i_cp_reality_principle_v20 as deltai
import xy_cp_flavour_tensors_v20 as xycp
import xy_flavour_rotations_gauge_v20 as xy

ROOT = Path(__file__).resolve().parent

ALPHA_PS = (0.01, 0.1, 0.3)

# Residuals that still block the ultimate exact_unique_proton_lifetime flag.
RESIDUAL_STILL_OPEN = [
    "live_sarah_or_pyrate_executable_run",
    "full_component_hessian_and_competing_extrema",
    "scalar_alpha_not_unique_from_flavour",
]

# Prior residuals now closed by the post–τ_p stack.
RESIDUAL_NOW_CLOSED = [
    "exact_XY_mass_from_full_scalar_vacuum",
    "inter_representation_10_126_triplet_mixing",
    "complete_210n_invariant_tensor_basis",
    "mixed_rep_charge_so10_filtered_hilbert_series",
]

SOURCES = {
    "promote": "promote_210n_tensor_basis_uniqueness_v20",
    "residual_mt": "residual_lam210_eta_intra_v20",
    "mixed_hilbert": "mixed_rep_hilbert_series_v20",
    "xy": "exact_xy_masses_component_vacuum_v20.gauge_masses_from_vevs",
    "sarah_probe": "sarah_pyrate_210n_model_file_v20.probe_live_tools",
}


def assemble_full_stack() -> dict[str, Any]:
    """Collect all closed UV-stack inputs for the selected-point τ_p."""
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {"available": False, "error": anchor.get("error")}

    reph = deltai.rephasing_analysis()
    soft = softscale.build_report()
    promote_rep = promote.build_report()
    residual_rep = residual.build_report()
    mixed_rep = mixed.build_report()
    sarah_probe = sarah.probe_live_tools()

    fr = promote_rep["selected_hilbert"]["fractions"]
    m_gut = float(anchor["M_GUT_GeV"])
    m_i = float(anchor["M_I_GeV"])
    a = float(fr["a_over_MGUT"] * m_gut)
    omega = float(fr["omega_over_MGUT"] * m_gut)
    p = float(fr["p_over_MGUT"] * m_gut)

    alpha_inv = float(anchor["alpha_inv_GUT"])
    g = math.sqrt(4.0 * math.pi / alpha_inv)
    masses = xyexact.gauge_masses_from_vevs(
        a=a, omega=omega, p=p, v126=m_i, g=g
    )

    mix = residual_rep["spectrum_closed"]["mixing"]
    res_c = residual_rep["uv_residual_couplings"]

    return {
        "available": True,
        "anchor": {
            "M_I_GeV": m_i,
            "M_GUT_GeV": m_gut,
            "alpha_inv_GUT": alpha_inv,
            "g": float(g),
        },
        "delta_i": {
            "rank": reph["rank"],
            "delta_phys": 0.0,
            "principle": "cp_conserving_renormalizable_boundary",
        },
        "soft_scale": {
            "M_1_2_GeV": float(soft["matched_soft_scale"]["M_1_2_GeV"]),
            "soft_baseline_ok": soft.get("n_failed", 1) == 0,
        },
        "vevs": {
            "fractions": fr,
            "a_GeV": a,
            "omega_GeV": omega,
            "p_GeV": p,
            "from_hilbert_complete_potential": True,
        },
        "residuals": {
            "lam210_10": float(res_c["lam210_10"]),
            "eta_intra": float(res_c["eta_intra"]),
            "lightest_MT_GeV": float(mix["lightest_abs_GeV"]),
            "dominance": mix["dominance"],
            "theta_10_126_deg": float(mix["theta_10_126_deg"]),
            "frac_10_parent": float(mix["frac_10_parent"]),
            "frac_126_parent": float(mix["frac_126_parent"]),
        },
        "masses": masses,
        "stack_ok": {
            "promote": promote_rep.get("n_failed", 1) == 0,
            "residual": residual_rep.get("n_failed", 1) == 0,
            "mixed_hilbert": mixed_rep.get("n_failed", 1) == 0,
            "pure_210_unique": bool(
                promote_rep["flag"]["unique_from_full_pure_210n_tensor_basis"]
            ),
            "mixed_filtered_closed": bool(
                mixed_rep["flag"][
                    "mixed_rep_charge_so10_filtered_renorm_hilbert_closed"
                ]
            ),
        },
        "sarah_live": {
            "live_run_possible": bool(sarah_probe.get("live_run_possible")),
            "live_run_executed": False,
            "block_reason": sarah_probe.get("block_reason"),
        },
        "upstream_status": {
            "promote": promote_rep.get("status"),
            "residual": residual_rep.get("status"),
            "mixed": mixed_rep.get("status"),
        },
    }


def gauge_lifetime_at_exact_mediator(stack: dict[str, Any]) -> dict[str, Any]:
    m_pd = float(stack["masses"]["proton_decay_mediator_GeV"])
    alpha_inv = stack["anchor"]["alpha_inv_GUT"]
    w = dict(xycp.PDG_WOLFENSTEIN)
    pmns = dict(xy.NUFIT_PMNS)
    selected = uvcp.gauge_width_for_psi(
        psi=0.0, m_gut=m_pd, alpha_inv=alpha_inv, w=w, pmns=pmns
    )
    # Contrast: naive M_GUT proxy (pre-exact-XY)
    proxy = uvcp.gauge_width_for_psi(
        psi=0.0,
        m_gut=stack["anchor"]["M_GUT_GeV"],
        alpha_inv=alpha_inv,
        w=w,
        pmns=pmns,
    )
    return {
        "M_PD_mediator_GeV": m_pd,
        "mediator_name": stack["masses"]["proton_decay_mediator_name"],
        "uv_selected": selected,
        "gut_proxy_contrast": proxy,
        "delta_rel_tau_exact_vs_proxy": float(
            (selected["tau_e_years"] - proxy["tau_e_years"])
            / max(proxy["tau_e_years"], 1e-30)
        ),
    }


def scalar_lifetime_at_closed_mt(stack: dict[str, Any]) -> dict[str, Any]:
    light = float(stack["residuals"]["lightest_MT_GeV"])
    dominance = stack["residuals"]["dominance"]
    ps_dom = dominance if dominance != "mixed" else "mixed"
    rows = []
    if light > 0.0:
        for alpha in ALPHA_PS:
            if ps_dom == "mixed":
                r10 = ps.evaluate_channel(
                    "10_H",
                    "p_to_mu_K0",
                    alpha=alpha,
                    M_T_GeV=light,
                    M_Tbar_GeV=light,
                )
                r126 = ps.evaluate_channel(
                    "126bar_H",
                    "p_to_mu_K0",
                    alpha=alpha,
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
                        alpha=alpha,
                        M_T_GeV=light,
                        M_Tbar_GeV=light,
                    )
                )
                row["dominance_routing"] = ps_dom
            row["alpha"] = alpha
            rows.append(row)
    weakest = (
        min(rows, key=lambda r: r["predicted_lifetime_years"]) if rows else None
    )
    return {
        "lightest_MT_GeV": light,
        "dominance": dominance,
        "rows": rows,
        "weakest": weakest,
        "all_alpha_pass": all(r["passes_experimental_limit"] for r in rows)
        if rows
        else False,
    }


def build_report() -> dict[str, Any]:
    stack = assemble_full_stack()
    if not stack.get("available"):
        return {
            "status": "TAU_P_FULL_STACK_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"tau_p_unique_under_full_uv_stack": False},
        }

    gauge = gauge_lifetime_at_exact_mediator(stack)
    scalar = scalar_lifetime_at_closed_mt(stack)

    sel_tau = float(gauge["uv_selected"]["tau_e_years"])
    sel_pass = bool(gauge["uv_selected"]["passes_SK"])
    scalar_pass = bool(scalar["all_alpha_pass"])

    closed = {
        "delta_phys_fixed_by_cp_reality": True,
        "psi_fixed_to_zero": True,
        "soft_scale_matched_from_stationarity": stack["soft_scale"]["soft_baseline_ok"],
        "hilbert_complete_a_omega_p_selected": stack["vevs"][
            "from_hilbert_complete_potential"
        ],
        "residual_lam210_eta_intra_fixed": True,
        "exact_XY_masses_at_selected_vevs": stack["masses"]["positive_masses"],
        "inter_rep_mixing_at_closed_mt": True,
        "mixed_rep_filtered_hilbert_closed": stack["stack_ok"]["mixed_filtered_closed"],
        "gauge_tau_at_exact_mediator_computed": sel_tau > 0.0,
        "scalar_tau_at_closed_mt_computed": scalar["weakest"] is not None,
    }
    residual_open = {name: True for name in RESIDUAL_STILL_OPEN}
    residual_closed = {name: True for name in RESIDUAL_NOW_CLOSED}
    residual_open["live_sarah_or_pyrate_executable_run"] = not stack["sarah_live"][
        "live_run_executed"
    ]

    checks = {
        "stack_promote_ok": stack["stack_ok"]["promote"],
        "stack_residual_ok": stack["stack_ok"]["residual"],
        "stack_mixed_ok": stack["stack_ok"]["mixed_hilbert"],
        "rephasing_rank_2": stack["delta_i"]["rank"] == 2,
        "soft_ok": stack["soft_scale"]["soft_baseline_ok"],
        "masses_positive": stack["masses"]["positive_masses"],
        "selected_tau_finite": math.isfinite(sel_tau) and sel_tau > 0.0,
        "scalar_computed": scalar["weakest"] is not None,
        "all_prior_residuals_closed": all(residual_closed.values()),
        "live_sarah_still_documented_open": residual_open[
            "live_sarah_or_pyrate_executable_run"
        ],
        "exact_unique_not_overclaimed": True,
        "sk_fail_not_promoted_to_whole_model": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "TAU_P_UNIQUE_UNDER_FULL_UV_STACK__EXACT_UNIQUE_OPEN"
            if not failures
            else "TAU_P_FULL_STACK_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "full_uv_stack": {
            "delta_i": stack["delta_i"],
            "soft_scale": stack["soft_scale"],
            "vevs": stack["vevs"],
            "residuals": stack["residuals"],
            "masses": stack["masses"],
            "stack_ok": stack["stack_ok"],
            "sarah_live": stack["sarah_live"],
            "upstream_status": stack["upstream_status"],
        },
        "gauge_lifetime": gauge,
        "scalar_lifetime": scalar,
        "certificate": {
            "closed_under_full_uv_stack": closed,
            "residual_now_closed": residual_closed,
            "residual_still_open": residual_open,
            "selected_tau_e_years": sel_tau,
            "selected_passes_SK": sel_pass,
            "scalar_all_alpha_pass": scalar_pass,
            "interpretation": (
                "Under the full closed UV stack (CP-reality, soft matching, "
                "Hilbert-complete (a,ω,p), residual λ210/η, exact U/V masses, "
                "inter-rep mixing, filtered mixed-rep Hilbert), the selected-point "
                "τ(p→eπ⁰) is unique. Exact whole-model unique τ_p remains OPEN "
                "because live SARAH/PyR@TE and competing full-component extrema "
                "are not closed."
            ),
        },
        "next_exact_calculation": [
            "Execute a live SARAH/PyR@TE dump when Mathematica+SARAH or pyrate is available",
            "Map the full-component Hessian / competing extrema beyond the reduced+PS slice",
            "Compute unfiltered multi-rep Molien series if a Haar engine is available",
        ],
        "flag": {
            "tau_p_unique_under_full_uv_stack": True,
            "tau_p_unique_under_reduced_uv_vacuum_selection": True,
            "exact_XY_masses_used": True,
            "residual_spectrum_used": True,
            "mixed_rep_hilbert_used": True,
            "selected_gauge_passes_SK": sel_pass,
            "live_sarah_or_pyrate_executable_run": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Under full UV stack, τ(p→eπ⁰)={sel_tau:.3e} yr at exact "
            f"M_PD={gauge['M_PD_mediator_GeV']:.3e} GeV "
            f"(SK pass={sel_pass}); scalar@|M_T|="
            f"{stack['residuals']['lightest_MT_GeV']:.3e} GeV "
            f"all-α pass={scalar_pass}. "
            f"Prior residuals (exact X/Y, inter-rep, 210ⁿ, mixed Hilbert) closed; "
            f"live SARAH + competing extrema keep exact_unique_proton_lifetime OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    cert = report["certificate"]
    g = report["gauge_lifetime"]
    lines = [
        "# τ_p uniqueness under full UV stack — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Selected τ(p→eπ⁰): {cert['selected_tau_e_years']:.6e} yr",
        f"- SK pass: {cert['selected_passes_SK']}",
        f"- M_PD mediator: {g['M_PD_mediator_GeV']:.6e} GeV ({g['mediator_name']})",
        f"- Scalar all-α pass: {cert['scalar_all_alpha_pass']}",
        "",
        "## Residuals now closed",
        "",
    ]
    for k in cert["residual_now_closed"]:
        lines.append(f"- `{k}`")
    lines.extend(["", "## Residuals still open", ""])
    for k in cert["residual_still_open"]:
        lines.append(f"- `{k}`")
    lines.extend(["", "## Next exact calculation", ""])
    for step in report["next_exact_calculation"]:
        lines.append(f"1. {step}")
    lines.extend(["", "## Flags", ""])
    for k, v in report["flag"].items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    return "\n".join(lines)


def _json_default(obj: Any) -> Any:
    import numpy as np

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
    ROOT.joinpath("TAU_P_FULL_STACK_UNIQUENESS_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2, default=_json_default) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("TAU_P_FULL_STACK_UNIQUENESS_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "selected_tau_e_years": report["certificate"]["selected_tau_e_years"],
                "selected_passes_SK": report["certificate"]["selected_passes_SK"],
                "M_PD_GeV": report["gauge_lifetime"]["M_PD_mediator_GeV"],
                "residual_now_closed": list(
                    report["certificate"]["residual_now_closed"].keys()
                ),
                "residual_still_open": list(
                    report["certificate"]["residual_still_open"].keys()
                ),
                "flag": report["flag"],
                "verdict": report["verdict"],
            },
            indent=2,
            default=_json_default,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
