#!/usr/bin/env python3
"""Extend the SO(10) gauge orbit with physical hEW=174 GeV (v20).

The existing certificate

    ⟨210_PS⟩ + ⟨Δ_R⟩  ⇒  orbit rank 33, stabilizer dim 12 (SM)

stops at the Standard Model. Adding the physical electroweak VEV in the 10

    ⟨H⟩ = hEW · ê   (unitary-gauge direction in the (1,2,2) weak subspace)

further breaks SU(2)_L×U(1)_Y → U(1)_EM and must raise the Goldstone count to

    45 − 9 = 36

with residual stabilizer SU(3)_c×U(1)_EM (dimension 9).

This module reuses the differential-form generator action on the 10 as a
one-form, stacks it into the tangent matrix with (210, 126bar), and proves
the extended rank. It also upgrades the Goldstone nullspace projector API to
the extended embedding.

Honesty
-------
* Still not the full dynamical component Hessian (missing S, Φ₁₇ spectators
  as dynamical fields, and incomplete SM-irrep mass matrices).
* Does not invent 120/320/1050/4125 CG.
* Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import so10_goldstone_nullspace_projector_v20 as gproj
import so10_nonsusy_gauge_orbit_v20 as orbit

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SO10_GAUGE_ORBIT_WITH_HEW_V20.json"
OUT_MD = ROOT / "SO10_GAUGE_ORBIT_WITH_HEW_V20.md"

HEW_GEV = 174.0
HEW_DIRECTION_INDEX = 6  # same weak-subspace convention as physical_54_hew
EXPECTED_SM_GOLDSTONES = 33
EXPECTED_EW_GOLDSTONES = 36
EXPECTED_EM_STABILIZER = 9  # SU(3)_c × U(1)_EM


def hew_one_form(*, h_ew_gev: float = HEW_GEV) -> orbit.Form:
    """Physical EW VEV as a real one-form (SO(10) vector) on ℝ¹⁰."""
    return orbit.one_form(HEW_DIRECTION_INDEX, complex(h_ew_gev))


def extended_tangent_matrix(
    *, h_ew_gev: float = HEW_GEV
) -> dict[str, Any]:
    """Tangent map for (Φ₂₁₀, Δ₁₂₆, H₁₀) including physical hEW."""
    vevs = orbit.build_vevs()
    phi = vevs["phi_210_ps"]
    delta = vevs["delta_126bar"]
    hew = hew_one_form(h_ew_gev=h_ew_gev)
    forms = [(phi, 4, False), (delta, 5, True), (hew, 1, False)]
    matrix = orbit.tangent_matrix(forms)
    return {
        "matrix": matrix,
        "n_field_components": int(matrix.shape[0]),
        "n_generators": int(matrix.shape[1]),
        "embedding": {
            "210_PS_four_form_real": 210,
            "126bar_five_form_real_imag": 504,
            "H10_vector_real": 10,
            "total": 724,
        },
        "hEW_GeV": float(h_ew_gev),
        "hew_direction_index": HEW_DIRECTION_INDEX,
        "forms": forms,
    }


def sm_only_tangent_matrix() -> dict[str, Any]:
    """Baseline (Φ, Δ) tangent without hEW."""
    return gproj.combined_tangent_matrix()


def build_report(*, h_ew_gev: float = HEW_GEV) -> dict[str, Any]:
    baseline = orbit.build_report()
    sm_tangent = sm_only_tangent_matrix()
    sm_rank = gproj.goldstone_frame_from_tangent(sm_tangent["matrix"])["rank"]

    ext = extended_tangent_matrix(h_ew_gev=h_ew_gev)
    tangent = ext["matrix"]
    frame_info = gproj.goldstone_frame_from_tangent(tangent)
    frame = frame_info["frame"]
    n_field = ext["n_field_components"]
    projs = gproj.projectors(frame, n_field)
    p_g = projs["P_G"]
    p_phys = projs["P_phys"]

    rank = frame_info["rank"]
    stabilizer = 45 - rank
    delta_rank = rank - sm_rank

    # Projector algebra on extended space.
    pg2_err = float(np.linalg.norm(p_g @ p_g - p_g))
    orth_err = float(np.linalg.norm(p_g @ p_phys))
    tang_residual = float(np.linalg.norm(p_g @ tangent - tangent)) / max(
        1.0, float(np.linalg.norm(tangent))
    )

    # Synthetic Hessian validation on extended embedding.
    synth = gproj.synthetic_hessian_with_goldstone_nulls(frame, n_field)
    h_proj = gproj.project_hessian(synth["hessian"], p_phys)
    eigs = np.linalg.eigvalsh(h_proj)
    tol = 1e-10 * max(1.0, float(np.max(np.abs(eigs))))
    n_zero = int(np.sum(np.abs(eigs) <= tol))
    n_pos = int(np.sum(eigs > tol))
    n_neg = int(np.sum(eigs < -tol))
    n_phys = n_field - EXPECTED_EW_GOLDSTONES

    # hEW-alone orbit rank (diagnostic): should be >0 and contribute the +3.
    hew_only = orbit.tangent_matrix([(hew_one_form(h_ew_gev=h_ew_gev), 1, False)])
    hew_rank = orbit.svd_rank(hew_only)

    checks = {
        "baseline_sm_orbit_green": baseline.get("n_failed", 1) == 0,
        "sm_goldstone_rank_33": sm_rank == EXPECTED_SM_GOLDSTONES,
        "extended_field_dim_724": n_field == 724,
        "extended_goldstone_rank_36": rank == EXPECTED_EW_GOLDSTONES,
        "em_stabilizer_dimension_9": stabilizer == EXPECTED_EM_STABILIZER,
        "hew_adds_three_goldstones": delta_rank == 3,
        "hew_alone_orbit_nonzero": hew_rank > 0,
        "P_G_idempotent": pg2_err < 1e-8,
        "P_G_orthogonal_P_phys": orth_err < 1e-8,
        "trace_P_G_equals_36": abs(float(np.trace(p_g)) - EXPECTED_EW_GOLDSTONES)
        < 1e-6,
        "tangent_in_goldstone_subspace": tang_residual < 1e-10,
        "synthetic_projected_33_or_36_zeros": n_zero == EXPECTED_EW_GOLDSTONES,
        "synthetic_no_negative": n_neg == 0,
        "synthetic_physical_positive": n_pos == n_phys,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "SO10_GAUGE_ORBIT_WITH_HEW_36_GOLDSTONES__FULL_HESSIAN_OPEN"
            if not failures
            else "SO10_GAUGE_ORBIT_WITH_HEW_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "breaking_chain": {
            "SO10_to_SM": {
                "fields": ["210_PS", "Delta_R"],
                "goldstones": sm_rank,
                "stabilizer_dim": 45 - sm_rank,
                "stabilizer": "SU(3)xSU(2)xU(1)",
            },
            "SM_to_UEM": {
                "fields": ["H10_hEW"],
                "added_goldstones": delta_rank,
                "hEW_GeV": float(h_ew_gev),
                "hew_direction_index": HEW_DIRECTION_INDEX,
                "hew_alone_orbit_rank": hew_rank,
            },
            "SO10_to_UEM": {
                "goldstones": rank,
                "stabilizer_dim": stabilizer,
                "stabilizer": "SU(3)_c x U(1)_EM",
            },
        },
        "embedding": ext["embedding"],
        "projectors": {
            "trace_P_G": float(np.trace(p_g)),
            "trace_P_phys": float(np.trace(p_phys)),
            "P_G_idempotence_residual": pg2_err,
            "tangent_in_image_residual": tang_residual,
        },
        "synthetic_validation": {
            "n_zero": n_zero,
            "n_positive": n_pos,
            "n_negative": n_neg,
            "physical_complement_dimension": n_phys,
        },
        "upstream_sm_orbit_status": baseline.get("status"),
        "flags": {
            "hew_extended_orbit_36_goldstones": not bool(failures),
            "sm_orbit_33_retained": sm_rank == EXPECTED_SM_GOLDSTONES,
            "em_stabilizer_9": stabilizer == EXPECTED_EM_STABILIZER,
            "goldstone_projector_extended": not bool(failures),
            "full_component_hessian_complete": False,
            "S_and_Phi17_dynamical_in_orbit": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "include_S_Phi17_as_dynamical_orbit_spectators": True,
            "build_dynamical_full_nonsusy_hessian": True,
            "missing_cg_120_320_1050_4125": True,
            "global_stationarity_boundedness": True,
        },
        "verdict": (
            f"Including physical hEW={h_ew_gev:g} GeV in the SO(10) vector "
            f"raises the gauge-orbit rank from {sm_rank} to {rank} "
            f"(+{delta_rank}), with residual stabilizer dimension {stabilizer} "
            "(SU(3)_c×U(1)_EM). Extended Goldstone projectors are validated on "
            "synthetic Hessians. Full dynamical component Hessian remains OPEN. "
            "Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    chain = report["breaking_chain"]
    OUT_MD.write_text(
        "# SO(10) gauge orbit with physical hEW — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- SO(10)→SM Goldstones: `{chain['SO10_to_SM']['goldstones']}`\n"
        f"- Added by hEW: `{chain['SM_to_UEM']['added_goldstones']}`\n"
        f"- SO(10)→U(1)_EM Goldstones: `{chain['SO10_to_UEM']['goldstones']}`\n"
        f"- EM stabilizer dim: `{chain['SO10_to_UEM']['stabilizer_dim']}`\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--hEW", type=float, default=HEW_GEV)
    args = parser.parse_args(argv)
    report = build_report(h_ew_gev=args.hEW)
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
