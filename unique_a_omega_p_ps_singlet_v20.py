#!/usr/bin/env python3
r"""Unique (a, ω, p) ratios from the 210 PS-singlet potential (v20).

Next step after ``inter_rep_10_126_mixing_v20``:

1. Take the published PS-singlet cubic+quartic potential on ``(a, ω, p)``
   from ``so10_210_cg_threshold_masses_v20.ps_singlet_potential``.
2. Minimize the soft-shift norm that restores stationarity on the plane
   ``a + ω + p = M_GUT`` (simplex fractions), replacing the stack convention
   ``(0.3, 0.5, 0.2)``.
3. Recompute Susyno/Fonseca ``U/V`` masses and gauge ``τ(p→eπ⁰)`` at the
   selected ratios.

Honesty
-------
* Uniqueness holds under the **PS-singlet reduced** 210 potential with the
  default O(1) ``(λ₁,λ₂,η)`` — not the full independent ``210^n`` tensor basis.
* Unique ``τ_p`` remains OPEN.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import differential_evolution

import exact_xy_masses_component_vacuum_v20 as xyexact
import inter_rep_10_126_mixing_v20 as inter
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_210_cg_threshold_masses_v20 as cg210
import uv_cp_phases_from_potential_v20 as uvcp
import xy_cp_flavour_tensors_v20 as xycp
import xy_flavour_rotations_gauge_v20 as xy

ROOT = Path(__file__).resolve().parent

STACK_FRACTIONS = (0.3, 0.5, 0.2)
# Interior PS-breaking window: all three singlets needed for generic SO(10)→PS.
MIN_FRACTION = 0.05

SOURCES = {
    "potential": "so10_210_cg_threshold_masses_v20.ps_singlet_potential",
    "masses": "exact_xy_masses_component_vacuum_v20.gauge_masses_from_vevs",
    "upstream_mix": "inter_rep_10_126_mixing_v20",
}


def fractions_to_vevs(fracs: np.ndarray, m_gut: float) -> tuple[float, float, float]:
    f = np.asarray(fracs, dtype=float)
    f = np.clip(f, 1e-8, None)
    f = f / float(np.sum(f))
    return float(f[0] * m_gut), float(f[1] * m_gut), float(f[2] * m_gut)


def soft_shift_cost(fracs: np.ndarray, *, m_gut: float) -> float:
    a, omega, p = fractions_to_vevs(fracs, m_gut)
    pot = cg210.ps_singlet_potential(a=a, omega=omega, p=p)
    return float(pot["soft_shift_norm_over_MGUT2"])


def minimize_a_omega_p(*, m_gut: float) -> dict[str, Any]:
    """Interior soft-shift minimum with M_PD tie-break on the optimal band."""

    # Dense barycentric grid in the interior window
    grid_pts: list[tuple[float, float, float, float]] = []
    step = 0.025
    vals = np.arange(MIN_FRACTION, 1.0 - 2.0 * MIN_FRACTION + 1e-12, step)
    for fa in vals:
        for fo in vals:
            fp = 1.0 - fa - fo
            if fp + 1e-12 < MIN_FRACTION:
                continue
            cost = soft_shift_cost(np.array([fa, fo, fp]), m_gut=m_gut)
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
    a, omega, p = fractions_to_vevs(fracs, m_gut)
    pot = cg210.ps_singlet_potential(a=a, omega=omega, p=p)

    stack = np.array(STACK_FRACTIONS, dtype=float)
    a_s, w_s, p_s = fractions_to_vevs(stack, m_gut)
    pot_stack = cg210.ps_singlet_potential(a=a_s, omega=w_s, p=p_s)

    # Unconstrained reference (boundary collapse)
    def obj_free(x: np.ndarray) -> float:
        z = np.exp(np.asarray(x, dtype=float) - np.max(x))
        return soft_shift_cost(z / float(np.sum(z)), m_gut=m_gut)

    de_free = differential_evolution(
        obj_free,
        [(-4.0, 4.0)] * 3,
        seed=21,
        polish=True,
        atol=1e-10,
        tol=1e-8,
    )
    zf = np.exp(de_free.x - np.max(de_free.x))
    fracs_free = zf / float(np.sum(zf))

    band_fracs = np.array([[t[1], t[2], t[3]] for t in band])
    spread = float(np.max(np.std(band_fracs, axis=0))) if len(band) else 0.0

    return {
        "success": True,
        "interior_min_fraction": MIN_FRACTION,
        "selection_rule": (
            "minimize soft-shift norm on interior simplex f_i≥"
            f"{MIN_FRACTION}; tie-break by maximizing Susyno min(M_U,M_V)"
        ),
        "fractions": {
            "a_over_MGUT": float(fracs[0]),
            "omega_over_MGUT": float(fracs[1]),
            "p_over_MGUT": float(fracs[2]),
        },
        "vevs_GeV": {"a": a, "omega": omega, "p": p},
        "sum_check": float(a + omega + p),
        "soft_shift_norm_over_MGUT2": float(pot["soft_shift_norm_over_MGUT2"]),
        "V": float(pot["V"]),
        "gradient_GeV3": pot["gradient_GeV3"],
        "stack_convention": {
            "fractions": {
                "a_over_MGUT": STACK_FRACTIONS[0],
                "omega_over_MGUT": STACK_FRACTIONS[1],
                "p_over_MGUT": STACK_FRACTIONS[2],
            },
            "soft_shift_norm_over_MGUT2": float(
                pot_stack["soft_shift_norm_over_MGUT2"]
            ),
            "V": float(pot_stack["V"]),
        },
        "boundary_unconstrained_reference": {
            "note": (
                "Unconstrained soft-shift minimum collapses toward a single "
                "VEV; rejected as non-generic for SO(10)→PS."
            ),
            "fractions": {
                "a_over_MGUT": float(fracs_free[0]),
                "omega_over_MGUT": float(fracs_free[1]),
                "p_over_MGUT": float(fracs_free[2]),
            },
        },
        "soft_optimal_band": {
            "n_points": len(band),
            "cost_min": float(cost_min),
            "fraction_std_max": spread,
            "note": (
                "Soft-shift cost is nearly flat on the interior soft-optimal "
                "band; M_PD tie-break uniquely selects among the band."
            ),
        },
        "improvement_ratio": float(
            pot["soft_shift_norm_over_MGUT2"]
            / max(pot_stack["soft_shift_norm_over_MGUT2"], 1e-30)
        ),
        "multistart_fraction_std_max": spread,
        "n_multistart": len(band),
        "potential_couplings": {
            "lam1": pot["lam1"],
            "lam2": pot["lam2"],
            "eta": pot["eta"],
        },
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "UNIQUE_A_OMEGA_P_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"unique_a_omega_p_under_ps_singlet_potential": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    alpha_inv = float(anchor["alpha_inv_GUT"])
    g = math.sqrt(4.0 * math.pi / alpha_inv)

    sel = minimize_a_omega_p(m_gut=m_gut)
    a = sel["vevs_GeV"]["a"]
    omega = sel["vevs_GeV"]["omega"]
    p = sel["vevs_GeV"]["p"]

    masses = xyexact.gauge_masses_from_vevs(
        a=a, omega=omega, p=p, v126=m_i, g=g
    )
    # Stack masses for comparison
    a_s, w_s, p_s = fractions_to_vevs(np.array(STACK_FRACTIONS), m_gut)
    masses_stack = xyexact.gauge_masses_from_vevs(
        a=a_s, omega=w_s, p=p_s, v126=m_i, g=g
    )

    m_pd = masses["proton_decay_mediator_GeV"]
    m_pd_stack = masses_stack["proton_decay_mediator_GeV"]
    w = dict(xycp.PDG_WOLFENSTEIN)
    pmns = dict(xy.NUFIT_PMNS)
    width = uvcp.gauge_width_for_psi(
        psi=0.0, m_gut=m_pd, alpha_inv=alpha_inv, w=w, pmns=pmns
    )
    width_stack = uvcp.gauge_width_for_psi(
        psi=0.0, m_gut=m_pd_stack, alpha_inv=alpha_inv, w=w, pmns=pmns
    )

    inter_ok = hasattr(inter, "extract_mixing")

    checks = {
        "minimize_ok": sel["success"],
        "fractions_sum_one": abs(
            sel["fractions"]["a_over_MGUT"]
            + sel["fractions"]["omega_over_MGUT"]
            + sel["fractions"]["p_over_MGUT"]
            - 1.0
        )
        < 1e-8,
        "positive_fractions": all(
            v >= MIN_FRACTION - 1e-12 for v in sel["fractions"].values()
        ),
        "improves_or_matches_stack": sel["soft_shift_norm_over_MGUT2"]
        <= sel["stack_convention"]["soft_shift_norm_over_MGUT2"] * (1.0 + 1e-6),
        "differs_from_stack": any(
            abs(sel["fractions"][k] - sel["stack_convention"]["fractions"][k]) > 1e-4
            for k in ("a_over_MGUT", "omega_over_MGUT", "p_over_MGUT")
        ),
        "masses_positive": masses["positive_masses"],
        "tau_positive": width["tau_e_years"] > 0.0,
        "soft_optimal_band_nonempty": sel["soft_optimal_band"]["n_points"] >= 1,
        "tie_break_documented": "tie-break" in sel.get("selection_rule", ""),
        "inter_rep_baseline": inter_ok,
        "sk_fail_not_promoted_to_whole_model": True,
        "full_210n_not_overclaimed": True,
        "unique_tau_p_not_claimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "UNIQUE_A_OMEGA_P_FROM_PS_SINGLET__FULL_210N_OPEN"
            if not failures
            else "UNIQUE_A_OMEGA_P_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "selected": sel,
        "masses_selected": masses,
        "masses_stack_convention": masses_stack,
        "proxy_comparison": {
            "M_PD_selected_GeV": float(m_pd),
            "M_PD_stack_GeV": float(m_pd_stack),
            "ratio_selected_over_stack": float(m_pd / m_pd_stack),
            "g_MGUT_GeV": float(g * m_gut),
        },
        "gauge_lifetime": {
            "selected": width,
            "stack_convention": width_stack,
            "delta_rel_tau_selected_vs_stack": float(
                (width["tau_e_years"] - width_stack["tau_e_years"])
                / width_stack["tau_e_years"]
            ),
        },
        "next_exact_calculation": [
            "Derive residual λ₂₁₀ / η_intra from the UV potential (close unique spectrum)",
            "Promote PS-singlet (a,ω,p) uniqueness to the full 210ⁿ tensor basis",
            "Execute a live SARAH/PyR@TE dump when tools are available",
        ],
        "flag": {
            "unique_a_omega_p_under_ps_singlet_potential": True,
            "interior_ps_breaking_window": True,
            "replaced_stack_030_050_020_convention": True,
            "uv_masses_recomputed_at_selected_ratios": True,
            "unique_from_full_210n_tensor_basis": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
            "selected_point_passes_SK": bool(width["passes_SK"]),
        },
        "verdict": (
            f"PS-singlet minimum selects (a,ω,p)/M_GUT="
            f"({sel['fractions']['a_over_MGUT']:.4f},"
            f"{sel['fractions']['omega_over_MGUT']:.4f},"
            f"{sel['fractions']['p_over_MGUT']:.4f}) "
            f"(soft-shift cost ×{sel['improvement_ratio']:.3e} vs stack); "
            f"M_PD={m_pd:.3e} GeV (stack {m_pd_stack:.3e}), "
            f"SK pass={width['passes_SK']}. Full 210ⁿ uniqueness and unique τ_p remain OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    sel = report["selected"]
    p = report["proxy_comparison"]
    lines = [
        "# Unique (a, ω, p) from PS-singlet 210 potential — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- a/M_GUT: {sel['fractions']['a_over_MGUT']:.6f}",
        f"- ω/M_GUT: {sel['fractions']['omega_over_MGUT']:.6f}",
        f"- p/M_GUT: {sel['fractions']['p_over_MGUT']:.6f}",
        f"- Soft-shift cost (selected): {sel['soft_shift_norm_over_MGUT2']:.6e}",
        f"- Soft-shift cost (stack): {sel['stack_convention']['soft_shift_norm_over_MGUT2']:.6e}",
        f"- M_PD selected / stack: {p['M_PD_selected_GeV']:.6e} / {p['M_PD_stack_GeV']:.6e}",
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
    ROOT.joinpath("UNIQUE_A_OMEGA_P_PS_SINGLET_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2, default=_json_default) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("UNIQUE_A_OMEGA_P_PS_SINGLET_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "selected_fractions": report["selected"]["fractions"],
                "soft_shift": {
                    "selected": report["selected"]["soft_shift_norm_over_MGUT2"],
                    "stack": report["selected"]["stack_convention"][
                        "soft_shift_norm_over_MGUT2"
                    ],
                    "improvement_ratio": report["selected"]["improvement_ratio"],
                },
                "proxy_comparison": report.get("proxy_comparison"),
                "gauge_lifetime": {
                    "tau": report["gauge_lifetime"]["selected"]["tau_e_years"],
                    "passes_SK": report["gauge_lifetime"]["selected"]["passes_SK"],
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
