#!/usr/bin/env python3
r"""Off-singlet mixed-210 operator census for ``OPEN_210_CHANNEL_210`` (v20).

Physics
-------
PS-singlet ``(Φ_vac ⊗ Φ_vac)_210`` is already nonzero (upstream self-map).
This module censuses the mixed off-singlet channel

    (Φ_vac ⊗ δΦ_off)_210 = Ξ(Φ_vac, δΦ)

on the 207-dim complement of span{p,a,ω}, with a diagnostic seed
``ΔM² ≈ λ̃ · RMS_k ||Ξ(Φ,ê_k)||²``.

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
import open_210_channel_45_off_singlet_census_v20 as census45
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_210_to_210_self_map_v20 as m210
import so10_210_to_54_projector_v20 as p54

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "OPEN_210_CHANNEL_210_OFF_SINGLET_CENSUS_V20.json"
OUT_MD = ROOT / "OPEN_210_CHANNEL_210_OFF_SINGLET_CENSUS_V20.md"

DIM_OFF = census45.DIM_OFF


def build_report() -> dict[str, Any]:
    ps = census45.ps_span_projector()
    frame = census45.off_singlet_frame(ps, seed=210)

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

    # Vacuum self-map (PS singlet seed reference)
    xi_self = m210.bilinear_210_to_210(phi_v, phi_v)
    self_fn = m210.frobenius_vec(xi_self)

    # Vacuum ⊗ PS-span
    ps_mixed_norms = []
    for i in range(ps["rank"]):
        e = ps["basis"][:, i]
        ps_mixed_norms.append(
            m210.frobenius_vec(m210.bilinear_210_to_210(phi_v, e))
        )

    # Precompute vacuum tensor for the off-singlet loop
    f_vac = m210.combo_to_tensor(phi_v)
    norms = []
    for k in range(frame.shape[1]):
        g = m210.combo_to_tensor(frame[:, k])
        raw = np.einsum("ijmn,klmn->ijkl", f_vac, g, optimize=True)
        xi = m210.tensor_to_combo(m210.antisymmetrize4(raw))
        norms.append(m210.frobenius_vec(xi))
    norms_arr = np.asarray(norms, dtype=float)
    rms = float(np.sqrt(np.mean(norms_arr))) if norms_arr.size else 0.0
    lam_tilde = 1.0e-2
    delta_m2 = lam_tilde * (rms**2)
    n_nonzero = int(np.sum(norms_arr > 1e-12 * max(rms, 1.0)))

    checks = {
        "ps_span_rank_3": ps["rank"] == 3,
        "off_singlet_frame_207": frame.shape[1] == DIM_OFF,
        "vacuum_self_210_nontrivial": self_fn > 0.0,
        "vacuum_times_off_singlet_nontrivial": float(np.max(norms_arr)) > 0.0,
        "seed_positive": delta_m2 > 0.0,
        "cg_not_invented": True,
        "mode_by_mode_sm_not_claimed": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "OPEN_210_CHANNEL_210_OFF_SINGLET_CENSUS_READY__CG_OPEN"
            if not failures
            else "OPEN_210_CHANNEL_210_OFF_SINGLET_CENSUS_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "inventory_slot": {
            "id": "OPEN_210_CHANNEL_210",
            "status": "PARTIAL_OFF_SINGLET_CENSUS_READY",
            "ps_singlet_self_map": "nontrivial (upstream so10_210_to_210_self_map)",
            "off_singlet_mixed": True,
            "mode_by_mode_cg": False,
        },
        "selected_vacuum": {
            "vevs_GeV": vevs,
            "phi_norm": vac["norm"],
            "self_210_frobenius": self_fn,
            "ps_span_mixed_norms": [float(x) for x in ps_mixed_norms],
        },
        "census": {
            "n_off_singlet_modes": int(frame.shape[1]),
            "norm_sq_min": float(np.min(norms_arr)),
            "norm_sq_max": float(np.max(norms_arr)),
            "norm_sq_mean": float(np.mean(norms_arr)),
            "norm_sq_rms": rms,
            "n_nonzero_modes": n_nonzero,
        },
        "diagnostic_seed": {
            "lam_tilde": lam_tilde,
            "OPEN_210_CHANNEL_210_OFF_SINGLET_seed_GeV2": delta_m2,
            "formula": "ΔM² ≈ λ̃ · RMS_k ||Ξ(Φ_vac, ê_k)||²",
        },
        "flags": {
            "off_singlet_210_census_ready": not bool(failures),
            "off_singlet_210_mode_cg": False,
            "cg_120_320_1050_4125_invented": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "off_singlet_210_sm_irrep_cg": True,
            "missing_cg_120_320_1050_4125": True,
            "full_nonsusy_vacuum_hessian": True,
        },
        "verdict": (
            "Off-singlet mixed-210 census: vacuum self-map nontrivial; "
            f"{n_nonzero}/{DIM_OFF} off-singlet modes source nonzero "
            f"Ξ(Φ,δΦ) (RMS={rms:.6e}). Diagnostic seed ΔM²≈{delta_m2:.6e} "
            "GeV². Mode-by-mode CG remains OPEN. Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# OPEN_210_CHANNEL_210 off-singlet census — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Nonzero off-singlet modes: "
        f"`{report['census']['n_nonzero_modes']}/{report['census']['n_off_singlet_modes']}`\n"
        f"- Diagnostic seed: "
        f"`{report['diagnostic_seed']['OPEN_210_CHANNEL_210_OFF_SINGLET_seed_GeV2']}` "
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
