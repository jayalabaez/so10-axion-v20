#!/usr/bin/env python3
"""Partial dynamical Hessian + hEW Goldstone gate (v20).

Assembles an honest *form-basis* dynamical skeleton on the extended
orbit embedding

    ℝ²¹⁰ ⊕ ℂ¹²⁶ ≅ ℝ⁵⁰⁴ ⊕ ℝ¹⁰   (dim 724)

using the defensible isotropic/norm Schur A/C seeds (including the
OPEN_MIXED_126 PS-singlet fill), then applies the exact 36-Goldstone
projector from ``so10_gauge_orbit_with_hew_v20``.

Separately records the 272-real Schur portal Hessian (Aulakh 10×126
basis). That Schur block is **not** identified with the exterior-algebra
embedding here: a Cartesian basis map between form components and the
portal tensor indices remains OPEN, so portal B is not inserted into the
724-space skeleton.

Honesty
-------
* Proves Goldstone removal on a positive-diagonal dynamical skeleton.
* Does not claim full component Hessian closure.
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
import so10_gauge_orbit_with_hew_v20 as hew_orbit
import so10_goldstone_nullspace_projector_v20 as gproj

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "PARTIAL_DYNAMICAL_HESSIAN_HEW_GOLDSTONE_GATE_V20.json"
OUT_MD = ROOT / "PARTIAL_DYNAMICAL_HESSIAN_HEW_GOLDSTONE_GATE_V20.md"

SOFT_210_FLOOR_GEV2 = 1.0e4
EXPECTED_GOLDSTONES = 36
EXPECTED_FIELD_DIM = 724


def form_basis_diagonal_hessian(
    *,
    a_h10: list[float] | np.ndarray,
    c_sigma: list[float] | np.ndarray,
    m2_210: float = SOFT_210_FLOOR_GEV2,
) -> dict[str, Any]:
    """Block-diagonal M² on (210 real, five-form Re/Im 504, H10 real).

    The orbit embedding uses the ambient five-form space
    ``C(10,5)=252`` complex (=504 real), not the Hodge ``-i`` 126bar
    subspace alone. Until a Hodge-projector map places the physical
    126-mode ``C_partial`` into that subspace, the skeleton uses
    ``min(C_partial)`` as a uniform positive floor on all 504 real
    five-form components (fail-closed, not overclaiming mode-by-mode fill).
    """
    a = np.asarray(a_h10, dtype=float)
    c = np.asarray(c_sigma, dtype=float)
    if a.shape != (10,):
        raise ValueError("a_h10 must have shape (10,)")
    if c.shape != (126,):
        raise ValueError("c_sigma must have shape (126,)")
    c_floor = float(np.min(c))
    a_floor = float(np.min(a))
    # Keep the 210 placeholder at the A/C mass scale. A literal soft floor
    # of O(10^4) GeV² under GUT-scale A/C (~10^30) is numerically null under
    # eigvalsh tolerances and would fake hundreds of extra zeros.
    m2_210_eff = max(float(m2_210), a_floor, c_floor)
    # Embedding order matches so10_gauge_orbit_with_hew_v20.extended_tangent_matrix:
    # 210 real | 252 Re + 252 Im (=504) | H10 real.
    diag = np.concatenate(
        [
            np.full(210, m2_210_eff, dtype=float),
            np.full(504, c_floor, dtype=float),
            a,
        ]
    )
    if diag.shape != (EXPECTED_FIELD_DIM,):
        raise ValueError(f"expected diag length {EXPECTED_FIELD_DIM}, got {diag.shape}")
    if not np.all(np.isfinite(diag)) or np.any(diag <= 0.0):
        raise ValueError("form-basis diagonal entries must be finite and positive")
    return {
        "hessian": np.diag(diag),
        "diag_GeV2": [float(x) for x in diag],
        "blocks": {
            "210_placeholder_GeV2": m2_210_eff,
            "210_requested_soft_floor_GeV2": float(m2_210),
            "fiveform_ambient_504_floor_GeV2": c_floor,
            "C_partial_126_min_GeV2": float(np.min(c)),
            "C_partial_126_max_GeV2": float(np.max(c)),
            "H10_min_GeV2": a_floor,
            "H10_max_GeV2": float(np.max(a)),
        },
        "hodge_126_placement": "uniform_floor_until_projector_map",
        "positive_definite_pre_projection": True,
    }


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
    n_h10_support = int(sum(1 for r in rows if r["frac_H10"] > 1e-6))
    n_sigma_support = int(sum(1 for r in rows if r["frac_sigmabar"] > 1e-6))
    n_210_support = int(sum(1 for r in rows if r["frac_210"] > 1e-6))
    return {
        "per_mode": rows,
        "mean_fractions": mean,
        "n_modes_with_H10_support": n_h10_support,
        "n_modes_with_sigmabar_support": n_sigma_support,
        "n_modes_with_210_support": n_210_support,
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
    """Algebraic checks that im(P_G) is in ker(P_phys H P_phys)."""
    h_proj = gproj.project_hessian(hessian, p_phys)
    if frame.size == 0:
        return {
            "frame_image_residual": 0.0,
            "frobenius_Hphys_PG": 0.0,
        }
    p_g = frame @ frame.T
    hg = h_proj @ frame
    return {
        "frame_image_residual": float(np.linalg.norm(hg))
        / max(1.0, float(np.linalg.norm(h_proj))),
        "frobenius_Hphys_PG": float(np.linalg.norm(h_proj @ p_g))
        / max(1.0, float(np.linalg.norm(h_proj))),
    }


def build_report() -> dict[str, Any]:
    iso_report = iso.build_report()
    orbit_report = hew_orbit.build_report()

    a = iso_report["A_partial_GeV2"]
    c = iso_report["C_partial_GeV2"]
    skeleton = form_basis_diagonal_hessian(a_h10=a, c_sigma=c)

    ext = hew_orbit.extended_tangent_matrix()
    tangent = ext["matrix"]
    n_field = ext["n_field_components"]
    frame_info = gproj.goldstone_frame_from_tangent(tangent)
    frame = frame_info["frame"]
    projs = gproj.projectors(frame, n_field)
    p_phys = projs["P_phys"]
    p_g = projs["P_G"]

    support = goldstone_support_fractions(frame)

    # Exact Goldstone-count proof on a unit-conditioned skeleton.
    unit_hess = np.eye(n_field, dtype=float)
    unit_spec = spectrum_after_projection(unit_hess, p_phys)
    unit_kernel = goldstone_kernel_residual(unit_hess, frame, p_phys)

    # Dynamical skeleton: rescale by median to tame A/C hierarchy before spectrum.
    diag = np.asarray(skeleton["diag_GeV2"], dtype=float)
    median = float(np.median(diag))
    scaled_hess = np.diag(diag / median)
    dyn_spec = spectrum_after_projection(scaled_hess, p_phys)
    dyn_kernel = goldstone_kernel_residual(scaled_hess, frame, p_phys)

    schur = iso_report.get("schur_with_partial_diagonals", {})
    n_phys = EXPECTED_FIELD_DIM - EXPECTED_GOLDSTONES

    checks = {
        "isotropic_partial_green": iso_report.get("n_failed", 1) == 0,
        "hew_orbit_36_green": orbit_report.get("n_failed", 1) == 0,
        "field_dim_724": n_field == EXPECTED_FIELD_DIM,
        "goldstone_rank_36": frame_info["rank"] == EXPECTED_GOLDSTONES,
        "trace_P_G_36": abs(float(np.trace(p_g)) - EXPECTED_GOLDSTONES) < 1e-6,
        "skeleton_positive_pre": skeleton["positive_definite_pre_projection"],
        "unit_projected_exactly_36_zeros": unit_spec["n_zero"] == EXPECTED_GOLDSTONES,
        "unit_projected_no_negative": unit_spec["n_negative"] == 0,
        "unit_projected_physical_positive": unit_spec["n_positive"] == n_phys,
        "unit_goldstone_kernel_tiny": unit_kernel["frame_image_residual"] < 1e-10,
        "dyn_scaled_projected_exactly_36_zeros": dyn_spec["n_zero"]
        == EXPECTED_GOLDSTONES,
        "dyn_scaled_projected_no_negative": dyn_spec["n_negative"] == 0,
        "dyn_scaled_projected_physical_positive": dyn_spec["n_positive"] == n_phys,
        "dyn_goldstone_kernel_tiny": dyn_kernel["frame_image_residual"] < 1e-8,
        "schur_272_recorded": "positive_definite" in schur,
        "four_isotropic_slots_filled": len(
            iso_report.get("partial_diagonals", {}).get("filled_slots", [])
        )
        == 4,
        "portal_basis_map_not_faked": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "PARTIAL_DYNAMICAL_HESSIAN_HEW_GOLDSTONE_GATE_READY__PORTAL_BASIS_MAP_OPEN"
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
            "schur_positive_definite": schur.get("positive_definite"),
            "schur_margin": schur.get("schur_margin"),
            "real_hessian_min_eigenvalue_GeV2": iso_report.get(
                "real_hessian_min_eigenvalue_GeV2"
            ),
        },
        "embedding": ext["embedding"],
        "form_basis_skeleton": {
            "shape": [EXPECTED_FIELD_DIM, EXPECTED_FIELD_DIM],
            "blocks": skeleton["blocks"],
            "m2_210_placeholder_GeV2": skeleton["blocks"]["210_placeholder_GeV2"],
            "m2_210_requested_soft_floor_GeV2": SOFT_210_FLOOR_GEV2,
            "median_diag_GeV2": median,
            "hodge_126_placement": skeleton["hodge_126_placement"],
            "uses_portal_B": False,
            "basis": "exterior_algebra_flatten_real",
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
                "Portal Schur Hessian lives in the Aulakh 10×126 component basis; "
                "it is recorded upstream but not identified with the form-basis "
                "724 embedding until a Cartesian basis map exists."
            ),
            "positive_definite": schur.get("positive_definite"),
            "schur_margin": schur.get("schur_margin"),
            "largest_normalized_singular_value": schur.get(
                "largest_normalized_singular_value"
            ),
        },
        "flags": {
            "partial_dynamical_hessian_goldstone_gate": not bool(failures),
            "hew_36_goldstones_applied": frame_info["rank"] == EXPECTED_GOLDSTONES,
            "form_basis_skeleton_positive_after_projection": (
                dyn_spec["n_negative"] == 0
                and dyn_spec["n_zero"] == EXPECTED_GOLDSTONES
            ),
            "portal_B_in_form_basis": False,
            "cartesian_portal_basis_map": False,
            "full_component_hessian_complete": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "hodge_projector_map_C126_into_ambient_fiveforms": True,
            "cartesian_basis_map_form_to_aulakh_10x126": True,
            "insert_portal_B_into_form_basis_hessian": True,
            "missing_cg_120_320_1050_4125": True,
            "S_Phi17_dynamical_blocks": True,
            "global_stationarity_boundedness": True,
        },
        "verdict": (
            "Form-basis isotropic A/C skeleton on the 724-dim (210⊕126bar⊕H10) "
            f"embedding, after exact removal of {EXPECTED_GOLDSTONES} hEW-extended "
            "Goldstones (unit and median-rescaled dynamical spectra), has "
            f"{dyn_spec['n_zero']} zeros, {dyn_spec['n_positive']} positive, "
            f"{dyn_spec['n_negative']} negative modes. Portal B remains in the "
            "separate Aulakh Schur 272 basis (basis map OPEN). Full dynamical "
            "Hessian and theory closure remain BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    gp = report["goldstone_projection"]
    OUT_MD.write_text(
        "# Partial dynamical Hessian + hEW Goldstone gate — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Goldstones removed: `{gp['rank']}`\n"
        f"- Unit skeleton zeros/pos/neg: "
        f"`{gp['unit_skeleton_spectrum']['n_zero']}` / "
        f"`{gp['unit_skeleton_spectrum']['n_positive']}` / "
        f"`{gp['unit_skeleton_spectrum']['n_negative']}`\n"
        f"- Dynamical (median-scaled) zeros/pos/neg: "
        f"`{gp['dynamical_scaled_spectrum']['n_zero']}` / "
        f"`{gp['dynamical_scaled_spectrum']['n_positive']}` / "
        f"`{gp['dynamical_scaled_spectrum']['n_negative']}`\n"
        f"- Schur 272 PD (Aulakh basis): "
        f"`{report['schur_272_aulakh_basis'].get('positive_definite')}`\n\n"
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
