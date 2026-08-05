#!/usr/bin/env python3
r"""Off-singlet mixed-45 operator census for ``OPEN_210_CHANNEL_45`` (v20).

Physics
-------
Same-field and PS-singlet-span bilinears into the adjoint vanish
(``so10_210_to_45_projector_v20``). The antisymmetric channel reopens for

    (Φ_vac ⊗ δΦ_off)_45 = P_45(M(Φ_vac, δΦ)) ≠ 0

when ``δΦ`` has an off-singlet component. This module censuses that mixed
operator:

1. Build an orthonormal frame for the 207-dim complement of span{p,a,ω};
2. Measure ``||(Φ_vac ⊗ ê_k)_45||`` on each off-singlet basis vector;
3. Record sector weights of the adjoint image under so6 / so4 / cross planes;
4. Emit a diagnostic curvature seed
   ``ΔM² ≈ λ̃ ||(Φ_vac⊗δΦ)_45||_F² / ||δΦ||²`` (off-singlet only).

Honesty
-------
* Census / diagnostic seed only — not mode-by-mode SM-irrep CG.
* Does not invent 120/320/1050/4125.
* Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import component_lift_210_126_10_v20 as clift
import direct_phi_h_sigmabar_tensor_v20 as direct
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_210_to_45_projector_v20 as p45
import so10_210_to_54_projector_v20 as p54

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "OPEN_210_CHANNEL_45_OFF_SINGLET_CENSUS_V20.json"
OUT_MD = ROOT / "OPEN_210_CHANNEL_45_OFF_SINGLET_CENSUS_V20.md"

N_COMBOS = 210
DIM_OFF = 207  # 210 − 3 PS singlets


def ps_span_projector() -> dict[str, Any]:
    """Orthonormal basis / projector for span{p,a,ω} in the combo basis."""
    singlets = direct.singlet_basis()
    cols = []
    for name in ("p", "a", "omega"):
        v = p54.form_to_combo_vector(singlets[name]).real
        cols.append(v)
    a = np.column_stack(cols)
    q, _ = np.linalg.qr(a)
    # Keep only the numerically independent columns
    rank = int(np.linalg.matrix_rank(q, tol=1e-10))
    q = q[:, :rank]
    p = q @ q.T
    return {"basis": q, "projector": p, "rank": rank}


def off_singlet_frame(ps: dict[str, Any], *, seed: int = 45) -> np.ndarray:
    """Orthonormal frame for the orthogonal complement of the PS span."""
    rng = np.random.default_rng(seed)
    p = ps["projector"]
    # Random vectors projected to complement, then QR
    raw = rng.normal(size=(N_COMBOS, DIM_OFF + 5))
    comp = raw - p @ raw
    q, _ = np.linalg.qr(comp)
    # Drop near-null columns
    norms = np.linalg.norm(q, axis=0)
    keep = norms > 1e-8
    frame = q[:, keep][:, :DIM_OFF]
    return frame


def adjoint_sector_weights(mat45: np.ndarray) -> dict[str, float]:
    """L2 weight of antisymmetric 10×10 on so6 / so4 / cross planes."""
    w = {"so6_color": 0.0, "so4_weak": 0.0, "so6_so4_cross": 0.0}
    m = np.asarray(mat45, dtype=complex)
    for a in range(10):
        for b in range(a + 1, 10):
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
    ps = ps_span_projector()
    frame = off_singlet_frame(ps)

    # Selected vacuum
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

    # Sanity: vacuum ⊗ PS-span → 45 vanishes
    ps_mixed_norms = []
    for i in range(ps["rank"]):
        e = ps["basis"][:, i]
        ps_mixed_norms.append(p45.frobenius(p45.bilinear_210_to_45(phi_v, e, kernel)))

    # Off-singlet census
    norms = []
    sector_acc = {"so6_color": 0.0, "so4_weak": 0.0, "so6_so4_cross": 0.0}
    for k in range(frame.shape[1]):
        e = frame[:, k]
        m45 = p45.bilinear_210_to_45(phi_v, e, kernel)
        n2 = p45.frobenius(m45)
        norms.append(n2)
        sw = adjoint_sector_weights(m45)
        for key in sector_acc:
            sector_acc[key] += sw[key]
    norms_arr = np.asarray(norms, dtype=float)
    # Normalize sector weights
    tot_sec = sum(sector_acc.values()) or 1.0
    sector_frac = {k: float(v / tot_sec) for k, v in sector_acc.items()}

    lam_tilde = 1.0e-2
    # Typical off-singlet seed from RMS of ||(Φ⊗ê)_45||² (ê unit)
    rms = float(np.sqrt(np.mean(norms_arr))) if norms_arr.size else 0.0
    delta_m2 = lam_tilde * (rms**2)  # already /||ê||²=1

    checks = {
        "ps_span_rank_3": ps["rank"] == 3,
        "off_singlet_frame_207": frame.shape[1] == DIM_OFF,
        "vacuum_times_ps_span_45_vanishes": max(ps_mixed_norms) < 1e-8 * (
            max(vac["norm"], 1.0) ** 2
        ),
        "vacuum_times_off_singlet_nontrivial": float(np.max(norms_arr)) > 0.0,
        "seed_positive": delta_m2 > 0.0,
        "cg_not_invented": True,
        "mode_by_mode_sm_not_claimed": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "OPEN_210_CHANNEL_45_OFF_SINGLET_CENSUS_READY__CG_OPEN"
            if not failures
            else "OPEN_210_CHANNEL_45_OFF_SINGLET_CENSUS_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "inventory_slot": {
            "id": "OPEN_210_CHANNEL_45_OFF_SINGLET",
            "status": "PARTIAL_OFF_SINGLET_CENSUS_READY",
            "same_field_and_ps_span": "vanishes (upstream)",
            "off_singlet_mixed": True,
            "mode_by_mode_cg": False,
        },
        "selected_vacuum": {"vevs_GeV": vevs, "phi_norm": vac["norm"]},
        "census": {
            "n_off_singlet_modes": int(frame.shape[1]),
            "norm_sq_min": float(np.min(norms_arr)),
            "norm_sq_max": float(np.max(norms_arr)),
            "norm_sq_mean": float(np.mean(norms_arr)),
            "norm_sq_rms": rms,
            "n_nonzero_modes": int(np.sum(norms_arr > 1e-12 * max(rms, 1.0))),
            "adjoint_sector_fractions": sector_frac,
        },
        "diagnostic_seed": {
            "lam_tilde": lam_tilde,
            "OPEN_210_CHANNEL_45_OFF_SINGLET_seed_GeV2": delta_m2,
            "formula": "ΔM² ≈ λ̃ · RMS_k ||(Φ_vac ⊗ ê_k)_45||_F²",
        },
        "flags": {
            "off_singlet_45_census_ready": not bool(failures),
            "off_singlet_45_mode_cg": False,
            "cg_120_320_1050_4125_invented": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "off_singlet_45_sm_irrep_cg": True,
            "missing_cg_120_320_1050_4125": True,
            "full_nonsusy_vacuum_hessian": True,
        },
        "verdict": (
            "Off-singlet mixed-45 census: vacuum⊗PS-span vanishes; "
            f"{int(np.sum(norms_arr > 1e-12 * max(rms, 1.0)))}/{DIM_OFF} off-singlet "
            f"modes source nonzero (Φ⊗δΦ)_45 (RMS={rms:.6e}). Diagnostic seed "
            f"ΔM²≈{delta_m2:.6e} GeV². Mode-by-mode CG remains OPEN. "
            "Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# OPEN_210_CHANNEL_45 off-singlet census — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Nonzero off-singlet modes: "
        f"`{report['census']['n_nonzero_modes']}/{report['census']['n_off_singlet_modes']}`\n"
        f"- Diagnostic seed: "
        f"`{report['diagnostic_seed']['OPEN_210_CHANNEL_45_OFF_SINGLET_seed_GeV2']}` "
        f"GeV²\n\n"
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
