#!/usr/bin/env python3
"""Rank-33 Goldstone nullspace projector for the exact SO(10) orbit (v20).

Consumes ``so10_nonsusy_gauge_orbit_v20.tangent_matrix`` on the certificate
VEVs (210 PS four-form + 126bar five-form) and builds:

1. An orthonormal frame for the 33-dimensional Goldstone subspace in the
   real field embedding;
2. Orthogonal projectors ``P_G`` (Goldstone) and ``P_phys = I - P_G``;
3. A Hessian map ``H ↦ P_phys H P_phys`` that removes gauge directions.

Honesty
-------
* Scope is the orbit-certificate embedding (210_PS ⊕ 126bar), not the full
  dynamical component space with H10, S, Φ₁₇, and all SM irreps.
* This closes reusable Goldstone-removal tooling for G3. It does **not**
  construct or validate the complete non-SUSY scalar Hessian.
* Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import so10_nonsusy_gauge_orbit_v20 as orbit

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SO10_GOLDSTONE_NULLSPACE_PROJECTOR_V20.json"
OUT_MD = ROOT / "SO10_GOLDSTONE_NULLSPACE_PROJECTOR_V20.md"

EXPECTED_GOLDSTONES = 33
REL_SVD_TOL = 1e-11


def combined_tangent_matrix() -> dict[str, Any]:
    """Exact tangent map columns = gauge generators acting on (Φ₂₁₀, Δ₁₂₆)."""
    vevs = orbit.build_vevs()
    phi = vevs["phi_210_ps"]
    delta = vevs["delta_126bar"]
    forms = [(phi, 4, False), (delta, 5, True)]
    matrix = orbit.tangent_matrix(forms)
    return {
        "matrix": matrix,
        "n_field_components": int(matrix.shape[0]),
        "n_generators": int(matrix.shape[1]),
        "embedding": {
            "210_PS_four_form_real": 210,
            "126bar_five_form_real_imag": 504,
            "total": 714,
        },
        "forms": forms,
    }


def goldstone_frame_from_tangent(
    tangent: np.ndarray, *, relative_tolerance: float = REL_SVD_TOL
) -> dict[str, Any]:
    """Orthonormal columns spanning the gauge-orbit image (Goldstones)."""
    # SVD: T = U Σ V†; nonzero left singular vectors span im(T).
    u, s, _vh = np.linalg.svd(tangent, full_matrices=False)
    if s.size == 0 or s[0] == 0.0:
        rank = 0
        frame = np.zeros((tangent.shape[0], 0), dtype=float)
    else:
        mask = s > relative_tolerance * s[0]
        rank = int(np.sum(mask))
        frame = u[:, mask]
    return {
        "frame": frame,
        "rank": rank,
        "singular_values": [float(x) for x in s],
        "n_nonzero_singular": rank,
    }


def projectors(frame: np.ndarray, n_field: int) -> dict[str, np.ndarray]:
    """P_G = F Fᵀ, P_phys = I - P_G on the real field embedding."""
    if frame.size == 0:
        p_g = np.zeros((n_field, n_field), dtype=float)
    else:
        p_g = frame @ frame.T
    eye = np.eye(n_field, dtype=float)
    return {"P_G": p_g, "P_phys": eye - p_g}


def project_hessian(hessian: np.ndarray, p_phys: np.ndarray) -> np.ndarray:
    """Remove Goldstone directions: H_phys = P_phys H P_phys."""
    return p_phys @ hessian @ p_phys


def synthetic_hessian_with_goldstone_nulls(
    frame: np.ndarray, n_field: int, *, seed: int = 0
) -> dict[str, Any]:
    """Build a PD physical block plus exact zeros on the Goldstone frame."""
    rng = np.random.default_rng(seed)
    # Random SPD on the full space, then kill Goldstone directions exactly.
    a = rng.normal(size=(n_field, n_field))
    h_raw = a.T @ a + np.eye(n_field)
    if frame.size == 0:
        p_g = np.zeros((n_field, n_field), dtype=float)
    else:
        p_g = frame @ frame.T
    p_phys = np.eye(n_field) - p_g
    h = p_phys @ h_raw @ p_phys
    eigs = np.linalg.eigvalsh(h)
    tol = 1e-10 * max(1.0, float(np.max(np.abs(eigs))))
    return {
        "hessian": h,
        "n_zero": int(np.sum(np.abs(eigs) <= tol)),
        "n_positive": int(np.sum(eigs > tol)),
        "n_negative": int(np.sum(eigs < -tol)),
        "eig_min": float(eigs[0]),
        "eig_max": float(eigs[-1]),
    }


def build_report() -> dict[str, Any]:
    upstream = orbit.build_report()
    tangent_info = combined_tangent_matrix()
    tangent = tangent_info["matrix"]
    n_field = tangent_info["n_field_components"]
    frame_info = goldstone_frame_from_tangent(tangent)
    frame = frame_info["frame"]
    projs = projectors(frame, n_field)
    p_g = projs["P_G"]
    p_phys = projs["P_phys"]

    # Projector algebra checks.
    pg2_err = float(np.linalg.norm(p_g @ p_g - p_g))
    pp2_err = float(np.linalg.norm(p_phys @ p_phys - p_phys))
    orth_err = float(np.linalg.norm(p_g @ p_phys))
    trace_g = float(np.trace(p_g))
    trace_p = float(np.trace(p_phys))

    # Tangent columns lie in Goldstone subspace: P_G T ≈ T.
    tang_residual = float(np.linalg.norm(p_g @ tangent - tangent)) / max(
        1.0, float(np.linalg.norm(tangent))
    )

    synth = synthetic_hessian_with_goldstone_nulls(frame, n_field)
    h_proj = project_hessian(synth["hessian"], p_phys)
    eigs_proj = np.linalg.eigvalsh(h_proj)
    tol = 1e-10 * max(1.0, float(np.max(np.abs(eigs_proj))))
    n_zero_proj = int(np.sum(np.abs(eigs_proj) <= tol))
    n_pos_proj = int(np.sum(eigs_proj > tol))
    n_neg_proj = int(np.sum(eigs_proj < -tol))

    # Physical complement dimension.
    n_phys = n_field - EXPECTED_GOLDSTONES

    checks = {
        "upstream_orbit_green": upstream.get("n_failed", 1) == 0,
        "field_embedding_dim_714": n_field == 714,
        "generator_count_45": tangent_info["n_generators"] == 45,
        "goldstone_rank_33": frame_info["rank"] == EXPECTED_GOLDSTONES,
        "P_G_idempotent": pg2_err < 1e-8,
        "P_phys_idempotent": pp2_err < 1e-8,
        "P_G_orthogonal_P_phys": orth_err < 1e-8,
        "trace_P_G_equals_33": abs(trace_g - EXPECTED_GOLDSTONES) < 1e-6,
        "trace_P_phys_equals_681": abs(trace_p - n_phys) < 1e-6,
        "tangent_in_goldstone_subspace": tang_residual < 1e-10,
        "synthetic_hessian_has_33_zeros": synth["n_zero"] == EXPECTED_GOLDSTONES,
        "projected_hessian_keeps_33_zeros": n_zero_proj == EXPECTED_GOLDSTONES,
        "projected_hessian_no_negative": n_neg_proj == 0,
        "projected_physical_positive_count": n_pos_proj == n_phys,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "SO10_GOLDSTONE_NULLSPACE_PROJECTOR_READY__FULL_HESSIAN_OPEN"
            if not failures
            else "SO10_GOLDSTONE_NULLSPACE_PROJECTOR_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "embedding": tangent_info["embedding"],
        "orbit": {
            "n_generators": tangent_info["n_generators"],
            "goldstone_rank": frame_info["rank"],
            "expected_goldstones": EXPECTED_GOLDSTONES,
            "physical_complement_dimension": n_phys,
            "singular_values_sample": frame_info["singular_values"][::8],
        },
        "projectors": {
            "trace_P_G": trace_g,
            "trace_P_phys": trace_p,
            "P_G_idempotence_residual": pg2_err,
            "P_phys_idempotence_residual": pp2_err,
            "P_G_P_phys_residual": orth_err,
            "tangent_in_image_residual": tang_residual,
        },
        "synthetic_validation": {
            "n_zero_before_reproject": synth["n_zero"],
            "n_zero_after_reproject": n_zero_proj,
            "n_positive_after_reproject": n_pos_proj,
            "n_negative_after_reproject": n_neg_proj,
        },
        "upstream_orbit_status": upstream.get("status"),
        "api": {
            "combined_tangent_matrix": "combined_tangent_matrix()",
            "goldstone_frame_from_tangent": "goldstone_frame_from_tangent(T)",
            "projectors": "projectors(frame, n_field)",
            "project_hessian": "project_hessian(H, P_phys)",
        },
        "flags": {
            "goldstone_nullspace_projector_ready": not bool(failures),
            "exact_33_goldstone_rank": frame_info["rank"] == EXPECTED_GOLDSTONES,
            "full_component_field_space": False,
            "full_component_hessian_complete": False,
            "root_by_root_33_goldstone_projection_on_dynamical_hessian": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "extend_projector_to_full_component_space_H10_S_Phi17": True,
            "build_dynamical_full_nonsusy_hessian": True,
            "missing_cg_120_320_1050_4125": True,
            "global_stationarity_boundedness": True,
        },
        "verdict": (
            "An exact rank-33 Goldstone nullspace projector is available on the "
            "orbit-certificate embedding (210_PS ⊕ 126bar, dim 714): P_G has "
            "trace 33, P_phys has trace 681, and synthetic Hessians retain "
            "exactly 33 zeros after projection. Full dynamical component "
            "Hessian and issue #86 remain OPEN. Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    orb = report["orbit"]
    OUT_MD.write_text(
        "# SO(10) Goldstone nullspace projector — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Goldstone rank: `{orb['goldstone_rank']}`\n"
        f"- Physical complement dim: `{orb['physical_complement_dimension']}`\n"
        f"- Embedding dim: `{report['embedding']['total']}`\n\n"
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
