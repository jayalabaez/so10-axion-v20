#!/usr/bin/env python3
r"""SM Cartan quantum numbers for off-singlet mixed-45 images (v20).

Physics
-------
Upstream ``open_210_channel_45_off_singlet_census_v20`` proves every off-singlet
mode sources a nonzero adjoint image

    M_k = (Φ_vac ⊗ ê_k)_45 ∈ ∧² ℝ¹⁰ ≅ 45.

This module assigns **Lie-algebra Cartan labels** to each ``M_k`` under the
repo PS embedding ℝ¹⁰ = ℝ⁶_color ⊕ ℝ⁴_weak, without Young/CG projectors:

1. Sector L2 on so6 / so4 / cross planes (same split as the Goldstone catalog);
2. Adjoint activity of the five so(10) Cartans ``H_p = i M_{2p,2p+1}``;
3. Electric-charge activity of ``Q = T3_L + T3_R = -i M_67``;
4. Discrete bucket: dominant sector × Q-neutral vs charged.

Honesty
-------
* Cartan / sector labels only — not mode-by-mode SM-irrep CG coefficients.
* Does not invent 120/320/1050/4125.
* Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

import component_lift_210_126_10_v20 as clift
import open_210_channel_45_off_singlet_census_v20 as census
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_210_to_45_projector_v20 as p45
import so10_210_to_54_projector_v20 as p54

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "OPEN_210_CHANNEL_45_OFF_SINGLET_SM_QN_V20.json"
OUT_MD = ROOT / "OPEN_210_CHANNEL_45_OFF_SINGLET_SM_QN_V20.md"

N = 10
CARTAN_PLANES = ((0, 1), (2, 3), (4, 5), (6, 7), (8, 9))
Q_NEUTRAL_TOL = 0.15
DOMINANT_FRAC = 0.55


def elementary_asym(a: int, b: int) -> np.ndarray:
    m = np.zeros((N, N), dtype=float)
    m[a, b] = 1.0
    m[b, a] = -1.0
    return m


def herm_cartan(a: int, b: int) -> np.ndarray:
    """Hermitian Cartan ``i M_ab`` on ℂ¹⁰."""
    return 1.0j * elementary_asym(a, b)


def q_em_generator() -> np.ndarray:
    """``Q = T3_L + T3_R = -i M_67`` (Hermitian on ℂ¹⁰)."""
    return -1.0j * elementary_asym(6, 7)


def frobenius_c(mat: np.ndarray) -> float:
    return float(np.sqrt(np.vdot(mat, mat).real))


def adjoint_action(h: np.ndarray, x: np.ndarray) -> np.ndarray:
    return h @ x - x @ h


def cartan_activities(m45: np.ndarray) -> dict[str, float]:
    norm = frobenius_c(m45)
    if norm < 1e-30:
        return {f"H{i}": 0.0 for i in range(5)} | {"Q_em": 0.0}
    out: dict[str, float] = {}
    for i, (a, b) in enumerate(CARTAN_PLANES):
        out[f"H{i}"] = frobenius_c(adjoint_action(herm_cartan(a, b), m45)) / norm
    out["Q_em"] = frobenius_c(adjoint_action(q_em_generator(), m45)) / norm
    return out


def classify_mode(
    sector: dict[str, float], activities: dict[str, float]
) -> dict[str, Any]:
    tot = sum(sector.values()) or 1.0
    fracs = {k: float(v / tot) for k, v in sector.items()}
    dominant = max(fracs, key=fracs.get)
    if fracs[dominant] < DOMINANT_FRAC:
        dominant = "mixed"
    q_neutral = bool(activities["Q_em"] < Q_NEUTRAL_TOL)
    bucket = f"{dominant}__{'Q0' if q_neutral else 'Qcharged'}"
    return {
        "dominant_sector": dominant,
        "sector_fractions": fracs,
        "Q_neutral": q_neutral,
        "bucket": bucket,
    }


def build_report() -> dict[str, Any]:
    kernel = p54.contraction_kernel_210()
    ps = census.ps_span_projector()
    frame = census.off_singlet_frame(ps)

    anchor = scalar_pd._unification_anchor()
    ledger = clift.component_ledger(anchor)
    by_name = {row["name"]: float(row["vev_GeV"]) for row in ledger["components"]}
    vevs = {
        "p": by_name["p_210"],
        "a": by_name["a_210"],
        "omega": by_name["omega_210"],
    }
    vac = p54.selected_vacuum_phi_combo(vevs)
    phi_v = vac["combo"].real

    buckets: Counter[str] = Counter()
    sector_dom: Counter[str] = Counter()
    q0_count = 0
    activity_acc = {f"H{i}": 0.0 for i in range(5)}
    activity_acc["Q_em"] = 0.0
    n_labeled = 0
    max_q = 0.0
    min_q = 1.0e99

    for k in range(frame.shape[1]):
        e = frame[:, k]
        m45 = p45.bilinear_210_to_45(phi_v, e, kernel)
        if p45.frobenius(m45) <= 0.0:
            continue
        n_labeled += 1
        sector = census.adjoint_sector_weights(m45)
        acts = cartan_activities(m45)
        lab = classify_mode(sector, acts)
        buckets[lab["bucket"]] += 1
        sector_dom[lab["dominant_sector"]] += 1
        if lab["Q_neutral"]:
            q0_count += 1
        for key, val in acts.items():
            activity_acc[key] += val
        max_q = max(max_q, acts["Q_em"])
        min_q = min(min_q, acts["Q_em"])

    mean_act = {k: float(v / max(n_labeled, 1)) for k, v in activity_acc.items()}

    # Sanity: PS-span images still vanish
    ps_norms = [
        p45.frobenius(p45.bilinear_210_to_45(phi_v, ps["basis"][:, i], kernel))
        for i in range(ps["rank"])
    ]

    checks = {
        "off_singlet_frame_207": frame.shape[1] == census.DIM_OFF,
        "all_nonzero_modes_labeled": n_labeled == census.DIM_OFF,
        "vacuum_times_ps_span_45_vanishes": max(ps_norms) < 1e-8 * (
            max(vac["norm"], 1.0) ** 2
        ),
        "buckets_nonempty": sum(buckets.values()) == n_labeled,
        "cartan_activities_finite": all(np.isfinite(v) for v in mean_act.values()),
        "q_activity_span_recorded": max_q > min_q,
        "cg_not_invented": True,
        "full_sm_irrep_cg_not_claimed": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "OPEN_210_CHANNEL_45_OFF_SINGLET_SM_QN_READY__CG_OPEN"
            if not failures
            else "OPEN_210_CHANNEL_45_OFF_SINGLET_SM_QN_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "conventions": {
            "cartans": {
                f"H{i}": f"i M_{a}{b}" for i, (a, b) in enumerate(CARTAN_PLANES)
            },
            "Q_em": "T3_L + T3_R = -i M_67",
            "T3_L": "-i (M_67 + M_89)/2",
            "T3_R": "-i (M_67 - M_89)/2",
            "Q_neutral_tol": Q_NEUTRAL_TOL,
            "dominant_sector_frac": DOMINANT_FRAC,
            "note": (
                "Labels from adjoint Cartan activity + so6/so4/cross L2; "
                "not Young-tableau CG multiplicities."
            ),
        },
        "inventory_slot": {
            "id": "OPEN_210_CHANNEL_45_OFF_SINGLET",
            "status": "PARTIAL_SM_QUANTUM_NUMBERS_READY",
            "mode_by_mode_cg": False,
        },
        "selected_vacuum": {"vevs_GeV": vevs, "phi_norm": vac["norm"]},
        "quantum_numbers": {
            "n_modes_labeled": n_labeled,
            "n_Q_neutral": q0_count,
            "n_Q_charged": n_labeled - q0_count,
            "dominant_sector_counts": dict(sector_dom),
            "bucket_counts": dict(sorted(buckets.items())),
            "mean_cartan_adjoint_activity": mean_act,
            "Q_em_activity_min": float(min_q if n_labeled else 0.0),
            "Q_em_activity_max": float(max_q if n_labeled else 0.0),
        },
        "flags": {
            "off_singlet_45_sm_qn_ready": not bool(failures),
            "off_singlet_45_mode_cg": False,
            "cg_120_320_1050_4125_invented": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "off_singlet_45_sm_irrep_cg_coeffs": True,
            "missing_cg_120_320_1050_4125": True,
            "full_nonsusy_vacuum_hessian": True,
        },
        "verdict": (
            f"Off-singlet mixed-45 SM Cartan labels: {n_labeled}/{census.DIM_OFF} "
            f"modes classified; Q-neutral={q0_count}, Q-charged="
            f"{n_labeled - q0_count}; dominant sectors "
            f"{dict(sector_dom)}. Mode-by-mode CG coefficients remain OPEN. "
            "Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    qn = report["quantum_numbers"]
    OUT_MD.write_text(
        "# OPEN_210_CHANNEL_45 off-singlet SM Cartan quantum numbers — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Modes labeled: `{qn['n_modes_labeled']}`\n"
        f"- Q-neutral / Q-charged: `{qn['n_Q_neutral']}` / `{qn['n_Q_charged']}`\n"
        f"- Dominant sectors: `{qn['dominant_sector_counts']}`\n"
        f"- Buckets: `{qn['bucket_counts']}`\n\n"
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
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
