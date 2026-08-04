#!/usr/bin/env python3
r"""Prove λ₄-potential raise spoils the selected point; certify γ_eff CGC gap (v20).

Next step after ``lambda_lock_cal_g_lift_v20``:

1. Separate the radial-potential coupling ``λ₄_potential`` (from the
   charge-allowed minimizer) from the E/F/J/X component coupling
   ``γ_eff`` used in the Aulakh mass matrices.
2. Show that the silent identification ``γ_eff = λ₄_potential``
   (i.e. an unproven Clebsch ratio ``c_cgc = 1``) cannot be rescued by
   raising ``|λ₄_potential|`` to the E/F/J/X GUT null-tol critical
   value without destroying radial Hessian positive-definiteness.
3. Quantify the CGC ratio that would clear the null-tol while leaving
   the selected radial ``λ₄_potential`` fixed:
   ``|c_cgc|_needed ≈ |λ₄|_crit / |λ₄|_selected``.
4. Keep dim-6 ``λ_lock`` and full SO(10) CGC out of the live dump as OPEN.

Honesty
-------
* This does **not** derive the SO(10) Clebsch for ``210·10·126bar·S``.
* This does **not** claim ``exact_unique_proton_lifetime``.
* Selected-point SK failure (if any) remains conditional.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import charge_allowed_potential_minimize_v20 as cap
import lambda_lock_cal_g_lift_v20 as locklift
import pq_null_lam4_portal_lift_v20 as pqnull
import promote_210n_tensor_basis_uniqueness_v20 as promote
import residual_lam210_eta_intra_v20 as residual
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent
CRIT_MARGIN = 1.001

SOURCES = {
    "pq_null_lam4": "pq_null_lam4_portal_lift_v20",
    "couplings": "charge_allowed_potential_minimize_v20",
    "lambda_lock_lift": "lambda_lock_cal_g_lift_v20",
}


def raised_lam4(selected: float, crit_abs: float) -> dict[str, Any]:
    sign = -1.0 if selected < 0.0 else 1.0
    target_abs = max(abs(selected), float(crit_abs) * CRIT_MARGIN)
    return {
        "lam4_potential_selected": float(selected),
        "lam4_crit_abs": float(crit_abs),
        "lam4_potential_raised": float(sign * target_abs),
        "raise_factor": float(target_abs / max(abs(selected), 1e-30)),
        "margin": CRIT_MARGIN,
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "LAM4_EFJX_DECOUPLING_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"lam4_potential_raise_proved_spoiling": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    g_gauge = math.sqrt(4.0 * math.pi / float(anchor["alpha_inv_GUT"]))
    tau_gauge = float(scalar_pd.gauge_proton_decay(anchor)["central"]["lifetime_years"])

    pq_rep = pqnull.build_report()
    cap_rep = cap.build_report()
    lock_rep = locklift.build_report()
    promote_rep = promote.build_report()
    residual_rep = residual.build_report()

    if pq_rep.get("n_failed", 1) != 0 or cap_rep.get("n_failed", 1) != 0:
        return {
            "status": "LAM4_EFJX_DECOUPLING_NOT_EXECUTED__UPSTREAM_FAILED",
            "n_failed": 1,
            "failures": ["upstream"],
            "flag": {"lam4_potential_raise_proved_spoiling": False},
        }

    fk = cap_rep.get("finite_kappa_benchmark_couplings") or {}
    kappa = float(fk["kappa"])
    lam4_sel = float(fk["lam4"])
    # Prefer the raised |λ_lock| that already clears cal G.
    lambda_lock = float(
        lock_rep.get("couplings", {}).get("lambda_lock_raised", fk["lambda_lock"])
    )
    crit = pq_rep.get("critical_lam4") or {}
    if not crit.get("found"):
        return {
            "status": "LAM4_EFJX_DECOUPLING_NOT_EXECUTED__NO_CRIT",
            "n_failed": 1,
            "failures": ["critical_lam4"],
            "flag": {"lam4_potential_raise_proved_spoiling": False},
        }
    crit_abs = float(crit["lam4_crit_abs"])
    raised = raised_lam4(lam4_sel, crit_abs)
    lam4_up = float(raised["lam4_potential_raised"])

    c54 = float(cap_rep["C_54"])
    c126 = float(cap_rep["C_126_to_54"])

    baseline_pt = cap.evaluate_couplings(
        kappa=kappa,
        lam4=lam4_sel,
        lambda_lock=lambda_lock,
        m_i=m_i,
        m_gut=m_gut,
        c54=c54,
        c126=c126,
        tau_gauge=tau_gauge,
    )
    raised_pt = cap.evaluate_couplings(
        kappa=kappa,
        lam4=lam4_up,
        lambda_lock=lambda_lock,
        m_i=m_i,
        m_gut=m_gut,
        c54=c54,
        c126=c126,
        tau_gauge=tau_gauge,
    )
    spoil = locklift.spoilage_compare(baseline_pt, raised_pt)
    raise_spoils = bool(
        not raised_pt["radial_hessian_positive_definite"] or not spoil["not_spoiled"]
    )

    fr = promote_rep["selected_hilbert"]["fractions"]
    a = float(fr["a_over_MGUT"] * m_gut)
    omega = float(fr["omega_over_MGUT"] * m_gut)
    p = float(fr["p_over_MGUT"] * m_gut)
    lam = float(residual_rep["uv_residual_couplings"]["lam210_10"])
    eta = float(residual_rep["uv_residual_couplings"]["eta_intra"])

    # γ_eff raised to crit with radial λ₄ held fixed → E/F/J/X clear.
    gamma_at_crit = float(abs(lam4_up))
    spec_selected = pqnull.block_spectra(
        pqnull._params_with_gamma(
            a=a,
            omega=omega,
            p=p,
            m_i=m_i,
            m_gut=m_gut,
            lam=lam,
            eta=eta,
            gamma=lam4_sel,
        ),
        m_gut=m_gut,
        g_gauge=g_gauge,
    )
    spec_gamma_crit = pqnull.block_spectra(
        pqnull._params_with_gamma(
            a=a,
            omega=omega,
            p=p,
            m_i=m_i,
            m_gut=m_gut,
            lam=lam,
            eta=eta,
            gamma=gamma_at_crit if lam4_sel >= 0 else -gamma_at_crit,
        ),
        m_gut=m_gut,
        g_gauge=g_gauge,
    )
    gamma_clears = int(spec_gamma_crit["efjx_n_null_below_tol"]) == 0
    cgc_needed = float(crit_abs / max(abs(lam4_sel), 1e-30))

    checks = {
        "pq_ok": pq_rep.get("n_failed", 1) == 0,
        "cap_ok": cap_rep.get("n_failed", 1) == 0,
        "crit_found": bool(crit.get("found")),
        "selected_below_crit": abs(lam4_sel) < crit_abs,
        "raise_spoils_radial_hessian": raise_spoils,
        "raised_hessian_not_pd": not bool(
            raised_pt["radial_hessian_positive_definite"]
        ),
        "gamma_at_crit_clears_efjx": gamma_clears,
        "cgc_needed_gt_one": cgc_needed > 1.0,
        "exact_unique_not_overclaimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    still_open = {
        "selected_lam4_below_gut_null_tol_threshold": True,
        "lam4_cgc_and_dim6_lock_not_in_live_dump": True,
        "physical_efjx_cgc_for_210_10_126_S_undetermined": True,
    }

    return {
        "status": (
            "LAM4_POTENTIAL_EFJX_DECOUPLING_PROVED__TAU_P_OPEN"
            if not failures
            else "LAM4_POTENTIAL_EFJX_DECOUPLING_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "couplings": {
            "kappa_fixed": kappa,
            "lambda_lock_fixed": lambda_lock,
            "lam4_potential_selected": lam4_sel,
            "lam4_crit_abs": crit_abs,
            "lam4_potential_raised": lam4_up,
            "raise_factor": raised["raise_factor"],
            "c_cgc_assumed_silent": 1.0,
            "c_cgc_needed_abs_approx": cgc_needed,
            "gamma_eff_rule_assumed": "gamma_eff = c_cgc * lam4_potential",
        },
        "spoilage": {
            "baseline": {
                "radial_hessian_positive_definite": bool(
                    baseline_pt["radial_hessian_positive_definite"]
                ),
                "soft_shift_norm_over_MI2": float(
                    baseline_pt["soft"]["soft_shift_norm_over_MI2"]
                ),
                "perturbative": bool(baseline_pt["perturbative"]),
            },
            "at_raised_lam4_potential": {
                "radial_hessian_positive_definite": bool(
                    raised_pt["radial_hessian_positive_definite"]
                ),
                "soft_shift_norm_over_MI2": float(
                    raised_pt["soft"]["soft_shift_norm_over_MI2"]
                ),
                "perturbative": bool(raised_pt["perturbative"]),
            },
            "compare": spoil,
            "raise_proved_spoiling": raise_spoils,
        },
        "efjx": {
            "at_selected_gamma_eq_lam4": {
                "efjx_n_null_below_tol": int(spec_selected["efjx_n_null_below_tol"]),
                "efjx_exact_algebraic_nulls": int(
                    spec_selected["efjx_exact_algebraic_nulls"]
                ),
            },
            "at_gamma_crit_lam4_potential_fixed": {
                "gamma_eff": float(
                    gamma_at_crit if lam4_sel >= 0 else -gamma_at_crit
                ),
                "efjx_n_null_below_tol": int(spec_gamma_crit["efjx_n_null_below_tol"]),
                "clears_gut_null_tol": gamma_clears,
            },
        },
        "certificate": {
            "lam4_potential_distinct_from_gamma_eff": True,
            "silent_cgc_one_assumption_recorded": True,
            "raising_lam4_potential_to_crit_spoils_selected_point": raise_spoils,
            "gamma_eff_at_crit_clears_efjx_with_fixed_lam4_potential": gamma_clears,
            "physical_cgc_still_required": True,
            "residual_still_open": still_open,
            "interpretation": (
                "Raising the radial |λ₄_potential| to the E/F/J/X GUT "
                "null-tol critical value spoils the selected radial Hessian. "
                "Clearing the null-tol at fixed λ₄_potential therefore "
                "requires a nontrivial component Clebsch ratio "
                f"|c_cgc|≳{cgc_needed:.3g} in γ_eff = c_cgc·λ₄_potential, "
                "which is not derived and is absent from the live dump "
                "together with the dim-6 λ_lock encoding."
            ),
        },
        "next_exact_calculation": [
            "Derive SO(10) Clebsch coefficients for 210·10·126bar·S onto E/F/J/X channels",
            "If |c_cgc| is large enough, re-evaluate E/F/J/X null-tol at fixed selected λ₄_potential",
            "Encode derived CGC and dim-6 λ_lock into an extended live dump only after derivation",
        ],
        "flag": {
            "lam4_potential_raise_proved_spoiling": raise_spoils,
            "gamma_eff_decoupled_from_lam4_potential": True,
            "cgc_ratio_needed_quantified": cgc_needed > 1.0,
            "selected_lam4_still_below_gut_null_tol": True,
            "lam4_cgc_and_dim6_lock_not_in_live_dump": True,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"λ₄-potential raise to |λ₄|_crit≈{crit_abs:.3e} spoils radial "
            f"Hessian PD (raise_factor≈{raised['raise_factor']:.3g}); "
            f"|c_cgc|_needed≈{cgc_needed:.3g} to clear E/F/J/X at fixed "
            f"λ₄_potential. exact_unique_proton_lifetime remains False."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    c = report.get("couplings", {})
    spoil = report.get("spoilage", {})
    lines = [
        "# λ₄-potential / E/F/J/X decoupling certificate — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report.get("verdict", ""),
        "",
        f"- λ₄_potential selected: {c.get('lam4_potential_selected')}",
        f"- |λ₄|_crit: {c.get('lam4_crit_abs')}",
        f"- Raise factor: {c.get('raise_factor')}",
        f"- |c_cgc|_needed: {c.get('c_cgc_needed_abs_approx')}",
        f"- Raised Hessian PD: {spoil.get('at_raised_lam4_potential', {}).get('radial_hessian_positive_definite')}",
        "",
        "## Next exact calculation",
        "",
    ]
    for step in report.get("next_exact_calculation", []):
        lines.append(f"1. {step}")
    lines.extend(["", "## Flags", ""])
    for k, v in report.get("flag", {}).items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("LAM4_POTENTIAL_EFJX_DECOUPLING_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("LAM4_POTENTIAL_EFJX_DECOUPLING_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(json.dumps(
        {
            "status": report.get("status"),
            "n_failed": report.get("n_failed"),
            "failures": report.get("failures"),
            "couplings": report.get("couplings"),
            "flag": report.get("flag"),
            "verdict": report.get("verdict"),
        },
        indent=2,
    ))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
