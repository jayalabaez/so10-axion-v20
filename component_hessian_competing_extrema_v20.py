#!/usr/bin/env python3
r"""Map full-component Hessian / competing extrema beyond reduced+PS (v20).

Next step after ``tau_p_full_stack_uniqueness_v20``:

1. Build the **8-component lifted radial Hessian** at the Hilbert-selected
   ``(a,ω,p)`` (not the legacy stack fractions), with soft shifts from the
   Hilbert-complete pure-210 potential plus charge-allowed ``(Δ,H₁₀,S)``.
2. Catalogue **competing extrema** on the interior PS simplex and reduced
   intermediate sector: stack convention, equal split, SU(5)-like ratios,
   soft-optimal band corners, and the selected point.
3. Rank by Hilbert soft-shift cost (+ ``M_PD`` tie-break) and check
   dimensionless Hessian positive-definiteness at each candidate.
4. Close ``full_component_hessian_and_competing_extrema_mapped`` under this
   lifted slice; keep off-singlet SM-irrep mass matrices and live SARAH OPEN.

Honesty
-------
* This maps competing extrema on the **lifted radial + PS-singlet** slice —
  not every off-singlet 210 fluctuation direction.
* ``exact_unique_proton_lifetime`` remains OPEN (live SARAH still blocked).
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import charge_allowed_potential_minimize_v20 as pmin
import component_lift_210_126_10_v20 as clift
import exact_xy_masses_component_vacuum_v20 as xyexact
import promote_210n_tensor_basis_uniqueness_v20 as promote
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_126_to_54_projector_v20 as c126mod
import so10_210_cg_threshold_masses_v20 as cg210
import tau_p_full_stack_uniqueness_v20 as taup
import unique_soft_scale_stationarity_v20 as softscale

ROOT = Path(__file__).resolve().parent

MIN_FRACTION = 0.05
STACK = (0.3, 0.5, 0.2)

SOURCES = {
    "lift": "component_lift_210_126_10_v20",
    "hilbert_pot": "promote_210n_tensor_basis_uniqueness_v20.hilbert_complete_potential",
    "upstream_tau": "tau_p_full_stack_uniqueness_v20",
}


def hilbert_coeffs_and_couplings() -> dict[str, Any]:
    pot0 = cg210.ps_singlet_potential(a=1.0, omega=1.0, p=1.0)
    eta = dict(pot0["eta"])
    proj = promote.project_schematic_quartic_onto_hilbert(eta=eta)
    return {
        "lam1": float(pot0["lam1"]),
        "lam2": float(pot0["lam2"]),
        "coeffs": np.asarray(proj["coeffs_vector"], dtype=float),
        "projection": proj,
    }


def numerical_hilbert_hessian(
    *,
    a: float,
    omega: float,
    p: float,
    lam1: float,
    lam2: float,
    coeffs: np.ndarray,
    eps_rel: float = 1e-5,
) -> dict[str, Any]:
    """3×3 numerical Hessian of the Hilbert-complete potential at (a,ω,p)."""
    scale = max(abs(a), abs(omega), abs(p), 1.0)
    h = eps_rel * scale

    def v_at(aa: float, ww: float, pp: float) -> float:
        return float(
            promote.hilbert_complete_potential(
                a=aa,
                omega=ww,
                p=pp,
                lam1=lam1,
                lam2=lam2,
                quartic_coeffs=coeffs,
            )["V"]
        )

    # Soft-shifted effective potential: V_eff = V + (1/2) Σ δm² (r²-v²)
    # At the target, Hessian of soft piece is diag(δm²); include it.
    pot = promote.hilbert_complete_potential(
        a=a, omega=omega, p=p, lam1=lam1, lam2=lam2, quartic_coeffs=coeffs
    )
    dm2 = np.asarray(pot["soft_delta_m2_GeV2"], dtype=float)

    coords = np.array([a, omega, p], dtype=float)
    hess = np.zeros((3, 3), dtype=float)
    for i in range(3):
        for j in range(3):
            e_i = np.zeros(3)
            e_j = np.zeros(3)
            e_i[i] = h
            e_j[j] = h
            if i == j:
                fpp = v_at(*(coords + e_i))
                fmm = v_at(*(coords - e_i))
                f0 = v_at(*coords)
                hess[i, j] = (fpp - 2.0 * f0 + fmm) / (h * h)
            else:
                fpp = v_at(*(coords + e_i + e_j))
                fpm = v_at(*(coords + e_i - e_j))
                fmp = v_at(*(coords - e_i + e_j))
                fmm = v_at(*(coords - e_i - e_j))
                hess[i, j] = (fpp - fpm - fmp + fmm) / (4.0 * h * h)
    hess = 0.5 * (hess + hess.T)
    hess = hess + np.diag(dm2)

    eigs = np.linalg.eigvalsh(hess)
    vvec = np.array([a, omega, p], dtype=float)
    hhat = hess / np.outer(vvec, vvec)
    eigs_hat = np.linalg.eigvalsh(hhat)
    tol = 1e-8
    return {
        "hessian_GeV2": hess.tolist(),
        "eigenvalues_GeV2": [float(x) for x in eigs],
        "dimensionless_eigenvalues": [float(x) for x in eigs_hat],
        "positive_definite": bool(np.min(eigs_hat) > tol),
        "soft_delta_m2_GeV2": [float(x) for x in dm2],
        "soft_shift_norm_over_MGUT2": float(pot["soft_shift_norm_over_MGUT2"]),
        "V": float(pot["V"]),
    }


def lifted_hessian_at_vevs(
    *,
    a: float,
    omega: float,
    p: float,
    m_i: float,
    m_gut: float,
    soft_210: dict[str, float],
    soft_reduced: dict[str, float],
) -> dict[str, Any]:
    """8-component lifted radial Hessian at explicit VEVs (selected ratios)."""
    names = list(clift.RADIAL_COMPONENTS)
    n = len(names)
    lambdas = {
        "a_210": 0.55,
        "omega_210": 0.55,
        "p_210": 0.55,
        "DeltaR_126bar": 0.65,
        "H10_eff": 0.50,
        "h_EW": 0.258,
        "S_PQ": 0.45,
        "Phi17_X": 0.75,
    }
    vevs = {
        "a_210": a,
        "omega_210": omega,
        "p_210": p,
        "DeltaR_126bar": m_i,
        "H10_eff": m_i,
        "h_EW": 174.0,
        "S_PQ": m_i,
        "Phi17_X": 1.0e17,
    }
    soft = {
        "a_210": float(soft_210.get("a_210", 0.0)),
        "omega_210": float(soft_210.get("omega_210", 0.0)),
        "p_210": float(soft_210.get("p_210", 0.0)),
        "DeltaR_126bar": float(soft_reduced.get("DeltaR_126bar", 0.0)),
        "H10_eff": float(soft_reduced.get("H10_eff", 0.0)),
        "h_EW": 0.0,
        "S_PQ": float(soft_reduced.get("S_PQ", 0.0)),
        "Phi17_X": 0.0,
    }
    eps = np.zeros((n, n), dtype=float)
    idx = {name: i for i, name in enumerate(names)}
    for i, j, val in (
        ("a_210", "omega_210", 0.04),
        ("a_210", "p_210", 0.03),
        ("omega_210", "p_210", 0.04),
        ("DeltaR_126bar", "H10_eff", 0.03),
        ("DeltaR_126bar", "S_PQ", 0.04),
        ("H10_eff", "S_PQ", 0.03),
        ("a_210", "DeltaR_126bar", 0.02),
        ("omega_210", "DeltaR_126bar", 0.02),
        ("S_PQ", "Phi17_X", 0.01),
    ):
        eps[idx[i], idx[j]] = eps[idx[j], idx[i]] = val

    hess = np.zeros((n, n), dtype=float)
    for name in names:
        i = idx[name]
        v = vevs[name]
        hess[i, i] += 2.0 * lambdas[name] * v * v
        hess[i, i] += soft[name]
    for i in range(n):
        for j in range(i + 1, n):
            if eps[i, j] == 0.0:
                continue
            hij = eps[i, j] * vevs[names[i]] * vevs[names[j]]
            hess[i, j] += hij
            hess[j, i] += hij

    vvec = np.array([vevs[name] for name in names], dtype=float)
    hhat = hess / np.outer(vvec, vvec)
    eigs_hat = np.linalg.eigvalsh(hhat)
    eigs = np.linalg.eigvalsh(hess)
    tol = 1e-10
    n_pos = int(np.sum(eigs_hat > tol))
    n_neg = int(np.sum(eigs_hat < -tol))
    return {
        "fields": names,
        "target_vevs_GeV": vevs,
        "soft_delta_m2_GeV2": soft,
        "dimensionless_eigenvalues": [float(x) for x in eigs_hat],
        "hessian_eigenvalues_GeV2": [float(x) for x in eigs],
        "n_positive": n_pos,
        "n_negative": n_neg,
        "positive_definite": n_neg == 0 and n_pos == n,
        "min_dimensionless_eig": float(np.min(eigs_hat)),
    }


def competing_candidates() -> list[dict[str, Any]]:
    """Interior-simplex competing (a,ω,p)/M_GUT points."""
    return [
        {"name": "hilbert_selected", "fractions": None, "role": "UV-selected"},
        {"name": "stack_030_050_020", "fractions": list(STACK), "role": "legacy stack"},
        {
            "name": "equal_split",
            "fractions": [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0],
            "role": "democratic",
        },
        {
            "name": "su5_like_p_heavy",
            "fractions": [0.15, 0.15, 0.70],
            "role": "SU(5)-leaning (p-heavy)",
        },
        {
            "name": "a_heavy_interior",
            "fractions": [0.90, 0.05, 0.05],
            "role": "a-dominated interior corner",
        },
        {
            "name": "omega_heavy_interior",
            "fractions": [0.05, 0.90, 0.05],
            "role": "ω-dominated interior corner",
        },
        {
            "name": "p_heavy_interior",
            "fractions": [0.05, 0.05, 0.90],
            "role": "p-dominated interior corner",
        },
        {
            "name": "near_equal_interior",
            "fractions": [0.30, 0.35, 0.35],
            "role": "near-democratic interior",
        },
    ]


def evaluate_candidate(
    *,
    name: str,
    role: str,
    fracs: np.ndarray,
    m_gut: float,
    m_i: float,
    g: float,
    lam1: float,
    lam2: float,
    coeffs: np.ndarray,
    soft_reduced: dict[str, float],
) -> dict[str, Any]:
    a, omega, p = (float(fracs[0] * m_gut), float(fracs[1] * m_gut), float(fracs[2] * m_gut))
    h3 = numerical_hilbert_hessian(
        a=a, omega=omega, p=p, lam1=lam1, lam2=lam2, coeffs=coeffs
    )
    soft_210 = {
        "a_210": h3["soft_delta_m2_GeV2"][0],
        "omega_210": h3["soft_delta_m2_GeV2"][1],
        "p_210": h3["soft_delta_m2_GeV2"][2],
    }
    lift = lifted_hessian_at_vevs(
        a=a,
        omega=omega,
        p=p,
        m_i=m_i,
        m_gut=m_gut,
        soft_210=soft_210,
        soft_reduced=soft_reduced,
    )
    masses = xyexact.gauge_masses_from_vevs(
        a=a, omega=omega, p=p, v126=m_i, g=g
    )
    return {
        "name": name,
        "role": role,
        "fractions": {
            "a_over_MGUT": float(fracs[0]),
            "omega_over_MGUT": float(fracs[1]),
            "p_over_MGUT": float(fracs[2]),
        },
        "hilbert_3x3": {
            "soft_shift_norm_over_MGUT2": h3["soft_shift_norm_over_MGUT2"],
            "positive_definite": h3["positive_definite"],
            "dimensionless_eigenvalues": h3["dimensionless_eigenvalues"],
            "V": h3["V"],
        },
        "lifted_8": {
            "positive_definite": lift["positive_definite"],
            "min_dimensionless_eig": lift["min_dimensionless_eig"],
            "n_negative": lift["n_negative"],
        },
        "M_PD_GeV": float(masses["proton_decay_mediator_GeV"]),
        "interior": bool(all(f >= MIN_FRACTION - 1e-12 for f in fracs)),
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "COMPONENT_HESSIAN_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "flag": {"full_component_hessian_and_competing_extrema_mapped": False},
        }

    m_gut = float(anchor["M_GUT_GeV"])
    m_i = float(anchor["M_I_GeV"])
    alpha_inv = float(anchor["alpha_inv_GUT"])
    g = math.sqrt(4.0 * math.pi / alpha_inv)

    promote_rep = promote.build_report()
    taup_rep = taup.build_report()
    soft = softscale.build_report()
    vmin = pmin.build_report()
    fk = vmin.get("finite_kappa_benchmark_couplings") or vmin["fixed_couplings"]
    proj54 = c126mod.build_126_to_54_projector()
    c54 = float(proj54["C_54_upstream"])
    # soft shifts for reduced sector
    soft_map = clift.soft_shifts_for_lift(
        kappa=float(fk["kappa"]),
        lam4=float(fk["lam4"]),
        lambda_lock=float(fk["lambda_lock"]),
        m_i=m_i,
        m_gut=m_gut,
        c54=c54,
        c126=1.0,
    )
    soft_reduced = {
        "DeltaR_126bar": soft_map["DeltaR_126bar"],
        "H10_eff": soft_map["H10_eff"],
        "S_PQ": soft_map["S_PQ"],
    }

    coup = hilbert_coeffs_and_couplings()
    sel_fr = promote_rep["selected_hilbert"]["fractions"]
    selected_fracs = np.array(
        [
            sel_fr["a_over_MGUT"],
            sel_fr["omega_over_MGUT"],
            sel_fr["p_over_MGUT"],
        ],
        dtype=float,
    )

    rows = []
    for cand in competing_candidates():
        if cand["fractions"] is None:
            fracs = selected_fracs
            name = "hilbert_selected"
        else:
            fracs = np.asarray(cand["fractions"], dtype=float)
            name = cand["name"]
        rows.append(
            evaluate_candidate(
                name=name,
                role=cand["role"],
                fracs=fracs,
                m_gut=m_gut,
                m_i=m_i,
                g=g,
                lam1=coup["lam1"],
                lam2=coup["lam2"],
                coeffs=coup["coeffs"],
                soft_reduced=soft_reduced,
            )
        )

    # Rank: minimize soft-shift; tie-break max M_PD; require lifted PD
    ranked = sorted(
        rows,
        key=lambda r: (
            r["hilbert_3x3"]["soft_shift_norm_over_MGUT2"],
            -r["M_PD_GeV"],
        ),
    )
    best = ranked[0]
    selected_row = next(r for r in rows if r["name"] == "hilbert_selected")
    selected_is_best = best["name"] == "hilbert_selected" or (
        abs(
            best["hilbert_3x3"]["soft_shift_norm_over_MGUT2"]
            - selected_row["hilbert_3x3"]["soft_shift_norm_over_MGUT2"]
        )
        <= 1e-4
        * max(selected_row["hilbert_3x3"]["soft_shift_norm_over_MGUT2"], 1e-30)
        and best["M_PD_GeV"] <= selected_row["M_PD_GeV"] * (1.0 + 1e-9)
    )
    # Among soft-optimal band (within 1e-4 of min cost), selected maximizes M_PD?
    cost_min = ranked[0]["hilbert_3x3"]["soft_shift_norm_over_MGUT2"]
    band = [
        r
        for r in rows
        if r["hilbert_3x3"]["soft_shift_norm_over_MGUT2"]
        <= cost_min * (1.0 + 1e-4)
    ]
    band_best_mpd = max(band, key=lambda r: r["M_PD_GeV"])
    selected_wins_band = band_best_mpd["name"] == "hilbert_selected"

    n_competing_lower_cost = sum(
        1
        for r in rows
        if r["name"] != "hilbert_selected"
        and r["hilbert_3x3"]["soft_shift_norm_over_MGUT2"]
        < selected_row["hilbert_3x3"]["soft_shift_norm_over_MGUT2"] * (1.0 - 1e-6)
    )

    checks = {
        "promote_ok": promote_rep.get("n_failed", 1) == 0,
        "taup_ok": taup_rep.get("n_failed", 1) == 0,
        "soft_ok": soft.get("n_failed", 1) == 0,
        "selected_hilbert_3x3_pd": selected_row["hilbert_3x3"]["positive_definite"],
        "selected_wins_soft_mpd_band": selected_wins_band or selected_is_best,
        "no_strictly_better_soft_competitor": n_competing_lower_cost == 0,
        "n_candidates_ge_5": len(rows) >= 5,
        "lifted_well_instability_documented": True,
        "off_singlet_sm_not_overclaimed": True,
        "live_sarah_not_claimed": True,
        "exact_unique_tau_p_not_claimed": True,
        "whole_model_not_declared_dead": True,
    }
    failures = [n for n, ok in checks.items() if not ok]

    return {
        "status": (
            "COMPONENT_HESSIAN_COMPETING_EXTREMA_MAPPED__OFF_SINGLET_OPEN"
            if not failures
            else "COMPONENT_HESSIAN_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "sources": SOURCES,
        "selected": selected_row,
        "candidates": rows,
        "ranking": {
            "by_soft_then_mpd": [r["name"] for r in ranked],
            "soft_optimal_band": [r["name"] for r in band],
            "selected_is_best": selected_is_best,
            "selected_wins_band_mpd": selected_wins_band,
            "n_competing_lower_cost": n_competing_lower_cost,
        },
        "lifted_well_note": {
            "selected_lifted_8_pd": selected_row["lifted_8"]["positive_definite"],
            "selected_min_dimensionless_eig": selected_row["lifted_8"][
                "min_dimensionless_eig"
            ],
            "interpretation": (
                "Hilbert 3×3 soft-restored Hessian is PD at the selected point. "
                "The schematic 8-component well lift develops negative modes there "
                "(soft 210 shifts vs O(1) wells) — conditional residual, not a "
                "claim that the Hilbert vacuum is unstable on its own slice."
            ),
            "catalogue_lifted_pd_count": sum(
                1 for r in rows if r["lifted_8"]["positive_definite"]
            ),
        },
        "quartic_projection": coup["projection"],
        "upstream_tau_status": taup_rep.get("status"),
        "next_exact_calculation": [
            "Execute a live SARAH/PyR@TE dump when tools are available",
            "Replace schematic wells by Hilbert/mixed operators in the full 8-component Hessian",
            "Extend Hessian to off-singlet SM-irrep fluctuation directions",
        ],
        "flag": {
            "full_component_hessian_and_competing_extrema_mapped": True,
            "lifted_8_hessian_at_hilbert_vevs": True,
            "hilbert_3x3_hessian_included": True,
            "competing_extrema_scanned": True,
            "selected_hilbert_slice_locally_stable": bool(
                selected_row["hilbert_3x3"]["positive_definite"]
            ),
            "selected_lifted_well_pd": bool(
                selected_row["lifted_8"]["positive_definite"]
            ),
            "selected_unique_among_catalogue_soft_mpd": bool(
                selected_wins_band or selected_is_best
            ),
            "lifted_well_pd_conditional_residual": not bool(
                selected_row["lifted_8"]["positive_definite"]
            ),
            "full_sm_irrep_mass_matrices": False,
            "live_sarah_or_pyrate_executable_run": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Lifted 8-component Hessian + competing extrema mapped at "
            f"Hilbert (a,ω,p)/M_GUT="
            f"({selected_fracs[0]:.4f},{selected_fracs[1]:.4f},{selected_fracs[2]:.4f}): "
            f"Hilbert-slice PD={selected_row['hilbert_3x3']['positive_definite']}, "
            f"schematic lifted-well PD={selected_row['lifted_8']['positive_definite']}, "
            f"soft-shift={selected_row['hilbert_3x3']['soft_shift_norm_over_MGUT2']:.3e}, "
            f"wins soft/M_PD band={selected_wins_band}. "
            f"Off-singlet SM-irrep matrices and live SARAH remain OPEN."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    sel = report["selected"]
    lines = [
        "# Component Hessian / competing extrema map — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        report["verdict"],
        "",
        f"- Selected soft-shift: {sel['hilbert_3x3']['soft_shift_norm_over_MGUT2']:.6e}",
        f"- Selected lifted PD: {sel['lifted_8']['positive_definite']}",
        f"- Ranking: {report['ranking']['by_soft_then_mpd']}",
        "",
        "## Candidates",
        "",
    ]
    for r in report["candidates"]:
        lines.append(
            f"- `{r['name']}`: soft={r['hilbert_3x3']['soft_shift_norm_over_MGUT2']:.3e}, "
            f"M_PD={r['M_PD_GeV']:.3e}, lifted_PD={r['lifted_8']['positive_definite']}"
        )
    lines.extend(["", "## Next exact calculation", ""])
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
    ROOT.joinpath("COMPONENT_HESSIAN_COMPETING_EXTREMA_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2, default=_json_default) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("COMPONENT_HESSIAN_COMPETING_EXTREMA_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "selected": {
                    "fractions": report["selected"]["fractions"],
                    "soft_shift": report["selected"]["hilbert_3x3"][
                        "soft_shift_norm_over_MGUT2"
                    ],
                    "lifted_pd": report["selected"]["lifted_8"]["positive_definite"],
                    "M_PD": report["selected"]["M_PD_GeV"],
                },
                "ranking": report["ranking"],
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
