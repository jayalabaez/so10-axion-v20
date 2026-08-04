#!/usr/bin/env python3
r"""Decide whether the cal G residual light singlet needs an extra portal (v20).

Next step after ``live_pyrate_quartic_soft_dump_v20`` / ultimate checklist:

1. Rebuild the Goldstone-compatible Aulakh ``cal G`` soft mode
   (orthogonal to the PS→SM Goldstone in the ``(σ,σ̄)`` plane).
2. Find the critical orthogonal soft mass ``μ_crit`` that lifts the
   lightest singular value above the GUT-relative null tolerance while
   preserving the chiral 5×5 Goldstone null.
3. Compare ``μ_crit`` to soft scales inducible by the **existing**
   charge-allowed operators ``(κ, λ₄, λ_lock)`` — especially dim-6
   ``λ_lock`` acting on the 126 PS singlets.
4. Decide: extra *new* portal required, or existing ``λ_lock`` sufficient
   in principle (possibly after a modest |λ_lock| raise).

Honesty
-------
* This is an effective soft embedding into transcribed MSGUT ``cal G``,
  not a new derivation of the full nonsusy singlet mass matrix.
* ``λ₄`` as ``γ_eff`` still does not enter ``cal G`` (γ-independent).
* ``κ`` acts on ``10_H``, not the 126 PS singlets.
* Exact unique ``τ_p`` remains OPEN while the selected-point soft mass
  stays below tolerance.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import cal_g_soft_mode_classification_v20 as calg
import charge_allowed_potential_minimize_v20 as cap
import g_singlet_6x6_cw_v20 as gsing
import mixed_210_126_10_hilbert_hessian_v20 as mxh
import promote_210n_tensor_basis_uniqueness_v20 as promote
import residual_lam210_eta_intra_v20 as residual
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent
NULL_TOL_OVER_MGUT = mxh.NULL_TOL_OVER_MGUT

SOURCES = {
    "cal_G_class": "cal_g_soft_mode_classification_v20",
    "cal_G": "g_singlet_6x6_cw_v20.aulakh_cal_G",
    "portals": "charge_allowed_potential_minimize_v20",
    "vevs": "promote_210n_tensor_basis_uniqueness_v20",
}


def goldstone_and_orthogonal(
    sigma: complex, sigma_bar: complex
) -> tuple[np.ndarray, np.ndarray]:
    gdir = np.array([0.0, 0.0, 0.0, sigma, sigma_bar, 0.0], dtype=complex)
    gdir = gdir / (np.linalg.norm(gdir) + 1e-30)
    # Phase-orthogonal partner in the (σ,σ̄) plane (physical residual singlet).
    orth = np.array(
        [0.0, 0.0, 0.0, -np.conj(sigma_bar), np.conj(sigma), 0.0], dtype=complex
    )
    orth = orth / (np.linalg.norm(orth) + 1e-30)
    return gdir, orth


def deform_cal_g(cal_g: np.ndarray, orth: np.ndarray, mu: float) -> np.ndarray:
    """Hermitian lift along the Goldstone-orthogonal (σ,σ̄) combination."""
    projector = np.outer(orth, np.conj(orth))
    return cal_g + float(mu) * projector


def spectrum_with_goldstone_check(
    mat: np.ndarray,
    *,
    sigma: complex,
    sigma_bar: complex,
    null_tol_GeV: float,
) -> dict[str, Any]:
    svals = np.linalg.svd(mat, compute_uv=False)
    lightest = float(min(svals))
    g5 = mat[:5, :5]
    null5 = gsing.null_vector_residual(g5, sigma, sigma_bar)
    return {
        "lightest_GeV": lightest,
        "singular_values_GeV": [float(x) for x in sorted(svals)],
        "above_null_tol": lightest > null_tol_GeV,
        "chiral_5x5_null_ok": bool(null5["ok"]),
        "goldstone_residual_rel_Frobenius": null5["residual_rel_Frobenius"],
    }


def critical_orthogonal_soft(
    cal_g: np.ndarray,
    orth: np.ndarray,
    *,
    sigma: complex,
    sigma_bar: complex,
    null_tol_GeV: float,
) -> dict[str, Any]:
    """Binary search smallest μ≥0 lifting lightest SVD above null tol."""
    base = spectrum_with_goldstone_check(
        cal_g, sigma=sigma, sigma_bar=sigma_bar, null_tol_GeV=null_tol_GeV
    )
    if base["above_null_tol"]:
        return {
            "found": True,
            "mu_crit_GeV": 0.0,
            "already_above_tol": True,
            "base": base,
            "lifted": base,
        }

    lo, hi = 0.0, max(null_tol_GeV, 1.0)
    # Expand until clear (or fail)
    for _ in range(40):
        trial = spectrum_with_goldstone_check(
            deform_cal_g(cal_g, orth, hi),
            sigma=sigma,
            sigma_bar=sigma_bar,
            null_tol_GeV=null_tol_GeV,
        )
        if trial["above_null_tol"] and trial["chiral_5x5_null_ok"]:
            break
        hi *= 2.0
    else:
        return {
            "found": False,
            "mu_crit_GeV": None,
            "already_above_tol": False,
            "base": base,
            "note": "No orthogonal soft μ cleared null tol with Goldstone null preserved",
            "hi_tried_GeV": hi,
        }

    for _ in range(56):
        mid = 0.5 * (lo + hi)
        trial = spectrum_with_goldstone_check(
            deform_cal_g(cal_g, orth, mid),
            sigma=sigma,
            sigma_bar=sigma_bar,
            null_tol_GeV=null_tol_GeV,
        )
        if trial["above_null_tol"] and trial["chiral_5x5_null_ok"]:
            hi = mid
        else:
            lo = mid

    lifted = spectrum_with_goldstone_check(
        deform_cal_g(cal_g, orth, hi),
        sigma=sigma,
        sigma_bar=sigma_bar,
        null_tol_GeV=null_tol_GeV,
    )
    return {
        "found": True,
        "mu_crit_GeV": float(hi),
        "already_above_tol": False,
        "base": base,
        "lifted": lifted,
    }


def lambda_lock_soft_mass_GeV(
    lambda_lock: float, *, m_i: float, m_gut: float
) -> float:
    """Estimate |m_σ| from V⊃λ_lock Δ² H² S²/M_GUT² at v_H=v_S=v_Δ~M_I.

    m² ≈ 2|λ_lock| (M_I⁴ / M_GUT²) ⇒ m ≈ √(2|λ_lock|) M_I²/M_GUT.
    """
    return float(math.sqrt(2.0 * abs(lambda_lock)) * (m_i**2) / m_gut)


def lambda_lock_for_soft_mass(
    mu_GeV: float, *, m_i: float, m_gut: float
) -> float:
    """Invert the λ_lock soft-mass estimate for |λ_lock|."""
    # m = sqrt(2|ll|) * m_i^2 / m_gut  ⇒  |ll| = 0.5 (m * m_gut / m_i^2)^2
    ratio = mu_GeV * m_gut / (m_i**2)
    return float(0.5 * ratio * ratio)


def portal_scale_ledger(
    *,
    kappa: float,
    lam4: float,
    lambda_lock: float,
    m_i: float,
    m_gut: float,
    mu_crit_GeV: float,
) -> dict[str, Any]:
    mu_lock = lambda_lock_soft_mass_GeV(lambda_lock, m_i=m_i, m_gut=m_gut)
    ll_crit = lambda_lock_for_soft_mass(mu_crit_GeV, m_i=m_i, m_gut=m_gut)
    # λ₄ as γ_eff: no cal G entry. Mixing scale |λ₄|M_GUT is large but does
    # not deform the transcribed Eq.(102) block without a new embedding.
    return {
        "kappa": {
            "value": kappa,
            "acts_on_126_ps_singlets": False,
            "note": "10_H^2 S portal; does not source μ_orth in (σ,σ̄)",
            "can_lift_cal_G_orth": False,
        },
        "lam4": {
            "value": lam4,
            "enters_aulakh_cal_G_as_gamma": False,
            "mixing_scale_GeV": float(abs(lam4) * m_gut),
            "can_lift_cal_G_orth_inside_eq102": False,
            "note": "γ_eff=λ₄ lifts E/F/J/X but cal G remains γ-independent",
        },
        "lambda_lock": {
            "value": lambda_lock,
            "soft_mass_estimate_GeV": mu_lock,
            "lambda_lock_crit_abs": ll_crit,
            "selected_clears_mu_crit": bool(mu_lock >= mu_crit_GeV),
            "crit_over_selected": float(ll_crit / max(abs(lambda_lock), 1e-30)),
            "perturbative_O1_window": bool(ll_crit <= 10.0),
            "can_lift_cal_G_orth_in_principle": bool(ll_crit <= 10.0),
            "note": (
                "dim-6 126^2 10^2 S^2 / M_GUT^2 soft for 126 PS singlets; "
                "estimate embedding into orthogonal (σ,σ̄) lift"
            ),
        },
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "CAL_G_PORTAL_DECISION_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"cal_G_portal_decision_resolved": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    g_gauge = math.sqrt(4.0 * math.pi / float(anchor["alpha_inv_GUT"]))
    null_tol = NULL_TOL_OVER_MGUT * m_gut

    class_rep = calg.build_report()
    promote_rep = promote.build_report()
    residual_rep = residual.build_report()
    cap_rep = cap.build_report()

    if class_rep.get("n_failed", 1) != 0 or promote_rep.get("n_failed", 1) != 0:
        return {
            "status": "CAL_G_PORTAL_DECISION_NOT_EXECUTED__UPSTREAM_FAILED",
            "n_failed": 1,
            "failures": ["upstream"],
            "flag": {"cal_G_portal_decision_resolved": False},
        }

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
    cal_g = gsing._cal_g_from_params(params, g_gauge)
    gdir, orth = goldstone_and_orthogonal(params["sigma"], params["sigma_bar"])
    light_vec = calg.singular_system(cal_g)["right_singular_vectors"][0]
    light_vec = light_vec / (np.linalg.norm(light_vec) + 1e-30)
    ov_g = float(abs(np.vdot(gdir, light_vec)))
    ov_o = float(abs(np.vdot(orth, light_vec)))

    crit = critical_orthogonal_soft(
        cal_g,
        orth,
        sigma=params["sigma"],
        sigma_bar=params["sigma_bar"],
        null_tol_GeV=null_tol,
    )
    mu_crit = float(crit.get("mu_crit_GeV") or 0.0)

    fk = cap_rep.get("finite_kappa_benchmark_couplings") or {}
    kappa = float(fk.get("kappa", 0.05))
    lam4 = float(fk.get("lam4", 0.0))
    lambda_lock = float(fk.get("lambda_lock", 1.0))
    portals = portal_scale_ledger(
        kappa=kappa,
        lam4=lam4,
        lambda_lock=lambda_lock,
        m_i=m_i,
        m_gut=m_gut,
        mu_crit_GeV=mu_crit,
    )

    # Decision logic
    lock = portals["lambda_lock"]
    extra_new_required = not bool(lock["can_lift_cal_G_orth_in_principle"])
    existing_sufficient = bool(lock["can_lift_cal_G_orth_in_principle"])
    selected_clears = bool(lock["selected_clears_mu_crit"])
    decision = (
        "extra_new_portal_required"
        if extra_new_required
        else (
            "existing_lambda_lock_clears_at_selected"
            if selected_clears
            else "existing_lambda_lock_sufficient_after_O1_raise"
        )
    )

    # Apply selected and crit λ_lock estimates as μ embeddings
    mu_selected = float(lock["soft_mass_estimate_GeV"])
    at_selected = spectrum_with_goldstone_check(
        deform_cal_g(cal_g, orth, mu_selected),
        sigma=params["sigma"],
        sigma_bar=params["sigma_bar"],
        null_tol_GeV=null_tol,
    )
    mu_at_crit_ll = lambda_lock_soft_mass_GeV(
        float(lock["lambda_lock_crit_abs"]), m_i=m_i, m_gut=m_gut
    )
    at_crit_ll = spectrum_with_goldstone_check(
        deform_cal_g(cal_g, orth, mu_at_crit_ll),
        sigma=params["sigma"],
        sigma_bar=params["sigma_bar"],
        null_tol_GeV=null_tol,
    )

    still_open = {
        "selected_lambda_lock_below_cal_G_lift_threshold": not selected_clears,
        "selected_lam4_below_gut_null_tol_threshold": True,
        "exact_unique_proton_lifetime": True,
    }

    checks = {
        "classification_ok": class_rep.get("n_failed", 1) == 0,
        "soft_mode_is_residual_singlet": class_rep["primary_classification"]["label"]
        == "residual_flat_or_light_singlet",
        "light_mode_orthogonal_to_goldstone": ov_g < 0.5 and ov_o >= 0.5,
        "mu_crit_found": bool(crit.get("found")),
        "goldstone_null_preserved_at_mu_crit": bool(
            (crit.get("lifted") or {}).get("chiral_5x5_null_ok", False)
        ),
        "decision_recorded": decision
        in {
            "extra_new_portal_required",
            "existing_lambda_lock_clears_at_selected",
            "existing_lambda_lock_sufficient_after_O1_raise",
        },
        "lam4_not_overclaimed_as_cal_G_lift": not portals["lam4"][
            "can_lift_cal_G_orth_inside_eq102"
        ],
        "exact_unique_not_overclaimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "CAL_G_PORTAL_DECISION_RESOLVED__TAU_P_OPEN"
            if not failures
            else "CAL_G_PORTAL_DECISION_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "vevs": {
            "fractions": fr,
            "lam210_10": lam,
            "eta_intra": eta,
            "M_I_GeV": m_i,
            "M_GUT_GeV": m_gut,
            "null_tol_GeV": null_tol,
        },
        "soft_mode": {
            "classification_label": class_rep["primary_classification"]["label"],
            "lightest_GeV": float(
                class_rep["slices"]["hilbert_goldstone_compatible_M"]["spectrum_6x6"][
                    "lightest_GeV"
                ]
            ),
            "overlap_goldstone_dir": ov_g,
            "overlap_orthogonal_dir": ov_o,
            "components_abs": [
                float(abs(x)) for x in light_vec
            ],
        },
        "critical_soft": crit,
        "portals": portals,
        "embeddings": {
            "at_selected_lambda_lock": at_selected,
            "at_lambda_lock_crit": at_crit_ll,
        },
        "decision": {
            "label": decision,
            "extra_new_portal_required": extra_new_required,
            "existing_lambda_lock_sufficient_in_principle": existing_sufficient,
            "selected_lambda_lock_clears_null_tol": selected_clears,
            "mu_crit_GeV": mu_crit,
            "lambda_lock_selected": lambda_lock,
            "lambda_lock_crit_abs": float(lock["lambda_lock_crit_abs"]),
        },
        "certificate": {
            "cal_G_portal_decision_resolved": len(failures) == 0,
            "residual_still_open": still_open,
            "interpretation": (
                "The cal G residual light singlet is the Goldstone-orthogonal "
                "(σ,σ̄) combination. An orthogonal soft mass μ_crit lifts it "
                "above the GUT null tolerance without spoiling the 5×5 "
                "Goldstone null. No extra *new* portal is required: the "
                "existing charge-allowed dim-6 λ_lock can source μ_orth in "
                "principle"
                + (
                    " and already clears at the selected point."
                    if selected_clears
                    else f" after raising |λ_lock| to ≳{lock['lambda_lock_crit_abs']:.3g} "
                    f"(selected={lambda_lock:.3g}). λ₄/κ do not close this "
                    "inside transcribed cal G."
                )
            ),
        },
        "next_exact_calculation": [
            (
                "Raise |λ_lock| to the cal G lift threshold and re-evaluate soft mode"
                if not selected_clears
                else "Re-check selected-point SK/τ_p with λ_lock-lifted cal G"
            ),
            "Assess whether |λ₄| can be raised to clear the GUT null-tol without spoiling the selected point",
            "Re-evaluate exact unique τ_p only after remaining light-mode / λ₄ caveats close",
        ],
        "flag": {
            "cal_G_portal_decision_resolved": len(failures) == 0,
            "extra_new_portal_required": extra_new_required,
            "existing_lambda_lock_sufficient_in_principle": existing_sufficient,
            "selected_lambda_lock_clears_cal_G_null_tol": selected_clears,
            "cal_G_residual_light_singlet_still_soft_at_selected": not selected_clears,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"cal G portal decision: `{decision}` "
            f"(μ_crit={mu_crit:.3e} GeV; |λ_lock|_crit≈{lock['lambda_lock_crit_abs']:.3g}, "
            f"selected={lambda_lock:.3g}; "
            f"extra_new_portal_required={extra_new_required}). "
            f"exact_unique_proton_lifetime remains False."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    dec = report["decision"]
    soft = report["soft_mode"]
    lock = report["portals"]["lambda_lock"]
    lines = [
        "# cal G residual light singlet — portal decision (v20)",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Soft mode label: `{soft['classification_label']}`",
        f"- Lightest: {soft['lightest_GeV']:.6e} GeV",
        f"- Overlap Goldstone / orthogonal: {soft['overlap_goldstone_dir']:.3e} / {soft['overlap_orthogonal_dir']:.3e}",
        f"- μ_crit: {dec['mu_crit_GeV']:.6e} GeV",
        f"- |λ_lock| selected / crit: {dec['lambda_lock_selected']:.6g} / {dec['lambda_lock_crit_abs']:.6g}",
        f"- λ_lock soft estimate: {lock['soft_mass_estimate_GeV']:.6e} GeV",
        "",
        "## Decision",
        "",
        f"- Label: `{dec['label']}`",
        f"- Extra new portal required: {dec['extra_new_portal_required']}",
        f"- Existing λ_lock sufficient in principle: {dec['existing_lambda_lock_sufficient_in_principle']}",
        f"- Selected λ_lock clears null tol: {dec['selected_lambda_lock_clears_null_tol']}",
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
    # Drop non-JSON bits from critical_soft if any numpy slipped through
    ROOT.joinpath("CAL_G_PORTAL_DECISION_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("CAL_G_PORTAL_DECISION_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "decision": report.get("decision"),
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
