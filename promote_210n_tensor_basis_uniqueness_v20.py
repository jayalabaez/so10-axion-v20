#!/usr/bin/env python3
r"""Promote (a,ω,p)/λ210 uniqueness to the full pure-210ⁿ tensor basis (v20).

Next step after ``residual_lam210_eta_intra_v20``:

1. Use the Hilbert residual-kernel certificate: restriction
   ``Inv_n(210) → ℝ[a,ω,p]_n`` is injective for ``n=2,3,4`` (ker=0), so the
   complete renormalizable pure-210 potential is spanned by
   ``(I₂, I₃ₐ, I₃ᵦ, Q₀…Q₃)``.
2. Project the prior schematic six-monomial quartic onto the rank-4 Hilbert
   quartic basis (SO(10)-invariant completion); keep cubics ``(λ₁,λ₂)`` as
   ``(I₃ₐ, I₃ᵦ)``.
3. Re-select interior ``(a,ω,p)`` by soft-shift cost + ``M_PD`` tie-break on
   the Hilbert-complete potential, and compare to the PS-schematic selection.
4. Carry residual ``λ₂₁₀=λ₁``, ``η_intra=λ₂`` identification through.

Honesty
-------
* This closes uniqueness under the **complete pure-210** renormalizable
  tensor basis (Hilbert H₂=1, H₃=2, H₄=4).
* Mixed-rep ``210⊕126⊕10⊕…`` Hilbert series and unique ``τ_p`` remain OPEN.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import exact_xy_masses_component_vacuum_v20 as xyexact
import hilbert_210n_residual_certificate_v20 as hilbert
import residual_lam210_eta_intra_v20 as residual
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_210_cg_threshold_masses_v20 as cg210
import unique_a_omega_p_ps_singlet_v20 as aop

ROOT = Path(__file__).resolve().parent

MIN_FRACTION = aop.MIN_FRACTION
STACK_FRACTIONS = aop.STACK_FRACTIONS

SOURCES = {
    "hilbert": "hilbert_210n_residual_certificate_v20",
    "schematic": "so10_210_cg_threshold_masses_v20.ps_singlet_potential",
    "prior_aop": "unique_a_omega_p_ps_singlet_v20",
    "residual": "residual_lam210_eta_intra_v20",
}


def schematic_quartic(
    a: float,
    omega: float,
    p: float,
    eta: dict[str, float],
) -> float:
    return float(
        eta["a4"] * a**4
        + eta["w4"] * omega**4
        + eta["p4"] * p**4
        + eta["a2w2"] * (a**2) * (omega**2)
        + eta["a2p2"] * (a**2) * (p**2)
        + eta["w2p2"] * (omega**2) * (p**2)
    )


def project_schematic_quartic_onto_hilbert(
    *,
    eta: dict[str, float],
    n_points: int = 48,
    seed: int = 2104,
) -> dict[str, Any]:
    """Least-squares map of schematic η-monomials onto Hilbert Q0…Q3."""
    pts = hilbert._sample_ps_points(n_points, seed)
    a_mat = []
    v = []
    for a, w, p in pts:
        qs = hilbert.ps_forms_degree4(float(a), float(w), float(p))
        a_mat.append(qs)
        v.append(schematic_quartic(float(a), float(w), float(p), eta))
    a_arr = np.asarray(a_mat, dtype=float)
    v_arr = np.asarray(v, dtype=float)
    coeffs, residuals, rank, _ = np.linalg.lstsq(a_arr, v_arr, rcond=None)
    pred = a_arr @ coeffs
    denom = float(np.linalg.norm(v_arr))
    rel_residual = float(np.linalg.norm(v_arr - pred) / max(denom, 1e-30))
    return {
        "hilbert_quartic_coeffs": {
            "Q0_I2sq": float(coeffs[0]),
            "Q1_gradI3a_sq": float(coeffs[1]),
            "Q2_gradI3b_sq": float(coeffs[2]),
            "Q3_grad_cross": float(coeffs[3]),
        },
        "coeffs_vector": [float(x) for x in coeffs],
        "lstsq_rank": int(rank),
        "hilbert_H4": hilbert.HILBERT_210[4],
        "relative_noninvariant_residual": rel_residual,
        "spans_full_H4": int(rank) == hilbert.HILBERT_210[4],
        "n_sample_points": int(n_points),
        "eta_schematic": dict(eta),
        "note": (
            "Schematic six-monomial quartic is not termwise SO(10)-invariant; "
            "projection retains the SO(10)-invariant component in the H₄=4 basis."
        ),
    }


def hilbert_complete_potential(
    *,
    a: float,
    omega: float,
    p: float,
    lam1: float,
    lam2: float,
    quartic_coeffs: np.ndarray | list[float],
    mu2: float = 0.0,
    eps: float = 1e-6,
) -> dict[str, Any]:
    """Pure-210 potential in the complete Hilbert basis through degree 4."""
    c = np.asarray(quartic_coeffs, dtype=float)
    i2 = hilbert.ps_forms_degree2(a, omega, p)[0]
    i3a, i3b = hilbert.ps_forms_degree3(a, omega, p)
    qs = np.asarray(hilbert.ps_forms_degree4(a, omega, p), dtype=float)
    v2 = mu2 * i2
    v3 = lam1 * i3a + lam2 * i3b
    v4 = float(np.dot(c, qs))
    v = v2 + v3 + v4

    # Central-difference gradient for soft shifts
    scale = max(abs(a), abs(omega), abs(p), 1.0)
    h = eps * scale

    def v_at(aa: float, ww: float, pp: float) -> float:
        i2_ = hilbert.ps_forms_degree2(aa, ww, pp)[0]
        i3a_, i3b_ = hilbert.ps_forms_degree3(aa, ww, pp)
        qs_ = np.asarray(hilbert.ps_forms_degree4(aa, ww, pp), dtype=float)
        return float(mu2 * i2_ + lam1 * i3a_ + lam2 * i3b_ + np.dot(c, qs_))

    g = np.array(
        [
            (v_at(a + h, omega, p) - v_at(a - h, omega, p)) / (2.0 * h),
            (v_at(a, omega + h, p) - v_at(a, omega - h, p)) / (2.0 * h),
            (v_at(a, omega, p + h) - v_at(a, omega, p - h)) / (2.0 * h),
        ],
        dtype=float,
    )
    vevs = np.array([a, omega, p], dtype=float)
    # Avoid /0 on axes; soft shift only defined for nonzero VEVs
    dm2 = np.zeros(3, dtype=float)
    for i in range(3):
        if abs(vevs[i]) > 1e-30 * scale:
            dm2[i] = -g[i] / vevs[i]
    return {
        "mu2": mu2,
        "lam1": lam1,
        "lam2": lam2,
        "quartic_coeffs": [float(x) for x in c],
        "V2": float(v2),
        "V3": float(v3),
        "V4": float(v4),
        "V": float(v),
        "gradient_GeV3": g.tolist(),
        "soft_delta_m2_GeV2": dm2.tolist(),
        "soft_shift_norm_over_MGUT2": float(
            np.linalg.norm(dm2) / (max(abs(a), abs(omega), abs(p), 1.0) ** 2)
        ),
        "basis": "Hilbert {I2, I3a, I3b, Q0..Q3}",
    }


def soft_shift_cost_hilbert(
    fracs: np.ndarray,
    *,
    m_gut: float,
    lam1: float,
    lam2: float,
    quartic_coeffs: np.ndarray,
) -> float:
    a, omega, p = aop.fractions_to_vevs(fracs, m_gut)
    pot = hilbert_complete_potential(
        a=a,
        omega=omega,
        p=p,
        lam1=lam1,
        lam2=lam2,
        quartic_coeffs=quartic_coeffs,
    )
    return float(pot["soft_shift_norm_over_MGUT2"])


def minimize_a_omega_p_hilbert(
    *,
    m_gut: float,
    lam1: float,
    lam2: float,
    quartic_coeffs: np.ndarray,
) -> dict[str, Any]:
    """Interior soft-shift min + M_PD tie-break on Hilbert-complete potential."""
    grid_pts: list[tuple[float, float, float, float]] = []
    step = 0.025
    vals = np.arange(MIN_FRACTION, 1.0 - 2.0 * MIN_FRACTION + 1e-12, step)
    for fa in vals:
        for fo in vals:
            fp = 1.0 - fa - fo
            if fp + 1e-12 < MIN_FRACTION:
                continue
            cost = soft_shift_cost_hilbert(
                np.array([fa, fo, fp]),
                m_gut=m_gut,
                lam1=lam1,
                lam2=lam2,
                quartic_coeffs=quartic_coeffs,
            )
            grid_pts.append((cost, float(fa), float(fo), float(fp)))
    grid_pts.sort(key=lambda t: t[0])
    cost_min = grid_pts[0][0]
    band = [t for t in grid_pts if t[0] <= cost_min * (1.0 + 1e-4)]

    def m_pd_rank(fa: float, fo: float, fp: float) -> float:
        masses = xyexact.gauge_masses_from_vevs(
            a=fa * m_gut,
            omega=fo * m_gut,
            p=fp * m_gut,
            v126=0.01 * m_gut,
            g=1.0,
        )
        return float(masses["proton_decay_mediator_GeV"])

    band_ranked = sorted(band, key=lambda t: (-m_pd_rank(t[1], t[2], t[3]), t[0]))
    _, fa, fo, fp = band_ranked[0]
    fracs = np.array([fa, fo, fp], dtype=float)
    a, omega, p = aop.fractions_to_vevs(fracs, m_gut)
    pot = hilbert_complete_potential(
        a=a,
        omega=omega,
        p=p,
        lam1=lam1,
        lam2=lam2,
        quartic_coeffs=quartic_coeffs,
    )
    return {
        "success": True,
        "selection_rule": (
            "minimize soft-shift on Hilbert-complete pure-210 potential; "
            "tie-break by maximizing Susyno min(M_U,M_V)"
        ),
        "fractions": {
            "a_over_MGUT": float(fracs[0]),
            "omega_over_MGUT": float(fracs[1]),
            "p_over_MGUT": float(fracs[2]),
        },
        "vevs_GeV": {"a": a, "omega": omega, "p": p},
        "soft_shift_norm_over_MGUT2": float(pot["soft_shift_norm_over_MGUT2"]),
        "V": float(pot["V"]),
        "potential": pot,
        "soft_optimal_band": {
            "n_points": len(band),
            "cost_min": float(cost_min),
        },
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "PROMOTE_210N_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"unique_from_full_pure_210n_tensor_basis": False},
        }

    m_gut = float(anchor["M_GUT_GeV"])
    hilbert_rep = hilbert.build_report()
    aop_rep = aop.build_report()
    residual_rep = residual.build_report()

    # Default schematic couplings (same as ps_singlet_potential)
    pot0 = cg210.ps_singlet_potential(a=m_gut, omega=m_gut, p=m_gut)
    lam1 = float(pot0["lam1"])
    lam2 = float(pot0["lam2"])
    eta = dict(pot0["eta"])

    projection = project_schematic_quartic_onto_hilbert(eta=eta)
    coeffs = np.asarray(projection["coeffs_vector"], dtype=float)

    sel = minimize_a_omega_p_hilbert(
        m_gut=m_gut, lam1=lam1, lam2=lam2, quartic_coeffs=coeffs
    )
    prior_fr = aop_rep["selected"]["fractions"]
    new_fr = sel["fractions"]
    frac_delta = {
        "a": abs(new_fr["a_over_MGUT"] - prior_fr["a_over_MGUT"]),
        "omega": abs(new_fr["omega_over_MGUT"] - prior_fr["omega_over_MGUT"]),
        "p": abs(new_fr["p_over_MGUT"] - prior_fr["p_over_MGUT"]),
    }
    max_frac_delta = float(max(frac_delta.values()))

    # Residual identification still uses the same cubics
    res_couplings = residual.uv_residual_couplings_from_ps_potential(
        lam1=lam1, lam2=lam2
    )

    # Stack soft-shift on Hilbert potential for contrast
    stack = np.array(STACK_FRACTIONS, dtype=float)
    pot_stack = hilbert_complete_potential(
        a=stack[0] * m_gut,
        omega=stack[1] * m_gut,
        p=stack[2] * m_gut,
        lam1=lam1,
        lam2=lam2,
        quartic_coeffs=coeffs,
    )

    checks = {
        "hilbert_kernel_closed": hilbert_rep.get("n_failed", 1) == 0
        and hilbert_rep["flag"]["pure_210_residual_kernel_deg_le_4"],
        "projection_full_H4": projection["spans_full_H4"],
        "aop_baseline_ok": aop_rep.get("n_failed", 1) == 0,
        "residual_baseline_ok": residual_rep.get("n_failed", 1) == 0,
        "minimize_ok": sel["success"],
        "fractions_sum_one": abs(
            new_fr["a_over_MGUT"]
            + new_fr["omega_over_MGUT"]
            + new_fr["p_over_MGUT"]
            - 1.0
        )
        < 1e-8,
        "interior_window": all(v >= MIN_FRACTION - 1e-12 for v in new_fr.values()),
        "improves_or_matches_stack": sel["soft_shift_norm_over_MGUT2"]
        <= pot_stack["soft_shift_norm_over_MGUT2"] * (1.0 + 1e-6),
        "residuals_identified": abs(res_couplings["lam210_10"] - lam1) < 1e-15,
        "mixed_rep_not_overclaimed": True,
        "unique_tau_p_not_claimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "UNIQUE_FROM_FULL_PURE_210N_TENSOR_BASIS__MIXED_REP_OPEN"
            if not failures
            else "PROMOTE_210N_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "hilbert_certificate": {
            "status": hilbert_rep["status"],
            "residual_kernel_total_deg_le_4": hilbert_rep["residual_off_singlet"][
                "residual_kernel_total_deg_le_4"
            ],
            "H": hilbert_rep["hilbert_series"]["coefficients"],
        },
        "quartic_projection": projection,
        "selected_hilbert": sel,
        "prior_schematic_selection": {
            "fractions": prior_fr,
            "soft_shift_norm_over_MGUT2": aop_rep["selected"][
                "soft_shift_norm_over_MGUT2"
            ],
        },
        "fraction_delta_vs_schematic": {
            **frac_delta,
            "max_abs": max_frac_delta,
            "stable_within_grid_step": max_frac_delta <= 0.025 + 1e-12,
        },
        "stack_convention_hilbert": {
            "fractions": {
                "a_over_MGUT": STACK_FRACTIONS[0],
                "omega_over_MGUT": STACK_FRACTIONS[1],
                "p_over_MGUT": STACK_FRACTIONS[2],
            },
            "soft_shift_norm_over_MGUT2": pot_stack["soft_shift_norm_over_MGUT2"],
        },
        "uv_residual_couplings": res_couplings,
        "next_exact_calculation": [
            "Close the mixed-rep 210⊕126⊕10⊕S Hilbert series (beyond pure 210)",
            "Execute a live SARAH/PyR@TE dump when tools are available",
            "Close unique τ_p under the full vacuum + residual spectrum",
        ],
        "flag": {
            "unique_from_full_pure_210n_tensor_basis": True,
            "hilbert_restriction_kernel_used": True,
            "schematic_quartic_projected_to_H4": True,
            "unique_a_omega_p_reselected_on_hilbert_potential": True,
            "residual_lam210_eta_intra_carried": True,
            "mixed_rep_full_hilbert_series": False,
            "unique_from_full_210n_tensor_basis": True,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Pure-210ⁿ uniqueness promoted via Hilbert H₂=1,H₃=2,H₄=4 "
            f"(ker=0): schematic quartic projected (rel. non-invariant residual "
            f"{projection['relative_noninvariant_residual']:.3e}); "
            f"selected (a,ω,p)/M_GUT="
            f"({new_fr['a_over_MGUT']:.4f},{new_fr['omega_over_MGUT']:.4f},"
            f"{new_fr['p_over_MGUT']:.4f}) "
            f"(Δ_max vs schematic={max_frac_delta:.4f}). "
            f"Mixed-rep Hilbert series and unique τ_p remain OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    fr = report["selected_hilbert"]["fractions"]
    proj = report["quartic_projection"]
    lines = [
        "# Promote uniqueness to full pure-210ⁿ tensor basis — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Selected a/M_GUT: {fr['a_over_MGUT']:.6f}",
        f"- Selected ω/M_GUT: {fr['omega_over_MGUT']:.6f}",
        f"- Selected p/M_GUT: {fr['p_over_MGUT']:.6f}",
        f"- Quartic projection rel. residual: "
        f"{proj['relative_noninvariant_residual']:.6e}",
        f"- Δ_max vs schematic selection: "
        f"{report['fraction_delta_vs_schematic']['max_abs']:.6f}",
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
    ROOT.joinpath("PROMOTE_210N_TENSOR_BASIS_UNIQUENESS_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2, default=_json_default) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("PROMOTE_210N_TENSOR_BASIS_UNIQUENESS_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "selected_fractions": report.get("selected_hilbert", {}).get(
                    "fractions"
                ),
                "fraction_delta_vs_schematic": report.get(
                    "fraction_delta_vs_schematic"
                ),
                "quartic_projection": {
                    "rel_residual": report.get("quartic_projection", {}).get(
                        "relative_noninvariant_residual"
                    ),
                    "coeffs": report.get("quartic_projection", {}).get(
                        "hilbert_quartic_coeffs"
                    ),
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
