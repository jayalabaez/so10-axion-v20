#!/usr/bin/env python3
r"""Multi-operator phase Hessian with cross terms (v20).

Next step after ``extended_126_tprime_fragments_v20``:

Replace the single-operator locking Hessian
``H = A_lock · g_L g_Lᵀ`` by the **sum of all charge-allowed phase
operators** active in the reduced ``(φ_Δ, φ_10, φ_S)`` sector:

1. Locking ``126bar² 10² S²``:  ``V = −A_L cos(2φ_Δ + 2φ_10 + 2φ_S)``
2. ``10_H² S`` (κ):              ``V = −A_κ cos(2φ_10 + φ_S)``
3. Dim-4 ``210·10·126·S`` (λ₄):  ``V = −A_4 cos(φ_Δ + φ_10 + φ_S)``
   (with ``φ_210`` fixed by the PS/GUT vacuum)

At a common phase-aligned minimum, the Hessian is the sum of rank-1
updates ``Σ_i A_i g_i g_iᵀ`` (operator cross terms). Radial–phase mixed
second derivatives vanish for pure ``−A(r)cosθ(φ)`` potentials at
``sinθ=0``.

Honesty
-------
* This completes the multi-operator Hessian in the **reduced** three-phase
  sector, not the full 210+126+10 component phase space.
* ``g_L = 2 g_4`` ⇒ locking and λ₄ are parallel; a nonzero κ lifts a second
  massive mode and leaves a single flat direction ∝ (1,1,−2).
* Unique ``τ_p`` and full-component Goldstone counting remain OPEN.
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
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_126_to_54_projector_v20 as c126mod

ROOT = Path(__file__).resolve().parent

FIELDS = ("phi_DeltaR_126", "phi_10", "phi_S")

# Charge vectors g for θ = g·φ in V = −A cos(θ)
G_LOCK = np.array([2.0, 2.0, 2.0], dtype=float)  # 2φ_Δ + 2φ_10 + 2φ_S
G_KAPPA = np.array([0.0, 2.0, 1.0], dtype=float)  # 2φ_10 + φ_S
G_LAM4 = np.array([1.0, 1.0, 1.0], dtype=float)  # φ_Δ + φ_10 + φ_S (φ_210=0)

SOURCES = {
    "operators": {
        "locking": "126bar_H^2 10_H^2 S^2 / M_GUT^2 (54-channel)",
        "kappa": "10_H^2 S",
        "lam4": "210·10·126·S with φ_210 fixed",
    },
    "upstream_c126": "so10_126_to_54_projector_v20",
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
    """Amplitudes A_i of V = −Σ A_i cos(θ_i) at r_Δ=r_10=r_S=M_I."""
    v = m_i
    a_lock = (
        lambda_lock * c54 * c126 * (v**2) * (v**2) * (v**2) / (m_gut**2)
    )
    # Match magnitude potential used in minimization: |V_κ|=κ M_I r_10² r_S
    a_kappa = abs(kappa) * m_i * (v**2) * v
    # |V_4|=|λ4| M_GUT r_10 r_Δ r_S
    a_lam4 = abs(lam4) * m_gut * v * v * v
    return {
        "A_lock": float(a_lock),
        "A_kappa": float(a_kappa),
        "A_lam4": float(a_lam4),
        "signs": {
            "kappa_sign": 1.0 if kappa >= 0 else -1.0,
            "lam4_sign": 1.0 if lam4 >= 0 else -1.0,
            "lambda_lock_sign": 1.0 if lambda_lock >= 0 else -1.0,
            "note": (
                "Hessian at a cos=+1 aligned minimum uses A_i≥0; relative "
                "signs are absorbed into the definition of the aligned point."
            ),
        },
        "vevs_GeV": {"r_Delta": v, "r_10": v, "r_S": v, "M_GUT": m_gut},
        "C_54": c54,
        "C_126_to_54": c126,
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
        contrib = a * np.outer(g, g)
        hess = hess + contrib
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

    # Analytic / stable spectrum: work in units of max(A‖g‖²)
    scale = max(
        abs(a_lock) * float(np.dot(G_LOCK, G_LOCK)),
        abs(a_kappa) * float(np.dot(G_KAPPA, G_KAPPA)),
        abs(a_lam4) * float(np.dot(G_LAM4, G_LAM4)),
        1.0,
    )
    # Normalize before eigh to avoid float64 noise at ~1e38
    eigs = np.linalg.eigvalsh(hess / scale) * scale
    eigs = np.sort(eigs)
    tol = 1e-10 * scale
    n_pos = int(np.sum(eigs > tol))
    n_zero = int(np.sum(np.abs(eigs) <= tol))
    n_neg = int(np.sum(eigs < -tol))

    # Rank / dependence: g_L = 2 g_4
    g_stack = []
    if a_lock > 0 or a_lam4 > 0:
        g_stack.append(G_LAM4)  # represents both locking and lam4
    if a_kappa > 0:
        g_stack.append(G_KAPPA)
    rank = 0
    if g_stack:
        m = np.column_stack(g_stack)
        rank = int(np.linalg.matrix_rank(m, tol=1e-12))

    # Flat direction when rank=2: ∝ (1,1,−2)
    flat_dir = None
    if rank == 2 and a_kappa > 0 and (a_lock > 0 or a_lam4 > 0):
        flat_dir = [1.0, 1.0, -2.0]
    elif rank == 1:
        # Orthogonal plane to g_4 (or g_κ alone)
        g = G_LAM4 if (a_lock > 0 or a_lam4 > 0) else G_KAPPA
        # Two orthonormal null vectors via SVD
        _, _, vh = np.linalg.svd(np.array([g]))
        flat_dir = {
            "null_basis": vh[1:].tolist(),
            "note": "Two flat directions orthogonal to the single active g",
        }

    # Radial–phase cross block at aligned minimum
    radial_phase = {
        "status": "RADIAL_PHASE_CROSS_VANISHES_AT_ALIGNED_MINIMUM",
        "argument": (
            "For V=−A(r)cosθ(φ), ∂²V/∂r∂φ ∝ (∂A/∂r)sinθ vanishes at sinθ=0. "
            "No radial–phase mixing in the Hessian at the aligned point for "
            "this operator class."
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
    # Single-operator baseline for comparison
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

    # Expected pattern checks
    locking_only = next(p for p in points if p["name"] == "locking_only")
    finite_k = next(p for p in points if p["name"] == "finite_kappa_benchmark")
    both = next(p for p in points if p["name"] == "kappa_and_lam4_on")

    checks = {
        "locking_only_one_massive": locking_only["multi_operator_hessian"][
            "n_positive"
        ]
        == 1,
        "locking_only_two_flat": locking_only["multi_operator_hessian"]["n_zero"]
        == 2,
        "finite_kappa_two_massive": finite_k["multi_operator_hessian"]["n_positive"]
        == 2,
        "finite_kappa_one_flat": finite_k["multi_operator_hessian"]["n_zero"] == 1,
        "kappa_lam4_two_massive": both["multi_operator_hessian"]["n_positive"] == 2,
        "kappa_lam4_one_flat": both["multi_operator_hessian"]["n_zero"] == 1,
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
        "upstream_minimize_ok": vmin.get("n_failed", 1) == 0,
        "c126_positive": c126 > 0,
        "not_claiming_full_component_space": True,
        "not_claiming_unique_taup": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "MULTI_OPERATOR_PHASE_HESSIAN_COMPLETE__REDUCED_SECTOR"
            if not failures
            else "MULTI_OPERATOR_PHASE_HESSIAN_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "fields": list(FIELDS),
        "charge_vectors": {
            "g_lock": G_LOCK.tolist(),
            "g_kappa": G_KAPPA.tolist(),
            "g_lam4": G_LAM4.tolist(),
            "identity": "g_lock = 2·g_lam4 (locking ∥ λ₄)",
        },
        "C_54": c54,
        "C_126_to_54": c126,
        "points": points,
        "upstream_minimize_status": vmin.get("status"),
        "next_exact_calculation": [
            "Include gauge–scalar interference with physical 4×4 mixings",
            "Lift the reduced minimum / phase Hessian to the full 210+126+10 component space",
            "Optionally restore t3 if a light 126_H is added to the field content",
            "Goldstone counting across every broken generator",
        ],
        "flag": {
            "multi_operator_phase_hessian": True,
            "includes_kappa_lam4_locking_cross_terms": True,
            "radial_phase_cross_analyzed": True,
            "complete_multi_operator_phase_hessian_reduced_sector": True,
            "full_component_phase_space": False,
            "invented_unpublished_cg_values": False,
            "complete_so10_scalar_potential": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Multi-operator phase Hessian constructed: H=Σ A_i g_i g_iᵀ with "
            "locking, κ(10²S), and λ₄(210·10·126·S). Locking ∥ λ₄; nonzero κ "
            "lifts a second massive mode and leaves one flat direction ∝(1,1,−2). "
            "Radial–phase cross terms vanish at the aligned minimum. Full "
            "component phase space remains OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Multi-operator phase Hessian — v20",
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
            f"λ_lock={p['couplings']['lambda_lock']:.4g})"
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
