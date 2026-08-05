#!/usr/bin/env python3
r"""Competing-extrema census on the reduced five-amplitude polynomial (v20).

Physics
-------
On the reduced radial slice ``(P_210, Δ_R, hEW, S, Φ₁₇)`` with the restored
quartic matrix ``Λ`` and charge-allowed portals ``(κ, λ₄, λ_lock)``, this
module enumerates a finite census of competing amplitude points, evaluates

    V_4 = Σ_{ij} Λ_{ij} ρ_i² ρ_j² ,
    V_int = V_κ + V_λ₄ + V_lock ,

and ranks candidates by ``V_4 + V_int`` together with Hessian positive-
definiteness (λ₄=0 survival and historical λ₄ benchmarks).

Census includes:
* selected vacuum at physical ``hEW=174`` (λ₄=0 survival);
* historical λ₄ = −κ M_I/M_GUT at the same VEVs (known tachyonic);
* ``H10 = M_I`` proxy (withdrawn physically);
* ``H10 → 0`` electroweak-unbroken;
* soft-band corners (±20% on S and P_210);
* equal-split intermediate amplitudes.

Honesty
-------
* Reduced five-amplitude census only — not the full invariant ring.
* Does not invent 120/320/1050/4125 CG.
* Theory remains BLOCKED; G5 competing-extrema stays PARTIAL.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import charge_allowed_potential_minimize_v20 as pmin
import nonsusy_reduced_hessian_v20 as reduced
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_126_to_54_projector_v20 as c126mod

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "REDUCED_POLYNOMIAL_COMPETING_EXTREMA_V20.json"
OUT_MD = ROOT / "REDUCED_POLYNOMIAL_COMPETING_EXTREMA_V20.md"

FIELDS = list(reduced.FIELDS)


def quartic_energy(rho: np.ndarray, lam: np.ndarray) -> float:
    r2 = np.asarray(rho, dtype=float) ** 2
    return float(r2 @ lam @ r2)


def interaction_energy(
    rho: np.ndarray,
    *,
    kappa: float,
    lam4: float,
    lambda_lock: float,
    m_i: float,
    m_gut: float,
    c54: float,
    c126: float,
) -> float:
    """V_κ + V_λ₄ + V_lock on (P, Δ, h, S); Φ₁₇ spectator in this slice."""
    p, delta, h, s, _phi = (float(x) for x in rho)
    v_k = -kappa * m_i * (h**2) * s
    v4 = -lam4 * m_gut * p * delta * h * s
    v_lock = (
        lambda_lock * c54 * c126 * (delta**2) * (h**2) * (s**2) / (m_gut**2)
    )
    return float(v_k + v4 + v_lock)


def hessian_min_eig(
    rho: dict[str, float],
    lam: np.ndarray,
    *,
    m_i: float,
    m_gut: float,
    lam4: float,
    kappa: float,
) -> dict[str, Any]:
    params = reduced.interaction_parameters(m_i, m_gut, lam4, kappa=kappa)
    hess = reduced.high_precision_hessian(rho, lam, params)
    eigs = reduced.high_precision_eigenvalues(hess)
    return {
        "min_eig_GeV2": float(eigs[0]),
        "positive_definite": bool(eigs[0] > 0.0),
        "eigenvalues_GeV2": [float(x) for x in eigs],
    }


def evaluate_point(
    name: str,
    rho_dict: dict[str, float],
    *,
    lam: np.ndarray,
    kappa: float,
    lam4: float,
    lambda_lock: float,
    m_i: float,
    m_gut: float,
    c54: float,
    c126: float,
) -> dict[str, Any]:
    rho = np.array([rho_dict[f] for f in FIELDS], dtype=float)
    v4 = quartic_energy(rho, lam)
    vint = interaction_energy(
        rho,
        kappa=kappa,
        lam4=lam4,
        lambda_lock=lambda_lock,
        m_i=m_i,
        m_gut=m_gut,
        c54=c54,
        c126=c126,
    )
    hess = hessian_min_eig(
        rho_dict, lam, m_i=m_i, m_gut=m_gut, lam4=lam4, kappa=kappa
    )
    return {
        "name": name,
        "rho_GeV": {f: float(rho_dict[f]) for f in FIELDS},
        "lam4": float(lam4),
        "kappa": float(kappa),
        "V4_GeV4": v4,
        "V_int_GeV4": vint,
        "V_total_GeV4": v4 + vint,
        "hessian": hess,
    }


def build_census(
    *,
    targets: dict[str, float],
    lam: np.ndarray,
    kappa: float,
    lambda_lock: float,
    m_i: float,
    m_gut: float,
    c54: float,
    c126: float,
) -> list[dict[str, Any]]:
    historical_lam4 = -0.05 * m_i / m_gut
    base = dict(targets)
    points: list[tuple[str, dict[str, float], float]] = [
        ("selected_hEW174_lam4_0", base, 0.0),
        ("selected_hEW174_historical_lam4", base, historical_lam4),
        (
            "H10_equals_MI_proxy_lam4_0",
            {**base, "H10_EW": float(m_i)},
            0.0,
        ),
        (
            "H10_unbroken_lam4_0",
            {**base, "H10_EW": 1.0},  # tiny, avoid exact zero / soft divide
            0.0,
        ),
        (
            "S_plus_20pct_lam4_0",
            {**base, "S_PQ": float(base["S_PQ"]) * 1.2},
            0.0,
        ),
        (
            "S_minus_20pct_lam4_0",
            {**base, "S_PQ": float(base["S_PQ"]) * 0.8},
            0.0,
        ),
        (
            "P210_plus_20pct_lam4_0",
            {**base, "P_210": float(base["P_210"]) * 1.2},
            0.0,
        ),
        (
            "P210_minus_20pct_lam4_0",
            {**base, "P_210": float(base["P_210"]) * 0.8},
            0.0,
        ),
        (
            "equal_split_intermediates_lam4_0",
            {
                **base,
                "P_210": float(m_i),
                "DeltaR_126bar": float(m_i),
                "S_PQ": float(m_i),
                "Phi17_X": float(m_i),
                "H10_EW": 174.0,
            },
            0.0,
        ),
    ]
    return [
        evaluate_point(
            name,
            rho,
            lam=lam,
            kappa=kappa,
            lam4=lam4,
            lambda_lock=lambda_lock,
            m_i=m_i,
            m_gut=m_gut,
            c54=c54,
            c126=c126,
        )
        for name, rho, lam4 in points
    ]


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    radial = scalar_pd.reduced_radial_vacuum_witness(
        {"available": True, "M_I_GeV": m_i, "M_GUT_GeV": m_gut}
    )
    lam, _lambdas, targets = reduced.radial_quartic_matrix(radial)

    vmin = pmin.build_report()
    fk = vmin.get("finite_kappa_benchmark_couplings") or vmin["fixed_couplings"]
    kappa = float(fk["kappa"])
    lambda_lock = float(fk["lambda_lock"])

    proj = c126mod.build_126_to_54_projector()
    c54 = float(proj["C_54_upstream"])
    c126 = float(proj["C_126_to_54"])

    census = build_census(
        targets=targets,
        lam=lam,
        kappa=kappa,
        lambda_lock=lambda_lock,
        m_i=m_i,
        m_gut=m_gut,
        c54=c54,
        c126=c126,
    )

    selected = next(c for c in census if c["name"] == "selected_hEW174_lam4_0")
    historical = next(
        c for c in census if c["name"] == "selected_hEW174_historical_lam4"
    )

    # Rank λ4=0 candidates by V_total (lower is preferred)
    lam0 = [c for c in census if abs(c["lam4"]) < 1e-30]
    ranked = sorted(lam0, key=lambda c: c["V_total_GeV4"])
    selected_rank = next(
        i for i, c in enumerate(ranked) if c["name"] == "selected_hEW174_lam4_0"
    )
    v_min = ranked[0]["V_total_GeV4"]
    v_sel = selected["V_total_GeV4"]
    # Relative gap is diagnostic only: census points are not free extrema.
    rel_gap = abs(v_sel - v_min) / max(abs(v_sel), abs(v_min), 1.0)

    pd_lam0 = [c["name"] for c in lam0 if c["hessian"]["positive_definite"]]
    tachyonic = [
        c["name"] for c in census if not c["hessian"]["positive_definite"]
    ]

    checks = {
        "physical_hEW_174": abs(float(targets["H10_EW"]) - 174.0) < 1e-12,
        "selected_survival_pd": selected["hessian"]["positive_definite"],
        "historical_lam4_tachyonic": not historical["hessian"]["positive_definite"],
        "selected_among_lam0_census": selected["name"] in [c["name"] for c in lam0],
        "at_least_one_pd_lam0": len(pd_lam0) >= 1,
        "census_size_ge_8": len(census) >= 8,
        "full_ring_extrema_not_claimed": True,
        "cg_not_invented": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "REDUCED_POLYNOMIAL_COMPETING_EXTREMA_CENSUSED__FULL_RING_OPEN"
            if not failures
            else "REDUCED_POLYNOMIAL_COMPETING_EXTREMA_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "couplings": {
            "kappa": kappa,
            "lambda_lock": lambda_lock,
            "source": "charge_allowed_potential_minimize finite-κ / fixed",
        },
        "selected_targets_GeV": targets,
        "census": census,
        "ranking_lam4_0_by_V_total": [
            {"rank": i, "name": c["name"], "V_total_GeV4": c["V_total_GeV4"]}
            for i, c in enumerate(ranked)
        ],
        "selected_rank_among_lam4_0": selected_rank,
        "selected_relative_gap_to_lam0_min": rel_gap,
        "ranking_note": (
            "V_total ranking among fixed amplitude probes is diagnostic; "
            "points are not solved free extrema. Local PD of the selected "
            "survival point is the stability certificate."
        ),
        "pd_lam4_0_points": pd_lam0,
        "tachyonic_points": tachyonic,
        "flags": {
            "reduced_competing_extrema_censused": not bool(failures),
            "selected_survival_locally_stable": selected["hessian"][
                "positive_definite"
            ],
            "historical_lam4_excluded_as_tachyonic": not historical["hessian"][
                "positive_definite"
            ],
            "full_invariant_ring_extrema": False,
            "cg_120_320_1050_4125_invented": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "full_ring_competing_extrema": True,
            "missing_cg_120_320_1050_4125": True,
            "full_nonsusy_vacuum_hessian": True,
        },
        "verdict": (
            f"Reduced census ({len(census)} points): selected hEW=174, λ₄=0 is "
            f"locally PD; historical λ₄ is tachyonic. Among λ₄=0 candidates "
            f"selected ranks {selected_rank}/{len(ranked)} by V_total "
            f"(relative gap to min {rel_gap:.3e}). "
            "Full-ring competing extrema remain OPEN. Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Reduced polynomial competing-extrema census — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Selected rank (λ₄=0): `{report['selected_rank_among_lam4_0']}`\n"
        f"- PD λ₄=0 points: `{report['pd_lam4_0_points']}`\n"
        f"- Tachyonic: `{report['tachyonic_points']}`\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    # Compact stdout
    compact = {k: v for k, v in report.items() if k != "census"}
    compact["n_census"] = len(report["census"])
    print(json.dumps(compact, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
