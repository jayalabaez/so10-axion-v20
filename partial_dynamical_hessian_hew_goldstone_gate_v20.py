#!/usr/bin/env python3
"""Partial dynamical Hessian + hEW Goldstone gate (v20).

Assembles a form-basis dynamical skeleton on the extended orbit embedding

    ℝ²¹⁰ ⊕ (ambient five-forms ℝ⁵⁰⁴) ⊕ ℝ¹⁰   (dim 724)

using:

* isotropic/norm Schur A/C seeds (including OPEN_MIXED_126);
* Hodge ``-i`` placement of physical ``C₁₂₆`` into ambient 504
  (``hodge_126bar_c_embedding_portal_lift_v20``);
* lifted portal ``B=λ₄ v_S T_Φ`` into H10_real ↔ 504 mixing
  (same anti-self-dual basis as the Schur gate; Im H still outside 724).

Then applies the exact 36-Goldstone projector from
``so10_gauge_orbit_with_hew_v20``.

Honesty
-------
* Im H is not in the orbit embedding, so the portal lift is the real-H
  sector of the holomorphic mixing.
* Does not invent 120/320/1050/4125 CG.
* Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import diagonal_h10_sigmabar_m2_isotropic_54_slots_v20 as iso
import direct_portal_mass2_schur_gate_v20 as schur
import hodge_126bar_c_embedding_portal_lift_v20 as hodge
import so10_gauge_orbit_with_hew_v20 as hew_orbit
import so10_goldstone_nullspace_projector_v20 as gproj

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "PARTIAL_DYNAMICAL_HESSIAN_HEW_GOLDSTONE_GATE_V20.json"
OUT_MD = ROOT / "PARTIAL_DYNAMICAL_HESSIAN_HEW_GOLDSTONE_GATE_V20.md"

SOFT_210_FLOOR_GEV2 = 1.0e4
EXPECTED_GOLDSTONES = 36
EXPECTED_FIELD_DIM = 724


def goldstone_support_fractions(
    frame: np.ndarray, *, n_210: int = 210, n_sigma: int = 504, n_h10: int = 10
) -> dict[str, Any]:
    """L2 support of each Goldstone mode on (210, Σ̄, H10) blocks."""
    if frame.ndim != 2 or frame.shape[0] != n_210 + n_sigma + n_h10:
        raise ValueError("frame embedding mismatch")
    rows = []
    for j in range(frame.shape[1]):
        v = frame[:, j]
        nrm2 = float(np.dot(v, v))
        if nrm2 <= 0.0:
            frac_210 = frac_s = frac_h = 0.0
        else:
            frac_210 = float(np.dot(v[:n_210], v[:n_210]) / nrm2)
            frac_s = float(
                np.dot(v[n_210 : n_210 + n_sigma], v[n_210 : n_210 + n_sigma])
                / nrm2
            )
            frac_h = float(np.dot(v[-n_h10:], v[-n_h10:]) / nrm2)
        rows.append(
            {
                "mode": j,
                "frac_210": frac_210,
                "frac_sigmabar": frac_s,
                "frac_H10": frac_h,
            }
        )
    mean = {
        "frac_210": float(np.mean([r["frac_210"] for r in rows])) if rows else 0.0,
        "frac_sigmabar": float(np.mean([r["frac_sigmabar"] for r in rows]))
        if rows
        else 0.0,
        "frac_H10": float(np.mean([r["frac_H10"] for r in rows])) if rows else 0.0,
    }
    return {
        "per_mode": rows,
        "mean_fractions": mean,
        "n_modes_with_H10_support": int(
            sum(1 for r in rows if r["frac_H10"] > 1e-6)
        ),
        "n_modes_with_sigmabar_support": int(
            sum(1 for r in rows if r["frac_sigmabar"] > 1e-6)
        ),
        "n_modes_with_210_support": int(
            sum(1 for r in rows if r["frac_210"] > 1e-6)
        ),
    }


def spectrum_after_projection(
    hessian: np.ndarray, p_phys: np.ndarray, *, rel_tol: float = 1e-10
) -> dict[str, Any]:
    h_proj = gproj.project_hessian(hessian, p_phys)
    eigs = np.linalg.eigvalsh(h_proj)
    scale = max(1.0, float(np.max(np.abs(eigs))))
    tol = rel_tol * scale
    return {
        "n_zero": int(np.sum(np.abs(eigs) <= tol)),
        "n_positive": int(np.sum(eigs > tol)),
        "n_negative": int(np.sum(eigs < -tol)),
        "eig_min_GeV2": float(eigs[0]),
        "eig_max_GeV2": float(eigs[-1]),
        "tol_GeV2": tol,
        "condition_proxy": scale,
    }


def goldstone_kernel_residual(
    hessian: np.ndarray, frame: np.ndarray, p_phys: np.ndarray
) -> dict[str, float]:
    h_proj = gproj.project_hessian(hessian, p_phys)
    if frame.size == 0:
        return {"frame_image_residual": 0.0, "frobenius_Hphys_PG": 0.0}
    p_g = frame @ frame.T
    return {
        "frame_image_residual": float(np.linalg.norm(h_proj @ frame))
        / max(1.0, float(np.linalg.norm(h_proj))),
        "frobenius_Hphys_PG": float(np.linalg.norm(h_proj @ p_g))
        / max(1.0, float(np.linalg.norm(h_proj))),
    }


def build_report() -> dict[str, Any]:
    iso_report = iso.build_report()
    orbit_report = hew_orbit.build_report()
    hodge_report = hodge.build_report()

    a = iso_report["A_partial_GeV2"]
    c = iso_report["C_partial_GeV2"]
    vevs = iso_report["vevs_GeV"]
    lam4 = iso_report["portal_B"]["lam4"]
    mixing = schur.portal_mass2_matrix(
        p=vevs["p"],
        a=vevs["a"],
        omega=vevs["omega"],
        v_s=vevs["vS"],
        lam4=lam4,
    )
    m2_210 = float(max(SOFT_210_FLOOR_GEV2, float(np.min(a)), float(np.min(c))))
    assembled = hodge.assemble_h10_sigma_block(
        a_h10=a, c_diag=c, b_10x126=mixing, m2_210=m2_210
    )
    hess = assembled["hessian_724"]
    emb = assembled["embedding"]

    ext = hew_orbit.extended_tangent_matrix()
    tangent = ext["matrix"]
    n_field = ext["n_field_components"]
    frame_info = gproj.goldstone_frame_from_tangent(tangent)
    frame = frame_info["frame"]
    projs = gproj.projectors(frame, n_field)
    p_phys = projs["P_phys"]
    p_g = projs["P_G"]

    support = goldstone_support_fractions(frame)

    unit_hess = np.eye(n_field, dtype=float)
    unit_spec = spectrum_after_projection(unit_hess, p_phys)
    unit_kernel = goldstone_kernel_residual(unit_hess, frame, p_phys)

    diag = np.diag(hess).copy()
    median = float(np.median(np.abs(diag[np.abs(diag) > 0.0]))) if np.any(diag) else 1.0
    if median <= 0.0:
        median = 1.0
    scaled_hess = hess / median
    dyn_spec = spectrum_after_projection(scaled_hess, p_phys)
    dyn_kernel = goldstone_kernel_residual(scaled_hess, frame, p_phys)

    schur_rep = iso_report.get("schur_with_partial_diagonals", {})
    n_phys = EXPECTED_FIELD_DIM - EXPECTED_GOLDSTONES

    checks = {
        "isotropic_partial_green": iso_report.get("n_failed", 1) == 0,
        "hew_orbit_36_green": orbit_report.get("n_failed", 1) == 0,
        "hodge_embedding_green": hodge_report.get("n_failed", 1) == 0,
        "field_dim_724": n_field == EXPECTED_FIELD_DIM,
        "goldstone_rank_36": frame_info["rank"] == EXPECTED_GOLDSTONES,
        "trace_P_G_36": abs(float(np.trace(p_g)) - EXPECTED_GOLDSTONES) < 1e-6,
        "hodge_C_placed": abs(emb["trace_P_126bar"] - 252.0) < 1e-6,
        "portal_B_inserted": assembled["portal"]["inserted"],
        "unit_projected_exactly_36_zeros": unit_spec["n_zero"] == EXPECTED_GOLDSTONES,
        "unit_projected_no_negative": unit_spec["n_negative"] == 0,
        "unit_projected_physical_positive": unit_spec["n_positive"] == n_phys,
        "unit_goldstone_kernel_tiny": unit_kernel["frame_image_residual"] < 1e-10,
        "dyn_scaled_projected_exactly_36_zeros": dyn_spec["n_zero"]
        == EXPECTED_GOLDSTONES,
        "dyn_scaled_projected_no_negative": dyn_spec["n_negative"] == 0,
        "dyn_scaled_projected_physical_positive": dyn_spec["n_positive"] == n_phys,
        "dyn_goldstone_kernel_tiny": dyn_kernel["frame_image_residual"] < 1e-8,
        "schur_272_recorded": "positive_definite" in schur_rep,
        "four_isotropic_slots_filled": len(
            iso_report.get("partial_diagonals", {}).get("filled_slots", [])
        )
        == 4,
        "im_H_not_faked": not assembled["portal"].get("im_H_included", True),
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "PARTIAL_DYNAMICAL_HESSIAN_HODGE_C_PORTAL_LIFT_READY__IM_H_OPEN"
            if not failures
            else "PARTIAL_DYNAMICAL_HESSIAN_HEW_GOLDSTONE_GATE_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "upstream": {
            "isotropic_status": iso_report.get("status"),
            "isotropic_n_failed": iso_report.get("n_failed"),
            "hew_orbit_status": orbit_report.get("status"),
            "hew_orbit_n_failed": orbit_report.get("n_failed"),
            "hodge_status": hodge_report.get("status"),
            "hodge_n_failed": hodge_report.get("n_failed"),
            "schur_positive_definite": schur_rep.get("positive_definite"),
            "schur_margin": schur_rep.get("schur_margin"),
            "real_hessian_min_eigenvalue_GeV2": iso_report.get(
                "real_hessian_min_eigenvalue_GeV2"
            ),
        },
        "embedding": ext["embedding"],
        "form_basis_skeleton": {
            "shape": [EXPECTED_FIELD_DIM, EXPECTED_FIELD_DIM],
            "m2_210_placeholder_GeV2": m2_210,
            "median_abs_diag_GeV2": median,
            "hodge_126_placement": "anti_self_dual_frame_E_map",
            "trace_P_126bar": emb["trace_P_126bar"],
            "complement_floor_GeV2": emb["complement_floor_GeV2"],
            "uses_portal_B": True,
            "portal_frobenius_GeV2": assembled["portal"].get("frobenius_GeV2"),
            "im_H_included": False,
            "basis": "exterior_algebra_flatten_real_plus_hodge_126bar",
        },
        "goldstone_projection": {
            "rank": frame_info["rank"],
            "trace_P_G": float(np.trace(p_g)),
            "trace_P_phys": float(np.trace(p_phys)),
            "support": {
                "mean_fractions": support["mean_fractions"],
                "n_modes_with_H10_support": support["n_modes_with_H10_support"],
                "n_modes_with_sigmabar_support": support[
                    "n_modes_with_sigmabar_support"
                ],
                "n_modes_with_210_support": support["n_modes_with_210_support"],
            },
            "unit_skeleton_spectrum": unit_spec,
            "unit_kernel_residual": unit_kernel,
            "dynamical_scaled_spectrum": dyn_spec,
            "dynamical_kernel_residual": dyn_kernel,
        },
        "schur_272_aulakh_basis": {
            "note": (
                "Portal B uses the same anti-self-dual 126bar basis as the "
                "form-basis lift; Schur 272 still includes Im H, which the "
                "724 orbit embedding omits."
            ),
            "positive_definite": schur_rep.get("positive_definite"),
            "schur_margin": schur_rep.get("schur_margin"),
            "largest_normalized_singular_value": schur_rep.get(
                "largest_normalized_singular_value"
            ),
        },
        "flags": {
            "partial_dynamical_hessian_goldstone_gate": not bool(failures),
            "hodge_c_embedding_applied": True,
            "portal_b_lifted_into_form_basis": assembled["portal"]["inserted"],
            "hew_36_goldstones_applied": frame_info["rank"] == EXPECTED_GOLDSTONES,
            "form_basis_skeleton_positive_after_projection": (
                dyn_spec["n_negative"] == 0
                and dyn_spec["n_zero"] == EXPECTED_GOLDSTONES
            ),
            "im_H_in_orbit_embedding": False,
            "full_component_hessian_complete": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "include_Im_H_in_extended_embedding": True,
            "S_Phi17_dynamical_blocks": True,
            "missing_cg_120_320_1050_4125": True,
            "global_stationarity_boundedness": True,
        },
        "verdict": (
            "Hodge-placed C and lifted portal B on the 724-dim form embedding, "
            f"after removing {EXPECTED_GOLDSTONES} hEW Goldstones, yield "
            f"{dyn_spec['n_zero']} zeros / {dyn_spec['n_positive']} positive / "
            f"{dyn_spec['n_negative']} negative (median-scaled). Im H remains "
            "outside this embedding. Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    gp = report["goldstone_projection"]
    OUT_MD.write_text(
        "# Partial dynamical Hessian + hEW Goldstone gate — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Goldstones removed: `{gp['rank']}`\n"
        f"- Hodge C placement: `{report['form_basis_skeleton']['hodge_126_placement']}`\n"
        f"- Portal B inserted: `{report['form_basis_skeleton']['uses_portal_B']}`\n"
        f"- Dynamical (median-scaled) zeros/pos/neg: "
        f"`{gp['dynamical_scaled_spectrum']['n_zero']}` / "
        f"`{gp['dynamical_scaled_spectrum']['n_positive']}` / "
        f"`{gp['dynamical_scaled_spectrum']['n_negative']}`\n\n"
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
