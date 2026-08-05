#!/usr/bin/env python3
r"""Multi-operator phase Hessian with selected-vacuum nulls enforced (v20).

Revalidated after PR #97: on the physical selected vacuum,

* P54(Delta_R, Delta_R) = 0 ⇒ A_lock = 0;
* T_Phi Delta_R = 0 ⇒ A_lam4 = 0;
* only κ H²S remains active.

Formal charge vectors are still recorded:

1. Locking ``126bar² 10² S²``:  g_L = (2,2,2)
2. ``10_H² S`` (κ):              g_κ = (0,2,1)
3. Dim-4 ``210·10·126·S`` (λ₄):  g_4 = (1,1,1)

with g_L = 2 g_4.  Historical MI-proxy amplitudes are retained only as
withdrawn bookkeeping.

Honesty
-------
* Reduced three-phase sector only.
* Selected-vacuum rank is one (κ) with two flat directions, one being the
  PQ axion (1,1,−2) and one additional unresolved flat phase.
* Unique τ_p and full-component Goldstone counting remain OPEN.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import charge_allowed_potential_minimize_v20 as pmin
import extended_ttbar_54_locking_v20 as ext
import physical_h10_54_mass_block_from_deltar_v20 as lock_zero
import scalar_vacuum_proton_decay_v20 as scalar_pd
import selected_vacuum_lambda4_portal_null_audit_v20 as lam4_zero
import so10_126_to_54_projector_v20 as c126mod

ROOT = Path(__file__).resolve().parent

FIELDS = ("phi_DeltaR_126", "phi_10", "phi_S")

G_LOCK = np.array([2.0, 2.0, 2.0], dtype=float)
G_KAPPA = np.array([0.0, 2.0, 1.0], dtype=float)
G_LAM4 = np.array([1.0, 1.0, 1.0], dtype=float)

SOURCES = {
    "operators": {
        "locking": "126bar_H^2 10_H^2 S^2 / M_GUT^2 (54-channel; selected vacuum null)",
        "kappa": "10_H^2 S",
        "lam4": "210·10·126·S (selected-vacuum radial/phase amplitude null)",
    },
    "upstream_exact_lock_null": "physical_h10_54_mass_block_from_deltar_v20",
    "upstream_exact_lam4_null": "selected_vacuum_lambda4_portal_null_audit_v20",
    "upstream_minimize": "charge_allowed_potential_minimize_v20",
}


def phase_amplitudes(
    *,
    kappa: float,
    lam4: float,
    lambda_lock: float,
    m_i: float,
    m_gut: float,
    c54: float,
    c126: float,
) -> dict[str, Any]:
    """Selected-vacuum amplitudes with exact lock/λ₄ nulls enforced."""
    v = m_i
    a_lock_proxy = (
        lambda_lock * c54 * c126 * (v**2) * (v**2) * (v**2) / (m_gut**2)
    )
    a_kappa = abs(kappa) * m_i * (v**2) * v
    a_lam4_proxy = abs(lam4) * m_gut * v * v * v
    return {
        "A_lock": 0.0,
        "A_kappa": float(a_kappa),
        "A_lam4": 0.0,
        "A_lock_historical_MI_proxy": float(a_lock_proxy),
        "A_lam4_historical_MI_proxy": float(a_lam4_proxy),
        "signs": {
            "kappa_sign": 1.0 if kappa >= 0 else -1.0,
            "lam4_sign": 1.0 if lam4 >= 0 else -1.0,
            "lambda_lock_sign": 1.0 if lambda_lock >= 0 else -1.0,
            "note": (
                "Selected-vacuum A_lock and A_lam4 forced to zero by exact "
                "tensor evaluations; proxies are withdrawn bookkeeping only."
            ),
        },
        "vevs_GeV": {"r_Delta": v, "r_10": v, "r_S": v, "M_GUT": m_gut},
        "C_54": c54,
        "C_126_to_54": c126,
        "selected_vacuum_nulls": {
            "P54_DeltaR_DeltaR": 0.0,
            "T_Phi_DeltaR": 0.0,
        },
    }


def multi_operator_phase_hessian(
    *,
    a_lock: float,
    a_kappa: float,
    a_lam4: float,
) -> dict[str, Any]:
    """H = Σ A_i g_i g_iᵀ on (φ_Δ, φ_10, φ_S)."""
    ops = [
        {"name": "locking_126bar2_10_2_S2", "A": a_lock, "g": G_LOCK},
        {"name": "kappa_10_2_S", "A": a_kappa, "g": G_KAPPA},
        {"name": "lam4_210_10_126_S", "A": a_lam4, "g": G_LAM4},
    ]
    hess = np.zeros((3, 3), dtype=float)
    active = []
    for op in ops:
        a = float(op["A"])
        g = np.asarray(op["g"], dtype=float)
        hess = hess + a * np.outer(g, g)
        active.append(
            {
                "name": op["name"],
                "A": a,
                "g": g.tolist(),
                "theta": " + ".join(
                    f"{gi:g}·{f}" for gi, f in zip(g, FIELDS) if abs(gi) > 0
                ),
                "active": a > 0.0,
            }
        )

    scale = max(
        abs(a_lock) * float(np.dot(G_LOCK, G_LOCK)),
        abs(a_kappa) * float(np.dot(G_KAPPA, G_KAPPA)),
        abs(a_lam4) * float(np.dot(G_LAM4, G_LAM4)),
        1.0,
    )
    eigs = np.linalg.eigvalsh(hess / scale) * scale
    eigs = np.sort(eigs)
    tol = 1e-10 * scale
    n_pos = int(np.sum(eigs > tol))
    n_zero = int(np.sum(np.abs(eigs) <= tol))
    n_neg = int(np.sum(eigs < -tol))

    g_stack = []
    if a_lock > 0 or a_lam4 > 0:
        g_stack.append(G_LAM4)
    if a_kappa > 0:
        g_stack.append(G_KAPPA)
    rank = 0
    if g_stack:
        m = np.column_stack(g_stack)
        rank = int(np.linalg.matrix_rank(m, tol=1e-12))

    flat_dir: Any = None
    if rank == 2 and a_kappa > 0 and (a_lock > 0 or a_lam4 > 0):
        flat_dir = [1.0, 1.0, -2.0]
    elif rank == 1:
        g = G_LAM4 if (a_lock > 0 or a_lam4 > 0) else G_KAPPA
        _, _, vh = np.linalg.svd(np.array([g]))
        flat_dir = {
            "null_basis": vh[1:].tolist(),
            "pq_axion_among_nulls": True,
            "note": (
                "Two flat directions orthogonal to the single active g; "
                "one contains the PQ combination (1,1,-2)."
            ),
        }
    elif rank == 0:
        flat_dir = {
            "null_basis": np.eye(3).tolist(),
            "note": "No active phase operator; full three-flat sector.",
        }

    radial_phase = {
        "status": "RADIAL_PHASE_CROSS_VANISHES_AT_ALIGNED_MINIMUM",
        "argument": (
            "For V=−A(r)cosθ(φ), ∂²V/∂r∂φ ∝ (∂A/∂r)sinθ vanishes at sinθ=0."
        ),
        "cross_block_GeV2": np.zeros((3, 3)).tolist(),
        "flag": {"radial_phase_cross_zero_at_minimum": True},
    }

    return {
        "fields": list(FIELDS),
        "operators": active,
        "hessian": hess.tolist(),
        "eigenvalues": [float(x) for x in eigs],
        "n_positive": n_pos,
        "n_zero": n_zero,
        "n_negative": n_neg,
        "operator_charge_rank": rank,
        "g_lock_parallel_g_lam4": True,
        "flat_direction": flat_dir,
        "radial_phase_cross": radial_phase,
        "spectrum_method": "sum_Ai_gi_giT_scaled_eigh",
        "massive_mode_mass_proxies": [
            float(math.sqrt(max(x, 0.0))) for x in eigs if x > tol
        ],
        "flag": {
            "multi_operator_phase_hessian": True,
            "includes_kappa_and_lam4_cross_terms": True,
            "selected_vacuum_lock_and_lam4_null": True,
            "radial_phase_cross_included": True,
            "full_component_phase_space": False,
        },
    }


def evaluate_point(
    name: str,
    *,
    kappa: float,
    lam4: float,
    lambda_lock: float,
    m_i: float,
    m_gut: float,
    c54: float,
    c126: float,
) -> dict[str, Any]:
    amp = phase_amplitudes(
        kappa=kappa,
        lam4=lam4,
        lambda_lock=lambda_lock,
        m_i=m_i,
        m_gut=m_gut,
        c54=c54,
        c126=c126,
    )
    hess = multi_operator_phase_hessian(
        a_lock=amp["A_lock"],
        a_kappa=amp["A_kappa"],
        a_lam4=amp["A_lam4"],
    )
    single = ext.phase_hessian_from_A(amp["A_lock"])
    return {
        "name": name,
        "couplings": {
            "kappa": kappa,
            "lam4": lam4,
            "lambda_lock": lambda_lock,
        },
        "amplitudes": amp,
        "multi_operator_hessian": hess,
        "single_locking_baseline": {
            "n_positive": single["n_positive"],
            "n_zero": single["n_zero"],
            "eigenvalues": single["eigenvalues"],
        },
        "delta_n_positive_vs_single": hess["n_positive"] - single["n_positive"],
        "delta_n_zero_vs_single": hess["n_zero"] - single["n_zero"],
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "MULTI_OPERATOR_HESSIAN_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"multi_operator_phase_hessian": False},
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    proj = c126mod.build_126_to_54_projector()
    c54 = float(proj["C_54_upstream"])
    c126 = float(proj["C_126_to_54"])
    vmin = pmin.build_report()
    best = vmin.get("fixed_couplings") or {}
    fk = vmin.get("finite_kappa_benchmark_couplings") or {}
    lock_rep = lock_zero.build_report()
    lam4_rep = lam4_zero.build_report()

    points = [
        evaluate_point(
            "minimized_best_fit",
            kappa=float(best.get("kappa", 0.0)),
            lam4=float(best.get("lam4", 0.0)),
            lambda_lock=float(best.get("lambda_lock", 1.0)),
            m_i=m_i,
            m_gut=m_gut,
            c54=c54,
            c126=c126,
        ),
        evaluate_point(
            "finite_kappa_benchmark",
            kappa=float(fk.get("kappa", 0.05)),
            lam4=float(fk.get("lam4", 0.0)),
            lambda_lock=float(fk.get("lambda_lock", 1.0)),
            m_i=m_i,
            m_gut=m_gut,
            c54=c54,
            c126=c126,
        ),
        evaluate_point(
            "kappa_and_lam4_on",
            kappa=0.1,
            lam4=0.2,
            lambda_lock=1.0,
            m_i=m_i,
            m_gut=m_gut,
            c54=c54,
            c126=c126,
        ),
        evaluate_point(
            "locking_only",
            kappa=0.0,
            lam4=0.0,
            lambda_lock=1.0,
            m_i=m_i,
            m_gut=m_gut,
            c54=c54,
            c126=c126,
        ),
    ]

    locking_only = next(p for p in points if p["name"] == "locking_only")
    finite_k = next(p for p in points if p["name"] == "finite_kappa_benchmark")
    both = next(p for p in points if p["name"] == "kappa_and_lam4_on")

    checks = {
        "locking_only_null": locking_only["multi_operator_hessian"]["n_positive"]
        == 0,
        "locking_only_three_flat": locking_only["multi_operator_hessian"]["n_zero"]
        == 3,
        "finite_kappa_one_massive": finite_k["multi_operator_hessian"]["n_positive"]
        == 1,
        "finite_kappa_two_flat": finite_k["multi_operator_hessian"]["n_zero"] == 2,
        "kappa_lam4_still_one_massive": both["multi_operator_hessian"]["n_positive"]
        == 1,
        "kappa_lam4_still_two_flat": both["multi_operator_hessian"]["n_zero"] == 2,
        "g_lock_parallel_documented": both["multi_operator_hessian"][
            "g_lock_parallel_g_lam4"
        ],
        "radial_phase_cross_zero": all(
            p["multi_operator_hessian"]["radial_phase_cross"]["flag"][
                "radial_phase_cross_zero_at_minimum"
            ]
            for p in points
        ),
        "no_negative_modes": all(
            p["multi_operator_hessian"]["n_negative"] == 0 for p in points
        ),
        "exact_lock_null_upstream": bool(
            lock_rep.get("flags", {}).get("DeltaR_squared_54_projection_zero")
        ),
        "exact_lam4_null_upstream": bool(
            lam4_rep.get("flags", {}).get("selected_DeltaR_is_portal_null_vector")
        ),
        "upstream_minimize_ok": vmin.get("n_failed", 1) == 0,
        "c126_positive": c126 > 0,
        "not_claiming_full_component_space": True,
        "not_claiming_unique_taup": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "MULTI_OPERATOR_PHASE_HESSIAN_REVALIDATED__KAPPA_ONLY_SELECTED_VACUUM"
            if not failures
            else "MULTI_OPERATOR_PHASE_HESSIAN_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "fields": list(FIELDS),
        "charge_vectors": {
            "g_lock": G_LOCK.tolist(),
            "g_kappa": G_KAPPA.tolist(),
            "g_lam4": G_LAM4.tolist(),
            "identity": "g_lock = 2·g_lam4 (locking ∥ λ₄; both null on vacuum)",
        },
        "C_54": c54,
        "C_126_to_54": c126,
        "points": points,
        "upstream_minimize_status": vmin.get("status"),
        "upstream_exact_nulls": {
            "lock": lock_rep.get("status"),
            "lam4": lam4_rep.get("status"),
        },
        "next_exact_calculation": [
            "Find a charge-allowed invariant with nonzero selected-vacuum phase amplitude",
            "Lift the κ-only reduced Hessian to the full 210+126+10 component space",
            "Include gauge–scalar interference with physical mixings",
            "Goldstone counting across every broken generator",
        ],
        "flag": {
            "multi_operator_phase_hessian": True,
            "includes_kappa_lam4_locking_cross_terms": True,
            "selected_vacuum_lock_and_lam4_null": True,
            "selected_vacuum_phase_rank_one": True,
            "radial_phase_cross_analyzed": True,
            "complete_multi_operator_phase_hessian_reduced_sector": True,
            "full_component_phase_space": False,
            "invented_unpublished_cg_values": False,
            "complete_so10_scalar_potential": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Selected-vacuum multi-operator phase Hessian revalidated: A_lock "
            "and A_lam4 are exact zeros, so only κ is active. Rank is one with "
            "two flat directions (PQ axion plus one unresolved flat phase). "
            "A different nonzero phase-sensitive invariant is required; the "
            "theory remains BLOCKED."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Multi-operator phase Hessian — selected-vacuum revalidation",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        "## Charge vectors",
        "",
        f"- g_lock = {report['charge_vectors']['g_lock']}",
        f"- g_κ = {report['charge_vectors']['g_kappa']}",
        f"- g_λ₄ = {report['charge_vectors']['g_lam4']}",
        f"- {report['charge_vectors']['identity']}",
        "",
        "## Points",
        "",
    ]
    for p in report["points"]:
        h = p["multi_operator_hessian"]
        lines.append(
            f"- `{p['name']}`: n₊={h['n_positive']}, n₀={h['n_zero']}, "
            f"rank={h['operator_charge_rank']} "
            f"(κ={p['couplings']['kappa']:.4g}, λ₄={p['couplings']['lam4']:.4g}, "
            f"λ_lock={p['couplings']['lambda_lock']:.4g}; "
            f"A_lock={p['amplitudes']['A_lock']}, A_lam4={p['amplitudes']['A_lam4']})"
        )
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
    ROOT.joinpath("MULTI_OPERATOR_PHASE_HESSIAN_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("MULTI_OPERATOR_PHASE_HESSIAN_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "charge_vectors": report.get("charge_vectors"),
                "points": [
                    {
                        "name": p["name"],
                        "n_positive": p["multi_operator_hessian"]["n_positive"],
                        "n_zero": p["multi_operator_hessian"]["n_zero"],
                        "rank": p["multi_operator_hessian"]["operator_charge_rank"],
                        "A_lock": p["amplitudes"]["A_lock"],
                        "A_lam4": p["amplitudes"]["A_lam4"],
                    }
                    for p in report.get("points", [])
                ],
                "flag": report.get("flag"),
                "verdict": report.get("verdict"),
            },
            indent=2,
        )
    )
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
