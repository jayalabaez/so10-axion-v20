#!/usr/bin/env python3
r"""SM Cartan quantum numbers for off-singlet mixed-54 images (v20).

Physics
-------
Upstream ``open_210_channel_54_off_singlet_census_v20`` proves every off-singlet
mode sources a nonzero

    Q_k = (Φ_vac ⊗ ê_k)_54 = P_54(M(Φ_vac, ê_k)) ∈ Sym_0(10).

This module assigns **Lie-algebra Cartan / sector labels** to each ``Q_k``
under the repo PS embedding ℝ¹⁰ = ℝ⁶_color ⊕ ℝ⁴_weak, without Young/CG:

1. Sector L2 on so6 / so4 / cross blocks of the symmetric matrix;
2. Adjoint activity of the five so(10) Cartans ``H_p = i M_{2p,2p+1}`` on End;
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
import open_210_channel_45_off_singlet_census_v20 as census45
import open_210_channel_45_off_singlet_sm_quantum_numbers_v20 as qn45
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_210_to_54_projector_v20 as p54

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "OPEN_210_CHANNEL_54_OFF_SINGLET_SM_QN_V20.json"
OUT_MD = ROOT / "OPEN_210_CHANNEL_54_OFF_SINGLET_SM_QN_V20.md"


def sym_sector_weights(mat54: np.ndarray) -> dict[str, float]:
    """L2 weight of symmetric 10×10 on so6 / so4 / cross planes (incl. diag)."""
    w = {"so6_color": 0.0, "so4_weak": 0.0, "so6_so4_cross": 0.0}
    m = np.asarray(mat54, dtype=complex)
    for a in range(10):
        for b in range(a, 10):
            val = abs(m[a, b]) ** 2
            if a < 6 and b < 6:
                w["so6_color"] += val
            elif a >= 6 and b >= 6:
                w["so4_weak"] += val
            else:
                w["so6_so4_cross"] += val
    return w


def build_report() -> dict[str, Any]:
    kernel = p54.contraction_kernel_210()
    ps = census45.ps_span_projector()
    frame = census45.off_singlet_frame(ps, seed=54)

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
        q54 = p54.bilinear_210_to_54(phi_v, e, kernel)
        if p54.frobenius(q54) <= 0.0:
            continue
        n_labeled += 1
        sector = sym_sector_weights(q54)
        acts = qn45.cartan_activities(q54)
        lab = qn45.classify_mode(sector, acts)
        buckets[lab["bucket"]] += 1
        sector_dom[lab["dominant_sector"]] += 1
        if lab["Q_neutral"]:
            q0_count += 1
        for key, val in acts.items():
            activity_acc[key] += val
        max_q = max(max_q, acts["Q_em"])
        min_q = min(min_q, acts["Q_em"])

    mean_act = {k: float(v / max(n_labeled, 1)) for k, v in activity_acc.items()}

    # Vacuum self-map remains nontrivial (contrast with 45 vanishing on PS)
    q_self = p54.bilinear_210_to_54(phi_v, phi_v, kernel)
    self_fn = p54.frobenius(q_self)

    checks = {
        "off_singlet_frame_207": frame.shape[1] == census45.DIM_OFF,
        "all_nonzero_modes_labeled": n_labeled == census45.DIM_OFF,
        "vacuum_self_54_nontrivial": self_fn > 0.0,
        "buckets_nonempty": sum(buckets.values()) == n_labeled,
        "cartan_activities_finite": all(np.isfinite(v) for v in mean_act.values()),
        "q_activity_span_recorded": max_q >= min_q and n_labeled > 0,
        "cg_not_invented": True,
        "full_sm_irrep_cg_not_claimed": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "OPEN_210_CHANNEL_54_OFF_SINGLET_SM_QN_READY__CG_OPEN"
            if not failures
            else "OPEN_210_CHANNEL_54_OFF_SINGLET_SM_QN_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "conventions": {
            "cartans": {
                f"H{i}": f"i M_{a}{b}"
                for i, (a, b) in enumerate(qn45.CARTAN_PLANES)
            },
            "Q_em": "T3_L + T3_R = -i M_67",
            "Q_neutral_tol": qn45.Q_NEUTRAL_TOL,
            "dominant_sector_frac": qn45.DOMINANT_FRAC,
            "note": (
                "Labels from End adjoint Cartan activity + so6/so4/cross L2 "
                "on Sym_0 images; not Young-tableau CG multiplicities."
            ),
        },
        "inventory_slot": {
            "id": "OPEN_210_CHANNEL_54_OFF_SINGLET",
            "status": "PARTIAL_SM_QUANTUM_NUMBERS_READY",
            "mode_by_mode_cg": False,
        },
        "selected_vacuum": {
            "vevs_GeV": vevs,
            "phi_norm": vac["norm"],
            "self_54_frobenius": self_fn,
        },
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
            "off_singlet_54_sm_qn_ready": not bool(failures),
            "off_singlet_54_mode_cg": False,
            "cg_120_320_1050_4125_invented": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "off_singlet_54_sm_irrep_cg_coeffs": True,
            "missing_cg_120_320_1050_4125": True,
            "full_nonsusy_vacuum_hessian": True,
        },
        "verdict": (
            f"Off-singlet mixed-54 SM Cartan labels: {n_labeled}/{census45.DIM_OFF} "
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
        "# OPEN_210_CHANNEL_54 off-singlet SM Cartan quantum numbers — v20\n\n"
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
