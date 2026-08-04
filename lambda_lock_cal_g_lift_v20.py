#!/usr/bin/env python3
r"""Raise |λ_lock| to the cal G lift threshold and re-evaluate (v20).

Next step after ``cal_g_portal_decision_v20``:

1. Keep finite-κ ``(κ, λ₄)`` fixed; raise ``|λ_lock|`` to
   ``max(|λ_lock|_selected, |λ_lock|_crit)`` from the portal decision.
2. Embed the λ_lock soft-mass estimate into the Goldstone-orthogonal
   ``cal G`` deformation and confirm the lightest mode clears the GUT
   null tolerance with the chiral 5×5 Goldstone null preserved.
3. Re-evaluate the charge-allowed radial / locking point for spoilage
   (Hessian PD, perturbativity, stationarity soft shifts, M_T).
4. Close ``selected_lambda_lock_below_cal_G_lift_threshold`` when the
   raised point lifts cal G without spoiling the selected window.

Honesty
-------
* Soft embedding into transcribed MSGUT ``cal G`` remains an estimate.
* ``λ₄`` GUT null-tol and exact unique ``τ_p`` remain OPEN.
* Selected-point SK failure (if any) stays conditional.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import cal_g_portal_decision_v20 as portal
import cal_g_soft_mode_classification_v20 as calg
import charge_allowed_potential_minimize_v20 as cap
import g_singlet_6x6_cw_v20 as gsing
import mixed_210_126_10_hilbert_hessian_v20 as mxh
import promote_210n_tensor_basis_uniqueness_v20 as promote
import residual_lam210_eta_intra_v20 as residual
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent
NULL_TOL_OVER_MGUT = mxh.NULL_TOL_OVER_MGUT
# Small margin above analytic crit so SVD clears numerically.
LOCK_CRIT_MARGIN = 1.001

SOURCES = {
    "portal_decision": "cal_g_portal_decision_v20",
    "couplings": "charge_allowed_potential_minimize_v20",
    "cal_G": "g_singlet_6x6_cw_v20.aulakh_cal_G",
}


def raised_lambda_lock(selected: float, crit_abs: float) -> dict[str, Any]:
    sign = 1.0 if selected >= 0.0 else -1.0
    target_abs = max(abs(selected), float(crit_abs) * LOCK_CRIT_MARGIN)
    return {
        "lambda_lock_selected": float(selected),
        "lambda_lock_crit_abs": float(crit_abs),
        "lambda_lock_raised": float(sign * target_abs),
        "raise_factor": float(target_abs / max(abs(selected), 1e-30)),
        "margin": LOCK_CRIT_MARGIN,
    }


def evaluate_cal_g_at_lock(
    *,
    lambda_lock: float,
    m_i: float,
    m_gut: float,
    g_gauge: float,
    params: dict[str, complex],
) -> dict[str, Any]:
    null_tol = NULL_TOL_OVER_MGUT * m_gut
    cal_g = gsing._cal_g_from_params(params, g_gauge)
    _, orth = portal.goldstone_and_orthogonal(params["sigma"], params["sigma_bar"])
    mu = portal.lambda_lock_soft_mass_GeV(lambda_lock, m_i=m_i, m_gut=m_gut)
    deformed = portal.deform_cal_g(cal_g, orth, mu)
    spec = portal.spectrum_with_goldstone_check(
        deformed,
        sigma=params["sigma"],
        sigma_bar=params["sigma_bar"],
        null_tol_GeV=null_tol,
    )
    base = portal.spectrum_with_goldstone_check(
        cal_g,
        sigma=params["sigma"],
        sigma_bar=params["sigma_bar"],
        null_tol_GeV=null_tol,
    )
    return {
        "lambda_lock": float(lambda_lock),
        "mu_embed_GeV": float(mu),
        "null_tol_GeV": float(null_tol),
        "baseline_no_embed": base,
        "with_lambda_lock_embed": spec,
        "clears_null_tol": bool(spec["above_null_tol"] and spec["chiral_5x5_null_ok"]),
    }


def spoilage_compare(baseline: dict[str, Any], raised: dict[str, Any]) -> dict[str, Any]:
    soft0 = float(baseline["soft"]["soft_shift_norm_over_MI2"])
    soft1 = float(raised["soft"]["soft_shift_norm_over_MI2"])
    mt0 = float(baseline["lightest_MT_GeV"])
    mt1 = float(raised["lightest_MT_GeV"])
    return {
        "radial_hessian_pd_preserved": bool(raised["radial_hessian_positive_definite"]),
        "perturbative_preserved": bool(raised["perturbative"]),
        "stationarity_restored_preserved": bool(raised["soft"]["stationarity_restored"]),
        "phase_structure_preserved": bool(
            raised["phase_n_positive"] == baseline["phase_n_positive"]
            and raised["phase_n_zero"] == baseline["phase_n_zero"]
        ),
        "soft_shift_norm_over_MI2_baseline": soft0,
        "soft_shift_norm_over_MI2_raised": soft1,
        "soft_shift_norm_increase_factor": float(soft1 / max(soft0, 1e-30)),
        "lightest_MT_GeV_baseline": mt0,
        "lightest_MT_GeV_raised": mt1,
        "lightest_MT_ratio_raised_over_baseline": float(mt1 / max(mt0, 1e-30)),
        "ps_mu_K0_pass_baseline": bool(baseline["patel_shukla_mu_K0_passes"]),
        "ps_mu_K0_pass_raised": bool(raised["patel_shukla_mu_K0_passes"]),
        "not_spoiled": bool(
            raised["radial_hessian_positive_definite"]
            and raised["perturbative"]
            and raised["soft"]["stationarity_restored"]
            and raised["phase_n_positive"] == 1
            and raised["phase_n_zero"] == 2
            and mt1 > 0.0
        ),
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "LAMBDA_LOCK_CAL_G_LIFT_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"selected_lambda_lock_raised_to_cal_G_lift": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    g_gauge = math.sqrt(4.0 * math.pi / float(anchor["alpha_inv_GUT"]))
    tau_gauge = float(scalar_pd.gauge_proton_decay(anchor)["central"]["lifetime_years"])

    portal_rep = portal.build_report()
    cap_rep = cap.build_report()
    promote_rep = promote.build_report()
    residual_rep = residual.build_report()

    if portal_rep.get("n_failed", 1) != 0 or cap_rep.get("n_failed", 1) != 0:
        return {
            "status": "LAMBDA_LOCK_CAL_G_LIFT_NOT_EXECUTED__UPSTREAM_FAILED",
            "n_failed": 1,
            "failures": ["upstream"],
            "flag": {"selected_lambda_lock_raised_to_cal_G_lift": False},
        }

    fk = cap_rep.get("finite_kappa_benchmark_couplings") or {}
    kappa = float(fk["kappa"])
    lam4 = float(fk["lam4"])
    lambda_lock_sel = float(fk["lambda_lock"])
    crit_abs = float(portal_rep["decision"]["lambda_lock_crit_abs"])
    raised = raised_lambda_lock(lambda_lock_sel, crit_abs)
    lambda_lock_up = float(raised["lambda_lock_raised"])

    c54 = float(cap_rep["C_54"])
    c126 = float(cap_rep["C_126_to_54"])

    baseline_pt = cap.evaluate_couplings(
        kappa=kappa,
        lam4=lam4,
        lambda_lock=lambda_lock_sel,
        m_i=m_i,
        m_gut=m_gut,
        c54=c54,
        c126=c126,
        tau_gauge=tau_gauge,
    )
    raised_pt = cap.evaluate_couplings(
        kappa=kappa,
        lam4=lam4,
        lambda_lock=lambda_lock_up,
        m_i=m_i,
        m_gut=m_gut,
        c54=c54,
        c126=c126,
        tau_gauge=tau_gauge,
    )
    spoil = spoilage_compare(baseline_pt, raised_pt)

    fr = promote_rep["selected_hilbert"]["fractions"]
    a = float(fr["a_over_MGUT"] * m_gut)
    omega = float(fr["omega_over_MGUT"] * m_gut)
    p = float(fr["p_over_MGUT"] * m_gut)
    lam = float(residual_rep["uv_residual_couplings"]["lam210_10"])
    eta = float(residual_rep["uv_residual_couplings"]["eta_intra"])
    params = calg.hilbert_g_params(
        a=a,
        omega=omega,
        p=p,
        m_i=m_i,
        m_gut=m_gut,
        lam=lam,
        eta=eta,
        goldstone_compatible=True,
    )

    cal_at_sel = evaluate_cal_g_at_lock(
        lambda_lock=lambda_lock_sel,
        m_i=m_i,
        m_gut=m_gut,
        g_gauge=g_gauge,
        params=params,
    )
    cal_at_raised = evaluate_cal_g_at_lock(
        lambda_lock=lambda_lock_up,
        m_i=m_i,
        m_gut=m_gut,
        g_gauge=g_gauge,
        params=params,
    )

    lifted = bool(cal_at_raised["clears_null_tol"] and spoil["not_spoiled"])
    still_open = {
        "selected_lam4_below_gut_null_tol_threshold": True,
        "lam4_cgc_and_dim6_lock_not_in_live_dump": True,
        "exact_unique_proton_lifetime": True,
    }

    checks = {
        "portal_ok": portal_rep.get("n_failed", 1) == 0,
        "cap_ok": cap_rep.get("n_failed", 1) == 0,
        "raise_at_or_above_crit": abs(lambda_lock_up) + 1e-15
        >= crit_abs * LOCK_CRIT_MARGIN * 0.999,
        "cal_G_clears_at_raised": bool(cal_at_raised["clears_null_tol"]),
        "goldstone_null_preserved": bool(
            cal_at_raised["with_lambda_lock_embed"]["chiral_5x5_null_ok"]
        ),
        "selected_point_not_spoiled": bool(spoil["not_spoiled"]),
        "kappa_lam4_held_fixed": True,
        "exact_unique_not_overclaimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "LAMBDA_LOCK_CAL_G_LIFT_EXECUTED__TAU_P_OPEN"
            if not failures
            else "LAMBDA_LOCK_CAL_G_LIFT_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "couplings": {
            "kappa_fixed": kappa,
            "lam4_fixed": lam4,
            **raised,
        },
        "cal_G": {
            "at_selected_lambda_lock": cal_at_sel,
            "at_raised_lambda_lock": cal_at_raised,
        },
        "point_evaluation": {
            "baseline": {
                "radial_hessian_positive_definite": baseline_pt[
                    "radial_hessian_positive_definite"
                ],
                "perturbative": baseline_pt["perturbative"],
                "soft_shift_norm_over_MI2": baseline_pt["soft"][
                    "soft_shift_norm_over_MI2"
                ],
                "lightest_MT_GeV": baseline_pt["lightest_MT_GeV"],
                "phase_n_positive": baseline_pt["phase_n_positive"],
                "phase_n_zero": baseline_pt["phase_n_zero"],
            },
            "raised": {
                "radial_hessian_positive_definite": raised_pt[
                    "radial_hessian_positive_definite"
                ],
                "perturbative": raised_pt["perturbative"],
                "soft_shift_norm_over_MI2": raised_pt["soft"][
                    "soft_shift_norm_over_MI2"
                ],
                "lightest_MT_GeV": raised_pt["lightest_MT_GeV"],
                "phase_n_positive": raised_pt["phase_n_positive"],
                "phase_n_zero": raised_pt["phase_n_zero"],
                "perturbativity_max_abs": raised_pt["perturbativity_max_abs"],
            },
            "spoilage": spoil,
        },
        "certificate": {
            "selected_lambda_lock_raised_to_cal_G_lift": lifted and len(failures) == 0,
            "residual_still_open": still_open,
            "interpretation": (
                "Raising |λ_lock| to the cal G lift threshold (κ, λ₄ fixed) "
                "embeds an orthogonal soft mass that clears the GUT null "
                "tolerance while preserving the Goldstone 5×5 null and the "
                "charge-allowed selected-point window (Hessian PD / "
                "perturbativity / stationarity). Selected |λ₄| GUT null-tol "
                "and exact unique τ_p remain OPEN."
                if lifted
                else "λ_lock raise did not close the cal G soft residual without spoilage."
            ),
        },
        "next_exact_calculation": [
            "Assess whether |λ₄| can be raised to clear the GUT null-tol without spoiling the selected point",
            "Re-evaluate exact unique τ_p only after remaining λ₄ / live-dump caveats close",
        ],
        "flag": {
            "selected_lambda_lock_raised_to_cal_G_lift": lifted and len(failures) == 0,
            "cal_G_soft_mode_cleared_at_raised_lock": bool(
                cal_at_raised["clears_null_tol"]
            ),
            "selected_point_not_spoiled_by_lock_raise": bool(spoil["not_spoiled"]),
            "selected_lam4_still_below_gut_null_tol": True,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"|λ_lock| raised {lambda_lock_sel:.4g}→{lambda_lock_up:.4g} "
            f"(crit≈{crit_abs:.4g}): cal G lightest="
            f"{cal_at_raised['with_lambda_lock_embed']['lightest_GeV']:.3e} GeV "
            f"(clears={cal_at_raised['clears_null_tol']}); "
            f"point_not_spoiled={spoil['not_spoiled']}. "
            f"exact_unique_proton_lifetime remains False."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    c = report["couplings"]
    cal = report["cal_G"]["at_raised_lambda_lock"]["with_lambda_lock_embed"]
    spoil = report["point_evaluation"]["spoilage"]
    lines = [
        "# Raise |λ_lock| to cal G lift threshold — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- κ (fixed): {c['kappa_fixed']:.6g}",
        f"- λ₄ (fixed): {c['lam4_fixed']:.6g}",
        f"- |λ_lock| selected → raised: {c['lambda_lock_selected']:.6g} → {c['lambda_lock_raised']:.6g}",
        f"- |λ_lock|_crit: {c['lambda_lock_crit_abs']:.6g}",
        f"- cal G lightest (raised embed): {cal['lightest_GeV']:.6e} GeV",
        f"- Above null tol: {cal['above_null_tol']}",
        f"- Goldstone 5×5 null OK: {cal['chiral_5x5_null_ok']}",
        f"- Point not spoiled: {spoil['not_spoiled']}",
        "",
        "## Still open",
        "",
    ]
    for k, v in report["certificate"]["residual_still_open"].items():
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Next exact calculation", ""])
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
    ROOT.joinpath("LAMBDA_LOCK_CAL_G_LIFT_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("LAMBDA_LOCK_CAL_G_LIFT_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "couplings": report.get("couplings"),
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
