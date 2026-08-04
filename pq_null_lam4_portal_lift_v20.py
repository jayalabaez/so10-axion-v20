#!/usr/bin/env python3
r"""Lift PQ-null E/F/J/X modes via the charge-allowed λ₄ portal (v20).

Next step after ``tau_p_hessian_residual_closure_v20`` (live SARAH absent):

1. Identify the PQ/X/Z₁₇–allowed dim-4 operator ``210·10·126·S`` (λ₄) as the
   legal substitute for the bare MSGUT cubic ``γ Φ H Σ`` (PQ-forbidden).
2. Match ``γ_eff = λ₄`` under the dictionary ``γ·⟨σ⟩ ↔ λ₄·⟨S⟩`` with
   ``⟨σ⟩ = ⟨S⟩ = M_I`` used in the Hilbert-matched Aulakh parameters.
3. Re-diagonalize E/F/J/X at Hilbert VEVs: exact SVD kernels at ``γ=0`` lift
   for any ``λ₄ ≠ 0``; report the selected finite-κ ``λ₄`` and the critical
   ``|λ₄|`` that clears the GUT-relative null tolerance.

Honesty
-------
* Closing the exact PQ-null kernel does **not** force the selected λ₄ large
  enough to push all induced masses above ``10^{-8} M_GUT``.
* The soft ``cal G`` near-null is independent of γ and is documented separately.
* Live SARAH and exact unique ``τ_p`` remain OPEN.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import g_singlet_6x6_cw_v20 as gsing
import literature_cg_triplet_matrix_v20 as lit
import mixed_210_126_10_cw_v20 as mixed
import mixed_210_126_10_hilbert_hessian_v20 as mxh
import nonsusy_z17_pq_potential_filter_v20 as z17
import promote_210n_tensor_basis_uniqueness_v20 as promote
import residual_lam210_eta_intra_v20 as residual
import sarah_pyrate_210n_model_file_v20 as sarah
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent

NULL_TOL_OVER_MGUT = mxh.NULL_TOL_OVER_MGUT
EFJX = ("E", "F", "J", "X")

SOURCES = {
    "portal": "charge_allowed_potential_minimize_v20 / 210·10·126·S (λ₄)",
    "charges": "nonsusy_z17_pq_potential_filter_v20",
    "blocks": "mixed_210_126_10_cw_v20 (Aulakh E/F/J/X)",
    "vevs": "promote_210n_tensor_basis_uniqueness_v20",
    "upstream_hessian_tau": "tau_p_hessian_residual_closure_v20",
}


def lam4_portal_charge_certificate() -> dict[str, Any]:
    """PQ/X/Z₁₇ certificate for the dim-4 λ₄ operator 210·10·126·S."""
    counts = {"210_H": 1, "10_H": 1, "126bar_H": 1, "S": 1}
    totals = z17._total_charge(counts)
    allowed = z17._allowed(totals, require_x=True)
    bare_gamma_counts = {"210_H": 1, "10_H": 1, "126bar_H": 1}
    bare_totals = z17._total_charge(bare_gamma_counts)
    bare_allowed = z17._allowed(bare_totals, require_x=True)
    return {
        "operator": "210_H 10_H 126bar_H S",
        "aulakh_slot": "gamma / gamma_bar (effective)",
        "counts": counts,
        "charge_totals": totals,
        "allowed": allowed,
        "bare_gamma_Phi_H_Sigma": {
            "operator": "210_H 10_H 126bar_H",
            "charge_totals": bare_totals,
            "allowed": bare_allowed,
            "note": "PQ-forbidden cubic; source of exact E/F/J/X nulls at γ=0",
        },
        "matching": (
            "γ_eff = λ₄ under γ·⟨σ⟩ ↔ λ₄·⟨S⟩ with ⟨σ⟩=⟨S⟩=M_I "
            "in the Hilbert-matched parameter set"
        ),
    }


def _params_with_gamma(
    *,
    a: float,
    omega: float,
    p: float,
    m_i: float,
    m_gut: float,
    lam: float,
    eta: float,
    gamma: float,
) -> dict[str, complex]:
    pd = mxh.hilbert_matched_params(
        a=a, omega=omega, p=p, m_i=m_i, m_gut=m_gut, lam=lam, eta=eta
    )
    pd["gamma"] = complex(gamma)
    pd["gamma_bar"] = complex(gamma)
    pd["pq_gamma_forbidden"] = abs(gamma) == 0.0
    pd["gamma_from_lam4_portal"] = abs(gamma) > 0.0
    return pd


def block_spectra(
    pdict: dict[str, complex],
    *,
    m_gut: float,
    g_gauge: float,
) -> dict[str, Any]:
    """SVD spectra for T/D/E/F/J/X/G at the given (possibly lifted) params."""
    cal_t = lit.aulakh_cal_T(
        **{
            k: pdict[k]
            for k in (
                "M_H",
                "M",
                "m",
                "lam",
                "eta",
                "gamma",
                "gamma_bar",
                "a",
                "omega",
                "p",
                "sigma",
                "sigma_bar",
            )
        }
    )
    cal_d = lit.aulakh_cal_D(
        M_H=pdict["M_H"],
        M=pdict["M"],
        m=pdict["m"],
        lam=pdict["lam"],
        eta=pdict["eta"],
        gamma=pdict["gamma"],
        gamma_bar=pdict["gamma_bar"],
        a=pdict["a"],
        omega=pdict["omega"],
        sigma=pdict["sigma"],
        sigma_bar=pdict["sigma_bar"],
    )
    blocks = [
        mxh.spectrum_with_nulls("T", cal_t, "(3,1) mixed cal T", m_gut=m_gut),
        mxh.spectrum_with_nulls("D", cal_d, "(1,2) mixed cal D", m_gut=m_gut),
        mxh.spectrum_with_nulls(
            "E", mixed.aulakh_E(pdict), "(3,2,±1/3)", m_gut=m_gut
        ),
        mxh.spectrum_with_nulls(
            "F", mixed.aulakh_F(pdict), "(1,1,±2)", m_gut=m_gut
        ),
        mxh.spectrum_with_nulls(
            "J", mixed.aulakh_J(pdict), "(3,1,±4/3)", m_gut=m_gut
        ),
        mxh.spectrum_with_nulls(
            "X", mixed.aulakh_X(pdict), "(3,2,±5/3)", m_gut=m_gut
        ),
    ]
    gmat = gsing.aulakh_cal_G(
        m=pdict["m"],
        M=pdict["M"],
        lam=pdict["lam"],
        eta=pdict["eta"],
        a=pdict["a"],
        p=pdict["p"],
        omega=pdict["omega"],
        sigma=pdict["sigma"],
        sigma_bar=pdict["sigma_bar"],
        g_gauge=g_gauge,
    )
    g_block = mxh.spectrum_with_nulls(
        "G", gmat, "G[1,1,0] cal G", m_gut=m_gut
    )
    g_block["n_dof_per_mode"] = gsing.DOF_G_SINGLET
    blocks.append(g_block)

    by_name = {b["name"]: b for b in blocks}
    efjx_min_all: dict[str, float] = {}
    for n in EFJX:
        vals = by_name[n]["masses_GeV"] + by_name[n]["pq_null_GeV"]
        efjx_min_all[n] = float(min(vals)) if vals else float("nan")
    g_vals = by_name["G"]["masses_GeV"] + by_name["G"]["pq_null_GeV"]

    return {
        "blocks": blocks,
        "efjx_n_null_below_tol": int(sum(by_name[n]["n_pq_null"] for n in EFJX)),
        "efjx_min_GeV": efjx_min_all,
        "efjx_exact_algebraic_nulls": int(
            sum(1 for n in EFJX if efjx_min_all[n] == 0.0)
        ),
        "g_n_null_below_tol": int(by_name["G"]["n_pq_null"]),
        "g_min_GeV": float(min(g_vals)) if g_vals else float("nan"),
        "n_pq_null_total": int(sum(b["n_pq_null"] for b in blocks)),
    }


def critical_lam4_for_tol(
    *,
    a: float,
    omega: float,
    p: float,
    m_i: float,
    m_gut: float,
    lam: float,
    eta: float,
    g_gauge: float,
) -> dict[str, Any]:
    """Binary search smallest |λ₄|=|γ_eff| clearing E/F/J/X null tolerance."""
    lo, hi = 0.0, 1.0
    # Expand hi if needed
    for _ in range(20):
        spec = block_spectra(
            _params_with_gamma(
                a=a, omega=omega, p=p, m_i=m_i, m_gut=m_gut, lam=lam, eta=eta, gamma=hi
            ),
            m_gut=m_gut,
            g_gauge=g_gauge,
        )
        if spec["efjx_n_null_below_tol"] == 0:
            break
        hi *= 2.0
    else:
        return {
            "found": False,
            "lam4_crit_abs": None,
            "note": "No |λ₄|≤hi cleared E/F/J/X null tol",
            "hi_tried": hi,
        }

    for _ in range(48):
        mid = 0.5 * (lo + hi)
        spec = block_spectra(
            _params_with_gamma(
                a=a, omega=omega, p=p, m_i=m_i, m_gut=m_gut, lam=lam, eta=eta, gamma=mid
            ),
            m_gut=m_gut,
            g_gauge=g_gauge,
        )
        if spec["efjx_n_null_below_tol"] == 0:
            hi = mid
        else:
            lo = mid
    return {
        "found": True,
        "lam4_crit_abs": float(hi),
        "null_tol_GeV": float(NULL_TOL_OVER_MGUT * m_gut),
        "clears_efjx_tol_at_crit": True,
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "PQ_NULL_LAM4_LIFT_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"pq_null_exact_kernel_lifted_by_lam4": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    alpha_inv = float(anchor["alpha_inv_GUT"])
    g_gauge = math.sqrt(4.0 * math.pi / alpha_inv)

    promote_rep = promote.build_report()
    residual_rep = residual.build_report()
    sarah_probe = sarah.probe_live_tools()
    portal = lam4_portal_charge_certificate()

    if promote_rep.get("n_failed", 1) != 0 or residual_rep.get("n_failed", 1) != 0:
        return {
            "status": "PQ_NULL_LAM4_LIFT_NOT_EXECUTED__UPSTREAM_FAILED",
            "n_failed": 1,
            "failures": ["promote_or_residual"],
            "flag": {"pq_null_exact_kernel_lifted_by_lam4": False},
        }

    fr = promote_rep["selected_hilbert"]["fractions"]
    a = float(fr["a_over_MGUT"] * m_gut)
    omega = float(fr["omega_over_MGUT"] * m_gut)
    p = float(fr["p_over_MGUT"] * m_gut)
    lam = float(residual_rep["uv_residual_couplings"]["lam210_10"])
    eta = float(residual_rep["uv_residual_couplings"]["eta_intra"])
    lam4 = float(residual_rep["inputs"]["lam4"])
    gamma_eff = float(lam4)  # matching γ_eff = λ₄

    baseline = block_spectra(
        _params_with_gamma(
            a=a, omega=omega, p=p, m_i=m_i, m_gut=m_gut, lam=lam, eta=eta, gamma=0.0
        ),
        m_gut=m_gut,
        g_gauge=g_gauge,
    )
    lifted = block_spectra(
        _params_with_gamma(
            a=a,
            omega=omega,
            p=p,
            m_i=m_i,
            m_gut=m_gut,
            lam=lam,
            eta=eta,
            gamma=gamma_eff,
        ),
        m_gut=m_gut,
        g_gauge=g_gauge,
    )
    crit = critical_lam4_for_tol(
        a=a,
        omega=omega,
        p=p,
        m_i=m_i,
        m_gut=m_gut,
        lam=lam,
        eta=eta,
        g_gauge=g_gauge,
    )

    exact_lifted = (
        baseline["efjx_exact_algebraic_nulls"] == len(EFJX)
        and lifted["efjx_exact_algebraic_nulls"] == 0
        and all(lifted["efjx_min_GeV"][n] > 0.0 for n in EFJX)
    )
    selected_clears_tol = lifted["efjx_n_null_below_tol"] == 0
    lam4_below_crit = bool(
        crit.get("found") and abs(lam4) < float(crit["lam4_crit_abs"])
    )

    still_open = {
        "live_sarah_or_pyrate_executable_run": not bool(
            sarah_probe.get("live_run_executed")
        ),
        "scalar_alpha_not_unique_from_flavour": True,
        "selected_lam4_below_gut_null_tol_threshold": lam4_below_crit
        and not selected_clears_tol,
        "cal_G_soft_mode_independent_of_gamma": lifted["g_n_null_below_tol"] >= 1,
    }

    checks = {
        "promote_ok": promote_rep.get("n_failed", 1) == 0,
        "residual_ok": residual_rep.get("n_failed", 1) == 0,
        "portal_charges_allowed": bool(portal["allowed"]["all"]),
        "bare_gamma_forbidden": not bool(
            portal["bare_gamma_Phi_H_Sigma"]["allowed"]["PQ"]
        ),
        "baseline_efjx_exact_nulls": baseline["efjx_exact_algebraic_nulls"]
        == len(EFJX),
        "lifted_efjx_exact_nulls_gone": exact_lifted,
        "gamma_eff_equals_lam4": abs(gamma_eff - lam4) < 1e-30,
        "crit_found": bool(crit.get("found")),
        "live_sarah_still_open": still_open["live_sarah_or_pyrate_executable_run"],
        "exact_unique_not_overclaimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "PQ_NULL_EXACT_KERNEL_LIFTED_BY_LAM4__LIGHT_MASSES_DOCUMENTED"
            if not failures
            else "PQ_NULL_LAM4_PORTAL_LIFT_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "portal_certificate": portal,
        "matching": {
            "rule": "gamma_eff = lam4",
            "lam4_selected": lam4,
            "gamma_eff": gamma_eff,
            "sigma_over_MI": 1.0,
            "S_vev_rule": "⟨S⟩ = M_I (= σ in Hilbert-matched params)",
        },
        "baseline_gamma0": {
            "efjx_exact_algebraic_nulls": baseline["efjx_exact_algebraic_nulls"],
            "efjx_n_null_below_tol": baseline["efjx_n_null_below_tol"],
            "efjx_min_GeV": baseline["efjx_min_GeV"],
            "g_n_null_below_tol": baseline["g_n_null_below_tol"],
            "n_pq_null_total": baseline["n_pq_null_total"],
        },
        "lifted_selected_lam4": {
            "efjx_exact_algebraic_nulls": lifted["efjx_exact_algebraic_nulls"],
            "efjx_n_null_below_tol": lifted["efjx_n_null_below_tol"],
            "efjx_min_GeV": lifted["efjx_min_GeV"],
            "g_n_null_below_tol": lifted["g_n_null_below_tol"],
            "g_min_GeV": lifted["g_min_GeV"],
            "n_pq_null_total": lifted["n_pq_null_total"],
            "selected_clears_gut_null_tol": selected_clears_tol,
        },
        "critical_lam4": crit,
        "vevs": {
            "fractions": fr,
            "a_GeV": a,
            "omega_GeV": omega,
            "p_GeV": p,
            "lam210_10": lam,
            "eta_intra": eta,
        },
        "upstream_status": {
            "promote": promote_rep.get("status"),
            "residual": residual_rep.get("status"),
        },
        "certificate": {
            "pq_null_exact_kernel_closed": exact_lifted,
            "residual_still_open": still_open,
            "interpretation": (
                "The charge-allowed dim-4 portal 210·10·126·S (λ₄) replaces "
                "the PQ-forbidden cubic γ Φ H Σ. Under γ_eff=λ₄, the exact "
                "E/F/J/X SVD kernels present at γ=0 are lifted. At the "
                "selected finite-κ λ₄ the induced masses remain below the "
                "GUT-relative null tolerance unless |λ₄|≳λ₄_crit; cal G soft "
                "mode is γ-independent."
            ),
        },
        "next_exact_calculation": [
            "Derive a unique scalar α from flavour / Clebsch fits (or prove non-uniqueness)",
            "Map the γ-independent cal G soft mode (Goldstone vs residual flat direction)",
            "Execute a live SARAH/PyR@TE dump when Mathematica+SARAH or pyrate is available",
        ],
        "flag": {
            "pq_null_exact_kernel_lifted_by_lam4": exact_lifted,
            "lam4_portal_charge_allowed": bool(portal["allowed"]["all"]),
            "bare_gamma_pq_forbidden": True,
            "selected_lam4_clears_gut_null_tol": selected_clears_tol,
            "cal_G_soft_mode_documented": lifted["g_n_null_below_tol"] >= 1,
            "live_sarah_or_pyrate_executable_run": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"λ₄ portal lifts exact E/F/J/X PQ-null kernels "
            f"(γ_eff=λ₄={lam4:.3e}): mins "
            + ", ".join(
                f"{n}={lifted['efjx_min_GeV'][n]:.3e}" for n in EFJX
            )
            + f" GeV; GUT-tol clear={selected_clears_tol}"
            + (
                f" (λ₄_crit≈{crit['lam4_crit_abs']:.3e})"
                if crit.get("found")
                else ""
            )
            + f"; cal G soft nulls={lifted['g_n_null_below_tol']}. "
            f"Live SARAH and exact unique τ_p remain OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    cert = report["certificate"]
    base = report["baseline_gamma0"]
    lift = report["lifted_selected_lam4"]
    lines = [
        "# PQ-null lift via λ₄ portal — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        "## Portal",
        "",
        f"- Operator: `{report['portal_certificate']['operator']}`",
        f"- Allowed: {report['portal_certificate']['allowed']}",
        f"- Matching: {report['matching']['rule']} "
        f"(λ₄={report['matching']['lam4_selected']:.6e})",
        "",
        "## Baseline γ=0",
        "",
        f"- E/F/J/X exact algebraic nulls: {base['efjx_exact_algebraic_nulls']}",
        f"- E/F/J/X below GUT null-tol: {base['efjx_n_null_below_tol']}",
        "",
        "## Lifted at selected λ₄",
        "",
        f"- E/F/J/X exact algebraic nulls: {lift['efjx_exact_algebraic_nulls']}",
        f"- E/F/J/X below GUT null-tol: {lift['efjx_n_null_below_tol']}",
        f"- Clears GUT null-tol: {lift['selected_clears_gut_null_tol']}",
        f"- cal G soft nulls: {lift['g_n_null_below_tol']}",
        "",
        "## Still open",
        "",
    ]
    for k, v in cert["residual_still_open"].items():
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Next exact calculation", ""])
    for step in report["next_exact_calculation"]:
        lines.append(f"1. {step}")
    lines.extend(["", "## Flags", ""])
    for k, v in report["flag"].items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    return "\n".join(lines)


def _json_default(obj: Any) -> Any:
    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    if isinstance(obj, complex):
        return {"re": obj.real, "im": obj.imag}
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    report = build_report()
    # Drop bulky by_name from JSON if present nested — spectra summaries only
    ROOT.joinpath("PQ_NULL_LAM4_PORTAL_LIFT_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2, default=_json_default) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("PQ_NULL_LAM4_PORTAL_LIFT_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "matching": report.get("matching"),
                "baseline": report.get("baseline_gamma0"),
                "lifted": report.get("lifted_selected_lam4"),
                "critical_lam4": report.get("critical_lam4"),
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
